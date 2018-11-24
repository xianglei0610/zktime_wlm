#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
from mysite.pos.pos_id.pos_id_util import set_pos_info_record
from datetime import time
import string
import os
from mysite.utils import get_option
YESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),

)
TIMENAME =(
('1',_(u'固定时间段')),
('2',_(u'第2批')),
('3',_(u'第3批')),
('4',_(u'第4批')),
('5',_(u'第5批')),
('6',_(u'第6批')),
('7',_(u'第7批')),
('8',_(u'第8批')),
('9',_(u'第9批')),
)

class BatchTime(CachingModel):
    code = models.CharField(max_length=3,verbose_name=_(u'编号'),null=False,blank=False,editable=False)
    name = models.CharField(max_length=20,verbose_name=_(u'时间段名称'),null=True,blank=True,editable=True)
    starttime= models.TimeField(verbose_name=_(u'开始时间'),  null=False,blank=False,editable=True)
    endtime = models.TimeField(verbose_name=_(u'结束时间'),  null=False, blank=False,editable=True)
    isvalid = models.BooleanField(verbose_name=_(u'是否有效'),null=False, default=True, blank=True, editable=True, choices=YESORNO)
    remarks = models.CharField(max_length=200,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
    pos_time = models.CharField(verbose_name=_(u"批次编号"),max_length=10,blank=True,null=True,choices=TIMENAME)
    def __unicode__(self):
        return u"%s" %(self.name)
    
    def save(self,*args, **kwargs):
        super(BatchTime,self).save()
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER)
            if dev:
                if self.isvalid == 1:
                    update_pos_device_info(dev,[self],"TIMESEG")
                else:
                    delete_pos_device_info(dev,[self],"TIMESEG")
            
        key="BatchTime_"+self.code
        cacheobj = BatchTime.objects.filter(code=self.code,isvalid=1)
        cache.set(key,list(cacheobj),TIMEOUT)
        set_pos_info_record()
    def data_valid(self, sendtype):
            if self.starttime>self.endtime:
                raise Exception(_(u'结束时间不能小于开始时间'))
                                             
    class Admin(CachingModel.Admin):
                sort_fields=["code","-starttime","starttime","endtime"]
                app_menu="pos"
                menu_group = 'pos'
                menu_index = 22
                visible=False
                cache = 3600
                query_fields=['name','isvalid']
                default_give_perms = ["contenttypes.can_PosFormPage",]
                adv_fields=['name','starttime','endtime','isvalid','remarks']
                list_display=['name','starttime','endtime','isvalid','remarks']
                @staticmethod
                def initial_data(): 
                        if BatchTime.objects.count()==0:
                            BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="1",endtime=time(23,59),isvalid=1).save()
                            BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="2",endtime=time(23,59),isvalid=1).save()
                            BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="3",endtime=time(23,59),isvalid=1).save()
                            BatchTime(starttime=time(0,1),name=u"%s"%_(u"固定时间段"),code="1",pos_time="4",endtime=time(23,59),isvalid=1).save()
                            BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="5",endtime=time(0,0),isvalid=0).save()
                            BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="6",endtime=time(0,0),isvalid=0).save()
                            BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="7",endtime=time(0,0),isvalid=0).save()
                            BatchTime(starttime=time(0,0),name=u"%s"%_(u"固定时间段"),code="1",pos_time="8",endtime=time(0,0),isvalid=0).save()
                            for i in range(2,10):
                                BatchTime(starttime=time(8,0),name= unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="1",endtime=time(9,0),isvalid=1).save()
                                BatchTime(starttime=time(10,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="2",endtime=time(14,0),isvalid=1).save()
                                BatchTime(starttime=time(17,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="3",endtime=time(19,0),isvalid=1).save()
                                BatchTime(starttime=time(20,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="4",endtime=time(23,59),isvalid=1).save()
                                BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="5",endtime=time(0,0),isvalid=0).save()
                                BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="6",endtime=time(0,0),isvalid=0).save()
                                BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="7",endtime=time(0,0),isvalid=0).save()
                                BatchTime(starttime=time(0,0),name=unicode('第%s批','utf-8')%i,code="%s"%i,pos_time="8",endtime=time(0,0),isvalid=0).save()
                            pass
                help_text=_(u"下述所填项目中，时间段名称不能为空，系统自动验证")    
    class Meta:
            verbose_name=_(u'消费时间段')
            verbose_name_plural=verbose_name
            app_label='pos'
  
        
class TimeSliceForeignKey(models.ForeignKey):
    def __init__(self, verbose_name="", **kwargs):
        super(TimeSliceForeignKey, self).__init__(BatchTime, verbose_name=verbose_name, **kwargs)
        
class TimeSliceManyToManyFieldKey(models.ManyToManyField):
    def __init__(self, verbose_name="", **kwargs):
        super(TimeSliceManyToManyFieldKey, self).__init__(BatchTime, verbose_name=verbose_name, **kwargs)


def update_timeSplice_widgets():
        from dbapp import widgets
        from timesliceDropDown import ZtimeSliceChoiceWidget,ZTimeSliceMultiChoiceWidget
        if TimeSliceForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[TimeSliceForeignKey] = ZtimeSliceChoiceWidget
        if TimeSliceManyToManyFieldKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[TimeSliceManyToManyFieldKey] = ZTimeSliceMultiChoiceWidget
            
update_timeSplice_widgets() 


