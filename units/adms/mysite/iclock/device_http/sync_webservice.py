# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType

class Emp(LadonType):
    u"""￉ￌￆﾷ人员基本信息"""
    name = str
    card =str
    password = str

class EmployeeUpdate(object):
    """
    This service does the math, and serves as example for new potential Ladon users.
    """
    @ladonize(int,int,rtype=int)
    def add(self,a,b):
      """
      Add two integers together and return the result
    
      @param a: 1st integer
      @param b: 2nd integer
      @rtype: The result of the addition
      """
      return a+b
    
    @ladonize(int,int,rtype=str)
    def join(self,a,b):
      """
      Add two integers together and return the result
    
      @param a: 1st integer
      @param b: 2nd integer
      @rtype: The result of the addition
      """
      return '%s%s'%(a,b)
    
    @ladonize(int,int,rtype=list)
    def list_all(self,a,b):
      """
      Add two integers together and return the result
    
      @param a: 1st integer
      @param b: 2nd integer
      @rtype: The result of the addition
      """
      return [a,b]

    def update_info(self,pin,info_dic):
        pass
        return 0
    
    def update_area(self,pin,area_list):
        pass
        return 0
    
    def update_FingerPrint(self,pin,data):
        pass
        return 0
    
    def update_HeadPortrait(self,pin,data):
        pass
        return 0
    
    def update_face(self,pin,data):
        pass
        return 0