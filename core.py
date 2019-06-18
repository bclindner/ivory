"""
Base classes for the Ivory system.
"""
from typing import List


class User:
    """
    A simplified class representation of a Mastodon user.
    """

    def __init__(self, user_id: str, username: str):
        self.id = user_id
        self.username = username

    def __repr__(self):
        return "User %s (@%s)" % (self.id, self.username)

    def __str__(self):
        return self.username


class Report:
    """
    A class representation of a Mastodon report.

    Since reports from other instances won't have accounts attached, drivers
    cannot create reporter users, so they should just set the reporter field to None.
    """

    def __init__(self,
                 report_id: str,
                 status: str,
                 reported: User,
                 reporter: User,
                 report_comment: str,
                 reported_posts: List[str],
                 reported_links: List[str]):
        # ugh
        self.report_id = report_id
        self.status = status
        self.reporter = reporter
        self.reported = reported
        self.comment = report_comment
        self.posts = reported_posts
        self.links = reported_links

    def __str__(self):
        return "Report #%s (%s)" % (self.report_id, self.reported.username)

    def __repr__(self):
        return self.__str__()  # lol


class Punishment:
    """
    A Punishment is Ivory's representation of a moderation action.
    Punishments are of a specific type (usually suspend, silence, or warn), and
    have a given severity.
    Punishments also optionally come with a configuration dict that defines
    extra options.
    NOTE: Should this be a base class where we derive punishments?
    """

    def __init__(self, config):
        self.type = config['type']
        self.severity = config['severity']
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

    def __init__(self, config):
        self.name = config['name']
        self.punishment = Punishment(config['punishment'])

    def test(self, report: Report):
        """
        Test the rule against a given report.
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

    def make_judgement(self, report: Report) -> (Punishment, List[Rule]):
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


class Driver:
    """
    A dummy Ivory driver to derive your own custom drivers from.

    For Ivory to work, all of the below base methods must be defined.
    """

    def __init__(self):
        pass

    def get_unresolved_report_ids(self):
        """
        Get a list of unresolved report IDs.

        Returns:
        list: An array of report ID strings.
        """
        raise NotImplementedError()

    def get_report(self, report_id: str):
        """
        Get a report by ID.

        The report ID is currently a string type as it will almost certainly be
        plugged into a URL or a REST API. This may change in future major versions.
        """
        raise NotImplementedError()

    def punish(self, report: Report, punishment: Punishment):
        """
        Apply a punishment to a report.

        Driver classes should implement Punishments of type "suspend",
        "silence", and "warn", if possible.  If it isn't possible to implement
        them, raise a NotImplementedError. You can define custom punishments,
        but be wary of extending too much.
        """
        raise NotImplementedError()

    def add_note(self, report_id: str, message: str, resolve: bool = False):
        """
        Add a note to a report by its ID.
        """
        raise NotImplementedError()

