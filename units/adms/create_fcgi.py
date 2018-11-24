# -*- coding: utf-8 -*-
import wsgiserver
import os
import sys
import django.core.handlers.wsgi
import dict4ini
from mysite import settings

adms_pid_file = settings.APP_HOME+'/tmp/fcgi.pid'

def killpids():
    u"杀掉fastcgi进程"
    if os.path.exists(adms_pid_file):
        try:
            file_pid = file(adms_pid_file,"r")
            str_pids = file_pid.read()
            pids = str_pids.strip().split("\n")
            for p in pids:
                os.system(u"TASKKILL /PID %s /T /F"%p)
        finally:
            file_pid.close()
        os.remove(adms_pid_file)
            
if __name__ == "__main__":
    try:
        file_pid = file(adms_pid_file,"a+")
        file_pid.write("%s\n"%os.getpid())
    finally:
        file_pid.close()
        
    ipaddress="0.0.0.0"
    port=20000
    try:
            ipaddress=sys.argv[1]
            port=int(sys.argv[2])
            sys.argv.remove(ipaddress)
            sys.argv.remove("%s"%port)
    except: pass
    print "get address ",ipaddress
    print "get port ",port
    if os.name=='posix': 
            setup_environ(settings)
            runfastcgi(method="threaded", maxrequests=500, protocol="fcgi", host="localhost", port=self.fcgiPort)
    else: #runfcgi method=threaded host=localhost port=10026
            print "start fcgi "
            from django.core.management import execute_manager
            sys.argv.append("runfcgi") 
            sys.argv.append("method=thread") 
            sys.argv.append("maxrequests=500")                
            sys.argv.append("host="+ipaddress) 
            sys.argv.append("port=%s"%port)
            sys.argv.append("daemonize=false")
            print sys.argv
            execute_manager(settings)
