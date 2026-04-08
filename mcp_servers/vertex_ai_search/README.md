# Vertex AI Search MCP Server

An MCP server that exposes Google Cloud's [Vertex AI Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview) (Discovery Engine) and Gemini grounding as tools. This gives any MCP-compatible client (Claude Code, Claude Desktop, your own Claude SDK app, etc.) the ability to manage document datastores and ask grounded questions with citations — essentially a programmable NotebookLM built on official Google Cloud APIs.

## Prerequisites

1. **Google Cloud project** with billing enabled
2. **APIs enabled** on the project:
   ```bash
   gcloud services enable discoveryengine.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```
3. **IAM permissions** — your user/service account needs:
   - `Discovery Engine Editor` (for datastore/document CRUD)
   - `Discovery Engine Viewer` (for search, if read-only is enough)
   - `Vertex AI User` (for Gemini grounded generation)
4. **Application Default Credentials** configured:
   ```bash
   gcloud auth application-default login
   ```
   Or if using a service account, set `GOOGLE_APPLICATION_CREDENTIALS` to the key file path.

## Setup

```bash
cd mcp_servers/vertex_ai_search
uv venv
uv pip install -e .
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Yes | — | Your GCP project ID |
| `VERTEX_AI_SEARCH_LOCATION` | No | `global` | Multi-region: `global`, `us`, or `eu` |
| `VERTEX_AI_SEARCH_DATASTORE_ID` | No | — | Default datastore for search/Q&A tools (avoids passing it every call) |
| `VERTEX_AI_SEARCH_GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model for grounded generation |

## Running standalone

```bash
GOOGLE_CLOUD_PROJECT=my-project python server.py
```

The server starts on stdio (MCP's default transport).

## Integration

### Claude Code

```bash
claude mcp add vertex-ai-search \
  -e GOOGLE_CLOUD_PROJECT=my-project \
  -e VERTEX_AI_SEARCH_DATASTORE_ID=my-datastore \
  -- /path/to/mcp_servers/vertex_ai_search/.venv/bin/python \
     /path/to/mcp_servers/vertex_ai_search/server.py
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "vertex-ai-search": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/mcp_servers/vertex_ai_search/server.py"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "my-project",
        "VERTEX_AI_SEARCH_DATASTORE_ID": "my-datastore"
      }
    }
  }
}
```

### Claude SDK (Python) — programmatic MCP client

```python
from anthropic import Anthropic
from anthropic.types import MessageParam
import subprocess, json

# Start MCP server as a subprocess and connect via stdio
# (or use your preferred MCP client library)
```

## Tools reference

### Datastore management

| Tool | Description |
|------|-------------|
| `create_datastore` | Create a new datastore for unstructured documents |
| `list_datastores` | List all datastores in the project |
| `delete_datastore` | Delete a datastore and all its documents |

### Document ingestion

| Tool | Description |
|------|-------------|
| `ingest_gcs_documents` | Bulk-import from GCS (PDF, HTML, TXT, DOCX, PPTX, XLSX) |
| `ingest_inline_document` | Create a document from inline text |
| `list_documents` | List documents in a datastore |
| `delete_document` | Delete a single document |
| `purge_documents` | Delete ALL documents in a datastore |

### Search & Q&A

| Tool | Description |
|------|-------------|
| `search_documents` | Keyword/semantic search with snippets and extractive answers |
| `ask_grounded` | Ask a question grounded in one datastore — returns answer + citations |
| `ask_grounded_multi` | Ask a question grounded across multiple datastores (max 10) |

## Typical workflow

```
1. create_datastore("my-docs", "My Documents")
2. ingest_gcs_documents("my-docs", ["gs://my-bucket/reports/*.pdf"])
   — wait a few minutes for indexing to complete —
3. ask_grounded("What were the key findings in Q4?", datastore_id="my-docs")
   -> { answer: "...", citations: [{uri: "...", title: "..."}] }
```

Or with inline text for quick testing:

```
1. create_datastore("test", "Test Store")
2. ingest_inline_document("test", "doc-1", "Meeting Notes", "We decided to migrate to Kubernetes...")
3. ask_grounded("What was the migration decision?", datastore_id="test")
```

## Notes

- **Indexing delay**: After ingesting documents, Vertex AI Search needs time to index them (usually 1-5 minutes for small batches). Queries against un-indexed documents will return empty results.
- **Costs**: Vertex AI Search and Gemini API calls are billed to your GCP project. See [Vertex AI Search pricing](https://cloud.google.com/generative-ai-app-builder/pricing) and [Gemini pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing).
- **Location**: If your org has data residency requirements, set `VERTEX_AI_SEARCH_LOCATION` to `us` or `eu` instead of `global`.
- **Auth in CI/CD**: Use workload identity federation or a service account key rather than `gcloud auth application-default login`.
