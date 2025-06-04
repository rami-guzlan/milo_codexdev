#!/usr/bin/env bash
set -e
MODEL_DIR="models/gemma-3-4b-it"
mkdir -p "$MODEL_DIR"

if ! command -v huggingface-cli >/dev/null 2>&1; then
  echo "huggingface-cli not found. Install with: pip install huggingface_hub" >&2
  exit 1
fi

huggingface-cli download google/gemma-3-4b-it --local-dir "$MODEL_DIR" --local-dir-use-symlinks False

echo "Model downloaded to $MODEL_DIR"
