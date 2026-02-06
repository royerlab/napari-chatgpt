import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.openai.default_model import get_default_openai_model_name
from napari_chatgpt.utils.openai.model_list import postprocess_openai_model_list


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_default_model():
    model_name = get_default_openai_model_name()
    # Check that the model name is a valid GPT model (gpt-3, gpt-4, gpt-5, etc.)
    assert model_name is not None
    assert model_name.startswith("gpt-")


def test_postprocess_empty_list():
    assert postprocess_openai_model_list([]) == []


def test_postprocess_removes_bad_models():
    models = ["gpt-4o", "gpt-3.5-turbo", "gpt-4o-mini", "chatgpt-4o-latest"]
    result = postprocess_openai_model_list(models)
    assert "gpt-3.5-turbo" not in result
    assert "chatgpt-4o-latest" not in result


def test_postprocess_sorts_best_to_top():
    models = ["gpt-4o-mini", "gpt-4o", "gpt-4-0314"]
    result = postprocess_openai_model_list(models)
    # gpt-4o (non-mini) should be at the very top
    assert result[0] == "gpt-4o"


def test_postprocess_no_matches_unchanged():
    models = ["custom-model-1", "custom-model-2"]
    result = postprocess_openai_model_list(models)
    assert set(result) == set(models)
