# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
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

from base.cached_model import CachingModel
from base.operation import Operation
from django import forms
from base.crypt import encryption,decryption
from mysite.utils import get_option
from mysite.pos.pos_utils import enc
from ooredis import *
FANAREA= (
('1',_(u'第1扇区')),
('2',_(u'第2扇区')),
('3',_(u'第3扇区')),
('4',_(u'第4扇区')),
('5',_(u'第5扇区')),
('6',_(u'第6扇区')),
('7',_(u'第7扇区')),
('8',_(u'第8扇区')),
('9',_(u'第9扇区')),
('10',_(u'第10扇区')),
('11',_(u'第11扇区')),
('12',_(u'第12扇区')),
('13',_(u'第13扇区')),
('14',_(u'第14扇区')),
('15',_(u'第15扇区')),
)
    ##消费系统参数表##
class PosParam(CachingModel):
    max_money=models.DecimalField(_(u'卡上最大可能余额'),max_digits=8,default=9999,decimal_places=0,)
    main_fan_area=models.CharField(_(u'发卡主扇区'),max_length=10,null=True,choices=FANAREA)
    minor_fan_area=models.CharField(_(u'发卡次扇区'),max_length=10,null=True,choices=FANAREA)
    system_pwd = models.CharField(_(u'系统密码'),max_length=20,default=123456,null=True)
    pwd_again = models.CharField(_(u'确认密码'),max_length=20,default=123456,null=True)
    
    def save(self,*args, **kwargs):
        CMD = "SET OPTION UseSection=%s\tBackSection=%s\tCardPass=%s\t\n" % (self.main_fan_area,self.minor_fan_area,enc(self.system_pwd))
        self.system_pwd = encryption(self.system_pwd)
        self.pwd_again = encryption(self.pwd_again)
        
        if PosParam.objects.count()== 1:#非初始化数据库的时候同步到redis
            redis_obj_param = Dict("pos_obj_param")
            redis_obj_param['main_fan_area'] = self.main_fan_area
            redis_obj_param['minor_fan_area'] = self.minor_fan_area
            redis_obj_param['system_pwd'] = self.system_pwd
            redis_obj_param['max_money'] = str(self.max_money)
        super(PosParam,self).save()
        from mysite.iclock.dataprocaction import appendDevCmdReturn
        from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
        device_list = Device.objects.filter(device_type = DEVICE_POS_SERVER)
        for dev in device_list:
            appendDevCmdReturn(dev,CMD)
    class Admin(CachingModel.Admin):
        disabled_perms=['add_posparam','dataexport_posparam','dataimport_posparam','delete_posparam']
        cancel_perms=[("change_posparam","browse_posparam"),]
        hide_perms=["browse_posparam"]
        menu_index=9
        cache=False
        visible = get_option("POS_IC")
        @staticmethod
        def initial_data(): 
            if PosParam.objects.count()==0:
                PosParam(max_money=9999,main_fan_area='1',minor_fan_area='2',system_pwd='123456',pwd_again='123456').save()
    def __unicode__(self):
        return ""    
    class Meta:
        app_label='pos'
        db_table = 'posparam'
        verbose_name=_(u'消费参数')
        verbose_name_plural=verbose_name
