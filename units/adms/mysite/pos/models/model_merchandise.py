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
from dbapp.widgets import ZBase4IntegerWidget,ZBaseSmallIntegerWidget,ZBaseMoneyWidget
from mysite.utils import get_option
from mysite.pos.pos_id.pos_id_util import set_pos_info_record
class Merchandise(CachingModel):
    code = models.IntegerField(max_length=4,verbose_name=_(u'商品编号'),editable=True)
    name = models.CharField(max_length=10,verbose_name=_(u'商品名称'),editable=True)
    barcode = models.CharField(max_length=20,verbose_name=_(u'商品条码'),editable=False)
    money = models.DecimalField (max_digits=6,decimal_places=2,verbose_name=_(u'单价(元)'),null=False,blank=False,editable=True)
    rebate = models.IntegerField(max_length=3,default=0,verbose_name=_(u'折扣'),null=False,blank=False,editable=True)
    
    def __unicode__(self):
        return u"%s %s %s"% (self.code,self.name,self.money)
    
    def save(self,*args, **kwargs):
        super(Merchandise,self).save()
        cacheobj = Merchandise.objects.all()
        cache.set("Merchandise",list(cacheobj),TIMEOUT)
        set_pos_info_record()
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER)
            if dev:
                update_pos_device_info(dev,[self],"STOREINFO")

    def delete(self):
        super(Merchandise, self).delete()     
        cacheobj = Merchandise.objects.all()
        cache.set("Merchandise",list(cacheobj),TIMEOUT)
        set_pos_info_record()
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER)
            delete_pos_device_info(dev,[self],"STOREINFO")
            
    def data_valid(self, sendtype):
            try:
               self.code = str(int(self.code))
            except:
               raise Exception(_(u'编号只能为数字'))
            if int(self.code)<=0:
                raise Exception(_(u'编号不能为负数'))
            if int(self.code) == 0:
                raise Exception(_(u'编号不能为0'))
            if self.money == 0:
               raise Exception(_(u'单价不能为0'))
            try:
               self.money = str(int(self.money))
            except:
               raise Exception(_(u'金额只能为数字'))
            if int(self.money)< 0:
                raise Exception(_(u'金额不能为负数'))
            tmp = Merchandise.objects.filter(code=self.code)
            if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                raise Exception(_(u'编号: %s 已存在') % self.code)
            if int(self.rebate)< 0:
                raise Exception(_(u'折扣不能为负数'))
            if int(self.rebate)>=100:
                raise Exception(_(u'折扣范围为0-99之间正整数'))  
            
                                             
    class Admin(CachingModel.Admin):
                sort_fields=["code","money"]
                app_menu="pos"
                menu_group = 'pos'
                menu_index =34
                visible=False
                cache = 3600
                default_widgets = {
                'code':ZBase4IntegerWidget,
                'rebate':ZBaseSmallIntegerWidget,
                'money':ZBaseMoneyWidget,
                }
                default_give_perms = ["contenttypes.can_PosFormPage",]
                query_fields=['code','name','money']
                adv_fields=['code','name','money','rebate']
                list_display=['code','name','money','rebate']
                help_text = _(u'下述所填项目中，商品编号(1-9999)不能为空且不能重复，折扣范围为0-99之间正整数,如果需要使用商品消费模式，需将此资料下载到机器上，系统自动验证：')
    class Meta:
            verbose_name=_(u'商品资料')
            verbose_name_plural=verbose_name
            app_label='pos'
