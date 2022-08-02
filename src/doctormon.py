#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from os.path import dirname, abspath, join, exists
import json
import requests
from mylogging import log, err, info


# ======================================
# Constants

MY_DEBUG = False
DEBUG_MON_URL = 'http://localhost:3000/db.json'

MON_INTERVAL = 1 * 60  # in sec

# Email settings
EMAIL_USER = "zangular@yandex.ru"
EMAIL_PWD = "Lamaster5"
EMAIL_TO = "alexey.a.zakharov@gmail.com"
#EMAIL_TO = "pups1912@yandex.ru"

CFG_PATH = join(dirname(abspath(__file__)), "config.json")
DATA_DIR = dirname(abspath(__file__))

#======================================

prevData = None

def monitor():
  global prevData
  cfgFile = open(CFG_PATH, "r")
  config = json.loads(cfgFile.read())
  cfgFile.close()

  for doctorInfo in config["doctors"]:
    # Request data
    doctor = doctorInfo["name"]
    monUrl = doctorInfo["url"] if not MY_DEBUG else DEBUG_MON_URL
    req = requests.get(monUrl, verify=False)  # don't verify SSL cert
    if req.status_code != 200:
      err("could not get data for '{}', status code {}".format(doctor, req.status_code))
      return
    rawData = req.json()
    #log(json.dumps(rawData, sort_keys=True, indent=2, separators=(',', ': ')))

    # Getting free intervals
    date2freeIntervals = extractData(rawData)
    # log(date2freeIntervals)

    areThereAnyFreeIntervals = (date2freeIntervals is not None) and len(date2freeIntervals.keys()) > 0

    # Compare the cur and prev data
    if prevData is None or date2freeIntervals != prevData:
      if areThereAnyFreeIntervals:
        info('Doctor "{}", free intervals:'.format(doctor))
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
    prevData = date2freeIntervals


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


def jsonPrettyPrintStr(data):
  return json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))


def send_email(user, pwd, recipient, subject, body):
  import smtplib

  FROM = user
  TO = recipient if type(recipient) is list else [recipient]
  SUBJECT = subject
  TEXT = body

  # Prepare actual message
  message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
  try:
    server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
    server.ehlo()
    # server.starttls()
    server.login(user, pwd)
    server.sendmail(FROM, TO, message.encode('UTF-8'))
    server.close()
    print('successfully sent the mail')
  except Exception as ex:
    print("failed to send mail")
    print(ex)


if __name__ == '__main__':
  while True:
    monitor()
    time.sleep(MON_INTERVAL)
