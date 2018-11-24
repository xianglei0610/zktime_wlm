#!/usr/bin/python
# -*- coding: utf-8 -*-
from service_utils import main, DjangoService
import win32serviceutil
import win32service
import win32event
import os
import sys
import time, datetime
import glob
from redis_self.filequeue import FileQueue, DictQueue
from mysite.utils import printf

CENTER_PROCE_LIST = "CENTER_PROCE_LIST"

path=os.path.split(__file__)[0]

def killall_pid(d_server, q_server, processes):
    try:
        fqpath = "%s/_fqueue/"%(os.getcwd())
        main_pid = q_server.get_from_file("CENTER_MAIN_PID")
        printf("main_pid============%s"%main_pid, True)
        os.system("taskkill /PID %s /F /T" % main_pid)
        
        if processes:
            for process in processes:#强制杀子进程
                chilren_pid = q_server.get_from_file("PROCESS_%s_PID"%process)
                printf("chilren_pid============%s"%chilren_pid, True)
                os.system("taskkill /PID %s /F /T" % chilren_pid)
        d_server.delete_dict("CENTER_RUNING")
    except Exception, e:
        printf("killall_pid  e=======%s"%e, True)

def check_center_stop(d_server, processes):
    #Settings cannot be imported, because environment variable DJANGO_SETTINGS_MODULE is undefined.
    try:
        for process in processes:
            process_status = d_server.get_from_dict("%s_SERVER" % process)#如Net0_SERVER #要么为stop要么为空
            #printf("--process_status=%s"%process_status, True)
            if process_status:#多个进程，只要有一个还没被停掉，就返回True
                printf("check_center_stop--True--", True)  
                return True
        printf("check_center_stop---False-", True)  
        return False#全部停掉了，返回False
    except Exception, e:
        printf("--check_center_stop-e=%s"%e, True)
        
class ServiceDataCommCenter(DjangoService):
    _svc_name_ = "ZKECODataCommCenterService"
    _svc_display_name_ = "ZKECO Data Comm Center Service"
    _svc_deps_ = ["ZKECOWEBService"]
    path = path
    cmd_and_args=["datacommcenter"]
   
    def SvcStop(self):
        printf("*******ServiceDataCommCenter stop", True)
        os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

        fqpath = "%s/_fqueue/"%(os.getcwd())
        q_server = FileQueue(path=fqpath)
        d_server = DictQueue()
        
        try:
            processes = d_server.get_from_dict(CENTER_PROCE_LIST)#如果python异常终止，该值返回None 
            printf("******* processes=%s"%processes, True)
            if processes:
                for process in processes:
                    process_server_key = "%s_SERVER"%process
                    d_server.set_to_dict(process_server_key, "STOP")
                
                start_time = datetime.datetime.now()
                while check_center_stop(d_server, processes):
                    end_time = datetime.datetime.now()
                    time_delta = (end_time - start_time).seconds
                    if time_delta > 10:#10秒钟停不下来，直接杀进程
                        printf("*******ServiceDataCommCenter stop 10s break", True)
                        break
                    time.sleep(1)
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            sys.stopservice = "true"
            win32event.SetEvent(self.hWaitStop)
            printf("*******before killall_pid", True)
            killall_pid(d_server, q_server, processes)#避免关闭服务器时重启服务
            printf("*******after killall_pid", True)
        except Exception, e:
            printf("ServiceDataCommCenter  error=%s"%e, True)
        q_server.connection.disconnect()
        d_server.close()

if __name__=='__main__':
    main(ServiceDataCommCenter)
