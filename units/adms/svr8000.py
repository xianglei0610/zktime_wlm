#!/usr/bin/python
# -*- coding: utf-8 -*-
import wsgiserver
import os
import sys
import django.core.handlers.wsgi
import dict4ini
from multiprocessing import Process,cpu_count
#sync_dict = {}


####################### 读取配置文件相关项 ###############################
import dict4ini
att_file = dict4ini.DictIni("attsite.ini")
VISIBLE_POS = att_file["Options"]["APP_POS"]
VISIBLE_ATT = att_file["Options"]["APP_ATT"]
VISIBLE_IACCESS = att_file["Options"]["APP_IACCESS"]
VISIBLE_POS_IC = att_file["Options"]["POS_IC"]

EN_POS = EN_ATT = EN_IACCESS = EN_POS_IC = False
if VISIBLE_POS.lower()=="true":
    EN_POS = True
    if VISIBLE_POS_IC.lower()=="true":EN_POS_IC = True
if VISIBLE_ATT.lower()=="true":
    EN_ATT = True
if VISIBLE_IACCESS.lower()=="true":
    EN_IACCESS = True

########################### 任务列表 #######################

path = os.path.split(__file__)[0]

apacheConf="""
ServerName ADMS
Listen %(address)s

# ThreadsPerChild 100
ThreadsPerChild %(numthreads)s

# MaxRequestsPerChild  0
MaxRequestsPerChild %(request_queue_size)s

KeepAlive On
KeepAliveTimeout 2

Timeout 600

LoadModule python_module modules/mod_python.so
#LoadModule access_module modules/mod_access.so
LoadModule actions_module modules/mod_actions.so
LoadModule alias_module modules/mod_alias.so
LoadModule asis_module modules/mod_asis.so
LoadModule autoindex_module modules/mod_autoindex.so
LoadModule dir_module modules/mod_dir.so
LoadModule env_module modules/mod_env.so
LoadModule file_cache_module modules/mod_file_cache.so
LoadModule log_config_module modules/mod_log_config.so
LoadModule mime_module modules/mod_mime.so

AddType text/css        css
TypesConfig conf/mime.types

<Location "/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE mysite.settings
        PythonDebug On
        Options All
</Location>

Alias /media/ "%(path)s/mysite/media/"
<Location "/media">
        SetHandler None
</Location>
Alias /iclock/media/ "%(path)s/mysite/media/"
<Location "/media">
        SetHandler None
</Location>

Alias /iclock/file/ "%(path)s/mysite/files/"
<Location "/iclock/file">
        SetHandler None
</Location>

Alias /iclock/tmp/ "%(path)s/mysite/tmp/"
<Location "/iclock/tmp">
        SetHandler None
</Location>

# LogFormat "%%h %%l %%u %%t \\"%%r\\" %%>s %%b" common
# CustomLog %(path)s/mysite/tmp/apache_access.log common
ErrorLog %(path)s/mysite/tmp/apache_error.log
"""

nginx_load_conf="""
upstream adms_device {
%(adms_device)s
}
upstream adms_mng {
%(adms_mng)s
}
"""

nginx_site_conf="""
	listen %(PORT)s;
	server_name adms;
	location /iclock/cdata {
		#proxy_pass http://adms_device;
		#include	proxy.conf;
        fastcgi_pass adms_device;
        include        fastcgi.conf;
        		
	}
	location /iclock/getrequest {
		#proxy_pass http://adms_device;
		#include	proxy.conf;		
        fastcgi_pass adms_device;
        include        fastcgi.conf;
        
	}
	location /iclock/devicecmd {
		#proxy_pass http://adms_device;
		#include	proxy.conf;		
        fastcgi_pass adms_device;
        include        fastcgi.conf;
        
	}
    location /iclock/fdata {
#    	proxy_pass http://adms_device;
#    	include	proxy.conf;		
        fastcgi_pass adms_device;
        include        fastcgi.conf;

    }
    
	location /{
        fastcgi_pass adms_mng;
        include        fastcgi.conf;

	}

"""


def writeRegForPython(path):
        import win32api
        import win32con
        key=win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SOFTWARE", 0, win32con.KEY_ALL_ACCESS)
        key2=win32api.RegCreateKey(key, "Python\\PythonCore\\2.5\\PythonPath")
        win32api.RegSetValueEx(key2,'',0,win32con.REG_SZ, path)
     

    
class server():
        server_type='Simple'
        def __init__(self, configFile='attsite.ini'):
                #global sync_dict 
                os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
                p=os.getcwd()
                self.p=p
#                os.environ['PATH']="%(p)s\\Apache2\\bin;%(p)s\\Python25;%(p)s\\mssql"%{"p":p}+os.environ['PATH']
#                newpath="%INSTALL_PATH%\\mssql;%INSTALL_PATH%\\mssql\\win32;%INSTALL_PATH%\\mssql\\win32\\lib;%INSTALL_PATH%\\Python25;%INSTALL_PATH%\\Python25\\Lib\\site-packages;%INSTALL_PATH%".replace('%INSTALL_PATH%',p).split(";")
#                for p in newpath:
#                        if p not in sys.path:
#                            sys.path.append(p)
#                print "sys.path:", sys.path
                self.address='0.0.0.0:80'
                self.numthreads=10
                self.queue_size=200        
                self.port=80
                self.fcgiPort=10026
                self.WebPort=20001
                self.portcount=1#cpu_count()
                self.webportcount=1#cpu_count()
                if os.path.exists(p+"/"+configFile+".dev"):
                    configFile+=".dev"
                if os.path.exists(p+"/"+configFile):
                        cfg=dict4ini.DictIni(p+"/"+configFile, values={'Options':
                        {'Port':80, 
                         'IPAddress':'0.0.0.0', 
                         'Type': self.server_type,
                         'NumThreads': 10,
                         'QueueSize': 200,
                         'FcgiPort': 10026,
                        }})
                        self.port=cfg.Options.Port
                        self.address="%s:%s"%(cfg.Options.IPAddress, cfg.Options.Port)
                        self.server_type=cfg.Options.Type
                        self.numthreads=cfg.Options.NumThreads
                        self.queue_size=cfg.Options.QueueSize
                        self.fcgiPort=cfg.Options.FcgiPort

#                print "address=%s,number of threads=%s,queue size=%s"%(self.address,self.numthreads,self.queue_size)
                print "Start Automatic Data Master Server ... ...\nOpen your web browser and go http://%s"%(self.address.replace("0.0.0.0","127.0.0.1"))+"/"
                if EN_POS:
                    from mysite.pos.pos_ic.ic_sync_action import init_pos_batch
                    init_pos_batch()
                
                from mysite.utils import printf
#                from mysite.iaccess.linux_or_win import run_commend
#                printf("start now", True)
#                try:
##                    from redis_self.filequeue import FileQueue
##                    q_server = FileQueue()
##                    main_pid = q_server.get_from_file("WEB_SERVER_PID")
##                    #print '--pid2=',pid
##                    if main_pid:
##                        main_process_info = os.popen(run_commend(1) % main_pid).read()
##                        if run_commend(3) in main_process_info.lower():
##                            os.system(run_commend(2) % main_pid)#启动时收尸
##                    
##                    q_server.set_to_file("WEB_SERVER_PID", "%d"%(os.getpid()))
##                    from mysite import settings 
##                    if "mysite.iaccess" in settings.INSTALLED_APPS:
##                        p = Process(target=run_acc_dictmanager, args=(q_server,))
##                        p.start()
#                    #启动时检测数据库版本和当前软件版本是否一致，不一致则同步数据库
#                    SyncDB().start()
#                except Exception, e:
#                    printf('------e=%s'%e, True)
                printf("init finished", True)
                
        def runWSGIServer(self):        
#                print "runWSGIServer"
                address=tuple(self.address.split(":"))
                wserver = wsgiserver.CherryPyWSGIServer(
                        (address[0], int(address[1])),
                        django.core.handlers.wsgi.WSGIHandler(),
                        server_name='www.bio-Device.com',
                        numthreads = self.numthreads,
                        request_queue_size=self.queue_size,
                )
                try:
                        wserver.start()
                except KeyboardInterrupt:
                        wserver.stop()

        def runSimpleServer(self):
#                print "runSimpleServer"
                from django.core.management import execute_manager
                from mysite import settings 
                execute_manager(settings, [self.p+'/mysite/manage.py', 'runserver', self.address])
        
        def runApacheServer(self):
#                print "runApacheServer"
                writeRegForPython(";".join(sys.path))
                from dbapp.utils import tmpFile
                fn=tmpFile('apache.conf', 
                        apacheConf%{
                                "address":self.address, 
                                "path": self.p.replace("\\","/"),
                                "numthreads":self.numthreads,
                                "request_queue_size":self.queue_size,
                        }, False)
                os.system("%s\\Apache2\\bin\\apache.exe -f \"%s\""%(self.p,fn))

        def runNginxServer(self):
                from django.core.servers.fastcgi import runfastcgi
                from django.core.management import setup_environ
                from mysite import settings
                from create_fcgi import killpids
                os.chdir("%s/../../python-support/nginx"%self.p)
                bl=[]
                for p in range(int(self.portcount)):
                    bl.append("     server 127.0.0.1:"+str(int(self.fcgiPort)+p)+";")
                webbl=[]
                for p in range(int(self.webportcount)):
                    webbl.append("      server 127.0.0.1:"+str(int(self.WebPort)+p)+";")
                
                fname="conf/load_balance.conf"    
                f=file(fname, "w+")
                confStr=nginx_load_conf%{"adms_device":"\n".join(bl),"adms_mng":"\n".join(webbl)}
                f.write(confStr)
                f.close()

                fname="conf/site.conf"
                
                
                f=file(fname, "w+")
                confStr=nginx_site_conf%{"PORT":self.port}
                f.write(confStr)
                f.close()
                
                #杀死fastcgi 进程
                killpids()

                os.chdir(self.p)
                address=("0.0.0.0",self.fcgiPort)
                for p in range(int(self.portcount)):  
                    print "start fcgi services "+str(p)
                    try:
                        os.system("""start "ZKECO ADMS PORT %s " python create_fcgi.pyc 0.0.0.0 %s"""%(str(int(self.fcgiPort)+p),str(int(self.fcgiPort)+p)))
                        os.system("""start "ZKECO WEB PORT %s " python create_fcgi.pyc 0.0.0.0 %s"""%(str(int(self.WebPort)+p),str(int(self.WebPort)+p)))
                        #os.system("""start "ZKECO ADMS PORT %s " python manage.pyc runserver  0.0.0.0:%s"""%(str(int(self.fcgiPort)+p),str(int(self.fcgiPort)+p)))
                    except:
                        import traceback ;traceback.print_exc()
                os.chdir("%s/../../python-support/nginx"%self.p)
                if os.name=='posix': 
                        os.system("""./nginx -s stop""")
                        os.system("""./nginx""")
                else: #'nt', windows
                        os.system("""taskkill /f /im nginx.exe""")
                        os.system("""nginx.exe""")
                        
				
        def run(self):
                if self.server_type=='Apache': return self.runApacheServer()
                if self.server_type=='WSGI': return self.runWSGIServer()
                if self.server_type=='Nginx': return self.runNginxServer()
                self.runSimpleServer()

import threading
#同步数据库信息时启动另一个线程，防止数据库同步时间过长导致服务器无法访问
class SyncDB(threading.Thread):
    def __init__(self):
        super(SyncDB, self).__init__()
    def run(self):
        try:
            os.system("python upgrade.pyc")
        except:
            pass

if __name__ == "__main__":
        config="attsite.ini"
        #os.system("taskkill /PID 2080 /F /T")
        try:
                config=sys.argv[1]
        except: pass
        server(config).run()
        




