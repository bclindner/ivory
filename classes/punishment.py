class Punishment:
    def __init__(self, config):
        self.type = config['type']
        self.severity = config['severity']
        self.config = config

    def __str__(self):
        return "Punishment (%s)" % self.type
    def __repr__(self):
        return "Punishment (%s, severity %s)" % (self.type, self.severity)
