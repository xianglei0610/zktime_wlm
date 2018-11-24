#!/usr/bin/python

from django.core.management import execute_manager
try:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(os.path.split(os.getcwd())[0])
    from mysite import settings # Assumed to be in the same directory.
except ImportError, e:
    print e
    sys.exit(1)

if __name__ == "__main__":
        if len(sys.argv)<2: sys.argv.append("runserver")
        try:
                execute_manager(settings)
        except Exception, e:
                print e
                sys.exit(2)
