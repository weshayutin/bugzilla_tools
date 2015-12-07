#!/usr/bin/python3

import ast
import bugzilla
from datetime import datetime
from email.mime.text import MIMEText
import os
import pytz
from dateutil.relativedelta import *
import smtplib

import pdb

bz = bugzilla.Bugzilla(url='https://bugzilla.redhat.com/xmlrpc.cgi')
bz.login(os.environ['BZ_USER'], os.environ['BZ_PASSWORD'])
full_team = ast.literal_eval(os.environ['TEAM'])
team_to_email = ast.literal_eval(os.environ['TEAM_TO_EMAIL'])
ospd_triage = str(os.environ['RED_HAT_OPENSTACK'])
rdo_all = str(os.environ['RDO_ALL'])
email_server = smtplib.SMTP('smtp.corp.redhat.com', 25)
now = datetime.now(pytz.utc)
three_weeks_ago = now+relativedelta(weeks=-3)

def email_send(email_from, email_to, subject, body):
    email = MIMEText(str(body))
    email['From'] = email_from
    email['To'] = email_to
    email['Subject'] = subject
    email_server.send_message(email)

def this_query(query, name):
    this_query = query.replace('whayutin', name)
    return this_query

def full_team_report(query_url, team):
    msg = ""
    for fullname, shortname in team.items():
       msg += report(query_url, fullname, shortname )
    return msg

def full_team_sprint_report(query_url, team):
    msg = ""
    for fullname, shortname in team.items():
       msg += sprint_report(query_url, fullname, shortname )
    return msg

def report(query_url, fullname, shortname):
    msg = ""
    query = this_query(query_url, shortname)
    bug_list = bz.query(bz.url_to_query(query))
    msg += "\n\n{0} total bugs {1}\n".format(fullname, len(bug_list))
    if bug_list: msg += "You have reported the following open bugs:\n"
    for bug in bug_list:
        if bug.status != 'CLOSED':
            msg += "{0:>10}: {2},  {1}\n".format(bug.status, bug.summary,  bug.weburl )
    return msg

def sprint_report(query_url, fullname, shortname):
    msg = ""
    query = this_query(query_url, shortname)
    bug_list = bz.query(bz.url_to_query(query))
    msg += "\n\n{0} total bugs {1}\n".format(fullname, len(bug_list))
    if bug_list:
      msg += "You have reported the following bugs in the last three weeks:\n"
      msg += "This information will be used as part of a roll up status report to management\n"
    for bug in bug_list:
        if bug.creation_time > three_weeks_ago:
            msg += "{0}, {1:>10}: {3},  {2}\n".format(bug.creator, bug.status, bug.summary,  bug.weburl )
    return msg

#MAIN
#FULL REPORT
msg = ""
query_dict = {'osp-d':ospd_triage, 'rdo':rdo_all}
for name, query in query_dict.items():
  msg +="********** {0} ***********".format(name)
  msg += full_team_report(query, full_team)
  msg += '\n'
  msg += "*******************************\n\n"

email_send(os.environ['REPORT_OWNER'], os.environ['REPORT_OWNER'], 'rdo-ci bz report', msg)

#FULL TEAM SPRINT REPORT
msg = ""
query_dict = {'osp-d':ospd_triage, 'rdo':rdo_all}
for name, query in query_dict.items():
  msg +="********** {0} ***********".format(name)
  msg += full_team_sprint_report(query, full_team)
  msg += '\n'
  msg += "*******************************\n\n"

email_send(os.environ['REPORT_OWNER'], os.environ['REPORT_OWNER'], 'rdo-ci bz sprint report', msg)

# #INDIVIDUAL REPORT
msg = ""
for item in team_to_email.items():
  for name, query in query_dict.items():
    msg +="********** {0} ***********".format(name)
    msg += sprint_report(query, item[0], item[1])
    msg += '\n'
    msg += "*******************************\n\n"
  email_send(os.environ['REPORT_LIST'], item[1]+'@redhat.com', 'rdo-ci bugz', msg)
  msg = ""
