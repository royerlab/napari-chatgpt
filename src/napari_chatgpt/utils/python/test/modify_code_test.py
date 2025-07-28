import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.python.modify_code import modify_code

___generated_python_code = """

@magicgui(call_button='Run')
def denoise_bilateral(image: ImageData, d: int = 15, sigmaColor: float = 75, sigmaSpace: float = 75) -> ImageData:
    img = image.astype(np.float32)
    img = cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)
    return img

"""


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_modify_code():
    # Add comments to the code:
    modified_code = modify_code(
        code=___generated_python_code,
        request="Make the function work for multichannel images too.",
    )
    print(modified_code)

    assert len(modified_code) >= len(___generated_python_code)

    assert (
        "multichannel" in modified_code
        or "multi-channel" in modified_code
        or "channel" in modified_code
    )
