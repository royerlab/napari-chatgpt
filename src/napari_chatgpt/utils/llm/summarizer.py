from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM


def summarize(text: str, llm: LLM = None):
    # Clean up text:
    text = text.strip()

    # Is there anything to summarise?
    if len(text) == 0:
        return text

    # Instantiates LLM if needed:
    llm = llm or get_llm()

    # Prepare the prompt for summarization:
    prompt = (
        "Summarize the following text, retaining all key ideas and information.\n"
        "Keep the summary concise (no more than 3 paragraphs). Use plain text.\n"
        "Return only the summary with no prefix, postfix, or additional explanations.\n\n"
        f"```text\n{text}\n```\n\n"
        "Summary:"
    )

    # Call the LLM to get the summary:
    summary = llm.generate(prompt)

    # get the last message and extract plain text:
    summary_text = summary[-1].to_plain_text()

    return summary_text
