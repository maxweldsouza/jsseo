import subprocess
import time
import os
import signal

def start_browser():
    '''Run a browser in a subprocess'''
    return subprocess.Popen(['google-chrome', '--user-agent=jsseobot', 'http://google.com'])

def kill_process(pid):
    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError as ex:
        os.kill(int(pid), signal.SIGKILL)

def test():
    browser = start_browser()
    time.sleep(20)
    kill_process(browser.pid)

def chrome_running_instances():
    print 'killing running chrome instances'
    try:
        # for user-agent to work any chrome processes should not
        # already be running
        pids = subprocess.check_output(["pidof", "chrome"])
        pids = pids.split(' ')
        for pid in pids:
            kill_process(pid)
        return pids

    except subprocess.CalledProcessError:
        return []

def kill_chrome_instances():
    while True:
        time.sleep(5)
        for pid in chrome_running_instances():
            kill_process(pid)
        else:
            break

kill_chrome_instances()
start_browser()
