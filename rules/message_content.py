import re

from judge import Rule

class MessageContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, **config)
        self.blocked = config['blocked']
    def test(self, report: dict):
        """
        Test if a post matches any of the given blocked regexes.
        """
        for post in report.posts:
            for regex in self.blocked:
                if re.search(regex, post):
                    return True
        return False

rule = MessageContentRule
