from napari_chatgpt.utils.llm.summarizer import summarize
from napari_chatgpt.utils.web.duckduckgo import summary_ddg
from napari_chatgpt.utils.web.google import search_overview


def metasearch(query: str,
               num_results: int = 3,
               lang: str = "en",
               do_summarize: bool = True):
    google_overview = search_overview(query=query,
                                      num_results=num_results,
                                      lang=lang)

    ddg_results = summary_ddg(query=query,
                              num_results=num_results,
                              lang=lang,
                              do_summarize=False)

    result = f'Overview:\n{google_overview}\nResults:{ddg_results}\n'

    if do_summarize:
        # summary prompt:
        text = f"The following overview and results were found for the web search query: '{query}'\n\n"

        text += result + '\n\n'
        text += "INSTRUCTIONS: Please summarise these results by listing relevant information that help answer the query:"
        result = summarize(text)

    return result
