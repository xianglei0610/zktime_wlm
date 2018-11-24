#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.iclock.tools import *
import string,os
import datetime
import time
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _

spLine="====================================="

def desSSRUser(upload_user):
        emps=[u"PIN,Name",spLine]
        #                typedef struct _User_{                //size:72
        #                        U16 PIN;                                //[:2]
        #                        U8 Privilege;                        //[2:3]                Privilege
        #                        char Password[8];                //[3:11]        Password
        #                        char Name[24];                        //[11:35]        EName
        #                        U8 Card[4];                                //[35:39]                                        //卡号码，用于存储对应的ID卡的号码
        #                        U8 Group;                                //[39:40]        AccGroup                //用户所属的分组
        #                        U16 TimeZones[4];                //[40:48]        TimeZones                //用户可用的时间段，位标志
        #                        char PIN2[24];                        //[48:]                PIN
        #                }GCC_PACKED TUser, *PUser;                        
        i, count = 0, len(upload_user) / 72        
        if not (count>0 and count*72==len(upload_user)):
                raise Exception()
        i_insert, i_update, i_rep = 0, 0, 0
        while i < count:
                buf = upload_user[i*72:(i+1)*72]
                pin = ord(buf[0])+ord(buf[1])*256
                if pin:
                        pin= format_pin(getStr_c_decode(buf[48:]))
                        ename=getStr_c_decode(buf[11:35])
                        Password = getStr_c_decode(buf[3:11])
                        emps.append(u"%s,%s"%(pin, ename))
                i += 1
        emps.append(spLine)
        emps.append(u"total %d"%i);
        return u"\r\n".join(emps)

def desSSRAttLog(data):
#//40byte
#typedef struct _AttLog_{
#        U16 PIN;                         [:2]
#        U8 PIN2[24];                [2:26]
#        BYTE verified;                [26:27]
#        time_t time_second;[27:31]
#        BYTE status;                [31:32]
#        U32 workcode;                [32:36]
#        BYTE reserved[4];        [36:]
#}GCC_PACKED TAttLog,*PAttLog;
        
        emps=[u"PIN,Time,Verification,State",spLine]
        i, count = 0, len(data) / 40        
        if not (count>0 and count*40==len(data)):
                raise Exception()
        i_insert, i_update, i_rep = 0, 0, 0
        while i < count:
                buf = data[i*40:(i+1)*40]
                pin= format_pin(getStr_c_decode(buf[2:26]))
                timeStr=decodeTime(buf[27:31])
                verify = ord(buf[26])
                status = ord(buf[31])
                emps.append(u"%s,%s,%s,%s"%(pin, timeStr, verify, status))
                i += 1
        emps.append(spLine)
        emps.append(_(u'%d attendance record(s).') % i);
        return u"\r\n".join(emps)        

def desOpLog(data):
#//16B
#typedef struct _OPLog_{
#    U16 Admin;      //2
#    BYTE OP;        //2
#    time_t time_second; //4
#    U16 Users[4];       //2*4
#}TOPLog, *POPLog;
#
        recSize=16
        emps=[u"Administarator, Time, Operation, Objects(1,2,3,4)",spLine]
        i, count = 0, len(data) / recSize        
        if not (count>0 and count*recSize==len(data)):
#                print "ERROR Size: ", count,"*",recSize,"!=",len(data)
                raise Exception()
        while i < count:
                buf = data[i*recSize:(i+1)*recSize]
                pin = ord(buf[0])+ord(buf[1])*256
                op = OpName(ord(buf[2]))
                timeStr=decodeTime(buf[4:8])
                emps.append(u"%s, %s, %s, [%s,%s,%s,%s]"%(pin, timeStr, op, 
                                        ord(buf[8])+ord(buf[9])*256, ord(buf[10])+ord(buf[11])*256, 
                                        ord(buf[12])+ord(buf[13])*256, ord(buf[14])+ord(buf[15])*256))
                i += 1
        emps.append(spLine)
        emps.append(u"Total %d"%i);
        return u"\r\n".join(emps)

