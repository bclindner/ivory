import re
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
