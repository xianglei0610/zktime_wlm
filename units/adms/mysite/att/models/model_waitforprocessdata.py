# -*- coding: utf-8 -*-
from django.db import models, connection


from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey

from base.cached_model import CachingModel
from base.operation import Operation,ModelOperation

#from mysite.sitebackend.models import Customer

PROCESSFLAG=(
    (1,_(u'未处理')),
    (2,_(u'处理完成')),
    (3,_(u'处理失败')),
)
class WaitForProcessData(CachingModel):
    UserID=EmpForeignKey(verbose_name=_(u'人员'))
    starttime=models.DateTimeField(_(u'开始时间'),null=False,blank=False)
    endtime=models.DateTimeField(_(u'结束时间'),null=False,blank=False)
    #customer=models.ForeignKey(Customer,verbose_name=_(u'客户'),blank=True,null=True)
    flag=models.IntegerField(_(u'处理标志'),null=False,blank=False,default=1,choices=PROCESSFLAG)    
    
    def save(self, **args):
        super(WaitForProcessData, self).save(log_msg=False)
    
    class Admin(CachingModel.Admin):
        visible=False
        verbose_name=_(u'后台计算命令队列')
    class Meta:
        app_label="att"