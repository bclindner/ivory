import re

from judge import Rule
from schemas import PendingAcctRule

class BlankSignupRule(Rule):
    def __init__(self, raw_config):
        config = PendingAcctRule(raw_config)
        Rule.__init__(self, **config)
    def test_pending_account(self, account: dict):
        """
        Test if a pending account's join reason is blank.
        """
        if not account.get('invite_request') or str(account.get('invite_request')) == "":
            return True
        return False

rule = BlankSignupRule
