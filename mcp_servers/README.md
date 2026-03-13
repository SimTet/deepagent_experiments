# MCP Servers

Reusable [Model Context Protocol](https://modelcontextprotocol.io/) servers that can be spun up and used with deepagent examples.

## Structure

Each server lives in its own subdirectory:

```
mcp_servers/
├── README.md
├── <server_name>/
│   ├── server.py        # MCP server implementation
│   ├── requirements.txt # Server-specific dependencies (if any)
│   └── README.md        # Usage instructions & tool descriptions
```

## Available Servers

| Server | Description | Tools |
|--------|-------------|-------|
| [ms365_graph](ms365_graph/) | Microsoft 365 via Graph API (Outlook, Teams, SharePoint, OneDrive) | 49 tools |

## Usage

### Standalone

```bash
cd mcp_servers/<server_name>
uv run server.py
```

### With a deepagent example

Configure the server in your agent's MCP client setup, then reference the exposed tools in your `create_deep_agent()` call. See individual server READMEs for integration details.
