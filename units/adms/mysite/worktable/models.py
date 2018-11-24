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
from base.cached_model import CachingModel
from base.operation import Operation
from base.options import AppOption
from base.base_code import base_code_by
from django.template.defaultfilters import escapejs
from django.conf import settings
from base.models import AppOperation
from mysite.utils import get_option
from django.db.models import Q
class MsgType(CachingModel):
    msgtype_name=models.CharField(_(u'类别'),null=False, blank=False,max_length=50)
    msgtype_value=models.CharField(_(u'值'),null=False, blank=False,max_length=20,editable=False)
    #公告提前几天提醒
    msg_keep_time=models.IntegerField(_(u'持续(天)'),null=False, blank=False,default=1 ,editable=True)
    #公告结束后延续提醒多少天
    msg_ahead_remind=models.IntegerField(_(u'提前提醒(天)'),null=False, blank=False,default=0 ,editable=True)
    #区分是用户自己添加的还是系统初始化的类别,默认是0，系统初始化的为-1
    type=models.CharField(_(u'类型'),null=False, blank=False,default='0' ,editable=False,max_length=2)
    def __unicode__(self):
            return self.msgtype_name
        
    @staticmethod    
    def clear():
        for e in MsgType.objects.all():
            if e.type != "-1":
                e.delete()
                    
    def delete(self):
        if self.type != "-1":
            if self.instantmsg_set.all().count()>0:
                raise Exception(_(u'正在使用，不能被删除'))
            else:
                super(MsgType,self).delete()
        else:
            raise Exception(_(u"系统默认类别(%s)不能删除!")%self.msgtype_name)
    class Meta:
        #verbose_name=_(u"%(name)s")%{"name":_(u'公告类别')}
        verbose_name=_(u'公告类别')
    def save(self, **args):
        tmp=MsgType.objects.filter(msgtype_name=self.msgtype_name)
        if len(tmp)>0 and tmp[0].id!=self.id:#新增
            raise Exception(_(u'类别不能重复'))
        if self.msg_keep_time>99 or self.msg_ahead_remind>99 or self.msg_keep_time <0 or self.msg_ahead_remind <0 :
            raise Exception(_(u'提前天数或持续天数必须是0到99之间！'))
        
        super(MsgType,self).save(**args)
    
    
    class Admin(CachingModel.Admin):
        report_fields=["msgtype_name","msgtype_value","msg_keep_time","create_time"]
        menu_index=501
        visible=get_option("WORKTABLE_MSGTYPE_VISIBLE")
#        visible = not (("mysite.pos" in settings.INSTALLED_APPS)and("mysite.iaccess" in settings.INSTALLED_APPS) and ("mysite.att" in settings.INSTALLED_APPS) and settings.ZKACCESS_ATT)#暂只有考勤使用，当门禁带简单考勤时屏蔽
        @staticmethod
        def initial_data():
            if not MsgType.objects.filter(msgtype_name=u"%(name)s"%{"name":_(u'系统')}, msgtype_value='9') :
                    MsgType(id=1,msgtype_name=u"%(name)s"%{"name":_(u'系统')},msgtype_value='9',type='-1').save()
            if not MsgType.objects.filter(msgtype_name=u"%(name)s"%{"name":_(u'考勤')}, msgtype_value='8') and "mysite.att" in settings.INSTALLED_APPS:
                    MsgType(id=2,msgtype_name=u"%(name)s"%{"name":_(u'考勤')},msgtype_value='8',type='-1').save()
            if not MsgType.objects.filter(msgtype_name=u"%(name)s"%{"name":_(u'门禁')}, msgtype_value='7') and "mysite.iaccess" in settings.INSTALLED_APPS:
                    MsgType(id=3,msgtype_name=u"%(name)s"%{"name":_(u'门禁')},msgtype_value='7',type='-1').save()
            if not MsgType.objects.filter(msgtype_name=u"%(name)s"%{"name":_(u'人事')}, msgtype_value='6'):
                    MsgType(id=4,msgtype_name=u"%(name)s"%{"name":_(u'人事')},msgtype_value='6',type='-1').save()
            if not MsgType.objects.filter(msgtype_name=u"%(name)s"%{"name":_(u'消费')}, msgtype_value='10') and "mysite.pos" in settings.INSTALLED_APPS:
                   MsgType(id=5,msgtype_name=u"%(name)s"%{"name":_(u'消费')},msgtype_value='10',type='-1').save()
            if not MsgType.objects.filter(msgtype_name=u"%(name)s"%{"name":_(u'会议')}, msgtype_value='11') and "mysite.meeting" in settings.INSTALLED_APPS:
                    MsgType(id=5,msgtype_name=u"%(name)s"%{"name":_(u'会议')},msgtype_value='11',type='-1').save()
                
            
            
            
        #help_text="系统提示设置是用来设置属于该角色的用户能够看到哪类消息！"
        app_menu="base"
        menu_group = 'base'
        list_display=['msgtype_name','msg_keep_time','msg_ahead_remind']
    
    
class GroupMsg(CachingModel):
    msgtype = models.ForeignKey(MsgType, verbose_name=_(u'类别'), null=False, blank=False,editable=True)
    group = models.ForeignKey(Group, verbose_name=_(u'分配给角色'),limit_choices_to=~Q(**{'name':'role_for_employee'}), null=False, blank=False, editable=True)
    def save(self, **args):
        tmp=GroupMsg.objects.filter(msgtype=self.msgtype,group=self.group)
        if len(tmp)>0 and tmp[0].id!=self.id:#新增
            raise Exception(_(u'\"%(f)s\"已经分配过给\"%(ff)s\"角色')%{"f":self.msgtype.msgtype_name,"ff":self.group.name})
        super(GroupMsg,self).save(**args)
    def __unicode__(self):
          return self.group.name
    class Admin(CachingModel.Admin):
        menu_index=503
        visible=get_option("WORKTABLE_GROUPMSG_VISIBLE")
#        visible = not (("mysite.iaccess" in settings.INSTALLED_APPS) and ("mysite.att" in settings.INSTALLED_APPS) and settings.ZKACCESS_ATT)#暂只有考勤使用，当门禁带简单考勤时屏蔽
        help_text=_(u"系统提醒设置用于将公告分配给不同的角色查看。")
        app_menu="base"
        menu_group = 'base'
        list_display=['group','msgtype']
    class Meta:
        verbose_name=_(u'系统提醒设置')
    
class UsrMsg(CachingModel):
    user= models.ForeignKey(User, verbose_name=_(u'用户'), null=True, blank=True, editable=True)
    msg = models.ForeignKey("InstantMsg", verbose_name=_(u'消息'), null=True, blank=True, editable=True) 
    readtype=models.CharField(_(u'标记'),blank=True,null=True,max_length=20)
    #def __unicode__(self):
           #return u"%s,%s"%(self.user._meta.verbose_name,self.msg)
    class Admin(CachingModel.Admin):
        app_menu="base"
        visible=False
    class Meta:
        verbose_name=_(u'用户消息确认')
    
class InstantMsg(CachingModel):
    monitor_last_time = models.DateTimeField(editable=False,db_column='monitor last time',null=True,blank=True)
    msgtype = models.ForeignKey(MsgType, verbose_name=_(u'类别'), null=False, blank=False,editable=True)
    content = models.TextField(_(u'公告内容'),max_length=100,null=True, blank=True)
    def __unicode__(self):
        return self.msgtype.msgtype_name+","+escapejs(self.content[:10]) 
    def save(self, **args):
        if len(self.content)>100:
            raise Exception(_(u'公告内容不能超过100字符！'))
        #if(not InstantMsg.objects.filter(content=self.content).exists()):
        super(InstantMsg,self).save(**args)
    
    class Admin(CachingModel.Admin):
        menu_index=502
        visible= get_option("WORKTABLE_INSTANTMSG_VISIBLE")
        app_menu="base"
        menu_group = 'base'
        list_display= ['msgtype','content']
        report_fields=["monitor_last_time","msgtype"]
    class Meta:
        verbose_name=_(u'公告发布')

import clean_data

class DeleteData(AppOperation):
        u'''清除数据'''
        verbose_name=_(u'临时数据清理')
        view=clean_data.get_html_data
        _app_menu="base"
        _menu_index = 99999
        visible = get_option("WORKTABLE_DELETEDATA")


def app_options():
    from base.options import  SYSPARAM,PERSONAL
    return (
        #参数名称, 参数默认值，参数显示名称，解释,参数类别
        #('msg_scanner', '07:01', u'消息监控时间','',SYSPARAM,True),
        )
