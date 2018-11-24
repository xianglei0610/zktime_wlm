# -*- coding: utf-8 -*-
from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from views import  get_specday,get_overtime,get_transaction,\
    get_selfreport,get_checkexact

verbose_name=_(u"员工自助")

class SelfCheckexact(AppOperation):
    verbose_name=_(u'补签卡')
    view=get_checkexact
    _app_menu="selfservice"
    _menu_index=1
    
class SelfSpecDay(AppOperation):
        u'''请假'''
        #from mysite.att.models import USER_OF_RUN,USER_TEMP_SCH
        verbose_name=_(u'请假')
        view=get_specday
        _app_menu="selfservice"
        _menu_index=1
        #_disabled_perms=["clear_user_of_run","change_user_of_run","delete_user_of_run","add_user_of_run","dataimport_user_of_run","change_user_temp_sch","add_user_temp_sch","delete_user_temp_sch","dataimport_user_temp_sch","clear_user_temp_sch"]#不要在权限列表里面显示的权限
        #add_model_permission=[USER_OF_RUN,USER_TEMP_SCH]
        #_select_related_perms={"can_AttUserOfRun":"browse_user_of_run.browse_user_temp_sch"}#点击can_RTMonitorPage菜单时默认选中can_MonitorAllPage中的权限,例如{"sourseperm":"perm1.perm2.perm3"}
        #_hide_perms = ["browse_user_of_run","browse_user_temp_sch"]

class SelfOverTime(AppOperation):
        u'''加班单'''
        #from mysite.att.models import USER_OF_RUN,USER_TEMP_SCH
        verbose_name=_(u'加班单')
        view=get_overtime
        _app_menu="selfservice"
        _menu_index=2
        #_disabled_perms=["clear_user_of_run","change_user_of_run","delete_user_of_run","add_user_of_run","dataimport_user_of_run","change_user_temp_sch","add_user_temp_sch","delete_user_temp_sch","dataimport_user_temp_sch","clear_user_temp_sch"]#不要在权限列表里面显示的权限
        #add_model_permission=[USER_OF_RUN,USER_TEMP_SCH]
        #_select_related_perms={"can_AttUserOfRun":"browse_user_of_run.browse_user_temp_sch"}#点击can_RTMonitorPage菜单时默认选中can_MonitorAllPage中的权限,例如{"sourseperm":"perm1.perm2.perm3"}
        #_hide_perms = ["browse_user_of_run","browse_user_temp_sch"]
        
class SelfTransaction(AppOperation):
        u'''考勤记录'''
        #from mysite.att.models import USER_OF_RUN,USER_TEMP_SCH
        verbose_name=_(u'原始记录表')
        view=get_transaction
        _app_menu="selfservice"
        _menu_index=3
        search_fields=('TTime',)
        tstart_end_search={
            "TTime":[_(u"起始考勤时间"),_(u"结束考勤时间")]
        }
        #_disabled_perms=["clear_user_of_run","change_user_of_run","delete_user_of_run","add_user_of_run","dataimport_user_of_run","change_user_temp_sch","add_user_temp_sch","delete_user_temp_sch","dataimport_user_temp_sch","clear_user_temp_sch"]#不要在权限列表里面显示的权限
        #add_model_permission=[USER_OF_RUN,USER_TEMP_SCH]
        #_select_related_perms={"can_AttUserOfRun":"browse_user_of_run.browse_user_temp_sch"}#点击can_RTMonitorPage菜单时默认选中can_MonitorAllPage中的权限,例如{"sourseperm":"perm1.perm2.perm3"}
        #_hide_perms = ["browse_user_of_run","browse_user_temp_sch"]

class SelfReport(AppOperation):
        u'''考勤报表'''
        #from mysite.att.models import USER_OF_RUN,USER_TEMP_SCH
        verbose_name=_(u'考勤报表')
        view=get_selfreport
        _app_menu="selfservice"
        _menu_index=4
        #_disabled_perms=["clear_user_of_run","change_user_of_run","delete_user_of_run","add_user_of_run","dataimport_user_of_run","change_user_temp_sch","add_user_temp_sch","delete_user_temp_sch","dataimport_user_temp_sch","clear_user_temp_sch"]#不要在权限列表里面显示的权限
        #add_model_permission=[USER_OF_RUN,USER_TEMP_SCH]
        #_select_related_perms={"can_AttUserOfRun":"browse_user_of_run.browse_user_temp_sch"}#点击can_RTMonitorPage菜单时默认选中can_MonitorAllPage中的权限,例如{"sourseperm":"perm1.perm2.perm3"}
        #_hide_perms = ["browse_user_of_run","browse_user_temp_sch"]
