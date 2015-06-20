import os
import time
import subprocess
import signal
import logging
from logging.handlers import RotatingFileHandler

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jsSeo')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('jsSeo.log', maxBytes=10*1000*1000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)


def kill_process(pid):
    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError as ex:
        print str(ex)
        os.kill(int(pid), signal.SIGKILL)

def running_instances(name):
    '''returns a list of pids of running processes with given name'''
    try:
        output = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
        processes = output.split('\n')
        processes.pop() # remove empty last line
        processes = [x.split() for x in processes]
        # first value is the pid, process names may have spaces in them
        pids = [x[1] for x in processes if name in x[10]]
        return pids

    except subprocess.CalledProcessError:
        logger.error('Called Process Error', exc_info=True)
