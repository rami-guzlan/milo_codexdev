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

Add a new dependency using:

```bash
poetry add <package_name>
```

## Model setup
Download the model weights by running:

```bash
./model_download.sh
```

This script requires `huggingface-cli` and stores the model in
`models/gemma-3-4b-it`. The assistant expects the weights in this default
directory.


## Adding plugins
Plugins live in the `plugins/` directory. Each plugin subclasses `BaseSkill` and defines a unique `name`. When `PluginManager.discover_plugins()` runs at startup, your skill is loaded automatically.

Example plugin (`plugins/file_finder.py`):

```python
from pathlib import Path
from plugins.base import BaseSkill

class FileFinder(BaseSkill):
    name = "file_finder"

    def execute(self, filename: str) -> str:
        for path in Path.home().rglob(filename):
            return str(path)
        return "not found"
```

Load and execute the skill:

```python
from milo_core.plugin_manager import PluginManager

pm = PluginManager()
pm.discover_plugins()
skill = pm.get_skill_by_name("file_finder")
print(skill.execute("todo.txt"))
```

The repository includes a small `TestSkill` plugin which you can use as a reference when creating new skills.


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
Speech recognition depends on PyAudio, which requires the system
`portaudio` libraries. The Python package is installed automatically
through Poetry or the generated `requirements.txt`, but ensure your
system has the necessary build tools and headers installed. Linux users
must install the development package first, for example:

```bash
sudo apt-get install portaudio19-dev
```

On macOS you can use Homebrew:

```bash
brew install portaudio
```

For text-to-speech via `pyttsx3` you may also need the `espeak` engine on
Linux:

```bash
sudo apt-get install espeak ffmpeg
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
