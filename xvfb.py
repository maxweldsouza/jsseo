import os
import subprocess
import processes

# Xvfb
class Xvfb():
    def start():
        '''start xvfb. this will be called only if the system has
        no display servers'''
        assert('DISPLAY' not in os.environ)
        try:
            displayno = ':0'
            self.process = subprocess.Popen(['Xvfb', displayno, '-screen', '0', '1024x768x16'])
            time.sleep(0.2)
            return_code = self.process.poll()

            if return_code is not None:
                print 'Xvfb did not start'
            else:
                self.display = displayno

        except OSError, e:
            print 'Check whether Xvfb is installed'
        except subprocess.CalledProcessError, e:
            print str(e)

    def stop():
        if self.process is not None:
            self.process.kill()
            self.process.wait()
            self.process = None
