# MILO - Minimal Input Life Organizer

MILO aims to give users a private, local-first assistant. All core reasoning and data stay on the machine. New features are built as plugins so the core remains small and extensible.

## Goals
- **Local-first**: keep user data on device and run the AI locally.
- **Plugin-based architecture**: skills live in the `plugins/` directory and are discovered by the `PluginManager`.

## Getting Started

This guide will walk you through setting up and running the MILO assistant on your local machine.

### 1. Prerequisites

Before you begin, ensure you have the following tools installed on your system. It is highly recommended to use a version manager like `asdf` or `mise` to handle different versions of these tools.

| Tool | Required Version | Notes |
| :--- | :--- | :--- |
| **Python** | `3.11.x` | The core language for the application. |
| **Node.js** | `20.x` | Recommended for n8n workflow development tools. |
| **ffmpeg** | Latest | Required for audio playback. |
| **Poetry** | Latest | The dependency manager for this project. |
| **PortAudio** | - | Required by `PyAudio` on Linux systems. |

### 2. Installation

Follow these steps to get the application running.

**A. Clone the Repository**

First, clone the project to your local machine:
```bash
git clone <your-repository-url>
cd MILO-Codex
```

**B. Install System Dependencies**

You need to install ffmpeg for audio processing and, on Linux, the portaudio development headers for the PyAudio library.

On Debian/Ubuntu (Linux):
```bash
sudo apt-get update && sudo apt-get install ffmpeg portaudio19-dev
```

On macOS (using Homebrew):
```bash
brew install ffmpeg portaudio
```

On Windows: You can install ffmpeg using a package manager like Chocolatey (`choco install ffmpeg`) or Scoop (`scoop install ffmpeg`). PortAudio is not typically required for PyAudio on Windows as wheels are pre-compiled.

**C. Install Python Dependencies**

This project uses Poetry to manage its Python packages. Install them with a single command:

```bash
poetry install
```

This will create a virtual environment and install all necessary libraries like faster-whisper, piper-tts, and llama-cpp-python.

### 3. Model Setup
MILO requires a local language model and a text-to-speech (TTS) voice model to function.

**A. Log in to Hugging Face**

You'll need to download the main language model from Hugging Face. First, authenticate your machine.

```bash
huggingface-cli login
```

Enter your Hugging Face token when prompted.

**B. Download the Language Model**

Run the provided script to download the quantized Gemma model. This will save it to the `models/` directory.

```bash
./model_download.sh
```

**C. Download the TTS Voice Model**

Next, download the pre-trained voice for the text-to-speech engine. The application expects this file to be in the root directory.

```bash
# Download the Piper TTS voice model
wget '[https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true](https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true)' -O ./piper-voice.onnx
```

### 4. Running MILO
Once all dependencies and models are in place, you can start the assistant with the following command:

```bash
poetry run milo-core
```

You can stop the assistant at any time by pressing Ctrl+C.
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
