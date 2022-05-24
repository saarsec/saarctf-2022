import json
import os
import time
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions

from .. import ServiceInterface, Team, TIMEOUT, OfflineException


class ServiceWithTimeout(Service):
    """
    Selenium service, with the connector wrapped for timeout reasons
    """

    def __init__(self, executable_path, port=0, service_args=None, log_path=None, env=None, timeout=60):
        wrapper = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selenium_wrapper')
        super().__init__(wrapper, port, service_args, log_path, env)
        self.prefix = [str(timeout), executable_path]

    def command_line_args(self):
        return self.prefix + super().command_line_args()


class SeleniumServiceInterface(ServiceInterface):
    """
    Service interface base class with Selenium integration. Check out "get_selenium_webdriver".
    """

    arguments = []  # additional arguments for the headless chrome process
    blocked_urls = []  # a list of url patterns that should not be accessed (example: "*/bootstrap.min.css")
    log_requested_urls = False  # collect a log of all requests made by the browser. Call #print_selenium_logs at the end of your script to access.

    def __init__(self, service_id: int):
        super().__init__(service_id)
        self.service: Optional[Service] = None
        self.webdriver: Optional[WebDriver] = None

    def initialize_team(self, team: Team):
        self.service = None
        self.webdriver = None

    def finalize_team(self, team: Team):
        try:
            if self.webdriver is not None:
                self.webdriver.quit()
                self.webdriver = None
        finally:
            if self.service is not None:
                self.service.stop()
                self.service = None

    def get_selenium_webdriver(self, arguments=None, timeout=TIMEOUT) -> WebDriver:
        if self.webdriver:
            return self.webdriver
        if not arguments:
            arguments = self.arguments
        if not self.service:
            self.service = ServiceWithTimeout('/usr/bin/chromedriver', timeout=65)
            # self.service = ServiceWithTimeout('/usr/bin/chromedriver', timeout=50, service_args=['--verbose', f'--log-path=/dev/shm/chromedriver-{os.getpid()}.log'])  # TODO timeout
            self.service.start()
            print(f'[selenium] new service started: {self.service.service_url}')
        # By default, ChromeDriver will create a new temporary profile for each session. (https://chromedriver.chromium.org/capabilities)
        options = webdriver.ChromeOptions()
        # copied from Chromium's unittests
        options.add_argument('disable-plugins')
        options.add_argument('disable-translate')
        options.add_argument('disable-permissions-api')
        options.add_argument('no-experiments')
        options.add_argument('no-crash-upload')
        options.add_argument('no-default-browser-check')
        options.add_argument('no-first-run')
        # more config
        options.add_argument('enable-logging=stderr')
        options.add_argument('disable-3d-apis')
        options.add_argument('disable-crash-reporter')
        options.add_argument('disable-gpu')
        options.add_argument('disable-nacl')
        options.add_argument('disable-bundled-ppapi-flash')
        options.add_argument('disable-accelerated-video-decode')
        options.add_argument('window-size=1280,1024')
        options.add_argument('headless')
        # options.add_argument('no-sandbox')
        # options.add_argument('disable-dev-shm-usage')
        if arguments:
            for arg in arguments:
                options.add_argument(arg)

        caps = DesiredCapabilities.CHROME
        if self.log_requested_urls:
            caps = dict(caps.items())
            caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.webdriver = webdriver.Remote(self.service.service_url, options=options, desired_capabilities=caps)
        self.webdriver.set_page_load_timeout(timeout)
        # add missing support for chrome "send_command"  to selenium webdriver
        self.webdriver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        if self.blocked_urls:
            self.set_blocked_urls(self.webdriver, self.blocked_urls)
        print('[selenium] new webdriver', self.webdriver.name)
        return self.webdriver

    def set_blocked_urls(self, driver: WebDriver, patterns: List[str]):
        params = {'cmd': 'Network.setBlockedURLs', 'params': {'urls': patterns}}
        command_result = self.webdriver.execute("send_command", params)
        params = {'cmd': 'Network.enable', 'params': {}}
        command_result = self.webdriver.execute("send_command", params)

    def wait_for_element_by_id(self, driver: WebDriver, id: str) -> None:
        """
        Block until the element #id is present in the current page of the browser, or raise an OfflineException in case of timeout.
        :param driver:
        :param id:
        :return:
        """
        try:
            element_present = EC.presence_of_element_located((By.ID, id))
            WebDriverWait(driver, TIMEOUT * 1000).until(element_present)
        except exceptions.TimeoutException:
            raise OfflineException(f"Timed out waiting for page to load / element '{id}' to appear")

    def wait_for_element_by_xpath(self, driver: WebDriver, xpath: str) -> None:
        """
        Block until an element with the given xpath is present in the current page of the browser, or raise an OfflineException in case of timeout.
        :param driver:
        :param xpath:
        :return:
        """
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(driver, TIMEOUT * 1000).until(element_present)
        except exceptions.TimeoutException:
            print(f'Timeout waiting for xpath: {xpath}')
            raise OfflineException("Timed out waiting for page to load / link to appear")

    def print_selenium_logs(self) -> None:
        if self.log_requested_urls and self.webdriver:
            browser_log = self.webdriver.get_log('performance')
            for log in browser_log:
                msg = json.loads(log['message'])['message']
                if msg['method'] == 'Network.requestWillBeSent':
                    url = msg.get('params', {}).get('request', {}).get('url', '')
                    if url:
                        self.print_log(msg['params']['request']['method'], url)

    def print_log(self, method: str, url: str) -> None:
        if url.startswith('data:') or url.startswith('blob:'):
            return
        print(method, url)


# ==========
# Example code how inherited classes could be checked
# ==========
if __name__ == '__main__':
    service = SeleniumServiceInterface(1)
    team = Team(1, 'localhost', '127.0.0.1')
    for tick in range(1, 4):
        ts = time.time()
        service.initialize_team(team)
        try:
            print(f'[tick {tick}] check integrity ...')
            service.check_integrity(team, tick)
            print(f'[tick {tick}] store flags ...')
            service.store_flags(team, tick)
            print(f'[tick {tick}] retrieve flags ...')
            service.retrieve_flags(team, tick)
        finally:
            service.finalize_team(team)
        ts = time.time() - ts
        print(f'[tick {tick}] checking done, took {ts:.3f} seconds.')
    print('[done]')
