# -*- coding: utf-8 -*-

def set_lib_path():
    import sys
    import os
    _cur = os.getcwd()
    _cur = _cur.replace('units%sadms'%os.sep,'')
    lib_path = os.path.join(_cur,'python-support')
    sys.path.append(lib_path)
    os.environ["PYTHONPATH"]=lib_path
set_lib_path()

import os
import sys
import dict4ini
from multiprocessing import Process,cpu_count

path = os.path.split(__file__)[0]


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


     
#用于当前进程与其他进程的管理同步(当前仅门禁使用)
#其他应用如果需要，下面的if需要修改，否则调用q_server时可能出错。
def run_acc_dictmanager(q_server):
    from redis_self.filequeue import SyncDict
    from mysite.utils import printf
    try:
        printf("-svr8000--pid=%s"%os.getpid(), True)
        
        pid = q_server.get_from_file("DICT_SERVER_PID")
        if pid:
            process_info = os.popen('tasklist |findstr "%s"' % pid).read()
            if "python.exe" in process_info.lower():
                os.system("taskkill /PID %s /F /T" % pid)#启动时收尸
        
        q_server.set_to_file("DICT_SERVER_PID", "%d"%(os.getpid()))
        q_server.connection.disconnect()
    except Exception, e:
        import traceback; traceback.print_exc()
    SyncDict(forever=True)
    
class server():
        server_type='Simple'
        def __init__(self, configFile='attsite.ini'):
                os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
                p=os.getcwd()
                
                self.p=p
                self.address='0.0.0.0:80'
                self.numthreads=10
                self.queue_size=200        
                self.port=80
                self.fcgiPort=10026
                self.WebPort=20001
                self.portcount=cpu_count()
                self.webportcount=cpu_count()
                
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
                if port:
                    self.port=int(port)
                if run_type:
                    if run_type=="1":
                        self.server_type = "Nginx"
                    if run_type=="2":
                        self.server_type = "Bjoern"
                    else:
                        self.server_type = "WSGI"

                print "Start Automatic Data Master Server ... ...\nOpen your web browser and go http://127.0.0.1:%s/"%self.port
                from mysite.utils import printf
                printf("start now", True)
                try:
                    from redis_self.filequeue import FileQueue
                    q_server = FileQueue()
                    main_pid = q_server.get_from_file("WEB_SERVER_PID")
                    if main_pid:
                        main_process_info = os.popen('tasklist |findstr "%s"' % main_pid).read()
                        if "python.exe" in main_process_info.lower():
                            os.system("taskkill /PID %s /F /T" % main_pid)#启动时收尸
                    
                    q_server.set_to_file("WEB_SERVER_PID", "%d"%(os.getpid()))
                    from mysite import settings 
                    if "mysite.iaccess" in settings.INSTALLED_APPS:
                        p = Process(target=run_acc_dictmanager, args=(q_server,))
                        p.start()
                    #启动时检测数据库版本和当前软件版本是否一致，不一致则同步数据库
                    SyncDB().start()
                except Exception, e:
                    printf('------e=%s'%e, True)
                printf("init finished", True)
                
        def runWSGIServer(self):
                import wsgiserver
                import django.core.handlers.wsgi       
                address=tuple(self.address.split(":"))
                wserver = wsgiserver.CherryPyWSGIServer(
                        (address[0], self.port),
                        django.core.handlers.wsgi.WSGIHandler(),
                        server_name='www.bio-Device.com',
                        numthreads = self.numthreads,
                        request_queue_size=self.queue_size,
                )
                try:
                        wserver.start()
                except KeyboardInterrupt:
                        wserver.stop()
                        
        def runBjoernServer(self):
                import bjoern
                import django.core.handlers.wsgi
                bjoern.listens(django.core.handlers.wsgi.WSGIHandler(), '0.0.0.0', 8123)
                try:
                    bjoern.run()
                except KeyboardInterrupt:
                    print 'sdfd'

        def runSimpleServer(self):
                from django.core.management import execute_manager
                from mysite import settings
                settings.DEBUG = True
                settings.TEMPLATE_DEBUG = True
                execute_manager(settings, [self.p+'/mysite/manage.py', 'runserver', '%s:%s'%(self.address.split(":")[0],self.port)])
        

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
                if self.server_type=='Bjoern': return self.runBjoernServer()
                if self.server_type=='Nginx': return self.runNginxServer()
                self.runSimpleServer()

import threading
class SyncDB(threading.Thread):
    '''
    用于同步数据库的线程
    '''
    def __init__(self):
        super(SyncDB, self).__init__()
    def run(self):
        try:
            if os.path.exists("upgrade.py"):
                os.system("python upgrade.py")
            else:
                os.system("python upgrade.pyc")
        except:
            pass
        
def sub_action(cmd,is_script=False):
    '''
    用于运行子命令、子进程
    '''
    import subprocess
    if os.path.exists("manage.py"):
        manage = "manage.py"
    else:
        manage = "manage.pyc"
    if  is_script:
        p = subprocess.Popen('python  %s'%cmd,shell=False)
    else:
        p = subprocess.Popen('python %s %s'%(manage,cmd),shell=False)
        
def run_all_service():
    '''
    用于运行所有服务
    '''
    import subprocess
    import datetime
    f = open('run_all_service.log','a')
    f.write('running at %s\n'%datetime.datetime.now())
    if os.path.exists("manage.py"):
        manage = "manage.py"
    else:
        manage = "manage.pyc"
    
    #f1 = open('run_all_service.log','a')
    #p1 = subprocess.Popen('python svr8000.py',shell=True,stdout=f1)
    log= 'running webserver ............. pid: %s\n'%os.getpid()
    print log
    f.write(log)
    
    f2 = open('autocalculate_pid.log','a')
    p2 = subprocess.Popen('python %s autocalculate'%manage,shell=False,stdout=f2)
    log = 'running autocalculate ......... pid: %s\n'%p2.pid
    print log
    f.write(log)
    
    f3 = open('writedata_pid.log','a')
    p3 = subprocess.Popen('python %s writedata'%manage,shell=False,stdout=f3)
    log = 'running writedata ............. pid: %s\n'%p3.pid
    print log
    f.write(log)
    
    f4 = open('zksaas_adms_pid.log','a')
    p4 = subprocess.Popen('python %s zksaas_adms'%manage,shell=False,stdout=f4)
    log = 'running zksaas_adms ........... pid: %s\n'%p4.pid
    print log
    f.write(log)
    
    print 'everything is ok!\n'


'''默认运行参数值'''
option_file = None        
port = None
run_type = None
run_all_b = None
run_cmd = None
run_script = None

def configOption():
    '''
    运行参数解析
    '''  
    from optparse import OptionParser  
    usage = "usage: %prog [-option]"  
    parser = OptionParser(usage)  
    parser.add_option("-f", "--file", dest = "option_file",
                      help = "use this file to set option for the web server")  
    parser.add_option("-p", "--port", dest = "port",
                      help = "use this option to set port for the web server")  
    parser.add_option("-t", "--type", dest="run_type",  
                      help = "use this option to set the server running type (0:WSGI 1: Ngnix)")  
    parser.add_option("-a", "--all", dest="run_all_b",  
                      help = "use this option to run all service of zkeco (not null)")  
    parser.add_option("-c", "--cmd", dest="run_cmd",  
                      help = "run django cmd")  
    parser.add_option("-s", "--script", dest="run_script",  
                      help = "run custom script")  

    (options, args) = parser.parse_args()  
    if options.option_file:  
        global option_file  
        option_file = options.option_file  
    if options.port:  
        global port  
        port = options.port  
    if  options.run_type:  
        global run_type  
        run_type= options.run_type
    if  options.run_all_b:  
        global run_all_b  
        run_all_b= options.run_all_b 
    if  options.run_cmd:  
        global run_cmd  
        run_cmd= options.run_cmd 
    if  options.run_script:  
        global run_script  
        run_script= options.run_script 

if __name__ == "__main__":
        '''
        运行入口
        '''
        configOption()
        
        if run_cmd:
            sub_action(run_cmd)
        elif run_script:
            sub_action(run_script,True)
        else:
            if run_all_b:
                run_all_service()
                
            config="attsite.ini"
            if option_file:
                config = option_file
            server(config).run()
        




