import time
import os
import subprocess
import processes
import logging
from logging.handlers import RotatingFileHandler

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jsSeo')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('jsSeo.log', maxBytes=10*1000*1000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)


# Xvfb
class Xvfb():
    def start(self):
        '''start xvfb. this will be called only if the system has
        no display servers'''
        assert('DISPLAY' not in os.environ)
        try:
            displayno = ':0'
            self.process = subprocess.Popen(['Xvfb', displayno, '-screen', '0', '1024x768x16'])
            time.sleep(0.2)
            return_code = self.process.poll()

            if return_code is not None:
                logger.error('Xvfb did not start')
            else:
                self.display = displayno

        except OSError, e:
            logger.error('Check whether Xvfb is installed', exc_info=True)
        except subprocess.CalledProcessError, e:
            logger.error('CalledProcessError', exc_info=True)

    def stop(self):
        if self.process is not None:
            self.process.kill()
            self.process.wait()
            self.process = None
