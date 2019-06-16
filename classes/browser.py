# webdriver itself
from selenium import webdriver
# WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# for (safely) parsing URLs
from urllib.parse import urljoin

from .report import Report
from .user import User

import time

class IvoryBrowser:
    def __init__(self, instanceURL, defaultTimeout=10):
        self.instanceURL = instanceURL
        self.__driver = webdriver.Firefox()
        self.__wait = WebDriverWait(self.__driver, defaultTimeout)
    def __url(self, path=''):
        return urljoin(self.instanceURL, path)
    def login_with_cookies(self, cookies):
        """
        Login to the given instance using stored cookies.

        Current implementation is pretty rough - needs more checking to see if the
        cookies are actually working or not.
        """
        self.__driver.get(self.__url())
        for cookie in cookies:
            self.__driver.add_cookie(cookie)
        return True
    def login_with_credentials(email, password, otp=""):
        """
        Login to the given instance using user credentials.

        Returns:
        list: A list of cookies in Selenium-consumable form. Save this and use it with login_with_cookies for future logins.
        """
        self.__driver.get(self.__url('/auth/sign_in'))
        # Email + Password
        self.__driver.find_element_by_id("user_email").send_keys(email)
        pwfield = self.__driver.find_element_by_id("user_password")
        pwfield.send_keys(password)
        pwfield.submit()
        # Server needs a sec to catch up
        self.__wait.until(EC.title_contains('Reports'))
        # OTP
        # TODO NON-OTP IS UNTESTED
        if len(otp) > 0:
            otpfield = self.__driver.find_element_by_id('user_otp_attempt')
            otpfield.send_keys(otp)
            otpfield.submit()
            # Server needs a sec to catch up
            self.__wait.until(EC.url_contains('getting-started'))
        # Grab cookies
        cookies = self.__driver.get_cookies()
        return cookies
    def get_latest_report_id(self):
        self.__driver.get(self.__url('/admin/reports'))
        self.__wait.until(EC.title_contains('Reports'))
        href = self.__driver.find_element_by_xpath('//div[@class="report-card__summary__item__content"]/a').get_attribute('href')
        return href.split('/')[-1]
    def get_report_ids(self):
        self.__driver.get(self.__url('/admin/reports'))
        self.__wait.until(EC.title_contains('Reports'))
        links = self.__driver.find_elements_by_xpath('//div[@class="report-card__summary__item__content"]/a')
        return [link.get_attribute('href').split('/')[-1] for link in links]
    def get_report(self, rep_id):
        # Convert to string here, just to be sure
        report_id = str(rep_id)
        # Parse the report from the page itself
        self.__driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        # Get report status
        report_status = self.__driver.find_element_by_xpath('//table[1]//tr[5]/td[1]').text
        # Get reported user
        reported_row = self.__driver.find_element_by_xpath('//table[1]//tr[1]/td[1]/a')
        reported_link = reported_row.get_attribute('href')
        reported_username = reported_row.get_attribute('title')
        reported_id = reported_row.get_attribute('href').split('/')[-1]
        reported_user = User(reported_id, reported_username)
        # Get reporter data
        reporter_row = self.__driver.find_element_by_xpath('//table[1]//tr[2]/td[1]/a')
        reporter_link = reporter_row.get_attribute('href')
        reporter_username = reporter_row.get_attribute('title')
        reporter_id = reporter_row.get_attribute('href').split('/')[-1]
        reporter_user = User(reported_id, reported_username)
        # Get reporter's comment
        reporter_comment = self.__driver.find_element_by_class_name('speech-bubble__bubble').text
        # Get reported posts
        posts = self.__driver.find_elements_by_class_name('status__content')
        reported_posts = [post.text for post in posts]
        # Get links in reported posts
        links = self.__driver.find_elements_by_xpath('//div[@class="status__content"]//a')
        reported_links = [link.get_attribute('href') for link in links] # lmfao
        # Turn it all into a Report object and send it back
        report = Report(report_id, report_status, reported_user, reporter_user, reporter_comment, reported_posts, reported_links)
        return report
    def add_note(self, rep_id, message, resolve=False):
        # Convert to string here, just to be sure
        report_id = str(rep_id)
        # Parse the report from the page itself
        self.__driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        self.__driver.find_element_by_id('report_note_content').send_keys(message)
        buttons = self.__driver.find_elements_by_class_name('btn')
        if resolve:
            buttons[0].click()
        else:
            buttons[1].click()
        self.__wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'notice')))
    def suspend_user(self, user_id, report_id, delete_account_data=True, message=""):
        self.__driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        self.__driver.find_element_by_xpath('//div[@class="content"]/div[1]/div[1]/a[2]').click()
        self.__wait.until(EC.title_contains('Perform moderation'))
        self.__driver.find_element_by_class_name('btn').click()
        self.__wait.until(EC.title_contains('Reports'))
    def silence_user(self, user_id, report_id="", message=""):
        self.__driver.get(self.__url('/admin/accounts/218050/action/new?report_id=%s&type=silence' % report_id))
        pass
    def warn_user(self, user_id, report_id="", message=""):
        self.__driver.get(self.__url('/admin/accounts/218050/action/new?report_id=%s&type=none' % report_id))
        pass
    def punish_user(self, report, punishment):
        if punishment.type == 'suspend':
            self.suspend_user(report.reported.id, report.id)
        else:
            print("Punishment type", punishment.type, "not implemented.")
