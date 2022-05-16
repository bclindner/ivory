"""
Ivory core class file.
Contains everything you need to run Ivory programmatically.
"""
import logging
import time # for Ivory.watch()

from mastodon import Mastodon, MastodonError, MastodonGatewayTimeoutError # API wrapper lib

import constants  # Ivory constants
from judge import ReportJudge, PendingAccountJudge, Punishment  # Judge to integrate into Ivory
from schemas import IvoryConfig


class Ivory():
    """
    The main Ivory class, which programmatically handles reports pulled from
    the Mastodon API.
    """

    def __init__(self, raw_config):
        """
        Runs Ivory.
        """
        # **Validate the configuration**
        config = IvoryConfig(raw_config)

        # **Set up logger**
        self._logger = logging.getLogger(__name__)

        self._logger.info("Ivory version %s starting", constants.VERSION)

        # **Load Judge and Rules**
        self._logger.info("parsing rules")
        if 'reports' in config:
            self.report_judge = ReportJudge(config['reports'].get("rules"))
        else:
            self._logger.debug("no report rules detected")
            self.report_judge = None
        if 'pendingAccounts' in config:
            self.pending_account_judge = PendingAccountJudge(config['pendingAccounts'].get("rules"))
        else:
            self._logger.debug("no pending account rules detected")
            self.pending_account_judge = None


        # **Initialize and verify API connectivity**
        self._api = Mastodon(
            access_token=config['token'],
            api_base_url=config['instanceURL']
        )
        self._logger.debug("mastodon API wrapper initialized")
        # 2.9.1 required for moderation API
        if not self._api.verify_minimum_version("2.9.1"):
            self._logger.error("This instance is not updated to 2.9.1 - this version is required for the Moderation API %s", self._api.users_moderated)
            exit(1)
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
        if 'waitTime' not in config:
            self._logger.info(
                "no waittime specified, defaulting to %d seconds", constants.DEFAULT_WAIT_TIME)
        self.wait_time = config.get("waitTime", constants.DEFAULT_WAIT_TIME)
        self.dry_run = config.get('dryRun', False)


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
        (punishment, rules_broken) = self.report_judge.make_judgement(report)
        if rules_broken:
            self._logger.info("report breaks these rules: %s", rules_broken)
        if punishment is not None:
            self._logger.info("handling report with punishment %s", punishment)
            self.punish(report['target_account']['id'], punishment, report['id'])

    def handle_pending_accounts(self):
        """
        Handle all accounts in the pending account queue.
        """
        accounts = self._api.admin_accounts(status="pending")
        for account in accounts:
            self.handle_pending_account(account)

    def handle_pending_account(self, account: dict):
        """
        Handle a single pending account.
        """
        self._logger.info("handling pending user %s", account['username'])

        # The Mastodon API changed the return value for IP addresses from
        # a string to a dict in 3.5
        # if self._api.verify_minimum_version("3.5.0"):
        if not isinstance(account['ip'], str):
            new_ip = account['ip']['ip']
            del account['ip']
            account['ip'] = new_ip

        (punishment, rules_broken) = self.pending_account_judge.make_judgement(account)
        if rules_broken:
            self._logger.info("pending account breaks these rules: %s", rules_broken)
        if punishment is not None:
            self._logger.info("handling report with punishment %s", punishment)
            self._logger.debug("punishment cfg: %s", punishment.config)
            self.punish(account['id'], punishment)

    def punish(self, account_id, punishment: Punishment, report_id=None):
        if self.dry_run:
            self._logger.info("ignoring punishment; in dry mode")
            return
        maxtries = 3
        tries = 0
        while True:
            try:
                if punishment.type == constants.PUNISH_REJECT:
                    self._api.admin_account_reject(account_id)
                elif punishment.type == constants.PUNISH_WARN:
                    self._api.admin_account_moderate(
                        account_id,
                        None,
                        report_id,
                        text=punishment.config.get('message')
                    )
                elif punishment.type == constants.PUNISH_DISABLE:
                    self._api.admin_account_moderate(
                        account_id,
                        "disable",
                        report_id,
                        text=punishment.config.get('message')
                    )
                elif punishment.type == constants.PUNISH_SILENCE:
                    self._api.admin_account_moderate(
                        account_id,
                        "silence",
                        report_id,
                        text=punishment.config.get('message')
                    )
                elif punishment.type == constants.PUNISH_SUSPEND:
                    self._api.admin_account_moderate(
                        account_id,
                        "suspend",
                        report_id,
                        text=punishment.config.get('message')
                    )
                else:
                    # whoops
                    raise NotImplementedError()
                break
            except MastodonGatewayTimeoutError as err:
                self._logger.warn("gateway timed out. ignoring for now, if that didn't do it we'll get it next pass...")
                break
    def run(self):
        self._logger.info("starting moderation pass")
        try:
            if self.report_judge:
                self.handle_unresolved_reports()
            if self.pending_account_judge:
                self.handle_pending_accounts()
            self._logger.info("moderation pass complete")
        except MastodonError:
            self._logger.exception(
                "enountered an API error. waiting %d seconds to try again", self.wait_time)

    def watch(self):
        """
        Runs handle_unresolved_reports() on a loop, with a delay specified in
        the "waittime" field of the config.
        """
        while True:
            starttime = time.time()
            self.run()
            time_to_wait = self.wait_time - (time.time() - starttime)
            if time_to_wait > 0:
                self._logger.debug("waiting for %.4f seconds", time_to_wait)
                time.sleep(time_to_wait)
            else:
                self._logger.warn("moderation pass took longer than waitTime - this will cause significant drift. you may want to increase waitTime")
