"""User profile & search tools — Microsoft Graph API /me and /users endpoints."""

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
    """Register user-related tools on the FastMCP server."""

    @mcp.tool(tags={"users"})
    async def get_current_user() -> dict:
        """Get the current authenticated user's profile."""
        return await _get_client().get("/me")

    @mcp.tool(tags={"users"})
    async def list_users(
        search: Annotated[
            str | None,
            Field(description="Search by displayName or mail, e.g. \"displayName:John\""),
        ] = None,
        filter: Annotated[
            str | None,
            Field(description="OData $filter, e.g. \"department eq 'Engineering'\""),
        ] = None,
        select: Annotated[
            str | None,
            Field(description="Comma-separated fields to return"),
        ] = None,
        top: Annotated[
            int, Field(description="Max users to return", ge=1, le=100)
        ] = 25,
    ) -> dict:
        """List or search users in the organization."""
        params: dict = {"$top": top}
        if search:
            params["$search"] = f'"{search}"'
        if filter:
            params["$filter"] = filter
        if select:
            params["$select"] = select
        headers = {}
        if search:
            headers["ConsistencyLevel"] = "eventual"
        return await _get_client().get(
            "/users", params=params, headers=headers or None
        )

    @mcp.tool(tags={"users"})
    async def get_my_manager() -> dict:
        """Get the current user's manager."""
        return await _get_client().get("/me/manager")

    @mcp.tool(tags={"users"})
    async def get_my_direct_reports() -> dict:
        """Get the current user's direct reports."""
        return await _get_client().get("/me/directReports")
