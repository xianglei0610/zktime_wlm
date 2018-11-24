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
import os
from mysite.utils import printf, write_log
from mysite.iclock.cache_cmds import set_last_save_cmd_pk
from mysite.utils import get_option
try:
    import cPickle as pickle
except:
    import pickle
import time

DEVICE_TIME_RECORDER = 1
DEVICE_ACCESS_CONTROL_PANEL = 2
DEVICE_ACCESS_CONTROL_DEVICE = 3
DEVICE_VIDEO_SERVER =4
DEVICE_POS_SERVER = 5


#门禁---考勤通用
def trigger_cmd_device(cmd_obj):
    #写入新命令队列
    old_cmd=0
    write_log('---------in trigger_cmd_device cmd_obj=%s'%cmd_obj)
    try:
        q_server = queqe_server()
        d_server = start_dict_server()
        cln = cmd_obj.SN.new_command_list_name()#NEWCMD_*
        #向文件缓存和dict中同时写入新命令
        dev = cmd_obj.SN
        #命令总数
        cntkey = dev.command_count_key()
        #print '---cntkey=',cntkey
        cnt = d_server.get_from_dict(cntkey)#从dict中取
        old_cmd = q_server.llen_file(cln)
        write_log('---cmd_obj=%s,---cnt=%s,-----old_cmd=%s'%(cmd_obj,cnt,old_cmd))
        if cnt is None:
           cnt = str(old_cmd)
           write_log('------devcmd get length from file-cnt=%s'%cnt)
        if cnt.find('\x00'):
           cnt = cnt.strip('\x00')
        #q_server.set(cntkey, "%d"%(int(cnt)+1))

        if dev.device_type == DEVICE_ACCESS_CONTROL_PANEL and cmd_obj.CmdImmediately: 
            timeout = 0
            while True:
                temp_cmd_lock = d_server.get_from_dict("TEMP_CMD_LOCK")
                if temp_cmd_lock:#如果当前其他线程或者进程在进行同样的操作，等待
                    write_log('--------!cmd_obj=%s temp_cmd_lock=%s timeout=%s'%(cmd_obj, temp_cmd_lock, timeout))
                    timeout += 1
                    if timeout > 300:
                        break#超时后不放入缓存
                    time.sleep(0.5)
                    continue
                else:
                    d_server.set_to_dict("TEMP_CMD_LOCK", 1)
                    immed_cmd_dict = d_server.get_from_dict("TEMP_CMD")
                    write_log('-devcmd-before immed_cmd_dict=%s, cmd_obj=%s'%(immed_cmd_dict, cmd_obj))
                    if not immed_cmd_dict:
                        immed_cmd_dict = {}
                        immed_cmd_dict.setdefault(dev.id, [cmd_obj])
                    else:
                        devcmds = immed_cmd_dict.get(dev.id) or []#获取到当前设备对应的所有的紧急命令
#                        if devcmds:
#                            devcmds.append(cmd_obj)
#                        else:
#                            devcmds = []
                        devcmds.append(cmd_obj)
                        immed_cmd_dict[dev.id] = devcmds
                    write_log('-devcmd-before set_to_dict cmd_obj=%s,immed_cmd_dict=%s'%(cmd_obj, immed_cmd_dict))
                    d_server.set_to_dict("TEMP_CMD", immed_cmd_dict)
                    d_server.set_to_dict("TEMP_CMD_LOCK", 0)
                    #immed_cmd_dict = d_server.get_from_dict("TEMP_CMD")
                    #write_log('-devcmd-after cmd_obj=%s,immed_cmd_dict=%s'%(cmd_obj, immed_cmd_dict))
                    #time.sleep(1)
                    #immed_cmd_dict = d_server.get_from_dict("TEMP_CMD")
                    #printf('-devcmd-after 5s cmd_obj=%s, immed_cmd_dict=%s'%(cmd_obj, immed_cmd_dict), True)
                    break
                #print d_server.get_from_dict("TEMP_CMD"),'-----------devcmds'
        else:    
            write_log('-------------------file catch')
            q_server.lpush_to_file(cln, pickle.dumps(cmd_obj))
        if not cmd_obj.CmdImmediately:
            d_server.set_to_dict(cntkey, "%d"%(int(cnt)+1))#命令总数写入dict
        write_log('---cmd_obj=%s--cnt========%s'%(cmd_obj, d_server.get_from_dict(cntkey)))
        q_server.connection.disconnect()
    except:
        print_exc()
    if not (dev.comm_type==COMMU_MODE_PUSH_HTTP): #门禁设备不须通知
        return
    pass
    #UDP 广播通知设备来读取命令
    if old_cmd: #若新命令队列不空，说明设备上次的命令还没有执行，不需要再次通知设备
        return  
    try:
        ip=cmd_obj.SN.ipaddress
        sNotify = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if ip: sNotify.sendto("R-CMD", (ip, 4374))
    except:
        print_exc()


CMDRETURN=(
    (-1, _(u"参数错误")),
    (-3, _(u"机器存取错误")),
    (-10 ,_(u"用户不存在")), 
    (-11, _(u"非法的指纹模板格式")),
    (-12, _(u"非法的指纹模板")),
)
class DevCmd(CachingModel):
    SN = DeviceForeignKey(verbose_name=_(u'设备'), null=True)
    CmdOperate = models.ForeignKey(OperateCmd, verbose_name = _(u'操作任务'), null=True)
    CmdContent = models.TextField(_(u'命令内容'),max_length=2048)
    CmdCommitTime = models.DateTimeField(_(u'提交时间'),default=datetime.datetime.now())
    CmdTransTime = models.DateTimeField(_(u'传送时间'),null=True, blank=True)
    CmdOverTime = models.DateTimeField(_(u'返回时间'),null=True, blank=True)
    CmdReturn = models.IntegerField(_(u'返回值'), null=True, blank=True)
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
        
#        try:
#            return u"%s, %s" % (self.SN, fmt_shortdatetime(self.CmdCommitTime))
#        except:
#            return u"%s, %s" % (self.SN_id, fmt_shortdatetime(self.CmdCommitTime))
    
    def save(self, **kargs):
        is_new = False
        if not self.pk:
            is_new = True
        if not self.CmdCommitTime: 
            self.CmdCommitTime=datetime.datetime.now()
            
        ret = models.Model.save(self, kargs)
        
        if is_new and self.SN and self.SN.device_type in [DEVICE_TIME_RECORDER,DEVICE_POS_SERVER]:#新增
            #更新缓存中该设备的最后一条命令
            set_last_save_cmd_pk(self.SN_id,self.pk)
        
        #加入判断  仅门禁
        if  self.SN and  self.SN.device_type==DEVICE_ACCESS_CONTROL_PANEL and not self.CmdTransTime:
            trigger_cmd_device(self)
        return ret
    
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
        verbose_name = _(u'''清空命令表''')
        help_text = _(u"清空服务器下发命令表。")
        tips_text =  _(u"确认要清空命令表")
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
        visible = get_option("ATT") or get_option("IACCESS") or get_option("POS_IC")
        #sort_fields = ["SN.sn","CmdCommitTime","CmdTransTime","CmdOverTime"]
        #list_display=('SN.alias','SN.sn','CmdCommitTime|fmt_shortdatetime','CmdTransTime|fmt_shortdatetime','CmdOverTime|fmt_shortdatetime','get_cmdcontent','CmdReturn')
        list_display=('SN.alias','SN.sn','CmdCommitTime','CmdTransTime','CmdOverTime','get_cmdcontent','CmdReturn')
        newadded_column={
            "SN.alias":"get_device_alias",
            "SN.sn":"get_device_sn",
        }
        adv_fields=('SN.sn', 'SN.alias','CmdCommitTime','CmdTransTime','CmdOverTime','CmdContent','CmdReturn')
        search_fields = ["CmdContent"]
        list_filter =['SN', 'CmdCommitTime', 'CmdOverTime']
        query_fields=['SN.sn', 'CmdReturn','SN.device_type',]
        disabled_perms = ["change_devcmd", "add_devcmd", "dataexport_devcmd"]#"dataexport_devcmd"]"delete_devcmd"
   
    class Meta:
        app_label='iclock'
        db_table = 'devcmds'
        verbose_name = _(u"服务器下发命令")
        verbose_name_plural=verbose_name
