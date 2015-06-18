import subprocess
import time
import os
import signal

'''for starting chrome with a custom user agent
chrome processes should not be running already'''

def kill_process(pid):
    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError as ex:
        os.kill(int(pid), signal.SIGKILL)

def start_chrome(url):
    '''run a browser in a subprocess'''
    return subprocess.Popen(['google-chrome', '--user-agent=jsSeoBot', url])

def test():
    chrome = start_chrome()
    time.sleep(20)
    kill_process(chrome.pid)

def chrome_running_instances():
    '''returns a list of pids of running chrome processes'''
    try:
        pids = subprocess.check_output(["pidof", "chrome"])
        pids = pids.split(' ')
        return pids

    except subprocess.CalledProcessError:
        return []

def kill_chrome_instances():
    '''checks for running google-chrome instances every 5 seconds.
    kills all of them in turn. returns after all instances have
    closed'''
    while True:
        time.sleep(5)
        for pid in chrome_running_instances():
            kill_process(pid)
        else:
            break

kill_chrome_instances()
start_chrome('http://localhost')
