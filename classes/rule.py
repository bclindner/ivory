from .punishment import Punishment

class Rule:
    def __init__(self, config):
        self.name = config['name']
        self.punishment = Punishment(config['punishment'])
    def test(self, report):
        # This is an empty rule, so it should always pass
        return False
    def __str__(self):
        return self.name
    def __repr__(self):
        return "Rule '%s' (%s)" % (self.name, type(self).__name__)
