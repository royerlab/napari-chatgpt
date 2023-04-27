from duckduckgo_search import ddg

keywords = 'Albert Einstein'
results = ddg(keywords, region='us-en', safesearch='Off', time='y',
              max_results=10)

for result in results:
    print(result)
