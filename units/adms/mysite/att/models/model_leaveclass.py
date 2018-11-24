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
from base.models import CachingModel, Operation,ModelOperation
from dbapp.models import ColorField

BOOLEANS=((0,_(u"否")),(1,_(u"是")),)
LEAVE_UNITS=(        
        (1, _(u'小时')),
        (2, _(u'分钟')),
        (3, _(u'工作日')),
)
LEAVETYPE=(
    (1, _(u'病假')),
    (2, _(u'事假')),
    (3, _(u'产假')),
    (4, _(u'探亲假')),
    (5, _(u'年假')),
    (6, _(u'因公外出')),

)

##假类表##
class LeaveClass(CachingModel):
        LeaveID=models.AutoField(_(u'假类编号'),primary_key=True,null=False, editable=False)
        LeaveName=models.CharField(_(u'假类名称'),max_length=20,null=False)
        MinUnit=models.FloatField(_(u'最小单位'),null=False,default=1,blank=False)
        Unit=models.SmallIntegerField(_(u'单位'),null=False,default=1,blank=False,max_length=2,choices=LEAVE_UNITS)
        RemaindProc=models.SmallIntegerField(_(u'是否按四舍五入计算'),null=False,max_length=2,default=1,blank=False,choices=BOOLEANS)
        RemaindCount=models.SmallIntegerField(_(u'按次计算'),null=False,default=1,max_length=2,blank=False,choices=BOOLEANS, editable=False)
        ReportSymbol=models.CharField(_(u'报表中的表示符号'),max_length=4,null=False,default='-')
        Deduct=models.FloatField(_(u'每一最小单位扣款'),null=True,default=0,blank=True,editable=False)
        Color=ColorField(_(u'显示颜色'),default=16715535,editable=False)
        Classify=models.SmallIntegerField(_(u'分类'),null=False,default=0,blank=True,editable=False)
        clearance=models.SmallIntegerField(_(u'是否自动销假'),db_column='clearance', null=False,default=0,blank=False, editable=False,choices=BOOLEANS)   #是否自动销假
        LeaveType=models.SmallIntegerField(_(u'所属类型'), null=False,default=1,blank=False, editable=False,choices=LEAVETYPE) #0 未知  1 病假 2事假 3产假 4探亲假 5年假
        def data_valid(self,sendtype):
            if float(self.MinUnit)==0:
                raise Exception(_(u'最小单位不能为0'))
            if self.Unit==1 and self.MinUnit>10:
                raise Exception(_(u'假类以小时为单位，最小单位不能超过10'))
            if self.Unit==2 and self.MinUnit>60:
                raise Exception(_(u'假类以分钟为单位，最小单位不能超过60'))
            if self.Unit==3 and self.MinUnit>1:
                raise Exception(_(u'假类以工作日为单位，最小单位不能超过1'))     
                
        def save(self):
            t=LeaveClass.objects.filter(LeaveName__exact=self.LeaveName)
            if t and t[0].pk!=self.pk:
                raise Exception(_(u'%s 假类名称已经存在')%self.LeaveName)
            t=LeaveClass.objects.filter(ReportSymbol__exact=self.ReportSymbol)
            if t and t[0].pk!=self.pk:
                raise Exception(_(u'%s 报表符号已经存在')%self.ReportSymbol)
            if self.pk and self.pk<=6:
                tt = LeaveClass.objects.get(pk=self.pk)
                if tt.LeaveName != self.LeaveName:
                    raise Exception(_(u'%s 默认假类名称不能修改')%self.LeaveName)
            super(LeaveClass,self).save()
            from mysite.att.calculate.global_cache import C_LEAVE_CLASS
            C_LEAVE_CLASS.refresh()
            
        def delete(self):
            super(LeaveClass,self).delete()
            from mysite.att.calculate.global_cache import C_LEAVE_CLASS
            C_LEAVE_CLASS.refresh()
#            if self.pk>6:
#                super(LeaveClass,self).delete()
#            else: 
#                raise Exception(_(u'默认假类不能被删除'))
        
        @staticmethod
        def clear():
                for obj in LeaveClass.objects.all():
                    if obj.pk>6:
                        obj.delete()
        
        def __unicode__(self):
#                return u"%s"%_(self.LeaveName)
                return u"%s"%self.LeaveName
        class _clear(ModelOperation):   
                help_text=_(u"清空所有记录") #清除该表的全部记录
                verbose_name=_(u"清空记录")
                visible=False
                def action(self):
                        t=LeaveClass.objects.all()
                        for i  in t:
                            if i.pk>6:
                                i.delete()
                        
                    
        class Admin(CachingModel.Admin):
                from dbapp.widgets import ZBaseColorWidget,ZBaseIntegerWidget,ZBaseFloatWidget,ZBaseNormalFloatWidget
                list_display=('LeaveName', 'MinUnit', 'Unit', 'RemaindProc','ReportSymbol')
                hide_fields=('LeaveID',)
                default_widgets={'Color': ZBaseColorWidget,
                    'MinUnit':ZBaseNormalFloatWidget,
                }
                cache = 3600
                menu_index=14
                def initial_data(self):
                    if LeaveClass.objects.all().count()==0:
                        LeaveClass(LeaveName=u"%s"%_(u'病假'),Unit=1,ReportSymbol='B',Color=3398744,LeaveType=1).save()
                        LeaveClass(LeaveName=u"%s"%_(u'事假'),MinUnit=0.5,Unit=1,RemaindProc=1,RemaindCount=1,ReportSymbol='G',Classify=0, LeaveType=2).save()
                        LeaveClass(LeaveName=u"%s"%_(u'产假'),MinUnit=0.5,Unit=1,RemaindProc=1,RemaindCount=1,ReportSymbol='C',LeaveType=3).save()
                        LeaveClass(LeaveName=u"%s"%_(u'探亲假'),Unit=1,ReportSymbol='T',Color=16744576,LeaveType=4).save()
                        LeaveClass(LeaveName=u"%s"%_(u'年假'),Unit=1,ReportSymbol='S',Color=8421631,LeaveType=5).save()
                        LeaveClass(LeaveName=u"%s"%_(u'因公外出'),Unit=1,ReportSymbol='W',Color=16715535,LeaveType=6).save()
                     #修改 假类  写入到数据的 根据初始化语言判断
                     
                       
                        
#                        LeaveClass(LeaveName=u'病假',Unit=1,ReportSymbol='B',Color=3398744,LeaveType=1).save()
#                        LeaveClass(LeaveName=u'事假',MinUnit=0.5,Unit=1,RemaindProc=1,RemaindCount=1,ReportSymbol='G',Classify=0, LeaveType=2).save()
#                        LeaveClass(LeaveName=u'产假',MinUnit=0.5,Unit=1,RemaindProc=1,RemaindCount=1,ReportSymbol='C',LeaveType=3).save()
#                        LeaveClass(LeaveName=u'探亲假',Unit=1,ReportSymbol='T',Color=16744576,LeaveType=4).save()
#                        LeaveClass(LeaveName=u'年假',Unit=1,ReportSymbol='S',Color=8421631,LeaveType=5).save()
                disabled_perms=['dataimport_leaveclass','clear_leaveclass']        
        class Meta:
                app_label='att'
                db_table = 'leaveclass'
                verbose_name=_(u'假类')
                verbose_name_plural=verbose_name
