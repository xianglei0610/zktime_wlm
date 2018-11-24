# -*- coding: utf-8 -*-
from acclinkageio import AccLinkageIO
from accdoor import AccDoor, AccDevice, AccMapDoorPos
from accfirstopen import AccFirstOpen
from accmorecardset import AccMoreCardSet, AccMoreCardGroup
from acctimeseg import AccTimeSeg
from accwiegandfmt import AccWiegandFmt
from accantiback import AccAntiBack
from accinterlock import AccInterLock
from accholidays import AccHolidays
from acclevelset import AccLevelSet
from accmonitorlog import AccRTMonitor
from accmap import AccMap

from django.utils.translation import ugettext_lazy as _

from models import RTMonitorPage, DoorSetPage, EmpLevelSetPage, ReportFormPage, DoorMngPage, \
    MonitorAllPage, MonitorAlarmPage, EmpLevelByLevelPage, EmpLevelByEmpPage, \
    AllEventReportPage, AlarmEventReportPage, EmpLevelReportPage, ElectroMapPage, AccOption, AccGuidePage

verbose_name = _(u"门禁")
_menu_index = 3

def app_options():
    from base.options import  SYSPARAM, PERSONAL
    return (
    #参数名称, 参数默认值，参数显示名称，解释
        ('iaccess_default_page', 'iaccess/RTMonitorPage/', u"%s"%_(u'门禁默认页面'), "", PERSONAL, False),
    )

