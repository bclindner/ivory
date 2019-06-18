import re

from core import Rule, Report

class UsernameContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        """
        Test if the reported user matches any of the blocked regexes."
        """
        username = report.reported.username
        for regex in self.blocked:
            if re.search(regex, username):
                return True
        return False

rule = UsernameContentRule
