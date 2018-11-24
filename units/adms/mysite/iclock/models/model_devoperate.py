# -*- coding: utf-8 -*-
#! /usr/bin/env python
import datetime
from django.db import models, connection
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from base.operation import OperationBase, Operation, ModelOperation
from base.cached_model import CachingModel
from django.conf import settings
from mysite.utils import get_option
CMM_TYPE=(
	(1,_(u'设备自动命令')),
	(2,_(u'用户下发命令')),
)
SUCCESS_FLAG=(
	(0,_(u'未处理')),
	(1,_(u'成功')),	
	(2,_(u'失败')),
)
CMM_SYSTEM=(
    (1,_(u'门禁')),
    (2,_(u'考勤')),
)

class OperateCmd(CachingModel):
    Author=models.ForeignKey(User, null=True,blank=True) 
    CmdContent = models.TextField(verbose_name=_(u'命令描述'),max_length=2048)
    CmdCommitTime = models.DateTimeField( verbose_name=_(u'命令创建时间'),default=datetime.datetime.now())
    commit_time = models.DateTimeField(verbose_name=_(u'命令处理完成时间'), null=True, blank=True)
    CmdReturn = models.IntegerField(_(u'返回值'),  null=True, blank=True)
    process_count=models.SmallIntegerField(verbose_name=_(u'处理次数'),default=0)
    success_flag=models.SmallIntegerField(verbose_name=_(u'处理标志'),default=0,choices=SUCCESS_FLAG)
    receive_data = models.TextField(verbose_name=_(u'命令数据'), null=True, blank=True)
    cmm_type=models.SmallIntegerField(verbose_name=_(u'命令类型'),default=1,blank=False,null=False,choices=CMM_TYPE)
    cmm_system=models.SmallIntegerField(verbose_name=_(u'命令系统'),default=1,blank=False,null=False,choices=CMM_SYSTEM)
    class Admin(CachingModel.Admin):
        list_display=('create_operator','CmdCommitTime','cmm_type','CmdContent','commit_time','process_count','success_flag',)
        sort_fields =["create_operator","CmdCommitTime","commit_time","success_flag"]
        search_fields = ["CmdContent"]        
        query_fields=('cmm_type','process_count','success_flag')
        cache=False
        read_only=True
        log=False
        visible = get_option("DEVOPERATE_VISIBLE")#暂只有考勤使用
        disabled_perms=["add_operatecmd",'change_operatecmd','delete_operatecmd']
        hide_perms=["dataexport_operatecmd",]
        
    class Meta:
        app_label='iclock'
        db_table = 'operatecmds'
        verbose_name = _(u'通信命令详情')
        verbose_name_plural=verbose_name
        
    def save(self, *args, **kwargs):
        super(OperateCmd, self).save(log_msg=False)
    @staticmethod    
    def clear():
		OperateCmd.objects.all().delete()
        
    class _delete(Operation):
        verbose_name=_(u'删除')
        visible=False
        def action():
            pass        
    class _add(Operation):
        visible=False
        verbose_name=_(u'新增')
        def action():
            pass
    class _change(Operation):
        visible=False
        verbose_name=_(u'编辑')
        def action():
            pass
    def get_process_status(self):
        total=self.devcmd_set.all().count()
        current=self.devcmd_set.filter(CmdOverTime__isnull=False).count()
        from decimal import ROUND_HALF_UP,Decimal
        if total>0:
            return str(Decimal(str(float(current)/float(total)*100)).quantize(Decimal('0'),ROUND_HALF_UP))+"%"
        else:
            if self.success_flag==1:
                return "100%"
            else:
                return "0%"
    def limit_operatecmd_to(self,qs,user):
        from django.db.models import Q
        filter={'cmm_system':2}
       
        if  user.is_superuser:
            
            pass
        else:
            
            filter['create_operator__exact']=u"%s"%user
        
        return qs.filter(Q(**filter))
            
    


