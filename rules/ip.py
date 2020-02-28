from judge import Rule
from schemas import RegexBlockingRule

class IPRule(Rule):
    """
    A rule that blocks specific IPs on pending accounts.
    """
    def __init__(self, raw_config):
        config = RegexBlockingRule(raw_config)
        Rule.__init__(self, **config)
        self.blocked = []
        for ip in config['blocked']:
            self.blocked.append(ip)
    def test_pending_account(self, account: dict):
        """
        Test if the user's IP address matches any of the supplied ones.
        """
        # IP should always be present so we don't check
        for ip in self.blocked:
            if account['ip'] == ip:
                return True
        return False


rule = IPRule
