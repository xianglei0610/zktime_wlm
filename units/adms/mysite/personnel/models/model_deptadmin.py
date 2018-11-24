# -*- coding: utf-8 -*-
from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django import forms
from model_dept import Department


class DeptAdmin(models.Model):
        user = models.ForeignKey(User)
        dept = models.ForeignKey(Department, verbose_name=_(u'授权部门'), null=False)
        def __unicode__(self):
                return unicode(self.dept)
        class Admin:
                list_display=("user","dept", )
                visible=False
        class Meta:
                app_label='iclock'
                db_table = 'deptadmin'
                verbose_name=_(u'部门管理')
                verbose_name_plural=verbose_name
