"""Confluence MCP tools: create and manage Confluence pages via REST API v1."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

_BASE_URL = os.environ.get("CONFLUENCE_BASE_URL", "https://wiki.corp.adobe.com").rstrip("/")
_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN", "")


def _get_body_from_wiki_file(body_file: str) -> str:
    """Read Confluence wiki markup from a .wiki file."""
    path = Path(body_file)
    if not path.suffix.lower() == ".wiki":
        raise ValueError(
            f"Only .wiki files are accepted; got: {path.suffix or path.name!r}"
        )
    if not path.is_absolute():
        path = Path.cwd() / path
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

    Pass the path to a .wiki file containing Confluence wiki markup (not HTML, not Markdown).
    Uses CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN from environment.
    Required: title, body_file (path to a .wiki file). Optional: parent_id, space_key.
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


# List of tools to register with FastMCP (add_tool(tool) for each)
tools = [create_confluence_article]
