"""Outlook Mail tools — Microsoft Graph API /me/messages endpoints."""

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
    """Register all mail tools on the FastMCP server."""

    @mcp.tool(tags={"mail", "outlook"})
    async def list_mail_folders() -> dict:
        """List all mail folders (Inbox, Sent, Drafts, etc.)."""
        return await _get_client().get("/me/mailFolders")

    @mcp.tool(tags={"mail", "outlook"})
    async def list_mail_messages(
        folder_id: Annotated[
            str | None,
            Field(description="Mail folder ID. If omitted, searches all messages."),
        ] = None,
        filter: Annotated[
            str | None,
            Field(description="OData $filter expression, e.g. \"isRead eq false\""),
        ] = None,
        search: Annotated[
            str | None,
            Field(description="Free-text search query across subject/body/from"),
        ] = None,
        select: Annotated[
            str | None,
            Field(
                description="Comma-separated fields to return, e.g. \"subject,from,receivedDateTime\""
            ),
        ] = None,
        top: Annotated[
            int, Field(description="Max number of messages to return", ge=1, le=100)
        ] = 25,
        orderby: Annotated[
            str | None,
            Field(
                description="OData $orderby, e.g. \"receivedDateTime desc\""
            ),
        ] = None,
    ) -> dict:
        """List email messages from Outlook. Supports filtering, searching, and sorting."""
        path = f"/me/mailFolders/{folder_id}/messages" if folder_id else "/me/messages"
        params: dict = {"$top": top}
        if filter:
            params["$filter"] = filter
        if search:
            params["$search"] = f'"{search}"'
        if select:
            params["$select"] = select
        if orderby:
            params["$orderby"] = orderby
        return await _get_client().get(path, params=params)

    @mcp.tool(tags={"mail", "outlook"})
    async def get_mail_message(
        message_id: Annotated[str, Field(description="The message ID")],
        select: Annotated[
            str | None,
            Field(description="Comma-separated fields to return"),
        ] = None,
    ) -> dict:
        """Get a specific email message by ID, including its full body."""
        params = {}
        if select:
            params["$select"] = select
        return await _get_client().get(
            f"/me/messages/{message_id}", params=params or None
        )

    @mcp.tool(tags={"mail", "outlook"})
    async def send_mail(
        subject: Annotated[str, Field(description="Email subject")],
        body: Annotated[str, Field(description="Email body (HTML supported)")],
        to_recipients: Annotated[
            list[str],
            Field(description="List of recipient email addresses"),
        ],
        cc_recipients: Annotated[
            list[str] | None,
            Field(description="List of CC email addresses"),
        ] = None,
        importance: Annotated[
            str | None,
            Field(description="low, normal, or high"),
        ] = None,
    ) -> dict:
        """Send an email via Outlook."""
        message: dict = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body},
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to_recipients
            ],
        }
        if cc_recipients:
            message["ccRecipients"] = [
                {"emailAddress": {"address": addr}} for addr in cc_recipients
            ]
        if importance:
            message["importance"] = importance
        return await _get_client().post("/me/sendMail", {"message": message})

    @mcp.tool(tags={"mail", "outlook"})
    async def reply_to_mail(
        message_id: Annotated[str, Field(description="ID of the message to reply to")],
        comment: Annotated[str, Field(description="Reply body (HTML supported)")],
        reply_all: Annotated[
            bool, Field(description="Reply to all recipients")
        ] = False,
    ) -> dict:
        """Reply to an email message."""
        action = "replyAll" if reply_all else "reply"
        return await _get_client().post(
            f"/me/messages/{message_id}/{action}", {"comment": comment}
        )

    @mcp.tool(tags={"mail", "outlook"})
    async def forward_mail(
        message_id: Annotated[str, Field(description="ID of the message to forward")],
        to_recipients: Annotated[
            list[str], Field(description="Email addresses to forward to")
        ],
        comment: Annotated[
            str | None, Field(description="Optional comment to include")
        ] = None,
    ) -> dict:
        """Forward an email message."""
        body: dict = {
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to_recipients
            ],
        }
        if comment:
            body["comment"] = comment
        return await _get_client().post(
            f"/me/messages/{message_id}/forward", body
        )

    @mcp.tool(tags={"mail", "outlook"})
    async def delete_mail_message(
        message_id: Annotated[str, Field(description="ID of the message to delete")],
    ) -> dict:
        """Delete an email message."""
        return await _get_client().delete(f"/me/messages/{message_id}")

    @mcp.tool(tags={"mail", "outlook"})
    async def move_mail_message(
        message_id: Annotated[str, Field(description="ID of the message to move")],
        destination_folder_id: Annotated[
            str,
            Field(
                description="Destination folder ID (use list_mail_folders to find IDs)"
            ),
        ],
    ) -> dict:
        """Move an email message to a different folder."""
        return await _get_client().post(
            f"/me/messages/{message_id}/move",
            {"destinationId": destination_folder_id},
        )

    @mcp.tool(tags={"mail", "outlook"})
    async def list_mail_attachments(
        message_id: Annotated[str, Field(description="ID of the message")],
    ) -> dict:
        """List attachments on an email message."""
        return await _get_client().get(
            f"/me/messages/{message_id}/attachments"
        )
