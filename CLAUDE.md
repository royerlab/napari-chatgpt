# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

napari-chatgpt is a napari plugin providing **Omega**, an LLM-powered autonomous agent for interactive image processing and analysis. It uses the LiteMind library to support multiple LLM providers (OpenAI, Anthropic, Gemini) and enables conversational image analysis within the napari viewer.

Publication: https://doi.org/10.1038/s41592-024-02310-w

## Build & Development Commands

The project uses a Makefile for common development tasks:

```bash
make help          # Show all available commands
make setup         # Install with all dev dependencies + pre-commit hooks
make install       # Install with minimal dependencies
make install-dev   # Install with test dependencies only
make test          # Run all tests
make test-cov      # Run tests with coverage report
make check         # Run all code checks (format + lint)
make format        # Format code with black and isort
make lint          # Run flake8 linter
make pre-commit    # Run all pre-commit hooks
make build         # Build package
make clean         # Clean build artifacts
make publish       # Bump version to today's date, tag, and push (triggers PyPI)
make publish-patch # Same-day patch release (e.g., 2025.2.1 -> 2025.2.1.1)

# Documentation (requires Claude Code CLI for readme/wiki updates)
make update-readme      # Review & update README.md relative to codebase
make update-screenshots # Regenerate widget screenshots for wiki (uses hatch docs env)
make update-wiki        # Review & update wiki pages relative to codebase
```

### Hatch Environments

- **default**: Main development environment with all project dependencies
- **hatch-test**: Testing environment with pytest, cellpose, stardist, tensorflow
- **docs**: Documentation environment for screenshot generation (`hatch run docs:screenshots`)

### Manual Commands

```bash
# Run a single test file
pytest src/napari_chatgpt/llm/api_keys/test/api_key_vault_test.py -v

# Run tests via tox (multi-environment)
tox
tox -e py311-linux  # specific environment
```

## Architecture

### Core Components

- **`_widget.py`**: Main `OmegaQWidget` - napari plugin entry point, UI for model selection, temperature control, agent settings
- **`chat_server/chat_server.py`**: `NapariChatServer` - FastAPI WebSocket server managing conversations and tool execution
- **`omega_agent/omega_agent.py`**: `OmegaAgent` - extends `litemind.agent.Agent`, orchestrates LLM interactions with tools
- **`omega_agent/napari_bridge.py`**: `NapariBridge` - queue-based thread-safe communication between LLM and napari's Qt thread
- **`llm/litemind_api.py`**: LLM abstraction factory functions (`get_litemind_api()`, `get_llm()`, `get_model_list()`)

### Tool System

Tools in `omega_agent/tools/`:
- `base_omega_tool.py`: Abstract base for all tools
- `base_napari_tool.py`: Base for napari-aware code generation/execution tools
- `napari/`: Viewer manipulation, widget creation, file operations, segmentation, plugin discovery (`napari_plugin_tool.py`)
- `search/`: Web search, Wikipedia search, image search
- `special/`: Python REPL execution, pip install (with user permission), exception handling, file download, function/package info

### Key Pattern: Thread-Safe napari Integration

The `NapariBridge` uses queues and napari's `@thread_worker` decorator to safely execute LLM-generated code on the Qt event loop:
1. LLM generates code via tool
2. Code sent to napari queue
3. Worker executes on Qt thread
4. Result/exception returned through response queue

### Supporting Modules

- **`llm/api_keys/`**: Encrypted API key storage using Fernet (`~/.omega_api_keys/`)
- **`microplugin/`**: AI-augmented code editor with syntax highlighting, Jedi completion, network code sharing
- **`utils/python/`**: Code manipulation - import fixing, error repair, package detection, AST utilities

## Code Style

Pre-commit enforces: black (formatting), isort (imports), flake8 (style), pyupgrade (py310+), autoflake (unused imports), napari-plugin-checks

## Tech Stack

- **LiteMind**: LLM abstraction (OpenAI, Anthropic, Gemini)
- **FastAPI/Uvicorn**: WebSocket chat server
- **QtPy/PyQt5**: UI framework
- **scikit-image**: Image processing
- **beautifulsoup4**: Web scraping
- **requests**: HTTP downloads
- **Python 3.10+** supported