import browser
import xvfb
from config import config

if config['headless'] and not xvfb.is__running():
    xvfb.start()

chromium = browser.Chromium()
chromium.kill_all()
chromium.start('http://localhost')
