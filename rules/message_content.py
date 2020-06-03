import re

from judge import Rule

from schemas import RegexBlockingRule

class MessageContentRule(Rule):
    def __init__(self, raw_config):
        config = RegexBlockingRule(raw_config)
        Rule.__init__(self, **config)
        self.blocked = config['blocked']
    def test_report(self, report: dict):
        """
        Test if a status matches any of the given blocked regexes.
        """
        for status in report.get('statuses', []):
            for regex in self.blocked:
                if re.search(regex, status.get('content', '')):
                    return True
        return False
    def test_pending_account(self, account: dict):
        """
        Test if a pending account's join reason matches any of the blocked
        regexes.
        """
        if 'invite_request' not in account:
            return False # can't violate this rule if you don't have a pending blurb :rollsafe:
        for regex in self.blocked:
            content = account.get("invite_request") or ""
            if re.search(regex, str(content)):
                return True
        return False

rule = MessageContentRule
