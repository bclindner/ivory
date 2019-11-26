import re

from judge import Rule

from schemas import RegexBlockingRule

class BioContentRule(Rule):
    def __init__(self, raw_config):
        config = RegexBlockingRule(raw_config)
        Rule.__init__(self, **config)
        self.blocked = config['blocked']
    def test_report(self, report: dict):
        """
        Test if the target account's bio text or fields matches any of the given blocked regexes.
        """
        acct = report['target_account']['account']
        for regex in self.blocked:
            if re.search(regex, acct.get('note')):
                return True
            for field in acct.get('fields'):
                if re.search(regex, field.get('value')):
                    return True

        return False

rule = BioContentRule
