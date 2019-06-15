from getpass import getpass
import utils.browser as browser
import yaml
import pickle
from classes.report import Report
import time

with open('config.yml') as config_yml:
    config = yaml.load(config_yml, Loader=yaml.Loader)

# get cookies if we can
cookies = []
try:
    with open('cookies.pickle', 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)
    print('found cookies; using those instead of asking you for login')
except:
    print("failed to open cookies file; manual login required")

instance_url = config['instance_url']
# Attempt Mastodon log-in
if len(cookies) > 0:
    driver = browser.login_with_cookies(instance_url, cookies)
    print('Looks like login was successful.')
else:
    email = input('Enter email: ')
    password = getpass(prompt='Enter password: ')
    otp = input('If using OTP, enter OTP token: ')
    driver, cookies = browser.login_with_credentials(instance_url, email, password, otp)
    print('Looks like login was successful. Saving cookies...')
    with open('cookies.pickle', 'wb') as cookies_file:
        pickle.dump(cookies, cookies_file)

# we should be signed in now, let's get to the admin page
driver.get(instance_url + '/admin/reports')
# TODO convert to explicit wait
time.sleep(1)
# parse out report links
report_urls = [element.get_attribute('href') for element in driver.find_elements_by_xpath('//div[@class="report-card__summary__item__content"]/a')]
print("found",len(report_urls), "reports.")
# visit first report link and judge it
report_id = report_urls[0].split('/')[-1]
print("processing report",report_id)
driver.get(report_urls[0])
reported_statuses = driver.find_elements_by_class_name('status__content')
# find womenarestupid.site spam by link
for reported_status in reported_statuses:
    links = reported_status.find_elements_by_tag_name('a')
    judged = False
    for link in links:
        if link.get_attribute('href') == "https://womenarestupid.site/blog/the-don-t-marry-movement":
            judged = True
            # yeet the banhammer at em
            driver.find_element_by_xpath('//a[text()="Suspend"]').click()
            # TODO convert to explicit wait
            time.sleep(1)
            # this line could fail so fucking hard
            driver.find_elements_by_tag_name('button')[0].click()
            # TODO convert to explicit wait
            time.sleep(1)
            # return to the report and comment
            driver.get(report_urls[0])
            message = "Suspension performed by Ivory. Reason: no womenarestupid.site spam"
            driver.find_element_by_id('report_note_content').send_keys(message)
            # hacky way to get the add note button but good enough for now
            driver.get_element_by_name('button').click()
            break
    if judged:
        break
