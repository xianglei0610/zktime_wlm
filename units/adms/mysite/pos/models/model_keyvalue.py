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
from dbapp.widgets import ZBase5IntegerWidget,ZBaseSmallIntegerWidget,ZBaseMoneyWidget,ZBaseSmallIntegerWidget
from mysite.utils import get_option
from mysite.iclock.models.model_device import DeviceManyToManyFieldKey
from dbapp import data_edit
from mysite.pos.pos_id.pos_id_util import set_pos_info_record
class KeyValue(CachingModel):
    code = models.IntegerField(verbose_name=_(u'键值编号'),editable=True)
    money = models.DecimalField (max_digits=6,decimal_places=2,verbose_name=_(u'单价(元)'),null=False,blank=False,editable=True)
    use_mechine = DeviceManyToManyFieldKey(verbose_name=_(u'可用设备'), blank=True, null=True)#从设备登记中获取
    def __unicode__(self):
        return u"%s %s" %(self.code,self.money)
    def save(self,*args, **kwargs):
        is_new = False #是否新增 
        if not self.pk:
            is_new = True
        super(KeyValue,self).save()
        cacheobj = KeyValue.objects.all()
        cache.set("KeyValue",list(cacheobj),TIMEOUT)
        set_pos_info_record()
        if not is_new and get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
            if dev:
                delete_pos_device_info(dev,[self],"PRESSKEY")
            
        
    def delete(self,*args, **kwargs):
        super(KeyValue,self).delete()
        cacheobj = KeyValue.objects.all()
        cache.set("KeyValue",list(cacheobj),TIMEOUT)
        set_pos_info_record()
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
            delete_pos_device_info(dev,[self],"PRESSKEY")
        
        
#        help_text = _(u"删除选定记录") #删除选定的记录
#        verbose_name = _(u"删除")
#        visible = True
#        def action(self):
#            cacheobj = cache.get("KeyValue")
#            if cacheobj:
#                for obj in cacheobj:
#                    if self.objects.code = obj.code:
#                        cacheobj.remove(obj)
#                cache.set("KeyValue",list(cacheobj),TIMEOUT)
#            else:
                
    def get_device(self):
           return u",".join([a.sn for a in self.use_mechine.all()])
    
    def data_valid(self, sendtype):
            try:
               self.code = str(int(self.code))
            except:
               raise Exception(_(u'编号只能为数字'))
            if int(self.code)< 0:
                raise Exception(_(u'编号不能为负数'))
            if self.code == "0":
                raise Exception(_(u'编号不能为0'))
            if self.money == 0:
               raise Exception(_(u'单价不能为0'))
            
            if int(self.code) >100:
                raise Exception(_(u'编号范围只能在1-99'))
            
            tmp = KeyValue.objects.filter(code=self.code)
            if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                raise Exception(_(u'编号: %s 已存在') % self.code)
            try:
                self.money = str(int(self.money))
            except:
                raise Exception(_(u'金额只能为数字'))
            if int(self.money)< 0:
             raise Exception(_(u'金额不能为负数'))
                                                 
    class Admin(CachingModel.Admin):
                sort_fields=["code"]
                app_menu="pos"
                menu_group = 'pos'
                menu_index = 35
                visible=False
                cache = 3600
                query_fields= ['code','money']
                default_widgets={'code':ZBaseSmallIntegerWidget,'money':ZBaseMoneyWidget}
                default_give_perms = ["contenttypes.can_PosFormPage",]
                if get_option("POS_IC"):
                    adv_fields=['use_mechine','code','money']
                    list_display=['code','money','use_mechine']
                    newadded_column = {'use_mechine':'get_device'}
                    api_m2m_display = { "use_mechine" : "get_device"}
                else:
                    adv_fields=['code','money']
                    list_display=['code','money']
                    
                help_text = _(u'下述所填项目中，键值编号(1-99)不能为空且不能重复，如果需要使用键值消费模式，需将此资料下载到机器上，系统自动验证：')
    class Meta:
            verbose_name=_(u'键值资料')
            verbose_name_plural=verbose_name
            app_label='pos'

def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, KeyValue):
        if  get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            n_dev = newObj.use_mechine.get_query_set()
            if n_dev:
                dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                delete_pos_device_info(dev,[newObj],"PRESSKEY")
                update_pos_device_info(n_dev,[newObj],"PRESSKEY")
            else:
                dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                update_pos_device_info(dev,[newObj],"PRESSKEY")
        
data_edit.post_check.connect(DataPostCheck)
