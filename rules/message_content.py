import re

from core import Rule, Report

class MessageContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        """
        Test if a post matches any of the given blocked regexes.
        """
        for post in report.posts:
            for regex in self.blocked:
                if re.search(regex, post):
                    return True
        return False

rule = MessageContentRule
