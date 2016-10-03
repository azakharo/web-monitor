#! python2
# -*- coding: utf-8 -*-

import time
from mylogging import log

#======================================
# Constants

MON_INTERVAL = 5 * 60 # in sec

#======================================

def examine():
    log('examine')

if __name__ == '__main__':
    while True:
        examine()
        time.sleep(MON_INTERVAL)
