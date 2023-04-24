from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.llms import BaseLLM
from langchain.text_splitter import CharacterTextSplitter

from napari_chatgpt.utils.openai_key import set_openai_key


def summarize(text: str, llm: BaseLLM = None):
    # Ensure that OpenAI key is set:
    set_openai_key()

    # Instantiates LLM if needed:
    llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

    # Splits the text:
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(text)

    # Make documents from the text:
    docs = [Document(page_content=t) for t in texts[:3]]

    # Load summariser:
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    # Summarize:
    summary = chain.run(docs)

    return summary
