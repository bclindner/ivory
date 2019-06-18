import re
import requests
from core import Rule, Report

class LinkResolverRule(Rule):
    """
    A rule which checks for banned links, resolving links to prevent shorturl
    mitigation.
    """
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        for link in report.links:
            response = requests.head(link, allow_redirects=True)
            resolved_url = response.url
            for regex in self.blocked:
                if re.search(regex, resolved_url):
                    return True
        return False

rule = LinkResolverRule
