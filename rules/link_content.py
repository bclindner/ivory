import re
from judge import Rule
from util import parse_links_from_statuses

from schemas import RegexBlockingRule

class LinkContentRule(Rule):
    """
    A rule which checks for banned link content.
    """
    def __init__(self, raw_config):
        config = RegexBlockingRule(raw_config)
        Rule.__init__(self, **config)
        self.blocked = {}
        for regex in config['blocked']
            self.blocked.add(re.compile(regex))
    def test_report(self, report: dict):
        """
        Test if a post's links matches any of the given blocked regexes.
        """
        for link in parse_links_from_statuses(report['statuses']):
            for regex in self.blocked:
                if regex.search(regex, link):
                    return True
        return False

rule = LinkContentRule
