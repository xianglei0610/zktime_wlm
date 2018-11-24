#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

import datetime
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
import os
from base.middleware import threadlocals
from mysite.utils import get_option
from model_icconsumerlist import ICConsumerList
from base.operation import OperationBase, Operation, ModelOperation
class StoreDetail(models.Model,OperationBase):    
    list_code_id = models.CharField(verbose_name=_(u'明细编号'),max_length=20, editable=True, null=True, blank=False)
    dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
    dev_serial_num = models.IntegerField(_(u'设备流水号'),max_length=20,null=True,blank=True)
    store_code = models.CharField(_(u'商品编号'),max_length=4,null=True,blank=True,editable=False)
    money = models.DecimalField (max_digits=9,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
    RecSum =  models.CharField(_(u'序号'),null=False, max_length=20)
    convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
    
    def __unicode__(self):
        return ""
    class Admin:
        app_menu="pos"
        menu_group = 'pos'
        menu_index =19
        cache = 3600
        visible = False
        
    class _change(ModelOperation):
        visible=False
        def action(self):
            pass 
        
    class _add(ModelOperation):
        visible=False
        def action(self):
            pass      
               
    class Meta:
        app_label='pos'
        verbose_name = _(u"商品模式明细表")
        verbose_name_plural = verbose_name
        unique_together = (("list_code_id", "RecSum"))
