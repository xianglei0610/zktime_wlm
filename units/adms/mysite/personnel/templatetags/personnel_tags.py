#coding=utf-8
from mysite.personnel.models.depttree import dept_treeview,area_treeview
import datetime
from django import template
from django.conf import settings
from cgi import escape
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.cache import cache
from dbapp.datautils import hasPerm
from django.utils.encoding import force_unicode, smart_str

register = template.Library()

@register.simple_tag
def dept_tree():
    return dept_treeview()

@register.simple_tag
def area_tree():
    
    return area_treeview()

