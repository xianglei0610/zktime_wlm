# -*- coding: utf-8 -*-
import sys
import socket
import time
import threading
from mysite.personnel.models.model_issuecard import IssueCard
from mysite.personnel.models.model_emp import Employee,getuserinfo
import random
from  decimal import Decimal
from mysite.iclock.models.model_device import Device
import threading,time,datetime
from mysite.personnel.models.model_area import Area
from mysite.sql_utils import p_query,p_execute,p_query_one
import urllib,urllib2
import sys, os
import dict4ini
from django.conf import settings
from ooredis import *
from ooredis.client  import get_client



import Queue, threading, sys   
from threading import Thread   
import time,urllib   
# working thread   
class Worker(Thread):   
   worker_count = 0   
   def __init__( self, workQueue, resultQueue, timeout = 0, **kwds):   
       Thread.__init__( self, **kwds )   
       self.id = Worker.worker_count   
       Worker.worker_count += 1   
       self.setDaemon( True )   
       self.workQueue = workQueue   
       self.resultQueue = resultQueue   
       self.timeout = timeout   
       self.start( )   
   def run( self ):   
       ''' the get-some-work, do-some-work main loop of worker threads '''   
       while True:   
           try:   
               callable, args, kwds = self.workQueue.get(timeout=self.timeout)   
               res = callable(*args, **kwds)   
               print "worker[%2d]: %s" % (self.id, str(res) )   
               self.resultQueue.put( res )   
           except Queue.Empty:   
               break   
           except :   
               print 'worker[%2d]' % self.id, sys.exc_info()[:2]   
                  
class WorkerManager:   
   def __init__( self, num_of_workers=10, timeout = 1):   
       self.workQueue = Queue.Queue()   
       self.resultQueue = Queue.Queue()   
       self.workers = []   
       self.timeout = timeout   
       self._recruitThreads( num_of_workers )   
   def _recruitThreads( self, num_of_workers ):   
       for i in range( num_of_workers ):   
           worker = Worker( self.workQueue, self.resultQueue, self.timeout )   
           self.workers.append(worker)   
   def wait_for_complete( self):   
       # ...then, wait for each of them to terminate:   
       while len(self.workers):   
           worker = self.workers.pop()   
           worker.join( )   
           if worker.isAlive() and not self.workQueue.empty():   
               self.workers.append( worker )   
       print "All jobs are are completed."   
   def add_job( self, callable, *args, **kwds ):   
       self.workQueue.put( (callable, args, kwds) )   
   def get_result( self, *args, **kwds ):   
       return self.resultQueue.get( *args, **kwds )  




def doPost(sn,card):
        request = 'http://192.168.10.92:8090/iclock/pos_getrequest?SN=%s&sequ=97600&card=%s&posmoney=100&postype=1'% (sn,card)
        print request
        response = urllib2.urlopen(request)
        file = response.read()
        print file
        
def set_random(bnum,enum):
    list = range(bnum,enum)
    blist_webId = random.sample(list, enum-1)
    return blist_webId 
    
def insert_card():
    pin=set_random(1,100)
    for i in pin:
        IssueCard(
                UserID_id=1,
                cardno=i,
                type_id=1,
                blance=Decimal('10000'),
                mng_cost=Decimal(10),
                card_cost=Decimal('10'),
                date_money=Decimal('20'),
                meal_money=Decimal('20'),
                card_privage='0',).save(force_insert=True, log_msg=False)
        print "inset date......"
    print "end"

def insert_device():
    pin=set_random(1,20)
    for i in pin:
        Device(
            sn=str(i), 
            alias="auto_add",
            last_activity=datetime.datetime.now(), 
            area=Area.objects.all()[0],
            ipaddress="192.168.10.160",
            dining_id=1,
            consume_model=1,
            device_type=5).save(log_msg=False)
        print "inset date......"
    print"end"
    




class ThreadDemo(threading.Thread):
    def __init__(self, index, create_time): #constructor
        threading.Thread.__init__(self)
        self.index = index
        self.create_time = create_time
    def run(self):
        doPost()
        print (time.time()-self.create_time),self.index
#for index in range(20):
#    thread = ThreadDemo(index, time.time())
#    thread.start() #start thread
#    if i%10==1: time.sleep(1)
#print "Main thread exit..."

def test_job(id, sleep = 100 ):  
    try:  
         card=id
         sn=random.randint(1,20)
         doPost(sn,card)
         print time.time()
         print "+++++++++++++++++++++++++++++++++++++++++"
    except:  
        print '[%4d]' % id, sys.exc_info()[:2]  
    return  id  
  
def test():  
    import socket  
#    import pos_test
    socket.setdefaulttimeout(1)  
    print 'start testing'  
    wm = WorkerManager(20)
    for i in range(2):  
        wm.add_job( test_job, i)  
#    wm.start()  
    wm.wait_for_complete()  
    print 'end testing'  




#def test_run(c):
#    devices=[]
#    for i in range(c):
#        device = ThreadDemo(i, time.time())
#        devices.append(device)
#        device.start()
#        if i%10==1: time.sleep(1)
#    return devices

if __name__=="__main__":
    import sys
#    insert_card()
    test()
    
    
    
from mysite.iclock.models.model_cmmdata import pos_gen_device_cmmdata
from mysite.pos.pos_ic.ic_sync_store import save_pos_file
from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE
def get_device(sn):
    from mysite.iclock.cache_cmds import get_device_raise
    return get_device_raise(sn)

def add_pos_log():
    device = get_device("5849791460183")
    head_data=":pos_log_stamp: SN=5849791460183\tIP=192.168.10.183\tTIME=%s\tSTAMP=%s\tSTAMPID=%s\tZ=1"%(datetime.datetime.now(),10000,888888)
    data_str = ""
#    s_data="%s\n%s\n\n"%(head_data, rawData)
    blance = 100000
    for i in range(100):
        dev_sere = i
        bl =  blance -i
        data_row = "1\t1\t%s\t100\t%s\t25\t1\t3\t4894\t%s\t0\n"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),bl*100,dev_sere)
        data_str+=data_row
    s_data="%s\n%s\n\n"%(head_data, data_str)
    from mysite.iclock.models.model_cmmdata import pos_gen_device_cmmdata
    from mysite.pos.pos_ic.ic_sync_store import save_pos_file
    if POS_IC_ADMS_MODEL:
        obj = save_pos_file(device,s_data)
    else:
        obj=pos_gen_device_cmmdata(device,s_data)
    print s_data
    
#模拟IC消费设备获取命令请求
def ic_posrequest():
    import time
    request = 'http://192.168.10.100:8000/iclock/posrequest?SN=5849791460183&type=pos&devno=967'
    while True:
        response = urllib2.urlopen(request)
        file = response.read()
        print file
        time.sleep(5)
    

#检查设备记录流水号有间断的情况
def check_device_pos_log(sn):
    from mysite.pos.models.model_icconsumerlist import ICConsumerList
    check_sql = """
        select * from(
        select dev_serial_num from pos_icconsumerlist where dev_sn = '%s' and  dev_serial_num is not null 
        union all
        select dev_serial_num  from  dbo.pos_icerrorlog where dev_sn = '%s' and  dev_serial_num is not null 
        ) a group by dev_serial_num order by dev_serial_num
    """
#    pos_data = ICConsumerList.objects.filter(dev_sn = sn,type_name__in=[6,10,9]).values_list('dev_serial_num','user_pin').order_by('dev_serial_num')
    pos_data = p_query(check_sql%(sn,sn))
    pos_data_bak = pos_data
    item = 0
    data_len = len(pos_data)
    b = pos_data[0][0]
    e = pos_data[data_len-1][0]
    err_log = []
    for i in range(b,e):
        if(i!=int(pos_data[item][0])):
            item = item-1
            err_log.append(i)
        item = item + 1
    print "end=================",item,err_log
    
#"""
#select * from 
#(
#select dev_serial_num from pos_icconsumerlist where dev_sn = '5849791460183' and  dev_serial_num is not null 
#union all
#select dev_serial_num  from  dbo.pos_icerrorlog where dev_sn = '5849791460183' and  dev_serial_num is not null 
#
#) a group by dev_serial_num  having count(1) >= 2 order by dev_serial_num
#
#"""

#检查设备记录流水号重复的记录
def check_repeating_data_log(sn):
    from mysite.pos.models.model_icconsumerlist import ICConsumerList
    check_sql = """
        select * from(
        select dev_serial_num from pos_icconsumerlist where dev_sn = '%s' and  dev_serial_num is not null 
        union all
        select dev_serial_num  from  dbo.pos_icerrorlog where dev_sn = '%s' and  dev_serial_num is not null 
        ) a group by dev_serial_num having count(1) >= 2 order by dev_serial_num
    """
#    pos_data = ICConsumerList.objects.filter(dev_sn = sn,type_name__in=[6,10,9]).values_list('dev_serial_num','user_pin').order_by('dev_serial_num')
    pos_data = p_query(check_sql%(sn,sn))
    if pos_data:
        print "repeating_data==",pos_data
        return pos_data
    else:
        print "not repeating data"
        return "not repeating data"


#返回设备记录是否采集完整
def pos_dev_status(sn):
    from mysite.sql_utils import p_query,p_execute,p_query_one

        sel_sql = """
            select max_dev_serial,min_dev_serial,pos_count,max_dev_serial - min_dev_serial + 1 as dic_count from 
                (
                    select max(dev_serial_num) as max_dev_serial,MIN(dev_serial_num) as min_dev_serial,COUNT(1) as pos_count from 
                    (
                        select dev_serial_num from 
                         (
                             select dev_serial_num from pos_icconsumerlist where dev_sn = '%s' and  dev_serial_num is not null and pos_time> DateAdd(Month,-3,getdate())
                             union all
                             select dev_serial_num  from  dbo.pos_icerrorlog where dev_sn = '%s' and  dev_serial_num is not null and pos_time> DateAdd(Month,-3,getdate())
                         ) as a group by dev_serial_num
                    )as pos_log  
                )
                as device_data_info
        """
        q_list = p_query_one(sel_sql %(self.sn,self.sn))
        print q_list
        if q_list[2] == q_list[3] or q_list[2] == 0:
            return True
        else:
            return False


def get_pos_site_file():
    current_path = settings.WORK_PATH
    pos_config=dict4ini.DictIni(current_path+"/pos/pos_config.ini")
    return pos_config

#保持redis中消费设备的数据到pos_config.ini文件
def set_pos_site_file():
    r_client = get_client()
    all_pos_device = r_client.keys("pos_device:*:data")
    for i in all_pos_device:
        sn = i.split(":")[1]
        print Dict(i)
        pos_log_stamp_id = Dict(i)['pos_log_stamp_id']
        full_log_stamp_id = Dict(i)['full_log_stamp_id']
        allow_log_stamp_id = Dict(i)['allow_log_stamp_id']
        pos_log_bak_stamp_id = Dict(i)['pos_log_bak_stamp_id']
        full_log_bak_stamp_id = Dict(i)['full_log_bak_stamp_id']
        allow_log_bak_stamp_id = Dict(i)['allow_log_bak_stamp_id']
        pos_config = get_pos_site_file()
        redis_key = "pos_device:%s:data"%sn
        redis_value = pos_log_stamp_id +"%"+full_log_stamp_id+"%"+allow_log_stamp_id+"%"+pos_log_bak_stamp_id+"%"+full_log_bak_stamp_id+"%"+allow_log_bak_stamp_id
        pos_config["Pos_Device"][redis_key]=redis_value
        pos_config.save()

def init_ic_pos_device(device):
    '''
    初始化设备信息
    '''
    from mysite.pos.pos_ic.ic_sync_model import Pos_Device
    import datetime
    m_dict = {}
    m_dict["sn"] = device.sn
    m_dict["pos_log_stamp_id"] = device.pos_log_stamp_id
    m_dict["full_log_stamp_id"] = device.full_log_stamp_id
    m_dict["allow_log_stamp_id"] = device.allow_log_stamp_id
    m_dict["pos_log_bak_stamp_id"] = device.pos_log_bak_stamp_id
    m_dict["full_log_bak_stamp_id"] = device.full_log_bak_stamp_id
    m_dict["allow_log_bak_stamp_id"] = device.allow_log_bak_stamp_id
    m_dict["pos_dev_data_status"] = device.pos_dev_data_status
    
    m_dict["pos_all_log_stamp"] = device.pos_all_log_stamp or 0
    m_dict["pos_log_stamp"] = device.pos_log_stamp or 0
    m_dict["full_log_stamp"] = device.full_log_stamp or 0 
    m_dict["allow_log_stamp"] = device.allow_log_stamp or 0 
    m_dict["last_activity"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r_device=Pos_Device(device.sn)
    r_device.sets(m_dict)

def init_all_pos_device():
    from mysite.iclock.models.model_device import Device ,DEVICE_POS_SERVER
    objs = Device.objects.filter(device_type__exact=DEVICE_POS_SERVER)
    for e in objs:
        init_ic_pos_device(e)

#获取pos_config.ini文件中的数据保持到redis
def update_redis_pos_device():
    from mysite.pos.pos_ic.ic_sync_model import Pos_Device
    pos_config = get_pos_site_file()
    
    pos_device_list = {}
    pos_device_list  = pos_config["Pos_Device"]
    pos_device_items = pos_device_list.items()
    if pos_device_items:
        for i in pos_device_items:
            print i[0].split(":")[1]
            print i[1].split("%")
            sn = i[0].split(":")[1]
            pos_log_stamp_id = i[1].split("%")[0]
            full_log_stamp_id = i[1].split("%")[1]
            allow_log_stamp_id = i[1].split("%")[2]
            pos_log_bak_stamp_id = i[1].split("%")[3]
            full_log_bak_stamp_id = i[1].split("%")[4]
            allow_log_bak_stamp_id = i[1].split("%")[5]
            
            m_dict = {}
            m_dict["sn"] = sn
            m_dict["pos_log_stamp_id"] = pos_log_stamp_id or 0
            m_dict["full_log_stamp_id"] = full_log_stamp_id or 0
            m_dict["allow_log_stamp_id"] = allow_log_stamp_id or 0

            m_dict["pos_log_bak_stamp_id"] = pos_log_bak_stamp_id or 0 
            m_dict["full_log_bak_stamp_id"] = full_log_bak_stamp_id or 0
            m_dict["allow_log_bak_stamp_id"] = allow_log_bak_stamp_id or 0
            m_dict["pos_dev_data_status"] = True
            
            m_dict["pos_all_log_stamp"] = 0
            m_dict["pos_log_stamp"] = 0
            m_dict["full_log_stamp"] = 0 
            m_dict["allow_log_stamp"] = 0 
            m_dict["last_activity"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            r_device=Pos_Device(sn)
            r_device.sets(m_dict)
    else:
        init_all_pos_device()
            
        
