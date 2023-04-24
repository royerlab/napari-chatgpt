import traceback

from duckduckgo_search import ddg

from napari_chatgpt.utils.summarizer import summarize


def search_overview(query: str,
                    num_results: int = 3,
                    lang: str = "us-en",
                    do_summarize: bool = True,
                    ) -> str:

    try:
        results = ddg(query,
                      region=lang,
                      time='y',
                      max_results=num_results)

        results = list(results)

        text = ''

        for result in results:
            text += f"Title: {result['title']}\n Description: {result['body']}\n URL: {result['href']}\n\n "

        if do_summarize:
            text = summarize(text)

        return text

    except Exception as e:
        traceback.format_exc()
        return f"Web search failed for: '{query}'"
