"""Outlook Calendar tools — Microsoft Graph API /me/events endpoints."""

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
    """Register all calendar tools on the FastMCP server."""

    @mcp.tool(tags={"calendar", "outlook"})
    async def list_calendars() -> dict:
        """List all calendars for the current user."""
        return await _get_client().get("/me/calendars")

    @mcp.tool(tags={"calendar", "outlook"})
    async def list_calendar_events(
        calendar_id: Annotated[
            str | None,
            Field(description="Specific calendar ID. Omit for the default calendar."),
        ] = None,
        filter: Annotated[
            str | None,
            Field(description="OData $filter, e.g. \"start/dateTime ge '2025-01-01'\""),
        ] = None,
        select: Annotated[
            str | None,
            Field(description="Comma-separated fields to return"),
        ] = None,
        top: Annotated[
            int, Field(description="Max events to return", ge=1, le=100)
        ] = 25,
        orderby: Annotated[
            str | None,
            Field(description="OData $orderby, e.g. \"start/dateTime asc\""),
        ] = None,
    ) -> dict:
        """List calendar events. Use calendar_id for a specific calendar or omit for default."""
        path = (
            f"/me/calendars/{calendar_id}/events"
            if calendar_id
            else "/me/events"
        )
        params: dict = {"$top": top}
        if filter:
            params["$filter"] = filter
        if select:
            params["$select"] = select
        if orderby:
            params["$orderby"] = orderby
        return await _get_client().get(path, params=params)

    @mcp.tool(tags={"calendar", "outlook"})
    async def get_calendar_event(
        event_id: Annotated[str, Field(description="The event ID")],
    ) -> dict:
        """Get a specific calendar event by ID."""
        return await _get_client().get(f"/me/events/{event_id}")

    @mcp.tool(tags={"calendar", "outlook"})
    async def get_calendar_view(
        start_datetime: Annotated[
            str,
            Field(description="Start of time range (ISO 8601), e.g. '2025-03-01T00:00:00'"),
        ],
        end_datetime: Annotated[
            str,
            Field(description="End of time range (ISO 8601), e.g. '2025-03-31T23:59:59'"),
        ],
        calendar_id: Annotated[
            str | None,
            Field(description="Specific calendar ID. Omit for default."),
        ] = None,
        select: Annotated[
            str | None,
            Field(description="Comma-separated fields to return"),
        ] = None,
        top: Annotated[
            int, Field(description="Max events to return", ge=1, le=100)
        ] = 50,
        timezone: Annotated[
            str | None,
            Field(description="IANA timezone, e.g. 'Europe/Berlin'. Defaults to UTC."),
        ] = None,
    ) -> dict:
        """Get a calendar view (expanded recurring events) for a time range."""
        path = (
            f"/me/calendars/{calendar_id}/calendarView"
            if calendar_id
            else "/me/calendarView"
        )
        params: dict = {
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "$top": top,
        }
        if select:
            params["$select"] = select
        headers = {}
        if timezone:
            headers["Prefer"] = f'outlook.timezone="{timezone}"'
        return await _get_client().get(
            path, params=params, headers=headers or None
        )

    @mcp.tool(tags={"calendar", "outlook"})
    async def create_calendar_event(
        subject: Annotated[str, Field(description="Event subject/title")],
        start_datetime: Annotated[
            str, Field(description="Start time (ISO 8601), e.g. '2025-03-15T10:00:00'")
        ],
        end_datetime: Annotated[
            str, Field(description="End time (ISO 8601), e.g. '2025-03-15T11:00:00'")
        ],
        timezone: Annotated[
            str, Field(description="IANA timezone, e.g. 'Europe/Berlin'")
        ] = "UTC",
        body: Annotated[
            str | None, Field(description="Event body/description (HTML supported)")
        ] = None,
        location: Annotated[
            str | None, Field(description="Event location display name")
        ] = None,
        attendees: Annotated[
            list[str] | None,
            Field(description="List of attendee email addresses"),
        ] = None,
        is_online_meeting: Annotated[
            bool, Field(description="Create a Teams meeting link")
        ] = False,
        calendar_id: Annotated[
            str | None, Field(description="Target calendar ID. Omit for default.")
        ] = None,
    ) -> dict:
        """Create a new calendar event. Can optionally create a Teams meeting."""
        event: dict = {
            "subject": subject,
            "start": {"dateTime": start_datetime, "timeZone": timezone},
            "end": {"dateTime": end_datetime, "timeZone": timezone},
        }
        if body:
            event["body"] = {"contentType": "HTML", "content": body}
        if location:
            event["location"] = {"displayName": location}
        if attendees:
            event["attendees"] = [
                {
                    "emailAddress": {"address": addr},
                    "type": "required",
                }
                for addr in attendees
            ]
        if is_online_meeting:
            event["isOnlineMeeting"] = True
            event["onlineMeetingProvider"] = "teamsForBusiness"

        path = (
            f"/me/calendars/{calendar_id}/events"
            if calendar_id
            else "/me/events"
        )
        return await _get_client().post(path, event)

    @mcp.tool(tags={"calendar", "outlook"})
    async def update_calendar_event(
        event_id: Annotated[str, Field(description="The event ID to update")],
        subject: Annotated[str | None, Field(description="New subject")] = None,
        start_datetime: Annotated[
            str | None, Field(description="New start time (ISO 8601)")
        ] = None,
        end_datetime: Annotated[
            str | None, Field(description="New end time (ISO 8601)")
        ] = None,
        timezone: Annotated[str | None, Field(description="IANA timezone")] = None,
        body: Annotated[str | None, Field(description="New body (HTML)")] = None,
        location: Annotated[str | None, Field(description="New location")] = None,
    ) -> dict:
        """Update an existing calendar event. Only provided fields are changed."""
        patch: dict = {}
        if subject:
            patch["subject"] = subject
        if body:
            patch["body"] = {"contentType": "HTML", "content": body}
        if location:
            patch["location"] = {"displayName": location}
        if start_datetime:
            patch["start"] = {
                "dateTime": start_datetime,
                "timeZone": timezone or "UTC",
            }
        if end_datetime:
            patch["end"] = {
                "dateTime": end_datetime,
                "timeZone": timezone or "UTC",
            }
        return await _get_client().patch(f"/me/events/{event_id}", patch)

    @mcp.tool(tags={"calendar", "outlook"})
    async def delete_calendar_event(
        event_id: Annotated[str, Field(description="The event ID to delete")],
    ) -> dict:
        """Delete a calendar event."""
        return await _get_client().delete(f"/me/events/{event_id}")

    @mcp.tool(tags={"calendar", "outlook"})
    async def find_meeting_times(
        attendees: Annotated[
            list[str], Field(description="Email addresses of attendees")
        ],
        duration_minutes: Annotated[
            int, Field(description="Meeting duration in minutes", ge=5)
        ] = 30,
        timezone: Annotated[str, Field(description="IANA timezone")] = "UTC",
    ) -> dict:
        """Find available meeting times for a set of attendees."""
        body = {
            "attendees": [
                {"emailAddress": {"address": addr}, "type": "required"}
                for addr in attendees
            ],
            "meetingDuration": f"PT{duration_minutes}M",
            "timeConstraint": {
                "timeslots": [],
            },
            "returnSuggestionReasons": True,
        }
        return await _get_client().post("/me/findMeetingTimes", body)
