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
        "Please summarize the following text retaining all the key ideas and information:\n\n"
        f"```text\n{text}\n```\n\n"
        "**Important** Please do not include any prefix, postfix, additional information or explanations, *just* the summary.**\n\n"
        "Summary:"
    )

    # Call the LLM to get the summary:
    summary = llm.generate(prompt)

    # get the last message and extract plain text:
    summary_text = summary[-1].to_plain_text()

    return summary_text
