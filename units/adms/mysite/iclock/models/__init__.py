# -*- coding: utf-8 -*-
from mysite.personnel.models.model_dept import Department, DeptForeignKey
from mysite.personnel.models.model_emp import Employee, EmpForeignKey, device_pin, format_pin, get_default_dept
from model_device import Device, DeviceForeignKey
from model_bio import Template
from model_trans import Transaction
from model_oplog import OpLog
from model_devlog import DevLog
from model_devcmd import DevCmd
from model_devcmdbak import DevCmdBak
from model_dstime import DSTime
from models import DevRTMonitorPage
from mysite.personnel.models.model_deptadmin import DeptAdmin
from mysite.personnel.models.model_areaadmin import AreaAdmin
from django.utils.translation import ugettext_lazy as _
from testmodel import TestData
#from model_cmmdata import CmmData
from mysite.personnel.models.model_area import Area
from model_devoperate import OperateCmd
#from model_guide import IclockGuide
from model_face import FaceTemplate
import device_extend
import pos_device_extend
import device_operation
import iaccess_operation
from model_dininghall import Dininghall
from model_notice import Notice
verbose_name = _(u"设备")
_menu_index=2

__all__=[
'Department','DeptAdmin','AreaAdmin', 'DeptForeignKey',
'Device','DeviceForeignKey',
'Employee', 'EmpForeignKey', 'device_pin','format_pin','get_default_dept',
'Template',
'Transaction',
'OpLog',
'DevLog',
'DevCmd',
'DevCmdBak',
#'IclockGuide'
]

#from django.contrib.auth.models import User
#
#if 'deptadmin_set|detail_str' not in User.Admin.list_display:
#        User.Admin.list_display+=('deptadmin_set|detail_str',)
#
#if 'areaadmin_set|detail_str' not in User.Admin.list_display:
#        User.Admin.list_display+=('areaadmin_set|detail_str',)

def app_options():  
    from base.options import  SYSPARAM,PERSONAL
    return(
    #参数名称, 参数默认值，参数显示名称，解释
        ('iclock_default_page', 'data/iclock/device/', u"%s"%_(u'设备默认页面'), "", PERSONAL,False),
    )
