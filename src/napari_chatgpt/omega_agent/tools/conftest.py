"""Tool-specific test fixtures for omega_agent/tools/ tests."""

from queue import Queue

import pytest


@pytest.fixture
def mock_napari_queues():
    """Returns (to_napari_queue, from_napari_queue) for BaseNapariTool tests."""
    return Queue(), Queue()
