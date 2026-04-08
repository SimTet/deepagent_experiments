"""
Vertex AI Search MCP Server — Python/FastMCP

A Model Context Protocol server providing grounded Q&A over your documents
using Google Cloud's Vertex AI Search (Discovery Engine) and Gemini.

Auth: Uses Application Default Credentials (ADC) via gcloud.
Set GOOGLE_CLOUD_PROJECT and optionally VERTEX_AI_SEARCH_LOCATION,
VERTEX_AI_SEARCH_DATASTORE_ID env vars.
"""

import logging
import os
import sys
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("vertex_ai_search")

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
os.environ.setdefault("FASTMCP_DISABLE_UPDATE_CHECK", "1")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("VERTEX_AI_SEARCH_LOCATION", "global")
DEFAULT_DATASTORE_ID = os.environ.get("VERTEX_AI_SEARCH_DATASTORE_ID", "")
GEMINI_MODEL = os.environ.get("VERTEX_AI_SEARCH_GEMINI_MODEL", "gemini-2.5-flash")

# ---------------------------------------------------------------------------
# Lazy-initialised clients
# ---------------------------------------------------------------------------
_datastore_client = None
_document_client = None
_search_client = None
_genai_client = None


def _get_client_options():
    from google.api_core.client_options import ClientOptions

    if LOCATION != "global":
        return ClientOptions(
            api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com"
        )
    return None


def _get_datastore_client():
    global _datastore_client
    if _datastore_client is None:
        from google.cloud import discoveryengine

        _datastore_client = discoveryengine.DataStoreServiceClient(
            client_options=_get_client_options()
        )
    return _datastore_client


def _get_document_client():
    global _document_client
    if _document_client is None:
        from google.cloud import discoveryengine

        _document_client = discoveryengine.DocumentServiceClient(
            client_options=_get_client_options()
        )
    return _document_client


def _get_search_client():
    global _search_client
    if _search_client is None:
        from google.cloud import discoveryengine

        _search_client = discoveryengine.SearchServiceClient(
            client_options=_get_client_options()
        )
    return _search_client


def _get_genai_client():
    global _genai_client
    if _genai_client is None:
        from google import genai
        from google.genai.types import HttpOptions

        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LOCATION)
        _genai_client = genai.Client(http_options=HttpOptions(api_version="v1"))
    return _genai_client


def _collection_path():
    return _get_datastore_client().collection_path(
        project=PROJECT_ID,
        location=LOCATION,
        collection="default_collection",
    )


def _branch_path(datastore_id: str):
    return _get_document_client().branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=datastore_id,
        branch="default_branch",
    )


def _datastore_path(datastore_id: str):
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{datastore_id}"


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Vertex AI Search",
    instructions=(
        "Vertex AI Search MCP server for grounded Q&A. "
        "Provides tools to manage datastores, ingest documents, "
        "search, and ask grounded questions powered by Gemini. "
        "Requires GOOGLE_CLOUD_PROJECT env var and gcloud ADC auth."
    ),
)


# ---------------------------------------------------------------------------
# Datastore management tools
# ---------------------------------------------------------------------------
@mcp.tool(tags={"datastore"})
async def create_datastore(
    datastore_id: Annotated[
        str,
        Field(description="Unique ID for the new datastore (lowercase, hyphens ok)"),
    ],
    display_name: Annotated[
        str,
        Field(description="Human-readable name for the datastore"),
    ],
) -> dict:
    """Create a new Vertex AI Search datastore for unstructured documents."""
    from google.cloud import discoveryengine

    client = _get_datastore_client()
    data_store = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )
    request = discoveryengine.CreateDataStoreRequest(
        parent=_collection_path(),
        data_store_id=datastore_id,
        data_store=data_store,
    )
    operation = client.create_data_store(request=request)
    response = operation.result()
    return {
        "name": response.name,
        "display_name": response.display_name,
        "datastore_id": datastore_id,
        "status": "created",
    }


@mcp.tool(tags={"datastore"})
async def list_datastores() -> dict:
    """List all Vertex AI Search datastores in the current project."""
    from google.cloud import discoveryengine

    client = _get_datastore_client()
    request = discoveryengine.ListDataStoresRequest(parent=_collection_path())
    stores = []
    for store in client.list_data_stores(request=request):
        stores.append(
            {
                "name": store.name,
                "display_name": store.display_name,
                "create_time": str(store.create_time),
            }
        )
    return {"datastores": stores, "count": len(stores)}


@mcp.tool(tags={"datastore"})
async def delete_datastore(
    datastore_id: Annotated[
        str,
        Field(description="ID of the datastore to delete"),
    ],
) -> dict:
    """Delete a Vertex AI Search datastore and all its documents."""
    from google.cloud import discoveryengine

    client = _get_datastore_client()
    request = discoveryengine.DeleteDataStoreRequest(
        name=_datastore_path(datastore_id),
    )
    operation = client.delete_data_store(request=request)
    operation.result()
    return {"datastore_id": datastore_id, "status": "deleted"}


# ---------------------------------------------------------------------------
# Document ingestion tools
# ---------------------------------------------------------------------------
@mcp.tool(tags={"documents"})
async def ingest_gcs_documents(
    datastore_id: Annotated[
        str,
        Field(description="Datastore ID to ingest into"),
    ],
    gcs_uris: Annotated[
        list[str],
        Field(
            description='GCS URIs to import, e.g. ["gs://bucket/path/*.pdf"]. '
            "Supports PDF, HTML, TXT, DOCX, PPTX, XLSX."
        ),
    ],
) -> dict:
    """Import documents from Google Cloud Storage into a datastore."""
    from google.cloud import discoveryengine

    client = _get_document_client()
    request = discoveryengine.ImportDocumentsRequest(
        parent=_branch_path(datastore_id),
        gcs_source=discoveryengine.GcsSource(
            input_uris=gcs_uris,
            data_schema="content",
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )
    operation = client.import_documents(request=request)
    response = operation.result()
    metadata = discoveryengine.ImportDocumentsMetadata(operation.metadata)
    return {
        "datastore_id": datastore_id,
        "status": "imported",
        "success_count": metadata.success_count,
        "failure_count": metadata.failure_count,
    }


@mcp.tool(tags={"documents"})
async def ingest_inline_document(
    datastore_id: Annotated[
        str,
        Field(description="Datastore ID to ingest into"),
    ],
    document_id: Annotated[
        str,
        Field(description="Unique ID for the document (lowercase, hyphens ok)"),
    ],
    title: Annotated[
        str,
        Field(description="Document title"),
    ],
    content: Annotated[
        str,
        Field(description="The text content of the document"),
    ],
    mime_type: Annotated[
        str,
        Field(description="MIME type of the content, e.g. 'text/plain' or 'text/html'"),
    ] = "text/plain",
) -> dict:
    """Create a document with inline text content in a datastore."""
    from google.cloud import discoveryengine

    client = _get_document_client()
    document = discoveryengine.Document(
        id=document_id,
        name=f"{_branch_path(datastore_id)}/documents/{document_id}",
        content=discoveryengine.Document.Content(
            raw_bytes=content.encode("utf-8"),
            mime_type=mime_type,
        ),
        struct_data={"title": title},
    )
    request = discoveryengine.CreateDocumentRequest(
        parent=_branch_path(datastore_id),
        document=document,
        document_id=document_id,
    )
    response = client.create_document(request=request)
    return {
        "name": response.name,
        "document_id": document_id,
        "status": "created",
    }


@mcp.tool(tags={"documents"})
async def list_documents(
    datastore_id: Annotated[
        str,
        Field(description="Datastore ID to list documents from"),
    ],
    page_size: Annotated[
        int,
        Field(description="Max documents to return", ge=1, le=100),
    ] = 25,
) -> dict:
    """List documents in a datastore."""
    from google.cloud import discoveryengine

    client = _get_document_client()
    request = discoveryengine.ListDocumentsRequest(
        parent=_branch_path(datastore_id),
        page_size=page_size,
    )
    docs = []
    for doc in client.list_documents(request=request):
        docs.append(
            {
                "name": doc.name,
                "id": doc.id,
                "struct_data": dict(doc.struct_data) if doc.struct_data else {},
            }
        )
    return {"documents": docs, "count": len(docs)}


@mcp.tool(tags={"documents"})
async def delete_document(
    datastore_id: Annotated[
        str,
        Field(description="Datastore ID containing the document"),
    ],
    document_id: Annotated[
        str,
        Field(description="ID of the document to delete"),
    ],
) -> dict:
    """Delete a document from a datastore."""
    from google.cloud import discoveryengine

    client = _get_document_client()
    name = f"{_branch_path(datastore_id)}/documents/{document_id}"
    request = discoveryengine.DeleteDocumentRequest(name=name)
    client.delete_document(request=request)
    return {"document_id": document_id, "status": "deleted"}


@mcp.tool(tags={"documents"})
async def purge_documents(
    datastore_id: Annotated[
        str,
        Field(description="Datastore ID to purge documents from"),
    ],
) -> dict:
    """Purge ALL documents from a datastore. Use with caution."""
    from google.cloud import discoveryengine

    client = _get_document_client()
    request = discoveryengine.PurgeDocumentsRequest(
        parent=_branch_path(datastore_id),
        filter="*",
        force=True,
    )
    operation = client.purge_documents(request=request)
    result = operation.result()
    return {
        "datastore_id": datastore_id,
        "purge_count": result.purge_count,
        "status": "purged",
    }


# ---------------------------------------------------------------------------
# Search tools
# ---------------------------------------------------------------------------
@mcp.tool(tags={"search"})
async def search_documents(
    query: Annotated[
        str,
        Field(description="The search query"),
    ],
    datastore_id: Annotated[
        str | None,
        Field(description="Datastore ID to search. Uses default if not set."),
    ] = None,
    page_size: Annotated[
        int,
        Field(description="Max results to return", ge=1, le=20),
    ] = 5,
) -> dict:
    """Search documents in a Vertex AI Search datastore. Returns relevant snippets."""
    from google.cloud import discoveryengine

    ds_id = datastore_id or DEFAULT_DATASTORE_ID
    if not ds_id:
        return {"error": "No datastore_id provided and VERTEX_AI_SEARCH_DATASTORE_ID not set"}

    client = _get_search_client()
    serving_config = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
        f"/dataStores/{ds_id}/servingConfigs/default_search"
    )
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
            ),
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=3,
            ),
        ),
    )
    response = client.search(request=request)
    results = []
    for result in response.results:
        doc = result.document
        snippets = []
        if hasattr(result, "document") and doc.derived_struct_data:
            derived = dict(doc.derived_struct_data)
            if "snippets" in derived:
                for s in derived["snippets"]:
                    snippets.append(dict(s))
            if "extractive_answers" in derived:
                for a in derived["extractive_answers"]:
                    snippets.append(dict(a))
        results.append(
            {
                "id": doc.id,
                "name": doc.name,
                "snippets": snippets,
                "struct_data": dict(doc.struct_data) if doc.struct_data else {},
            }
        )
    return {"query": query, "results": results, "count": len(results)}


# ---------------------------------------------------------------------------
# Grounded Q&A — the main value tool
# ---------------------------------------------------------------------------
@mcp.tool(tags={"qa", "grounding"})
async def ask_grounded(
    question: Annotated[
        str,
        Field(description="The question to answer using your document sources"),
    ],
    datastore_id: Annotated[
        str | None,
        Field(description="Datastore ID to ground against. Uses default if not set."),
    ] = None,
    model: Annotated[
        str | None,
        Field(description="Gemini model to use. Defaults to gemini-2.5-flash."),
    ] = None,
) -> dict:
    """Ask a question grounded in your Vertex AI Search documents.
    Returns an answer with citations from your sources."""
    from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexAISearch

    ds_id = datastore_id or DEFAULT_DATASTORE_ID
    if not ds_id:
        return {"error": "No datastore_id provided and VERTEX_AI_SEARCH_DATASTORE_ID not set"}

    client = _get_genai_client()
    datastore_path = _datastore_path(ds_id)

    tool = Tool(
        retrieval=Retrieval(
            vertex_ai_search=VertexAISearch(datastore=datastore_path)
        )
    )

    response = client.models.generate_content(
        model=model or GEMINI_MODEL,
        contents=question,
        config=GenerateContentConfig(tools=[tool]),
    )

    # Extract grounding metadata
    citations = []
    if response.candidates and response.candidates[0].grounding_metadata:
        gm = response.candidates[0].grounding_metadata
        if gm.grounding_chunks:
            for chunk in gm.grounding_chunks:
                citation = {}
                if chunk.retrieved_context:
                    citation["uri"] = chunk.retrieved_context.uri
                    citation["title"] = chunk.retrieved_context.title
                if chunk.web:
                    citation["uri"] = chunk.web.uri
                    citation["title"] = chunk.web.title
                citations.append(citation)

    return {
        "answer": response.text,
        "citations": citations,
        "model": model or GEMINI_MODEL,
        "datastore_id": ds_id,
    }


@mcp.tool(tags={"qa", "grounding"})
async def ask_grounded_multi(
    question: Annotated[
        str,
        Field(description="The question to answer"),
    ],
    datastore_ids: Annotated[
        list[str],
        Field(description="List of datastore IDs to ground against (max 10)"),
    ],
    model: Annotated[
        str | None,
        Field(description="Gemini model to use. Defaults to gemini-2.5-flash."),
    ] = None,
) -> dict:
    """Ask a grounded question across multiple datastores at once.
    Gemini will synthesize an answer from all sources with citations."""
    from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexAISearch

    if len(datastore_ids) > 10:
        return {"error": "Maximum 10 datastores per query"}

    client = _get_genai_client()
    tools = [
        Tool(
            retrieval=Retrieval(
                vertex_ai_search=VertexAISearch(datastore=_datastore_path(ds_id))
            )
        )
        for ds_id in datastore_ids
    ]

    response = client.models.generate_content(
        model=model or GEMINI_MODEL,
        contents=question,
        config=GenerateContentConfig(tools=tools),
    )

    citations = []
    if response.candidates and response.candidates[0].grounding_metadata:
        gm = response.candidates[0].grounding_metadata
        if gm.grounding_chunks:
            for chunk in gm.grounding_chunks:
                citation = {}
                if chunk.retrieved_context:
                    citation["uri"] = chunk.retrieved_context.uri
                    citation["title"] = chunk.retrieved_context.title
                if chunk.web:
                    citation["uri"] = chunk.web.uri
                    citation["title"] = chunk.web.title
                citations.append(citation)

    return {
        "answer": response.text,
        "citations": citations,
        "model": model or GEMINI_MODEL,
        "datastore_ids": datastore_ids,
    }


if __name__ == "__main__":
    if not PROJECT_ID:
        logger.error("GOOGLE_CLOUD_PROJECT env var is required")
        sys.exit(1)
    logger.info(
        "Starting Vertex AI Search MCP server (project=%s, location=%s)", PROJECT_ID, LOCATION
    )
    mcp.run()
