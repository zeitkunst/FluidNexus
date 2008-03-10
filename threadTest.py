# Standard library imports
import sys
import time
import os
import md5
import thread
import time

# @HACK@
# Adding paths to find the modules
sys.path.append('.')
sys.path.append(os.getcwd())
sys.path.append('E:\\System\\Apps\\Python\\my\\')
sys.path.append('C:\\Python')
sys.path.append('E:\\Python')

sys.path.append('C:\\System\\Apps\\Python\\my\\')
from logger import Logger

# Series 60 specific imports
try:
    # On phone?
    import e32
    import e32db
    
    # @SEMI-HACK@
    # At the moment, set global variable that determines where our data is going to live
    availableDrives = e32.drive_list()
    #if 'E:' in availableDrives:
    #    dataPath = u'E:\\System\\Data\\FluidNexusData'
    #else:
    #    dataPath = u'C:\\System\\Data\\FluidNexusData'
 
    try:
        os.listdir("E:")
        dataPath = u'E:\\System\\Data\\FluidNexusData'
    except OSError:
        # there is no memory card
        dataPath = u'C:\\System\\Data\\FluidNexusData'

    # Setup our data path
    if not os.path.isdir(dataPath):
        os.makedirs(dataPath)

    # Setup logging and redirect standard input and output
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'database: ')
    #sys.stderr = sys.stdout = log

    onPhone = True
except ImportError:
    from s60Compat import e32
    dataPath = '.'
    log = Logger(dataPath + u'\\FluidNexus.log', prefix = 'database: ')
    sys.stderr = sys.stdout = log

    onPhone = False

class Thread1Test(object):
    def __init__(self):
        pass

    def run(self):
        while 1:
            e32.ao_sleep(5)
            print 'foo'

class Thread2Test(object):
    def __init__(self):
        pass

    def run(self):
        while 1:
            e32.ao_sleep(10)
            print 'bar'


if __name__ == "__main__":
    thread1 = Thread1Test()
    thread2 = Thread2Test()
    thread.start_new_thread(thread1.run, ())
    thread.start_new_thread(thread2.run, ())
    time.sleep(200)
