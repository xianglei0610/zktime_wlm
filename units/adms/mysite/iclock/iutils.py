#!/usr/bin/env python
#coding=utf-8
from mysite.utils import *
from django.db import models
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import User, Permission
from django.utils import simplejson as json
from django.conf import settings
import datetime
import types
from django.db.models import Q

def contruct_q(ids,field_name = "pk__in"):
    u"超过一千个构造条件"
    if len(ids)>1000:
        query = []
        while ids:
            query.append(Q(**{field_name:ids[:900]}))
            ids = ids[900:]
        
        combine_query = query[0]
        for qq in query[1:]:
            combine_query |= qq
        return combine_query
    else:
        return  Q(**{field_name:ids})
    

def get_max_in(qs,ids,field_name = "pk__in"):
    u"超过一千个组织后的问题"
    if len(ids)>1000:
        query = []
        while ids:
            query.append(Q(**{field_name:ids[:900]}))
            ids = ids[900:]
        
        combine_query = query[0]
        for qq in query[1:]:
            combine_query |= qq
        qs = qs.filter(combine_query)
    else:
        qs = qs.filter(**{field_name:ids})
    return qs
    

def get_childs(depts,current_pk):
    u"堆栈方式递归，从depts中得到当前组织current_dept的所有父组织"
    store=[]
    stack=[]
    stack.append(current_pk)
    while len(stack)>0:
        pop_pk=stack.pop()
        if pop_pk!=current_pk:
            store.append(pop_pk)
        for elem in depts:
            if elem.parent_id==pop_pk:
                stack.append(elem.pk)
    return store

#def get_dept_child(depts,current_dept):
#    ret=[]
#    for e in depts:
#        if e.parent_id==current_dept.pk:
#            ret.append(e)
#            ret.extend(get_dept_child(depts,e))
#    return ret


def get_dept_child_obj(depts,current_dept):
    ret=[]
    for e in depts:
        if e.parent_id==current_dept.pk:
            ret.append(e)
            ret.extend(get_dept_child(depts,e))
    return ret

def get_child(qs,current_pk):
    u"从qs中查找current_pk的子记录"
    ret=[]
    for e in qs:
        if e.parent_id==current_pk:
            ret.append(e.pk)
            ret.extend(get_child(qs,e.pk))
    return ret


def get_list_children(qs,pks=[]):
    u"从qs中查找pks的所有子记录"
    ret = []
    for pk in pks:
        if type(pk) != types.IntType:
            pk = int(pk)
        ret.append( pk )
        ret.extend(get_childs(qs,pk))
        #ret.extend( get_child(qs,pk) )
    
    ret = list(set(ret))
    return ret


def get_dept_from_all(depts_ids = [],request = None):
    u"从所有组织中得到depts_ids的子集组织"
    from dbapp.datautils import filterdata_by_user
    from models import DeptAdmin, AreaAdmin, Department
    
    qs_all = Department.objects.all()
    if request:
        qs_all = filterdata_by_user(qs_all,request.user)
        
    ret  =  get_list_children(qs_all,depts_ids)
    return ret

def get_emps_from_dept(depts_id=[],request = None):
    from mysite.personnel.models.model_emp import Employee
    objs_dept = get_dept_from_all(depts_id,request)
    emps = get_max_in(Employee.objects.all(),objs_dept,"DeptID__in")
    #emps = Employee.objects.filter(DeptID__in = objs_dept)
    return emps

def get_area_from_all(area_ids = [],request = None):
    u"从所有区域中得到area_ids的子集区域"
    from mysite.iclock.models import Area
    from dbapp.datautils import filterdata_by_user
    qs_all = Area.objects.all()
    
    if request:
        qs_all = filterdata_by_user(qs_all,request.user)
    
    ret =  get_list_children(qs_all,area_ids)
    return ret
    

def userDeptList(user):
    from models import DeptAdmin, AreaAdmin, Department
    depts_id = list(DeptAdmin.objects.filter(user=user).values_list("dept_id",flat = True))
#    depts=Department.objects.filter(pk__in=depts_id)
#    depts_all=Department.objects.all()
#    result=[]
#    for e in depts:
#        result.append(e)
#        result.extend(get_dept_child(depts_all,e))
#    result=list(set(result))
#    if result:
#        return result
    return depts_id

def userAreaList(user):
    from mysite.iclock.models import Area
    from models import  AreaAdmin
    area_ids = list(AreaAdmin.objects.filter(user=user).values_list("area_id",flat = True))
#    areas=Area.objects.filter(pk__in=area_ids)
#    areas_all=Area.objects.all()
#    result=[]
#    for e in areas:
#        result.append(e)
#        result.extend(get_dept_child(areas_all,e))
#    result=list(set(result))
#    if result:
#        return result
    
    return area_ids



def getAllAuthChildDept(curid,request=None):
        from models import DeptAdmin, AreaAdmin, Department
        return curid
        result=[]
        if request==None or request.user.is_superuser:
                rs_dept = Department.objects.filter(id=int(curid))
                if len(rs_dept)>0:
                        child_dept_list=getChildDept(rs_dept[0])
                        child_dept_list.append(rs_dept[0])
                        result = [d.id for d in child_dept_list]
        else:
                rs_dept = Department.objects.filter(id=int(curid))
                if len(rs_dept)>0:
                        child_dept_list=getChildDept(rs_dept[0])
                        child_dept_list.append(rs_dept[0])
                        child_dept_list = [d.id for d in child_dept_list]
                        alluserdeptList=userDeptList(request.user)
                        dd=[]
                        for i in alluserdeptList:
                                dd.append(int(i.id))
                        
                        for t in child_dept_list:
                                if t in dd:
                                        result.append(t)
        return result

def userIClockList(user):
        depts=userDeptList(user)
        if depts:
                rs_SN = Device.objects.filter(DeptID__in=depts)
                return [row.SN for row in rs_SN]
        return []
# 获得部门的下级所有部门
def getChildDept(dept):
	child_list=[]
	dept.all_children(child_list)
	return child_list

def AuthedIClockList(user):
        depts=userDeptList(user)
        if depts:
#                rs_SN = iclock.objects.filter(DeptID__in=depts)
                rs_SN = IclockDept.objects.filter(dept__in=depts)
                len(rs_SN)
                return [row.SN.SN for row in rs_SN]
        return []


def getUserIclocks(user):
        return userIClockList(user)

def fieldVerboseName(model, fieldName):
        try:
                f = model._meta.get_field(fieldName)
                return f.verbose_name
        except:
                pass


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)

def dumps(data):
        return JSONEncoder().encode(data)

def loads(str):
        return json.loads(str, encoding=settings.DEFAULT_CHARSET)

def stamp_to_datetime(t):
    u"时间戳转换为时间"
    t = int(t)
    tm_sec =t % 60
    t/=60;
    tm_min=t % 60
    t/=60;
    tm_hour=t % 24
    t/=24;
    tm_mday=t % 31+1
    t/=31;
    tm_mon=t % 12
    t/=12;
    tm_year=t + 2000
    ts = datetime.datetime(
        year = tm_year,
        month = tm_mon+1,
        day = tm_mday,
        hour = tm_hour,
        minute = tm_min,
        second = tm_sec,
    )
    return ts

def datetime_to_stamp(dt):
    u"时间转换为时间戳"
    year = dt.year - 2000
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second
    return ((((year *12 + month-1)*31 + day-1)*24+hour)*60+minute)*60 +second