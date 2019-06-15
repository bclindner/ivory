class Judge:
    rules = []
    def add_rule(self, rule):
        self.rules.append(rule)
    def clear_rules(self, rule):
        self.rules = []
    def make_judgement(self, report):
        most_severe_rule = None
        rules_broken = set()
        for rule in self.rules:
            if rule.test(report):
                rules_broken.add(rule)
                if most_severe_rule is None or most_severe_rule['severity'] < rule['severity']:
                    most_severe_rule = rule
        return (most_severe_rule, rules_broken)
