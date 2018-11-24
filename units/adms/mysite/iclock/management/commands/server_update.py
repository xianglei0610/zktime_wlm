# -*- coding: utf-8 -*-
import os
import time
import datetime
import sys

from django.core.management.base import BaseCommand
from mysite.personnel.models import Employee
from mysite.personnel.models.model_emp import format_pin 
from mysite.iclock.models import Device,Area
from django.db import IntegrityError ,connections
from mysite.utils import get_option 

conn = connections['default']
def set_user(emp_dict,emp):
	"""
		将字典转换为人员对象
	"""
	if emp_dict.has_key("PIN"):
		emp.PIN = format_pin(emp_dict.get("PIN"))
		
	if emp_dict.has_key("AccGroup") and emp_dict.get("AccGroup"):
		m_val = emp_dict.get("AccGroup")
		if m_val!='None':
		  emp.AccGroup = m_val
		
	if emp_dict.has_key("EName"):
		emp.EName = u"%s"%emp_dict.get("EName")
						
	if emp_dict.has_key("Privilege") and emp_dict.get("Privilege"):
		m_val = emp_dict.get("Privilege")
		if m_val!='None':
			emp.Privilege =m_val
		
	if emp_dict.has_key("TimeZones"):
		m_val = emp_dict.get("TimeZones")
		if m_val!='None':
			emp.TimeZones = m_val

	if emp_dict.has_key("Password"):
		from base.crypt import encryption
		emp.Password = encryption(emp_dict.get("Password"))
	return emp

def set_dev(dev_dict,dev,new=False):
    '''
    将字典转化为设备对象
    '''
    for key,value in dev_dict.items():
        if key=="area":
			if new:
			    value = Area.objects.get(pk=value)
			    dev.area = value
			continue
        try:
        	if  key !="alias" or  new:
        	   setattr(dev, key, str(value) )
        except:
        	import traceback
        	traceback.print_exc()
        	continue
    return dev
   
def set_card(emp,cardNO):
	from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP
	from mysite.personnel.models.model_iccard import ICcard
	if get_option("POS") or cardNO == "0" or (not cardNO.strip()) :
		return 
	try:
		tmp_issuecare = IssueCard.objects.filter(UserID=emp)
		if tmp_issuecare:#编辑
			if  tmp_issuecare[0].cardno <> cardNO:
#				old_card = tmp_issuecare[0].cardno
#				tmp_issuecare[0].cardstatus = CARD_STOP  #停用旧卡号
				tmp_issuecare[0].cardno = cardNO
				tmp_issuecare[0].save(force_update=True)
		else:
			issuecard = IssueCard()
			issuecard.UserID = emp
			issuecard.cardno = cardNO
			issuecard.issuedate = datetime.datetime.now().strftime("%Y-%m-%d")
			try:
				issuecard.save()
			except IntegrityError:
				conn._rollback()
				conn.close()
	except:
			import traceback
			traceback.print_exc()
			
def save_area(eid,epin):
    '''
    将人员的redis区域信息保存到数据库
    '''
    from mysite.iclock.models import Area
    from base.sync_api import get_area
    from mysite.personnel.models.model_emp import device_pin
    from mysite.sql_utils import p_query,p_execute
    pin = device_pin(epin)
    m_list = get_area(pin)
    delete_sql="""
      delete  userinfo_attarea where employee_id = %s
    """
    insert_sql = """
        if not exists(select id from userinfo_attarea where employee_id = %(employee_id)s and area_id= %(area_id)s) 
        insert into userinfo_attarea (employee_id,area_id) values(%(employee_id)s,%(area_id)s)
    """
    sqlList = []
    p_execute(delete_sql%eid)
    for a in m_list:
        p_execute(insert_sql%{'employee_id':eid,'area_id':a})

def update_user(emps):
	"""
		更新服务器人员信息,使之与redis 同步
	"""
	if emps:
		pin_dict = dict([(format_pin(e.get("PIN")),e) for e in emps])
		emp_objs = Employee.all_objects.filter(PIN__in=pin_dict.keys()) 
		db_emps_dict = emp_objs and dict([(e.PIN,e) for e in emp_objs]) or {}
		
		param_pins = pin_dict.keys()   # redis 中存在的人员PIN
		db_pins = db_emps_dict.keys()  # 数据库中存在的人员
		
		insert_emps = set(param_pins) - set(db_pins)
		update_emps = set(db_pins)
		for e in insert_emps:
			if pin_dict.has_key(e):
				emp_dict = pin_dict.get(e)
				emp = Employee()
				emp = set_user(emp_dict,emp)
				emp.DeptID_id = 1
				emp.from_dev = True
				try:
					super(Employee,emp).save()
				except IntegrityError:
					conn._rollback()
					conn.close()
					db_emps_dict[e]=Employee.all_objects.filter(PIN__exact=format_pin(emp_dict.get("PIN")))[0] 
					update_emps.add(e)
					continue
				#保存卡   
				if emp_dict.has_key("Card"):
					if emp_dict.get("Card"):
						set_card(emp,emp_dict.get("Card"))	
				 
				'''保存区域'''
				save_area(emp.id,emp.PIN)
		for e in update_emps:
			if db_emps_dict.has_key(e) and pin_dict.has_key(e):
				emp_dict = pin_dict.get(e)
				emp = db_emps_dict.get(e)
				emp = set_user(emp_dict,emp)
				emp.from_dev = True
				super(Employee,emp).save()	
				#保存卡 
				if emp_dict.has_key("Card"):
					if emp_dict.get("Card"):
						set_card(emp,emp_dict.get("Card"))	
				'''更新'''
				save_area(emp.id,emp.PIN)
	
def update_device(devs):
	"""
		更新服务器数据库 设备信息,使之与redis 同步
	"""
	if devs:
		SN_dict = dict([(d.get("sn"),d) for d in devs])
		
		dev_objs = Device.objects.filter(sn__in=SN_dict.keys()) 
		len(dev_objs)
		db_devs_dict = dev_objs and dict([(d.sn,d) for d in dev_objs]) or {}
		
		param_SN = SN_dict.keys()   # redis 中存在的设备SN
		db_SN = db_devs_dict.keys()  # 数据库中存在的设备SN
		
		insert_devs = set(param_SN) - set(db_SN)
		update_devs = set(db_SN)
		
		for d in insert_devs:
			if SN_dict.has_key(d):
				dev_dict = SN_dict.get(d)
				dev = Device()
				dev = set_dev(dev_dict,dev,new=True)
				dev.from_dev = True
				try:
					super(Device,dev).save(log_msg=False)
				except IntegrityError:
					conn._rollback()
					conn.close()	 
					update_devs.add(d)
					continue
		
		for d in update_devs:
			if db_devs_dict.has_key(d) and SN_dict.has_key(d):
				dev_dict = SN_dict.get(d)
				dev = db_devs_dict.get(d)
				dev = set_dev(dev_dict,dev)
				dev.from_dev = True
				super(Device,dev).save(log_msg=False)		

def clean_cache():
	from base.sync_api import get_device_status, clean_cache_data
	dev_objs = Device.objects.all()
	for obj in dev_objs:
		if not get_device_status(obj.sn):
			clean_cache_data(obj.sn)
