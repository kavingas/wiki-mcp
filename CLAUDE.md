# Wiki MCP — Claude Code Guide

## Project Overview

MCP server that exposes tools to create, read, and update Confluence pages via Confluence REST API v1.

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastMCP server entry point; registers tools and prompts |
| `wiki_tools.py` | All Confluence tool implementations; add new tools here |
| `wiki_mcp_prompts.py` | MCP prompt registrations |
| `pyproject.toml` | Package metadata and version |
| `scripts/release.sh` | Build, version bump, git tag, and publish to PyPI |

## Development

```bash
uv sync        # install dependencies
uv run main.py # run the MCP server locally
```

Environment variables are loaded from `.env` (via `python-dotenv`). Required: `CONFLUENCE_API_TOKEN`. See README for the full variable list.

## Adding a Tool

1. Implement an `async def` function in `wiki_tools.py`
2. Append it to the `tools` list at the bottom of `wiki_tools.py`

FastMCP uses the function signature and docstring as the tool schema — keep docstrings accurate.

## Body Content Rules

All Confluence page bodies must be written in **Confluence wiki markup** (not HTML, not Markdown). Body files must:
- Have a `.wiki` extension
- Use an absolute path when passed to tools

## Release

The release script handles version bump → build → git tag → publish in one step.

```bash
./scripts/release.sh
```

### What it does

1. **Bumps patch version** — increments `version` in `pyproject.toml` (`X.Y.Z` → `X.Y.Z+1`)
2. **Builds** — cleans `dist/` and runs `uv build`
3. **Git release** — commits `pyproject.toml` and creates a `vX.Y.Z` tag
4. **Publishes** — uploads to `https://sauronai.adobe.io/pypi` using credentials from `.env`

### Required `.env` keys for release

```
PYPI_USERNAME=your_username
PYPI_PASSWORD=your_password
```

### After release

Push the commit and tag to the remote:

```bash
git push && git push --tags
```

## PyPI Index

Package is published to and installed from the internal registry:

```
https://sauronai.adobe.io/pypi
```

Use `https://sauronai.adobe.io/pypi/simple/` as the index URL for `uv` / `pip`.
