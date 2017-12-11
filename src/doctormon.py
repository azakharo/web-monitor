#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from os.path import dirname, abspath, join, exists
import json
import requests
from mylogging import log, err, info

# ======================================
# Constants

MY_DEBUG = True

MON_INTERVAL = 1 * 60  # in sec

# Email settings
EMAIL_USER = "alexey.a.zakharov@gmail.com"
EMAIL_PWD = "MyGmail6"
EMAIL_TO = "zangular@yandex.ru"
#EMAIL_TO = "pups1912@yandex.ru"

CFG_PATH = join(dirname(abspath(__file__)), "config.json")
DATA_DIR = dirname(abspath(__file__))

#======================================


################################################
# Variable stuff

DOCTOR_NAME = 'Chuvatkin'
if MY_DEBUG:
  MON_URL = 'http://localhost:3000/db.json'
else:
  MON_URL = 'https://152.is-mis.ru/pp/group/department_305/service/36/resource/214/planning/2017/11?_salt=1511505893507'

# Variable stuff
################################################


def monitor(doctor, monUrl):
  # Request data
  req = requests.get(monUrl, verify=False)  # don't verify SSL cert
  if req.status_code != 200:
    err("could not get data for '{}', status code {}".format(doctor, req.status_code))
    return
  rawData = req.json()
  #log(json.dumps(rawData, sort_keys=True, indent=2, separators=(',', ': ')))

  prevData = loadPrevData(doctor)

  # Getting free intervals
  date2freeIntervals = extractData(rawData)
  # log(date2freeIntervals)

  # Compare the cur and prev data
  if prevData is None or date2freeIntervals != prevData:
    info('free intervals have been changed:')
    info(jsonPrettyPrintStr(date2freeIntervals))
    # Send email with cur state
    msgBody = "{}\n".format(doctor)
    if len(date2freeIntervals.keys()) > 0:
      msgBody += "Свободное время приёма:\n"
      for date in date2freeIntervals.keys():
        msgBody += "{} число: {}\n".format(date, ', '.join(date2freeIntervals[date]))
    else:
      msgBody += "Пока всё занято :("
    send_email(EMAIL_USER, EMAIL_PWD, EMAIL_TO, doctor, msgBody)

  # Save data
  saveData(doctor, date2freeIntervals)


def getDataFilePath(doctor):
  return join(DATA_DIR, doctor) + '.json'


def loadPrevData(doctor):
  fname = getDataFilePath(doctor)
  if not exists(fname):
    open(fname, 'w').close()
    prevData = None
  else:
    f = open(fname, "r")
    prevData = json.loads(f.read())
    f.close()
  return prevData


def saveData(doctor, data):
  fname = getDataFilePath(doctor)
  f = open(fname, "w")
  f.write(jsonPrettyPrintStr(data))
  f.close()


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


def jsonPrettyPrintStr(data):
  return json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))


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
    monitor(DOCTOR_NAME, MON_URL)
    time.sleep(MON_INTERVAL)
