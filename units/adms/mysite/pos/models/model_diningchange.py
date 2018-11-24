#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

import datetime

from mysite.iclock.models.model_device import Device

class DiningChange(CachingModel):
    changeno=models.AutoField(verbose_name=_(u'调动单号'),db_column='changeno',primary_key=True,editable=False)
    device=models.ForeignKey(Device,verbose_name=_(u"设备"),editable=True)
    changedate=models.DateTimeField(verbose_name=_(u'调动时间'),null=True,blank=True,editable=True,auto_now=True)
    #changepostion=models.IntegerField(verbose_name=_(u'调动栏位'),choices=POSTION,editable=True,null=True,blank=True,)        
    oldvalue=models.TextField(verbose_name=_(u'调动前'),editable=False,null=True,blank=True)
    newvalue=models.TextField(verbose_name=_(u'调动后'),editable=False,null=True,blank=True)
    #changereason=models.CharField(max_length=200,verbose_name=_(u'调动原因'),null=True,blank=True,editable=True)
    #isvalid=models.BooleanField(verbose_name=_(u'是否生效'),choices=YESORNO,editable=True,default=0)
    #approvalstatus=models.IntegerField(verbose_name=_(u'审核状态'),choices=APPROVAL,editable=False,default=2)
    #remark=models.CharField(verbose_name=_(u'备注'),editable=True,null=True,blank=True,max_length=200)
#    def __unicode__(self):
#            return self.UserID.PIN+(self.UserID.EName and " %s"%self.UserID.EName or "")   
    class Admin(CachingModel.Admin):
                sort_fields=["-changedate","changeno","changedate"]
                app_menu="pos"
                menu_group = 'pos'
                menu_index =15
                visible=False
                cache = 3600
                query_fields=['device.alias','device.sn']
                #default_widgets={'parent': ZDeptChoiceWidget}
                adv_fields=['device.sn','oldvalue','newvalue','changedate']
                list_display=['device.alias','device.sn','oldvalue','newvalue','changedate']
                disabled_perms=["add_diningchange","change_diningchange",]
                search_fields=['changedate']
                tstart_end_search={
                                "changedate":[_(u"起始时间"),_(u"结束时间")]
                        }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
                help_text=_(u"消费机餐厅调整明细")
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
            verbose_name=_(u'消费机调动明细')
            
            verbose_name_plural=verbose_name
               