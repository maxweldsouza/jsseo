import time
import subprocess
import os
import signal
from config import config
import processes
import fnmatch
import logging
from xvfb import Xvfb
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
        if not displays:
            if config['headless']:
                logger.info('Xvfb is not already running. Starting xvfb')
                xvfb = Xvfb()
                xvfb.start()
                self.display = xvfb.display
            else:
                logger.error('Headless mode is off in config but there are no displays')
        else:
            self.display = displays[0]

    def start(self, url):
        pass
    def running_instances(self):
        return processes.running_instances(self.name)
    def kill_all(self):
        while True:
            running = self.running_instances()
            if len(running) == 0:
                return
            try:
                for process in running:
                    processes.kill_process(process)
            except OSError:
                pass
            # give em some time
            time.sleep(5)

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
