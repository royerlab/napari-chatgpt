from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.llms import BaseLLM
from langchain.text_splitter import CharacterTextSplitter

from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name


def summarize(text: str, llm: BaseLLM = None):
    # Clean up text:
    text = text.strip()

    # Is there anything to summarise?
    if len(text) == 0:
        return text

    # Instantiates LLM if needed:
    from langchain.chat_models import ChatOpenAI
    llm = llm or ChatOpenAI(model_name=get_default_openai_model_name(), temperature=0)

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
