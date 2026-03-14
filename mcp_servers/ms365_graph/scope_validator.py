"""Validate Microsoft Graph API token scopes and gate tool availability."""

import base64
import json
import logging
import os

logger = logging.getLogger("ms365_graph")

# Maps each tool name to the minimum Graph API scope(s) required.
# A tool is enabled if the token contains ANY of its listed scopes
# (higher-privilege scopes like Mail.ReadWrite imply Mail.Read).
TOOL_SCOPES: dict[str, list[str]] = {
    # Mail
    "list_mail_folders": ["Mail.Read", "Mail.ReadWrite"],
    "list_mail_messages": ["Mail.Read", "Mail.ReadWrite"],
    "get_mail_message": ["Mail.Read", "Mail.ReadWrite"],
    "send_mail": ["Mail.Send"],
    "reply_to_mail": ["Mail.Send"],
    "forward_mail": ["Mail.Send"],
    "delete_mail_message": ["Mail.ReadWrite"],
    "move_mail_message": ["Mail.ReadWrite"],
    "list_mail_attachments": ["Mail.Read", "Mail.ReadWrite"],
    # Calendar
    "list_calendars": ["Calendars.Read", "Calendars.ReadWrite"],
    "list_calendar_events": ["Calendars.Read", "Calendars.ReadWrite"],
    "get_calendar_event": ["Calendars.Read", "Calendars.ReadWrite"],
    "get_calendar_view": ["Calendars.Read", "Calendars.ReadWrite"],
    "create_calendar_event": ["Calendars.ReadWrite"],
    "update_calendar_event": ["Calendars.ReadWrite"],
    "delete_calendar_event": ["Calendars.ReadWrite"],
    "find_meeting_times": ["Calendars.Read.Shared", "Calendars.ReadWrite"],
    # Teams — channels
    "list_joined_teams": ["Team.ReadBasic.All"],
    "get_team": ["Team.ReadBasic.All"],
    "list_team_channels": ["Channel.ReadBasic.All"],
    "list_team_members": ["TeamMember.Read.All"],
    "list_channel_messages": ["ChannelMessage.Read.All"],
    "get_channel_message": ["ChannelMessage.Read.All"],
    "send_channel_message": ["ChannelMessage.Send"],
    "reply_to_channel_message": ["ChannelMessage.Send"],
    "list_channel_message_replies": ["ChannelMessage.Read.All"],
    # Teams — chats
    "list_chats": ["Chat.Read", "Chat.ReadWrite"],
    "get_chat": ["Chat.Read", "Chat.ReadWrite"],
    "list_chat_messages": ["ChatMessage.Read"],
    "send_chat_message": ["ChatMessage.Send"],
    # SharePoint & OneDrive
    "search_sharepoint_sites": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "get_sharepoint_site": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "get_sharepoint_site_by_path": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "list_sharepoint_lists": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "get_sharepoint_list": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "list_sharepoint_list_items": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "get_sharepoint_list_item": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "list_site_drives": ["Sites.Read.All", "Sites.ReadWrite.All"],
    "list_my_drives": ["Files.Read", "Files.ReadWrite"],
    "list_drive_root_children": ["Files.Read", "Files.ReadWrite"],
    "list_folder_children": ["Files.Read", "Files.ReadWrite"],
    "get_drive_item": ["Files.Read", "Files.ReadWrite"],
    "get_file_download_url": ["Files.Read", "Files.ReadWrite"],
    "search_drive": ["Files.Read", "Files.ReadWrite"],
    # Users
    "get_current_user": ["User.Read"],
    "list_users": ["User.Read.All"],
    "get_my_manager": ["User.Read"],
    "get_my_direct_reports": ["User.Read"],
}


def decode_token_scopes(token: str) -> set[str]:
    """Decode the scp (scope) claim from a JWT access token without verification.

    We only read claims to check which scopes were granted — we don't
    validate the signature (that's the Graph API's job).
    """
    try:
        # JWT = header.payload.signature — we need the payload
        payload = token.split(".")[1]
        # Add padding for base64url
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        claims = json.loads(base64.urlsafe_b64decode(payload))
        # Delegated tokens use "scp" (space-separated string)
        # App-only tokens use "roles" (list of strings)
        scp = claims.get("scp", "")
        if isinstance(scp, str):
            scopes = set(scp.split())
        else:
            scopes = set(scp)
        roles = claims.get("roles", [])
        scopes.update(roles)
        return scopes
    except Exception as e:
        logger.warning("Could not decode token scopes: %s", e)
        return set()


def validate_and_filter_tools(
    mcp_server,
    token: str | None = None,
) -> tuple[set[str], set[str]]:
    """Check token scopes and remove tools that lack required permissions.

    Returns (enabled_tools, disabled_tools).
    """
    token = token or os.environ.get("MS365_ACCESS_TOKEN", "")
    if not token:
        logger.warning("No access token available — cannot validate scopes")
        return set(), set()

    granted = decode_token_scopes(token)
    if not granted:
        logger.warning(
            "Token has no scopes — either it's an opaque token or decoding failed. "
            "All tools remain enabled (scope errors will surface at call time)."
        )
        return set(TOOL_SCOPES.keys()), set()

    logger.info("Token scopes: %s", ", ".join(sorted(granted)))

    enabled: set[str] = set()
    disabled: set[str] = set()

    for tool_name, required_any_of in TOOL_SCOPES.items():
        if any(scope in granted for scope in required_any_of):
            enabled.add(tool_name)
        else:
            disabled.add(tool_name)
            logger.warning(
                "Disabling tool '%s' — requires one of [%s] but token has none of them",
                tool_name,
                ", ".join(required_any_of),
            )

    # Actually remove disabled tools from the server
    for tool_name in disabled:
        try:
            # Use local_provider API if available (FastMCP >= 3.x),
            # fall back to deprecated remove_tool for older versions.
            if hasattr(mcp_server, "local_provider"):
                mcp_server.local_provider.remove_tool(tool_name)
            else:
                mcp_server.remove_tool(tool_name)
        except Exception:
            pass  # Tool may not exist if registration order changed

    return enabled, disabled
