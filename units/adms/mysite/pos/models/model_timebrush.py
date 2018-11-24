#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

import datetime
import string
import os
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT

class TimeBrush(CachingModel):
    sn_name = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
    serialnum = models.IntegerField(_(u'设备流水号'),max_length=20,null=True,blank=True)
    carno = models.CharField(max_length=10,verbose_name=_(u'卡号'),editable=True)
    begintime = models.DateTimeField(verbose_name=_(u'开始时间'),null=True,blank=True,editable=True)
    endtime = models.DateTimeField(verbose_name=_(u'结束时间'),null=True,blank=True,editable=True)
    type = models.IntegerField(max_length=3,verbose_name=_(u'状态'),null=True,blank=True,editable=True)
    
    def __unicode__(self):
        return u"%s" %(self.carno)
    def save(self,*args, **kwargs):
        super(TimeBrush, self).save()
        if self.serialnum and self.sn_name:
            iskey="TimeBrush%s%s" %(self.serialnum,self.carno)
            cache.set(iskey,self,TIMEOUT)
#    def delete(self,*args, **kwargs):
#        super(TimeBrush, self).delete()
#        iskey="TimeBrush%s%s" %(self.serialnum,self.sn_name)
#        cache.delete(iskey)
    def update(self,*args, **kwargs):
       super(TimeBrush, self).update()
       iskey="TimeBrush%s%s" %(self.serialnum,self.sn_name)
       cache.set(iskey,self,TIMEOUT)
               
    
    class Admin(CachingModel.Admin):
                sort_fields=["carno","begintime","endtime"]
                visible=False
                app_menu="pos"
                menu_group = 'pos'
                menu_index =33
                cache = 3600
                query_fields=['carno','begintime','endtime']
                adv_fields=['carno','begintime','endtime']
                list_display=['carno','money','rebate']
    class Meta:
            verbose_name=_(u'计时消费表')
            verbose_name_plural=verbose_name
            app_label='pos'
