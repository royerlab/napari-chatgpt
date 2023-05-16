import os

from arbol import aprint

from napari_chatgpt.llm.bard import ChatBard


def test_bard():
    token = 'Wgi6lxj2R-NE9yMgkG3r_sXrsV9-JVO16thWD-2tTGjnAoxCvJxj0vYieQFdBinHGntcQA.'
    os.environ["BARD_KEY"] = token

    chat = ChatBard(bard_token=token)

    result = chat('What is your name?')

    aprint(result)
