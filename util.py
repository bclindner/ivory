"""
Utilities for Ivory operations.
"""
from bs4 import BeautifulSoup
from typing import List

def parse_links(text: str):
    """
    Parse all links out of an HTML string.
    Currently using BeautifulSoup for this.

    Used primarily when getting links out of a status or bio.

    TODO: Make parsing read non-<a> links?
    TODO: Exclude mentions? The "mention" class is not a good way to filter that...
    """
    return [a.get('href') for a in BeautifulSoup(text, "html.parser").find_all('a')]

def parse_links_from_statuses(statuses: List[dict]):
    """
    Get a list of all links out of an array of Mastodon statuses.
    """
    links = []
    for status in statuses:
        for text in status['content']:
            for link in parse_links(text): # weee
                links.append(link)
    return links
