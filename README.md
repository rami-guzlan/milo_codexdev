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

### Hardware Recommendations
Running large language and speech models locally is resource-intensive. For a smooth experience, we recommend the following minimum hardware:

* **RAM:** **16 GB** or more. 32 GB is recommended for larger models.
* **GPU:** A dedicated NVIDIA GPU (for CUDA) with at least **8 GB of VRAM** is highly recommended for performant LLM inference. The application will fall back to the CPU, but this will be significantly slower.
* **Storage:** At least 20 GB of free space for models and dependencies.

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

You also need to download a voice for the Text-to-Speech engine. We recommend a standard quality voice to start:

```bash
# Download the Piper TTS voice model
wget '[https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true)' -O ./piper-voice.onnx
```
This command downloads the voice model and saves it as piper-voice.onnx in the root directory, where MILO expects to find it.

## Memory system
MILO stores long-term notes in a local ChromaDB instance under
`./milo_memory_db`. Each conversation session is summarized and verified
for usefulness before being saved. Older memories are consolidated into
weekly digests when the assistant starts.


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
Speech recognition is powered by `faster-whisper`, a high-performance implementation of OpenAI's Whisper model. Voice capture now uses a real-time Voice Activity Detection (VAD) model so MILO responds as soon as you speak. Text-to-speech uses `piper-tts`, a fast and local neural TTS system.

Audio capture and playback are handled by `ffmpeg` and `ffplay`. The VAD system relies on `PyAudio` which may require the `portaudio` development headers.

**Linux Example:**
```bash
sudo apt-get update && sudo apt-get install ffmpeg portaudio19-dev
```
macOS (using Homebrew):
```bash
brew install ffmpeg
```
## Running MILO
Start the assistant with:

```bash
poetry run milo-core
```

Stop it at any time with `Ctrl+C`. New plugins added to the `plugins/`
directory are discovered automatically when MILO starts.

## Conversational Interaction
MILO listens continuously and detects when you start and stop speaking using a Voice Activity Detection model. This allows for more natural back-and-forth conversation without fixed recording lengths.

## Configuration
The `milo-core` command accepts a few options to tune VAD behaviour:

```bash
poetry run milo-core --vad-threshold 0.6 --vad-silence-duration 1.0
```

* `--vad-threshold` – speech probability needed to consider audio as speech (0-1).
* `--vad-silence-duration` – seconds of silence before an utterance is finalized.

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
