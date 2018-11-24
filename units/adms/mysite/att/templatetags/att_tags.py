#!/usr/bin/env python
#coding=utf-8
import datetime
from django import template
from base.options import options
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.cache import cache
from django.db import models
from django.utils.encoding import force_unicode, smart_str
from django.conf import settings

register = template.Library()

@register.filter
def AttExceptDesc(exceptID):
    from mysite.att.models import LeaveClass
    t=LeaveClass.objects.get(pk=exceptID)
    if t:
        return u"%s"%t.LeaveName
    else:
        return exceptID

@register.filter
def audit_filter(v):
    try:
        v=int(v)
        ret=(
            (1,_(u'申请')),
            (2,_(u'审核通过')),
            (3,_(u'拒绝')),        
            (4,_(u'重新申请')),
            )
        return ret[v-1][1]
    except:
        return ""
