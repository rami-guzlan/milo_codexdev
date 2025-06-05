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
Create a new file under `plugins/` with a class that subclasses `BaseSkill` and implements `execute`. When `PluginManager.discover_plugins()` runs, your skill will be loaded automatically. Files named `test_*.py` are skipped by default; set the `MILO_INCLUDE_TEST_PLUGINS=1` environment variable or pass `include_tests=True` to `discover_plugins()` to load them.

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
Speech recognition depends on PyAudio, which requires OS-level
`portaudio` libraries. The Python package is installed automatically
through Poetry or the generated `requirements.txt`, but ensure your
system has the necessary build tools and `portaudio` headers. Linux
users must install the development headers first, for example:

```bash
sudo apt-get install portaudio19-dev
```

On macOS you can use Homebrew:

```bash
brew install portaudio
```

## Running MILO
Start the assistant with:

```bash
poetry run milo-core
```

Stop it at any time with `Ctrl+C`. New plugins added to the `plugins/`
directory are discovered automatically when MILO starts.
