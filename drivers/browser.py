import pickle
# for (safely) parsing URLs
from urllib.parse import urljoin
# for getting passwords during initialization
from getpass import getpass
# The WebDriver itself
from selenium import webdriver
# WebDriverWait stuff
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# NoElementFoundException, which we use to handle some potential fault areas
from selenium.common.exceptions import NoSuchElementException
# Ivory imports
from core import Report, Driver, User

# Default timeout for the Selenium driver to get a Web page.
DEFAULT_TIMEOUT = 30

class BrowserDriver(Driver):
    """
    A Selenium-based browser driver for Ivory.
    """

    def __init__(self, config):
        Driver.__init__(self)
        try:
            self.instance_url = config['instance_url']
        except KeyError:
            print("ERROR: Instance URL not found in your config! Is it set correctly?")
            exit(1)
        self.__driver = webdriver.Firefox()
        self.__wait = WebDriverWait(self.__driver, DEFAULT_TIMEOUT)
        # Attempt log-in
        cookies = []
        try:
            with open('cookies.pickle', 'rb') as cookies_file:
                cookies = pickle.load(cookies_file)
            print('Found cookies; using those instead of asking you for login')
        except Exception:
            print("Failed to open cookies file; manual login required")
        if cookies:
            self.__login_with_cookies(cookies)
            print('Looks like login was successful.')
        else:
            email = input('Enter email: ')
            password = getpass(prompt='Enter password: ')
            otp = input('If using OTP, enter OTP token: ')
            cookies = self.__login_with_credentials(email, password, otp)
            print('Looks like login was successful. Saving cookies...')
            with open('cookies.pickle', 'wb') as cookies_file:
                pickle.dump(cookies, cookies_file)

    def __url(self, path=''):
        return urljoin(self.instance_url, path)

    def __login_with_cookies(self, cookies):
        """
        Login to the given instance using stored cookies.

        Current implementation is pretty rough - needs more checking to see if the
        cookies are actually working or not.
        """
        self.__driver.get(self.__url())
        for cookie in cookies:
            self.__driver.add_cookie(cookie)
        return True

    def __login_with_credentials(self, email, password, otp=""):
        """
        Login to the given instance using user credentials.

        Returns:
        list: A list of cookies in Selenium-consumable form.
        Save this and use it with login_with_cookies for future logins.
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
        if otp:
            otpfield = self.__driver.find_element_by_id('user_otp_attempt')
            otpfield.send_keys(otp)
            otpfield.submit()
            # Server needs a sec to catch up
            self.__wait.until(EC.url_contains('getting-started'))
        # Grab cookies
        cookies = self.__driver.get_cookies()
        return cookies

    def get_unresolved_report_ids(self):
        """
        Scrapes the page to get unresolved reports.

        This does not get all reports! Currently it's just designed to get what
        it can. If you end up with more than a page of reports at a time, this
        driver might not work for you for now.
        """
        self.__driver.get(self.__url('/admin/reports'))
        self.__wait.until(EC.title_contains('Reports'))
        links = self.__driver.find_elements_by_xpath(
            '//div[@class="report-card__summary__item__content"]/a')
        return [link.get_attribute('href').split('/')[-1] for link in links]

    def get_report(self, report_id: str):
        """
        Scrape the report page into a Report object.
        """
        # Parse the report from the page itself
        self.__driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        # Get report status
        report_status = self.__driver.find_element_by_xpath(
            '//table[1]//tr[5]/td[1]').text
        # Get reported user
        reported_row = self.__driver.find_element_by_xpath(
            '//table[1]//tr[1]/td[1]/a')
        reported_username = reported_row.get_attribute('title')
        reported_id = reported_row.get_attribute('href').split('/')[-1]
        reported_user = User(reported_id, reported_username)
        # Get reporter data
        try:
            reporter_row = self.__driver.find_element_by_xpath(
                '//table[1]//tr[2]/td[1]/a')
            reporter_username = reporter_row.get_attribute('title')
            reporter_id = reporter_row.get_attribute('href').split('/')[-1]
            reporter_user = User(reporter_id, reporter_username)
        except NoSuchElementException:
            # If that block failed, then this was probably a federated report
            # forwarded to us - set reporter_user to None
            reporter_user = None
        # Get reporter's comment
        reporter_comment = self.__driver.find_element_by_class_name(
            'speech-bubble__bubble').text
        # Get reported posts
        posts = self.__driver.find_elements_by_class_name('status__content')
        reported_posts = [post.text for post in posts]
        # Get links in reported posts
        links = self.__driver.find_elements_by_xpath(
            '//div[@class="status__content"]//a')
        reported_links = [link.get_attribute(
            'href') for link in links]  # lmfao
        # Turn it all into a Report object and send it back
        report = Report(report_id, report_status, reported_user,
                        reporter_user, reporter_comment, reported_posts, reported_links)
        return report

    def add_note(self, report_id: str, message: str, resolve: bool = False):
        """
        Adds a note through the reports page directly.
        """
        # Parse the report from the page itself
        self.__driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        self.__driver.find_element_by_id(
            'report_note_content').send_keys(message)
        buttons = self.__driver.find_elements_by_class_name('btn')
        if resolve:
            buttons[0].click()
        else:
            buttons[1].click()
        self.__wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'notice')))

    def punish(self, report, punishment):
        """
        Punish a user.
        """
        if punishment.type == 'suspend':
            self.suspend(report.report_id)
        else:
            raise NotImplementedError()

    def suspend(self, report_id):
        """
        Suspends a user through the reports page directly.
        """
        self.__driver.get(self.__url('/admin/reports/') + report_id)
        self.__wait.until(EC.title_contains('Report #'+report_id))
        self.__driver.find_element_by_xpath(
            '//div[@class="content"]/div[1]//a[text() = "Suspend"]').click()
        self.__wait.until(EC.title_contains('Perform moderation'))
        self.__driver.find_element_by_class_name('btn').click()
        self.__wait.until(EC.title_contains('Reports'))
