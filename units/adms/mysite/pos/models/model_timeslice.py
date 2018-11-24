#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

from datetime import time
import string
import os

YESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),

)

class TimeSlice(CachingModel):
    code = models.CharField(max_length=20,verbose_name=_(u'时间段编号'),editable=True)
    starttime= models.TimeField(verbose_name=_(u'开始时间'),  null=False,blank=False,editable=True)
    endtime = models.TimeField(verbose_name=_(u'结束时间'),  null=False, blank=False,editable=True)
    isvalid = models.BooleanField(verbose_name=_(u'是否有效'),null=False, default=True, blank=True, editable=True, choices=YESORNO)
    remarks = models.CharField(max_length=200,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
    
    def __unicode__(self):
        return u"%s %s" %(self.starttime,self.endtime)
    
    
    def delete(self):
        if self.id!=1:
            super(TimeSlice,self).delete() 
    def data_valid(self, sendtype):
            try:
               self.code = str(int(self.code))
            except:
               raise Exception(_(u'编号只能为数字'))
            if int(self.code)< 0:
                raise Exception(_(u'编号不能为负数'))
            if int(self.code) == 0:
                raise Exception(_(u'编号不能为0'))
           
            if len(self.code) > settings.PIN_WIDTH:
                raise Exception(_(u'%(f)s 编号长度不能超过%(ff)s位') % {"f":self.code, "ff":settings.PIN_WIDTH})

            tmp = TimeSlice.objects.filter(code=self.code)
            if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                raise Exception(_(u'编号: %s 已存在') % self.code)
            
            if self.starttime>self.endtime:
                raise Exception(_(u'结束时间不能小于开始时间'))
                                             
    class Admin(CachingModel.Admin):
                sort_fields=["code"]
                app_menu="pos"
                menu_group = 'pos'
                menu_index = 22
                visible=False
                cache = 3600
                query_fields=['code','isvalid']
                default_give_perms = ["contenttypes.can_PosFormPage",]
                adv_fields=['code','starttime','endtime','isvalid','remarks']
                list_display=['code','starttime','endtime','isvalid','remarks']
                @staticmethod
                def initial_data(): 
                        if TimeSlice.objects.count()==0:
                                TimeSlice(starttime=time(8,0),code="1",endtime=time(10,0),isvalid=1).save()
                                TimeSlice(starttime=time(10,0),code="2",endtime=time(14,0),isvalid=1).save()
                                TimeSlice(starttime=time(14,0),code="3",endtime=time(20,0),isvalid=1).save()
                                TimeSlice(starttime=time(20,0),code="4",endtime=time(23,0),isvalid=1).save()
                                TimeSlice(starttime=time(0,0),code="5",endtime=time(10,0),isvalid=0).save()
                                TimeSlice(starttime=time(0,0),code="6",endtime=time(10,0),isvalid=0).save()
                                TimeSlice(starttime=time(0,0),code="7",endtime=time(10,0),isvalid=0).save()
                                TimeSlice(starttime=time(0,0),code="8",endtime=time(10,0),isvalid=0).save()
                        pass
                help_text="下述所填项目中，时间段编号不能为空且不能重复，系统自动验证："    
    class Meta:
            verbose_name=_(u'固定时间段设置')
            verbose_name_plural=verbose_name
            app_label='pos'
    class _delete(Operation):
        help_text = _(u"删除选定记录") #删除选定的记录
        verbose_name = _(u"删除")
        visible=False
        def action(self):
            pass     
    class _add(ModelOperation):
        visible=False
        def action(self):
            pass    

class TimeSliceForeignKey(models.ForeignKey):
    def __init__(self, verbose_name="", **kwargs):
        super(TimeSliceForeignKey, self).__init__(TimeSlice, verbose_name=verbose_name, **kwargs)
        
class TimeSliceManyToManyFieldKey(models.ManyToManyField):
    def __init__(self, verbose_name="", **kwargs):
        super(TimeSliceManyToManyFieldKey, self).__init__(TimeSlice, verbose_name=verbose_name, **kwargs)


def update_timeSplice_widgets():
        from dbapp import widgets
        from timesliceDropDown import ZtimeSliceChoiceWidget,ZTimeSliceMultiChoiceWidget
        if TimeSliceForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[TimeSliceForeignKey] = ZtimeSliceChoiceWidget
        if TimeSliceManyToManyFieldKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[TimeSliceManyToManyFieldKey] = ZTimeSliceMultiChoiceWidget
            
update_timeSplice_widgets() 
