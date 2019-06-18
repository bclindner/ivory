"""
Some rules for Ivory.
These serve as good examples if you're looking to write your own.
"""
import re

import requests

from core import Rule, Report

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

class UsernameContentRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
        self.blocked = config['blocked']
    def test(self, report: Report):
        """
        Test if the reported user matches any of the blocked regexes."
        """
        username = report.reported.username
        for regex in self.blocked:
            if re.search(regex, username):
                return True
        return False
