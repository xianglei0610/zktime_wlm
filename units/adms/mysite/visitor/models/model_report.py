# -*- coding: utf-8 -*-
from django.db import models, connection
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation, ModelOperation
from django import forms
from base.base_code import BaseCode, base_code_by
from mysite.personnel.models.model_emp import YESORNO
from model_visitor import CERTIFICATE_TYPES, VISIT_REASON, CAR_TYPE, VISIT_STATE


class ReportManage(CachingModel):
    """
    访客来访历史记录
    """
    visited_emp_pin = models.CharField(_(u'被访人编号'), max_length=9, null=True, blank=True)
    visited_person = models.CharField(_(u'被访人'), null=True, max_length=24, blank=True, default='')
    dept = models.CharField(_(u'部门'),  max_length=20, null=True, blank=True)
    visitor_pin = models.CharField(_(u'访客编号'), max_length=9, null=True, blank=True)#
    visitor = models.CharField(_(u'访客'), null=False, max_length=24, blank=True, default="")
    visit_number = models.IntegerField(_(u'来访人数'), null=True, blank=True)
    card = models.CharField(_(u'卡号'), max_length=20, null=True, blank=True, editable=True)
    visitor_company = models.CharField(_(u'来访单位'), null=True, max_length=50, blank=True)
    visit_reason = models.CharField(_(u'来访事由'), max_length=5, null=True, choices=VISIT_REASON, blank=True)
    visitor_number = models.IntegerField(_(u'来访人数'), null=True, blank=True)
    enter_time = models.DateTimeField(_(u'进入时间'), null=True, blank=True, editable=True)
    leave_time = models.DateTimeField(_(u'离开时间'), null=True, blank=True, editable=True)
    entrance = models.CharField(_(u'进入地点'),  max_length=20, null=True, blank=True)#进入地点和离开地点共用一个字段
    leave_place = models.CharField(_(u'离开地点'),  max_length=20, null=True, blank=True)
    visit_state = models.CharField(_(u'来访状态'), max_length=2, choices=VISIT_STATE, null=True, blank=True)
    is_alarm = models.BooleanField(_(u'是否已报警'), editable=True, null=False, blank=True, choices=YESORNO, default=0)
    
    def __unicode__(self):
        return u"%s"%(self.visitor_pin  or "")
    
    def delete(self):
        super(ReportManage, self).delete()


    class _delete(Operation):
        visible = True
        verbose_name=_(u'删除')
        def action(self):
            self.object.delete()
    
    class _change(Operation):
        visible = False
        verbose_name=_(u'编辑')
        def action(self):
            pass
        
        
    class _add(ModelOperation):
        visible = False
        verbose_name=_(u'新增')
        def action(self):
            pass
        
    class _export(ModelOperation):
        visible = False
        verbose_name=_(u'导出')
        def action(self):
            pass
        
    def get_visit_reason(self):
        return self.visit_reason and unicode(dict(VISIT_REASON)[int(self.visit_reason)]) or ""
    
    
    def get_visit_state(self):
        return unicode(dict(VISIT_STATE)[int(self.visit_state)])

    
    
    class Admin(CachingModel.Admin):
        sort_fields = ["-enter_time", "leave_time"]
        app_menu = "visitor"
#        help_text = _(u"如果新增的访客在访客列表中未能显示，请联系管理员！")
        #search_fields = ['pin', 'visited_person', 'visitor']
        list_display = ('visited_emp_pin', 'visited_person', 'dept', 'visitor', 'visitor_pin', 'card', 'visitor_company', 'get_visit_reason', 'visitor_number', 'entrance', 'leave_place', 'enter_time', 'leave_time', 'get_visit_state', )
        adv_fields = ['visited_emp_pin', 'visited_person', 'dept', 'visitor', 'visit_reason', 'entrance', 'leave_place', 'enter_time', 'leave_time',]
        query_fields = ['visited_emp_pin', 'visited_person', 'visitor', 'entrance', 'leave_place', 'enter_time', 'leave_time', 'visitor_number', 'visit_state']
        menu_index = 10005
        cache = 3600
        position = _(u'访客系统 -> 访客记录')


    class Meta:
        app_label = 'visitor'
        db_table = 'report_manage'
        verbose_name = _(u'访客记录')
        verbose_name_plural = verbose_name

