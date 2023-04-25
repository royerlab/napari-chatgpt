import traceback

from duckduckgo_search import ddg

from napari_chatgpt.utils.summarizer import summarize


def summary_ddg(query: str,
                num_results: int = 3,
                lang: str = "us-en",
                do_summarize: bool = True,
                ) -> str:

    try:
        results = search_ddg(query=query,
                             num_results=num_results,
                             lang=lang)

        text = f"Summarise the following results web search query:  '{query}'"

        for result in results:
            text += f"Title: {result['title']}\n Description: {result['body']}\n URL: {result['href']}\n\n "

        if do_summarize:
            text = summarize(text)

        return text

    except Exception as e:
        traceback.format_exc()
        return f"Web search failed for: '{query}'"


def search_ddg(query: str,
               num_results: int = 3,
               lang: str = "us-en",
               safesearch: str = 'moderate'
               ) -> str:

    results = ddg(query,
                  region=lang,
                  time='h_',
                  safesearch=safesearch,
                  max_results=num_results)

    results = list(results)

    return results
