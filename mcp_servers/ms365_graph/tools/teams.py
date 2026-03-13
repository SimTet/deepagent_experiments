"""Microsoft Teams tools — Microsoft Graph API Teams/Chats endpoints."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from graph_client import GraphClient

_client: GraphClient | None = None


def _get_client() -> GraphClient:
    global _client
    if _client is None:
        _client = GraphClient()
    return _client


def register(mcp: FastMCP) -> None:
    """Register all Teams tools on the FastMCP server."""

    # --- Teams & Channels ---

    @mcp.tool(tags={"teams"})
    async def list_joined_teams() -> dict:
        """List all Teams the current user has joined."""
        return await _get_client().get("/me/joinedTeams")

    @mcp.tool(tags={"teams"})
    async def get_team(
        team_id: Annotated[str, Field(description="The team ID")],
    ) -> dict:
        """Get details of a specific Team."""
        return await _get_client().get(f"/teams/{team_id}")

    @mcp.tool(tags={"teams"})
    async def list_team_channels(
        team_id: Annotated[str, Field(description="The team ID")],
    ) -> dict:
        """List all channels in a Team."""
        return await _get_client().get(f"/teams/{team_id}/channels")

    @mcp.tool(tags={"teams"})
    async def list_team_members(
        team_id: Annotated[str, Field(description="The team ID")],
    ) -> dict:
        """List members of a Team."""
        return await _get_client().get(f"/teams/{team_id}/members")

    @mcp.tool(tags={"teams"})
    async def list_channel_messages(
        team_id: Annotated[str, Field(description="The team ID")],
        channel_id: Annotated[str, Field(description="The channel ID")],
        top: Annotated[
            int, Field(description="Max messages to return", ge=1, le=50)
        ] = 20,
    ) -> dict:
        """List messages in a Teams channel."""
        return await _get_client().get(
            f"/teams/{team_id}/channels/{channel_id}/messages",
            params={"$top": top},
        )

    @mcp.tool(tags={"teams"})
    async def get_channel_message(
        team_id: Annotated[str, Field(description="The team ID")],
        channel_id: Annotated[str, Field(description="The channel ID")],
        message_id: Annotated[str, Field(description="The message ID")],
    ) -> dict:
        """Get a specific message from a Teams channel."""
        return await _get_client().get(
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}"
        )

    @mcp.tool(tags={"teams"})
    async def send_channel_message(
        team_id: Annotated[str, Field(description="The team ID")],
        channel_id: Annotated[str, Field(description="The channel ID")],
        content: Annotated[str, Field(description="Message content (HTML supported)")],
    ) -> dict:
        """Send a message to a Teams channel."""
        return await _get_client().post(
            f"/teams/{team_id}/channels/{channel_id}/messages",
            {"body": {"contentType": "html", "content": content}},
        )

    @mcp.tool(tags={"teams"})
    async def reply_to_channel_message(
        team_id: Annotated[str, Field(description="The team ID")],
        channel_id: Annotated[str, Field(description="The channel ID")],
        message_id: Annotated[str, Field(description="The parent message ID")],
        content: Annotated[str, Field(description="Reply content (HTML supported)")],
    ) -> dict:
        """Reply to a message in a Teams channel."""
        return await _get_client().post(
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies",
            {"body": {"contentType": "html", "content": content}},
        )

    @mcp.tool(tags={"teams"})
    async def list_channel_message_replies(
        team_id: Annotated[str, Field(description="The team ID")],
        channel_id: Annotated[str, Field(description="The channel ID")],
        message_id: Annotated[str, Field(description="The parent message ID")],
    ) -> dict:
        """List replies to a message in a Teams channel."""
        return await _get_client().get(
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        )

    # --- Chats (1:1 and group chats) ---

    @mcp.tool(tags={"teams", "chat"})
    async def list_chats(
        top: Annotated[
            int, Field(description="Max chats to return", ge=1, le=50)
        ] = 20,
        filter: Annotated[
            str | None,
            Field(description="OData $filter, e.g. \"chatType eq 'oneOnOne'\""),
        ] = None,
    ) -> dict:
        """List the current user's Teams chats (1:1 and group)."""
        params: dict = {"$top": top}
        if filter:
            params["$filter"] = filter
        return await _get_client().get("/me/chats", params=params)

    @mcp.tool(tags={"teams", "chat"})
    async def get_chat(
        chat_id: Annotated[str, Field(description="The chat ID")],
    ) -> dict:
        """Get details of a specific chat."""
        return await _get_client().get(f"/chats/{chat_id}")

    @mcp.tool(tags={"teams", "chat"})
    async def list_chat_messages(
        chat_id: Annotated[str, Field(description="The chat ID")],
        top: Annotated[
            int, Field(description="Max messages to return", ge=1, le=50)
        ] = 20,
    ) -> dict:
        """List messages in a Teams chat."""
        return await _get_client().get(
            f"/chats/{chat_id}/messages", params={"$top": top}
        )

    @mcp.tool(tags={"teams", "chat"})
    async def send_chat_message(
        chat_id: Annotated[str, Field(description="The chat ID")],
        content: Annotated[str, Field(description="Message content (HTML supported)")],
    ) -> dict:
        """Send a message in a Teams chat."""
        return await _get_client().post(
            f"/chats/{chat_id}/messages",
            {"body": {"contentType": "html", "content": content}},
        )
