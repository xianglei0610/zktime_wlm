#coding=utf-8
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import permission_required
import models
import views
from mysite.personnel.models.empwidget import get_widget_for_select_emp
from django.conf import settings
from django.conf.urls.defaults import url
urlpatterns = patterns('mysite.iclock',
#设备连接相关
    (r'^ouputtreejson$', 'testtreeview.ouputtreejson'),
    (r'^funTestTree$','testtreeview.funTestTree'),
#    (r'^cdata$', 'devview.cdata'),
#    (r'^getrequest$', 'devview.getreq'),
#    (r'^devicecmd$', 'devview.devpost'),
#    (r'^fdata$', 'devview.post_photo'),
    (r'^cdata$', 'device_http.device_view.cdata'),
    (r'^getrequest$', 'device_http.device_view.getreq'),
    (r'^devicecmd$', 'device_http.device_view.devpost'),
    (r'^fdata$', 'device_http.device_view.post_photo'),
    
#消费
    (r'^pos_setoptions$', 'devview.set_pos_options'),#消费机修改参数&
    (r'^pos_getreback$', 'devview.pos_reback'),#消费回滚
    (r'^pos_getdata$', 'devview.pos_getdata'),#获取消费基本信息
    (r'^pos_getrequest$', 'devview.pos_getreq'),#消费业务
#IC消费
#    (r'^cpos$', 'ic_pos_devview.cdata'),
#    (r'^posrequest$', 'ic_pos_devview.pos_getreq'),
#    (r'^posdevicecmd$', 'ic_pos_devview.pos_devpost'),
#数据管理相关        
    (r'^_checktranslog_$', 'datamisc.newTransLog'), #实时记录下载
    (r'^_checkoplog_$', 'datamisc.newDevLog'), #设备实时记录
    (r'^ic1ock$', 'datasql.sql_page'),                                #执行SQL
    (r'^upload$', 'importdata.uploadData'),                                #上传导入数据文件
#其他功能        
    (r'^options/', 'setoption.index'),
    (r'^filemng/(?P<pageName>.*)$', 'filemngview.index'),
    (r'^tasks/del_emp$', 'taskview.FileDelEmp'),
    (r'^tasks/disp_emp$', 'taskview.FileChgEmp'),
    (r'^tasks/name_emp$', 'taskview.FileChgEmp'),
    (r'^tasks/disp_emp_log$', 'taskview.disp_emp_log'),
    (r'^tasks/del_emp_log$', 'taskview.del_emp_log'),
    (r'^tasks/app_emp$', 'taskview.app_emp'),
    (r'^tasks/upgrade$', 'taskview.upgrade'),
    (r'^tasks/restart$', 'taskview.restartDev'),
    (r'^tasks/autorestart$', 'taskview.autoRestartDev'),
    (r'^data_exp/(?P<pageName>.*)$', 'expview.index'),
    (r'^pics/(?P<path>.*)$', 'browsepic.index'),

    (r'^upload/(?P<path>.*)$', 'datamisc.uploadFile'),
    (r'^DevRTMonitorPage/$', 'models.models.render_devrtmonitor_page'),
    (r'^tasks/check_old_commpwd/$' ,'accview.check_old_commpwd'),
    (r'^get_acc_dev/$', 'accview.get_acc_dev'),
    #lhj 获取控制器类型
    (r'^get_dev_use_type/$', 'accview.get_dev_use_type'),
    (r'^iclock/iclock_guide/$' ,'views.iclock_guide'),

    (r'^choice_widget_for_select_emp/$',get_widget_for_select_emp),
)

dict_urls={
    "ic_pos_devview.cdata":url(r'^cpos$',('mysite.pos.pos_ic.ic_pos_devview.cdata'),prefix=''),
    "ic_pos_devview.pos_getreq":url(r'^posrequest$',('mysite.pos.pos_ic.ic_pos_devview.pos_getreq'),prefix=''),
    "ic_pos_devview.pos_devpost":url(r'^posdevicecmd$',('mysite.pos.pos_ic.ic_pos_devview.pos_devpost'),prefix=''),
}

for k,v in dict_urls.items():
    if "mysite.pos" in settings.INSTALLED_APPS:
        urlpatterns.append(v)
