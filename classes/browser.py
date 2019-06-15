# webdriver itself
from selenium import webdriver
# WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# for (safely) parsing URLs
from urllib.parse import urljoin

class IvoryBrowser:
    def __init__(self, instanceURL, defaultTimeout=10):
        self.instanceURL = instanceURL
        self.driver = webdriver.Firefox()
        self.__wait = WebDriverWait(self.driver, defaultTimeout)
    def __url(self, path=''):
        return urljoin(self.instanceURL, path)
    def login_with_cookies(self, cookies):
        """
        Login to the given instance using stored cookies.

        Current implementation is pretty rough - needs more checking to see if the
        cookies are actually working or not.
        """
        self.driver.get(self.__url())
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        return True
    def login_with_credentials(email, password, otp=""):
        """
        Login to the given instance using user credentials.

        Returns:
        list: A list of cookies in Selenium-consumable form. Save this and use it with login_with_cookies for future logins.
        """
        self.driver.get(self.__url('/auth/sign_in'))
        # Email + Password
        self.driver.find_element_by_id("user_email").send_keys(email)
        pwfield = self.driver.find_element_by_id("user_password")
        pwfield.send_keys(password)
        pwfield.submit()
        # Server needs a sec to catch up
        self.__wait.until(EC.title_contains('Reports'))
        # OTP
        # TODO NON-OTP IS UNTESTED
        if len(otp) > 0:
            otpfield = self.driver.find_element_by_id('user_otp_attempt')
            otpfield.send_keys(otp)
            otpfield.submit()
            # Server needs a sec to catch up
            self.__wait.until(EC.url_contains('getting-started'))
        # Grab cookies
        cookies = self.driver.get_cookies()
        return cookies
    def get_latest_report_id(self):
        self.driver.get(self.__url('/admin/reports'))
        self.__wait.until(EC.title_contains('Reports'))
        href = self.driver.find_element_by_xpath('//div[@class="report-card__summary__item__content"]/a').get_attribute('href')
        return href.split('/')[-1]
    def get_report(self, rep_id):
        # Convert to string here, just to be sure
        report_id = str(rep_id)
        # Parse the report from the page itself
        self.driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        report = {
            "id": report_id
        }
        # Get report status
        report_status = self.driver.find_element_by_xpath('//table[1]//tr[5]/td[1]').text
        report['status'] = report_status
        # Get reported user
        reported_row = self.driver.find_element_by_xpath('//table[1]//tr[1]/td[1]/a')
        reported_link = reported_row.get_attribute('href')
        reported_username = reported_row.get_attribute('title')
        reported_id = reported_row.get_attribute('href').split('/')[-1]
        report['reported'] = {
            "id": reported_id,
            "username": reported_username,
            "link": reported_link
        }
        # Get reporter data
        reporter_row = self.driver.find_element_by_xpath('//table[1]//tr[2]/td[1]/a')
        reporter_link = reporter_row.get_attribute('href')
        reporter_username = reporter_row.get_attribute('title')
        reporter_id = reporter_row.get_attribute('href').split('/')[-1]
        report['reporter'] = {
            "id": reporter_id,
            "username": reporter_username,
            "link": reporter_link
        }
        # Get reporter's comment
        reporter_comment = self.driver.find_element_by_class_name('speech-bubble__bubble').text
        report['comment'] = reporter_comment
        # Get reported posts
        reported_posts = self.driver.find_elements_by_class_name('status__content')
        report['posts'] = [post.text for post in reported_posts]
        # Get links in reported posts
        report['links'] = []
        for post in reported_posts:
            links = post.find_elements_by_tag_name('a')
            for link in links:
                report['links'].append(link.get_attribute('href'))
        return report
    def add_note(self, rep_id, message):
        # Convert to string here, just to be sure
        report_id = str(rep_id)
        # Parse the report from the page itself
        self.driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
