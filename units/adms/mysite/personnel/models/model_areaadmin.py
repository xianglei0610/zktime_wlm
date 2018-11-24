# -*- coding: utf-8 -*-
from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django import forms
from model_area import Area


class AreaAdmin(models.Model):
        user = models.ForeignKey(User)
        area = models.ForeignKey(Area, verbose_name=_(u'授权区域'), null=False)
        def __unicode__(self):
                return unicode(self.area)
        class Admin:
                list_display=("user","area", )
                visible=False
        class Meta:
                app_label='iclock'
                db_table = 'areaadmin'
                verbose_name=_(u"区域管理")
                verbose_name_plural=verbose_name
