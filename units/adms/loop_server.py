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

import sys
import os
import datetime
import time

import pyuv

loop = pyuv.Loop.default_loop()

############################ 公共方法 ###########################
def log_t(name,pid,msg):
    LOG_FORMAT = '%s %s [pid:%s] %s\n'%(datetime.datetime.now(),name,pid,msg)
    return LOG_FORMAT


def save_pid():
    import cPickle
    f = open('loop_server.pid',"w")
    cPickle.dump(process_pid,f)
    f.close()

process_pid = {}
process_dict = {}
def common_callback(procname):
    m_now = datetime.datetime.now()
    if process_dict.has_key(procname):
        m_rec = process_dict[procname]
        m_rec["last"] = m_now
        m_rec["count"] += 1
        time.sleep(1)
        return 1
    else:
        process_dict[procname] = {"last":m_now,"count":1}
        time.sleep(1)
        return 1

############################相关全局参数 ########################
if os.path.exists("manage.py"):
    manage = "manage.py"
    websvr = "svr8000.py"
else:
    manage = "manage.pyc"
    websvr = "svr8000.pyc"

'''配置python 解释器'''    
if sys.platform == 'win32':
    pythoner = "python"
else:
    pythoner = "python"
    
python_path = "python.exe"
memcached_path = "memcached.exe"
cur_path = os.getcwd()

####################### 读取配置文件相关项 ###############################
import dict4ini
att_file = dict4ini.DictIni("attsite.ini")
VISIBLE_POS = att_file["Options"]["APP_POS"]
VISIBLE_ATT = att_file["Options"]["APP_ATT"]
VISIBLE_IACCESS = att_file["Options"]["APP_IACCESS"]
VISIBLE_POS_IC = att_file["Options"]["POS_IC"]
STD_PRINT = att_file["Options"]["STD_PRINT"]

EN_POS = EN_ATT = EN_IACCESS = EN_POS_IC = False
if VISIBLE_POS.lower()=="true":
    EN_POS = True
    if VISIBLE_POS_IC.lower()=="true":EN_POS_IC = True
if VISIBLE_ATT.lower()=="true":
    EN_ATT = True
if VISIBLE_IACCESS.lower()=="true":
    EN_IACCESS = True
    
m_arg = ''  #'-u' 输出缓冲开关
std_print = False #打印日志开关
if STD_PRINT.lower()=="true":
    m_arg = '-u'
    std_print = True

########################### 任务列表 #######################
#-------------------task1-------------------
#task1_log = open('task1.txt','a')  
def task1_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    print u'任务1退出'
    task1_log.write(log_t('任务1',proc.pid,'退出'))
    task1_log.flush()
    task1_log.close()
    proc.close()


task1 = pyuv.Process(loop)
def task1_spawn():
    task1.spawn(file="cmd.exe", args=[b"/c", r'C:\Python26\python.exe -u test.py'], exit_callback=task1_exit_cb)
    print u'任务1启动'
    task1_log.write(log_t('任务1',task1.pid,'启动'))
    task1_log.flush()
    
#--------------------task2------------------
#task2_log = open('task2.txt','a')  
def task2_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    print u'任务2退出'
    task2_log.write(log_t('任务2',proc.pid,'退出'))
    task2_log.flush()
    proc.close()


task2 = pyuv.Process(loop)
def task2_spawn():
    task2.spawn(file="cmd.exe", args=[b"/c", r'C:\Python26\python.exe -u test.py'], exit_callback=task2_exit_cb)
    print u'任务2启动'
    task2_log.write(log_t('任务2',task2.pid,'启动'))
    task2_log.flush()

##########################设置定时执行任务 ##################

def check(h,m,key):
    t_now=datetime.datetime.now()
    print key,u'最后执行时间....',last_dic[key]
    m_last = last_dic[key]==None and True or t_now.date() != last_dic[key].date()
    m_now = t_now.minute
    m_flag =  m==50 and m_now<=m+9 or m_now<m+10
    if m_last and t_now.hour==h and m_now>=m and m_flag:
        last_dic[key] = t_now
        return True
    else:
        return False
    
last_dic = {
            'task1':None,
            'task2':None,
            'task3':None,
            }
    
def timer_cb(timer):
    print 'cb...'
    if check(16,30,'task1'):
        task1_spawn()
        #print u'执行task1'
        
    if check(11,30,'task2'):
        print u'执行task2'
        
    if check(11,40,'task3'):
        print u'执行task3'

#timer = pyuv.Timer(loop)
#timer.start(timer_cb, 0.1, 2)

########################### 设置定频率执行任务 ##########################
def freq1_cb(timer):
    global task2
    try:
        task2.close()
    except:
        pass
    task2 = pyuv.Process(loop)
    task2_spawn()
    #print 'freq1_cb...'
    #timer.stop()
#freq1 = pyuv.Timer(loop)
#freq1.start(freq1_cb, 0.5, 4)   #0.5秒后开始执行,每4秒执行一次

def freq2_cb(timer):
    print 'freq2_cb...'
    #timer.stop()
#freq2 = pyuv.Timer(loop)
#freq2.start(freq2_cb, 0.5, 4)

########################### 定义服务相关对象 #######################
def handle_close_cb(handle):
    pass
#---------------------------webserver服务---------------------------------
def webserver_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global webserver
    global webserver_pipe
    global webserver_error_pipe
    print u'webserver exit'
    if common_callback("webserver")==0:
        webserver.close()
        return
    webserver_log.write(log_t('webserver',proc.pid,'exit'))
    webserver_log.write(log_t('webserver',proc.pid,'auto start'))
    webserver_log.flush()
    webserver.close(handle_close_cb)
    webserver = pyuv.Process(loop)
    webserver_pipe = pyuv.Pipe(loop)
    webserver_error_pipe = pyuv.Pipe(loop)
    webserver_spawn()
    save_pid()
    
webserver_log = open('webserver.log','a')
def webserver_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    webserver_log.write('%s\n'%data_str)
    webserver_log.flush()
    
webserver = pyuv.Process(loop)
webserver_pipe = pyuv.Pipe(loop)
webserver_error_pipe = pyuv.Pipe(loop)


def webserver_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=webserver_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=webserver_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        webserver.spawn(file=pythoner, args=[m_arg, r'%s'%websvr],  exit_callback=webserver_exit_cb, stdio=stdio)
    else:
        webserver.spawn(file=pythoner, args=[m_arg, r'%s'%websvr],  exit_callback=webserver_exit_cb, stdio=stdio)
    if std_print:
        webserver_pipe.start_read(webserver_read_cb)
        webserver_error_pipe.start_read(webserver_read_cb)
    print u'webserver start'
    process_pid["webserver"] = webserver.pid
    webserver_log.write(log_t('webserver',webserver.pid,'start'))
    webserver_log.flush()

#------------------------------WriteData服务------------------------------
def WriteData_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global WriteData
    global WriteData_pipe
    global WriteData_error_pipe
    print u'WriteData exit'
    if common_callback("WriteData")==0:
        WriteData.close()
        return
    WriteData_log.write(log_t('WriteData',proc.pid,'exit'))
    WriteData_log.write(log_t('WriteData',proc.pid,'auto start'))
    WriteData_log.flush()
    WriteData.close(handle_close_cb)
    WriteData = pyuv.Process(loop)
    WriteData_pipe = pyuv.Pipe(loop)
    WriteData_error_pipe = pyuv.Pipe(loop)
    WriteData_spawn()
    save_pid()

def WriteData_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    WriteData_log.write('%s\n'%data_str)
    WriteData_log.flush()
if EN_ATT:    
    WriteData_log = open('WriteData.log','a')   
    WriteData = pyuv.Process(loop)
    WriteData_pipe = pyuv.Pipe(loop)
    WriteData_error_pipe = pyuv.Pipe(loop)

def WriteData_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=WriteData_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=WriteData_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        WriteData.spawn(file=pythoner, args=[m_arg, manage, 'writedata'],  exit_callback=WriteData_exit_cb, stdio=stdio)
    else:
        WriteData.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'writedata'],  exit_callback=WriteData_exit_cb, stdio=stdio)
    if std_print:
        WriteData_pipe.start_read(WriteData_read_cb)
        WriteData_error_pipe.start_read(WriteData_read_cb)
    print u'WriteData start'
    process_pid["WriteData"] = WriteData.pid
    WriteData_log.write(log_t('WriteData',WriteData.pid,'start'))
    WriteData_log.flush()    
    
#-----------------------------ZksaasAdms服务------------------------------
def ZksaasAdms_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global ZksaasAdms
    global ZksaasAdms_pipe
    global ZksaasAdms_error_pipe
    print u'ZksaasAdms exit'
    if common_callback("ZksaasAdms")==0:
        ZksaasAdms.close()
        return
    ZksaasAdms_log.write(log_t('ZksaasAdms',proc.pid,'exit'))
    ZksaasAdms_log.write(log_t('ZksaasAdms',proc.pid,'auto start'))
    ZksaasAdms_log.flush()
    ZksaasAdms.close(handle_close_cb)
    ZksaasAdms = pyuv.Process(loop)
    ZksaasAdms_pipe = pyuv.Pipe(loop)
    ZksaasAdms_error_pipe = pyuv.Pipe(loop)
    ZksaasAdms_spawn()
    save_pid()
    
def ZksaasAdms_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    ZksaasAdms_log.write('%s\n'%data_str)
    ZksaasAdms_log.flush()

if EN_ATT:    
    ZksaasAdms_log = open('ZksaasAdms.log','a')
    ZksaasAdms = pyuv.Process(loop)
    ZksaasAdms_pipe = pyuv.Pipe(loop)
    ZksaasAdms_error_pipe = pyuv.Pipe(loop)

def ZksaasAdms_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=ZksaasAdms_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=ZksaasAdms_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        ZksaasAdms.spawn(file=pythoner, args=[m_arg, manage, 'zksaas_adms'],  exit_callback=ZksaasAdms_exit_cb, stdio=stdio)
    else:
        ZksaasAdms.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'zksaas_adms'],  exit_callback=ZksaasAdms_exit_cb, stdio=stdio)
    if std_print:
        ZksaasAdms_pipe.start_read(ZksaasAdms_read_cb)
        ZksaasAdms_error_pipe.start_read(ZksaasAdms_read_cb)
    print u'ZksaasAdms start'
    process_pid["ZksaasAdms"] = ZksaasAdms.pid
    ZksaasAdms_log.write(log_t('ZksaasAdms',ZksaasAdms.pid,'start'))
    ZksaasAdms_log.flush()    
    
#-----------------------------AutoCalculate服务------------------------------
def AutoCalculate_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global AutoCalculate
    global AutoCalculate_pipe
    global AutoCalculate_error_pipe
    print u'AutoCalculate exit'
    if common_callback("AutoCalculate")==0:
        AutoCalculate.close()
        return
    AutoCalculate_log.write(log_t('AutoCalculate',proc.pid,'exit'))
    AutoCalculate_log.write(log_t('AutoCalculate',proc.pid,'auto start'))
    AutoCalculate_log.flush()
    AutoCalculate.close(handle_close_cb)
    AutoCalculate = pyuv.Process(loop)
    AutoCalculate_pipe = pyuv.Pipe(loop)
    AutoCalculate_error_pipe = pyuv.Pipe(loop)
    AutoCalculate_spawn()
    save_pid()
    
def AutoCalculate_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    AutoCalculate_log.write('%s\n'%data_str)
    AutoCalculate_log.flush()

if EN_ATT:    
    AutoCalculate_log = open('AutoCalculate.log','a')
    AutoCalculate = pyuv.Process(loop)
    AutoCalculate_pipe = pyuv.Pipe(loop)
    AutoCalculate_error_pipe = pyuv.Pipe(loop)

def AutoCalculate_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=AutoCalculate_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=AutoCalculate_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        AutoCalculate.spawn(file=pythoner, args=[m_arg, manage, 'autocalculate'],  exit_callback=AutoCalculate_exit_cb, stdio=stdio)
    else:
        AutoCalculate.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'autocalculate'],  exit_callback=AutoCalculate_exit_cb, stdio=stdio)
    if std_print:
        AutoCalculate_pipe.start_read(AutoCalculate_read_cb)
        AutoCalculate_error_pipe.start_read(AutoCalculate_read_cb)
    print u'AutoCalculate start'
    process_pid["AutoCalculate"] = AutoCalculate.pid
    AutoCalculate_log.write(log_t('AutoCalculate',AutoCalculate.pid,'start'))
    AutoCalculate_log.flush()    
    
    
      # --ftp_sync ftp 同步服务   ----- 
def FTPSync_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global FTPSync
    global FTPSync_pipe
    global FTPSync_error_pipe
    print u'FTPSync exit'
    if common_callback("FTPSync")==0:
        FTPSync.close()
        return
    FTPSync_log.write(log_t('FTPSync',proc.pid,'exit'))
    FTPSync_log.write(log_t('FTPSync',proc.pid,'auto start'))
    FTPSync_log.flush()
    FTPSync.close(handle_close_cb)
    FTPSync = pyuv.Process(loop)
    FTPSync_pipe = pyuv.Pipe(loop)
    FTPSync_error_pipe = pyuv.Pipe(loop)
    FTPSync_spawn()
    save_pid()
    
def FTPSync_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    FTPSync_log.write('%s\n'%data_str)
    FTPSync_log.flush()

FTPSync_log = open('FTPSync.log','a')
FTPSync = pyuv.Process(loop)
FTPSync_pipe = pyuv.Pipe(loop)
FTPSync_error_pipe = pyuv.Pipe(loop)

def FTPSync_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=FTPSync_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=FTPSync_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        FTPSync.spawn(file=pythoner, args=[m_arg, manage, 'ftp_sync'],  exit_callback=FTPSync_exit_cb, stdio=stdio)
    else:
        FTPSync.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'ftp_sync'],  exit_callback=FTPSync_exit_cb, stdio=stdio)
    if std_print:
        FTPSync_pipe.start_read(FTPSync_read_cb)
        FTPSync_error_pipe.start_read(FTPSync_read_cb)
    print u'FTPSync start'
    process_pid["FTPSync"] = FTPSync.pid
    FTPSync_log.write(log_t('FTPSync',FTPSync.pid,'start'))
    FTPSync_log.flush() 
    
    
    
    
    
#------------------------------InstantMsg服务------------------------------
def InstantMsg_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global InstantMsg
    global InstantMsg_pipe
    global InstantMsg_error_pipe
    print u'InstantMsg exit'
    if common_callback("InstantMsg")==0:
        InstantMsg.close()
        return
    InstantMsg_log.write(log_t('InstantMsg',proc.pid,'exit'))
    InstantMsg_log.write(log_t('InstantMsg',proc.pid,'auto start'))
    InstantMsg_log.flush()
    InstantMsg.close(handle_close_cb)
    InstantMsg = pyuv.Process(loop)
    InstantMsg_pipe = pyuv.Pipe(loop)
    InstantMsg_error_pipe = pyuv.Pipe(loop)
    InstantMsg_spawn()
    save_pid()
    
def InstantMsg_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    InstantMsg_log.write('%s\n'%data_str)
    InstantMsg_log.flush()

InstantMsg_log = open('InstantMsg.log','a')
InstantMsg = pyuv.Process(loop)
InstantMsg_pipe = pyuv.Pipe(loop)
InstantMsg_error_pipe = pyuv.Pipe(loop)

def InstantMsg_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=InstantMsg_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=InstantMsg_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        InstantMsg.spawn(file=pythoner, args=[m_arg, manage, 'instantmsg'],  exit_callback=InstantMsg_exit_cb, stdio=stdio)
    else:
        InstantMsg.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'instantmsg'],  exit_callback=InstantMsg_exit_cb, stdio=stdio)
    if std_print:
        InstantMsg_pipe.start_read(InstantMsg_read_cb)
        InstantMsg_error_pipe.start_read(InstantMsg_read_cb)
    print u'InstantMsg start'
    process_pid["InstantMsg"] = InstantMsg.pid
    InstantMsg_log.write(log_t('InstantMsg',InstantMsg.pid,'start'))
    InstantMsg_log.flush()    
    
#------------------------------ZkposAdms服务------------------------------
def ZkposAdms_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global ZkposAdms
    global ZkposAdms_pipe
    global ZkposAdms_error_pipe
    print u'ZkposAdms exit'
    if common_callback("ZkposAdms")==0:
        ZkposAdms.close()
        return
    ZkposAdms_log.write(log_t('ZkposAdms',proc.pid,'exit'))
    ZkposAdms_log.write(log_t('ZkposAdms',proc.pid,'auto start'))
    ZkposAdms_log.flush()
    ZkposAdms.close(handle_close_cb)
    ZkposAdms = pyuv.Process(loop)
    ZkposAdms_pipe = pyuv.Pipe(loop)
    ZkposAdms_error_pipe = pyuv.Pipe(loop)
    ZkposAdms_spawn()
    save_pid()
    
def ZkposAdms_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    ZkposAdms_log.write('%s\n'%data_str)
    ZkposAdms_log.flush()
    
if EN_POS_IC: 
    ZkposAdms_log = open('ZkposAdms.log','a')
    ZkposAdms = pyuv.Process(loop)
    ZkposAdms_pipe = pyuv.Pipe(loop)
    ZkposAdms_error_pipe = pyuv.Pipe(loop)

def ZkposAdms_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=ZkposAdms_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=ZkposAdms_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        ZkposAdms.spawn(file=pythoner, args=[m_arg, manage, 'zkpos_adms'],  exit_callback=ZkposAdms_exit_cb, stdio=stdio)
    else:
        ZkposAdms.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'zkpos_adms'],  exit_callback=ZkposAdms_exit_cb, stdio=stdio)
    if std_print:
        ZkposAdms_pipe.start_read(ZkposAdms_read_cb)
        ZkposAdms_error_pipe.start_read(ZkposAdms_read_cb)
    print u'ZkposAdms start'
    process_pid["ZkposAdms"] = ZkposAdms.pid
    ZkposAdms_log.write(log_t('ZkposAdms',ZkposAdms.pid,'start'))
    ZkposAdms_log.flush()    
    
#------------------------------DataCommCenter服务------------------------------
def DataCommCenter_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global DataCommCenter
    global DataCommCenter_pipe
    global DataCommCenter_error_pipe
    print u'DataCommCenter exit'
    if common_callback("DataCommCenter")==0:
        DataCommCenter.close()
        return
    DataCommCenter_log.write(log_t('DataCommCenter',proc.pid,'exit'))
    DataCommCenter_log.write(log_t('DataCommCenter',proc.pid,'auto start'))
    DataCommCenter_log.flush()
    DataCommCenter.close(handle_close_cb)
    DataCommCenter = pyuv.Process(loop)
    DataCommCenter_pipe = pyuv.Pipe(loop)
    DataCommCenter_error_pipe = pyuv.Pipe(loop)
    DataCommCenter_spawn()
    save_pid()
    
def DataCommCenter_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    DataCommCenter_log.write('%s\n'%data_str)
    DataCommCenter_log.flush()
    
if EN_IACCESS: 
    DataCommCenter_log = open('DataCommCenter.log','a')
    DataCommCenter = pyuv.Process(loop)
    DataCommCenter_pipe = pyuv.Pipe(loop)
    DataCommCenter_error_pipe = pyuv.Pipe(loop)

def DataCommCenter_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=DataCommCenter_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=DataCommCenter_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        DataCommCenter.spawn(file=pythoner, args=[m_arg, manage, 'datacommcenter'],  exit_callback=DataCommCenter_exit_cb, stdio=stdio)
    else:
        DataCommCenter.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'datacommcenter'],  exit_callback=DataCommCenter_exit_cb, stdio=stdio)
    if std_print:
        DataCommCenter_pipe.start_read(DataCommCenter_read_cb)
        DataCommCenter_error_pipe.start_read(DataCommCenter_read_cb)
    print u'DataCommCenter start'
    process_pid["DataCommCenter"] = DataCommCenter.pid
    DataCommCenter_log.write(log_t('DataCommCenter',DataCommCenter.pid,'start'))
    DataCommCenter_log.flush()    
    
#------------------------------RedisSelf服务------------------------------
def RedisSelf_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global RedisSelf
    global RedisSelf_pipe
    global RedisSelf_error_pipe
    print u'RedisSelf exit'
    if common_callback("RedisSelf")==0:
        RedisSelf.close()
        return
    RedisSelf_log.write(log_t('RedisSelf',proc.pid,'exit'))
    RedisSelf_log.write(log_t('RedisSelf',proc.pid,'auto start'))
    RedisSelf_log.flush()
    RedisSelf.close(handle_close_cb)
    RedisSelf = pyuv.Process(loop)
    RedisSelf_pipe = pyuv.Pipe(loop)
    RedisSelf_error_pipe = pyuv.Pipe(loop)
    RedisSelf_spawn()
    save_pid()
    
def RedisSelf_read_cb(handle, data, error):
    data_str = data and data.strip() or ""
    RedisSelf_log.write('%s\n'%data_str)
    RedisSelf_log.flush()
    
if EN_IACCESS: 
    RedisSelf_log = open('RedisSelf.log','a')
    RedisSelf = pyuv.Process(loop)
    RedisSelf_pipe = pyuv.Pipe(loop)
    RedisSelf_error_pipe = pyuv.Pipe(loop)

def RedisSelf_spawn():
    stdio = []
    stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
    stdio.append(pyuv.StdIO(stream=RedisSelf_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    stdio.append(pyuv.StdIO(stream=RedisSelf_error_pipe, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
    if sys.platform == 'win32':
        RedisSelf.spawn(file=pythoner, args=[m_arg, manage, 'redis_self'],  exit_callback=RedisSelf_exit_cb, stdio=stdio)
    else:
        RedisSelf.spawn(file=pythoner, args=[m_arg, r'%s'%manage,'redis_self'],  exit_callback=RedisSelf_exit_cb, stdio=stdio)
    if std_print:
        RedisSelf_pipe.start_read(RedisSelf_read_cb)
        RedisSelf_error_pipe.start_read(RedisSelf_read_cb)
    print u'RedisSelf start'
    process_pid["RedisSelf"] = RedisSelf.pid
    RedisSelf_log.write(log_t('RedisSelf',RedisSelf.pid,'start'))
    RedisSelf_log.flush()  
    
#------------------------------Memmcached服务------------------------------
def Memmcached_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global Memmcached
    print u'Memmcached exit'
    if common_callback("Memmcached")==0:
        Memmcached.close()
        return
    Memmcached.close(handle_close_cb)
    Memmcached = pyuv.Process(loop)
    Memmcached_spawn()
    save_pid()
    
Memmcached = pyuv.Process(loop)

def Memmcached_spawn():
    if sys.platform == 'win32':
        Memmcached.spawn(file="cmd.exe", args=[b"/c", memcached_path, "-p", "11211",  "-m ", "512"], exit_callback=Memmcached_exit_cb)
    else:
        Memmcached.spawn(file="/usr/local/bin/memcached", args=[m_arg,'nobody', '-p', '11211', '-l', '127.0.0.1', '-m', '128'], exit_callback=Memmcached_exit_cb)
    print u'Memmcached start'
    process_pid["Memmcached"] = Memmcached.pid

#------------------------------Redis服务------------------------------
def Redis_exit_cb(proc, exit_status, term_signal):
    exit_status==0
    global Redis
    print u'Redis exit'
    if common_callback("Redis")==0:
        Redis.close()
        return
    Redis.close(handle_close_cb)
    Redis = pyuv.Process(loop)
    Redis_spawn()
    save_pid()
    
Redis = pyuv.Process(loop)

def Redis_spawn():
    if sys.platform == 'win32':
        os.chdir('../../python-support/redis/redis-2.0.2')
        Redis.spawn(file="cmd.exe", args=[b"/c", "redis-server.exe", "redis.conf"], exit_callback=Redis_exit_cb)
        os.chdir(cur_path)
    else:
        Redis.spawn(file="/usr/local/bin/redis", args=[m_arg,'nobody', '-p', '11211', '-l', '127.0.0.1', '-m', '128'], exit_callback=Redis_exit_cb)
    print u'Redis start'
    process_pid["Redis"] = Redis.pid
    
#################################注册信号回调函数 ###########################
import signal

def stop_signal_cb(handle, signum=None):
    signum==signal.SIGTERM
    print u'Loop server exit. all proccesses is stopping...'
    try:
        webserver.kill(signal.SIGTERM)  #SIGABRT
        webserver.close()
        webserver_log.write(log_t('webserver',0,'be stoped'))
        webserver_log.flush()
    except:pass
    
    if EN_ATT:
        try:
            AutoCalculate.kill(signal.SIGTERM)
            AutoCalculate.close()
            AutoCalculate_log.write(log_t('AutoCalculate',0,'be stoped'))
            AutoCalculate_log.flush()
        except:pass
        
        try:
            WriteData.kill(signal.SIGTERM)
            WriteData.close()
            WriteData_log.write(log_t('WriteData',0,'be stoped'))
            WriteData_log.flush()
        except:pass
        
        try:
            ZksaasAdms.kill(signal.SIGTERM)
            ZksaasAdms.close()
            ZksaasAdms_log.write(log_t('ZksaasAdms',0,'be stoped'))
            ZksaasAdms_log.flush()
        except:pass
        
    try:
        InstantMsg.kill(signal.SIGTERM)
        InstantMsg.close()
        InstantMsg_log.write(log_t('InstantMsg',0,'be stoped'))
        InstantMsg_log.flush()
    except:pass
    
    if EN_POS_IC:
        try:
            ZkposAdms.kill(signal.SIGTERM)
            ZkposAdms.close()
            ZkposAdms_log.write(log_t('ZkposAdms',0,'be stoped'))
            ZkposAdms_log.flush()
        except:pass
    if EN_IACCESS:
        try:
            DataCommCenter.kill(signal.SIGTERM)
            DataCommCenter.close()
            DataCommCenter_log.write(log_t('DataCommCenter',0,'be stoped'))
            DataCommCenter_log.flush()
        except:pass
        
        try:
            RedisSelf.kill(signal.SIGTERM)
            RedisSelf.close()
            RedisSelf_log.write(log_t('RedisSelf',0,'be stoped'))
            RedisSelf_log.flush()
        except:pass
        
    try: 
        Memmcached.kill(signal.SIGTERM)
        Memmcached.close()
    except:pass
    
    try:
        redis_safe_exit()
        Redis.close()
    except:pass
#    if sys.platform == 'win32':
#        os.popen("taskkill /im redis-server.exe /f")
#    else:
#        Redis.kill(signal.SIGTERM)
    exit()
    
def  redis_safe_exit():
    from ooredis.sync_redis import safe_exit
    safe_exit()

def restart_signal_cb(handle, signum):
    signum==signal.SIGUSR2
    print u'All services is restarting...'
    webserver_log.write(log_t('webserver',0,'be restartting'))
    webserver_log.flush()
    webserver.kill(signal.SIGTERM)
    
    WriteData_log.write(log_t('WriteData',0,'be restartting'))
    WriteData_log.flush()
    WriteData.kill(signal.SIGTERM)
    
    ZksaasAdms_log.write(log_t('ZksaasAdms',0,'be restartting'))
    ZksaasAdms_log.flush()
    ZksaasAdms.kill(signal.SIGTERM)
    
    InstantMsg_log.write(log_t('ZksaasAdms',0,'be restartting'))
    InstantMsg_log.flush()
    InstantMsg.kill(signal.SIGTERM)
    
    ZkposAdms_log.write(log_t('ZkposAdms',0,'be restartting'))
    ZkposAdms_log.flush()
    ZkposAdms.kill(signal.SIGTERM)
    
    DataCommcenter_log.write(log_t('DataCommcenter',0,'be restartting'))
    DataCommcenter_log.flush()
    DataCommcenter.kill(signal.SIGTERM)
    
    SycnServer_log.write(log_t('SycnServer',0,'be restartting'))
    SycnServer_log.flush()
    SycnServer.kill(signal.SIGTERM)
    
    Memmcached.kill(signal.SIGTERM)

#############################启动各服务###############################
Memmcached_spawn()
Redis_spawn()
webserver_spawn()
InstantMsg_spawn() 

if EN_ATT:
    AutoCalculate_spawn()
    WriteData_spawn()
    ZksaasAdms_spawn()
    
if EN_POS_IC:
    ZkposAdms_spawn()
  
if EN_IACCESS:
    DataCommCenter_spawn()
    RedisSelf_spawn()

save_pid()
#############################注册信号,启动事件循环##############################
def set_exit_handler():
    '''
    注册关闭信号的处理
    '''
    if os.name == "nt":
        try:
            import win32api
            win32api.SetConsoleCtrlHandler(stop_signal_cb, True)
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
    else:
        import signal
        signal.signal(signal.SIGTERM, stop_signal_cb)
        signal.signal(signal.SIGUSR1, stop_signal_cb)
        signal.signal(signal.SIGUSR2, restart_signal_cb)
    
if __name__ == "__main__":
    print u"Completed."
    set_exit_handler()
    loop.run()

    
