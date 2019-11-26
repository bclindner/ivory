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
    def __init__(self, raw_config):
        # Validate configuration
        config = Config(raw_config)
        Rule.__init__(self, **config)
        # Caching for known emails/IPs
        self.email_confidences = {}
        self.tested_emails = set()
        self.ip_confidences = {}
        self.tested_ips = set()
        self.threshold = config['threshold']

    def calc_confidence(self, ip_confidence, email_confidence):
        if not email_confidence and not ip_confidence:
            return False
        elif email_confidence and not ip_confidence:
            return email_confidence >= self.threshold
        elif ip_confidence and not email_confidence:
            return ip_confidence >= self.threshold
        else:
            return max([email_confidence, ip_confidence]) >= self.threshold

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
            judgement = self.calc_confidence(self.ip_confidences.get(ip), self.email_confidences.get(email))
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
