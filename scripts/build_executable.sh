#!/usr/bin/env bash
set -e
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"
DIST_DIR="$REPO_DIR/dist"

pyinstaller milo_core/main.py \
  --onefile \
  --name milo \
  --distpath "$DIST_DIR" \
  --add-data "plugins:plugins" \
  --add-data ".n8n/workflows:.n8n/workflows"

MODEL_DIR="models/gemma-3-4b-it"
MODEL_FILE="$MODEL_DIR/gemma-2-9b-it-Q4_K_M.gguf"
if [ ! -f "$MODEL_FILE" ]; then
  echo "Gemma model not found. Downloading..."
  "$REPO_DIR/model_download.sh"
fi

"$DIST_DIR/milo" "$@"
