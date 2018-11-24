# -*- coding: utf-8 -*-
#*****一些静态的常量，根据不同的系统自己写一份不同的参数，
#****不在通过mysite.att in ...这种方式来做复杂的判断
#如果能够区分默写操作一定是某子系统的，可以通过ATT,POST,ACCESS...这些个参数来控制，
#否则使用新的自定义参数来配置
#默认为ZKECO的配置
import const
from django.utils.translation import ugettext_lazy as _
import settings
from base.backup import get_attsite_file
att_file = get_attsite_file()
v_pos_id = False
v_pos_ic = False
op_pos_id = att_file["Options"]["POS_ID"]
op_pos_ic = att_file["Options"]["POS_IC"]

if op_pos_id.lower()=="true":
    v_pos_id = True

if op_pos_ic.lower()=="true":
    v_pos_ic = True

#-----------------------------------------app控制参数-------------------------------
const.ATT = False
const.IACCESS = False
const.POS = False
const.POS_ID = False #ID消费
const.POS_IC = False #IC消费
#-----------------------------------------app控制参数-------------------------------
#控制帮助文档
const.ATT_HELP = False  
const.IACCESS_HELP = False
const.POS_HELP = False

installed_apps = settings.INSTALLED_APPS
if "mysite.att" in installed_apps:
    const.ATT = True #确定只有考勤，其他系统不会用的时候可以用此参数
    const.ATT_HELP = True
    
if "mysite.iaccess" in installed_apps:
    const.IACCESS = True #确定只有门禁，其他系统不会用的时候可以用此参数
    const.IACCESS_HELP = True
    
if "mysite.pos" in installed_apps:
    const.POS = True #消费存在的时候使用
    const.POS_ID = v_pos_id #ID消费  
    const.POS_IC = v_pos_ic #IC消费
    const.POS_HELP = True
    
const.ONLY_ATT = False
if const.ATT and not const.IACCESS and not const.POS:
   const.ONLY_ATT=True
  
const.ONLY_POS = False
const.LEAVE_ONLY_POS =False 
if not const.ATT and not const.IACCESS and const.POS:
    const.ONLY_POS = True #单独消费系统的时候使用
    const.LEAVE_ONLY_POS =True 
    const.EMPLOYEE_HIDE_PERMS = ['opadjustarea_employee','deleteuserface_employee','deleteuserphoto_employee','opaddusermsg_employee','opadjustdept_employee','opdeletetemplate_employee','oppositionchange_employee','pushuserface_employee','pushuserphoto_employee','opemptype_employee','opissuecard_employee','opregisterfinger_employee','opaddleveltoEmp_employee','opdellevelfromemp_employee','opsynctodevice_employee']
    #在角色树上屏蔽不需要的操作权限
    const.DEVICE_HIDE_PERMS =[
    'opsetdstime_device',
    'opremovedstime_device',
    'openableaccgapb_device',
    'opdisableaccgapb_device',
    
    'cleartransaction_device',
    'clearpicture_device',
    'opchangemthreshold_device',
    
    
    'opsearchacpanel_device',
    'opdisabledevice_device',
    'openabledevice_device',
    'resetpassword_device',
    'opchangeipofacpanel_device',
    'openableaccpush_device',
    'opdisableaccpush_device',
    'opchangeelevatorparamters_device',
    'opcloseauxout_device',
    'opupgradefirmware_device',
    'uploadlogs_device',
    'uploaduserinfo_device',
    'opreloaddata_device',
    'opupempinfo_device',
    'remoteupgrade_device',
    'opupattinfo_device',
    'opcheckattinfo_device',
    'opadddevicemsg_device',
    'refreshdeviceinfo_device'
    ]
    
const.VIDEO = False #确定只有硬盘录像机，其他系统不会用的时候可以用此参数
const.IACCESS_5TO4 = False      #门禁专用，用5.0代码打4.5包，主要是功能差异，值为False代表当前为5.0软件。
const.IACCESS_WITH_ATT = False    #只有门禁带考勤才打开,默认不带
const.VISITOR = False #访客
#登入页面的浏览器标题 #_(u"门禁管理系统") _("ZKAccess4.5 门禁管理系统") _("ZKAccess5.0 门禁管理系统") _("时间&安全管理平台") _("ZKECO 时间&安全管理平台")_("门禁管理系统" )#_("ZKAccess5.0 门禁管理系统")_("考勤管理系统" ) _("ZKTime8.0 考勤管理系统")

const.FINGER_LOGIN = True #指纹登入
if const.ONLY_POS:
    const.FINGER_LOGIN = False #指纹登入
const.CHANGE_CSS = False #改变样式
const.NORMAL_LOGIN = "displayN"   #正常登入

#工作面板
def ZKeco():
    const.WORKTABLE_JS = True  #工作面板JS初始化隐藏
    const.WORKTABLE_HAS_REGISTERFINGER = True #工作面板指纹登记
    const.WORKTABLE_HAS_ADD_LEAVELOG = True #工作面板新增人员离职
    const.WORKTABLE_HAS_ADD_AREA = True #工作面板新增区域
    const.WORKTABLE_HAS_ADD_CHECKEXACT = True #工作面板新增补签卡
    const.WORKTABLE_HAS_EMPSPECDAY = True #工作面板请假
    const.WORKTABLE_HAS_ATTCAL = True #工作面板考勤计算
    const.WORKTABLE_COMMON_SEARCH = True #工作面板常用查询
    const.WORKTABLE_ATT_COMMON_SEARCH = True #工作面板考勤常用查询
    const.WORKTABLE_OVERTIME_AUDIT = True #工作面板加班单审核
    const.WORKTABLE_SPECDAY_AUDIT = True #工作面板请假单审核
    const.WORKTABLE_CHECKEXACT_AUDIT = True #工作面板补签卡审核
    const.WORKTABLE_COMMON_MONITOR  =  True #工作面板公告提醒
    const.WORKTABLE_EMPSTRUCTrue  =  True #人力构成分析
    const.WORKTABLE_ATTRATE  =  True #人力构成分析
    const.WORKTABLE_REPORT_NAME  = _(u"查看报表")  #_(u"查看门禁报表")
    const.WORKTABLE_MONITOR_DEVICE_NAME  = _(u"设备监控")  #_(u"门禁设备监控")
    const.WORKTABLE_ACC_HOLIDAYS_NAME  = _(u"新增节假日")  #_(u"新增门禁节假日")
    const.WORKTABLE_UPLOADLOGS  = _(u"获取事件记录")  #_(u"获取控制器事件记录")
    const.WORKTABLE_CLEAR_UPLOAD_DIR  = True  #清理上传的文件目录
    const.WORKTABLE_DEVCMD_BAK  = True  #清理失败命令
    const.WORKTABLE_OPERATE_CMDS  = True  #清理通讯命令日志
    const.WORKTABLE_DELETEDATA = True #是否需要清理垃圾的界面
    const.WORKTABLE_GROUPMSG_VISIBLE = True #是否显示系统提醒设置
    const.WORKTABLE_MSGTYPE_VISIBLE = True #是否显示公告类别
    const.WORKTABLE_INSTANTMSG_VISIBLE = True #是否显示公告类别
    const.WORKTABLE_ACCESS = True #门禁常用操作
    
def Att():
    const.WORKTABLE_JS = True  #工作面板JS初始化隐藏
    const.WORKTABLE_HAS_REGISTERFINGER = True #工作面板指纹登记
    const.WORKTABLE_HAS_ADD_LEAVELOG = True #工作面板新增人员离职
    const.WORKTABLE_HAS_ADD_AREA = True #工作面板新增区域
    const.WORKTABLE_HAS_ADD_CHECKEXACT = True #工作面板新增补签卡
    const.WORKTABLE_HAS_EMPSPECDAY = True #工作面板请假
    const.WORKTABLE_HAS_ATTCAL = True #工作面板考勤计算
    const.WORKTABLE_COMMON_SEARCH = True #工作面板常用查询
    const.WORKTABLE_ATT_COMMON_SEARCH = True #工作面板考勤常用查询
    const.WORKTABLE_OVERTIME_AUDIT = True #工作面板加班单审核
    const.WORKTABLE_SPECDAY_AUDIT = True #工作面板请假单审核
    const.WORKTABLE_CHECKEXACT_AUDIT = True #工作面板补签卡审核
    const.WORKTABLE_COMMON_MONITOR  =  True #工作面板公告提醒
    const.WORKTABLE_EMPSTRUCTrue  =  True #人力构成分析
    const.WORKTABLE_ATTRATE  =  True #人力构成分析
    const.WORKTABLE_REPORT_NAME  = _(u"查看报表")  #_(u"查看门禁报表")
    const.WORKTABLE_MONITOR_DEVICE_NAME  = _(u"设备监控")  #_(u"门禁设备监控")
    const.WORKTABLE_ACC_HOLIDAYS_NAME  = _(u"新增节假日")  #_(u"新增门禁节假日")
    const.WORKTABLE_UPLOADLOGS  = _(u"获取事件记录")  #_(u"获取控制器事件记录")
    const.WORKTABLE_CLEAR_UPLOAD_DIR  = True  #清理上传的文件目录
    const.WORKTABLE_DEVCMD_BAK  = True  #清理失败命令
    const.WORKTABLE_OPERATE_CMDS  = True  #清理通讯命令日志
    const.WORKTABLE_DELETEDATA = True #是否需要清理垃圾的界面
    const.WORKTABLE_GROUPMSG_VISIBLE = True #是否显示系统提醒设置
    const.WORKTABLE_MSGTYPE_VISIBLE = True #是否显示公告类别
    const.WORKTABLE_INSTANTMSG_VISIBLE = True #是否显示公告类别
    const.WORKTABLE_ACCESS = False #门禁常用操作

def Acc():
    const.WORKTABLE_JS = False  #工作面板JS初始化隐藏 ---初始化隐藏考勤面板JS
    #const.WORKTABLE_HAS_REGISTERFINGER = True
    const.WORKTABLE_HAS_ADD_LEAVELOG = False #工作面板新增人员离职
    const.WORKTABLE_HAS_ADD_AREA = True #工作面板新增区域
    const.WORKTABLE_HAS_ADD_CHECKEXACT = False #工作面板新增补签卡
    const.WORKTABLE_HAS_EMPSPECDAY = False #工作面板请假
    const.WORKTABLE_HAS_ATTCAL = False #工作面板考勤计算
    const.WORKTABLE_COMMON_SEARCH = False #工作面板常用查询(考勤快速上手)
    const.WORKTABLE_ATT_COMMON_SEARCH = False #工作面板考勤常用查询
    const.WORKTABLE_OVERTIME_AUDIT = False #工作面板加班单审核
    const.WORKTABLE_SPECDAY_AUDIT = False #工作面板请假单审核
    const.WORKTABLE_CHECKEXACT_AUDIT = False #工作面板补签卡审核
    const.WORKTABLE_COMMON_MONITOR  =  False #工作面板公告提醒
    const.WORKTABLE_EMPSTRUCTrue  =  False #人力构成分析
    const.WORKTABLE_ATTRATE  =  False #人力构成分析
    const.WORKTABLE_REPORT_NAME  = _(u"查看门禁报表")  #_(u"查看门禁报表"),_(u"查看报表")
    const.WORKTABLE_MONITOR_DEVICE_NAME  = _(u"门禁设备监控")  #_(u"门禁设备监控"),_(u"设备监控")
    const.WORKTABLE_ACC_HOLIDAYS_NAME  = _(u"新增门禁节假日")  #_(u"新增门禁节假日"),_(u"新增节假日")
    const.WORKTABLE_UPLOADLOGS  = _(u"获取控制器事件记录")  #_(u"获取控制器事件记录"),_(u"获取事件记录")
    const.WORKTABLE_CLEAR_UPLOAD_DIR  = True  #清理上传的文件目录
    const.WORKTABLE_DEVCMD_BAK  = True  #清理失败命令
    const.WORKTABLE_OPERATE_CMDS  = True  #清理通讯命令日志
    const.WORKTABLE_DELETEDATA = False #是否需要清理垃圾的界面 （门禁系统下不需要）
    const.WORKTABLE_GROUPMSG_VISIBLE = False #是否显示系统提醒设置 -- 暂只有考勤使用，当门禁带简单考勤时屏蔽
    const.WORKTABLE_MSGTYPE_VISIBLE = False #是否显示公告类别  -- 暂只有考勤使用，当门禁带简单考勤时屏蔽
    const.WORKTABLE_INSTANTMSG_VISIBLE = False #是否显示公告类别  -- 暂只有考勤使用，当门禁带简单考勤时屏蔽
    const.WORKTABLE_ACCESS = True #门禁常用操作

def Pos():
    const.WORKTABLE_JS = False  #工作面板JS初始化隐藏
    const.WORKTABLE_HAS_REGISTERFINGER = False #工作面板指纹登记
    const.WORKTABLE_HAS_ADD_LEAVELOG = False #工作面板新增人员离职
    const.WORKTABLE_HAS_ADD_AREA = False #工作面板新增区域
    const.WORKTABLE_HAS_ADD_CHECKEXACT = False #工作面板新增补签卡
    const.WORKTABLE_HAS_EMPSPECDAY = False #工作面板请假
    const.WORKTABLE_HAS_ATTCAL = False #工作面板考勤计算
    const.WORKTABLE_COMMON_SEARCH = False #工作面板常用查询
    const.WORKTABLE_ATT_COMMON_SEARCH = False #工作面板考勤常用查询
    const.WORKTABLE_OVERTIME_AUDIT = False #工作面板加班单审核
    const.WORKTABLE_SPECDAY_AUDIT = False #工作面板请假单审核
    const.WORKTABLE_CHECKEXACT_AUDIT = False #工作面板补签卡审核
    const.WORKTABLE_COMMON_MONITOR  =  False #工作面板公告提醒
    const.WORKTABLE_EMPSTRUCTrue  =  False #人力构成分析
    const.WORKTABLE_ATTRATE  =  False #人力构成分析
    const.WORKTABLE_REPORT_NAME  = _(u"查看报表")  #_(u"查看门禁报表")
    const.WORKTABLE_MONITOR_DEVICE_NAME  = _(u"设备监控")  #_(u"门禁设备监控")
    const.WORKTABLE_ACC_HOLIDAYS_NAME  = _(u"新增节假日")  #_(u"新增门禁节假日")
    const.WORKTABLE_UPLOADLOGS  = _(u"获取事件记录")  #_(u"获取控制器事件记录")
    const.WORKTABLE_CLEAR_UPLOAD_DIR  = False  #清理上传的文件目录
    const.WORKTABLE_DEVCMD_BAK  = False  #清理失败命令
    const.WORKTABLE_OPERATE_CMDS  = False  #清理通讯命令日志
    const.WORKTABLE_DELETEDATA = True #是否需要清理垃圾的界面
    const.WORKTABLE_GROUPMSG_VISIBLE = False #是否显示系统提醒设置
    const.WORKTABLE_MSGTYPE_VISIBLE = False #是否显示公告类别
def Other():
    const.WORKTABLE_JS = False  #工作面板JS初始化隐藏
    const.WORKTABLE_HAS_REGISTERFINGER = False #工作面板指纹登记
    const.WORKTABLE_HAS_ADD_LEAVELOG = True #工作面板新增人员离职
    const.WORKTABLE_HAS_ADD_AREA = True #工作面板新增区域
    const.WORKTABLE_HAS_ADD_CHECKEXACT = False #工作面板新增补签卡
    const.WORKTABLE_HAS_EMPSPECDAY = False #工作面板请假
    const.WORKTABLE_HAS_ATTCAL = False #工作面板考勤计算
    const.WORKTABLE_COMMON_SEARCH = False #工作面板常用查询
    const.WORKTABLE_ATT_COMMON_SEARCH = False #工作面板考勤常用查询
    const.WORKTABLE_OVERTIME_AUDIT = False #工作面板加班单审核
    const.WORKTABLE_SPECDAY_AUDIT = False #工作面板请假单审核
    const.WORKTABLE_CHECKEXACT_AUDIT = False #工作面板补签卡审核
    const.WORKTABLE_COMMON_MONITOR  =  False #工作面板公告提醒
    const.WORKTABLE_EMPSTRUCTrue  =  True #人力构成分析
    const.WORKTABLE_ATTRATE  =  False #人力构成分析
    const.WORKTABLE_REPORT_NAME  = _(u"查看报表")  #_(u"查看门禁报表")
    const.WORKTABLE_MONITOR_DEVICE_NAME  = _(u"设备监控")  #_(u"门禁设备监控")
    const.WORKTABLE_ACC_HOLIDAYS_NAME  = _(u"新增节假日")  #_(u"新增门禁节假日")
    const.WORKTABLE_UPLOADLOGS  = _(u"获取事件记录")  #_(u"获取控制器事件记录")
    const.WORKTABLE_CLEAR_UPLOAD_DIR  = True  #清理上传的文件目录
    const.WORKTABLE_DEVCMD_BAK  = True  #清理失败命令
    const.WORKTABLE_OPERATE_CMDS  = True  #清理通讯命令日志
    const.WORKTABLE_DELETEDATA = True #是否需要清理垃圾的界面
    const.WORKTABLE_GROUPMSG_VISIBLE = True #是否显示系统提醒设置
    const.WORKTABLE_MSGTYPE_VISIBLE = True #是否显示公告类别
    const.WORKTABLE_INSTANTMSG_VISIBLE = True #是否显示公告类别
    const.WORKTABLE_ACCESS = False #门禁常用操作
    
    
#设备管理
const.DECMDBAk_VISIBLE = True #是否显示失败命令查询
const.DEVLOG_VISIBLE = False #是否显示设备通讯日志
const.DEVOPERATE_VISIBLE = False # 是否显示通信命令详情

app_list = [const.ATT,const.IACCESS,const.POS]
const.SELF_LOGIN = False#员工自助是否要显示
const.SELF_FG_LOG = False # 员工自助是否显示指纹登录
const.PIC_INFO_NORMAL_NAME = False
const.PIC_INFO_ACC_NAME = False
const.LOGIN_RIGHT_IMAGE = False #单消费登陆页面右侧图片
const.EMPLOYEE_EDIT_REGISTER_FINGERPRINT = False #employee_edit.html页面是否显示指纹登记  "mysite.iaccess&mysite.att"|hasApp and "mysite"|is_zkaccess_att and "mysite"|is_zkaccess_5to4 
const.EMPLOYEE_IS_FINNGER = False # 是否显示指纹机登记  {% if "mysite.att"|hasApp and not "mysite"|is_zkaccess_att %} 
const.EMPLOYEE_DISABLED_ATT_SET = False #人员编辑页面是否显示考勤设置
const.EMPCHANGE_VISIBLE = True #人员调动是否显示
const.NOTICE_VISIBLE = False # 是否显示设备短信息

const.BASE_PAGE_IS_CONTAIN_ATT = "false" #...
const.BASE_PAGE_HIDE_APP = [] #隐藏默写应用，例如门禁带考勤时需要隐藏考勤["att",] 
const.DEVICE_USER_MANAGEMENT_VISIBLE = True#是否显示区域用户管理

#User_edit.html
const.USER_FINGER_LOGIN = True #用户编辑指纹模块是否显示

#针对门禁带简单考勤
#user_option.html
const.USER_OPTION_ADD_ATT = False #是否添加考勤 暂时只有中文下才考虑是否显示和隐藏考勤模块

#Group_edit.html
const.HIDE_ATT_PERMISSION = False  #隐藏考勤
const.IACCESS_ATTLOG = True        #门禁开门事件当考勤记录使用

const.MEETING_HELP = False
const.VIDEO_HELP = False

#门禁
const.HIDE_ATT_EN = False #门禁带考勤时，英文下没有考勤配置项，帮助文档默认隐藏考勤相关帮助页面
    
if app_list==[True,False,False]:#单考勤
    const.BROWSER_TITLE = _(u"ZKTime8.3 考勤管理系统") 
    const.LOGIN_IMAGE ="logoAtt" #登入图片logoZKAccess,logoZKECO,oem,logoZKAccess,logoAtt
    const.SELF_LOGIN = True#员工自助是否要显示    
    const.PIC_INFO_NORMAL_NAME = True #登入的默认图片名称
    const.EMPLOYEE_IS_FINNGER = True # 是否显示指纹机登记  {% if "mysite.att"|hasApp and not "mysite"|is_zkaccess_att %} 
    const.EMPLOYEE_DISABLED_ATT_SET = True #人员编辑页面是否显示考勤设置
    const.EMPCHANGE_VISIBLE = True #人员调动是否显示
    Att();
    const.NOTICE_VISIBLE = True # 是否显示设备短信息
    const.BASE_PAGE_SYSTEM_NAME = "ZKTime" #Access,ZKAccess,ECO,Attendance,ZKTime,ZKPos,
    const.BASE_PAGE_SYSTEM_TYPE = "zktime" #zkeco,zktime,ZKPos,zkaccess
    const.BASE_PAGE_HEADLOG_NAME = "headLogoatt"  #每个模块的图片_zkaccess_att_oem,_zkaccess_att,_oem
    const.APPOPTION_BROWSE_TITLE = _(u"ZKTime8.3 考勤管理系统")
    const.APPOPTION_HELP_TEXT = _(u"系统参数即系统的一些设置项，如消息监控时间，\n系统会根据此参数值来监控过生日和转正的人员！")

    
    
elif app_list==[False,True,False]:#单门禁
    const.BROWSER_TITLE =  _(u"ZKAccess5.0 门禁管理系统")
    const.LOGIN_IMAGE ="logoZKAccess" #登入图片logoZKAccess,logoZKECO,oem,logoZKAccess,logoAtt    
    const.PIC_INFO_ACC_NAME = True
    Acc()
    const.BASE_PAGE_SYSTEM_NAME = "ZKAccess" #base_page_from.html
    const.BASE_PAGE_SYSTEM_TYPE = "zkaccess" #zkaccess
    const.BASE_PAGE_HEADLOG_NAME = "headLogo_zkaccess_att"  #每个模块的图片
    const.APPOPTION_BROWSE_TITLE = _(u"ZKAccess5.0 门禁管理系统")#options.py


    
elif app_list==[False,False,True]:#单消费
    const.BROWSER_TITLE = _(u"ZKPos消费管理系统") 
    const.LOGIN_IMAGE ="logoZKPos" #登入图片logoZKAccess,logoZKECO,oem,logoZKAccess,logoAtt    
    const.LOGIN_RIGHT_IMAGE = True #单消费登陆页面右侧图片
    const.EMPLOYEE_EDIT_REGISTER_FINGERPRINT = True #employee_edit.html页面是否显示指纹登记  "mysite.iaccess&mysite.att"|hasApp and "mysite"|is_zkaccess_att and "mysite"|is_zkaccess_5to4 
    Pos()
    const.BASE_PAGE_SYSTEM_NAME = "ZKPos" #Access,ZKAccess,ECO,Attendance,ZKTime,ZKPos,
    const.BASE_PAGE_SYSTEM_TYPE = "ZKPos" #zkeco,zktime,ZKPos,zkaccess
    const.BASE_PAGE_HEADLOG_NAME = "headLogopos"  #每个模块的图片_zkaccess_att_oem,_zkaccess_att,_oem
    const.USER_FINGER_LOGIN = False #用户编辑指纹模块是否显示
    const.APPOPTION_BROWSE_TITLE = _(u"ZKPos消费管理系统")
    const.APPOPTION_HELP_TEXT = _(u"系统参数即系统的一些设置项，如消息监控时间，\n系统会根据此参数值来监控过生日和转正的人员！")

    
elif app_list==[True,True,True]:
    const.BROWSER_TITLE = _(u"ZKECO 时间&安全管理平台") 
    const.LOGIN_IMAGE ="logoZKECO" #登入图片logoZKAccess,logoZKECO,oem,logoZKAccess,logoAtt
    const.SELF_LOGIN = True#员工自助是否要显示
    const.PIC_INFO_NORMAL_NAME = True #登入的默认图片名称
    const.EMPLOYEE_IS_FINNGER = True # 是否显示指纹机登记  {% if "mysite.att"|hasApp and not "mysite"|is_zkaccess_att %} 
    const.EMPLOYEE_DISABLED_ATT_SET = True #人员编辑页面是否显示考勤设置
    const.EMPCHANGE_VISIBLE = True #人员调动是否显示
    ZKeco()
    const.NOTICE_VISIBLE = True # 是否显示设备短信息
    const.BASE_PAGE_SYSTEM_NAME = "ZKECO" #Access,ZKAccess,ECO,Attendance,ZKTime,ZKPos,
    const.BASE_PAGE_SYSTEM_TYPE = "zkeco" #zkeco,zktime,ZKPos,zkaccess
    const.BASE_PAGE_HEADLOG_NAME = "headLogo"  #每个模块的图片_zkaccess_att_oem,_zkaccess_att,_oem
    const.APPOPTION_BROWSE_TITLE = _(u'ZKECO 时间&安全管理平台')
    const.APPOPTION_HELP_TEXT = _(u"系统参数即系统的一些设置项！")
else:
    const.BROWSER_TITLE = _(u"ZKECO 时间&安全管理平台") 
    const.LOGIN_IMAGE ="logoZKECO" #登入图片logoZKAccess,logoZKECO,oem,logoZKAccess,logoAtt
    const.SELF_LOGIN = False#员工自助是否要显示
    const.PIC_INFO_NORMAL_NAME = True #登入的默认图片名称
    const.EMPLOYEE_IS_FINNGER = True # 是否显示指纹机登记  {% if "mysite.att"|hasApp and not "mysite"|is_zkaccess_att %} 
    const.EMPLOYEE_DISABLED_ATT_SET = False #人员编辑页面是否显示考勤设置
    const.EMPCHANGE_VISIBLE = True #人员调动是否显示
    Other()
    const.NOTICE_VISIBLE = False # 是否显示设备短信息
    const.BASE_PAGE_SYSTEM_NAME = "ZKECO" #Access,ZKAccess,ECO,Attendance,ZKTime,ZKPos,
    const.BASE_PAGE_SYSTEM_TYPE = "zkeco" #zkeco,zktime,ZKPos,zkaccess
    const.BASE_PAGE_HEADLOG_NAME = "headLogo"  #每个模块的图片_zkaccess_att_oem,_zkaccess_att,_oem
    const.APPOPTION_BROWSE_TITLE = _(u'ZKECO 时间&安全管理平台')
    const.APPOPTION_HELP_TEXT = _(u"系统参数即系统的一些设置项！")

#else:
#    const.BROWSER_TITLE = _(u"ZKECO 时间&安全管理平台") 
#    const.LOGIN_IMAGE ="logoZKECO" #登入图片logoZKAccess,logoZKECO,oem,logoZKAccess,logoAtt
#    const.SELF_LOGIN = False#员工自助是否要显示
#    const.PIC_INFO_NORMAL_NAME = True #登入的默认图片名称
#    const.EMPLOYEE_IS_FINNGER = True # 是否显示指纹机登记  {% if "mysite.att"|hasApp and not "mysite"|is_zkaccess_att %} 
#    const.EMPLOYEE_DISABLED_ATT_SET = False #人员编辑页面是否显示考勤设置
#    const.EMPCHANGE_VISIBLE = True #人员调动是否显示
#    Other()
#    const.NOTICE_VISIBLE = False # 是否显示设备短信息
#    const.BASE_PAGE_SYSTEM_NAME = "ZKECO" #Access,ZKAccess,ECO,Attendance,ZKTime,ZKPos,
#    const.BASE_PAGE_SYSTEM_TYPE = "zkeco" #zkeco,zktime,ZKPos,zkaccess
#    const.BASE_PAGE_HEADLOG_NAME = "headLogo"  #每个模块的图片_zkaccess_att_oem,_zkaccess_att,_oem
#    const.APPOPTION_BROWSE_TITLE = _(u'ZKECO 时间&安全管理平台')
#    const.APPOPTION_HELP_TEXT = _(u"系统参数即系统的一些设置项！")
#    if app_list==[True,True,False]:#考勤、门禁
#        const.IACCESS_ATTLOG = True    #只有门禁带考勤才打开,默认不带    
if const.ATT:
    const.SELF_LOGIN = True
    const.EMPLOYEE_DISABLED_ATT_SET = True
    const.NOTICE_VISIBLE = True

#const.BASE_PAGE_HEADLOG_NAME = "headLogo"  #每个模块的图片_zkaccess_att_oem,_zkaccess_att,_oem
        


#const.SELF_LOGIN="" const.NORMAL_LOGIN="displayN"标示要员工自助
#const.SELF_LOGIN="displayN" const.NORMAL_LOGIN="" 标示不需要员工自助

#人员不需要的字段
EMPLOYEE_DISABLE_COLS_list = ['photo','Tele'] #人员不需要的字段
#if const.IACCESS:
#    del EMPLOYEE_DISABLE_COLS_list [1] #人员不需要的字段
#    del EMPLOYEE_DISABLE_COLS_list [2] #人员不需要的字段

EMPLOYEE_DISABLED_ACTIONS_STR = ",'OpAddLevelToEmp','OpDelLevelFromEmp'"
if not const.ATT:
    EMPLOYEE_DISABLE_COLS_list.append('get_face')
    EMPLOYEE_DISABLE_COLS_list.append('attarea')
    EMPLOYEE_DISABLE_COLS_list.append('get_template')
    EMPLOYEE_DISABLE_COLS_list.append('Privilege')
    EMPLOYEE_DISABLED_ACTIONS_STR += ",'DeleteUserFace','DeleteUserPhoto','OpAddUserMsg','OpAdjustDept','OpDeleteTemplate','OpPositionChange','PushUserFace','PushUserPhoto','OpAdjustArea','OpEmpType','OpIssueCard','OpRegisterFinger',,'OpAddLevelToEmp','OpDelLevelFromEmp','OpSyncToDevice',"
if const.POS:
    EMPLOYEE_DISABLED_ACTIONS_STR+=",'_delete'"
#if not const.IACCESS:
#    EMPLOYEE_DISABLE_COLS_list.append('level_count')
#    EMPLOYEE_DISABLED_ACTIONS_STR += ",'DeleteUserFace','DeleteUserPhoto','OpAddUserMsg','OpAdjustDept','OpDeleteTemplate','OpPositionChange','PushUserFace','PushUserPhoto','OpAdjustArea','OpEmpType','OpIssueCard','OpRegisterFinger',,'OpAddLevelToEmp','OpDelLevelFromEmp','OpSyncToDevice',"
    
    
if const.ONLY_POS:
    EMPLOYEE_DISABLE_COLS_list = ['get_face','Privilege','attarea','get_template','photo','Tele','level_count',] #人员不需要的字段
    const.EMPLOYEE_DISABLED_ACTIONS=",'OpUploadPhoto','_delete','DeleteUserFace','DeleteUserPhoto','OpAddUserMsg','OpAdjustDept','OpDeleteTemplate','OpPositionChange','PushUserFace','PushUserPhoto','OpAdjustArea','OpEmpType','OpIssueCard','OpRegisterFinger',,'OpAddLevelToEmp','OpDelLevelFromEmp','OpSyncToDevice'," #人员不需要的操作 ",'OpAddLevelToEmp','OpDelLevelFromEmp'"
else:
    const.EMPLOYEE_DISABLED_ACTIONS = EMPLOYEE_DISABLED_ACTIONS_STR #人员不需要的操作 ",'OpAddLevelToEmp','OpDelLevelFromEmp'"
    
#人员
const.EMPLOYEE_IMPORT_FIELDS = ('PIN', 'EName', 'DeptID', 'Gender', 'identitycard', 'Mobile')#人员导入字段
const.EMPLOYEE_DISABLED_PERMS = ["clear_employee"] #人员不必要的权限屏蔽
const.EMPLOYEE_HELP_TEXT = _(u"人员信息是系统的基本信息，人员编号、部门为必填项，指纹登记需要指纹仪驱动，如果您未安装驱动，请先下载驱动程序！黑白屏考勤机仅支持5位密码，彩屏考勤机支持6位密码，门禁控制器仅支持6位密码，超过规定长度后系统将自动截取！")
const.EMPLOYEE_DISABLE_COLS = EMPLOYEE_DISABLE_COLS_list #人员不需要的字段
const.EMPLOYEE_IS_SELFPASSWORD = const.SELF_LOGIN #人员编辑页面是否显示登录密码 {% if not "mysite.att"|hasApp or "mysite"|is_zkaccess_att %}


#卡
#ISSUECARD_VERBOSE_NAME = _(u'卡管理')
const.ISSUECARD_HELP_TEXT = _(u"发卡时需连接读卡器,操作对象为已登记人事资料但未登记卡账号人员!管理卡跟操作卡对应权限为所属餐厅的设备!")


#卡模型操作配置
if const.POS:
    if const.POS_ID:
        const.ISSUECARD_DISABLE_ACTIONS = ",'RestateCard'"
        const.ISSUECARD_DISABLE_COLS = []
        const.ISSUECARD_LIST_DISPLAY = ['UserID.PIN', 'UserID.EName', 'UserID.DeptID.code', 'UserID.DeptID.name','cardno', 'type.name','card_privage','blance','cardstatus','issuedate']
        const.ISSUECARD_GET_CARD_WAY = True#批量发卡是否显示发卡器 {% if "mysite.iaccess&mysite.att"|hasApp or "mysite.iaccess"|hasApp %}
        const.ISSUECARD_ADV_FIELDS = ['UserID.PIN', 'UserID.EName', 'UserID.DeptID.code', 'UserID.DeptID.name','cardno', 'card_privage','blance','cardstatus','issuedate']
        const.ISSUECARD_QUERY_FIELDS = ['UserID__PIN','card_privage','cardstatus','cardno']
    else:
        const.ISSUECARD_DISABLE_ACTIONS = ""
        const.ISSUECARD_DISABLE_COLS = []
        const.ISSUECARD_LIST_DISPLAY = ['UserID.PIN', 'UserID.EName', 'UserID.DeptID.code', 'UserID.DeptID.name','cardno','sys_card_no', 'card_privage','type.name','blance','cardstatus','issuedate']
        const.ISSUECARD_GET_CARD_WAY = False#批量发卡是否显示发卡器 {% if "mysite.iaccess&mysite.att"|hasApp or "mysite.iaccess"|hasApp %}
        const.ISSUECARD_ADV_FIELDS = ['UserID.PIN', 'UserID.EName', 'UserID.DeptID.code', 'UserID.DeptID.name','cardno','sys_card_no','card_privage','blance','cardstatus','issuedate']
        const.ISSUECARD_QUERY_FIELDS = ['UserID__PIN','card_privage','cardstatus','cardno','sys_card_no']
        
else:
    const.ISSUECARD_DISABLE_ACTIONS = ",'OpLoseCard','InitFanArea','InitCardPwd','OpRevertCard','OpRefund','OpCharge','Reimburse','CardTypeSet','ResetPassword','Supplement'"
    const.ISSUECARD_DISABLE_COLS = ['card_privage','type.name','blance']
    const.ISSUECARD_LIST_DISPLAY = ['UserID.PIN', 'UserID.EName', 'UserID.DeptID.code', 'UserID.DeptID.name','cardno', 'card_privage','type.name','blance','cardstatus','issuedate']
    const.ISSUECARD_GET_CARD_WAY = True#批量发卡是否显示发卡器 {% if "mysite.iaccess&mysite.att"|hasApp or "mysite.iaccess"|hasApp %}
    const.ISSUECARD_ADV_FIELDS = ['UserID.PIN', 'UserID.EName', 'UserID.DeptID.code', 'UserID.DeptID.name','cardno','cardstatus','issuedate']
    const.ISSUECARD_QUERY_FIELDS = ['UserID__PIN', 'cardno','cardstatus']    

#设备
const.DEVICE_DISABLED_PERMS = ["dataimport_device","resume_device","pause_device","opbrowselog_device"]
const.DEVICE_HELP_TEXT = _(u"请选择设备类型以及对应的通信方式，设备名称、各通信参数以及所属区域为必填项！")
const.DEVICE_API_FIELDS = ('alias','sn', 'device_type','comm_type','ipaddress','area.areaname','dining.name','consume_model','Fpversion', 'last_activity', 'acpanel_type')
const.DEVICE_LIST_DISPLAY = ('alias','sn', 'device_type','device_use_type','comm_type','ipaddress','com_port',
                    'com_address','get_dstime_name','area.areaname','dining.name','consume_model','Fpversion','show_status|boolean_icon','pos_dev_status|boolean_icon','pos_file_count','pos_cmd_count',
                    'show_enabled|boolean_icon','last_activity', 'acpanel_type', 'device_name','user_count','fp_count','transaction_count','show_fp_mthreshold','fw_version','att_cmd_cnt')
const.DEVICE_QUERY_FIELDS = ['alias','sn', 'device_type']


const.DEVICE_DISABLE_COLS = ['user_count','face_count','fp_count','transaction_count','get_dstime_name','show_fp_mthreshold','acpanel_type','Fpversion','show_enabled|boolean_icon','dining.name','consume_model','last_activity','pos_dev_status|boolean_icon','pos_file_count','pos_cmd_count','com_address','com_port','device_use_type','att_cmd_cnt']
DEVICE_DISABLE_ACTIONS_STR =''',
'IcPosOnlineReloadData',
'OpIcDeviceDataCheck',
'OpSetDSTime',
'OpRemoveDSTime',
'OpEnableAccGAPB',
'OpDisableAccGAPB',

'ClearTransaction',
'ClearPicTrue',
'OpChangeMThreshold',

'ClearData',
'ClearPosData',
'OpReloadICPOSData',

'OpDisableDevice',
'OpEnableDevice',
'ResetPassword',
'OpChangeIPOfACPanel',
'SyncACPanelTime',
'OpEnableAccPush',
'OpDisableAccPush',
'OpChangeElevatorParamters',
'OpCloseAuxOut',
'OpUpgradeFirmware',
'UploadLogs',
'UploadUserInfo',
'OpReloadData',
'RefreshDeviceInfo',
'ClearPicture',
'OpUpEmpInfo',
'RemoteUpgrade',
'OpUpAttInfo',
'OpCheckAttInfo',
'OpAddDeviceMsg',
'''

if const.ONLY_POS and const.POS_ID:
    DEVICE_DISABLE_ACTIONS_STR+=("'Reboot','Syncdata',")
    const.DEVICE_DISABLE_ACTIONS = DEVICE_DISABLE_ACTIONS_STR
else:
    const.DEVICE_DISABLE_ACTIONS = DEVICE_DISABLE_ACTIONS_STR

#base_page_form.html




#user_option.html

#Group_edit.html

#User_edit.html


#离职
const.LEAVE_DISABLE_COLS = ['isReturnTools','isReturnClothes','isReturnCard'] #pos_disable_cols:['isReturnTools','isReturnClothes','isReturnCard'],
LEAVE_LIST_DISPLAY_LIST = ['UserID.PIN','UserID.EName','UserID.DeptID','UserID.isblacklist','leavedate','leavetype','reason']

if const.ATT:
    LEAVE_LIST_DISPLAY_LIST.append('isClassAtt')
if const.IACCESS:
    LEAVE_LIST_DISPLAY_LIST.append('isClassAccess')
if const.POS:
    LEAVE_LIST_DISPLAY_LIST.append('is_close_pos')
    
const.LEAVE_HELP_TEXT= _(u"对人员进行离职操作")#pos_(u"对离职人员进行恢复操作")
const.LEAVE_DISABLED_PERMS = ['change_leavelog','dataimport_leavelog','delete_leavelog']#['opcloseatt_leavelog','opcloseaccess_leavelog','change_leavelog','dataimport_leavelog','delete_leavelog']
const.LEAVE_LIST_DISPLAY = LEAVE_LIST_DISPLAY_LIST#['UserID.PIN','UserID.EName','UserID.DeptID','leavedate','leavetype','reason']
const.LEAVE_DISABLE_COLS = "" #pos_disable_cols:['isReturnTools','isReturnClothes','isReturnCard'],
const.LEAVE_DISABLE_ACTIONS = ",'_delete'"
const.LEAVE_VISIBLE = True #是否显示人员离职管理not (get_option("IACCESS") and settings.ZKACCESS_ATT and 'en' in dict(settings.LANGUAGES).keys())
#options.py







