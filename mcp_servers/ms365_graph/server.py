"""
Microsoft 365 MCP Server — Python/FastMCP

A Model Context Protocol server exposing Microsoft Graph API tools
for Outlook (mail + calendar), Teams, SharePoint/OneDrive, and user profiles.

Auth: Bring Your Own Token (BYOT) via MS365_ACCESS_TOKEN env var.
Token scopes are validated on startup — tools without the required
permissions are automatically disabled.
"""

import logging
import sys
from pathlib import Path

# Ensure the server's own directory is on the import path so tool modules
# can import graph_client regardless of how the server is launched.
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

from fastmcp import FastMCP

from scope_validator import validate_and_filter_tools
from tools import calendar, mail, sharepoint, teams, users

mcp = FastMCP(
    "MS365 Graph",
    instructions=(
        "Microsoft 365 MCP server powered by the Graph API. "
        "Provides tools for Outlook mail & calendar, Teams channels & chats, "
        "SharePoint sites & document libraries, and user profiles. "
        "Set the MS365_ACCESS_TOKEN environment variable with a valid "
        "Microsoft Graph API access token before connecting."
    ),
)

# Register all tool modules
mail.register(mcp)
calendar.register(mcp)
teams.register(mcp)
sharepoint.register(mcp)
users.register(mcp)

# Validate token scopes and disable tools the token can't support
enabled, disabled = validate_and_filter_tools(mcp)
if disabled:
    logging.getLogger("ms365_graph").warning(
        "%d tool(s) disabled due to missing scopes (see warnings above)", len(disabled)
    )
else:
    logging.getLogger("ms365_graph").info(
        "All %d tools enabled — token scopes look good", len(enabled)
    )

if __name__ == "__main__":
    mcp.run()
