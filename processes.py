import os
import time
import subprocess

def kill_process(pid):
    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError as ex:
        print str(ex)
        os.kill(int(pid), signal.SIGKILL)

def running_instances(name):
    '''returns a list of pids of running chrome processes'''
    try:
        output = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
        processes = ouput.split('\n')
        processes.pop() # remove empty last line
        processes = [x.split() for x in processes]
        # first value is the pid, last is the process name
        pids = [x[1] for x in processes if name in x[-1]]
        return pids

    except subprocess.CalledProcessError:
        return []
