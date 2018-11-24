#coding=utf-8
import os

#用于当前进程与其他进程的管理同步(当前仅门禁使用)
#其他应用如果需要，下面的if需要修改，否则调用q_server时可能出错。
def run_acc_dictmanager():
    from redis_self.filequeue import SyncDict,FileQueue
    from mysite.utils import printf
    from mysite.iaccess.linux_or_win import run_commend
    try:
        #raw_input("Press any key to start server".center(50, "-"))
        #print '--server started--'
        
        q_server = FileQueue()
        printf("-svr8000--pid=%s"%os.getpid(), True)
        
        pid = q_server.get_from_file("DICT_SERVER_PID")
        #print '--pid2=',pid
        if pid:
            process_info = os.popen(run_commend(1) % pid).read()
            #print '---process_info=',process_info
            if run_commend(3) in process_info.lower():
                os.system(run_commend(2) % pid)#启动时收尸
        
        q_server.set_to_file("DICT_SERVER_PID", "%d"%(os.getpid()))
        q_server.connection.disconnect()
    except Exception, e:
        import traceback; traceback.print_exc()
    SyncDict(forever=True)


#显示运行在本地或远程计算机上的所有进程，带有多个执行参数
#'tasklist |findstr "%s"' % main_pid
dict_select_task={
    'win':'tasklist |findstr "%s"',
    'linux':'ps %s',
}
#杀死进程
#"taskkill /PID %s /F /T" % main_pid
dict_delete_task={
    'win':"taskkill /PID %s /F /T",
    'linux':'kill -9 %s',
}
#python应用程序
dict_python={
    'win':'python.exe',
    'linux':'python',
}

#强行杀死某进程
dict_f_delete_task={
    'win':"taskkill /im plrscagent.* /f",
    'linux':'killall -9 plrscagent'
}

all_dict={
    1:dict_select_task,
    2:dict_delete_task,
    3:dict_python,
    4:dict_f_delete_task,
}

def run_commend(dict_id):
    u""" 
    param:
        is_sys 操作系统{win,linux}
        dict_id   all_dict中的key
    """
    import dict4ini
#    APP_CONFIG = dict4ini.DictIni(os.getcwd()+"/appconfig.ini") 
#    IS_SYS = APP_CONFIG.iaccess.is_sys
    if os.name=='nt':
        get_commend=all_dict[dict_id]['win']
    else:
        get_commend=all_dict[dict_id]['linux']
    #print 'get_commend=',get_commend
    return get_commend
        




