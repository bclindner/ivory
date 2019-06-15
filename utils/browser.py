from selenium import webdriver
import time

def get_driver():
    """
    Get a Selenium webdriver.

    This is defined here so it can be easily changed, and all functions are
    using the same webdriver type.

    Returns:
    WebDriver: a standard Selenium webdriver (currently Gecko).
    """
    return webdriver.Firefox()

def login_with_cookies(instanceURL, cookies):
    """
    Login to the given instance using stored cookies.

    Current implementation is pretty rough - needs more checking to see if the
    cookies are actually working or not.

    Returns:
    WebDriver: a Selenium webdriver logged into the given instance URL.
    """
    driver = get_driver()
    driver.get(instanceURL)
    for cookie in cookies:
        driver.add_cookie(cookie)
    return driver
def login_with_credentials(instanceURL, email, password, otp=""):
    """
    Login to the given instance using user credentials.

    Returns:
    WebDriver: a Selenium webdriver logged into the given instance URL.
    list: A list of cookies in Selenium-consumable form. Save this and use it with login_with_cookies for future logins.
    """
    driver = get_driver()
    driver.get(instanceURL + '/auth/sign_in')
    # username+password
    driver.find_element_by_id("user_email").send_keys(email)
    pwfield = driver.find_element_by_id("user_password")
    pwfield.send_keys(password)
    pwfield.submit()
    # server needs a sec to catch up
    # TODO change this to an explicit wait
    time.sleep(1)
    # otp
    if len(otp) > 0:
        otpfield = driver.find_element_by_id('user_otp_attempt')
        otpfield.send_keys(otp)
        otpfield.submit()
        # server needs a sec to catch up
        # TODO change this to an explicit wait
        time.sleep(1)
    # grab cookies
    cookies = driver.get_cookies()
    return (driver, cookies)
