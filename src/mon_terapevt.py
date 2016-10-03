#! python2
# -*- coding: utf-8 -*-

import time
import requests
from mylogging import log, err

#======================================
# Constants

MY_DEBUG = True

MON_INTERVAL = 5 * 60 # in sec
if MY_DEBUG:
    MON_URL = 'http://localhost:3000/db.json'
else:
    MON_URL = 'https://sarov.r-mis.ru/pp/group/department_295/service/61/resource/161/planning/2016/10?_salt=1475064375273'

#======================================

def extractData(rawData):
    date2freeIntervals = {}
    for dateData in rawData["planning"]:
        if dateData['freeIntervalCount']:
            freeIntervals = []
            for interval in dateData['intervals']:
                if interval['free']:
                    freeIntervals.append(interval['formattedDate'])
            date2freeIntervals[dateData['date']] = freeIntervals
    return date2freeIntervals


def examine():
    # Request data
    req = requests.get(MON_URL, verify=False) # don't verify SSL cert
    if req.status_code != 200:
        err("could not get data from '{}', status code {}".format(MON_URL, req.status_code))
        return
    rawData = req.json()
    #log(json.dumps(rawData, sort_keys=True, indent=2, separators=(',', ': ')))
    # Getting free intervals
    date2freeIntervals = extractData(rawData)
    log(date2freeIntervals)


if __name__ == '__main__':
    if MY_DEBUG:
        examine()
    else:
        while True:
            examine()
            time.sleep(MON_INTERVAL)
