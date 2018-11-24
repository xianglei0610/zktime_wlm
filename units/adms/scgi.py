from django.core.servers.fastcgi import runfastcgi
from django.core.management import setup_environ

try:
    import sys, os
    sys.path.append(os.getcwd())
    from mysite import settings # Assumed to be in the same directory.
except ImportError, e:
    import sys
    print e
    sys.exit(1)

setup_environ(settings)


runfastcgi(method="threaded", daemonize="true", maxrequests=5,
   protocol="scgi", host="127.0.0.1", port=3033)
