from judge import Rule
import requests
import logging

import schemas
from voluptuous import Required, Range

Config = schemas.Rule.extend({
    Required("threshold"): Range(min=0, max=100)
})

class StopForumSpamRule(Rule):
    """
    A rule which pings StopForumSpam's API to see if a user is a reported
    spammer.
    """
    # Setting these as static to cache them among all the StopForumSpam rules
    # hacky i guess but whatever
    email_confidences = {}
    tested_emails = set()
    ip_confidences = {}
    tested_ips = set()
    def __init__(self, raw_config):
        # Validate configuration
        config = Config(raw_config)
        Rule.__init__(self, **config)
        self.threshold = config['threshold']

    def calc_confidence(self, email_confidence, ip_confidence):
        if not email_confidence and not ip_confidence:
            return False
        if email_confidence and not ip_confidence:
            return email_confidence > self.threshold
        if ip_confidence and not email_confidence:
            return ip_confidence > self.threshold
        return max([email_confidence, ip_confidence]) > self.threshold

    def test_pending_account(self, account: dict):
        """
        Test if the reported user's email is listed in StopForumSpam's
        database.

        See https://www.stopforumspam.com/usage for how we're interfacing with
        the API here.
        """
        email = account['email']
        ip = account['ip']
        if email in self.tested_emails and ip in self.tested_ips:
            self._logger.debug("looks like we've already tested for this user and ip; recalculating to be sure")
            judgement = self.calc_confidence(self.email_confidences.get(email), self.ip_confidences.get(ip))
            return judgement

        params = {
            "email": email,
            "ip": ip,
            "json": ''
        }
        resp = requests.get("https://api.stopforumspam.org/api", params=params)
        results = resp.json()

        ip_confidence = results.get('ip').get('confidence')
        email_confidence = results.get('email').get('confidence')
        if ip_confidence:
            self.ip_confidences[ip] = ip_confidence
        if email_confidence:
            self.email_confidences[email] = email_confidence
        self.tested_emails.add(email)
        self.tested_ips.add(ip)

        judgement = self.calc_confidence(ip_confidence, email_confidence)
        self._logger.debug("ip confidence {}".format(ip_confidence))
        self._logger.debug("email confidence {}".format(email_confidence))
        self._logger.debug("judgement: {}".format(judgement))

        return judgement

rule = StopForumSpamRule
