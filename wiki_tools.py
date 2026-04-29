"""Wiki MCP tools: create and manage Confluence pages via REST API v1."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

_BASE_URL = os.environ.get("CONFLUENCE_BASE_URL", "https://wiki.corp.adobe.com").rstrip("/")
_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN", "")


def _get_body_from_wiki_file(body_file: str) -> str:
    """Read Confluence wiki markup from a .wiki file. body_file must be an absolute path."""
    path = Path(body_file)
    if not path.is_absolute():
        raise ValueError(
            "body_file must be an absolute path; got a relative path."
        )
    if not path.suffix.lower() == ".wiki":
        raise ValueError(
            f"Only .wiki files are accepted; got: {path.suffix or path.name!r}"
        )
    if not path.exists():
        raise FileNotFoundError(f"Wiki file not found: {path}")
    return path.read_text(encoding="utf-8")


def _build_view_url(page: dict[str, Any]) -> str:
    base = (page.get("_links") or {}).get("base", _BASE_URL)
    base = str(base).rstrip("/")
    return f"{base}/pages/viewpage.action?pageId={page.get('id', '')}"


async def create_confluence_article(
    title: str,
    body_file: str,
    space_key: str = "~kavingas",
    parent_id: str | None = None,
) -> str:
    """Create a Confluence page (article) via REST API v1.

    Pass the absolute path to a .wiki file containing Confluence wiki markup (not HTML, not Markdown).
    Uses CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN from environment.
    Required: title, body_file (absolute path to a .wiki file). Optional: parent_id, space_key.
    """
    token = _API_TOKEN or os.environ.get("CONFLUENCE_API_TOKEN")
    if not token:
        raise ValueError(
            "CONFLUENCE_API_TOKEN is not set. Set it in the environment or in .env."
        )

    body_value = _get_body_from_wiki_file(body_file)

    payload: dict[str, Any] = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": body_value,
                "representation": "wiki",
            }
        },
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{_BASE_URL}/rest/api/content",
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    text = resp.text
    if not resp.is_success:
        err_msg = f"Confluence {resp.status_code} {resp.reason_phrase}: {text}"
        raise RuntimeError(err_msg)

    page = json.loads(text) if text else {}
    view_url = _build_view_url(page) if page.get("id") else ""
    msg = f"Created page ID: {page.get('id', 'N/A')}"
    if view_url:
        msg += f"\nView URL: {view_url}"
    return msg


async def update_confluence_article(
    page_id: str,
    body_file: str,
    title: str | None = None,
) -> str:
    """Update an existing Confluence page via REST API v1.

    Fetches the current page to get version and metadata, then PUTs new body (and
    optionally a new title). body_file must be the absolute path to a .wiki file with Confluence wiki markup.
    Required: page_id, body_file (absolute path). Optional: title (if omitted, keeps existing title).
    """
    token = _API_TOKEN or os.environ.get("CONFLUENCE_API_TOKEN")
    if not token:
        raise ValueError(
            "CONFLUENCE_API_TOKEN is not set. Set it in the environment or in .env."
        )

    body_value = _get_body_from_wiki_file(body_file)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get current page (version, title, space) for the update payload
        get_resp = await client.get(
            f"{_BASE_URL}/rest/api/content/{page_id}",
            params={"expand": "version,space"},
            headers=headers,
        )
        if not get_resp.is_success:
            err_msg = f"Confluence GET {get_resp.status_code} {get_resp.reason_phrase}: {get_resp.text}"
            raise RuntimeError(err_msg)

        page = json.loads(get_resp.text) if get_resp.text else {}
        version = (page.get("version") or {}).get("number")
        if version is None:
            raise RuntimeError("Page response missing version; cannot update.")

        space_key = (page.get("space") or {}).get("key")
        if not space_key:
            raise RuntimeError("Page response missing space key; cannot update.")

        new_title = title if title is not None else page.get("title", "")
        if not new_title:
            raise RuntimeError("Page has no title and none was provided.")

        payload: dict[str, Any] = {
            "id": str(page.get("id", page_id)),
            "type": "page",
            "title": new_title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body_value,
                    "representation": "wiki",
                }
            },
            "version": {"number": version + 1},
        }

        put_resp = await client.put(
            f"{_BASE_URL}/rest/api/content/{page_id}",
            json=payload,
            headers=headers,
        )

    text = put_resp.text
    if not put_resp.is_success:
        err_msg = f"Confluence PUT {put_resp.status_code} {put_resp.reason_phrase}: {text}"
        raise RuntimeError(err_msg)

    updated = json.loads(text) if text else {}
    view_url = _build_view_url(updated) if updated.get("id") else ""
    msg = f"Updated page ID: {page_id}"
    if view_url:
        msg += f"\nView URL: {view_url}"
    return msg


async def get_confluence_page(page_id: str) -> str:
    """Fetch a Confluence page by ID and return its content.

    Returns the page title, view URL, version, and body content (storage format).
    Uses CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN from environment.
    Required: page_id (Confluence page ID, e.g. "123456789").
    """
    token = _API_TOKEN or os.environ.get("CONFLUENCE_API_TOKEN")
    if not token:
        raise ValueError(
            "CONFLUENCE_API_TOKEN is not set. Set it in the environment or in .env."
        )

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{_BASE_URL}/rest/api/content/{page_id}",
            params={"expand": "body.storage,version,space"},
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    text = resp.text
    if not resp.is_success:
        err_msg = f"Confluence GET {resp.status_code} {resp.reason_phrase}: {text}"
        raise RuntimeError(err_msg)

    page = json.loads(text) if text else {}
    title = page.get("title", "")
    view_url = _build_view_url(page) if page.get("id") else ""
    version_num = (page.get("version") or {}).get("number", "?")
    body_storage = (page.get("body") or {}).get("storage") or {}
    content = body_storage.get("value", "")
    representation = body_storage.get("representation", "storage")

    lines = [
        f"Title: {title}",
        f"Page ID: {page.get('id', page_id)}",
        f"Version: {version_num}",
        f"Representation: {representation}",
    ]
    if view_url:
        lines.append(f"View URL: {view_url}")
    lines.append("")
    lines.append("--- Content ---")
    lines.append(content if content.strip() else "(empty)")

    return "\n".join(lines)


# List of tools to register with FastMCP (add_tool(tool) for each)
tools = [create_confluence_article, update_confluence_article, get_confluence_page]
