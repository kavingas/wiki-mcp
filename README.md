# Wiki MCP

MCP server that creates Confluence articles via the Confluence REST API v1 (e.g. wiki.corp.adobe.com). Based on `create-confluence-article.js`.

## Setup

```bash
uv sync
```

Create a `.env` in the project root (or set env vars):

```env
CONFLUENCE_BASE_URL=https://wiki.corp.adobe.com
CONFLUENCE_API_TOKEN=your-api-token
```

Optional: `CONFLUENCE_SPACE_KEY` can be set as a default but is usually passed per tool call.

## Run the server

Stdio (for Cursor / MCP clients):

```bash
uv run python main.py
```

Or with the MCP CLI:

```bash
uv run mcp run main.py
```

## Cursor MCP config

Add to **Cursor Settings → MCP** or to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "wiki": {
      "command": "uv",
      "args": ["run", "python", "/Users/kavingas/VSCodeProjects/wiki-mcp/main.py"],
      "env": {
        "CONFLUENCE_BASE_URL": "https://wiki.corp.adobe.com",
        "CONFLUENCE_API_TOKEN": "<your-token>"
      }
    }
  }
}
```

Use your actual project path and token. You can omit `env` if you use a `.env` file in the project directory.

## Tools

### create_confluence_article

Creates a Confluence page from a **.wiki file** (Confluence wiki markup only; not HTML, not raw Markdown).

**For LLMs:** If the user provides Markdown, convert it to [Confluence wiki markup](https://confluence.atlassian.com/doc/confluence-wiki-markup-251003035.html) and write it to a `.wiki` file, then pass that file path. Examples: `# Heading` → `h1. Heading`; `**bold**` → `*bold*`; `- item` → `* item`; `[text](url)` → `[text|url]`.

| Argument     | Required | Description |
|--------------|----------|-------------|
| `title`      | Yes      | Page title |
| `body_file`  | Yes      | **Absolute path** to a **.wiki** file containing Confluence wiki markup |
| `space_key`  | No       | Space key (default: ~kavingas) |
| `parent_id`  | No       | Parent page ID |

## Relation to create-confluence-article.js

This MCP exposes the same Confluence REST API v1 flow as the Node script:

- `POST /rest/api/content` with Bearer token
- Same payload shape: `type`, `title`, `space`, `body.storage`, optional `ancestors`

Use the MCP from Cursor to create pages via the AI; use the JS script for one-off CLI runs.
