# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
import datetime
from mysite.utils import get_option
CONSUMEMODEL=(
            (2,_(u'金额模式')),
            (1,_(u'定值模式')),
            (4,_(u'计次模式')),
            
            (3,_(u'键值模式')),
            (5,_(u'商品模式')),
            (6,_(u'计时模式')),
            (7,_(u'消费纠错')),
            (8,_(u'计次纠错')),
            (9,_(u'计时开始纠错')),
            (10,_(u'计时结束纠错')),
                  )

class PosLog(CachingModel):
    devname= models.CharField(_(u'设备名称'),max_length=20,null=True,blank=True)
    sn= models.CharField(_(u'序列号'),max_length=20,null=True,blank=True)
    serialnum = models.CharField(_(u'设备流水号'),max_length=20,null=True,blank=True)
    pin = models.CharField(_(u'人员编号'), db_column="badgenumber", null=True, max_length=20)
    carno = models.CharField(_(u'卡号'),max_length=10, null=True, blank=True)
    posmodel = models.IntegerField(_(u'消费操作'),null=True, blank=True,choices=CONSUMEMODEL)
    posmoney = models.DecimalField(verbose_name=_(u'消费金额'),max_digits=20,null=True, blank=True,decimal_places=2)
    blance = models.DecimalField(verbose_name=_(u'卡上余额'),max_digits=20,null=True, blank=True,decimal_places=2)
    posOpTime = models.DateTimeField(verbose_name=_(u'消费时间'),default=datetime.datetime.now(),blank=True,editable=True,null=True)
    def __unicode__(self): 
        try:
            return u"%s,%s"%(self.sn,self.carno)
        except:
            return u"%s,%s"%(self.sn,self.carno)
    def save(self, **args):
       models.Model.save(self,args)
    
    class Admin(CachingModel.Admin):
        sort_fields=["-posOpTime",'posOpTime','serialnum','posmoney']
        app_menu="pos"
        menu_group = 'pos'
        menu_index = 11
        cache = 3600
        visible = get_option("POS_ID")#暂只有消费使用
        list_display=['devname','sn','serialnum','pin','carno','posmodel','posmoney','blance','posOpTime']
        query_fields=['pin','carno','posmodel','posOpTime']
        adv_fields = ['devname','sn','serialnum','pin','carno','posmodel','posOpTime','posmoney']
        #search_fields = ["OP","Object"]
        disabled_perms=["change_poslog","delete_poslog","add_poslog"]
        search_fields=['posOpTime']
        tstart_end_search={
                        "posOpTime":[_(u"起始时间"),_(u"结束时间")]
                    }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        
    class _delete(Operation):
                help_text = _(u"删除选定记录") #删除选定的记录
                verbose_name = _(u"删除")
                visible=False
                def action(self):
                    pass   
              
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
        verbose_name = _(u"消费日志")
        verbose_name_plural=verbose_name
