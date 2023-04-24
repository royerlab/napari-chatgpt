from arbol import aprint

from src.napari_chatgpt.utils.missing_imports import get_missing_imports

_code_snippet = """
import numpy as np

data = pd.read_csv("data.csv")
result = np.mean(data["value"])
"""


def test_missing_imports():
    missing_imports = get_missing_imports(_code_snippet)
    aprint(missing_imports)
