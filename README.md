# Wiki MCP Server

MCP server to **create**, **read**, and **update** Confluence pages. Targets Confluence REST API v1 (e.g. `wiki.corp.adobe.com`).

---

## Tools

| Tool | Description |
|------|-------------|
| `create_confluence_article` | Create a new page. Required: `title`, `body_file` (absolute path to a `.wiki` file). Optional: `space_key` (default `~kavingas`), `parent_id`. |
| `get_confluence_page` | Fetch a page by ID. Returns title, version, view URL, and body content. Required: `page_id`. |
| `update_confluence_article` | Update an existing page. Required: `page_id`, `body_file` (absolute path to a `.wiki` file). Optional: `title` (if omitted, keeps existing title). |

**Note for LLMs:** All body content must be in [Confluence wiki markup](https://confluence.atlassian.com/doc/confluence-wiki-markup-251003035.html) — not HTML, not Markdown. Write the markup to a `.wiki` file and pass its absolute path. Examples: `# Heading` → `h1. Heading`; `**bold**` → `*bold*`; `- item` → `* item`; `[text](url)` → `[text|url]`.

---

## Installation Instructions

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Confluence API token (Personal Access Token)

### Authentication

Generate a token from your Confluence instance profile page and set it via environment variable.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONFLUENCE_BASE_URL` | No | Confluence base URL (default: `https://wiki.corp.adobe.com`) |
| `CONFLUENCE_API_TOKEN` | Yes | Bearer token for Confluence REST API auth |
| `CONFLUENCE_SPACE_KEY` | No | Default space key — can also be passed per tool call |

### Install (recommended via `uvx`)

Add to your MCP config — no separate install step needed.

```json
{
  "mcpServers": {
    "wiki": {
      "command": "uvx",
      "args": [
        "--index", "https://sauronai.adobe.io/pypi/simple/",
        "wiki-mcp"
      ],
      "env": {
        "CONFLUENCE_BASE_URL": "https://wiki.corp.adobe.com",
        "CONFLUENCE_API_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Or install explicitly with uv:

```bash
uv pip install --index https://sauronai.adobe.io/pypi/simple/ wiki-mcp
```

### Claude Code Setup

One-time CLI registration:

```bash
claude mcp add wiki \
  --env CONFLUENCE_BASE_URL=https://wiki.corp.adobe.com \
  --env CONFLUENCE_API_TOKEN=YOUR_TOKEN_HERE \
  -- uvx --index https://sauronai.adobe.io/pypi/simple/ wiki-mcp
```

Or add manually to `~/.claude/settings.json` or project `.claude/settings.json`.

### Cursor Setup

Edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project-level) with the JSON block above, then restart Cursor.

### Codex CLI Setup

Edit `~/.codex/config.yaml`:

```yaml
mcpServers:
  wiki:
    type: stdio
    command: uvx
    args:
      - --index
      - https://sauronai.adobe.io/pypi/simple/
      - wiki-mcp
    env:
      CONFLUENCE_BASE_URL: "https://wiki.corp.adobe.com"
      CONFLUENCE_API_TOKEN: "YOUR_TOKEN_HERE"
```

### Local Development

```bash
uv sync
uv run main.py
```
