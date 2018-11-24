# -*- coding: utf-8 -*-
import os

from ooredis import *
from redis.client import Lock
from sync_store import load_att_file
from constant import ATT_DEAL_BAT_SIZE

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

class att_batch(object):
    def __init__(self):
        self.key = 'attbatch:datalist'
        self.__oo = List(self.key)
        self.store = String('attbatch:store')
        self.sn = String('attbatch:sn')
        self.lock = Lock(self.__oo._client, 'att_batch_lock', timeout=120)
        self.multi = False
        self.m_bat = None
        
    def get(self):
        if (len(self.__oo)>0):
            self.m_bat = self.__oo[:ATT_DEAL_BAT_SIZE]
            m_rtn = [e for e in self.m_bat if e]
            del self.__oo[:ATT_DEAL_BAT_SIZE]
            return m_rtn
        else:
            self.lock.acquire()
            try:
                self.done()
            except:
                pass
            self.set()
            self.lock.release()
            if (len(self.__oo)>0):
                self.m_bat = self.__oo[:ATT_DEAL_BAT_SIZE]
                m_rtn = [e for e in self.m_bat if e]
                del self.__oo[:ATT_DEAL_BAT_SIZE]
                return m_rtn
            else:
                return []
    
    def set(self,file=None):
        m_store, m_sn, m_list = load_att_file(file)
        if m_store:
            self.store.set(m_store)
            self.sn.set(m_sn)
        if m_list:
            for e in m_list:
                if e:
                    self.__oo.rpush(e)
    
    def init_data(self):
        file = self.store.get()
        if file:
            self.set(file)
            
    def done(self):
        os.remove(self.store.get())
    
    def get_sn(self):
        return self.sn.get()