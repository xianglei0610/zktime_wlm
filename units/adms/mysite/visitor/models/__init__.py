# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from model_reservation import ReservationManage
from model_report import ReportManage
from model_visitor import VisitorManage
from models import VisitorOptionPage

verbose_name = _(u"访客")
_menu_index = 7

def app_options():
    from base.options import SYSPARAM, PERSONAL
    return (
    #参数名称, 参数默认值，参数显示名称，解释
        ('visitor_default_page', 'data/visitor/VisitorManage/', u"%s"%_(u'访客默认页面'), "", PERSONAL, False),
    )



