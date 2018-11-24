#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 
from datetime import time
import datetime
import string
import os
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
from mysite.utils import get_option
from dbapp import data_edit
from mysite.iclock.models.model_device import DeviceManyToManyFieldKey
from mysite.pos.pos_id.pos_id_util import set_pos_info_record
YESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),
)

class SplitTime(CachingModel):
    code = models.CharField(max_length=20,verbose_name=_(u'编号'),editable=False)
    name = models.CharField(max_length=20,verbose_name=_(u'名称'),editable=True)
    starttime= models.TimeField(verbose_name=_(u'开始时间'),  null=False,blank=False,editable=True)
    endtime = models.TimeField(verbose_name=_(u'结束时间'),  null=False, blank=False,editable=True)
    isvalid = models.BooleanField(verbose_name=_(u'是否有效'),null=False, default=True, blank=True, editable=True, choices=YESORNO)
    fixedmonery = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
    use_mechine = DeviceManyToManyFieldKey(verbose_name=_(u'可用设备'), blank=True, null=True)#从设备登记中获取
    remarks = models.CharField(max_length=200,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
    
    def __unicode__(self):
        return u"%s %s %s"% (self.starttime,self.endtime,self.fixedmonery)
    def save(self,*args, **kwargs):
        self.endtime=self.endtime.replace(second=59)
        self.starttime=self.starttime.replace(second=00)
        super(SplitTime,self).save()
        cacheobj = SplitTime.objects.all().filter(isvalid=1)
        cache.set("SplitTime",list(cacheobj),TIMEOUT)
        set_pos_info_record()
#        if get_option("POS_IC"):
#            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,delete_pos_device_info
#            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
#            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
#            if dev:
#                delete_pos_device_info(dev,[self],"FIXED")
            
    def delete(self):
        if self.id not in  range(9):
            super(SplitTime, self).delete()  
    def get_device(self):
        return u",".join([a.sn for a in self.use_mechine.all()])
    
    def get_endtime(self):
        return self.endtime.strftime("%H:%M")
    def get_begintime(self):
        return self.starttime.strftime("%H:%M")
    
    def data_valid(self, sendtype):
            try:
               self.code = str(int(self.code))
            except: 
               raise Exception(_(u'编号只能为数字'))
            if int(self.code)< 0:
                raise Exception(_(u'编号不能为负数'))
            if int(self.code) == 0:
                raise Exception(_(u'编号不能为0'))
            try:
               self.fixedmonery = str(int(self.fixedmonery))
            except:
               raise Exception(_(u'金额只能为数字'))
            if int(self.fixedmonery)< 0:
                raise Exception(_(u'金额不能为负数'))
            if len(self.code) > settings.PIN_WIDTH:
                raise Exception(_(u'%(f)s编号长度不能超过%(ff)s位') % {"f":self.code, "ff":settings.PIN_WIDTH})

            tmp = SplitTime.objects.filter(code=self.code)
            if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                raise Exception(_(u'编号: %s 已存在') % self.code)
            if int(self.code)<>1:
                tmp = SplitTime.objects.get(code=int(self.code)-1)
                minute1 = tmp.endtime.minute+1
                hour1 = tmp.endtime.hour
                hour2 = self.starttime.hour
                if minute1==60:
                    minute1 =0
                    hour1=tmp.endtime.hour+1
                minute2 = self.starttime.minute
                if hour1<>hour2 and self.isvalid==1:
                    raise Exception(_(u'本分段定值的开始时间必须是上一分段定值的结束时间加一分钟'))
                if minute2 <> minute1 and self.isvalid==1:
                    raise Exception(_(u'本分段定值的开始时间必须是上一分段定值的结束时间加一分钟'))

            if self.starttime>self.endtime:
                raise Exception(_(u'结束时间不能小于开始时间'))
                                             
    class Admin(CachingModel.Admin):
            help_text=_(u"下述所填项目中，分段定值系统默认为八个，如需使用分段定值消费，需将此资料下载到消费机上，系统自动验证。当分段定值有效时，本分段定值开始时间必须是上一分段定值的结束时间加一分钟")
            sort_fields=["code","starttime","endtime"]
            app_menu="pos"
            menu_group = 'pos'
            menu_index =21
            cache = 3600
            visible=False
            query_fields = ['code','fixedmonery','isvalid']
            default_give_perms = ["contenttypes.can_PosFormPage",]
            if get_option("POS_IC"):
                adv_fields=['code','name','starttime','endtime','fixedmonery','isvalid','use_mechine','remarks']
                list_display=['code','name','starttime','endtime','fixedmonery','isvalid','use_mechine','remarks']
                newadded_column = {'use_mechine':'get_device','endtime':'get_endtime','starttime':'get_begintime'}
                api_m2m_display = {'use_mechine':'get_device'}
            else:
                adv_fields=['code','name','starttime','endtime','fixedmonery','isvalid','remarks']
                list_display=['code','name','starttime','endtime','fixedmonery','isvalid','remarks']
                newadded_column = {'endtime':'get_endtime','starttime':'get_begintime'}
                
                
            @staticmethod
            def initial_data(): 
                    if SplitTime.objects.count()==0:
                            SplitTime(starttime=time(0,0),code="1",name=u"%s"%_(u"默认1"),endtime=time(10,0),fixedmonery="10").save()
                            SplitTime(starttime=time(10,1),code="2",name=u"%s"%_(u"默认2"),endtime=time(14,0),fixedmonery="10").save()
                            SplitTime(starttime=time(14,1),code="3",name=u"%s"%_(u"默认3"),endtime=time(20,0),fixedmonery="10").save()
                            SplitTime(starttime=time(20,1),code="4",name=u"%s"%_(u"默认4"),endtime=time(23,59),fixedmonery="10").save()
                            SplitTime(starttime=time(0,1),code="5",name=u"%s"%_(u"默认5"),endtime=time(0,1),fixedmonery="10",isvalid = False).save()
                            SplitTime(starttime=time(0,1),code="6",name=u"%s"%_(u"默认6"),endtime=time(0,1),fixedmonery="10",isvalid = False).save()
                            SplitTime(starttime=time(0,1),code="7",name=u"%s"%_(u"默认7"),endtime=time(0,1),fixedmonery="10",isvalid = False).save()
                            SplitTime(starttime=time(0,1),code="8",name=u"%s"%_(u"默认8"),endtime=time(0,1),fixedmonery="10",isvalid = False).save()
                                 
    class Meta:
            verbose_name=_(u'分段定值')
            verbose_name_plural=verbose_name
            app_label='pos'

class SplitTimeForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
            super(SplitTimeForeignKey, self).__init__(SplitTime, to_field=to_field, **kwargs)

class SplitTimeManyToManyFieldKey(models.ManyToManyField):
    def __init__(self, verbose_name="", **kwargs):
        super(SplitTimeManyToManyFieldKey, self).__init__(SplitTime, verbose_name=verbose_name, **kwargs)

def update_splitTime_widgets():
        from dbapp import widgets
        if SplitTimeForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                from splittimeDropDown import ZSplitChoiceWidget,ZSplitTimeMultiChoiceWidget
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[SplitTimeForeignKey] = ZSplitChoiceWidget
        if SplitTimeManyToManyFieldKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[SplitTimeManyToManyFieldKey] = ZSplitTimeMultiChoiceWidget

update_splitTime_widgets() 


def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, SplitTime):
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            n_dev = newObj.use_mechine.get_query_set()
            if n_dev:
                if newObj.isvalid == 1:
                    dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                    delete_pos_device_info(dev,[newObj],"FIXED")
                    update_pos_device_info(n_dev,[newObj],"FIXED")
                else:
                    delete_pos_device_info(n_dev,[newObj],"FIXED")
            else:
                dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                if newObj.isvalid == 1:
                    update_pos_device_info(dev,[newObj],"FIXED")
                else:
                    delete_pos_device_info(dev,[newObj],"FIXED")
        
data_edit.post_check.connect(DataPostCheck)
