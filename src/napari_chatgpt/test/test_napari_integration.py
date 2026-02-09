"""Integration tests for napari-chatgpt plugin registration."""

import numpy as np
import pytest


def test_napari_manifest():
    """Verify the npe2 manifest loads and declares expected contributions."""
    from npe2 import PluginManifest

    manifest = PluginManifest.from_distribution("napari-chatgpt")

    assert manifest.name == "napari-chatgpt"
    assert manifest.display_name == "napari-chatgpt | Omega"

    command_ids = [c.id for c in manifest.contributions.commands]
    assert "napari-chatgpt.start_omega" in command_ids
    assert "napari-chatgpt.sample_data" in command_ids

    assert len(manifest.contributions.widgets) >= 1
    assert len(manifest.contributions.sample_data) >= 1


def test_sample_data_returns_layer_tuple():
    """Verify make_sample_data() returns a valid LayerDataTuple list."""
    from napari_chatgpt._sample_data import make_sample_data

    result = make_sample_data()

    assert isinstance(result, list)
    assert len(result) == 1

    data, meta, layer_type = result[0]
    assert isinstance(data, np.ndarray)
    assert data.ndim >= 2
    assert isinstance(meta, dict)
    assert "name" in meta
    assert layer_type == "image"


@pytest.mark.slow
def test_omega_widget_creation(make_napari_viewer):
    """Verify OmegaQWidget can be instantiated inside a napari viewer."""
    viewer = make_napari_viewer()

    from napari_chatgpt._widget import OmegaQWidget

    widget = OmegaQWidget(viewer, add_code_editor=False)

    assert widget.viewer is viewer
    assert widget.main_layout is not None
    assert widget.main_model_combo_box.count() > 0

    widget.close()
