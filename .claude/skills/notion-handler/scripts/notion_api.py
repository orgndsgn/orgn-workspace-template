#!/usr/bin/env python3
"""
Notion API Handler for Claude Code
Supports: Database, Page, Block, Search operations
"""

import os
import sys
import json
import mimetypes
import argparse
import requests
from typing import Optional, Dict, Any, List

# Configuration
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_headers() -> Dict[str, str]:
    """Get API headers with token from environment."""
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }


def format_id(id_str: str) -> str:
    """Format page/database ID (remove hyphens if present)."""
    return id_str.replace("-", "")


def _is_phone_number(value: str) -> bool:
    """Check if value looks like a Korean phone number."""
    # Remove hyphens for checking
    digits = value.replace("-", "").replace(" ", "")
    # Korean mobile: 010xxxxxxxx (10-11 digits starting with 010)
    if digits.startswith("010") and len(digits) in [10, 11]:
        return True
    # Korean landline: 02xxxxxxxx, 031xxxxxxxx, etc.
    if digits.startswith("0") and len(digits) in [9, 10, 11] and digits.isdigit():
        return True
    return False


def parse_properties_schema(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert simplified property schema to Notion API format.

    Input formats:
    - "title" -> title property
    - "rich_text" -> rich_text property
    - "number" -> number property
    - "checkbox" -> checkbox property
    - "date" -> date property
    - "email" -> email property
    - "phone_number" -> phone_number property
    - "url" -> url property
    - {"select": ["opt1", "opt2"]} -> select with options
    - {"multi_select": ["opt1", "opt2"]} -> multi_select with options
    """
    result = {}
    for name, prop in properties.items():
        if isinstance(prop, str):
            # Simple type
            result[name] = {prop: {}}
        elif isinstance(prop, dict):
            # Complex type with options
            if "select" in prop:
                options = [{"name": opt} for opt in prop["select"]]
                result[name] = {"select": {"options": options}}
            elif "multi_select" in prop:
                options = [{"name": opt} for opt in prop["multi_select"]]
                result[name] = {"multi_select": {"options": options}}
            else:
                result[name] = prop
    return result


def _format_value_for_type(prop_type: str, value: Any) -> Dict[str, Any]:
    """Format a value into Notion API property format based on its type."""
    if prop_type == "title":
        return {"title": [{"text": {"content": str(value)}}]}
    if prop_type == "rich_text":
        return {"rich_text": [{"text": {"content": str(value)}}]}
    if prop_type == "number":
        return {"number": value if isinstance(value, (int, float)) else float(value)}
    if prop_type == "select":
        return {"select": {"name": str(value)}}
    if prop_type == "multi_select":
        items = value if isinstance(value, list) else [value]
        return {"multi_select": [{"name": str(v)} for v in items]}
    if prop_type == "checkbox":
        return {"checkbox": bool(value)}
    if prop_type == "date":
        if isinstance(value, str):
            return {"date": {"start": value}}
        if isinstance(value, dict):
            return {"date": value}
    if prop_type == "url":
        return {"url": str(value)}
    if prop_type == "email":
        return {"email": str(value)}
    if prop_type == "phone_number":
        return {"phone_number": str(value)}
    raise ValueError(f"Unsupported property type for value formatting: {prop_type}")


def parse_page_properties(properties: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convert simple property values to Notion API format for page creation.

    When `schema` (from get_database) is provided, types are determined authoritatively.
    Without schema, falls back to heuristics on value shape and field name.

    Dict values are passed through as raw Notion format — use this for files,
    people, relation, etc. Example:
        {"섬네일": {"files": [{"type": "file_upload", "file_upload": {"id": "..."}, "name": "x.png"}]}}
    """
    result = {}
    for name, value in properties.items():
        # Raw Notion format passthrough
        if isinstance(value, dict):
            result[name] = value
            continue

        # Schema-driven (authoritative)
        if schema and name in schema:
            prop_type = schema[name].get("type")
            if prop_type:
                result[name] = _format_value_for_type(prop_type, value)
                continue

        # Heuristic fallback (no schema)
        if name == "이름":
            result[name] = {"title": [{"text": {"content": str(value)}}]}
        elif isinstance(value, bool):
            result[name] = {"checkbox": value}
        elif isinstance(value, (int, float)):
            result[name] = {"number": value}
        elif isinstance(value, list):
            result[name] = {"multi_select": [{"name": str(v)} for v in value]}
        elif isinstance(value, str):
            if "@" in value and "." in value:
                result[name] = {"email": value}
            elif name == "연락처" or _is_phone_number(value):
                result[name] = {"phone_number": value}
            elif value.startswith("http"):
                result[name] = {"url": value}
            elif len(value) == 10 and value[4] == "-" and value[7] == "-":
                result[name] = {"date": {"start": value}}
            else:
                result[name] = {"rich_text": [{"text": {"content": value}}]}
    return result


# =============================================================================
# FILE UPLOAD
# =============================================================================

def upload_file(file_path: str, content_type: Optional[str] = None) -> Dict:
    """
    Upload a local file to Notion via File Upload API (2-step process).
    Returns dict with 'id' (upload_id) and 'name' (filename).

    Usage in files property:
        {"files": [{"type": "file_upload", "file_upload": {"id": <id>}, "name": <name>}]}
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    if not content_type:
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"

    # Step 1: Create file upload object
    create_url = f"{NOTION_API_BASE}/file_uploads"
    create_payload = {
        "filename": filename,
        "content_type": content_type,
    }
    create_resp = requests.post(create_url, headers=get_headers(), json=create_payload)
    create_data = create_resp.json()

    if "id" not in create_data:
        raise RuntimeError(f"Failed to create file upload: {json.dumps(create_data, ensure_ascii=False)}")

    upload_id = create_data["id"]
    upload_url = create_data.get("upload_url") or f"{NOTION_API_BASE}/file_uploads/{upload_id}/send"

    # Step 2: Send file (multipart/form-data, no Content-Type header)
    send_headers = get_headers()
    send_headers.pop("Content-Type", None)

    with open(file_path, "rb") as f:
        files = {"file": (filename, f, content_type)}
        send_resp = requests.post(upload_url, headers=send_headers, files=files)

    if send_resp.status_code not in (200, 201):
        raise RuntimeError(f"Failed to send file content: {send_resp.status_code} {send_resp.text}")

    return {"id": upload_id, "name": filename, "content_type": content_type}


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def create_database(parent_id: str, title: str, properties: Dict[str, Any]) -> Dict:
    """Create a new database under the specified parent page."""
    url = f"{NOTION_API_BASE}/databases"

    # Parse properties to Notion format
    notion_properties = parse_properties_schema(properties)

    payload = {
        "parent": {"type": "page_id", "page_id": format_id(parent_id)},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": notion_properties
    }

    response = requests.post(url, headers=get_headers(), json=payload)
    return response.json()


def get_database(database_id: str) -> Dict:
    """Get database information."""
    url = f"{NOTION_API_BASE}/databases/{format_id(database_id)}"
    response = requests.get(url, headers=get_headers())
    return response.json()


def query_database(database_id: str, filter_obj: Optional[Dict] = None,
                   sorts: Optional[List] = None) -> Dict:
    """Query database with optional filter and sorts."""
    url = f"{NOTION_API_BASE}/databases/{format_id(database_id)}/query"

    payload = {}
    if filter_obj:
        payload["filter"] = filter_obj
    if sorts:
        payload["sorts"] = sorts

    response = requests.post(url, headers=get_headers(), json=payload)
    return response.json()


def update_database(database_id: str, properties: Optional[Dict] = None,
                    title: Optional[str] = None) -> Dict:
    """Update database properties or title."""
    url = f"{NOTION_API_BASE}/databases/{format_id(database_id)}"

    payload = {}
    if title:
        payload["title"] = [{"type": "text", "text": {"content": title}}]
    if properties:
        payload["properties"] = parse_properties_schema(properties)

    response = requests.patch(url, headers=get_headers(), json=payload)
    return response.json()


# =============================================================================
# PAGE OPERATIONS
# =============================================================================

def create_page(parent_id: str, properties: Dict[str, Any],
                children: Optional[List] = None, is_database: bool = True) -> Dict:
    """Create a new page (as database item or standalone page)."""
    url = f"{NOTION_API_BASE}/pages"

    schema = None
    if is_database:
        # Fetch DB schema for authoritative type handling
        db_info = get_database(parent_id)
        if isinstance(db_info, dict) and "properties" in db_info:
            schema = db_info["properties"]
        parent = {"type": "database_id", "database_id": format_id(parent_id)}
    else:
        parent = {"type": "page_id", "page_id": format_id(parent_id)}

    payload = {
        "parent": parent,
        "properties": parse_page_properties(properties, schema)
    }

    if children:
        payload["children"] = children

    response = requests.post(url, headers=get_headers(), json=payload)
    return response.json()


def get_page(page_id: str) -> Dict:
    """Get page information."""
    url = f"{NOTION_API_BASE}/pages/{format_id(page_id)}"
    response = requests.get(url, headers=get_headers())
    return response.json()


def update_page(page_id: str, properties: Dict[str, Any]) -> Dict:
    """Update page properties. Fetches parent DB schema for type accuracy."""
    url = f"{NOTION_API_BASE}/pages/{format_id(page_id)}"

    schema = None
    page_info = get_page(page_id)
    parent = page_info.get("parent", {}) if isinstance(page_info, dict) else {}
    if parent.get("type") == "database_id":
        db_info = get_database(parent["database_id"])
        if isinstance(db_info, dict) and "properties" in db_info:
            schema = db_info["properties"]

    payload = {
        "properties": parse_page_properties(properties, schema)
    }

    response = requests.patch(url, headers=get_headers(), json=payload)
    return response.json()


def archive_page(page_id: str, archived: bool = True) -> Dict:
    """Archive (delete) a page."""
    url = f"{NOTION_API_BASE}/pages/{format_id(page_id)}"

    payload = {"archived": archived}

    response = requests.patch(url, headers=get_headers(), json=payload)
    return response.json()


# =============================================================================
# BLOCK OPERATIONS
# =============================================================================

def parse_blocks(blocks: List[Dict]) -> List[Dict]:
    """
    Convert simplified block format to Notion API format.

    Input formats:
    - {"type": "heading_1", "text": "Title"}
    - {"type": "heading_2", "text": "Subtitle"}
    - {"type": "heading_3", "text": "Section"}
    - {"type": "paragraph", "text": "Content"}
    - {"type": "bulleted_list_item", "text": "Item"}
    - {"type": "numbered_list_item", "text": "Item"}
    - {"type": "to_do", "text": "Task", "checked": false}
    - {"type": "divider"}
    - {"type": "image", "url": "https://..."} (external image)
    - {"type": "bookmark", "url": "https://..."}
    - {"type": "quote", "text": "Quote text"}
    - {"type": "callout", "text": "Callout text", "emoji": "💡"}
    - {"type": "code", "text": "code here", "language": "python"}
    - {"type": "toggle", "text": "Toggle title"}
    """
    result = []
    for block in blocks:
        block_type = block.get("type", "paragraph")

        if block_type == "divider":
            result.append({"object": "block", "type": "divider", "divider": {}})

        elif block_type == "image":
            # External image
            result.append({
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": block.get("url", "")
                    }
                }
            })

        elif block_type == "bookmark":
            # Bookmark (link preview)
            result.append({
                "object": "block",
                "type": "bookmark",
                "bookmark": {
                    "url": block.get("url", "")
                }
            })

        elif block_type == "quote":
            # Quote block
            result.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"type": "text", "text": {"content": block.get("text", "")}}]
                }
            })

        elif block_type == "callout":
            # Callout with emoji icon
            callout_content = {
                "rich_text": [{"type": "text", "text": {"content": block.get("text", "")}}]
            }
            if block.get("emoji"):
                callout_content["icon"] = {"type": "emoji", "emoji": block.get("emoji")}
            result.append({
                "object": "block",
                "type": "callout",
                "callout": callout_content
            })

        elif block_type == "code":
            # Code block with language
            result.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": block.get("text", "")}}],
                    "language": block.get("language", "plain text")
                }
            })

        elif block_type == "toggle":
            # Toggle block (can have children)
            result.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": block.get("text", "")}}]
                }
            })

        elif block_type in ["heading_1", "heading_2", "heading_3", "paragraph",
                           "bulleted_list_item", "numbered_list_item"]:
            result.append({
                "object": "block",
                "type": block_type,
                block_type: {
                    "rich_text": [{"type": "text", "text": {"content": block.get("text", "")}}]
                }
            })

        elif block_type == "to_do":
            result.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": block.get("text", "")}}],
                    "checked": block.get("checked", False)
                }
            })
    return result


def append_blocks(block_id: str, children: List[Dict]) -> Dict:
    """Append blocks to a page or block."""
    url = f"{NOTION_API_BASE}/blocks/{format_id(block_id)}/children"

    payload = {
        "children": parse_blocks(children)
    }

    response = requests.patch(url, headers=get_headers(), json=payload)
    return response.json()


def get_blocks(block_id: str) -> Dict:
    """Get child blocks of a page or block."""
    url = f"{NOTION_API_BASE}/blocks/{format_id(block_id)}/children"
    response = requests.get(url, headers=get_headers())
    return response.json()


def update_block(block_id: str, content: Dict) -> Dict:
    """Update a block's content."""
    url = f"{NOTION_API_BASE}/blocks/{format_id(block_id)}"
    response = requests.patch(url, headers=get_headers(), json=content)
    return response.json()


def delete_block(block_id: str) -> Dict:
    """Delete a block."""
    url = f"{NOTION_API_BASE}/blocks/{format_id(block_id)}"
    response = requests.delete(url, headers=get_headers())
    return response.json()


def delete_blocks(block_ids: List[str]) -> List[Dict]:
    """Delete multiple blocks."""
    results = []
    for block_id in block_ids:
        result = delete_block(block_id)
        results.append({"id": block_id, "result": result})
    return results


def get_all_blocks(block_id: str, recursive: bool = False) -> List[Dict]:
    """
    Get all child blocks with pagination support.
    If recursive=True, also fetches children of children.
    """
    all_blocks = []
    start_cursor = None

    while True:
        url = f"{NOTION_API_BASE}/blocks/{format_id(block_id)}/children"
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = requests.get(url, headers=get_headers(), params=params)
        data = response.json()

        if "results" in data:
            for block in data["results"]:
                all_blocks.append(block)
                # Recursively fetch children if needed
                if recursive and block.get("has_children"):
                    child_blocks = get_all_blocks(block["id"], recursive=True)
                    block["children"] = child_blocks

        if not data.get("has_more"):
            break
        start_cursor = data.get("next_cursor")

    return all_blocks


def clear_page(page_id: str) -> Dict:
    """Delete all blocks from a page."""
    blocks = get_all_blocks(page_id)
    block_ids = [b["id"] for b in blocks]
    if block_ids:
        results = delete_blocks(block_ids)
        return {"deleted_count": len(block_ids), "results": results}
    return {"deleted_count": 0, "message": "No blocks to delete"}


# =============================================================================
# SEARCH
# =============================================================================

def search(query: str, filter_type: Optional[str] = None) -> Dict:
    """
    Search Notion workspace.
    filter_type: "page" or "database"
    """
    url = f"{NOTION_API_BASE}/search"

    payload = {"query": query}
    if filter_type:
        payload["filter"] = {"value": filter_type, "property": "object"}

    response = requests.post(url, headers=get_headers(), json=payload)
    return response.json()


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Notion API Handler")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Database commands
    create_db_parser = subparsers.add_parser("create-db", help="Create database")
    create_db_parser.add_argument("--parent", required=True, help="Parent page ID")
    create_db_parser.add_argument("--title", required=True, help="Database title")
    create_db_parser.add_argument("--properties", required=True, help="Properties JSON")

    get_db_parser = subparsers.add_parser("get-db", help="Get database info")
    get_db_parser.add_argument("--id", required=True, help="Database ID")

    query_db_parser = subparsers.add_parser("query-db", help="Query database")
    query_db_parser.add_argument("--id", required=True, help="Database ID")
    query_db_parser.add_argument("--filter", help="Filter JSON")
    query_db_parser.add_argument("--sorts", help="Sorts JSON")

    update_db_parser = subparsers.add_parser("update-db", help="Update database")
    update_db_parser.add_argument("--id", required=True, help="Database ID")
    update_db_parser.add_argument("--properties", help="Properties JSON")
    update_db_parser.add_argument("--title", help="New title")

    # Page commands
    create_page_parser = subparsers.add_parser("create-page", help="Create page")
    create_page_parser.add_argument("--parent", required=True, help="Parent DB/page ID")
    create_page_parser.add_argument("--properties", required=True, help="Properties JSON")
    create_page_parser.add_argument("--children", help="Children blocks JSON")
    create_page_parser.add_argument("--standalone", action="store_true", help="Create as standalone page (not DB item)")

    get_page_parser = subparsers.add_parser("get-page", help="Get page info")
    get_page_parser.add_argument("--id", required=True, help="Page ID")

    update_page_parser = subparsers.add_parser("update-page", help="Update page")
    update_page_parser.add_argument("--id", required=True, help="Page ID")
    update_page_parser.add_argument("--properties", required=True, help="Properties JSON")

    archive_page_parser = subparsers.add_parser("archive-page", help="Archive page")
    archive_page_parser.add_argument("--id", required=True, help="Page ID")

    # Block commands
    append_blocks_parser = subparsers.add_parser("append-blocks", help="Append blocks")
    append_blocks_parser.add_argument("--id", required=True, help="Page/block ID")
    append_blocks_parser.add_argument("--blocks", required=True, help="Blocks JSON")

    get_blocks_parser = subparsers.add_parser("get-blocks", help="Get blocks")
    get_blocks_parser.add_argument("--id", required=True, help="Page/block ID")

    get_all_blocks_parser = subparsers.add_parser("get-all-blocks", help="Get all blocks with pagination")
    get_all_blocks_parser.add_argument("--id", required=True, help="Page/block ID")
    get_all_blocks_parser.add_argument("--recursive", action="store_true", help="Include nested children")

    update_block_parser = subparsers.add_parser("update-block", help="Update a block")
    update_block_parser.add_argument("--id", required=True, help="Block ID")
    update_block_parser.add_argument("--content", required=True, help="Block content JSON")

    delete_block_parser = subparsers.add_parser("delete-block", help="Delete a block")
    delete_block_parser.add_argument("--id", required=True, help="Block ID")

    delete_blocks_parser = subparsers.add_parser("delete-blocks", help="Delete multiple blocks")
    delete_blocks_parser.add_argument("--ids", required=True, help="Block IDs JSON array")

    clear_page_parser = subparsers.add_parser("clear-page", help="Delete all blocks from a page")
    clear_page_parser.add_argument("--id", required=True, help="Page ID")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search workspace")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--type", choices=["page", "database"], help="Filter by type")

    # File upload command
    upload_parser = subparsers.add_parser("upload-file", help="Upload a local file to Notion (returns upload_id)")
    upload_parser.add_argument("--path", required=True, help="Local file path")
    upload_parser.add_argument("--content-type", help="MIME type (auto-detected if omitted)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    result = None

    # Execute command
    if args.command == "create-db":
        props = json.loads(args.properties)
        result = create_database(args.parent, args.title, props)

    elif args.command == "get-db":
        result = get_database(args.id)

    elif args.command == "query-db":
        filter_obj = json.loads(args.filter) if args.filter else None
        sorts = json.loads(args.sorts) if args.sorts else None
        result = query_database(args.id, filter_obj, sorts)

    elif args.command == "update-db":
        props = json.loads(args.properties) if args.properties else None
        result = update_database(args.id, props, args.title)

    elif args.command == "create-page":
        props = json.loads(args.properties)
        children = json.loads(args.children) if args.children else None
        result = create_page(args.parent, props, children, not args.standalone)

    elif args.command == "get-page":
        result = get_page(args.id)

    elif args.command == "update-page":
        props = json.loads(args.properties)
        result = update_page(args.id, props)

    elif args.command == "archive-page":
        result = archive_page(args.id)

    elif args.command == "append-blocks":
        blocks = json.loads(args.blocks)
        result = append_blocks(args.id, blocks)

    elif args.command == "get-blocks":
        result = get_blocks(args.id)

    elif args.command == "get-all-blocks":
        blocks = get_all_blocks(args.id, args.recursive)
        result = {"blocks": blocks, "count": len(blocks)}

    elif args.command == "update-block":
        content = json.loads(args.content)
        result = update_block(args.id, content)

    elif args.command == "delete-block":
        result = delete_block(args.id)

    elif args.command == "delete-blocks":
        block_ids = json.loads(args.ids)
        result = delete_blocks(block_ids)

    elif args.command == "clear-page":
        result = clear_page(args.id)

    elif args.command == "search":
        result = search(args.query, args.type)

    elif args.command == "upload-file":
        result = upload_file(args.path, args.content_type)

    # Output result
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
