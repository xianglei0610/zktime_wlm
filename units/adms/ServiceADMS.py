#!/usr/bin/python
# -*- coding: utf-8 -*-
from service_utils import main, PythonService
import os
import win32service
import win32event
from mysite.utils import printf
path = os.path.split(__file__)[0]


class ZKECOADMSService(PythonService):
    _svc_name_ = "ZKECOWEBService"
    _svc_display_name_ = "ZKECO Web Service"
    _svc_deps_ = ["ZKECOMemCachedService"]
    path = path
    cmd_and_args=["svr8000.pyc", ]
    def stop_fun(self, process):
        try:
            from create_fcgi import killpids
            os.system("""taskkill /IM nginx.exe /F""")
            #杀死fastcgi进程
            killpids()
        except Exception, e:
            printf('------stop_fun e=%s'%e, True)
    def SvcStop(self):
        try:
            
            from mysite import settings
            from redis_self.filequeue import FileQueue
            #printf("---path settings.APP_HOME=%s"%settings.APP_HOME, True)
            q_server = FileQueue(path="%s/_fqueue/"%settings.APP_HOME)
            #main_pid = q_server.get_from_file("WEB_SERVER_PID")
            dict_pid = q_server.get_from_file("DICT_SERVER_PID")
            #self.logger.info("dict_pid=%s"%dict_pid)
            #printf("---pid=%s"%dict_pid, True)
            #os.system("taskkill /PID %s /F /T" % main_pid)#杀自己，没权限 error5
            os.system("taskkill /PID %s /F /T" % dict_pid)#关闭服务时为门禁字典缓存进程收尸
            q_server.connection.disconnect()
    
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.logger.info("Send Stop")
        except Exception, e:
            self.logger.info("e==%s"%e)
            printf('------svcstop e=%s'%e, True)
            import traceback; traceback.print_exc(file=self.logger.handlers[0].stream)
    

if __name__=='__main__':
    main(ZKECOADMSService)
