import re
import requests
from core import Rule, Report
from constants import VERSION

# HTTP headers for the LinkResolverRule.
# Certain URL shorteners require us to set a valid non-generic user agent.
HEADERS = {
    "User-Agent": "Mozilla/5.0 IvoryAutomod/" + VERSION
}

class LinkResolverRule(Rule):
    """
    A rule which checks for banned links, resolving links to prevent shorturl
    mitigation.
    """
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        for post in report.posts:
            for link in post.links:
                response = requests.head(link, allow_redirects=True, headers=HEADERS)
                resolved_url = response.url
                for regex in self.blocked:
                    if re.search(regex, resolved_url):
                        return True
        return False

rule = LinkResolverRule