import os
import time
import subprocess

def kill_process(pid):
    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError as ex:
        print str(ex)
        os.kill(int(pid), signal.SIGKILL)

def running_instances(browser):
    '''returns a list of pids of running chrome processes'''
    try:
        pids = subprocess.check_output(["pidof", browser])
        pids = pids.split(' ')
        return pids

    except subprocess.CalledProcessError:
        return []

def kill_instances(pids):
    '''checks for running google-chrome instances every 5 seconds.
    kills all of them in turn. returns after all instances have
    closed'''
    while True:
        time.sleep(5)
        for pid in pids:
            kill_process(pid)
        else:
            break
