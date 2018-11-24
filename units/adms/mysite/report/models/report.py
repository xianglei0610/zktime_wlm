# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from base.models import CachingModel
from django.contrib.auth.models import User
from report_type import ReportType
from base.operation import Operation
class Report(CachingModel):
    name=models.CharField(max_length=20,verbose_name=_(u'报表名称'),editable=True)
    report_type=models.ForeignKey(ReportType,verbose_name=_(u'报表类别'),null=True,blank=True,editable=True)
    user=models.ForeignKey(User,verbose_name=_(u'所属用户'),null=True,blank=True,editable=False)
    json_data=models.TextField(_(u'报表json字符串'),null=True,blank=True)
    remark=models.CharField(max_length=300,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
    class Admin(CachingModel.Admin):
        query_fields=["name","user__username","remark"]
        list_display=["name","report_type.name","user"]
        menu_index=2
    class Meta:
        verbose_name=_(u'报表设计')
        verbose_name_plural=verbose_name
        app_label='report'
    class ViewReport(Operation):
        help_text = _(u"预览")
        verbose_name = _(u"预览报表")
        only_one_object = True
        def action(self):
            pass
        
    class DownloadReport(Operation):
        help_text = _(u"下载") 
        verbose_name = _(u"下载报表")
        only_one_object = True
        def action(self):
            pass
    
    
    def save(self,**args):
        args["log_msg"]=False
        #json_data的字符串太长，日记记录里面保存不了
        super(Report,self).save(**args)
    def __unicode__(self):
        return u"%s"%self.name