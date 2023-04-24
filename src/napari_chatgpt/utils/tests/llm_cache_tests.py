import time

from arbol import aprint
from langchain.chat_models import ChatOpenAI

from src.napari_chatgpt.utils.llm_cache import wrap_llm


def test_llm_cache():
    # TODO: not functional!

    llm = ChatOpenAI(temperature=0)

    cached_llm = wrap_llm(llm)

    question = 'Who is Albert Einstein?'

    before = time.time()
    answer = cached_llm(question)
    aprint(answer)
    aprint("Cache Hit Time Spent =", time.time() - before)

    before = time.time()
    answer = cached_llm("What is your hobby")
    aprint(answer)
    aprint("Read through Time Spent =", time.time() - before)

    before = time.time()
    question = "What is the winner Super Bowl in the year Justin Bieber was born?"
    answer = cached_llm(question)
    aprint(answer)
    aprint("Cache Hit Time Spent =", time.time() - before)
