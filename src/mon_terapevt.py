#! python2
# -*- coding: utf-8 -*-

import time
import requests
from mylogging import log, err

#======================================
# Constants

MON_INTERVAL = 5 * 60 # in sec
MON_URL = 'https://sarov.r-mis.ru/pp/group/department_295/service/61/resource/161/planning/2016/10?_salt=1475064375273'

#======================================

def examine():
    # Request data
    req = requests.get(MON_URL, verify=False) # don't verify SSL cert
    if req.status_code != 200:
        err("could not get data from '{}', status code {}".format(MON_URL, req.status_code))
        return
    rawData = req.json()


if __name__ == '__main__':
    while True:
        examine()
        time.sleep(MON_INTERVAL)
