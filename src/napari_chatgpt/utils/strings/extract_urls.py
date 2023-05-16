import re
from typing import List


def extract_urls(text: str) -> List[str]:
    # URL regex:
    # url_pattern_str = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    url_pattern_str = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    # Define the regular expression pattern for URLs
    url_pattern = re.compile(url_pattern_str)

    # Use findall() function to extract all URLs from the text
    urls = re.findall(url_pattern, text)

    # get the URL part:
    urls = [u[0] for u in urls]

    return urls
