import re
from judge import Rule

from schemas import RegexBlockingRule

class UsernameContentRule(Rule):
    def __init__(self, raw_config):
        config = RegexBlockingRule(raw_config)
        Rule.__init__(self, **config)
        self.blocked = config['blocked']
    def test_report(self, report: dict):
        """
        Test if the reported user matches any of the blocked regexes.
        """
        username = report['target_account']['account']['username']
        for regex in self.blocked:
            if re.search(regex, username):
                return True
        return False
    def test_pending_account(self, account: dict):
        """
        Test if the pending user's username matches any of the blocked regexes.
        """
        username = account['username']
        for regex in self.blocked:
            if re.search(regex, username):
                return True
        return False

rule = UsernameContentRule
