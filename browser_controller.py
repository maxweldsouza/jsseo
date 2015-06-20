import subprocess
import os
import signal
from config import config
import processes

'''for starting chrome with a custom user agent
chrome processes should not be running already'''

BOT_USER_AGENT = 'jsSeoBot'
DISPLAY = None

def active_displays():
    '''gets the display no for an active server. Returns
    None if there are none available'''
    locks = fnmatch.filter(os.listdir('/tmp'), '.X*-lock')
    locks = [lock for lock in locks if os.path.isfile(os.path.join('/tmp', lock))]
    # get the display no, .X11-lock => 11
    displays = [int(lock.split('X')[1].split('-')[0]) for lock in locks]
    return displays

def start_chrome_like_browser(url, name):
    '''run a browser in a subprocess'''
    command = ' '.join([name, '--user-agent=' + BOT_USER_AGENT, url])
    if config['headless']:
        env = os.environ.copy()
        env['DISPLAY'] = ':' + DISPLAY
    else:
        env=None
    return subprocess.Popen(command, shell=True, env=env)

class Browser():
    def __init__(self):
        if config['headless']:
            displays = active_displays()
            if displays == None:
                xvfb.start()
            else:
                DISPLAY = displays[0]

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
        return start_chrome_like_browser(url, self.name)

class Chromium(Browser):
    def __init__(self):
        self.name = 'chromium-browser'
        Browser.__init__(self)

    def start(self, url):
        return start_chrome_like_browser(url, self.name)
