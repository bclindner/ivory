"""
Ivory core class file.
Contains everything you need to run Ivory programmatically.
"""
import logging
from time import sleep  # for Ivory.watch()

from mastodon import Mastodon, MastodonError  # API wrapper lib

import constants  # Ivory constants
from judge import Judge  # Judge to integrate into Ivory


class Ivory():
    """
    The main Ivory class, which programmatically handles reports pulled from
    the Mastodon API.
    """

    def __init__(self, **kwargs):
        """
        Runs Ivory.
        """
        # **Set up logger**
        self._logger = logging.getLogger(__name__)

        self._logger.info("Ivory version %s starting", constants.VERSION)

        # **Load Judge and Rules**
        self._logger.info("parsing rules")
        self.judge = Judge(kwargs['rules'])

        # **Initialize and verify API connectivity**
        self._api = Mastodon(
            access_token=kwargs['token'],
            api_base_url=kwargs['instanceURL']
        )
        self._logger.debug("mastodon API wrapper initialized")
        # 2.9.1 required for moderation API
        self._api.verify_minimum_version("2.9.1")
        self._logger.debug("minimum version verified; should be ok")
        # grab some info which could be helpful here
        self.instance = self._api.instance()
        self.user = self._api.account_verify_credentials()
        # log a bunch of shit
        self._logger.info("logged into %s as %s",
                          self.instance['uri'], self.user['username'])
        self._logger.debug("instance info: %s", self.instance)
        self._logger.debug("user info: %s", self.user)

        # **Set some variables from config**
        if 'waittime' not in kwargs:
            self._logger.info(
                "no waittime specified, defaulting to %d seconds", constants.DEFAULT_WAIT_TIME)
        self.wait_time = kwargs.get("waitTime", constants.DEFAULT_WAIT_TIME)

    def handle_unresolved_reports(self):
        """
        Handles all unresolved reports.
        """
        reports = self._api.admin_reports()
        for report in reports:
            self.handle_report(report)

    def handle_report(self, report: dict):
        """
        Handles a single report.
        """
        self._logger.info("handling report #%d", report['id'])
        (punishment, rules_broken) = self.judge.make_judgement(report)
        if not rules_broken:
            self._logger.info("report breaks these rules: %s",
                              " ".join(rules_broken))
        if punishment is not None:
            self._logger.info("handling report with punishment %s", punishment)
            self._logger.debug("punishment cfg: %s", punishment.config)

    def watch(self):
        """
        Runs handle_unresolved_reports() on a loop, with a delay specified in
        the "waittime" field of the config.
        """
        while True:
            self._logger.debug("running report pass")
            try:
                self.handle_unresolved_reports()
                self._logger.debug(
                    "report pass complete, waiting for %d seconds", self.wait_time)
            except MastodonError:
                self._logger.exception(
                    "API error while handling reports. waiting %d seconds to try again", self.wait_time)
            sleep(self.wait_time)
