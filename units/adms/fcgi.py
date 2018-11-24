#!/usr/bin/python

from django.core.servers.fastcgi import runfastcgi
from django.core.management import setup_environ
import sys, os
cwd=os.getcwd()
try:
    sys.path.append(cwd)
    from mysite import settings # Assumed to be in the same directory.
except ImportError, e:
    import sys
    print e
    sys.exit(1)

setup_environ(settings)

socket=cwd+"/adms.sock"
pidfile=cwd+"/adms.pid"

runfastcgi(method="threaded", maxrequests=50,
   protocol="fcgi",  socket=socket, pidfile=pidfile)

