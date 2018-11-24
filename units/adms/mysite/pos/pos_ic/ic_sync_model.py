# -*- coding: utf-8 -*-
from ooredis import *
import time


class PosDeviceDoesNotExist(Exception):
    "The requested object does not exist"
    pos_variable_failure = True


class SyncObject(object):
    '''
    redis同步模型基类
    '''
    def __init__(self,oo,_isnew):
        self.__isnew = True
        self.isdel = False
        self.__oo = oo

    def __setattr__(self,name,value):
            self.__dict__[name] = value
              
    def get(self,field=None):
        '''
        从redis中获取该key的所有属性或者某个字段属性
        '''
        if field:
            return self.__oo[field]
        else:
            dev_r = self.__oo.getall()
            if dev_r:
                self.__isnew = False
                for e in dev_r.keys():
                    setattr(self,e,dev_r[e])
                return self
            else:
                raise PosDeviceDoesNotExist
            
    def isnew(self):
        return self.__isnew
    
    def delete(self):
        self.__oo.delete()
        
    def clean(self):
        '''计数器控制的对象的数据清空操作'''
#        for e in self.__oo.keys():
#            if e!='counter':
        del self.__oo
                
    def init_counter(self):
        self.__oo.incrby("counter",0)
        
    def pipecli(self):
        _client = self.__oo._client.pipeline()
        return _client
    #pipecli = property(_pipecli)
    
    def setcli(self,client):
        '''获取模型当前使用的redis客户端对象'''
        self.__oo._client = client
        
    def getoo(self):
        '''获取当前模型对应的ooredis对象'''
        return self.__oo


class Pos_Device(SyncObject):
    '''
    设备模型 
    存储格式:
        设备
            device:[sn]:data        [data_dict]
    '''
    def __init__(self,sn):
        self.sn = sn
        self.__oo = Dict("pos_device:%s:data"%sn)
        self.__isnew = True
        super(Pos_Device, self).__init__(self.__oo,self.__isnew)
               
    def __getattr__(self,name):
        '''当没有该时返回None'''
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            return None

    def set(self,field=None):
        '''设置设备相关属性 set()时触发服务器更新设备信息'''
        if field:
            self.__oo[field] = getattr(self,field)
        
            
    def sets(self,m_dic):
        self.__oo.sets(m_dic)
    
    def delete(self):
        try:
            super(Pos_Device, self).delete()
        except:
            pass
        
    def total(self):
        '''得到已注册的设备总数'''
        all_device_key = self.__oo._client.keys("pos_device:*:data")
        return len(all_device_key)
