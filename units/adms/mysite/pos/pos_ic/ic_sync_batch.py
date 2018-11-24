# -*- coding: utf-8 -*-
import os

from ooredis import *
from redis.client import Lock
from ic_sync_store import load_pos_file
from mysite.pos.pos_constant import POS_DEAL_BAT_SIZE
import shutil
from django.conf import settings
def server_update():
    pass

class BatchObject(object):
    '''
    redis同步模型基类
    '''
    def __init__(self,oo,_isnew):
        self.__isnew = True
        self.isdel = False
        self.__oo = oo

class ic_pos_batch(object):
    def __init__(self):
        self.key = 'posbatch:datalist'
        self.__oo = List(self.key)
        self.store = String('posbatch:store')
        self.head_data = String('posbatch:head_data')
        self.lock = Lock(self.__oo._client, 'pos_ic_batch_lock', timeout=120)
    
    def get_is_sistributed(self):#分布式部署情况
        if (len(self.__oo)>0):
            self.lock.acquire()
            m_bat = self.__oo[:POS_DEAL_BAT_SIZE]
            del self.__oo[:POS_DEAL_BAT_SIZE]
            self.lock.release()
            m_rtn = [e for e in m_bat if e]
            return m_rtn
        else:
            self.lock.acquire()
            try:
                self.done()
            except:
#                 import traceback;traceback.print_exc()
                 pass
            self.set()
            self.lock.release()
            if (len(self.__oo)>0):
                self.lock.acquire()
                m_bat = self.__oo[:POS_DEAL_BAT_SIZE]
                del self.__oo[:POS_DEAL_BAT_SIZE]
                self.lock.release()
                m_rtn = [e for e in m_bat if e]
                return m_rtn
            else:
                return []
    
    def get(self):
        if (len(self.__oo)>0):
#            print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",len(self.__oo)
            m_bat = self.__oo[:POS_DEAL_BAT_SIZE]
            m_rtn = [e for e in m_bat if e]
            return m_rtn
        else:
            self.lock.acquire()
            try:
#                print "dddddddddddddddddddddddddddd",len(self.__oo)
                self.done()
            except:
                 pass
            self.set()
            self.lock.release()
            if (len(self.__oo)>0):
                m_bat = self.__oo[:POS_DEAL_BAT_SIZE]
                m_rtn = [e for e in m_bat if e]
                return m_rtn
            else:
                return []
    
    def del_oo_item(self):
        self.lock.acquire()
        del self.__oo[:POS_DEAL_BAT_SIZE]
        self.lock.release()
        return len(self.__oo)
        
    def set(self,file=None):
        try:
            m_store, m_head_data, m_list = load_pos_file(file)
            if m_store:
                self.store.set(m_store)
                self.head_data.set(m_head_data)
            if m_list:
                for e in m_list:
                    if e:
                        self.__oo.rpush(e)
        except:
            pass
#            import traceback;traceback.print_exc()
    
    def init_data(self):
        file = self.store.get()
        if file:
            del self.__oo[:]
            self.set(file)
            
    def done(self):
        file_path = self.store.get()
        file_name = file_path.split("/")[-1:][0].split("_")
        sn = file_name[0]
        f_dir = file_name[1][:8]
        cf_path=settings.WORK_PATH+"/files/zkpos/%s/"+f_dir+"/"
        cf_path=cf_path%sn  #数据备份路径
        if not os.path.exists(cf_path):
            os.makedirs(cf_path)
        shutil.copy(file_path,cf_path)
        os.remove(self.store.get())
    
    def get_head_data(self):
        return self.head_data.get()
