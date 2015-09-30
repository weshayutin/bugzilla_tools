#!/usr/bin/python3

import ast
import bugzilla
import os

import pdb

bz = bugzilla.Bugzilla(url='https://bugzilla.redhat.com/xmlrpc.cgi')
bz.login(os.environ['BZ_USER'], os.environ['BZ_PASSWORD'])
team = ast.literal_eval(os.environ['TEAM'])
ospd_triage = str(os.environ['OSPD_TRIAGE'])
rdo_all = str(os.environ['RDO_ALL'])

def this_query(query, name):
    this_query = query.replace('whayutin', name)
    return this_query

def report(query_url):
  for fullname, shortname in team.items():
    query = this_query(query_url, shortname)
    value = bz.query(bz.url_to_query(query))
    print("{0} total bugs {1}".format(fullname, len(value)))


#MAIN
print("OSPD BUGS:")
report(ospd_triage)
print("\n\n")

print("RDO BUGS:")
report(rdo_all)



