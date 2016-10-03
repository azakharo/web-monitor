#! python2

import time

#======================================
# Constants

MON_INTERVAL = 5 * 60 # in sec

#======================================

def examine():
    print 'examine'

if __name__ == '__main__':
    while True:
        examine()
        time.sleep(MON_INTERVAL)
