#! /usr/bin/env python
#coding=utf-8
from mysite.personnel.models.model_emp import EmpForeignKey
from model_device import DeviceForeignKey
from django.db import models
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel


BOOLEANS=((0,_(u"否")),(1,_(u"是")),)


class FaceTemplate(CachingModel):
    id=models.AutoField(db_column='templateid',primary_key=True)
    user = models.CharField(db_column='pin', verbose_name=u"员工",max_length=20)
    facetemp = models.TextField(_(u'人面模板'))
    faceid = models.SmallIntegerField(_(u'面部序号'),default=0)
    sn = models.CharField(db_column='sn', verbose_name=_(u'登记设备'), null=True, blank=True,max_length=20)
    utime = models.DateTimeField(_(u'更新时间'), null=True, blank=True, editable=False)
    valid = models.SmallIntegerField(_(u'是否有效'),default=1, choices=BOOLEANS)
    face_ver = models.CharField(_(u'人脸算法版本'), max_length=30, null=True, blank=True, editable=False) #-----------------------
    def __unicode__(self):
        #print '---self.FingerID=',self.FingerID, type(self.FingerID)
        return u"%s, %s,%s"%(unicode(self.user), unicode(self.faceid),unicode(self.face_ver))

    def template(self):
        return self.facetemp.decode("base64")

    def temp(self):
        #去掉BASE64编码的指纹模板中的回车
        return self.facetemp.replace("\n","").replace("\r","")

    class Admin(CachingModel.Admin):
        list_display=('user', 'faceid', 'valid', 'deltag')
        list_filter = ('user','sn','utime',)
        report_fields=['user', 'faceid', 'valid']
        visible=False
    class Meta:
        app_label='iclock'
        db_table = 'face_template'
        unique_together = (("user", "faceid","face_ver"),)
        verbose_name = _(u"人员面部模板")
        verbose_name_plural=verbose_name
