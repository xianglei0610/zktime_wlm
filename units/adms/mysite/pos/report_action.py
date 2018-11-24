#coding=utf-8
from mysite.personnel.models import Employee,Department
from mysite.iclock.models.model_dininghall import Dininghall
from mysite.personnel.models.model_meal import Meal
from mysite.personnel.models.model_iccard import ICcard
from django.conf import settings
import os
import datetime
from django.core.cache.backends.filebased import CacheClass
from django.db import models
 
def tmpDir():
    ret=settings.LOG_DIR
    try:
        os.makedirs(ret)
    except: pass
    return ret

def dict_dept_obj():
    all_department = Department.all_objects.all().values_list('id','name')
    dept_dict = {}
    for obj in all_department:
        dept_dict[obj[0]] = obj[1]
    return dept_dict

def dict_dining_obj():
    all_dining = Dininghall.all_objects.all().values_list('id','name')
    dining_dict = {}
    for obj in all_dining:
        dining_dict[obj[0]] = obj[1]
    return dining_dict


def dict_meal_obj():
    all_meal = Meal.all_objects.all().values_list('id','name')
    meal_dict = {}
    for obj in all_meal:
        meal_dict[obj[0]] = obj[1]
    return meal_dict

def dict_card_type_obj():
    all_card_type = ICcard.all_objects.all().values_list('id','name')
    card_type_dict = {}
    for obj in all_card_type:
        card_type_dict[obj[0]] = obj[1]
    return card_type_dict

def dict_cash_type_obj():
    from mysite.pos.models import CarCashType 
    all_cash_type = CarCashType.all_objects.all().values_list('id','name')
    cash_type_dict = {}
    for obj in all_cash_type:
        cash_type_dict[obj[0]] = obj[1]
    return cash_type_dict

def dict_all_emp_obj():
    all_emp = Employee.all_objects.all().values_list('id','PIN','EName','DeptID_id')
    all_emp_dict = {}
    for obj in all_emp:
        emp_attribute = "%s_%s_%s"%(obj[1],obj[2],obj[3])
        all_emp_dict[obj[0]] = emp_attribute
    return all_emp_dict



def pos_save_tmp_file(name, object):
    CacheClass(tmpDir(), {"max_entries":1024}).set(name, object,3600)

def pos_load_tmp_file(name):
    return CacheClass(tmpDir(), {"max_entries":1024}).get(name)


def pos_save_datalist(data):
    fn="_tmp_%s"%id(data)
    head=data['heads']
    attrs=dict([(str(k), models.CharField(max_length=1024, verbose_name=head[k])) for k in data['fields']])
    admin_attrs={"read_only":True, "cache": False, "log":False}
    pos_save_tmp_file(fn, (attrs, admin_attrs,  data['data']))
    return fn


#消费报表导出临时文件存储，一次性导出所有记录
def save_pos_tmp_datalist(all_data):
    objdata={}
    heads={}
    objdata['data']=all_data['datas']
    objdata['fields']=all_data['fieldnames']
    for i  in  range(len(all_data['fieldnames'])):
           heads[all_data['fieldnames'][i]]=all_data['fieldcaptions'][i]
    objdata['heads']=heads
#    print "objdataobjdataobjdata==",objdata
    tmp_name=pos_save_datalist(objdata)
    return tmp_name
#    allr['tmp_name']=tmp_name


#
#select  *
#from (
#    select row_number()over(order by pos_time)temprownumber,
#	 (select count(*) from pos_icconsumerlist where pos_time>='2013-03-01 00:00:00' and pos_time <'2013-03-08 00:00:00' and user_id in (1)) as count,
#
#user_pin,user_name,dept_id,card,sys_card_no,money,balance,pos_model,     
#                 dining_id,meal_id,meal_data,dev_sn,dev_serial_num,card_serial_num,log_flag,            
#          create_operator,pos_time,convey_time 
#    from (
#select top 20 * from pos_icconsumerlist)test
#)tt
#where temprownumber>10 













