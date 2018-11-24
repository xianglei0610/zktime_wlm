# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
import datetime
from mysite.iclock.models.model_device import CONSUMEMODEL
from mysite.utils import get_option
ACTIOMTYPE=(
            (1,_(u'定值消费')),
            (4,_(u'计次消费')),
            (3,_(u'键值模式')),
            (5,_(u'商品模式')),
            (2,_(u'金额消费')),
            (6,_(u'计时消费')),
            (7,_(u'解挂')),
            (8,_(u'余额查询')),
            (9,_(u'个人明细查询')),
            (10,_(u'个人汇总查询')),
            (11,_(u'设备汇总查询')),
            (12,_(u'超时回滚')),
            (13,_(u'设备参数修改')),
            (14,_(u'挂失')),
            (15,_(u'修改密码')),
            (16,_(u'获取系统时间')),
            (17,_(u'下载管理卡信息')),
            (18,_(u'下载消费错误信息')),
            (19,_(u'系统故障')),
            (20,_(u'下载键值信息')),
            (21,_(u'下载商品信息')),
)
REMARKCONTENT=(
(-1,_(u'系统故障')),
(-2,_(u'正在消费')),
(0,_(u'操作成功')),
(1,_(u'黑名单')),
(2,_(u'无效卡')),
(3,_(u'卡余额不足')),
(4,_(u'管理卡')),
(5,_(u'停用卡')),


(101,_(u'卡片已过有效期')),
(102,_(u'不在消费时间段')),
(103,_(u'无消费权限（卡片不可在此机器上使用）')),
(104,_(u'卡类不存在（发卡时设置了卡类，在卡类信息找不到）')),
(106,_(u'无此餐别消费权限(限制就餐)')),
(107,_(u'系统无餐别(有设置餐限次限额就必须有餐别)')),
(108,_(u'余额异常(余额大于或小于卡类设置的限额)')),


(201,_(u'超出日消费最大金额')),
(203,_(u'超出餐消费最大金额')),
(202,_(u'超出日消费最大次数')),
(204,_(u'超出餐消费最大次数')),


(109,_(u'超出次消费最大金额')),#208
(309,_(u'分段定值无效')),#209
(310,_(u'超出分段定值')),#210


(208,_(u'设备不存在')),#213
(216,_(u'密码错误')),#214
(102,_(u'消费时间段无效')),#系统没有当前消费时间段,211


(120,_(u'回滚成功')),
(212,_(u'没有消费记录')),
(-2,_(u'密码错误')),
(122,_(u'无消费记录')),
(123,_(u'计时消费开始')),
(124,_(u'计时消费成功')),
(300,_(u'没有数据')),
)

#1      黑名单
#2      无效卡
#3      卡余额不足
#4      卡类不存在
#
#101    卡片已过有效期
#102    不在消费时间段
#103    无消费权限（卡片不可在此机器上使用）
#104    卡类不存在（发卡时设置了卡类，在卡类信息找不到）
#105    未定餐(定餐使用)
#106    无此餐别消费权限(限制就餐)
#107    系统无餐别(有设置餐限次限额就必须有餐别)
#108    余额异常(余额大于或小于卡类设置的限额)
#
#
#200    卡片没有登记卡类
#201    超过日消费最大金额
#202    超过日消费最大次数
#203    超过餐别的消费金额限制
#204    超过餐别的消费金额次数
#205    此餐别没有权限
#206    没有在本消费机上消费的权限
#207    卡片状态无法识别


class PosDevLog(CachingModel):
    sn= models.CharField(_(u'序列号'),max_length=20,null=True,blank=True)
    serialnum = models.CharField(_(u'设备流水号'),max_length=20,null=True,blank=True)
    pin = models.CharField(_(u'人员编号'), db_column="badgenumber", null=True, max_length=20)
    carno = models.CharField(_(u'卡号'),max_length=10, null=True, blank=True)
    posmodel = models.IntegerField(_(u'操作类型'),null=True, blank=True,choices=ACTIOMTYPE)
    posOpTime = models.DateTimeField(verbose_name=_(u'操作时间'),default=datetime.datetime.now(),blank=True,editable=True,null=True)
    content = models.CharField(_(u'命令内容'),max_length=200,null=True,blank=True)
    returncon = models.CharField(_(u'返回内容'),max_length=1000,null=True,blank=True)
    remark = models.IntegerField(_(u'备注'),null=True, blank=True,choices=REMARKCONTENT)
    def __unicode__(self): 
        try:
            return u"%s,%s"%(self.sn, self.carno)
        except:
            return u"%s,%s"%(self.sn, self.carno)
    def save(self, **args):
        models.Model.save(self,args)
    class Admin(CachingModel.Admin):
        sort_fields=["-posOpTime",'posOpTime','serialnum']
        app_menu="pos"
        menu_index = 12
        menu_group = 'pos'
        visible = False
        #visible = "mysite.pos" in settings.INSTALLED_APPS#暂只有消费使用
        list_display=['sn','serialnum','pin','carno','posmodel','posOpTime','content','returncon','remark']
        query_fields=['posmodel','pin','carno','posOpTime']
        adv_fields = ['sn','serialnum','posmodel','pin','carno','posOpTime']
        #search_fields = ["OP","Object"]
        disabled_perms=["change_posdevlog","delete_posdevlog","add_posdevlog"]
        search_fields=['posOpTime']
        tstart_end_search={
                              "posOpTime":[_(u"起始时间"),_(u"结束时间")]
                          }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        
    class _delete(Operation):
        help_text = _(u"删除选定记录") #删除选定的记录
        verbose_name = _(u"删除")
        visible=False
        def action(self):
            pass   
              
    class _change(ModelOperation):
        visible=False
        def action(self):
            pass 
        
    class _add(ModelOperation):
        visible=False
        def action(self):
            pass      
    
    class Meta:
        app_label='pos'
        verbose_name = _(u"消费机通讯日志")
        verbose_name_plural=verbose_name
