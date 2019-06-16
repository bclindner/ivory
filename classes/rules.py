import re
import requests
from .rule import Rule
from .report import Report

class MessageContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        for post in report.posts:
            for regex in self.blocked:
                if re.search(regex, post):
                    return True
        return False

class LinkContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        for link in report.links:
            for regex in self.blocked:
                if re.search(regex, link):
                    return True
        return False

class LinkResolverRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        for link in report.links:
            r = requests.head(link, allow_redirects=True)
            resolved_url = r.url
            for regex in self.blocked:
                if re.search(regex, resolved_url):
                    return True
        return False
