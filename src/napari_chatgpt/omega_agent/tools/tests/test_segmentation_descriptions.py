"""Tests for segmentation tool descriptions — verify bias-free language."""

from napari_chatgpt.omega_agent.tools.napari.delegated_code.signatures import (
    cellpose_signature,
    classic_signature,
    stardist_signature,
)


class TestSignaturesNeutral:
    """Verify that signature comments don't contain biased language."""

    def test_cellpose_no_bias(self):
        assert "better" not in cellpose_signature.lower()
        assert "best" not in cellpose_signature.lower()
        assert "superior" not in cellpose_signature.lower()

    def test_stardist_no_bias(self):
        assert "better" not in stardist_signature.lower()
        assert "best" not in stardist_signature.lower()
        assert "superior" not in stardist_signature.lower()

    def test_classic_no_bias(self):
        assert "simple" not in classic_signature.lower()
        assert "baseline" not in classic_signature.lower()
        assert "basic" not in classic_signature.lower()

    def test_classic_mentions_methods(self):
        assert "otsu" in classic_signature.lower()
        assert "li" in classic_signature.lower()
        assert "triangle" in classic_signature.lower()


class TestAlgorithmDescriptions:
    """Verify that algorithm descriptions in utils.py are neutral."""

    def test_classic_description_no_bias(self):
        from napari_chatgpt.omega_agent.tools.napari.delegated_code.utils import (  # noqa: E501
            get_description_of_algorithms,
        )

        desc = get_description_of_algorithms()
        desc_lower = desc.lower()
        assert "simple" not in desc_lower
        assert "baseline" not in desc_lower
        assert "easy" not in desc_lower


class TestSegmentationInstructions:
    """Verify the segmentation tool instructions include method-honoring."""

    def test_method_honoring_instruction(self):
        from napari_chatgpt.omega_agent.tools.napari.cell_nuclei_segmentation_tool import (  # noqa: E501
            _instructions,
        )

        assert "MUST use classic_segmentation()" in _instructions
        assert "Never override" in _instructions
