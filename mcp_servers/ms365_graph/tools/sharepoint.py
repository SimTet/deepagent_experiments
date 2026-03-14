"""SharePoint & OneDrive tools — Microsoft Graph API Sites/Drives endpoints."""

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
    """Register all SharePoint/OneDrive tools on the FastMCP server."""

    # --- Sites ---

    @mcp.tool(tags={"sharepoint"})
    async def search_sharepoint_sites(
        search: Annotated[
            str, Field(description="Search query to find SharePoint sites")
        ],
    ) -> dict:
        """Search for SharePoint sites by keyword."""
        # Graph API uses 'search' (not '$search') for the sites endpoint.
        return await _get_client().get("/sites", params={"search": search})

    @mcp.tool(tags={"sharepoint"})
    async def get_sharepoint_site(
        site_id: Annotated[str, Field(description="The site ID")],
    ) -> dict:
        """Get details of a specific SharePoint site."""
        return await _get_client().get(f"/sites/{site_id}")

    @mcp.tool(tags={"sharepoint"})
    async def get_sharepoint_site_by_path(
        hostname: Annotated[
            str,
            Field(description="SharePoint hostname, e.g. 'contoso.sharepoint.com'"),
        ],
        site_path: Annotated[
            str,
            Field(description="Site relative path, e.g. '/sites/engineering'"),
        ],
    ) -> dict:
        """Get a SharePoint site by its hostname and path."""
        return await _get_client().get(f"/sites/{hostname}:/{site_path.lstrip('/')}")

    # --- Lists ---

    @mcp.tool(tags={"sharepoint"})
    async def list_sharepoint_lists(
        site_id: Annotated[str, Field(description="The site ID")],
    ) -> dict:
        """List all lists in a SharePoint site."""
        return await _get_client().get(f"/sites/{site_id}/lists")

    @mcp.tool(tags={"sharepoint"})
    async def get_sharepoint_list(
        site_id: Annotated[str, Field(description="The site ID")],
        list_id: Annotated[str, Field(description="The list ID")],
    ) -> dict:
        """Get details of a specific SharePoint list."""
        return await _get_client().get(f"/sites/{site_id}/lists/{list_id}")

    @mcp.tool(tags={"sharepoint"})
    async def list_sharepoint_list_items(
        site_id: Annotated[str, Field(description="The site ID")],
        list_id: Annotated[str, Field(description="The list ID")],
        expand_fields: Annotated[
            bool,
            Field(description="Include field values for each item"),
        ] = True,
        top: Annotated[
            int, Field(description="Max items to return", ge=1, le=200)
        ] = 50,
        filter: Annotated[
            str | None,
            Field(description="OData $filter expression"),
        ] = None,
    ) -> dict:
        """List items in a SharePoint list."""
        params: dict = {"$top": top}
        if expand_fields:
            params["$expand"] = "fields"
        if filter:
            params["$filter"] = filter
        return await _get_client().get(
            f"/sites/{site_id}/lists/{list_id}/items", params=params
        )

    @mcp.tool(tags={"sharepoint"})
    async def get_sharepoint_list_item(
        site_id: Annotated[str, Field(description="The site ID")],
        list_id: Annotated[str, Field(description="The list ID")],
        item_id: Annotated[str, Field(description="The list item ID")],
    ) -> dict:
        """Get a specific item from a SharePoint list, including field values."""
        return await _get_client().get(
            f"/sites/{site_id}/lists/{list_id}/items/{item_id}",
            params={"$expand": "fields"},
        )

    # --- Drives (document libraries) ---

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def list_site_drives(
        site_id: Annotated[str, Field(description="The site ID")],
    ) -> dict:
        """List document libraries (drives) in a SharePoint site."""
        return await _get_client().get(f"/sites/{site_id}/drives")

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def list_my_drives() -> dict:
        """List the current user's OneDrive drives."""
        return await _get_client().get("/me/drives")

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def list_drive_root_children(
        drive_id: Annotated[str, Field(description="The drive ID")],
    ) -> dict:
        """List files and folders at the root of a drive."""
        return await _get_client().get(f"/drives/{drive_id}/root/children")

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def list_folder_children(
        drive_id: Annotated[str, Field(description="The drive ID")],
        item_id: Annotated[str, Field(description="The folder item ID")],
    ) -> dict:
        """List files and folders inside a specific folder."""
        return await _get_client().get(
            f"/drives/{drive_id}/items/{item_id}/children"
        )

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def get_drive_item(
        drive_id: Annotated[str, Field(description="The drive ID")],
        item_id: Annotated[str, Field(description="The item ID")],
    ) -> dict:
        """Get metadata for a specific file or folder in a drive."""
        return await _get_client().get(f"/drives/{drive_id}/items/{item_id}")

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def get_file_download_url(
        drive_id: Annotated[str, Field(description="The drive ID")],
        item_id: Annotated[str, Field(description="The file item ID")],
    ) -> dict:
        """Get a pre-authenticated download URL for a file. The /content endpoint
        returns a 302 redirect, so this fetches the item metadata with the
        @microsoft.graph.downloadUrl property instead."""
        return await _get_client().get(
            f"/drives/{drive_id}/items/{item_id}",
            params={"$select": "id,name,size,@microsoft.graph.downloadUrl"},
        )

    @mcp.tool(tags={"sharepoint", "onedrive"})
    async def search_drive(
        drive_id: Annotated[str, Field(description="The drive ID")],
        query: Annotated[str, Field(description="Search query")],
    ) -> dict:
        """Search for files and folders in a drive."""
        return await _get_client().get(
            f"/drives/{drive_id}/root/search(q='{query}')"
        )
