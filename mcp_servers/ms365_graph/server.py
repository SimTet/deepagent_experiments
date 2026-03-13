"""
Microsoft 365 MCP Server — Python/FastMCP

A Model Context Protocol server exposing Microsoft Graph API tools
for Outlook (mail + calendar), Teams, SharePoint/OneDrive, and user profiles.

Auth: Bring Your Own Token (BYOT) via MS365_ACCESS_TOKEN env var.
"""

import sys
from pathlib import Path

# Ensure the server's own directory is on the import path so tool modules
# can import graph_client regardless of how the server is launched.
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP

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

# Register tool modules
mail.register(mcp)
calendar.register(mcp)
teams.register(mcp)
sharepoint.register(mcp)
users.register(mcp)

if __name__ == "__main__":
    mcp.run()
