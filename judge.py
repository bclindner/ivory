"""
Base classes used by the Ivory main class.
"""
import logging # for logging in Judge
from typing import List # type hinting for List
from importlib import import_module # for dynamic rule imports

class Punishment:
    """
    A Punishment is Ivory's representation of a moderation action.

    Currently this is a simple proxy to the Mastodon.admin_account_moderate()
    function's kwargs, with an extra field for the punishment's severity.
    """

    def __init__(self, severity: int, **config):
        self.type = config['type']
        self.severity = severity
        self.config = config

    def __str__(self):
        return "Punishment (%s)" % self.type

    def __repr__(self):
        return "Punishment (%s, severity %s)" % (self.type, self.severity)


class Rule:
    """
    Rules in Ivory are kind of like unit tests for reports.
    Each one can be run against a report to determine if it passes or fails.
    In this case, it differs in that a Rule comes with a Punishment.
    """

    def __init__(self, **config):
        self.name = config['name']
        self.punishment = Punishment(config['severity'], **config['punishment'])

    def test(self, report: dict):
        """
        Test the rule against a given report dict.
        """

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Rule '%s' (%s)" % (self.name, type(self).__name__)


class Judge:
    """
    Interface for judging reports based on rules.

    The Judge class is a dead-simple class that holds Rule objects, and allows
    you to test each Rule on a single Report object with the make_judgement
    method.
    """
    rules = []

    def __init__(self, rule_configs: List[dict] = None):
        if rule_configs is not None:
            self.load_rules(rule_configs)

    def load_rules(self, rule_configs: List[dict]):
        """
        Load rules from a list of rule configuration dicts.
        """
        rulecount = 1
        logger = logging.getLogger(__name__)
        for rule_config in rule_configs:
            try:
                # programmatically load rule based on type in config
                rule_type = rule_config['type']
                logger.debug(
                    "loading rule #%d of type %s", rulecount, rule_type)
                Rule = import_module('rules.{}'.format(rule_type)).rule
                new_rule = Rule(rule_config)
                self.add_rule(new_rule)
                rulecount += 1
            except ModuleNotFoundError as err:
                logger.exception("rule #%d not found", rulecount)
                logger.critical("could not parse rules")
                raise err
            except Exception as err:
                logger.exception(
                    "failed to initialize rule #%d", rulecount)
                logger.critical("could not parse rules")
                raise err
            logger.info("loaded %d rules (%d total)", rulecount - 1, len(self.rules))

    def add_rule(self, rule):
        """
        Add a rule to the judge's list.

        Future judgements will use this rule.
        """
        self.rules.append(rule)

    def clear_rules(self):
        """
        Clear this judge's rules list.
        """
        self.rules = []

    def make_judgement(self, report: dict) -> (Punishment, List[Rule]):
        """
        Judge a report.

        Returns:
        final_verdict: Returns the Punishment object that should be used for
        this report, or None if there is none.
        rules_broken: The list of rules the judge determined were broken.
        """
        most_severe_rule = None
        rules_broken = set()
        for rule in self.rules:
            if rule.test(report):
                rules_broken.add(rule)
                if (most_severe_rule is None or
                        most_severe_rule.punishment.severity < rule.punishment.severity):
                    most_severe_rule = rule
        if most_severe_rule is not None:
            final_verdict = most_severe_rule.punishment
        else:
            final_verdict = None
        return (final_verdict, rules_broken)
