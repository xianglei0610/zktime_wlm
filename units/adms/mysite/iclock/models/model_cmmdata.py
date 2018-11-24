# -*- coding: utf-8 -*-
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from mysite.personnel.models import Department
from base.cached_model import CachingModel
from model_device import Device, DeviceForeignKey
from base.operation import OperationBase, Operation, ModelOperation
from django.db import models, connection
import datetime
import traceback
from model_devoperate import OperateCmd
#class CmmData(CachingModel):	
#	receive_time = models.DateTimeField( verbose_name=_(u'命令创建时间'), null=True, blank=True)
#	cmm_type=models.SmallIntegerField(verbose_name=_(u'命令类型'),default=1,blank=False,null=False,choices=CMM_TYPE)
#	cmm_desc=models.CharField(verbose_name=_(u'命令描述'),max_length=200,default='',blank=True,null=True)
#	receive_data = models.TextField(verbose_name=_(u'命令数据'))	
#	commit_time =  models.DateTimeField( verbose_name=_(u'命令处理完成时间'), null=True, blank=True)	
#	process_count=models.SmallIntegerField(verbose_name=_(u'处理次数'),default=0)
#	success_flag=models.SmallIntegerField(verbose_name=_(u'处理标志'),default=0,choices=SUCCESS_FLAG)
#	
#	class Admin(CachingModel.Admin):
#		list_display=('create_operator','receive_time','cmm_type','cmm_desc','commit_time','process_count','success_flag')
#		query_fields=('cmm_type','process_count','success_flag')
#		read_only=True
#	class Meta:
#		app_label='iclock'
#		verbose_name=_(u'通信命令详情')
#		
#	class _delete(Operation):
#		visible=False
#		def action():
#			pass	
#		
		
		
def pos_gen_device_cmmdata(device,data,errfile=None):
	from mysite import settings
	import datetime
	import os
	desc=""
	tnow=datetime.datetime.now()
	pos_log_path = settings.C_ADMS_PATH%"zkpos/%s"
	err_log_path = settings.WORK_PATH+"/files/zkpos/%s"
	m_f=("000"+str(tnow.microsecond/1000))[-3:]
	if errfile:
		filename=device.sn+"_"+tnow.strftime("%Y%m%d%H%M%S")+m_f+"_errorfile.txt"
		desc=desc+u"%s"%_(u'----重新处理')
		path=err_log_path%device.sn+"error/%s/"%tnow.strftime("%Y%m%d")
	else:	
		filename=tnow.strftime("%Y%m%d%H%M%S")+m_f+".txt"
		path=pos_log_path%device.sn+"new/"
	#path=settings.APP_HOME+"/tmp/upload/"+device.sn+"/"+tnow.strftime("%Y%m%d")+"/"
#	print "path-----:%s"%path
	try:
		if not os.path.exists(path):
			os.makedirs(path)
		filename=path+filename
		upfile=file(filename,"a+")
		upfile.write(data)
		upfile.close()
	except Exception ,e:		
		print traceback.print_exc()
		raise u"%s"%e

#	data="cmmsubtype=1\t;dev=%s\t;data=%s"%(device.pk,filename)
#	c=OperateCmd()
#	c.cmm_system=2
#	c.CmdCommitTime=datetime.datetime.now()
#	c.cmm_type=1
#	c.CmdContent=desc
#	c.receive_data=data
#	c.save()
	#return c
	return

		
def gen_device_cmmdata(device,data,errfile=None):
	from mysite import settings
	import datetime
	import os
#	if data.find("oplog_stamp")>0:
#		if data.find("USER")>0:
#			desc=u"%s"%_(u'上传用户信息')
#		elif data.find("FP")>0:
#			desc=u"%s"%_(u'上传用户指纹')
#		else:
#			desc=u"%s"%_(u'上传日志')
#	elif data.find("log_stamp"):
#		desc=u"%s"%_(u'上传考勤记录')
#	else:		
#		desc=u"%s"%_(u'上传照片')
	desc=""
	tnow=datetime.datetime.now()
	m_f=("000"+str(tnow.microsecond/1000))[-3:]
	if errfile:
		filename=tnow.strftime("%Y%m%d%H%M%S")+m_f+"_errorfile.txt"
		desc=desc+u"%s"%_(u'----重新处理')
	else:	
		filename=tnow.strftime("%Y%m%d%H%M%S")+m_f+".txt"
	#path=settings.APP_HOME+"/tmp/upload/"+device.sn+"/"+tnow.strftime("%Y%m%d")+"/"
	path=settings.C_ADMS_PATH%device.sn
	path=path+"new/"
	#print "data:%s"%data
	try:
		if not os.path.exists(path):
			os.makedirs(path)
		filename=path+filename
		upfile=file(filename,"a+")
		upfile.write(data)
		upfile.close()
	except Exception ,e:		
		print traceback.print_exc()
		raise u"%s"%e

#	data="cmmsubtype=1\t;dev=%s\t;data=%s"%(device.pk,filename)
#	c=OperateCmd()
#	c.cmm_system=2
#	c.CmdCommitTime=datetime.datetime.now()
#	c.cmm_type=1
#	c.CmdContent=desc
#	c.receive_data=data
#	c.save()
	#return c
	return
def adj_device_cmmdata(device,area,getstring=False):
	data="cmmsubtype=2\t;dev=%s\t;area=%s"%(device.pk,area.pk)
	if getstring:
		return data
	c=OperateCmd()
	c.cmm_system=2
	c.CmdCommitTime=datetime.datetime.now()
	c.CmdContent=_(u'调整设备:%(f)s 的区域至:%(f2)s')%{'f':u"%s"%device,'f2':area.areaname}
	c.cmm_type=2
	c.receive_data=data
	c.save()
def sync_for_server(device,area,desc=""):
	'''
	考勤：同步服务器数据到设备
	'''
	data="cmmsubtype=4\t;dev=%s\t;area=%s"%(device.pk,area.pk)
	c=OperateCmd()
	c.cmm_system=2
	c.CmdCommitTime=datetime.datetime.now()
	c.CmdContent=_(u'同步服务器数据到设备:%(f)s ')%{'f':u"%s"%device}
	c.cmm_type=2
	c.receive_data=data
	c.save()
	
def save_devicearea_together(devlist,d_area,datalist):
	devdesc=",".join([u"%s"%u for u in devlist])
	if len(devdesc)>50:
		devdesc=devdesc[:47]+"..."
	areadesc=",".join([u"%s"%u for u in d_area])
	if len(areadesc)>50:
		areadesc=areadesc[:47]+"..."	
	c=OperateCmd()
	c.cmm_system=2
	c.CmdCommitTime=datetime.datetime.now()
	c.cmm_type=2
	c.CmdContent=_(u'调整设备:%(f)s 到区域:%(f2)s')%{'f':devdesc,'f2':areadesc}
	c.receive_data="\n\r".join(datalist)
	c.save()
	
def del_user_cmmdata(user,getstring=False):	
	if getstring:
		return adj_user_cmmdata(user,user.attarea.all(),[],getstring)
	desc=_(u'删除用户:%s')%(user)
	adj_user_cmmdata(user,user.attarea.all(),[],getstring,desc)
		
def del_user_together(userlist,datalist):	

	desc=_(u'删除用户:%s')%(",".join([u"%s"%u for u in list(userlist)]))
	if len(desc)>50:
		desc=desc[:47]+"..."
	save_userarea_together(userlist,[],datalist,desc)

def adj_user_cmmdata(user,s_area,d_area,getstring=False,desc=None):
	if not isinstance(user,list):
		user=[user]
	#print user
	s_dev=Device.objects.filter(area__in=list(s_area)).filter(device_type=1)
	d_dev=Device.objects.filter(area__in=list(d_area)).filter(device_type=1)

	data="cmmsubtype=3\t;user=%s\t;s_dev=%s\t;d_dev=%s"%(",".join(["%s"%u.pk for u in user]),
											",".join(["%s"%s.pk for s in s_dev]),
											",".join(["%s"%d.pk for d in d_dev]))
	if getstring:
		return data
	c=OperateCmd()
	c.cmm_system=2
	c.CmdCommitTime=datetime.datetime.now()
	if desc:
		c.CmdContent=u"%s"%desc
	else:
		c.CmdContent=_(u'调整用户:%(f)s 到区域:%(f2)s')%{'f':u"%s"%user[0],'f2':",".join([u"%s"%u for u in d_area])}
		
	c.cmm_type=2
	c.receive_data=data
	c.save()
	
def save_userarea_together(userlist,d_area,datalist,desc=None):
	userdesc=",".join([u"%s"%u for u in userlist])
	if len(userdesc)>50:
		userdesc=userdesc[:47]+"..."
	areadesc=",".join([u"%s"%u for u in d_area])
	if len(areadesc)>50:
		areadesc=areadesc[:47]+"..."	
	c=OperateCmd()
	c.cmm_system=2
	c.CmdCommitTime=datetime.datetime.now()
	c.cmm_type=2
	if desc:
		c.CmdContent==u"%s"%desc
	else:
		c.CmdContent=_(u'调整用户:%(f)s 到区域:%(f2)s')%{'f':userdesc,'f2':areadesc}
	c.receive_data="\n\r".join(datalist)
	c.save()
	
def parse_cmmdata(cmmdata):
	'''
	将操作命令转化为设备命令，主要用于会产生大批量设备命令的操作
	'''
	from model_device import Device
	from mysite.personnel.models import Employee
	from mysite.personnel.models import Area
	from mysite.iclock.device_http.device_view import write_data
	from mysite.iclock.models.model_devcmd import DevCmd
	#from dev_comm_operate import sync_delete_all_data, sync_set_all_data,sync_delete_user,sync_set_user
	from mysite.iclock.constant import REALTIME_EVENT, DEVICE_POST_DATA
	
	if cmmdata.cmm_type==1:
		cmm=cmmdata.receive_data.split("\t;",1)
		if cmm[0]=="cmmsubtype=1":
			tmp=cmm[1].split("\t;",1)
			snid=tmp[0].split("=")[1]
			
			fn=tmp[1].split("=")[1]
			wf=file(fn,"r+")
			writedata=wf.read()
			wf.close()
			
			dev=Device.objects.get(pk=snid)
			if writedata:
				write_data(writedata,dev,cmmdata)
			
	elif cmmdata.cmm_type==2:

		cmm=cmmdata.receive_data.split("\t;",1)
		if cmm[0]=="cmmsubtype=2":
			alldata=cmmdata.receive_data.split("\n\r")
			for cmm in alldata:			
				cmm=cmm.split("\t;",1)	
				tmp=cmm[1].split("\t;",1)
				snid=tmp[0].split("=")[1]
				dev=Device.objects.get(pk=snid)
				if dev:
					cmd=DevCmd(SN=dev, CmdOperate=cmmdata, CmdContent="CLEAR DATA", CmdCommitTime=datetime.datetime.now())
					cmd.save(force_insert=True)
					
					dev.set_all_data(cmmdata)
		if cmm[0]=="cmmsubtype=4":#同步所有数据到设备
			alldata=cmmdata.receive_data.split("\n\r")
			for cmm in alldata:			
				cmm=cmm.split("\t;",1)	
				tmp=cmm[1].split("\t;",1)
				snid=tmp[0].split("=")[1]
				dev=Device.objects.get(pk=snid)
				if dev:			
					dev.set_all_data(cmmdata)
					
		if cmm[0]=="cmmsubtype=3":	
			alldata=cmmdata.receive_data.split("\n\r")

			for cmm in alldata:
				cmm=cmm.split("\t;",1)	
				tmp=cmm[1].split("\t;")
				#print "Tmp:%s"%tmp
				user=tmp[0].split("=")[1].split(",")
				s_dev=tmp[1].split("=")[1].split(",")
				d_dev=tmp[2].split("=")[1].split(",")

				user=Employee.objects.filter(pk__in=user)
				if s_dev[0]:					
					devset=Device.objects.filter(pk__in=s_dev)			
					#sync_delete_user(dev,user)
					for dev in devset:
					    dev.delete_user(user, cmmdata)					    
					
				if d_dev[0]:
					devset=Device.objects.filter(pk__in=d_dev)		
		
					#sync_set_user(dev,user)
					for dev in devset:
						dev.set_user(user,  cmmdata, "")
						dev.set_user_fingerprint(user, cmmdata)
						dev.set_user_face(user, cmmdata)  #----下发人脸模板	
				
	else:
		pass
	pass


def process_writedata():
	import traceback
	import time	
	cur_obj=None  #当前对象
	cur_id=0
	start =time.time()
	while True:
		if cur_id==0:
			try:                
				c=OperateCmd.objects.filter(success_flag=0,cmm_system__exact=2).order_by("id")
				if c:
					cur_obj=c[0]
					cur_id=cur_obj.pk            
				else:
					#print "No data"
					cur_obj=None
					time.sleep(5)				
			except:
				cur_obj=None
		try:
			try:
				cur_obj=OperateCmd.objects.get(pk=cur_id)
			except:
				cur_obj=None    
			if cur_obj:
				if cur_obj.cmm_system==2:
					try:                       
						parse_cmmdata(cur_obj)

						cur_obj.commit_time=datetime.datetime.now()
						cur_obj.success_flag=1
						cur_obj.process_count=cur_obj.process_count+1
						cur_obj.save()                        
					except:	
						cur_obj.process_count=cur_obj.process_count+1
						cur_obj.commit_time=datetime.datetime.now()
						cur_obj.success_flag=2
						cur_obj.save()
					cur_id=cur_id+1
					time.sleep(1)
				else:
					cur_id=cur_id+1
			else:
				time.sleep(5)	
		except:
			pass
		
		end=time.time()
		if end-start>30*60:
			break
		
