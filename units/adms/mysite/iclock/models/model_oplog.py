# -*- coding: utf-8 -*-
from django.db import models, connection
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from model_device import Device, DeviceForeignKey

def OpName(op):
    OPNAMES={0: _(u"开机"),
        1: _(u"关机"),
        2: _(u"验证失败"),
        3: _(u"报警"),
        4: _(u"进入菜单"),
        5: _(u"更改设置"),
        6: _(u"登记指纹"),
        7: _(u"登记密码"),
        8: _(u"卡登记"),
        9: _(u"删除用户"),
        10: _(u"删除指纹"),
        11: _(u"删除密码"),
        12: _(u"删除射频卡"),
        13: _(u"清除数据"),
        14: _(u"创建MF卡"),
        15: _(u"登记MF卡"),
        16: _(u"登记MF卡"),
        17: _(u"删除MF卡注册"),
        18: _(u"清除MF卡内容"),
        19: _(u"把登记数据移到卡中"),
        20: _(u"把卡中的数据复制到机器中"),
        21: _(u"设置时间"),
        22: _(u"恢复出厂设置"),
        23: _(u"删除进出记录"),
        24: _(u"清除管理员权限"),
        25: _(u"修改门禁设置"),
        26: _(u"修改用户门禁设置"),
        27: _(u"修改门禁时间段"),
        28: _(u"修改开锁组合设置"),
        29: _(u"开锁"),
        30: _(u"登记新用户"),
        31: _(u"更改指纹属性"),
        32: _(u"胁迫报警"),
        } #{0: u"开机",
        #1: u"关机",
        #2: u"验证失败",
        #3: u"报警",
        #4: u"进入菜单",
        #5: u"更改设置",
        #6: u"登记指纹",
        #7: u"登记密码",
        #8: u"登记HID卡",
        #9: u"删除用户",
        #10: u"删除指纹",
        #11: u"删除密码",
        #12: u"删除射频卡",
        #13: u"清除数据",
        #14: u"创建MF卡",
        #15: u"登记MF卡",
        #16: u"注册MF卡",
        #17: u"删除MF卡注册",
        #18: u"清除MF卡内容",
        #19: u"把登记数据移到卡中",
        #20: u"把卡中的数据复制到机器中",
        #21: u"设置时间",
        #22: u"恢复出厂设置",
        #23: u"删除进出记录",
        #24: u"清除管理员权限}",
        #25: u"修改门禁组设置",
        #26: u"修改用户门禁设置",
        #27: u"修改门禁时间段",
        #28: u"修改开锁组合设置",
        #29: u"开锁",
        #30: u"登记新用户",
        #31: u"更改指纹属性",
        #32: u"胁迫报警",    
    try:
        return OPNAMES[op]
    except:
        return op and "%s"%op or ""
        
def AlarmName(obj):
    ALARMNAMES={
        50:_(u"门被非法关闭"),
        51:_(u"门被非法打开"),
        55:_(u"机器被拆除"),
        53:_(u"出门按钮"),
        54:_(u"门被意外打开"),
        58:_(u"多次验证失败"),
        65535:_(u"取消报警"),
    }
    try:
        return ALARMNAMES[obj]
    except:
        return obj and "%s"%obj or ""

class OpLog(models.Model):
    SN = DeviceForeignKey(db_column='SN', verbose_name=_(u'设备'), null=True, blank=True)
    admin = models.IntegerField(_(u'设备超级管理员'), null=False, blank=False, default=0)
    OP = models.SmallIntegerField(_(u'操作'), null=False, blank=False, default=0)
    OPTime=models.DateTimeField(_(u'时间'))
    Object=models.IntegerField(_(u'对象'), null=True, blank=True)
    Param1=models.IntegerField(_(u'参数1'), null=True, blank=True)
    Param2=models.IntegerField(_(u'参数2'), null=True, blank=True)
    Param3=models.IntegerField(_(u'参数3'), null=True, blank=True)
    def Device(self):
        return get_device(self.SN_id)
    @staticmethod    
    def delOld(): return ("OPTime", 200)
    def OpName(self):
        return OpName(self.OP)
    def ObjName(self):
        if self.OP==3:
            return AlarmName(self.Object)
        return self.Object or ""
    def __unicode__(self):
        return u"%s,%s,%s"%(self.Device(), self.OP, self.OPTime.strftime("%y-%m-%d %H:%M:%S"))
    class Meta:
        app_label='iclock'
        verbose_name = _(u"操作设备日志")
        verbose_name_plural = verbose_name
        unique_together = (("SN", "OPTime"),)
        permissions = (
            ('monitor_oplog', 'Transaction Monitor'),
            )
    class Admin:
        visible=False
        list_display=('SN','admin','OP','OPTime', 'Object',)
        list_filter = ('SN','admin','OP','OPTime')


