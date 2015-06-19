import xvfb
from config import config
import browser_controller

if config['headless'] and not xvfb.is_running():
    xvfb.start()

if config['browser'] == 'chromium':
    browser = browser_controller.Chromium()
elif config['browser'] == 'google-chrome':
    browser = browser_controller.GoogleChrome()

browser.kill_all()
browser.start('http://localhost')
