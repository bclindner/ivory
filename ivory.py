from importlib import import_module
import traceback
import time
from typing import List

import yaml

from core import Judge
from exceptions import DriverError, DriverAuthorizationError, DriverNetworkError

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
            exit(1)
        rulecount = 1
        for rule_config in rules_config:
            try:
                # programmatically load rule based on type in config
                rule_type = rule_config['type']
                Rule = import_module('rules.' + rule_type).rule
                self.judge.add_rule(Rule(rule_config))
                rulecount += 1
            except ModuleNotFoundError:
                print("ERROR: Rule #%d not found!" % rulecount)
                exit(1)
            except Exception as err:
                print("Failed to initialize rule #%d!" % rulecount)
                raise err
        try:
            driver_config = config['driver']
            # programmatically load driver based on type in config
            module_name = 'drivers.' + driver_config['type']
            Driver = import_module(module_name).driver
            self.driver = Driver(driver_config)
        except KeyError:
            print("ERROR: Driver configuration not found in config.yml!")
            exit(1)
        except ModuleNotFoundError as err:
            if err.name == module_name:
                print("ERROR: Driver not found!")
                exit(1)
            else:
                raise err
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
            retries = 0
            while True:
                try:
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
                # network error handling
                except DriverNetworkError as err:
                    retries += 1
                    print("Encountered network error:", err)
                    if retries < MAX_RETRIES:
                        print("Retrying (attempt %d)..." % retries)
                        continue
                    else:
                        print("Max retries hit; skipping...")
                # driver error handling
                except DriverAuthorizationError as err:
                    print("Fatal authorization error:",err)
                    print("Exiting...")
                    exit(1)
                except DriverError as err:
                    print("Driver error handling report #"+report_id+":",err)
                    print("Skipping...")
                    break
                # general exception catch
                except Exception as err:
                    print("Error handling report #"+report_id+":",err)
                    print("Skipping...")
                    break
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
