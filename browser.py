import subprocess
import time
import os
import signal

'''for starting chrome with a custom user agent
chrome processes should not be running already'''

botagent = 'jsSeoBot'

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

# Google Chrome
def start_chrome(url):
    '''run a browser in a subprocess'''
    return subprocess.Popen(['google-chrome', '--user-agent=' + botagent, url])

def chrome_running_instances():
    return running_instances("chrome")

def kill_chrome_instances():
    kill_instances(chrome_running_instances())

# Chromium
def start_chromium(url):
    return subprocess.Popen(['chromium-browser', '--user-agent=' + botagent, url])

def chromium_running_instances():
    return running_instances("chromium-browser")

def kill_chromium_instances():
    kill_instances(chromium_running_instances())

kill_chromium_instances()
start_chromium('http://localhost')
