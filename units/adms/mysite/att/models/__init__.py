# -*- coding: utf-8 -*-
#from excnotes import EXCNOTES
from model_holiday import Holiday
from schclass import SchClass 
from num_run_deil import NUM_RUN_DEIL
from num_run import NUM_RUN
from user_of_run import USER_OF_RUN
from model_empspecday import EmpSpecDay
from user_temp_sch import USER_TEMP_SCH
from model_leaveclass import LeaveClass
from model_leaveclass1 import LeaveClass1
from attparam import AttParam
from userusedsclasses import UserUsedSClasses
#from auditedexc import AuditedExc
from attcalclog import attCalcLog
from attexception import AttException
from attrecabnormite import attRecAbnormite
from attshifts import attShifts
#from attoperation import CheckForget
from attoperation import AttUserOfRun
from attoperation import AttDeviceUserManage
from attoperation import AttDeviceDataManage
from attoperation import AttGuide
from checkexact_model import CheckExact
from model_report import AttReport
from attoperation import AttCalculate
from model_setuseratt import SetUserAtt
#from attoperation import AttParamSetting
from django.utils.translation import ugettext_lazy as _
from model_waitforprocessdata import WaitForProcessData
from model_overtime import OverTime
from att_cal_log import att_autocal_log
from checkinout import CheckInOut
from grid_models.checkinout import CheckInOutGrid
from grid_models.attrec_result import RecAbnormite
from grid_models.attshifts import AttShiftsBase
from grid_models.card_times import CardTimes
from grid_models.first_last import FirstLast
from grid_models.day_abnormal import DayAbnormal
from grid_models.exception_attshifts import ExceptionAttshifts
from grid_models.day_list import DayList
from grid_models.emp_sum import EmpSum
from grid_models.exception_sum import ExceptionSum
from att_report_page import AttReport
from  model_syncset import SyncSet

verbose_name=_(u"考勤")
_menu_index=4

def app_options():
    from base.options import  SYSPARAM,PERSONAL
    return (
    #参数名称, 参数默认值，参数显示名称，解释
        ('att_default_page', 'att/AttGuide/', u"%s"%_(u'考勤默认页面'), "", PERSONAL,False),
    )
def get_autocalculate_time():
    import datetime
    #from mysite.sitebackend.models import CustomerOption
    #obj=CustomerOption.objects.filter(optionname='auto_calculate_time')    
    today=datetime.datetime.now().strftime("%Y-%m-%d")
    
#    if obj:
#        t=datetime.datetime.strptime(today+" "+obj[0].optionvalue,"%Y-%m-%d %H:%M:%S")
#        
#    else:
    t=datetime.datetime.strptime(today+" 03:00:00","%Y-%m-%d %H:%M:%S")
    return t
