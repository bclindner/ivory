import traceback
import time
from typing import List

import yaml

from drivers.browser import BrowserDriver as BrowserDriver
import rules
from core import Judge

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
                config = yaml.load(config_file, Loader=yaml.Loader)
        except OSError:
            print("Failed to open config.yml!")
            exit(1)
        self.debug_mode = config.get('debug_mode', False)
        self.wait_time = config.get('wait_time', 300)
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
                    self.judge.add_rule(rules.MessageContentRule(rule_config))
                elif rule_config['type'] == "link":
                    self.judge.add_rule(rules.LinkContentRule(rule_config))
                elif rule_config['type'] == "link_redir":
                    self.judge.add_rule(rules.LinkResolverRule(rule_config))
                elif rule_config['type'] == "username":
                    self.judge.add_rule(rules.UsernameContentRule(rule_config))
                else:
                    raise NotImplementedError()
                rulecount += 1
            except Exception as err:
                print("Failed to initialize rule #%d!" % rulecount)
                raise err
        try:
            driver_config = config['driver']
            if driver_config['type'] == "browser":
                self.driver = BrowserDriver(driver_config)
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
            self.handled_reports.append(report_id)

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
                if self.debug_mode:
                    raise err
            print('Report pass complete.')
            time.sleep(self.wait_time)

if __name__ == '__main__':
    Ivory().run()
