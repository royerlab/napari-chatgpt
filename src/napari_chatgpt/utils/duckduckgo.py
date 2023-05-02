import traceback

from duckduckgo_search import ddg, ddg_images

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

        text = f"The following results were found for the web search query: '{query}'"

        for result in results:
            text += f"Title: {result['title']}\n Description: {result['body']}\n URL: {result['href']}\n\n "

        text += "How do the results inform the query ?"

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

    if results:
        results = list(results)
    else:
        results = []

    return results


def search_images_ddg(query: str,
                      num_results: int = 3,
                      lang: str = "us-en",
                      safesearch: str = 'moderate'
                      ) -> str:
    results = ddg_images(query,
                         region=lang,
                         safesearch=safesearch,
                         size=None,
                         color=None,
                         type_image=None,
                         layout=None,
                         license_image=None,
                         max_results=num_results)

    results = list(results)

    return results
