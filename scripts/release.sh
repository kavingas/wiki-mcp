#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
PYPROJECT="$REPO_ROOT/pyproject.toml"
PYPI_URL="https://sauronai.adobe.io/pypi/"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env not found at $ENV_FILE" >&2
  exit 1
fi

# Read credentials from .env
PYPI_USERNAME=$(grep -E '^PYPI_USERNAME=' "$ENV_FILE" | head -1 | cut -d= -f2-)
PYPI_PASSWORD=$(grep -E '^PYPI_PASSWORD=' "$ENV_FILE" | head -1 | cut -d= -f2-)

if [[ -z "$PYPI_USERNAME" ]]; then
  echo "Error: PYPI_USERNAME not set in .env" >&2
  exit 1
fi
if [[ -z "$PYPI_PASSWORD" ]]; then
  echo "Error: PYPI_PASSWORD not set in .env" >&2
  exit 1
fi

cd "$REPO_ROOT"

# --- Bump version (patch: X.Y.Z -> X.Y.Z+1) ---
CURRENT_VERSION=$(grep -E '^version\s*=' "$PYPROJECT" | head -1 | sed 's/.*"\(.*\)".*/\1/')
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo "Bumping version: $CURRENT_VERSION -> $NEW_VERSION"
sed -i '' "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT"

# --- Build ---
echo "Cleaning dist/..."
rm -rf dist/

echo "Building $NEW_VERSION..."
uv build

# --- Git commit + tag ---
echo "Creating git release v$NEW_VERSION..."
git add "$PYPROJECT"
git commit -m "chore: release v$NEW_VERSION"
git tag "v$NEW_VERSION"

# --- Publish ---
echo "Publishing to $PYPI_URL..."
uv publish \
  --publish-url "$PYPI_URL" \
  --username "$PYPI_USERNAME" \
  --password "$PYPI_PASSWORD"

echo "Done. Released v$NEW_VERSION"
