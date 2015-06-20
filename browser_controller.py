import subprocess
import os
import signal
from config import config
import processes
import fnmatch
import logging
from logging.handlers import RotatingFileHandler

'''for starting chrome with a custom user agent
chrome processes should not be running already'''

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jsSeo')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('jsSeo.log', maxBytes=10*1000*1000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

BOT_USER_AGENT = 'jsSeoBot'

def active_displays():
    '''gets the display no for an active server. Returns
    None if there are none available'''
    locks = fnmatch.filter(os.listdir('/tmp'), '.X*-lock')
    locks = [lock for lock in locks if os.path.isfile(os.path.join('/tmp', lock))]
    # get the display no ex: .X11-lock => 11
    displays = [int(lock.split('X')[1].split('-')[0]) for lock in locks]
    displays = [':' + str(x) for x in displays]
    return displays

def start_chrome_like_browser(url, name, display):
    '''run a browser in a subprocess'''
    command = ' '.join([name, '--user-agent=' + BOT_USER_AGENT, url])
    if config['headless']:
        os.environ['DISPLAY'] = display
    logger.info('Starting %s on display %s with command: %s', name, display, command)
    return subprocess.Popen(command, shell=True)

class Browser():
    def __init__(self):
        displays = active_displays()
        if displays is not None:
            self.display = displays[0]

        if config['headless'] and displays is None:
            logger.info('xvfb is not already running. starting xvfb')
            xvfb.start()
            self.display = xvfb.display

    def start(self, url):
        pass
    def running_instances(self):
        return processes.running_instances(self.name)
    def kill_all(self):
        processes.kill_instances(self.running_instances())

class GoogleChrome(Browser):
    def __init__(self):
        self.name = 'google-chrome'
        Browser.__init__(self)

    def start(self, url):
        return start_chrome_like_browser(url, self.name, self.display)

class Chromium(Browser):
    def __init__(self):
        self.name = 'chromium-browser'
        Browser.__init__(self)

    def start(self, url):
        return start_chrome_like_browser(url, self.name, self.display)
