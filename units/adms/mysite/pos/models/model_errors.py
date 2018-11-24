#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

import datetime
import string
import os

class Errors(CachingModel):
    errno = models.CharField(max_length=10,verbose_name=_(u'错误编号'),editable=False)
    errmsg = models.CharField(max_length=20,verbose_name=_(u'错误名称'),editable=False)
    errmemo = models.CharField(max_length=20,verbose_name=_(u'错误解释'),editable=False,null=True,blank=True)
    
    def __unicode__(self):
        return u"%s %s %s"% (self.errno,self.errmsg,self.errmemo)
    

    def delete(self):   
            pass
    class Admin(CachingModel.Admin):
                sort_fields=["errno"]
                visible=False
                app_menu="pos"
                menu_group = 'pos'
                menu_index =4
                query_fields=['errno','errmsg','errmemo']
                adv_fields=['errno','errmsg','errmemo']
                list_display=['errno','errmsg','errmemo']
                help_text = _(u'消费机错误信息')
                @staticmethod
                def initial_data(): 
                        if Errors.objects.count()==0:                           
                            Errors(errno=1,errmsg=u"%s"%_(u"黑名单"),errmemo=u"%s"%_(u"黑名单卡"),).save()#1
                            Errors(errno=2,errmsg=u"%s"%_(u"无效卡"),errmemo=u"%s"%_(u"无效卡"),).save()#1
                            Errors(errno=3,errmsg=u"%s"%_(u"卡余额不足"),errmemo=u"%s"%_(u"卡余额不足"),).save()#1
                            Errors(errno=101,errmsg=u"%s"%_(u"卡片已过有效期"),errmemo=u"%s"%_(u"卡片已过有效期"),).save()#1
                            Errors(errno=102,errmsg=u"%s"%_(u"不在消费时间段"),errmemo=u"%s"%_(u"不在消费时间段"),).save()#1
                            Errors(errno=103,errmsg=u"%s"%_(u"无消费权限"),errmemo=u"%s"%_(u"卡片不可在此机器上使用"),).save()#1
                            Errors(errno=104,errmsg=u"%s"%_(u"卡类不存在"),errmemo=u"%s"%_(u"发卡时设置了卡类，在卡类信息找不到"),).save()#1
                            Errors(errno=105,errmsg=u"%s"%_(u"未定餐"),errmemo=u"%s"%_(u"定餐使用"),).save()#1
                            Errors(errno=106,errmsg=u"%s"%_(u"无此餐别权限"),errmemo=u"%s"%_(u"限制就餐"),).save()#1
                            Errors(errno=107,errmsg=u"%s"%_(u"系统无此餐别"),errmemo=u"%s"%_(u"黑名单卡"),).save()#1
                            Errors(errno=108,errmsg=u"%s"%_(u"余额异常"),errmemo=u"%s"%_(u"余额大于或小于卡类设置的限额"),).save()#1
                            Errors(errno=201,errmsg=u"%s"%_(u"日消费超额"),errmemo=u"%s"%_(u"超过日消费最大金额"),).save()#1
                            Errors(errno=202,errmsg=u"%s"%_(u"日消费超次"),errmemo=u"%s"%_(u"超过日消费最大次数"),).save()#1
                            Errors(errno=203,errmsg=u"%s"%_(u"餐消费超额"),errmemo=u"%s"%_(u"超过餐别的消费金额限制"),).save()#1
                            Errors(errno=204,errmsg=u"%s"%_(u"餐消费超次"),errmemo=u"%s"%_(u"超过餐别的消费金额次数"),).save()#1
                            Errors(errno=109,errmsg=u"%s"%_(u"单次消费超额"),errmemo=u"%s"%_(u"超出次消费最大金额"),).save()#1
                            Errors(errno=309,errmsg=u"%s"%_(u"分段定值无效"),errmemo=u"%s"%_(u"系统没有分段定值"),).save()#1
                            Errors(errno=310,errmsg=u"%s"%_(u"超出分段定值时间"),errmemo=u"%s"%_(u"超出分段定值"),).save()#1
                            Errors(errno=208,errmsg=u"%s"%_(u"设备不存在"),errmemo=u"%s"%_(u"设备没有注册"),).save()#1
#                            Errors(errno=102,errmsg=u"%s"%_(u"消费时间段无效"),errmemo=u"%s"%_(u"系统没有设置消费时间段"),).save()#1
                            Errors(errno=314,errmsg=u"%s"%_(u"超出卡最小余额"),errmemo=u"%s"%_(u"超出卡最小余额"),).save()#1
                            Errors(errno=315,errmsg=u"%s"%_(u"超出卡最大余额"),errmemo=u"%s"%_(u"超出卡最大余额"),).save()#1
                            Errors(errno=216,errmsg=u"%s"%_(u"密码错误"),errmemo=u"%s"%_(u"挂失解挂改密密码错误"),).save()#1
                        pass
                
    class Meta:
            verbose_name=_(u'错误信息')
            verbose_name_plural=verbose_name
            app_label='pos'
