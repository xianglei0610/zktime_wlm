# -*- coding: utf-8 -*-

import datetime

from mysite.personnel.models.model_emp import Employee,format_pin
from mysite.iclock.models.model_devcmd import DevCmd
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

def get_db_type():
    from django.db import connection
    db_select=1
    if 'mysql' in connection.__module__:#mysql 数据库
        db_select=1
    elif 'sqlserver_ado' in connection.__module__:#sqlserver 2005 数据库 
        db_select=2
    elif 'oracle' in connection.__module__: #oracle 数据库 
        db_select=3
    elif 'postgresql_psycopg2' in connection.__module__: # postgresql 数据库
        db_select=4
        
def appendDevCmdOld(dObj, cmdStr, Op, cmdTime=None):
        from mysite.iclock.models.model_devcmd import DevCmd
        try:
            #print cmdStr
            cmd=DevCmd(SN=dObj, CmdOperate=Op, CmdContent=cmdStr, CmdCommitTime=(cmdTime or datetime.datetime.now()))
            cmd.save(force_insert=True)
            return cmd.id
        except:
            import traceback;traceback.print_exc()

def append_dev_cmd(dObj, cmdStr, Op=None, cursor=None, cmdTime=None):
        appendDevCmdOld(dObj, cmdStr, Op, cmdTime)
        
        
def get_employee(pin, Device=None):
    '''
    根据给定员工PIN查找员工,若不存在就创建改PIN的员工
    '''
    s_pin = format_pin(pin)
    try:
        e=Employee.all_objects.get(PIN=s_pin)
        if e:
            e.IsNewEmp=False
            return e
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        if not settings.DEVICE_CREATEUSER_FLAG:
            return None
        e = Employee(PIN=s_pin, EName=pin)
        e.save()
        e.IsNewEmp=True
        return e