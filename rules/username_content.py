import re

from judge import Rule

class UsernameContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, **config)
        self.blocked = config['blocked']
    def test(self, report: dict):
        """
        Test if the reported user matches any of the blocked regexes."
        """
        username = report['target_account']['acct']['username']
        for regex in self.blocked:
            if re.search(regex, username):
                return True
        return False

rule = UsernameContentRule
