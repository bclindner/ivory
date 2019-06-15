import re

class MessageContentRule:
    def __init__(self, config):
        self.name = config['name']
        self.punishment = config['punishment']
        self.blocked = config['blocked']
    def test(self, report):
        for post in report['posts']:
            for regex in blocked:
                if re.search(regex, post):
                    return True
        return False

class LinkContentRule:
    def __init__(self, config):
        self.name = config['name']
        self.punishment = config['punishment']
        self.blocked = config['blocked']
    def test(self, report):
        for link in report['links']:
            for regex in self.blocked:
                if re.search(regex, link):
                    return True
        return False
