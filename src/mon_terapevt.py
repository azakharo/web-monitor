#! python2
# -*- coding: utf-8 -*-

import time
from os.path import dirname, abspath, join, exists
import json
import requests
from mylogging import log, err, info

#======================================
# Constants

MY_DEBUG = False

MON_INTERVAL = 15 * 60 # in sec
if MY_DEBUG:
    MON_URL = 'http://localhost:3000/db.json'
else:
    MON_URL = 'https://sarov.r-mis.ru/pp/group/department_298/service/27/resource/183/planning/2016/10?_salt=1475503090305'
PREV_DATA_FNAME = join(dirname(abspath(__file__)), "prev_data.json")

# Email settings
EMAIL_USER = "alexey.a.zakharov@gmail.com"
EMAIL_PWD = "MyGmail6"
EMAIL_TO = "zangular@yandex.ru"
EMAIL_SUBJ = "запись к детскому кардиологу"

#======================================

def extractData(rawData):
    date2freeIntervals = {}
    for dateData in rawData["planning"]:
        if dateData['freeIntervalCount']:
            freeIntervals = []
            for interval in dateData['intervals']:
                if interval['free']:
                    freeIntervals.append(interval['formattedDate'])
            date2freeIntervals[unicode(dateData['date'])] = freeIntervals
    return date2freeIntervals

def loadPrevData():
    if not exists(PREV_DATA_FNAME):
        open(PREV_DATA_FNAME, 'w').close()
        prevData = None
    else:
        f = open(PREV_DATA_FNAME, "r")
        prevData = json.loads(f.read())
        f.close()
    return prevData

def saveData(data):
    f = open(PREV_DATA_FNAME, "w")
    f.write(jsonPrettyPrintStr(data))
    f.close()

def jsonPrettyPrintStr(data):
    return json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))

def examine():
    # Request data
    req = requests.get(MON_URL, verify=False) # don't verify SSL cert
    if req.status_code != 200:
        err("could not get data from '{}', status code {}".format(MON_URL, req.status_code))
        return
    rawData = req.json()
    #log(json.dumps(rawData, sort_keys=True, indent=2, separators=(',', ': ')))

    prevData = loadPrevData()

    # Getting free intervals
    date2freeIntervals = extractData(rawData)
    # log(date2freeIntervals)

    # Compare the cur and prev data
    if date2freeIntervals != prevData:
        info('free intervals have been changed:')
        info(jsonPrettyPrintStr(date2freeIntervals))
        # Send email with cur state
        msgBody = "Свободное время приёма:\n"
        for date in date2freeIntervals.keys():
            msgBody += "{} число: {}\n".format(date, ', '.join(date2freeIntervals[date]))
        send_email(EMAIL_USER, EMAIL_PWD, EMAIL_TO, EMAIL_SUBJ, msgBody)

    # Save data
    saveData(date2freeIntervals)


def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

if __name__ == '__main__':
    while True:
        examine()
        time.sleep(MON_INTERVAL)
