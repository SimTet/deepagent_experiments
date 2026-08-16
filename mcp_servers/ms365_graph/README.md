# MS365 Graph MCP Server

A Python [FastMCP](https://gofastmcp.com) server that exposes Microsoft 365 functionality via the [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/overview) as MCP tools.

## Services & Tools

| Service | Tools | Graph API Scopes |
|---------|-------|-----------------|
| **Outlook Mail** | list folders, list/get/send/reply/forward/delete/move messages, list attachments | Mail.Read, Mail.ReadWrite, Mail.Send |
| **Outlook Calendar** | list calendars, list/get/create/update/delete events, calendar view, find meeting times | Calendars.Read, Calendars.ReadWrite, Calendars.Read.Shared |
| **Teams** | list joined teams, list channels/members, list/send/reply channel messages, list/send chat messages | Team.ReadBasic.All, Channel.ReadBasic.All, Chat.Read, ChatMessage.Read, ChatMessage.Send, ChannelMessage.Read.All, ChannelMessage.Send |
| **SharePoint & OneDrive** | search/get sites, list/get lists & items, list drives & folders, download files, search drives | Sites.Read.All, Files.Read, Files.ReadWrite |
| **Users** | get current user, list/search users, get manager, get direct reports | User.Read, User.Read.All |

## Prerequisites

1. An Azure AD app registration with the required Graph API **delegated** permissions
2. A valid Microsoft Graph API access token with the scopes you need

## Setup

```bash
cd mcp_servers/ms365_graph
uv pip install -r requirements.txt
```

## Usage

### Set your access token

```bash
export MS365_ACCESS_TOKEN="eyJ0eXAi..."
```

### Run the server

```bash
# stdio (default, for MCP clients like Claude Desktop)
python server.py

# or via fastmcp CLI
fastmcp run server.py:mcp

# HTTP transport (for network access)
fastmcp run server.py:mcp --transport http --port 8000
```

### Claude Desktop / Claude Code config

```json
{
  "mcpServers": {
    "ms365": {
      "command": "python",
      "args": ["/path/to/mcp_servers/ms365_graph/server.py"],
      "env": {
        "MS365_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

### With a deepagent example

Use FastMCP's client to connect from your agent code:

```python
from fastmcp import Client

async with Client("mcp_servers/ms365_graph/server.py") as client:
    result = await client.call_tool("list_mail_messages", {"top": 5})
```

## Getting an Access Token

Use the [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) for quick testing, or authenticate via MSAL:

```bash
# Interactive device code flow (example)
pip install msal
python -c "
import msal, os
app = msal.PublicClientApplication(
    'YOUR_CLIENT_ID',
    authority='https://login.microsoftonline.com/YOUR_TENANT_ID'
)
flow = app.initiate_device_flow(scopes=['Mail.Read', 'Calendars.Read', 'Team.ReadBasic.All', 'Sites.Read.All'])
print(flow['message'])
result = app.acquire_token_by_device_flow(flow)
print(result['access_token'])
"
```

## Scope Validation

On startup, the server decodes the JWT access token's `scp` claim and disables any tools whose required Graph API scopes are missing. This prevents confusing 403 errors at runtime — the MCP client only sees tools the token can actually use.

Example: a token with only `Mail.Read Calendars.Read User.Read` will have 37 tools disabled, leaving only the 11 read-only mail/calendar/user tools available.

See [scope_handling.md](../../examples/gemini_mcp_agent/scope_handling.md) for the full token lifecycle, refresh strategy, and architecture guide.

## Architecture

```
ms365_graph/
├── server.py           # FastMCP entry point, registers tools & runs scope validation
├── graph_client.py     # Async HTTP client for Graph API (BYOT auth)
├── scope_validator.py  # JWT scope decoder & tool gating logic
├── tools/
│   ├── mail.py         # Outlook mail tools (9 tools)
│   ├── calendar.py     # Outlook calendar tools (8 tools)
│   ├── teams.py        # Teams channels & chats (14 tools)
│   ├── sharepoint.py   # SharePoint & OneDrive (14 tools)
│   └── users.py        # User profile tools (4 tools)
└── requirements.txt
```

Inspired by [Softeria/ms-365-mcp-server](https://github.com/Softeria/ms-365-mcp-server) (TypeScript), rebuilt in Python with FastMCP.
