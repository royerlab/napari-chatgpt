.PHONY: help setup install install-dev test test-cov check format lint build clean publish publish-patch update-readme update-screenshots update-wiki .check-claude

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup        - Install project with all development dependencies"
	@echo "  make install      - Install project with minimal dependencies"
	@echo "  make install-dev  - Install project with dev dependencies only"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make check        - Run all code checks (format check + lint)"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Run flake8 linter"
	@echo "  make build        - Build package"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make publish      - Bump version, commit, tag, and push (triggers PyPI release)"
	@echo "  make publish-patch- Publish patch version (same day increment)"
	@echo ""
	@echo "Documentation:"
	@echo "  make update-readme      - Update README.md using Claude Code CLI"
	@echo "  make update-screenshots - Regenerate widget screenshots for wiki"
	@echo "  make update-wiki        - Update wiki pages using Claude Code CLI"

# =============================================================================
# Setup & Installation
# =============================================================================

setup:
	python -m pip install --upgrade pip
	pip install -e ".[testing]"
	pip install pre-commit
	pre-commit install

install:
	pip install -e .

install-dev:
	pip install -e ".[testing]"

# =============================================================================
# Testing
# =============================================================================

test:
	pytest src/ -v

test-cov:
	@mkdir -p reports
	pytest --cov=napari_chatgpt --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml src/

# =============================================================================
# Code Quality
# =============================================================================

check: format-check lint
	@echo "All checks passed!"

format:
	isort src/
	black src/

format-check:
	@echo "Checking code formatting..."
	black --check src/
	isort --check-only src/

lint:
	@echo "Running flake8..."
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

pre-commit:
	pre-commit run --all-files

# =============================================================================
# Building
# =============================================================================

build: clean
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# =============================================================================
# Publishing
# =============================================================================

# Get current version from __init__.py (first occurrence only)
CURRENT_VERSION := $(shell grep -m1 -o '__version__ = "[^"]*"' src/napari_chatgpt/__init__.py | cut -d'"' -f2)
TODAY := $(shell date +%Y.%-m.%-d)

# Bump version to today's date and publish
publish:
	@echo "Current version: $(CURRENT_VERSION)"
	@if echo "$(CURRENT_VERSION)" | grep -q "^$(TODAY)"; then \
		echo "Error: Version $(CURRENT_VERSION) is already today's date."; \
		echo "Use 'make publish-patch' for same-day releases."; \
		exit 1; \
	fi
	@echo "Updating version to: $(TODAY)"
	@sed -i.bak 's/__version__ = "[^"]*"/__version__ = "$(TODAY)"/' src/napari_chatgpt/__init__.py && rm -f src/napari_chatgpt/__init__.py.bak
	@echo "Committing version bump..."
	git add src/napari_chatgpt/__init__.py
	git commit -m "chore: bump version to $(TODAY)"
	@echo "Creating tag v$(TODAY)..."
	git tag "v$(TODAY)"
	@echo "Pushing to origin..."
	git push origin main --tags
	@echo "Done! GitHub Actions will publish to PyPI."

# Publish patch version (for same-day releases)
publish-patch:
	@echo "Current version: $(CURRENT_VERSION)"
	@if echo "$(CURRENT_VERSION)" | grep -q "^$(TODAY)\."; then \
		PATCH=$$(echo "$(CURRENT_VERSION)" | sed 's/$(TODAY)\.\([0-9]*\)/\1/'); \
		NEW_PATCH=$$((PATCH + 1)); \
		NEW_VERSION="$(TODAY).$$NEW_PATCH"; \
	elif [ "$(CURRENT_VERSION)" = "$(TODAY)" ]; then \
		NEW_VERSION="$(TODAY).1"; \
	else \
		NEW_VERSION="$(TODAY)"; \
	fi; \
	echo "Updating version to: $$NEW_VERSION"; \
	sed -i.bak "s/__version__ = \"[^\"]*\"/__version__ = \"$$NEW_VERSION\"/" src/napari_chatgpt/__init__.py && rm -f src/napari_chatgpt/__init__.py.bak; \
	echo "Committing version bump..."; \
	git add src/napari_chatgpt/__init__.py; \
	git commit -m "chore: bump version to $$NEW_VERSION"; \
	echo "Creating tag v$$NEW_VERSION..."; \
	git tag "v$$NEW_VERSION"; \
	echo "Pushing to origin..."; \
	git push origin main --tags; \
	echo "Done! GitHub Actions will publish to PyPI."

# =============================================================================
# Documentation
# =============================================================================

WIKI_DIR := $(abspath ../napari-chatgpt.wiki)

# Check that Claude Code CLI is installed
.check-claude:
	@command -v claude >/dev/null 2>&1 || { \
		echo "Error: 'claude' CLI not found."; \
		echo "Install Claude Code first:"; \
		echo "  npm install -g @anthropic-ai/claude-code"; \
		echo "See: https://docs.anthropic.com/en/docs/claude-code"; \
		exit 1; \
	}

update-readme: .check-claude
	@echo "Updating README.md with Claude Code..."
	claude -p --permission-mode acceptEdits \
	"Review the README.md and check whether it is up-to-date \
	relative to the current codebase. Look at recent git commits since the \
	last README-related commit, the current tool list, dependencies, \
	installation instructions, and project structure. If anything is outdated \
	or missing, update README.md directly. If everything is already current, \
	say so and make no changes. Do NOT remove existing video links or images. \
	Keep the same overall structure and tone."
	@echo "Done."

update-screenshots:
	@echo "Regenerating screenshots..."
	@if [ ! -d "$(WIKI_DIR)" ]; then \
		echo "Warning: Wiki directory not found at $(WIKI_DIR)"; \
		echo "Screenshots will be saved to ./screenshots/ instead."; \
		mkdir -p screenshots; \
		hatch run docs:screenshots --output-dir screenshots/; \
	else \
		hatch run docs:screenshots --output-dir "$(WIKI_DIR)/images/"; \
	fi
	@echo "Done."

update-wiki: .check-claude
	@echo "Updating wiki pages with Claude Code..."
	@if [ ! -d "$(WIKI_DIR)" ]; then \
		echo "Error: Wiki directory not found at $(WIKI_DIR)"; \
		echo "Clone it first: git clone git@github.com:royerlab/napari-chatgpt.wiki.git ../napari-chatgpt.wiki"; \
		exit 1; \
	fi
	claude -p --add-dir "$(WIKI_DIR)" --permission-mode acceptEdits \
	"Review the wiki pages in $(WIKI_DIR)/ and check whether \
	they are up-to-date relative to the current codebase. Look at the tools, \
	dependencies, installation instructions, API key setup, and UI changes. \
	Update any wiki .md files that are outdated. Do NOT remove existing content \
	that is still valid. Keep the same overall structure and tone."
	@echo "Done."
