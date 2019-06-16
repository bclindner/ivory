from classes.browser import IvoryBrowser
from classes.judge import Judge
import classes.rules as rules

from getpass import getpass
import time
import yaml
import pickle


try:
    with open('config.yml') as config_yml:
        config = yaml.load(config_yml, Loader=yaml.Loader)
except:
    print("Failed to open config file!")
    print("Exiting.")
    exit(1)

judge = Judge()
for rule_config in config['rules']:
    rule_type = rule_config['type']
    if rule_type == 'content':
        judge.add_rule(rules.MessageContentRule(rule_config))
    elif rule_type == 'link':
        judge.add_rule(rules.LinkContentRule(rule_config))
    else:
        print("Invalid config! Couldn't find a rule with type:", rule_type)
        print("Exiting.")
        exit(1)

# get cookies if we can
cookies = []
try:
    with open('cookies.pickle', 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
    print('Found cookies; using those instead of asking you for login')
except:
    print("Failed to open cookies file; manual login required")

browser = IvoryBrowser(config['instance_url'])
# Attempt Mastodon log-in
if len(cookies) > 0:
    driver = browser.login_with_cookies(cookies)
    print('Looks like login was successful.')
else:
    email = input('Enter email: ')
    password = getpass(prompt='Enter password: ')
    otp = input('If using OTP, enter OTP token: ')
    driver, cookies = browser.login_with_credentials(email, password, otp)
    print('Looks like login was successful. Saving cookies...')
    with open('cookies.pickle', 'wb') as cookies_file:
        pickle.dump(cookies, cookies_file)

# Cache report IDs to prevent making judgement multiple times
completed_reports = []

while True:
    print("Starting pass...")
    report_ids = browser.get_report_ids()
    for report_id in report_ids:
        # Skip if report ID is already completed, and add it to the list if not
        if report_id in completed_reports:
            print("Already did #%s, skipping..." % report_id)
            continue
        completed_reports.append(report_id)
        print("Handling report #%s..." % report_id)
        # Get the report and make judgement
        report = get_report(report_id)
        punishment, rules_broken = judge.make_judgement(report)
        # Punish if necessary
        if punishment:
            browser.punish_user(report, punishment)
            rule_names = [rule.name for rule in rules_broken]
            rule_names_pretty = ', '.join(rule_names)
            # Notify about punishment
            browser.add_note(report.id, "Ivory has punished this user for breaking rules: "+rule_names_pretty)
        else:
            # Note 0 rule violations
            browser.add_note(report.id, "Ivory found no rule violations.")
    print("Pass complete. Waiting for next pass...")
    time.sleep(config['wait_time'])
