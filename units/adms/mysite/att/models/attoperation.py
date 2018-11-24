#coding=utf-8
from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from mysite.att.views import funAttGuide,funForget,funAttUerOfRun,funAttCalculate,funAttDeviceUserManage,funAttDeviceDataManage
from mysite import settings
from mysite.utils import get_option

#class CheckForget(AppOperation):
#        u'''补签卡'''
#        verbose_name=_(u'补签卡')
#        view=funForget
#        _app_menu="att"
#        _menu_index=99998
        
#class AttParamSetting(AppOperation):
#        u'''考勤参数'''
#        verbose_name=_(u'考勤参数')
#        view=funAttParamSetting
#        _app_menu="att"
#        _menu_index=99997


class AttUserOfRun(AppOperation):
        u'''排班'''
        from mysite.att.models import USER_OF_RUN,USER_TEMP_SCH
        verbose_name=_(u'排班')
        view=funAttUerOfRun
        _app_menu="att"
        _menu_index=3
        _disabled_perms=["clear_user_of_run","change_user_of_run","delete_user_of_run","add_user_of_run","dataimport_user_of_run","change_user_temp_sch","add_user_temp_sch","delete_user_temp_sch","dataimport_user_temp_sch","clear_user_temp_sch"]#不要在权限列表里面显示的权限
        add_model_permission=[USER_OF_RUN,USER_TEMP_SCH]
        _select_related_perms={"can_AttUserOfRun":"browse_user_of_run.browse_user_temp_sch"}#点击can_RTMonitorPage菜单时默认选中can_MonitorAllPage中的权限,例如{"sourseperm":"perm1.perm2.perm3"}
        _hide_perms = ["browse_user_of_run","browse_user_temp_sch"]
        
class AttCalculate(AppOperation):
        u'''考勤计算与报表'''
        from mysite.att.models.model_report import AttReport
        verbose_name=_(u'考勤报表')
        view=funAttCalculate
        visible=False
        _app_menu="att"
        _select_related_perms={
            "can_AttCalculate":"calcresultdetail_attreport.calctotalreport_attreport.calculate_attreport.checkexact_attreport.earchdayattreport_attreport.exceptionreport_attreport.leavetotalreport_attreport.orgbrushrecord_attreport.otherexceptionreport_attreport",
            "dataexport_attreport":"calcresultdetail_attreport.calctotalreport_attreport.calculate_attreport.checkexact_attreport.earchdayattreport_attreport.exceptionreport_attreport.leavetotalreport_attreport.orgbrushrecord_attreport.otherexceptionreport_attreport"
        }
        _disabled_perms=["browse_attreport","add_attreport","change_attreport","delete_attreport"]
        _hide_perms=["calcresultdetail_attreport","calctotalreport_attreport","calculate_attreport","checkexact_attreport","earchdayattreport_attreport","exceptionreport_attreport","leavetotalreport_attreport","orgbrushrecord_attreport","otherexceptionreport_attreport"]
        add_model_permission=[AttReport,]
        _menu_index=10


class AttDeviceUserManage(AppOperation):
        u'''区域用户管理'''
        verbose_name=_(u'区域用户')
        view=funAttDeviceUserManage
        _app_menu ="att"
        _menu_index=12
#        visible = not (("mysite.iaccess" in settings.INSTALLED_APPS) and ("mysite.att" in settings.INSTALLED_APPS) and settings.ZKACCESS_ATT)
        visible = get_option("DEVICE_USER_MANAGEMENT_VISIBLE")
        
class AttDeviceDataManage(AppOperation):
        u'''考勤设备管理'''
        verbose_name=_(u'考勤设备')
        view=funAttDeviceDataManage
        _app_menu ="att"
        _menu_index=11
        visible =get_option("ATT")
        
class AttGuide(AppOperation):
        u'''导航'''
        verbose_name=_(u'导航')
        view=funAttGuide
        _app_menu ="att"
        _menu_index=0

    
