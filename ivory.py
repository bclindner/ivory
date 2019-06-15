from classes.browser import IvoryBrowser
from classes.judge import Judge
import classes.rules as rules

from getpass import getpass

import yaml
import pickle

import sys

try:
    report_id = sys.argv[1]
except:
    print("No report ID specified. Exiting.")
    exit(1)

try:
    with open('config.yml') as config_yml:
        config = yaml.load(config_yml, Loader=yaml.Loader)
except:
    print("Failed to open config file!")
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

report = browser.get_report("977")
punish_rule, rules_broken = judge.make_judgement(report)
print("Punish rule:",punish_rule.punishment)
print("All broken rules:",rules_broken)
