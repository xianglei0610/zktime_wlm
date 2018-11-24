# -*- coding: utf-8 -*-

import win32serviceutil
import win32service
import win32event
import logging
import sys
import time
import os

def create_logger(fname):
    logger = logging.getLogger()
    hdlr = logging.FileHandler(fname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def get_python():
    '''
    获取安装包安装后的python.exe 路径
    '''
    return sys.executable.replace("lib\\site-packages\\win32\\PythonService.exe","python.exe")
    import win32api
    import win32con
    key=win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SOFTWARE", 0, win32con.KEY_ALL_ACCESS)
    key2=win32api.RegCreateKey(key, "Python\\PythonCore\\2.6\\InstallPath")
    return win32api.RegQueryValue(key2,"")+"python.exe"

def get_proc_mem_size(p):
    '''
    获取进程占用的内存大小
    '''
    import os
    pid=str(p.pid)
    tasks=[[i for i in item.split(" ") if i] \
           for item in os.popen("tasklist", "r").read().splitlines() if item][2:]
    for proc in tasks:
        if proc[1]==pid:
            return int(proc[-2].replace(",",""))
    return 0

def cmd_run(self, hWaitStop, cmd_and_args, path, logger, stop_fun=None):
    from subprocess import Popen
    import os
    import time
    if path: os.chdir(path)
    p=Popen(cmd_and_args, stdout=logger.handlers[0].stream)
    '''日志样式 2012-09-23 03:17:35,390 INFO pid=2532: d:\Program Files\ZKSoftware\ZKECO\Python26\python.exe svr8000.pyc'''
    logger.info("[pid:%s] command: %s"%(p.pid, " ".join(cmd_and_args)))
    
    # Test if it be stopped!
    while win32event.WAIT_TIMEOUT==win32event.WaitForSingleObject(hWaitStop, 1000):
        if p:
            if p.poll() is not None: #stoped, restart it
                logger.info("%s terminated, restart it"%p.pid)
                p=Popen(cmd_and_args, stdout=logger.handlers[0].stream)
                logger.info("pid=%s: %s"%(p.pid, " ".join(cmd_and_args)))
                time.sleep(10)
            elif self.check_max_log_time:
                '''对最大日志记录时间的控制'''
                f=logger.handlers[0].stream
                f.flush()
                if int(time.time())-os.fstat(f.fileno()).st_mtime>self.check_max_log_time:
                    logger.info("process dead, kill it")
                    if stop_fun:
                        stop_fun(p)
                    p.kill()
                    p.wait()
                    time.sleep(10)
            elif self.check_max_mem:
                '''对内存的监控'''
                msize=get_proc_mem_size(p)
                if msize>self.check_max_mem:
                    logger.info("process memory to large: %dK, kill it", msize)
                    if stop_fun:
                        stop_fun(p)
                    p.kill()
                    p.wait()
                    time.sleep(1)
            
    logger.info("finished")
    if stop_fun:
        stop_fun(p)
    if p:
        import signal
        import cPickle
        from ooredis.sync_redis import safe_exit
        p.send_signal(signal.SIGTERM)
        p.wait()
        safe_exit()
        f = open('loop_server.pid')
        process_pid = cPickle.load(f)
        for e in process_pid.keys():
            try:
                os.system("taskkill /PID %s /F /T" %process_pid[e])
            except:pass
        f.close()
        try:
            os.system("""taskkill /f /im nginx.exe""")
        except:pass
    logger.info(".\n")

class CmdService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ZkecoControlCenterService"
    _svc_display_name_ = "Zkeco Control Center Service"
    path = os.path.split(__file__)[0]
    cmd_and_args=[get_python(),"-u", "loop_server.pyc"]
    stop_fun=None
    check_max_log_time=0
    check_max_mem=0
    
    def init(self, args):
        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
        except Exception, e:
            import traceback; traceback.print_exc()
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger=create_logger("%stmp/Svc%s.log"%(self.path and self.path+"/" or "", self._svc_name_))
        self.logger.info('Service Init.')
        
    def __init__(self, args):
        try:
            return self.init(args)
        except:
            import traceback; traceback.print_exc(file=self.logger.handlers[0].stream)
            
    def SvcStop(self):
        '''关闭服务时的处理'''
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.logger.info("Service Stop.")
        except:
            import traceback; traceback.print_exc(file=self.logger.handlers[0].stream)
            
    def SvcDoRun(self):
        '''启动服务时的处理'''
        self.logger.info("Service Run.")
        try:
            self.run(self.cmd_and_args)
        except Exception, e:
            import traceback; traceback.print_exc(file=self.logger.handlers[0].stream)
            
    def run(self, cmd_and_args):
        return cmd_run(self, self.hWaitStop, cmd_and_args, self.path, self.logger, self.stop_fun)

def main(ServiceClass):
    import sys
    if len(sys.argv)>1:
        win32serviceutil.HandleCommandLine(ServiceClass)
    else:
        r=ServiceClass([ServiceClass._svc_name_])
        r.run(ServiceClass.cmd_and_args)

if __name__=='__main__':
    main(CmdService)