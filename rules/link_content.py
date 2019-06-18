import re
from core import Rule, Report

class LinkContentRule(Rule):
    """
    A rule which checks for banned link content.
    """
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        """
        Test if a post's links matches any of the given blocked regexes.
        """
        for link in report.links:
            for regex in self.blocked:
                if re.search(regex, link):
                    return True
        return False

rule = LinkContentRule
