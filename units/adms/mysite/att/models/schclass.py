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
from dbapp.utils import getJSResponse
from django.utils import simplejson
from django.utils.encoding import  smart_str

from base.cached_model import CachingModel
from base.operation import Operation


BOOLEANS=((0,_(u"否")),(1,_(u"是")),)
    ##班次时段类别设置表##
class SchClass(CachingModel):
    SchclassID=models.AutoField(primary_key=True,null=False, editable=False)
    SchName=models.CharField(_(u'时段名称'), max_length=20,null=False)
    StartTime = models.TimeField(_(u'上班时间'),null=False, blank=False,editable=True)
    EndTime = models.TimeField(_(u'下班时间'),null=False, blank=False,editable=True)
    LateMinutes=models.IntegerField(_(u'允许迟到分钟数'),null=True,blank=True, default=0)
    EarlyMinutes=models.IntegerField(_(u'允许早退分钟数'),null=True,blank=True, default=0)
    CheckIn = models.SmallIntegerField(_(u'必须签到'),default=1,choices=BOOLEANS)
    CheckOut = models.SmallIntegerField(_(u'必须签退'),default=1,choices=BOOLEANS)
    CheckInTime1 = models.TimeField(_(u'开始签到时间'),null=False, blank=False)
    CheckInTime2 = models.TimeField(_(u'结束签到时间'),null=False, blank=False)
    CheckOutTime1 = models.TimeField(_(u'开始签退时间'),null=False, blank=False)
    CheckOutTime2 = models.TimeField(_(u'结束签退时间'),null=False, blank=False)
    Color=models.IntegerField(_(u'显示颜色'),null=False,default=16715535,blank=False,editable=False)
    AutoBind=models.SmallIntegerField(null=True,default=1,blank=True,choices=BOOLEANS,editable=False)
    WorkDay=models.FloatField(_(u'计为工作日数'), null=True, default=1.0, blank=True)
    IsCalcRest=models.IntegerField(_(u'设置时间'),null=True,default=0,  blank=True,editable=False) #暂时不编辑,是否扣减休息时间
    StartRestTime = models.TimeField(_(u'段中休息开始时间'),null=True, blank=True,editable=False)             #暂时不编辑,
    EndRestTime = models.TimeField(_(u'段中休息结束时间'),null=True, blank=True,editable=False)                  #暂时不编辑
    StartRestTime1 = models.TimeField(_(u'段中休息开始时间2'),null=True, blank=True,editable=False)             #暂时不编辑,
    EndRestTime1= models.TimeField(_(u'段中休息结束时间2'),null=True, blank=True,editable=False)                  #暂时不编辑

    shiftworktime = models.IntegerField(_(u'工作时间(分钟)'),null=False,blank=False,editable=True,default=480)
    IsOverTime=models.SmallIntegerField(_(u'延时是否计加班'),default=0,choices=BOOLEANS)
    OverTime=models.IntegerField(_(u'下班'),null=True,blank=True, default=60,editable=True) #下班 **分钟后签退记加班 ,如此命名为了前台好编辑
    
    def save(self):
        if self.pk==1:
            raise Exception(_(u'%s 不能被修改！')%self.SchName)
#        编辑时验证
        if self.pk>0: 
            from mysite.att.models import NUM_RUN_DEIL,USER_TEMP_SCH
            t=NUM_RUN_DEIL.objects.filter(SchclassID=self)
            if t:
                raise Exception(_(u'%s 该时段还有班次正在使用，不能编辑!')%self)
            t=USER_TEMP_SCH.objects.filter(SchclassID__exact=self.pk)
            if t:
                raise Exception(_(u'%s 该时段还有临时排班次正在使用，不能编辑!')%self)
            
#        tmp=SchClass.objects.filter(StartTime__exact=self.StartTime,EndTime__exact=self.EndTime).exclude(pk=1)
#        if tmp and tmp[0].pk !=self.pk and tmp[0].pk!=1:
#            raise Exception(_(u'已存在相同起始时间与结束时间的时段'))
        import datetime
        
        st= self.StartTime.strftime("%H:%M:%d")
        st=st.split(":")
        
        st=int(st[0])*60+int(st[1])
        et= self.EndTime.strftime("%H:%M:%d")
        #t=AttParam.objects.filter(ParaName__exact='TwoDay')

        
        et=et.split(":")
        
        et=int(et[0])*60+int(et[1])
        if et<st:
            et=et+60*24
#        st=datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d")+" "+self.StartTime,"%Y-%m-%m %H:%M:%D")
#        et=datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d")+" "+self.EndTime,"%Y-%m-%m %H:%M:%D")
#        print st
#        print et

        dumin=int(et)-int(st)
        
#        from mysite.att.models import AttParam
        from mysite.att.calculate.global_cache import C_ATT_RULE
        parm = C_ATT_RULE.data
#        t=AttParam.objects.filter(ParaName__exact='MaxShiftInterval')
        MaxShiftInterval = parm.has_key("MaxShiftInterval") and int(parm["MaxShiftInterval"]) or 660
        MinShiftInterval = parm.has_key("MinShiftInterval") and int(parm["MinShiftInterval"]) or 120
        if dumin>MaxShiftInterval:
            raise Exception(_(u'起始时间与结束时间的时间不能超过系统设置最大时段时间长度%d 分钟！')%MaxShiftInterval) 
        elif dumin<MinShiftInterval:
            raise Exception(_(u'起始时间与结束时间的时间不能小余系统设置最小时段时间长度%d 分钟！')%MinShiftInterval) 
#        if t:
#            t=t[0]
#            #print t.ParaValue
#            if dumin>int(t.ParaValue):
#                raise Exception(_(u'起始时间与结束时间的时间不能超过系统设置最大时段时间长度% s 分钟！')%t.ParaValue)            
#        else:
#            if dumin>660:           #默认值660
#                raise Exception(_(u'起始时间与结束时间的时间不能超过系统设置最大时段时间长度660分钟！'))
#        t=AttParam.objects.filter(ParaName__exact='MinShiftInterval')
#        if self.CheckInTime1>self.StartTime:
#            raise Exception(_(u'开始签到时间不能大于上班时间'))           
#        if self.CheckInTime2<self.StartTime:
#            raise Exception(_(u'结束签到时间不能小于上班时间'))           
#        if self.CheckOutTime1>self.EndTime:
#            raise Exception(_(u'开始签退时间不能大于下班时间'))           
#        if self.CheckOutTime2<self.EndTime:
#            raise Exception(_(u'结束签退时间不能小于下班时间'))   

        if self.StartRestTime:
            if self.StartTime <= self.EndTime:         
                if not( self.StartRestTime<=self.EndTime and  self.StartRestTime>=self.StartTime):
                    raise Exception(_(u'段中休息开始时间不正确'))
            else:
                if not( self.StartRestTime<=self.EndTime or  self.StartRestTime>=self.StartTime):
                    raise Exception(_(u'段中休息开始时间不正确'))   
        if self.EndRestTime:
            if self.StartTime <= self.EndTime:
                if not( self.EndRestTime<=self.EndTime and  self.EndRestTime>=self.StartTime):
                    raise Exception(_(u'段中休息结束时间不正确'))
            else:      
                if not( self.EndRestTime<=self.EndTime or  self.EndRestTime>=self.StartTime):
                    raise Exception(_(u'段中休息结束时间不正确'))  
        
#        if t:
#            t=t[0]
#            
#            if dumin<=int(t.ParaValue):                
#                raise Exception(_(u'起始时间与结束时间的时间不能小于系统设置最小时段时间长度% s 分钟！')%t.ParaValue)           
#        else:
#            if dumin<=120:           #默认值120
#                raise Exception(_(u'起始时间与结束时间的时间不能小于系统设置最小时段时间长度120分钟！'))
        
        super(SchClass,self).save()
        from mysite.att.calculate.global_cache import C_SCH_CLASS
        C_SCH_CLASS.refresh()
        
    def __unicode__(self):
        return unicode(u"%s"%(self.SchName))
    
    @staticmethod
    def clear():
        for e in SchClass.objects.all():
            if e.pk>1: 
                e.delete()
    
    def delete(self):
        if self.pk>1:            
            from mysite.att.models import NUM_RUN_DEIL,USER_TEMP_SCH
            t=NUM_RUN_DEIL.objects.filter(SchclassID=self)
            if t:
                raise Exception(_(u'%s 该时段还有班次正在使用，不能删除!')%self)
            t=USER_TEMP_SCH.objects.filter(SchclassID__exact=self.pk)
            if t:
                raise Exception(_(u'%s 该时段还有临时排班次正在使用，不能删除!')%self)
            super(SchClass,self).delete()
            from mysite.att.calculate.global_cache import C_SCH_CLASS
            C_SCH_CLASS.refresh()
        else:
            raise Exception(_(u'%s 不能被删除！')%self.SchName)
    class Admin(CachingModel.Admin):
        from dbapp.widgets import ZBaseDayMinsIntegerWidget, ZBaseSmallIntegerWidget,ZBaseColorWidget,ZBaseFloatWidget,ZBaseFloat_abv_zero_Widget,ZBase3IntegerWidget
        list_filter=('SchName','StartTime','EndTime','WorkDay','CheckIn','CheckOut')
        list_display=('SchName','StartTime','EndTime','WorkDay','CheckIn','CheckOut','IsOverTime')
        hide_fields=('SchclassID',)
        help_text=_(u'1、不能与已存在的时段有相同上班时间和下班时间<br>2、必须签到与签退，选取否时，系统在计算时会自动创建相应的随机签卡!<br>3、若该时段有班次或临时排班正在使用,则不能编辑和删除!')
        default_widgets={'LateMinutes':ZBaseSmallIntegerWidget,
        'EarlyMinutes':ZBaseSmallIntegerWidget,
        'Color':ZBaseColorWidget,
        'shiftworktime':ZBaseDayMinsIntegerWidget,
        'WorkDay':ZBaseFloat_abv_zero_Widget,
        'OverTime':ZBase3IntegerWidget,
        }
        disabled_perms=['dataimport_schclass']
        menu_index=1
        @staticmethod
        def initial_data(): #
                import datetime
                if SchClass.objects.count()==0:
                        SchClass(SchName=u"%s"%_(u"弹性时段"), 
                                StartTime=datetime.datetime.strptime("08:00","%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00","%H:%M").time(),
                                CheckInTime1=datetime.datetime.strptime("00:01","%H:%M").time(),
                                CheckInTime2 = datetime.datetime.strptime("23:59","%H:%M").time(),
                                CheckOutTime1 = datetime.datetime.strptime("00:01","%H:%M").time(),
                                CheckOutTime2 = datetime.datetime.strptime("23:59","%H:%M").time(),
                                OverTime=0,
                                ).save()
                pass

    class Meta:
        app_label='att'
        db_table = 'schclass'
        verbose_name=_(u'时段')
        verbose_name_plural=verbose_name

def getSchClass(request):
#    res=SchClass.objects.all().values("SchclassID","SchName","StartTime","EndTime")
#    index=0
#    for obj in res :
#        for k,v in obj.items():
#            if str(type(v))=="<type 'datetime.time'>":
#                res[index][k]=v.strftime("%H:%M")
#            else:
#                res[index][k]="%s"%v
#        index+=1
#    obj={}
#    obj["res"]=res
#    toResponse=smart_str(simplejson.dumps(obj))
#    return getJSResponse(toResponse)
    re = []
    ss = {}
    for t in SchClass.objects.all():
        ss['SchclassID'] = t.SchclassID
        ss['SchName'] = t.SchName
        ss['StartTime'] = t.StartTime.strftime("%H:%M")
        ss['EndTime'] = t.EndTime.strftime("%H:%M")
        t = ss.copy()
        re.append(t)
    return getJSResponse(smart_str(simplejson.dumps(re)))
