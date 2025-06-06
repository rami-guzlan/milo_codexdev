# MILO - Minimal Input Life Organizer

MILO aims to give users a private, local-first assistant. All core reasoning and data stay on the machine. New features are built as plugins so the core remains small and extensible.

## Goals
- **Local-first**: keep user data on device and run the AI locally.
- **Plugin-based architecture**: skills live in the `plugins/` directory and are discovered by the `PluginManager`.

## Development setup
Install dependencies with Poetry:

```bash
poetry install
```

Poetry is the canonical way to manage MILO's Python dependencies.
If you need a `requirements.txt` for other tooling, generate it with

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Add a new dependency using:

```bash
poetry add <package_name>
```

## Model setup
Before downloading the weights you must authenticate with Hugging Face. Run
`huggingface-cli login` (or set the `HUGGINGFACE_TOKEN` environment variable)
so the CLI can access the model. You can also use SSH keys if you have them
configured on your Hugging Face account.

Download the model weights by running:

```bash
./model_download.sh
```

This script requires `huggingface-cli` and stores the model in
`models/gemma-3-4b-it`. The assistant expects the weights in this default
directory.


## Testing and formatting
Run tests with:

```bash
poetry run pytest
```

Format the codebase using:

```bash
poetry run ruff format .
```

Check linting with:

```bash
poetry run ruff check .
```

## Audio requirements
Speech recognition is powered by Whisper via the `openai-whisper` package.
Text-to-speech uses Coqui TTS from the `TTS` package. Audio capture and
playback are handled by `ffmpeg` and `ffplay`, so make sure these tools are
installed and available on your `PATH`.

Linux example:

```bash
sudo apt-get install ffmpeg
```

## Running MILO
Start the assistant with:

```bash
poetry run milo-core
```

Stop it at any time with `Ctrl+C`. New plugins added to the `plugins/`
directory are discovered automatically when MILO starts.

## Running n8n workflows
n8n acts as a local bridge to external services. Start an instance locally (Docker example):

```bash
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

Open the n8n editor at `http://localhost:5678` and import the JSON files from `.n8n/workflows/`. After configuring credentials you can trigger a workflow from Python:

```python
from milo_core.workflows import trigger_workflow

response = trigger_workflow("gmail_read", {"query": "label:inbox"})
print(response.status_code)
```

This sends a POST request to `http://localhost:5678/webhook/gmail_read`.
