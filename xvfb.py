import os
import subprocess
import processes

XVFB_PID = None

# Xvfb
def start():
    '''start xvfb. this should be called only if the system has
    no display servers'''
    assert('DISPLAY' not in os.environ)
    try:
        os.environ['DISPLAY'] = ':0'
        process = subprocess.Popen(['ls'])
        XVFB_PID = process.pid
    except OSError, e:
        del os.environ['DISPLAY']
        print 'Check whether Xvfb is installed'
    except subprocess.CalledProcessError, e:
        del os.environ['DISPLAY']
        print str(e)

def is__running():
    return XVFB_PID != None

def close():
    processes.kill_process(XVFB_PID)

print XVFB_PID
