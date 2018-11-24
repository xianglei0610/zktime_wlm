#!/usr/bin/python

from django.core.management import execute_manager
try:
    import sys, os
    reload(sys)
    sys.path.append(os.getcwd())
    from mysite import settings # Assumed to be in the same directory.
except ImportError, e:
    print e
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv)<2: sys.argv.append("runserver")
    try:
        execute_manager(settings)
    except Exception, e:
        import traceback;traceback.print_exc();
        sys.exit(2)
