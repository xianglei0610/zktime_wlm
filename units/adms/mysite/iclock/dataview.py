#coding=utf-8
from models.model_device import Device 

from mysite.personnel.models.model_dept import  Department
from tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from exceptions import AttributeError
from django.core.cache import cache
import string,os
import datetime
import time
from dbapp.utils import *
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required,permission_required
from django import forms
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import User, Permission
from reb        import *
from django.conf import settings
from cab import *
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from dbapp.datautils import *
from dbapp import dataviewdb, data_edit
from dbapp.modelutils import getDefaultJsonDataTemplate, GetModel
from django.template import add_to_builtins
from dataprocaction import *
#from dbapp.additionfile import save_model_file, save_model_image_from_request

from django.template import add_to_builtins
add_to_builtins('mysite.iclock.templatetags.tags')

def DataPostCheck(sender, **kwargs):
        from mysite.personnel.models.model_emp import device_pin,Employee
        from mysite.iclock.models.modelproc  import getEmpCmdStr
        oldObj=kwargs['oldObj']
        newObj=kwargs['newObj']
        request=sender
        if isinstance(newObj, Employee):
                try:
                        for i in request.FILES: print i
                        if "fileUpload" in request.FILES:
                                from dbapp.additionfile import save_model_image_from_request
                                f=device_pin(newObj.PIN)+".jpg"
                                print "upload:", f
                                save_model_image_from_request(request, "fileUpload", Employee, f)
                except:
                        errorLog()
                        pass #errorLog()
                if oldObj:  #修改人员数据
                        old_dev=oldObj.device()
                        if int(oldObj.PIN)<>int(newObj.PIN): #changed the PIN, 需要把原来的PIN从设备中删除
                                if old_dev:
                                                delEmpFromDev(None, oldObj, None)
                dev=newObj.device()
                if dev: #需要把新的人员指纹传送到设备上
                        if not oldObj or (int(oldObj.PIN)<>int(newObj.PIN)): #changed the PIN, 需要把指纹等都传送一遍
                                append_emp_to_dev(dev, newObj)
                        else:                                                  #只需要传送人员信息           
                                cmdStr=getEmpCmdStr(newObj)
                                append_dev_cmd(dev, cmdStr)
                                backDev=dev.backup_device()
                                if backDev: #把新的数据传送到登记考勤机的备份机上
                                        append_dev_cmd(backDev, cmdStr)                
        elif isinstance(newObj, Device):
                append_dev_cmd(newObj, "CHECK") #命令设备读取服务器上的配置信息
                sn=request.POST["BackupDev"]
                if oldObj is not None:
                        oldsn=oldObj.BackupDev
                        if sn and oldsn!=sn: #设置了一个新的备份设备，则把该设备登记的指纹复制到新的备份设备上
                                copyDevEmpToDev(get_device(sn), oldObj)
                if sn!=newObj.BackupDev:
                        newObj.BackupDev = sn
                        newObj.save()

data_edit.post_check.connect(DataPostCheck)

def checkReboot(iclocks):
        if not settings.REBOOT_CHECKTIME: return
        iclocks=iclocks.filter(LastActivity__lt=datetime.datetime.now()-datetime.timedelta(0,settings.REBOOT_CHECKTIME*60))
        ips=updateLastReboot(iclocks)
        rebDevs(ips)

def create_dept_page(cc, querySet):
        from mysite.personnel.models.depttree import DeptTree
        ds=DeptTree(querySet)
        l=[d[0] for d in ds.tree]
        c=len(l)
        limit=cc['limit']
        offset=cc['offset']
        minIndex=(offset-1)*limit
        l=l[minIndex:minIndex+limit]
        cc['latest_item_list']=l
        cc['page_count']=(c+limit-1)/limit
        cc['item_count']=len(l)

def iclockPaginator(sender, **kwargs):
        request=kwargs['request']
        dataModel=kwargs['dataModel']
        querySet=kwargs['querySet']
        if dataModel==Department:
                create_dept_page(sender, querySet)
                return True
        if dataModel==Device:
                checkReboot(querySet)
                state = int(request.REQUEST.get(STATE_VAR, -1))
                if state==-1:
                        return False
                pgList=[]
                cc=sender
                offset=cc['offset']
                limit=cc['limit']
                count=0
                curCount=0;
                minIndex=(offset-1)*limit
                for i in querySet:
                        if i.get_dyn_state()==state:
                                curCount+=1
                                count=len(pgList)
                                if curCount>minIndex and count<limit:
                                        pgList.append(i)
                pageCount=curCount/limit
                if pageCount*limit<curCount: pageCount+=1
                count=curCount
                cc['latest_item_list']=pgList
                cc['from']=(offset-1)*limit+1
                cc['page']=offset
                cc['item_count']=count
                cc['page_count']=pageCount
                return True
        return False

dataviewdb.on_list_paginator.connect(iclockPaginator)        

def detail_resplonse(sender, **kargs):
        from dbapp.templatetags import dbapp_tags
        from mysite.personnel.models.model_emp import Employee
        if kargs['dataModel']==Employee:
                form=sender['form']
                instance=sender['instance']
                if        instance and instance.pk:
                        form.object_photo=dbapp_tags.thumbnail_url(instance, 'pin')

data_edit.pre_detail_response.connect(detail_resplonse)        

