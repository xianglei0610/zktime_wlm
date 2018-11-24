#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from django.conf import settings
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from model_device import DeviceForeignKey, COMMU_MODE_PUSH_HTTP, DEVICE_ACCESS_CONTROL_PANEL
from model_devoperate import OperateCmd
import datetime
from traceback import print_exc
from base.operation import OperationBase, Operation, ModelOperation
import socket
from redis_self.server import queqe_server, start_dict_server
import threading
from base.operation import OperationBase, Operation
from mysite.iclock.cache_cmds import set_last_save_cmd_pk
from mysite import settings 
from mysite.utils import get_option
DEVICE_TIME_RECORDER = 1
DEVICE_ACCESS_CONTROL_PANEL = 2
DEVICE_ACCESS_CONTROL_DEVICE = 3
DEVICE_VIDEO_SERVER =4


CMDRETURN=(
    (-1, _(u"参数错误")),
    (-3, _(u"机器存取错误")),
    (-10 ,_(u"用户不存在")), 
    (-11, _(u"非法的指纹模板格式")),
    (-12, _(u"非法的指纹模板")),
)


class DevCmdBak(CachingModel):
    SN = DeviceForeignKey(verbose_name=_(u'设备'), null=True)
    CmdOperate = models.ForeignKey(OperateCmd, verbose_name = _(u'操作任务'), null=True)
    CmdContent = models.TextField(_(u'命令内容'),max_length=2048)
    CmdCommitTime = models.DateTimeField(_(u'提交时间'),default=datetime.datetime.now())
    CmdTransTime = models.DateTimeField(_(u'传送时间'),null=True, blank=True)
    CmdOverTime = models.DateTimeField(_(u'返回时间'),null=True, blank=True)
    CmdReturn = models.IntegerField(_(u'返回值'), null=True, blank=True,choices=CMDRETURN)
    CmdReturnContent = models.TextField(_(u'返回内容'), null=True, blank=True)
    CmdImmediately=models.BooleanField(_(u'是否是立即备份'), default=False)
    
    def device(self):
        return get_device(self.SN_id)
    
    class _delete(Operation):
        help_text=_(u"删除选定记录") #删除选定的记录
        verbose_name=_(u"删除")
        def action(self):
                self.object.delete()
    
    def __unicode__(self): 
        from base.templatetags.base_tags import fmt_shortdatetime
        from mysite.iclock.models.model_device import get_device
        try:
            return u"%s, %s" % (get_device(self.SN_id), self.CmdCommitTime)
        except:
            return u"%s, %s" % (self.SN_id, self.CmdCommitTime)
    
    def save(self, **kargs):
        if not self.CmdCommitTime: 
            self.CmdCommitTime=datetime.datetime.now()
            
        ret = models.Model.save(self, kargs)
    
    def file_url(self):
        if self.CmdContent.find("GetFile ")==0:
            fname=self.CmdContent[8:]
        elif self.CmdContent.find("Shell ")==0:
            fname="shellout.txt"
        else:
            return ""
        return getUploadFileURL(self.SN.SN, self.id, fname)
    class dataexport(Operation):
        help_text=_(u"数据导出") #导出
        verbose_name=u"导出"
        visible=False
        def action(self):
                pass

    class OpClearDevCmd(ModelOperation):
        verbose_name = _(u'''清空失败命令''')
        help_text = _(u"清空服务器失败命令")
        tips_text =  _(u"确认要清空失败命令")
        def action(self):
            self.model.objects.all().delete()

    #修正命令长度过长导致浏览器崩溃的bug，只保留前200个字符
    def get_cmdcontent(self):
        content = self.CmdContent[0:200]
        if len(content) == 200:
            return content+'...'
        return content
    def get_device_sn(self):
        from mysite.iclock.models.model_device import get_device_attr
        return get_device_attr(self.SN_id,"sn")
    
    def get_device_alias(self):
        from mysite.iclock.models.model_device import get_device_attr
        return get_device_attr(self.SN_id,"alias")
    
    class Admin(CachingModel.Admin):
        sort_fields = ["SN.sn","CmdCommitTime","CmdTransTime","CmdOverTime"]
        list_display=('SN.alias','SN.sn','CmdCommitTime','CmdTransTime','CmdOverTime','get_cmdcontent','CmdReturn')
        adv_fields=('SN.sn', 'SN.alias','CmdCommitTime','CmdTransTime','CmdOverTime','CmdContent','CmdReturn')
        newadded_column={
            "SN.alias":"get_device_alias",
            "SN.sn":"get_device_sn",
        }
        search_fields = ["CmdContent"]
        list_filter =['SN', 'CmdCommitTime', 'CmdOverTime']
        query_fields=['SN.alias', 'SN.sn', 'CmdReturn','SN.device_type']
        disabled_perms = ["change_devcmdbak", "add_devcmdbak", "dataexport_devcmdbak"]
        visible = get_option("DECMDBAk_VISIBLE")
   
    class Meta:
        app_label='iclock'
        db_table = 'devcmds_bak'
        verbose_name = _(u"失败命令查询")
        verbose_name_plural=verbose_name
