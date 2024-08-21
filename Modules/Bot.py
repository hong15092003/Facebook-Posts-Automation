import logging
from difflib import SequenceMatcher
import platform
from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)


def url_parse(url):
    if url is None or url == '' or url.count('.') == 0 or 'facebook.com' not in url:
        return None
    if url.count('/') == 0:
        return 'http://mbasic.facebook.com/'
    return 'http://mbasic.facebook.com/' + url[url.find('.com/') + len('.com/')::]


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class Bot:
    def __init__(self, headless):
        self.options = webdriver.FirefoxOptions()
        if headless:
            self.options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.implicitly_wait('5')
        self.logged_in = False

    def __del__(self):
        if self.driver.service.process is not None:
            self.driver.quit()

    def check_browser_state(self):
        try:
            x = self.driver.current_url
        except InvalidSessionIdException and WebDriverException:
            self.driver.quit()
            self.__init__(self.options.headless)
            print('Restarting browser..')

    def doLogin(self, username, password):
        if not self.logged_in:
            try:
                self.driver.get('http://mbasic.facebook.com')
                user_box = self.driver.find_element(By.XPATH, '//input[@name="email"]')
                user_box.send_keys(username)
                password_box = self.driver.find_element(By.XPATH, '//input[@name="pass"]')
                password_box.send_keys(password)
                login_btn = self.driver.find_element(By.XPATH, '//input[@name="login"]')
                login_btn.click()
                if self.driver.title == 'Facebook':
                    self.logged_in = True
                    return 'Login Successful'
                else:
                    return 'Failed to login'
            except NoSuchElementException as e:
                logging.error(e)
            except WebDriverException as e:
                logging.error(e)
        return 'Already logged in'

    def postToUrl(self, message='', media_path='', url='http://mbasic.facebook.com'):
        url = url_parse(url)
        if url is None:
            return 'Bad url'
        try:
            self.driver.get(url)

            if message != '':
                textbox = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//textarea[@name="xc_message"]'))
                )
                textbox.send_keys(message)

            if media_path is not None and media_path != '' and media_path != 'None':
                current_os = platform.system()
                if current_os == 'Windows':
                    media_path = media_path.replace('/', '\\')
                upload_photo = self.driver.find_element(By.XPATH, '//input[@name="view_photo"]')
                upload_photo.click()
                upload_photo = self.driver.find_element(By.XPATH, '//input[@name="file1"]')
                upload_photo.send_keys(media_path)
                upload_photo = self.driver.find_element(By.XPATH, '//input[@name="add_photo_done"]')
                upload_photo.click()

            if media_path != '' or message != '':
                post_btn = self.driver.find_element(By.XPATH, '//input[@name="view_post"]')
                post_btn.click()
                return 'Posted to :' + url
        except Exception as e:
            print(f"An error occurred: {e}")
            return 'Failed to post'

    def groupScraper(self, url):
        try:
            self.driver.get(url)
            
            # Wait for the "Members" link to be present
            members_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[text()="Members"]'))
            )
            members_btn.click()
            
            # Add further scraping logic here
            return 'Scraping Successful'
        except NoSuchElementException as e:
            logging.error(f"Element not found: {e}")
            return 'Failed to find element'
        except WebDriverException as e:
            logging.error(f"WebDriver exception occurred: {e}")
            return 'WebDriver exception occurred'
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return 'An unexpected error occurred'

    def logout(self):
        try:
            self.logged_in = False
            self.driver.delete_all_cookies()
            self.driver.get('https://mobile.facebook.com/')
            return 'Logged out successfully'
        except WebDriverException as e:
            logging.error(e)
            return 'Failed to logout'
