import subprocess
import os
import signal
from config import config
import processes

'''for starting chrome with a custom user agent
chrome processes should not be running already'''

botagent = 'jsSeoBot'

def start_chrome_like_browser(url, name):
    '''run a browser in a subprocess'''
    command = [name, '--user-agent=' + botagent, url]
    if config['headless']:
        assert('DISPLAY' in os.environ)
        command = ['DISPLAY=' + os.environ['DISPLAY']] + command
    return subprocess.Popen(command)

class Browser():
    def start(self, url):
        pass
    def running_instances(self):
        return processes.running_instances(self.name)
    def kill_all(self):
        processes.kill_instances(self.running_instances())

class GoogleChrome(Browser):
    def __init__(self):
        self.name = 'google-chrome'

    def start(self, url):
        return start_chrome_like_browser(url, self.name)

class Chromium(Browser):
    def __init__(self):
        self.name = 'chromium-browser'

    def start(self, url):
        return start_chrome_like_browser(url, self.name)
