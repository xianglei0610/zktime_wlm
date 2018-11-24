#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from base.operation import ModelOperation
from django.utils.translation import ugettext_lazy as _
from accdoor import AccDoor
from mysite.personnel.models import Employee
from mysite.utils import get_option
import redis_self, re, os, dict4ini, datetime
import re
from traceback import print_exc
from django.conf import settings
from django import forms


EVENT_LINKCONTROL       = 6     #联动事件
CANCEL_ALARM            = 7#取消报警
OPEN_AUXOUT             = 12#开启辅助输出
CLOSE_AUXOUT            = 13#关闭辅助输出
EVENT_UNREGISTERCARD    = 27 #卡未注册
EVENT_DOORSENSOROPEN = 200  #门磁开
EVENT_DOORSENSORCLOSE = 201     #门磁关
INOUT_SEVER             = 220
INOUT_SHORT             = 221

ALARM_ID_START    = 100#20
ALARM_ID_END      = 200
DOOR_STATE_ID     = 255

#验证方式---从设备上来的事件的验证方式
VERIFIED_CHOICES = (
    (3, _(u'仅密码')),
    (4, _(u'仅卡')),
    #(7, _(u'卡或密码')),        
    (11, _(u'卡加密码')),
    (200, _(u'其他'))
)
   
if not get_option("IACCESS_5TO4"):
    VERIFIED_CHOICES = VERIFIED_CHOICES + (
        (1, _(u'仅指纹')),
        (6, _(u'卡或指纹')),
        (10, _(u'卡加指纹')),
    )

IN_ADDRESS_CHOICES = (
    (-1,_(u'无')),
    (1, _(u'辅助输入1')),
    (2, _(u'辅助输入2')),
    (3, _(u'辅助输入3')),
    (4, _(u'辅助输入4')),
    (9, _(u'辅助输入9')),
    (10, _(u'辅助输入10')),
    (11, _(u'辅助输入11')),
    (12, _(u'辅助输入12')),
)

OUT_ADDRESS_CHOICES = (
    (-1,_(u'无')),
    (1, _(u'辅助输出1')),
    (2, _(u'辅助输出2')),
    (3, _(u'辅助输出3')),
    (4, _(u'辅助输出4')),
    (6, _(u'辅助输出6')),
    (8, _(u'辅助输出8')),
    (9, _(u'辅助输出9')),
    (10, _(u'辅助输出10')),
)

#出入状态-单向时都为入

STATE_CHOICES = (
    (0, _(u'入')),
    (1, _(u'出')),
    (2, _(u'无')),
    #(2, _(u'未知或无或其他')),#即其他
)

EVENT_LOG_AS_ATT = [0, 1, 2, 3, 14, 15, 16, 17, 18, 19, 21, 22, 23, 26, 32, 35,203]#用来作为考勤用的实时监控记录。20110518 lhj 增加多卡开门事件作为考勤原始记录

#事件选项
#公共事件，即C3和inbio公共的。
EVENT_CHOICES = (
    (-1, _(u'无')),
    (0, _(u'正常刷卡开门')),
    (1, _(u'常开时间段内刷卡')),#含门常开时段和首卡常开设置的开门时段 （开门后）
    (2, _(u'首卡开门(刷卡)')),
    (3, _(u'多卡开门(刷卡)')),#门打开
    (4, _(u'紧急状态密码开门')),
    (5, _(u'常开时间段开门')),
    (6, _(u'触发联动事件')),
    (7, _(u'取消报警')),#远程开关门与扩展输出   ，至于远程开关门与扩展输出等动作执行后还有相应事件记录
    (8, _(u'远程开门')),
    (9, _(u'远程关门')),
    (10, _(u'禁用当天常开时间段')),#
    (11, _(u'启用当天常开时间段')),#
    (12, _(u'开启辅助输出')),#
    (13, _(u'关闭辅助输出')),#
    
    (20, _(u'刷卡间隔太短')),#5
    (21, _(u'门非有效时间段(刷卡)')),
    (22, _(u'非法时间段')),#！！！有权限但是时间段不对。当前时段无合法权限
    (23, _(u'非法访问')),#当前时段无此门权限----卡已注册，但是没有该门的权限
    (24, _(u'反潜')),
    (25, _(u'互锁')),
    (26, _(u'多卡验证(刷卡)')),#刷卡
    (27, _(u'卡未注册')),#10
    (28, _(u'门开超时')),
    (29, _(u'卡已过有效期')),
    (30, _(u'密码错误')),

    (36, _(u'门非有效时间段(按出门按钮)')),
    (37, _(u'常开时间段无法关门')),
    #(38, _(u'卡已挂失')),#暂未国际化
    #(39, _(u'黑名单')),
    
    #(41, _(u'反潜验证')),#可能用不到？
    (42, _(u'韦根格式错误')),#韦根格式与配置不符
    #(43, _(u'反潜验证超时')),#固件连不通软件
    (47, _(u'发送命令失败')),#增加开门命令失败事件 ，产生开门命令而485通讯失败时上传此事件，事件代码为 38
    (48, _(u'多卡验证失败(刷卡)')),

    (49, _(u'门非有效时间段(密码)')),
    (50, _(u'按密码间隔太短')),
    (51, _(u'多卡验证(密码)')),
    (52, _(u'多卡验证失败(密码)')),

    (53, _(u'密码已过有效期')),
    
    (100, _(u'防拆报警')),#机器被拆除
    (101, _(u'胁迫密码开门')),
    (102, _(u'门被意外打开')),

    (200, _(u'门已打开')),#16
    (201, _(u'门已关闭')),
    (202, _(u'出门按钮开门')),
    
    (204, _(u'常开时间段结束')),
    (205, _(u'远程开门常开')),
    (206, _(u'设备启动')),
    (207, _(u'密码开门')),
    (208, _(u'超级用户开门')),
    (209, _(u'触发出门按钮(被锁定)')),
    (210, _(u'启动消防开门')),
    (211, _(u'超级用户关门')),
    (212, _(u'开启电梯控制功能')),
    (213, _(u'关闭电梯控制功能')),
    (214, _(u'多卡开门(密码)')),
    (215, _(u'首卡开门(密码)')),
    
    (216, _(u'常开时间段内按密码')),
    
    (220, _(u'辅助输入点断开')),
    (221, _(u'辅助输入点短路')), 
    
    
    #(222, _(u'反潜验证成功')),#门也会打开--darcy20110803-锦湖轮胎
    #(223, _(u'反潜验证暂停')),#反潜验证暂停，固件根据门禁权限组判断，门也会打开（如果有权限的话）--darcy20110804-锦湖轮胎
    #(224, _(u'反潜验证开始')),#初始化反潜规则时，第一次记录固件按照门禁权限组判断，门也会打开（如果有权限的话）--darcy20110804-锦湖轮胎//224后台重新启用反潜
)


if not get_option("IACCESS_5TO4"):#inBio控制器多余的跟指纹相关的事件-darcy20120113
    EVENT_CHOICES = EVENT_CHOICES + (
        (14, _(u'正常按指纹开门')),#
        (15, _(u'多卡开门(按指纹)')),#
        (16, _(u'常开时间段内按指纹')),#
        (17, _(u'卡加指纹开门')),#
        (18, _(u'首卡开门(按指纹)')),#
        (19, _(u'首卡开门(卡加指纹)')),#

        (31, _(u'按指纹间隔太短')),
        (32, _(u'多卡验证(按指纹)')),
        (33, _(u'指纹已过有效期')),
        (34, _(u'指纹未注册')),
        (35, _(u'门非有效时间段(按指纹)')),

        (40, _(u'多卡验证失败(按指纹)')),
        
        (103, _(u'胁迫指纹开门')),

        (203, _(u'多卡开门(卡加指纹)')),
    )
   

class AccRTMonitor(CachingModel):
    u"""
    实时监控记录
    """
    log_tag = models.IntegerField(_(u'记录ID'), null=True, blank=True, editable=False)#唯一标识记录
    time = models.DateTimeField(_(u'时间'), null=True, blank=True, editable=True)
    pin = models.CharField(_(u'人员编号'), max_length=20, null=True, blank=True, editable=True)
    card_no = models.CharField(_(u'卡号'), max_length=20, null=True, blank=True, editable=True)
    #device = models.ForeignKey(Device, verbose_name=_(u'设备'), null=True, blank=False, editable=True)
    device_id = models.IntegerField(_(u'设备ID'), null=True, blank=True, editable=False)#特殊用途--表征唯一
    device_sn = models.CharField(_(u'序列号'), max_length=20, editable=False)
    device_name = models.CharField(_(u'设备'), max_length=20, null=True, blank=True, editable=True)
    door_id = models.IntegerField(_(u'门ID'), null=True, blank=True, editable=False)#特殊用途
    door_name = models.CharField(_(u'门事件点'), max_length=30, null=True, blank=True, editable=True)
    #door = models.ForeignKey(AccDoor,verbose_name=_(u'门事件点'), null=True, blank=True, editable=True)
    in_address = models.IntegerField(_(u'辅助输入点'), null=True, blank=True, editable=True, choices=IN_ADDRESS_CHOICES,default=-1)
    out_address = models.IntegerField(_(u'辅助输出点'), null=True, blank=True, editable=True, choices=OUT_ADDRESS_CHOICES,default=-1)
    verified = models.IntegerField(_(u'验证方式'), default=200, null=True, blank=True, editable=True, choices=VERIFIED_CHOICES)#暂时只支持密码验证和卡验证
    state = models.IntegerField(_(u'出入状态'), null=True, blank=True, editable=True, choices=STATE_CHOICES)
    event_type = models.SmallIntegerField(_(u'事件描述'), null=True, blank=True, editable=True, choices=EVENT_CHOICES)
    trigger_opt = models.SmallIntegerField(_(u'联动触发条件'), null=True, blank=True, editable=True, choices=EVENT_CHOICES,default=-1)
    
#    def limit_accrtmonitor_to(self, queryset, user):
#        #需要过滤掉用户权限不能控制的设备对应的门的实时监控记录(列表datalist)
#        aa = user.areaadmin_set.all()
#        if not user.is_superuser and aa:
#            areas = [a.area for a in aa]
#            queryset = queryset.filter(device__area__in=areas)#door__device__area__in
#        return queryset

    @staticmethod
    def clear():
        AccRTMonitor.objects.all().delete()
    
    def save(self, *args, **kwargs):
        super(AccRTMonitor, self).save(log_msg=False)
        
    def get_name_by_PIN(self):
#        emp = Employee.objects.filter(PIN=self.pin)
#        return emp and emp[0].EName +' '+ emp[0].lastname or ''
        try:
            emp = Employee.objects.get(PIN=self.pin)
            return "%s %s"%(emp.EName or '', emp.lastname or '')
        except:
            return ''


    class OpClearRTLogs(ModelOperation):
        verbose_name = _(u"清空全部事件记录")
        help_text = _(u"全部事件记录包含了所有的实时监控记录（包含异常事件记录），确认后将会被清空！") #清除该表的全部记录
        tips_text =  _(u"确认要清空全部事件记录")
        def action(self):
            self.model.objects.all().delete()

    class OpClearAbnormityLogs(ModelOperation):
        help_text = _(u"门禁异常事件记录是实时监控记录中存在异常的部分，确认后将会被清空！") #清除该表的全部记录
        tips_text =  _(u"确认要清空异常事件记录")
        verbose_name = _(u"清空异常事件记录")
        def action(self):
            self.model.objects.filter(event_type__gte=20).filter(event_type__lt=200).delete()

#    class OpExportRTLogs(ModelOperation):
#        help_text=_(u"导出全部事件记录")
#        verbose_name=u"导出全部事件记录"
#        def action(self):
#            pass
#
#    class OpExportAbnormityLogs(ModelOperation):
#        help_text=_(u"导出异常事件记录")
#        verbose_name=u"导出异常事件记录"
#        def action(self):
#            pass
        
    class Admin(CachingModel.Admin):
        list_display = ['time','pin','get_name_by_PIN','card_no','device_name','door_name','in_address','out_address','verified', 'state', 'event_type', 'trigger_opt']
        query_fields = ('time','pin', 'card_no', 'device_name','door_name','in_address','verified', 'state', 'event_type')#'time', 只能支持精确查询，模糊查询暂时支持不了，故暂时不开放（可使用高级查询）
        visible = False
        menu_group = "acc_monitor_"
        tstart_end_search = {
            "time":[_(u"开始时间"), _(u"结束时间")]
        }
        
        #配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        #用来进行特殊查询，查询的字段不在当前模型中，并且与当前模型没有外键或者多对多的关系，但是这两个模型必须有某字段一样
        #每个需要查询的字段在下面定义，并传进5个参数
        #参数1会在查询界面创建一个查询的输入框，参数2和参数3表示该字段存在的应用和模型名字
        #参数4和参数5表示这两个模型共享的字段分别在他们中的名字
        new_added_fields = {
            "EName" : [forms.CharField(label=_(u"姓名"), required=False, widget=forms.TextInput, max_length=24), "personnel", "Employee", "pin", "PIN"],                       
            #"lastname" : [forms.CharField(label=_(u"姓氏"), required=False, widget=forms.TextInput, max_length=24), "personnel", "Employee", "pin", "PIN"], 
        }

    class Meta:
        app_label = 'iaccess'
        db_table = 'acc_monitor_log'
        unique_together = (("time", "pin","card_no","device_id","door_id","in_address","verified","state","event_type","trigger_opt"),)
        verbose_name = _(u'实时监控记录')
        verbose_name_plural = verbose_name
