#!/usr/bin/python
# -*- coding: utf-8 -*-
from mysite.personnel.models.model_emp import EmpForeignKey
from model_device import DeviceForeignKey,FPVERSION
from django.db import models
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel
from django.core.cache import cache


BOOLEANS=((0,_(u"否")),(1,_(u"是")),)
FINGERIDS=(
    (0, _(u'左手小指')),
    (1, _(u'左手无名指')),
    (2, _(u'左手中指')),
    (3, _(u'左手食指')),
    (4, _(u'左手拇指')),
    (5, _(u'右手拇指')),
    (6, _(u'右手食指')),
    (7, _(u'右手中指')),
    (8, _(u'右手无名指')),
    (9, _(u'右手小指')),
)

class Template(CachingModel):
    id=models.AutoField(db_column='templateid',primary_key=True)
    UserID = models.CharField(db_column='pin', verbose_name=u"员工", max_length=20)
    Template = models.TextField(_(u'指纹模板'))
    FingerID = models.SmallIntegerField(_(u'手指'),default=0, choices=FINGERIDS)
    Valid = models.SmallIntegerField(_(u'指纹类别'),default=1, choices=BOOLEANS)
    
    Fpversion=models.CharField(verbose_name=_(u'指纹版本'), max_length=10, null=False, blank=False, editable=False,default='9',choices=FPVERSION)
    
    bio_type = models.SmallIntegerField(choices=((0,_(u"指纹")),(1,_(u'人脸'))),default=0)
    SN = models.CharField(db_column='SN', verbose_name=_(u'登记设备'), null=True, blank=True,max_length=20)
    UTime = models.DateTimeField(_(u'更新时间'), null=True, blank=True, editable=False)
    BITMAPPICTURE=models.TextField(null=True,editable=False)
    BITMAPPICTURE2=models.TextField(null=True,editable=False)
    BITMAPPICTURE3=models.TextField(null=True,editable=False)
    BITMAPPICTURE4=models.TextField(null=True,editable=False)
    USETYPE = models.SmallIntegerField(null=True, editable=False)
    Template2 = models.TextField(_(u'指纹模板'),null=True,editable=False)
    Template3 = models.TextField(_(u'指纹模板'),null=True,editable=False)

    def __unicode__(self):
        #print '---self.FingerID=',self.FingerID, type(self.FingerID)
        return u"%s, %s"%(unicode(self.UserID), unicode(self.FingerID))

    def template(self):
        return self.Template.decode("base64")
    
    def cache_template_count(self,is_new):
        u'''缓存模板数量'''
        from mysite.personnel.cache import PERSONNEL_EMP_T_COUNT,TIMEOUT
        if is_new:
            cache_key=PERSONNEL_EMP_T_COUNT+str(self.UserID)
            cache_t_count=cache.get(cache_key)
            if cache_t_count:
                if self.Fpversion=="9":
                    cache_t_count["9"]=cache_t_count["9"]+1
                if self.Fpversion=="10":
                    cache_t_count["10"]=cache_t_count["10"]+1
    
                cache.set(cache_key,cache_t_count,TIMEOUT)
            
    
    def delete_template_count(self):
        u'''删除模板缓存'''
        from mysite.personnel.cache import PERSONNEL_EMP_T_COUNT,TIMEOUT
        cache_key=PERSONNEL_EMP_T_COUNT+str(self.UserID)
        cache_t_count=cache.get(cache_key)
        if cache_t_count:
            if self.Fpversion=="9":
                cache_t_count["9"]=cache_t_count["9"]-1
            if self.Fpversion=="10":
                cache_t_count["10"]=cache_t_count["10"]-1
        
            cache.set(cache_key,cache_t_count,TIMEOUT)
            
    def delete(self):
        u'''删除指纹'''
        self.delete_template_count()
        super(Template,self).delete()
        
    def save(self,**kargs):
        is_new = False
        if not self.pk:
            is_new = True
        models.Model.save(self, kargs)
        
        self.cache_template_count(is_new)
    
    def temp(self):
        #去掉BASE64编码的指纹模板中的回车
        return self.Template.replace("\n","").replace("\r","")

    class Admin(CachingModel.Admin):
        list_display=('UserID', 'FingerID', 'Valid', 'DelTag')
        list_filter = ('UserID','SN','UTime',)
        report_fields=['UserID', 'FingerID', 'Valid']
        visible=False
    class Meta:
        app_label='iclock'
        db_table = 'finger_template'
        unique_together = (("UserID", "FingerID","Fpversion"),)
        verbose_name = _(u"人员指纹")
        verbose_name_plural=verbose_name
