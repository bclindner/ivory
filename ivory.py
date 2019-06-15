from getpass import getpass
import utils.browser as browser
import yaml
import pickle

with open('config.yml') as config_yml:
    config = yaml.load(config_yml, Loader=yaml.Loader)

cookies = []
try:
    with open('cookies.pickle', 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
    print('found cookies; using those instead of asking you for login')
except Exception:
    print("failed to open cookies file; manual login required")

print(config)
instance_url = config['instance_url']
# Attempt Mastodon log-in
if len(cookies) > 0:
    driver = browser.login_with_cookies(instance_url)
else:
    email = input('Enter email: ')
    password = getpass(prompt='Enter password: ')
    otp = input('If using OTP, enter OTP token: ')
    driver, cookies = browser.login_with_credentials(instance_url, email, password, otp)
    print('Looks like login was successful. Saving cookies...')
    with open('cookies.pickle', 'wb') as cookies_file:
        pickle.dump(cookies, cookies_file)

# we should be signed in now, let's get to the admin page
driver.get(instance_url + '/admin/reports?resolved=1')
# parse out reports
reportcards = driver.find_elements_by_class_name('report-card')
print("found",len(reportcards), "reported accounts.")
for reportcard in reportcards:
    username = reportcard.find_element_by_class_name('display-name__account').text
    print("Reports for", username)
    reports = reportcard.find_elements_by_class_name('report-card__summary__item')
    for report in reports:
        report_text = report.find_element_by_class_name('one-line').text
        reported_by = report.find_element_by_class_name('report-card__summary__item__reported-by').text
        print(reported_by+":",report_text)
