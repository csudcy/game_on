#!c:/Python27/python.exe -u
#/usr/bin/env python2.6
import pdb
import sys, os

# Add a custom Python path.
paths = [
#    "/home/wikimomo/github/team_not_found/team_not_found",
    "C:/dev/team_not_found/team_not_found",
]
paths.extend(sys.path)
sys.path = paths

#from django.core.servers.fastcgi import runfastcgi
#runfastcgi(method="threaded", daemonize="false")
import TNF
#TNF.run_fcgi_http()
#TNF.run_fcgi_sock()
TNF.run_server()
