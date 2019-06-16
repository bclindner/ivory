from .report import Report

class Judge:
    rules = []
    def add_rule(self, rule):
        self.rules.append(rule)
    def clear_rules(self):
        self.rules = []
    def make_judgement(self, report: Report):
        most_severe_rule = None
        rules_broken = set()
        for rule in self.rules:
            if rule.test(report):
                rules_broken.add(rule)
                if most_severe_rule is None or most_severe_rule['severity'] < rule['severity']:
                    most_severe_rule = rule
        if most_severe_rule is not None:
            final_verdict = most_severe_rule.punishment
        else:
            final_verdict = None
        return (final_verdict, rules_broken)
