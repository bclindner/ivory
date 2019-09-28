import re
from judge import Rule
from util import parse_links_from_statuses

class LinkContentRule(Rule):
    """
    A rule which checks for banned link content.
    """
    def __init__(self, config):
        Rule.__init__(self, **config)
        self.blocked = config['blocked']
    def test(self, report: dict):
        """
        Test if a post's links matches any of the given blocked regexes.
        """
        for link in parse_links_from_statuses(report['statuses']):
            for regex in self.blocked:
                if re.search(regex, link):
                    return True
        return False

rule = LinkContentRule
