"""
Base classes for the Ivory system.
"""
from typing import List
import re
import time
import traceback
import yaml
import requests

import drivers


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

class LinkContentRule(Rule):
    """
    A rule which checks for banned link content.
    """
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        """
        Test if a post's links matches any of the given blocked regexes.
        """
        for link in report.links:
            for regex in self.blocked:
                if re.search(regex, link):
                    return True
        return False

class LinkResolverRule(Rule):
    """
    A rule which checks for banned links, resolving links to prevent shorturl
    mitigation.
    """
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        for link in report.links:
            response = requests.head(link, allow_redirects=True)
            resolved_url = response.url
            for regex in self.blocked:
                if re.search(regex, resolved_url):
                    return True
        return False

class MessageContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        """
        Test if a post matches any of the given blocked regexes.
        """
        for post in report.posts:
            for regex in self.blocked:
                if re.search(regex, post):
                    return True
        return False

class Ivory:
    """
    The core class for the Ivory automoderation system.
    In practice, you really only need to import this and a driver to get it
    running.
    """
    handled_reports: List[str] = []

    def __init__(self):
        # get config file
        try:
            with open('config.yml') as config_file:
                config = yaml.load(config_file)
        except OSError:
            print("Failed to open config.yml!")
            exit(1)
        try:
            self.wait_time = config['wait_time']
        except KeyError:
            print("No wait time specified, using 5min...")
            self.wait_time = 300
        # parse rules first; fail early and all that
        self.judge = Judge()
        try:
            rules_config = config['rules']
        except KeyError:
            print("ERROR: Couldn't find any rules in config.yml!")
        rulecount = 1
        for rule_config in rules_config:
            try:
                # FIXME this type switch suckssss
                if rule_config['type'] == "content":
                    self.judge.add_rule(MessageContentRule(rule_config))
                elif rule_config['type'] == "link":
                    self.judge.add_rule(LinkContentRule(rule_config))
                elif rule_config['type'] == "link_redir":
                    self.judge.add_rule(LinkResolverRule(rule_config))
                else:
                    raise NotImplementedError()
                rulecount += 1
            except err:
                print("Failed to initialize rule #%d!" % rulecount)
                raise err
        try:
            driver_config = config['driver']
            if driver_config['type'] == "browser":
                self.driver = drivers.browser.BrowserDriver(driver_config)
            else:
                raise NotImplementedError()
        except KeyError:
            print("ERROR: Driver configuration not found in config.yml!")
            exit(1)
        except Exception as err:
            print("ERROR: Failed to initialize driver!")
            raise err

    def handle_reports(self):
        """
        Get reports from the driver, and judge and punish each one accordingly.
        """
        reports_to_check = self.driver.get_unresolved_report_ids()
        for report_id in reports_to_check:
            if report_id in self.handled_reports:
                print("Report #%s skipped" % report_id)
                continue
            print("Handling report #%s..." % report_id)
            report = self.driver.get_report(report_id)
            (final_verdict, rules_broken) = self.judge.make_judgement(report)
            if final_verdict:
                self.driver.punish(report, final_verdict)
                rules_broken_str = ', '.join(
                    [str(rule) for rule in rules_broken])  # lol
                note = "Ivory has suspended this user for breaking rules: "+rules_broken_str
            else:
                note = "Ivory has scanned this report and found no infractions."
            self.driver.add_note(report.report_id, note)

    def run(self):
        """
        Runs the Ivory automoderator main loop.
        """
        while True:
            print('Running report pass...')
            try:
                self.handle_reports()
            except Exception as err:
                print("Unexpected error handling reports!")
                traceback.format_exc()
            print('Report pass complete.')
            time.sleep(self.wait_time)
