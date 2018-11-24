# -*- coding: utf-8 -*-
from django.db import models, connection
import datetime
import sched, time
import os
import os.path
from django.conf import settings
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation, ModelOperation
from mysite.personnel.models.model_dept import DeptForeignKey, DEPT_NAME
from mysite.personnel.models.model_area import Area, AreaForeignKey
from redis_self.server import queqe_server, start_dict_server
from dbapp import data_edit
from traceback import print_exc
from django import forms
from mysite.utils import printf
from threading import Event, Semaphore
from base.crypt import encryption,decryption
import re
from django.core.cache import cache
from model_dstime import DSTime
from mysite.settings import MIN_REQ_DELAY as min_delay
try:
    import cPickle as pickle
except:
    import pickle
import socket, dict4ini
#from mysite.pos.pos_constant import TIMEOUT    
from model_dininghall import Dininghall
from mysite.utils import get_option 
from dbapp.widgets import ZBaseIntegerWidget,ZBaseSmallIntegerWidget,ZBaseMoneyWidget,ZBase3IntegerWidget
#from mysite.pos.models.model_splittime import SplitTime,SplitTimeManyToManyFieldKey
from redis_self.server import queqe_server, start_dict_server

sem = Semaphore()#
MAX_COMMAND_TIMEOUT_SECOND  = 60#30 远程开关门等紧急命令的超时时间
#MAX_ACPANEL_COUNT = 50#最大支持50台门禁控制器

DEV_STATUS_OK=1
DEV_STATUS_TRANS=2
DEV_STATUS_OFFLINE=3
DEV_STATUS_PAUSE=0
CMD_OK=200

ACCDEVICE_DISABLED = "ACCDEVICE_%d_DISABLED"#%d为设备id  设备被禁用
ACCDEVICE_ENABLE_CHANGED = "ACCDEVICE_ENABLE_CHANGED"#%d为设备id  设备被禁用
ACCDEVICE_PUSH_ON = "ACCDEVICE_%s_PUSH_ON"

DEVOPT = "DEV_OPERATE"
DeviceAdvField = ['com_address','device_type', 'acpanel_type']
init_settings  = []
if settings.APP_CONFIG["remove_permision"]:
    init_settings = [ k.split(".")[1] for k,v in settings.APP_CONFIG["remove_permision"].items() if v=="False" and k.split(".")[0]=="Device"]

if settings.APP_CONFIG["iclock"]:
    if settings.APP_CONFIG["iclock"].has_key('DeviceAdvField'):
        DeviceAdvField=[]

def encodetime():
    '''
    得到当前时间的秒数
    '''
    dt = datetime.datetime.now()
    tt = ((dt.year-2000)*12*31 + (dt.month-1)*31 + (dt.day-1))*(24*60*60) + dt.hour*60*60 + dt.minute*60 + dt.second
    return tt

def format_time(tmstart, tmend):
    u"""
    时间格式转换
    """
    st=tmstart.hour*100+tmstart.minute
    et=tmend.hour*100+tmend.minute
    return (st<<16)+(et&(0xFFFF))
def save_elevatorsettings_todb(dev,interval_swip_card, keepkeyopen_time):
    from mysite.iaccess.models.accdoor import AccDoor
    door = AccDoor.objects.filter(device = dev).filter(door_no = 1)
    if door:
        door[0].card_intervaltime = interval_swip_card
        door[0].lock_delay = keepkeyopen_time
        door[0].save(force_update = True)
    return True

class ReadData(object):
    def __init__(id, timeout):
        self.id=id
        self.returndata=""
        s=sched.scheduler(time.time, time.sleep)
        for i in range(0, timeout, 2):
            s.enter(i, 1, self.read_data(), ())
        s.run()
    def read_data():
        from mysite.iclock.models.model_devcmd import DevCmd
        devcmd=DevCmd.objects.filter(id=self.id)
        if len(devcmd.CmdReturnContent)>0:
            self.returndata=devcmd.CmdReturnContent

def decode_holiday(holidayset):
    line=""
    g=[]
    for hol in holidayset:
        start = hol.start_date
        end = hol.end_date
        delta = (end-start).days+1
        for index in range(delta):
            date = start + datetime.timedelta(index)
            date = date.year*10000 + date.month*100 + date.day
            linestr={}
            linestr["HolidayType"]=hol.holiday_type
            linestr["Holiday"]=date
            if linestr not in g:
                g.append(linestr.copy())
                line += ("\r\n" if line else "") +"Holiday=%d\tHolidayType=%d\tLoop=%d"%(linestr["Holiday"], linestr["HolidayType"], hol.loop_by_year)
    return line

def decode_timeseg(segmentset):
    line=""
    for settime in segmentset:
        #print settime
        retbuf = ""
        retbuf += "TimezoneId=%d\t"%settime.id
        retbuf += "SunTime1=%d\t"%format_time(settime.sunday_start1,settime.sunday_end1)
        retbuf += "SunTime2=%d\t"%format_time(settime.sunday_start2,settime.sunday_end2)
        retbuf += "SunTime3=%d\t"%format_time(settime.sunday_start3,settime.sunday_end3)
        retbuf += "MonTime1=%d\t"%format_time(settime.monday_start1,settime.monday_end1)
        retbuf += "MonTime2=%d\t"%format_time(settime.monday_start2,settime.monday_end2)
        retbuf += "MonTime3=%d\t"%format_time(settime.monday_start3,settime.monday_end3)
        retbuf += "TueTime1=%d\t"%format_time(settime.tuesday_start1,settime.tuesday_end1)
        retbuf += "TueTime2=%d\t"%format_time(settime.tuesday_start2,settime.tuesday_end2)
        retbuf += "TueTime3=%d\t"%format_time(settime.tuesday_start3,settime.tuesday_end3)
        retbuf += "WedTime1=%d\t"%format_time(settime.wednesday_start1,settime.wednesday_end1)
        retbuf += "WedTime2=%d\t"%format_time(settime.wednesday_start2,settime.wednesday_end2)
        retbuf += "WedTime3=%d\t"%format_time(settime.wednesday_start3,settime.wednesday_end3)
        retbuf += "ThuTime1=%d\t"%format_time(settime.thursday_start1,settime.thursday_end1)
        retbuf += "ThuTime2=%d\t"%format_time(settime.thursday_start2,settime.thursday_end2)
        retbuf += "ThuTime3=%d\t"%format_time(settime.thursday_start3,settime.thursday_end3)
        retbuf += "FriTime1=%d\t"%format_time(settime.friday_start1,settime.friday_end1)
        retbuf += "FriTime2=%d\t"%format_time(settime.friday_start2,settime.friday_end2)
        retbuf += "FriTime3=%d\t"%format_time(settime.friday_start3,settime.friday_end3)
        retbuf += "SatTime1=%d\t"%format_time(settime.saturday_start1,settime.saturday_end1)
        retbuf += "SatTime2=%d\t"%format_time(settime.saturday_start2,settime.saturday_end2)
        retbuf += "SatTime3=%d\t"%format_time(settime.saturday_start3,settime.saturday_end3)
        retbuf += "Hol1Time1=%d\t"%format_time(settime.holidaytype1_start1,settime.holidaytype1_end1)
        retbuf += "Hol1Time2=%d\t"%format_time(settime.holidaytype1_start2,settime.holidaytype1_end2)
        retbuf += "Hol1Time3=%d\t"%format_time(settime.holidaytype1_start3,settime.holidaytype1_end3)
        retbuf += "Hol2Time1=%d\t"%format_time(settime.holidaytype2_start1,settime.holidaytype2_end1)
        retbuf += "Hol2Time2=%d\t"%format_time(settime.holidaytype2_start2,settime.holidaytype2_end2)
        retbuf += "Hol2Time3=%d\t"%format_time(settime.holidaytype2_start3,settime.holidaytype2_end3)
        retbuf += "Hol3Time1=%d\t"%format_time(settime.holidaytype3_start1,settime.holidaytype3_end1)
        retbuf += "Hol3Time2=%d\t"%format_time(settime.holidaytype3_start2,settime.holidaytype3_end2)
        retbuf += "Hol3Time3=%d"%format_time(settime.holidaytype3_start3,settime.holidaytype3_end3)
        line += ("\r\n" if line else "") +"%s"%(retbuf)
    return line

def device_cmd(device):
    q_server = queqe_server()
    try:
        ret = q_server.llen_file(device.new_command_list_name())
        return ret
    except:
        traceback.print_exc()
    finally:
        q_server.connection.disconnect()
    return 0

TIMEZONE_CHOICES=(
    (-750,'Etc/GMT-12:30'),
    (-12,'Etc/GMT-12'),
    (-690,'Etc/GMT-11:30'),
    (-11,'Etc/GMT-11'),
    (-630,'Etc/GMT-10:30'),
    (-10,'Etc/GMT-10'),
    (-570,'Etc/GMT-9:30'),
    (-9,'Etc/GMT-9'),
    (-510,'Etc/GMT-8:30'),
    (-8,'Etc/GMT-8'),
    (-450,'Etc/GMT-7:30'),
    (-7,'Etc/GMT-7'),
    (-390,'Etc/GMT-6:30'),    
    (-6,'Etc/GMT-6'),
    (-330,'Etc/GMT-5:30'),
    (-5,'Etc/GMT-5'),
    (-270,'Etc/GMT-4:30'),
    (-4,'Etc/GMT-4'),
    (-210,'Etc/GMT-3:30'),
    (-3,'Etc/GMT-3'),
    (-150,'Etc/GMT-2:30'),
    (-2,'Etc/GMT-2'),
    (-90,'Etc/GMT-1:30'),
    (-1,'Etc/GMT-1'),
    (-30,'Etc/GMT-0:30'),
    (0,'Etc/GMT'),
    (30,'Etc/GMT+0:30'),
    (1,'Etc/GMT+1'),
    (90,'Etc/GMT+1:30'),
    (2,'Etc/GMT+2'),
    (150,'Etc/GMT+2:30'),
    (3,'Etc/GMT+3'),
    (210,'Etc/GMT+3:30'),
    (4,'Etc/GMT+4'),
    (270,'Etc/GMT+4:30'),
    (5,'Etc/GMT+5'),
    (330,'Etc/GMT+5:30'),
    (6,'Etc/GMT+6'),
    (390,'Etc/GMT+6:30'),    
    (7,'Etc/GMT+7'),
    (450,'Etc/GMT+7:30'),
    (8,'Etc/GMT+8'),
    (510,'Etc/GMT+8:30'),
    (9,'Etc/GMT+9'),
    (570,'Etc/GMT+9:30'),
    (10,'Etc/GMT+10'),
    (630,'Etc/GMT+10:30'),
    (11,'Etc/GMT+10'),
    (690,'Etc/GMT+10:30'),
    (12,'Etc/GMT+12'),
    (750,'Etc/GMT+12:30'),
    (13,'Etc/GMT+13'),
    (810,'Etc/GMT+13:30'),

)

#COMPORT_CHOICES=(
#    (1,_('COM1')),(2,_('COM2')),(3,_('COM3')),(4,_('COM4')),(5,_('COM5')),
#    (6,_('COM6')),(7,_('COM7')),(8,_('COM8')),(9,_('COM9')),(10,_('COM10')),
#)
COMPORT_CHOICES = tuple([(i, 'COM'+str(i)) for i in range(1, 255)])#1-254

CONNECTTYPE_CHOICES = (
    (0, _(u'内容类型')),
    (1, _(u'无线局域网')),
    (2, _(u'GPRS')),
    (3, _(u'3G适配器')),
    (4, _(u'232')),
    (5, _(u'485')),
)

BAUDRATE_CHOICES=(
    (0,'9600'),(1,'19200'),(2,'38400'),(3,'57600'),(4,'115200'),
)

COMMU_MODE_PULL_TCPIP = 1
COMMU_MODE_PULL_RS485 = 2
COMMU_MODE_PUSH_HTTP = 3

COMMU_MODE_CHOICES=(
    (COMMU_MODE_PULL_TCPIP,_('TCP/IP')),
    (COMMU_MODE_PULL_RS485,_('RS485')),
    (COMMU_MODE_PUSH_HTTP, _('HTTP')),
)

DEVICE_TIME_RECORDER = 1
DEVICE_ACCESS_CONTROL_PANEL = 2
DEVICE_ACCESS_CONTROL_DEVICE = 3
DEVICE_VIDEO_SERVER =4
DEVICE_POS_SERVER = 5
DEVICE_CAMERA_SERVER = 6


DEVICE_TYPE = ()
if get_option("ATT"):#单独考勤或者ZKECO，都需要加考勤机。门禁做考勤用只需要用到考勤的业务逻辑，不需要加考勤机
    DEVICE_TYPE = ((DEVICE_TIME_RECORDER,_(u'考勤机')),)
if get_option("IACCESS"):#只要有iaccess就一定要加门禁控制器设备
    DEVICE_TYPE = DEVICE_TYPE + ((DEVICE_ACCESS_CONTROL_PANEL, _(u'门禁控制器')),)
if get_option("VIDEO"):#只要有video就一定要加硬盘录像机设备
    DEVICE_TYPE = DEVICE_TYPE + ((DEVICE_VIDEO_SERVER, _(u'硬盘录像机')),(DEVICE_CAMERA_SERVER, _(u'网络摄像机')),)
if get_option("POS"):#只要有pos就一定要加消费设备
    DEVICE_TYPE = DEVICE_TYPE + ((DEVICE_POS_SERVER, _(u'消费机')),)
if get_option("MEETING"):
    DEVICE_TYPE = ((DEVICE_TIME_RECORDER,_(u'考勤机')),)
#    (DEVICE_ACCESS_CONTROL_DEVICE,_(u'门禁考勤一体机')),    # 暂不支持

DEFAULT_DEVICE_TYPE = dict(DEVICE_TYPE).keys()[0]#DEVICE_TYPE不能为空，空的话无意义


ACPANEL_1_DOOR = 1
ACPANEL_2_DOOR = 2
ACPANEL_4_DOOR = 4
ACCESS_CONTROL_DEVICE = 5#一体机
ACPANEL_10_DOOR = 10
ACPANEL_11_DOOR = 11

#ACPANEL_TYPE_CHOICES=(
#    (ACPANEL_1_DOOR, _(u'单门控制器')),
#    (ACPANEL_2_DOOR, _(u'两门控制器')),
#    (ACPANEL_4_DOOR, _(u'四门控制器')),
#    (ACCESS_CONTROL_DEVICE,  _(u'一体机')),
#    (ACPANEL_10_DOOR, _(u'十门控制器')),
#    (ACPANEL_11_DOOR, _(u'十一门控制器')),
#)

ACPANEL_TYPE_CHOICES = ()
if get_option("IACCESS"):
    ACPANEL_TYPE_CHOICES = ((ACPANEL_1_DOOR, _(u'单门控制器')),(ACPANEL_2_DOOR, _(u'两门控制器')),(ACPANEL_4_DOOR, _(u'四门控制器')))
if get_option("ACD"):
    ACPANEL_TYPE_CHOICES = ACPANEL_TYPE_CHOICES + (ACCESS_CONTROL_DEVICE,  _(u'一体机'))
if get_option("ELEVATOR"):
    ACPANEL_TYPE_CHOICES = ACPANEL_TYPE_CHOICES+ ((ACPANEL_10_DOOR, _(u'十门控制器')),(ACPANEL_11_DOOR, _(u'十一门控制器')))

FPVERSION=(
    ('9',_(u'9.0算法')),
    ('10',_(u'10.0算法')),
)

ACPANEL_AS_USUAL_ACPANEL = 0
ACPANEL_AS_ELEVATOR = 1
ACPANEL_AS_CHOICES = (
    (ACPANEL_AS_USUAL_ACPANEL,_(u'普通门禁控制器')),
    (ACPANEL_AS_ELEVATOR,_(u'电梯控制器')),
)


CONSUMEMODEL=(
            (2,_(u'金额模式')),
            (1,_(u'定值模式')),
            (3,_(u'键值模式')),
            (4,_(u'计次模式')),
            (5,_(u'商品模式')),
            (6,_(u'计时模式')),
                  )
    

DEVICEUSETYPE =(
            (0,_(u'消费机')),
            (1,_(u'出纳机')),
            (2,_(u'补贴机')),
)

CASHMODEL =(
            (0,_(u'定值模式')),
            (1,_(u'金额模式')),
)

CASHTYPE =(
            (0,_(u'充值')),
            (1,_(u'退款')),
)
class Device(CachingModel):
    sn = models.CharField(_(u'序列号'), max_length=20, null=True, blank=True)# unique=True
    device_type = models.IntegerField(_(u'设备类型'), editable=True, choices=DEVICE_TYPE, default=DEFAULT_DEVICE_TYPE)
    last_activity = models.DateTimeField(_(u'最近联机时间'), null=True, blank=True, editable=False)
    trans_times = models.CharField(_(u'定时传送时间'), max_length=50, null=True, blank=True, default="00:00;14:05")#, help_text=_('Setting device for a moment from the plane started to send checks to the new data server. Hh: mm (hours: minutes) format, with a number of time between the semicolon (;) separately')
    trans_interval = models.IntegerField(_(u'刷新间隔时间(分钟)'), db_column="TransInterval", default=1, null=True, blank=True)#, help_text=_('Device set for each interval to check how many minutes to send new data server')
    log_stamp = models.CharField(_(u'传送签到记录标记'), max_length=20, null=True, blank=True)#, help_text=_('Logo for the latest device to the server send the transactions timestamps')
    oplog_stamp = models.CharField(_(u'传送用户数据标记'), max_length=20, null=True, blank=True)#, help_text=_('Marking device for the server to the employee data transfer as timestamps')
    photo_stamp = models.CharField(_(u'传送图片标记'), max_length=20, null=True, blank=True)#, help_text=_('Marking device for the server to the picture transfer as timestamps')
    alias = models.CharField(_(u'设备名称'), max_length=20)
    update_db = models.CharField(_(u'数据更新标志'), db_column="UpdateDB", max_length=10, null=True, default="1111101011", blank=True, editable=True)#, help_text=_('To identify what kind of data should be transfered to the server')
    push_status = models.CharField(_(u'数据下发标志'), db_column="push_status", max_length=10, null=True, default="0000000000", blank=True)
    fw_version = models.CharField(_(u'固件版本'), max_length=30, null=True, blank=True, editable=False)
    device_name = models.CharField(_(u'设备型号'), max_length=30, null=True, blank=True, editable=False)
    fp_count = models.IntegerField(_(u'指纹数'), null=True, blank=True, editable=False)
    
    face_count=models.IntegerField(_(u'人脸数'),null=True,blank=True,editable=False)
    face_tmp_count=models.IntegerField(_(u'人脸模板数'),null=True,blank=True,editable=False) 
    face_ver = models.CharField(_(u'人脸算法版本'), max_length=30, null=True, blank=True, editable=False) 
    
    transaction_count = models.IntegerField(_(u'记录数'), null=True, blank=True, editable=False)
    user_count = models.IntegerField(_(u'用户数'), null=True, blank=True, editable=False)
    main_time = models.CharField(_(u'动作时间'), max_length=20, null=True, blank=True, editable=False)
    max_user_count = models.IntegerField(_(u'最大用户容量'), null=True, blank=True, editable=False)
    max_finger_count = models.IntegerField(_(u'最大指纹容量'), null=True, blank=True, editable=False)
    max_attlog_count = models.IntegerField(_(u'最大记录容量'), null=True, blank=True, editable=False)
    alg_ver = models.CharField(_(u'Push库版本'), max_length=30, null=True, blank=True, editable=False)
    flash_size = models.CharField(_(u'总Flash容量'), max_length=10, null=True, blank=True, editable=False)
    free_flash_size = models.CharField(_(u'剩余Flash容量'), max_length=10, null=True, blank=True, editable=False)
    language = models.CharField(_(u'语言'), max_length=30, null=True, blank=True, editable=False)
    lng_encode = models.CharField(_(u'语言编码'), max_length=10, null=True, blank=True, editable=False, default="gb2312")
    volume = models.CharField(_(u'容量'), max_length=10, null=True, blank=True, editable=False)
    dt_fmt = models.CharField(_(u'日期格式'), max_length=10, null=True, blank=True, editable=False)
    is_tft = models.CharField(_(u'是否为彩屏'), max_length=5, null=True, blank=True, editable=False)
    platform = models.CharField(_(u'系统平台'), max_length=20, null=True, blank=True, editable=False)
    brightness = models.CharField(_(u'分辨率'), max_length=5, null=True, blank=True, editable=False)
    oem_vendor = models.CharField(_(u'制造商'), max_length=30, null=True, blank=True, editable=False)
    city = models.CharField(_(u'所在城市'), max_length=50, null=True, blank=True)#, help_text=_('City of the location')
    lockfun_on = models.SmallIntegerField(db_column='AccFun', default=0, blank=True, editable=False)#, help_text=_('Access Function')
    tz_adj = models.SmallIntegerField(_(u'时区'), db_column="TZAdj", default=8, null=True, blank=True, editable=True, choices=TIMEZONE_CHOICES)#help_text=_('Timezone of the location'),
    #add as follows by darcy
    comm_type = models.SmallIntegerField(_(u'通信方式'), default=3, editable=True, choices=COMMU_MODE_CHOICES)#通讯类型null=True,
    #agent_ipaddress = models.IPAddressField(_(u'通信中'), max_length=20, null=True, blank=True, editable=True, default="")
    agent_ipaddress = models.CharField(_(u'通信中'), max_length=20, null=True, blank=True, editable=True, default="")
    ipaddress = models.IPAddressField(_(u'IP地址'), max_length=20, null=True, blank=True, editable=True)
    ip_port = models.IntegerField(_(u'IP端口号'),null=True, blank=True, editable=True,default=4370)
    subnet_mask = models.IPAddressField(_(u'子网掩码'),null=True, blank=True, editable=False)
    gateway = models.IPAddressField(_(u'网关'),null=True, blank=True, editable=False)
    com_port = models.SmallIntegerField(_(u'串口号'), default=1, null=True, blank=True, editable=True, choices=COMPORT_CHOICES)#串口号
    baudrate = models.SmallIntegerField(_(u'波特率'), default=2, null=True, blank=True, editable=True, choices=BAUDRATE_CHOICES)#波特率
    com_address = models.SmallIntegerField(_(u'RS485地址'), blank=True, null=True,default=1)
    area = AreaForeignKey(verbose_name=_(u'所属区域'), editable=True, null=True,blank=True)# default=1, 
    #comm_pwd = models.CharField(_(u'通讯密码'), max_length=16, null=True, blank=True, editable=True)#仅门禁用，表单在新增时显示
    comm_pwd = models.CharField(_(u'通讯密码'), max_length=32, null=True, blank=True, editable=True)#仅门禁用，表单在新增时显示 加密后需增加长度
    acpanel_type = models.IntegerField(_(u'门禁控制器类型'), choices=ACPANEL_TYPE_CHOICES, default=2, null=True, blank=True, editable=True,)
    sync_time = models.BooleanField(_(u'自动同步设备时间'), null=False, default=True, blank=True, editable=True)
    four_to_two = models.BooleanField(_(u'切换为两门双向'), null=False, default=False, blank=True, editable=True) #C4-400,C3-400help_text=_(u" (四门单向与两门双向之间切换)"),
    video_login = models.CharField(_(u'用户名'), max_length=20, null=True, blank=True, editable=True)
    fp_mthreshold = models.IntegerField(_(u'指纹比对阈值'), null=True, blank=True, editable=False)
    Fpversion = models.CharField(verbose_name=_(u'设备指纹识别版本'), max_length=10, null=True, blank=False, editable=False,default='9',choices=FPVERSION)
    enabled = models.BooleanField(_(u'是否启用'), null=False, default=True, blank=True, editable=False)#启用True(1)-禁用False(0)-默认为1

    max_comm_size = models.IntegerField(_(u'和服务器通讯的最大数据包长度(KB)'), default=40, null=True, blank=True, editable=True)
    max_comm_count = models.IntegerField(_(u'和服务器通讯的最大命令个数'), default=20, null=True, blank=True, editable=True)
    realtime = models.BooleanField(_(u'实时上传数据'), null=False, default=True, blank=True, editable=True)
    delay = models.IntegerField(_(u'查询记录时间(秒)'), default=10, null=True, blank=True, editable=True)
    encrypt = models.BooleanField(_(u'加密传输数据'), null=False, default=False, blank=True, editable=True)
    dstime = models.ForeignKey(DSTime, verbose_name=_(u'夏令时'),editable=False, null=True, blank=True)

    is_elevator = models.IntegerField(_(u'控制器用途'),default=ACPANEL_AS_USUAL_ACPANEL, null=False, blank=False, editable=True, choices=ACPANEL_AS_CHOICES)

    
    dining = models.ForeignKey(Dininghall,verbose_name=_(u'所属餐厅'),editable=True, blank=True,null=True)
    consume_model = models.IntegerField(verbose_name=_(u'消费模式'),editable=True,choices=CONSUMEMODEL, null=True, blank=True)
#   checkisblacklist = models.BooleanField(verbose_name=_(u'是否检查黑名单'),null=False,default=True, blank=True, editable=True)#启用True(1)-禁用False(0)-默认为1
#   checkiswhitelist = models.BooleanField(verbose_name=_(u'是否检查白名单'),null=False,default=True, blank=True, editable=True)#启用True(1)-禁用False(0)-默认为1
    dz_money = models.DecimalField(verbose_name=_(u'定值金额'),max_digits=10,decimal_places=2,null=True,blank=True,editable=True)
    time_price = models.DecimalField(verbose_name=_(u'时价(元)'),max_digits=10,decimal_places=2,default=6,null=True,blank=True,editable=True)
    long_time = models.IntegerField(_(u'时长取整(分钟)'),default=20, null=True, blank=True, editable=True)
    #IC消费字段
    device_use_type = models.IntegerField(verbose_name=_(u'设备用途'),editable=True,choices=DEVICEUSETYPE, null=True, blank=True)
    cash_model = models.IntegerField(verbose_name=_(u'出纳模式'),editable=True,choices=CASHMODEL, null=True, blank=True)
    cash_type = models.IntegerField(verbose_name=_(u'出纳类型'),editable=True,choices=CASHTYPE, null=True, blank=True)
    favorable = models.IntegerField(verbose_name=_(u'优惠比例'),editable=True, null=True, blank=True,default = 0)
    card_max_money = models.DecimalField(verbose_name=_(u'最大限额'),max_digits=5,decimal_places=0,null=True,blank=True,default=999,editable=True)
    is_add = models.BooleanField(verbose_name=_(u"累加补贴"), default=False)#对未下发的补贴金额进行累计再下发
    is_zeor = models.BooleanField(verbose_name=_(u"清零补贴"), default=False)#每次只下发最后一次补贴金额
    is_OK = models.BooleanField(verbose_name=_(u"按确定键补贴"), default=False)# 是否按确定键进行补贴
    check_black_list = models.BooleanField(verbose_name=_(u'黑名单检查'),null=False,default=True, blank=True, editable=True)#启用True(1)-禁用False(0)-默认为1
    check_white_list = models.BooleanField(verbose_name=_(u'白名单检查'),null=False,default=False, blank=True, editable=True)#启用True(1)-禁用False(0)-默认为1
    is_cons_keap = models.BooleanField(verbose_name=_(u"是否记账"), default=False)
    is_check_operate = models.BooleanField(verbose_name=_(u"操作员卡检查"), default=False)
    pos_all_log_stamp = models.CharField(_(u'传送所有记录标记'), max_length=20, null=True, blank=True,editable=False)#为设备最后上传消费记录的记录时间戳标记
    pos_log_stamp = models.CharField(_(u'传送消费记录时间戳'), max_length=20, null=True, blank=True,editable=False)#为设备最后上传消费记录的记录时间戳标记
    full_log_stamp  = models.CharField(_(u'传送充值记录时间戳'), max_length=20, null=True, blank=True,editable=False)#为设备最后上传充值记录的记录时间戳标记
    allow_log_stamp  = models.CharField(_(u'传送补贴记录时间戳'), max_length=20, null=True, blank=True,editable=False)#为设备最后上传补贴记录的记录时间戳标记 
    table_name_stamp = models.CharField(_(u'自动上传数据时间戳'), max_length=20, null=True, blank=True,editable=False)#自动上传数据时间日戳。TableName相应数据表名，与固件注册的数据表命名保持一致，Stamp为固定标志; 所有自动上传数据表的时间戳需返回给设备
    only_RFMachine = models.CharField(_(u'是否只是卡机'), max_length=5, null=True, blank=True, editable=False,default='0')
    pos_log_stamp_id = models.CharField(_(u'传送消费记录标记'), max_length=20, null=True, blank=True,default = '0',editable=False)#为设备最后上传消费记录的记录设备流水号标记
    full_log_stamp_id  = models.CharField(_(u'传送充值记录标记'), max_length=20, null=True, blank=True,default = '0',editable=False)#为设备最后上传充值记录的记录设备流水号标记
    allow_log_stamp_id  = models.CharField(_(u'传送补贴记录标记'), max_length=20, null=True, blank=True,default = '0',editable=False)#为设备最后上传补贴记录的记录设备流水号标记 
    
    pos_log_bak_stamp_id = models.CharField(_(u'传送备份消费记录标记'), max_length=20, null=True, blank=True,default = '0',editable=False)#为设备最后上传消费记录的记录设备流水号标记
    full_log_bak_stamp_id  = models.CharField(_(u'传备份送充值记录标记'), max_length=20, null=True, blank=True,default = '0',editable=False)#为设备最后上传充值记录的记录设备流水号标记
    allow_log_bak_stamp_id  = models.CharField(_(u'传备份送补贴记录标记'), max_length=20, null=True, blank=True,default = '0',editable=False)#为设备最后上传补贴记录的记录设备流水号标记 
    pos_dev_data_status = models.BooleanField(verbose_name=_(u"记录是否完整"), default=True,editable=False)#消费设备记录的所有记录是否成功上传
    
    
    def data_valid(self, sendtype):
        #print "sendtype:%s",sendtype

#        if self.comm_type == COMMU_MODE_PULL_RS485:#rs485通讯
#            tmp_dev = Device.objects.filter(com_port=self.com_port, com_address=self.com_address)
#            if tmp_dev and tmp_dev[0].id != self.id:#
#                raise Exception(_(u'串口 %(f)s 的485地址 %(ff)s 已存在')%{"f":dict(COMPORT_CHOICES)[self.com_port], "ff":self.com_address})

        if self.comm_type in [COMMU_MODE_PULL_TCPIP, COMMU_MODE_PUSH_HTTP]:
            #if self.ipaddress:#当通讯方式为485时ip地址为空
            tmp_ip = Device.objects.filter(ipaddress__exact = self.ipaddress.strip())
            if (self.comm_type==COMMU_MODE_PULL_TCPIP) and len(tmp_ip)>0 and tmp_ip[0].id != self.id:   #编辑状态
                raise Exception(_(u'IP地址为:%s 的设备已存在')%self.ipaddress)
        self.__class__.page_input=True              #当修改设备信息时需要下发指令，增加此属性

    def save(self, **args):
        from django.conf import settings
        from mysite.authorize_fun import get_cache
        import re
        tmpre = re.compile('^[0-9]+$')
        if self.sn and not tmpre.search(self.sn):
            raise Exception(_(u'设备序列号只能为数字'))
        is_new = False #是否新增 
        if not self.pk:
            is_new = True
        
        if self.sn:
            self.sn = self.sn.strip()
        if self.comm_pwd:
            dev = Device.objects.filter(pk=self.pk)
            if len(dev)!=0:
                if dev[0].comm_pwd == self.comm_pwd and not dev[0].comm_pwd.isdigit():
                    pass
                else:
                    self.comm_pwd = encryption(self.comm_pwd)
            else:
                self.comm_pwd = encryption(self.comm_pwd)
        if self.comm_type == COMMU_MODE_PULL_RS485:#rs485通讯
            self.ipaddress = None
            self.ip_port = None
        elif self.comm_type in [COMMU_MODE_PULL_TCPIP, COMMU_MODE_PUSH_HTTP]:
            self.com_address = None
            self.com_port = None
            self.baudrate = None
            
        zkeco_count = get_cache("ZKECO_DEVICE_LIMIT")
        zktime_count = get_cache("ATT_DEVICE_LIMIT")
        zkaccess_count = get_cache("MAX_ACPANEL_COUNT")
        zkpos_count = get_cache("POS_DEVICE_LIMIT")

        try:
            if zkeco_count != 0:
                all_dev_count=Device.objects.all().count()
                if (all_dev_count > zkeco_count and is_new):
                   raise Exception(_(u"登记的设备总数%(d1)s，已经达到系统限制%(d2)s！")%{"d1":all_dev_count,"d2":zkeco_count});
            
            if self.device_type == DEVICE_TIME_RECORDER:
                #新增、修改时考勤的序列号不为空(考勤)，门禁新增时为'',修改时可能为空可能不为空(用户不可见)
                tmp_sn = Device.objects.filter(sn__exact=self.sn.strip())
                if len(tmp_sn) > 0 and tmp_sn[0].id != self.id:   #编辑状态
                    raise Exception(_(u'序列号：%s 已存在') % self.sn)

                sem.acquire()
                count=Device.objects.filter(device_type=DEVICE_TIME_RECORDER).count()
                try:
                    if (count < zktime_count) or (count == zktime_count and self.pk):
                        self.acpanel_type = None
                        self.consume_model = None
                        super(Device, self).save(**args)
                    elif zkeco_count != 0:
                        count=Device.objects.filter(device_type__in = [DEVICE_TIME_RECORDER, DEVICE_ACCESS_CONTROL_PANEL]).count()
                        if (count < zkeco_count) or (count == zkeco_count and self.pk):
                            self.acpanel_type = None
                            self.consume_model = None
                            super(Device, self).save(**args)
                        else:
                            raise Exception(_(u"登记的设备总数%(d1)s，已经达到系统限制%(d2)s！")%{"d1":count,"d2":zkeco_count});
                    else:                        
                        raise Exception(_(u"登记的考勤机数%(d1)s，已经达到系统限制%(d2)s！")%{"d1":count,"d2":zktime_count});
                finally:
                        sem.release()
                if hasattr(self.__class__,"page_input"):
                    if self.__class__.page_input:                                    
                        from mysite.iclock.dataprocaction import append_dev_cmd
                        append_dev_cmd(self,"CHECK")      #修改或新增都需要对机器下发CHECK指令
                        self.__class__.page_input=False
                #缓存或更新设备信息
                self.cache_device(is_new=is_new)
            elif self.device_type == DEVICE_POS_SERVER:
                from mysite.pos.pos_constant import TIMEOUT
                #消费===================================  
                tmp_sn = Device.objects.filter(sn__exact=self.sn.strip())
                if len(tmp_sn) > 0 and tmp_sn[0].id != self.id:   #编辑状态
                    raise Exception(_(u'序列号：%s 已存在') % self.sn)
                sem.acquire()
                count=Device.objects.filter(device_type=DEVICE_POS_SERVER).count()
                if get_option("POS_ID"):#暂时没用刀加密狗参数
                    POS_DEVICE_LIMIT = settings.POS_ID_DEVICE_LIMIT
                else:
                    POS_DEVICE_LIMIT = settings.POS_IC_DEVICE_LIMIT
                try:
                    if (count < zkpos_count) or (count == zkpos_count and self.pk):#20120907消费设备台数加入到zkeco加密狗台数控制
                        self.acpanel_type = None
                        self.Fpversion = None
                        super(Device, self).save(**args)
                        cache.set(self.sn,self,TIMEOUT)
                    elif zkeco_count != 0:
                        count=Device.objects.all().count()
                        if (count < zkeco_count) or (count == zkeco_count and self.pk):
                            self.acpanel_type = None
                            self.Fpversion = None
                            super(Device, self).save(**args)
                            cache.set(self.sn,self,TIMEOUT)
                        else:
                            raise Exception(_(u"登记的设备总数%(d1)s，已经达到系统限制%(d2)s！")%{"d1":count,"d2":zkeco_count});
                    else:    
                        raise Exception(_(u"登记的消费机数%(d1)s，已经达到系统限制%(d2)s！")%{"d1":count,"d2":zkpos_count});
                finally:
                        sem.release()
                if hasattr(self.__class__,"page_input"):
                    if self.__class__.page_input:                                    
                        from mysite.iclock.dataprocaction import append_dev_cmd
#                            append_dev_cmd(self,"CHECK")      #修改或新增都需要对机器下发CHECK指令
                        if get_option("POS_IC"):
                            from mysite.iclock.models.dev_comm_operate import update_pos_device_info
                            ret = self.set_pos_device_option()
                            update_pos_device_info([self],None,"CARDMANAGE")
                        else:
                            key = self.sn.strip()+"_update_db"
                            cache.set(key,1,TIMEOUT)
                        self.__class__.page_input=False           
                #缓存或更新设备信息
                self.cache_device(is_new=is_new)
                if get_option("POS_IC") and is_new:
                    from mysite.pos.pos_ic.ic_sync_action import init_ic_pos_device
                    init_ic_pos_device(self)
                    self.set_all_pos_data()
                    
            else:
                #force_insert = 'force_insert' in args.keys() and args['force_insert'] or False#update时为False不判断最大数量
                tmp_alias = Device.objects.filter(device_type__in = [DEVICE_ACCESS_CONTROL_PANEL, DEVICE_VIDEO_SERVER, DEVICE_CAMERA_SERVER]).filter(alias__exact = self.alias.strip())
                if len(tmp_alias)>0 and tmp_alias[0] != self:   #编辑状态
                    raise Exception(_(u'设备名称：%s 已存在') % self.alias)
                elif self.id:
                    from mysite.iaccess.dev_comm_center import OPERAT_EDIT
                    self.add_comm_center(self.getdevinfo(), OPERAT_EDIT)

                if self.device_type == DEVICE_ACCESS_CONTROL_PANEL:
                    sem.acquire()
                    acc_limit = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL).count()
                    try:
                        if (acc_limit < zkaccess_count) or (acc_limit == zkaccess_count and self.pk):
                            self.TZAdj = None
                            self.max_comm_count = None
                            self.max_comm_size = None
                            self.delay = None
                            self.Fpversion = None
                            self.consume_model = None
                            super(Device, self).save(**args)

                        elif zkeco_count != 0:
                            count = Device.objects.filter(device_type__in = [DEVICE_TIME_RECORDER, DEVICE_ACCESS_CONTROL_PANEL]).count()
                            if (count < zkeco_count) or (count == zkeco_count and self.pk):
                                self.TZAdj = None
                                self.max_comm_count = None
                                self.max_comm_size = None
                                self.delay = None
                                self.Fpversion = None
                                self.consume_model = None
                                super(Device, self).save(**args)
                            else:
                                raise Exception(_(u"登记的设备总数，已经达到系统限制！"));
                        else:                        
                            raise Exception(_(u'系统最大支持%s台门禁控制器') % zkaccess_count)
                        
                    finally:
                            sem.release()
                elif self.device_type == DEVICE_VIDEO_SERVER or self.device_type == DEVICE_CAMERA_SERVER:
                    self.acpanel_type = None
                    self.Fpversion = None
                    self.consume_model = None
                    #print "save video server"
                    super(Device, self).save(**args)

        except Exception, e:
            print_exc()
            raise e
        
    def cache_device(self,*args,**kwarg):
        u'''缓存设备的信息,不管是新增还是修改都更新'''
        from mysite.iclock.cache_cmds import cache_device_sn,cache_device
        is_new=kwarg.pop("is_new",None)
        cache_device(self) #缓存设备
        if is_new:
            cache_device_sn(self) #缓存设备SN

    def delete(self):#
        from mysite import settings
        try:
            if self.device_type == DEVICE_TIME_RECORDER:
                from mysite.iclock.cache_cmds import cache_delete_device,cache_delete_sn,cache_delete_cmds
                cache_delete_device(self)#删除缓存设备对象
                from base.sync_api import SYNC_MODEL
                if not SYNC_MODEL:
                    cache_delete_sn(self)#删除文件中的SN序列号
                    cache_delete_cmds(self)#删除设备命令缓存
                if "mysite.meeting" in settings.INSTALLED_APPS:
                    from mysite.meeting.models.room import Room
#                    from mysite.iclock.models.room import Room
                    deviceOfMeeting = Room.objects.filter(devices__sn = self.sn)#判断会议室中是否在使用考勤签到设备
                    if len(deviceOfMeeting)>0:
                        raise Exception(_(u'会议室中正在使用该设备'))
               
            
            if self.device_type == DEVICE_ACCESS_CONTROL_PANEL:
                devinfo = self.getdevinfo()
                #删除相关缓存
                self.clear_device_cache()

                d_server = start_dict_server()
                from mysite.iaccess.dev_comm_center import OPERAT_DEL, delete_tempcmd
                timeout = 0
                while True:
                    temp_cmd_lock = d_server.get_from_dict("TEMP_CMD_LOCK")
                    if temp_cmd_lock:#如果当前其他线程或者进程在进行同样的操作，等待
                        timeout += 1
                        if timeout > 300:
                            break#超时后不放入缓存
                        time.sleep(0.5)
                        continue
                    else:
                        d_server.set_to_dict("TEMP_CMD_LOCK", 1)
                        immed_cmd_dict = d_server.get_from_dict("TEMP_CMD")
                        devcmd_list = None
                        if immed_cmd_dict:
                            devcmd_list = immed_cmd_dict.get(self.id)
                        delete_tempcmd(self, devcmd_list, d_server)
                        cnk = self.command_count_key()
                        d_server.delete_dict(cnk)
                        d_server.set_to_dict("TEMP_CMD_LOCK", 0)
                        break
                #from mysite.iaccess.dev_comm_center import OPERAT_DEL
                devinfo["operatstate"] = OPERAT_DEL
                minfo = True      #没有相同操作
                lens = d_server.llen_dict(DEVOPT)   #设备操作列表
                dev_opt = d_server.get_from_dict(DEVOPT) or []
                for info in dev_opt:
                    try:
                        #dinfo=pickle.loads(info[0])
                        dinfo = pickle.loads(info)
                        #print '----delete device  dinfo=',dinfo
                        if dinfo["id"] == devinfo["id"]:
                            minfo = False
                            break;
                    except:
                        dinfo = False
                #没有相同的操作就加,
                if minfo:
                    #print "add operate delete"
                    d_server.rpush_to_dict(DEVOPT, pickle.dumps(devinfo))
                dev_id = self.pk
                super(Device, self).delete()
                #d_server.delete_dict(ACCDEVICE_INFO%dev_id)#如果已存在,就删除
                d_server.set_to_dict("DEVICE_DELETE", 1)
                d_server.set_to_dict("DEVICE_DELETE_MONITOR", 1)#删除设备后通知监控更新缓存 
                d_server.close()
            elif self.device_type == DEVICE_POS_SERVER:
                from mysite.iclock.cache_cmds import cache_delete_device,cache_delete_sn,cache_delete_cmds
                from mysite.pos.pos_constant import TIMEOUT 
                from mysite.pos.pos_ic.ic_sync_model import Pos_Device
                super(Device, self).delete()
                cache_delete_device(self)#删除缓存设备对象
                cache_delete_sn(self)#删除文件中的SN序列号
                cache_delete_cmds(self)#删除设备命令缓存
                
                redis_device=Pos_Device(self.sn)
                redis_device.delete()
                
                
                key=self.sn
                cache.delete(key)
                from mysite.personnel.models.model_iccard import ICcard,get_device_code
                objICcard = ICcard.objects.all()
                if objICcard:
                    for obj in objICcard:
                        key="use_mechine_"+str(obj.pk)
                        use_device=obj.use_mechine.get_query_set()
                        cache.set(key,list(use_device),TIMEOUT)
            else:
                super(Device, self).delete()
        except Exception, e:
            print_exc()
            raise e

    def clear_device_cache(self):
        q_server = queqe_server()
        q_server.delete_file(self.new_command_list_name())
        q_server.connection.disconnect()

        d_server = start_dict_server()
        d_server.delete_dict(self.processing_command_set_name())
        d_server.delete_dict(self.cache_key())
        d_server.delete_dict(self.command_temp_list_name())
        d_server.delete_dict(self.command_count_key())
        d_server.delete_dict(self.get_doorstate_cache_key())
        d_server.delete_dict(self.get_last_activity())
        d_server.close()

    def get_std_fw_version(self):
        return ""

    def cache_key(self):
        return "ICLOCK_%s"%self.id

    #命令队列
    def new_command_list_name(self):
        return "NEWCMDS_%s"%self.id

    #命令执行
    def processing_command_set_name(self):
        return "PROCCMDS_%s"%self.id

    #当前执行命令缓存
    def command_temp_list_name(self):
        return "ICLOCK_%s_TMP"%self.id

    #命令统计
    def command_count_key(self):
        return "ICLOCK_%s_CMD"%self.id

    #门状态
    def get_doorstate_cache_key(self):
        return "DEVICE_DOOR_%s"%self.id

    #最后连接时间
    def get_last_activity(self):
        return "ICLOCK_%d_LAST_ACTIVEITY"%self.id

    #下载新记录标记
    def get_transaction_cache(self):
        return "ICLOCK_%d_TRANS_CACHE"%self.id

    #标记正在同步所有数据（仅门禁）
    def whether_setting_all_data(self):
        return "DEVICE_%s_SETTING_ALL_DATA" % self.id

    def set_fqueue_progress(self, gress, session_key):
        d_server = start_dict_server()
        d_server.set_to_dict("DEV_COMM_PROGRESS_%s"%session_key, "%s,%d"%(self.alias.encode("gb18030"), gress))
        d_server.close()
        return 0

    def get_dyn_state(self):
        try:
            if self.state==DEV_STATUS_PAUSE:
                return DEV_STATUS_PAUSE
            if not self.last_activity:
                return DEV_STATUS_OFFLINE
            d=datetime.datetime.now()-self.last_activity
            if d>datetime.timedelta(0,5*60):
                return DEV_STATUS_OFFLINE
            #如果有命令等待执行，返回“通讯中”
            if device_cmd(self)>0:  #if DevCmd.objects.filter(SN=self,CmdOverTime__isnull=True).count()>0:
                return DEV_STATUS_TRANS
            return DEV_STATUS_OK
        except:
            errorLog()

    def check_dev_enabled(self):
        return self.enabled

    def set_dev_disabled(self, d_server):
        self.enabled = False
        self.save(force_update=True)
        d_server.set_to_dict(ACCDEVICE_DISABLED%self.pk, True)#禁用该设备。获取到False或者返回None均为未禁用（启用）
        d_server.set_to_dict(ACCDEVICE_ENABLE_CHANGED, True)#任何一个设备被禁用，实时监控都需要重新获取设备。-darcy20111012        #print '----get disabled=',q_server.get_from_dict(ACCDEVICE_DISABLED%self.pk)

    def set_dev_enabled(self, d_server):
        self.enabled = True
        self.save(force_update=True)
        #q_server.set_to_dict(ACCDEVICE_DISABLED%self.pk, False)#禁用该设备。获取到False或者返回None均为未禁用（启用）
        d_server.delete_dict(ACCDEVICE_DISABLED%self.pk)
        d_server.set_to_dict(ACCDEVICE_ENABLE_CHANGED, True)#任何一个设备被禁用或启用，实时监控都需要重新获取设备。-darcy20111012

    def get_img_url(self):
        if self.DeviceName:
            imgUrl=settings.MEDIA_ROOT+'img/device/'+self.DeviceName+'.png'
            if os.path.exists(imgUrl):
                return settings.MEDIA_URL+'/img/device/'+self.DeviceName+'.png'
        return settings.MEDIA_URL+'/img/device/noImg.png'

    def get_thumbnail_url(self):
        return self.get_img_url()

    def set_acc_baudrate(self, baudrate):
        CMD = "SET OPTION RS232BaudRate=%s" % baudrate#
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
    
    def set_mthreshold(self, threshold):
        from mysite.iclock.dataprocaction import appendDevCmdReturn
        CMD = "SET OPTION MThreshold=%d" % threshold   #同步指纹阈值
        #return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)#appendcmdreturn
        return appendDevCmdReturn(self, CMD)
    
    def set_elevator_params(self,interval_swip_card, keepkeyopen_time):
        from mysite.iclock.dataprocaction import appendDevCmdReturn
        CMD = "SET OPTION Door1Intertime=%d,Door1Drivertime=%d" %(interval_swip_card, keepkeyopen_time) #梯控锁驱动时长和刷卡间隔
        return appendDevCmdReturn(self, CMD)
  
    def __unicode__(self):
        if self.device_type in [DEVICE_ACCESS_CONTROL_PANEL, DEVICE_VIDEO_SERVER]:
            return self.alias
        return self.sn+(self.alias and "("+self.alias+")" or "")
#        return self.alias or ""

    #设置全局反潜参数   ----darcy 20110901   
    def set_acc_gapb(self, enable):
        return self.appendcmdreturn("SET OPTION OverallAntiFunOn=%s"%enable)
    
    #设置门禁控制器push功能参数   ----darcy 20110901   
    def set_acc_push_params(self, enable):
        
        ip_address = socket.gethostbyname(socket.gethostname())#获取服务IP，
        cfg = dict4ini.DictIni(os.getcwd()+"/attsite.ini", values={"Options":{"Port":80}}) #默认0点定时下载新记录
        port = cfg.Options.Port
        if enable:
            ret = self.appendcmdreturn("SET OPTION IclockSvrFun=%s,WebServerIP=%s,WebServerPort=%s"%(enable, ip_address,port))
        else:
            ret = self.appendcmdreturn("SET OPTION IclockSvrFun=%s"%enable)
        return ret
            
#    class OpReloadLogData(Operation):
#        help_text=_("upload transactions again from device")
#        verbose_name = u"重新上传记录"
#        def action(self):
#            from mysite.iclock.dataprocaction import reloadLogDataCmd
#            reloadLogDataCmd(self.object)

                
#    class PowerSuspend(Operation):
#        help_text=u"""设置自动关机"""
#        verbose_name=u"""设置自动关机"""
#        def action(self):
#            return setOpt(self.object,params)



    #数据同步相关命令
    def appendcmd(self, cmd, Op=None):
        from mysite.iclock.dataprocaction import append_dev_cmd
        append_dev_cmd(self, cmd, Op)

    def appendcmdreturn(self, cmd, timeout=None):
        from mysite.iclock.dataprocaction import appendDevCmdReturn
        from mysite.iclock.models.model_devcmd import DevCmd
        cmdid = appendDevCmdReturn(self, cmd)
        #print "##cmdid==",cmdid
        returncmd = None
        if not timeout:
            timeout = MAX_COMMAND_TIMEOUT_SECOND
        for i in range(0, timeout, 1):
            #print "##appendcmdreturn==", i
            devcmd = DevCmd.objects.filter(id=cmdid)
            #print devcmd[0].CmdReturn
            if devcmd:
                returncmd = devcmd[0].CmdReturn
            if returncmd is not None:#返回大于等于0表示成功
                break
            #print "##returncmd=", returncmd
            time.sleep(1)
        return returncmd#返回None说明固件没有返回值。返回0说明成功，负数说明失败。如果是获取记录大于零表示记录条数--comment by darcy

    def getdevinfo(self):
        comminfo = {
            'id': self.id,
            'comm_type': self.comm_type,
            'operatstate': 0,
            'commstate': 0,
            'password': decryption(self.comm_pwd),
        }
        if self.comm_type == COMMU_MODE_PULL_TCPIP:
            comminfo['ipaddress'] = self.ipaddress
            comminfo['ip_port'] = self.ip_port
        elif self.comm_type == COMMU_MODE_PULL_RS485:
            comminfo['com_address'] = self.com_address
            comminfo['com_port'] = "COM"+str(self.com_port)
            comminfo['baudrate'] = self.baudrate and Device._meta.get_field('baudrate').choices[self.baudrate][1] or ''
        return comminfo

    def getcomminfo(self):
        comminfo={
            'id': self.id,
            'comm_type': self.comm_type,
            'ipaddress': self.ipaddress,
            'ip_port': self.ip_port,
            'com_port': "COM"+str(self.com_port),
            'com_address': self.com_address,
            'baudrate': self.baudrate and Device._meta.get_field('baudrate').choices[self.baudrate][1] or '',
            'password': self.comm_pwd and decryption(self.comm_pwd) or "",
        }
        return comminfo

    def search_user_bydevice(self): #查找设备关联员工 返回empobjects
        return self.area.employee_set.all()

    def search_accuser_bydevice(self):
        from mysite.personnel.models import Employee
        from mysite.iaccess import sqls
        #sql="select distinct employee_id from acc_levelset_emp where acclevelset_id in ( select distinct acclevelset_id from  acc_levelset_door_group  where accdoor_id in (select id from acc_door where device_id=%d))"%self.id
        sql=sqls.search_accuser_bydevice_select(self.id)
        cursor = connection.cursor()
        cursor.execute(sql)
        fet=[f[0] for f in set(cursor.fetchall())]
        i = 0
        each_rows = 800  #sql server where 参数长度问题
        empsets = []
        while i < len(fet):
            emp_list = Employee.objects.filter(id__in = fet[i:i+each_rows])
            for emp in emp_list:
                empsets.append(emp)
            i += each_rows
        return empsets

    def report_user(self, table, objectset, Op=None, session_key="", immediate=False, timeout=0):
        from mysite.personnel.models.model_emp import device_pin
        from mysite.iclock.models.modelproc import get_normal_card
        from mysite.iaccess.models.accdoor import DEVICE_C3_100, DEVICE_C3_200, DEVICE_C3_400, DEVICE_C3_400_TO_200
        CMD=""
        #print " ---report_user    len(object)=",len(objectset)#注意不能屏蔽删除，处理sqlserver 查询的问题
        if (table.upper() == "USER"):
            line=""
            if self.device_type == DEVICE_TIME_RECORDER:
                #print datetime.datetime.now()
                #pk_lst=objectset.values_list('Card','EName','PIN','Password','AccGroup')
                for u in objectset:
                    line="CardNo=%s\tName=%s\tPin=%s\tPassword=%s\tGroup=%s\tPri=%s"%(get_normal_card("0"),u.EName,
                        device_pin(u.PIN), decryption(u.Password) or "", u.AccGroup and u.AccGroup or 0,u.Privilege and u.Privilege or 0)
                    CMD="DATA UPDATE user %s"%(line)
                    self.appendcmd(CMD, Op)
            elif self.device_type == DEVICE_ACCESS_CONTROL_PANEL:
                line_tuple = []
                for u in objectset:
                    if (u.acc_startdate is None):
                        sdate=0
                    else:
                        sdate = u.acc_startdate.year*10000 + u.acc_startdate.month*100 + u.acc_startdate.day
                    if (u.acc_enddate is None):
                        edate=0
                    else:
                        edate = u.acc_enddate.year*10000 + u.acc_enddate.month*100 + u.acc_enddate.day
#                    if self.accdevice.machine_type == 12:
#                        line_tuple.append("\r\nCardNo=%s\tName=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d\tSuperAuthorize=%d"%(u.Card, u.EName.decode('utf8').encode('GBK'), u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate, u.acc_super_auth or 0))
#                    else:
#                        line_tuple.append("\r\nCardNo=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d\tSuperAuthorize=%d"%(u.Card,u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate, u.acc_super_auth or 0))
                    
                    if self.accdevice.machine_type not in [DEVICE_C3_100, DEVICE_C3_200, DEVICE_C3_400, DEVICE_C3_400_TO_200]:
                        try:
                            line_tuple.append("\r\nCardNo=0\tName=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d"%(u.EName and u.EName.decode('utf8').encode('gb18030'), u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate))
                        except:
                            line_tuple.append("\r\nCardNo=0\tName=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d"%(u.EName or '', u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate))

                    else:
                        line_tuple.append("\r\nCardNo=0\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d"%(u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate))
                    
                    if len(line_tuple) == 10000:  #拆分命令，防止字符串太长，写入MYSQL时出现GONE AWAY问题
                        line = ''.join(line_tuple).replace("\r\n","",1)
                        if len(line)>0:
                            CMD="DATA UPDATE user %s"%(line)
                            self.appendcmd(CMD, Op)
                        line = ""
                        line_tuple = []
                line = ''.join(line_tuple).replace("\r\n","",1)
                if len(line)>0:
                    CMD="DATA UPDATE user %s"%(line)
                    self.appendcmd(CMD, Op)
        else:
            pass

    def set_data(self, table, objectset, Op=None, session_key="", immediate=False, timeout=0):
        from mysite.personnel.models.model_emp import device_pin
        from mysite.iclock.models.modelproc import get_normal_card
        from mysite.iaccess.models.accdoor import DEVICE_C3_100, DEVICE_C3_200, DEVICE_C3_400, DEVICE_C3_400_TO_200
        CMD=""
        #print "len(object)=",len(objectset)#注意不能屏蔽删除，处理sqlserver 查询的问题
        if (table.upper() == "USER"):
            line=""
            temp_card = "0"
            if self.device_type == DEVICE_TIME_RECORDER:
                #print datetime.datetime.now()
                #pk_lst=objectset.values_list('Card','EName','PIN','Password','AccGroup')
                for u in objectset:
                    if u.Card and u.Card<>"":
                        temp_card = u.Card
                    line="CardNo=%s\tName=%s\tPin=%s\tPassword=%s\tGroup=%s\tPri=%s"%(get_normal_card(temp_card),u.EName,
                        device_pin(u.PIN), decryption(u.Password) or "", u.AccGroup and u.AccGroup or 0,u.Privilege and u.Privilege or 0)
                    CMD="DATA UPDATE user %s"%(line)
                    self.appendcmd(CMD, Op)
            elif self.device_type == DEVICE_ACCESS_CONTROL_PANEL:
                line_tuple = []
                for u in objectset:
                    if (u.acc_startdate is None):
                        sdate=0
                    else:
                        sdate = u.acc_startdate.year*10000 + u.acc_startdate.month*100 + u.acc_startdate.day
                    if (u.acc_enddate is None):
                        edate=0
                    else:
                        edate = u.acc_enddate.year*10000 + u.acc_enddate.month*100 + u.acc_enddate.day
#                    if self.accdevice.machine_type == 12:
#                        line_tuple.append("\r\nCardNo=%s\tName=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d\tSuperAuthorize=%d"%(u.Card, u.EName.decode('utf8').encode('GBK'), u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate, u.acc_super_auth or 0))
#                    else:
#                        line_tuple.append("\r\nCardNo=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d\tSuperAuthorize=%d"%(u.Card,u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate, u.acc_super_auth or 0))
                    
                    if self.accdevice.machine_type not in [DEVICE_C3_100, DEVICE_C3_200, DEVICE_C3_400, DEVICE_C3_400_TO_200]:
                        try:
                            line_tuple.append("\r\nCardNo=%s\tName=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d"%(u.Card, u.EName and u.EName.decode('utf8').encode('gb18030'), u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate))
                        except:
                            line_tuple.append("\r\nCardNo=%s\tName=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d"%(u.Card, u.EName or '', u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate))

                    else:
                        line_tuple.append("\r\nCardNo=%s\tPin=%s\tPassword=%s\tGroup=%d\tStartTime=%d\tEndTime=%d"%(u.Card,u.PIN, decryption(u.Password) or "", u.morecard_group and u.morecard_group.id or 0, sdate, edate))
                    
                    if len(line_tuple) == 10000:  #拆分命令，防止字符串太长，写入MYSQL时出现GONE AWAY问题
                        line = ''.join(line_tuple).replace("\r\n","",1)
                        if len(line)>0:
                            CMD="DATA UPDATE user %s"%(line)
                            self.appendcmd(CMD, Op)
                        line = ""
                        line_tuple = []
                line = ''.join(line_tuple).replace("\r\n","",1)
                if len(line)>0:
                    CMD="DATA UPDATE user %s"%(line)
                    self.appendcmd(CMD, Op)

        elif (table.upper() == "FINGERPRINT"):
            line=""
            t = time.time()
            if self.comm_type==COMMU_MODE_PUSH_HTTP:
                from mysite.personnel.models import Employee
                for template in objectset:
                    if len(template.Template)>0:
                        emp=Employee.objects.get(PIN=template.UserID)
                        line = "Pin=%s\tFingerID=%d\tTemplate=%s"%(device_pin(emp.PIN), template.FingerID, template.Template)
                        CMD="DATA UPDATE fingerprint %s"%(line)
                        self.appendcmd(CMD, Op)
            else:
                line_tuple = []
                for template in objectset:
                    if len(template.Template)>0:
                        line_tuple.append("\r\nPin=%s\tFingerID=%d\tTemplate=%s"%(template.UserID, template.FingerID, template.Template))

                line = ''.join(line_tuple).replace("\r\n","",1)
                if len(line)>0:
                    CMD="DATA UPDATE fingerprint %s"%(line)
                    self.appendcmd(CMD, Op)       
        elif (table.upper() == "FACETEMPLATE"):#------------------------下发人脸模板FACETEMPLATE
            line=""#----命令行
            t = time.time()
            if self.comm_type==COMMU_MODE_PUSH_HTTP:    #---通信类型
                for face in objectset:   
                    if len(face.facetemp)>0:
                        line = "PIN=%s\tFID=%d\tSIZE=%d\tValid=%d\tTMP=%s"%(device_pin(face.user), face.faceid,len(face.facetemp),face.valid, face.facetemp)
                        CMD="DATA UPDATE FACE %s"%(line)
                        self.appendcmd(CMD, Op)
            else:
                line_tuple = []
                for face in objectset:
                    if len(face.facetemp)>0:
                        line_tuple.append("\r\nPIN=%s\tFID=%d\tSIZE=%d\tValid=%d\tTMP=%s"%(face.user, face.faceid,len(face.facetemp),face.valid, face.facetemp))
                line = ''.join(line_tuple).replace("\r\n","",1)
                if len(line)>0:
                    CMD="DATA UPDATE FACE %s"%(line)
                    self.appendcmd(CMD, Op)

        elif (table.upper() == "TEMPLATEV10"):#仅门禁控制器
            if self.accdevice.IsOnlyRFMachine == 0:
                line=""
                line_tuple = []
                objectset = [object for object in objectset]
                for template in objectset:
                    if len(template.Template)>0:
                        line_tuple.append("\r\nPin=%s\tFingerID=%d\tValid=%d\tTemplate=%s"%(template.UserID, template.FingerID, template.Valid, template.Template))
                    if len(line_tuple) == 500:#800以上可能会导致mysql挂掉
                        line = ''.join(line_tuple).replace("\r\n","",1)
                        CMD="DATA UPDATE templatev10 %s"%(line)
                        self.appendcmd(CMD, Op)
                        line = ""
                        line_tuple = []
                line = ''.join(line_tuple).replace("\r\n","",1)
                if len(line)>0:
                    CMD="DATA UPDATE templatev10 %s"%(line)
                    self.appendcmd(CMD, Op)
        elif (table.upper()=="USERAUTHORIZE"):
            line=""
            line_tuple = []
            for level in objectset:
                line_tuple.append("\r\nPin=%s\tAuthorizeTimezoneId=%d\tAuthorizeDoorId=%d"%(level['PIN'],level['leveltimeseg'],level['tAuthorizeDoorId']))
                if len(line_tuple) == 1000:
                    line = ''.join(line_tuple).replace("\r\n","",1)
                    CMD="DATA UPDATE userauthorize %s"%(line)
                    self.appendcmd(CMD, Op)
                    line = ""
                    line_tuple = []
            line = ''.join(line_tuple).replace("\r\n","",1)
            if len(line)>0:
                CMD="DATA UPDATE userauthorize %s"%(line)
                self.appendcmd(CMD, Op)

        elif (table.upper() == "HOLIDAY"):
            line=decode_holiday(objectset)
            if len(line)>0:
                CMD="DATA UPDATE holiday %s"%(line)
                self.appendcmd(CMD, Op)
        elif (table.upper() == "TIMEZONE"):
            #print "settime", objectset
            line=decode_timeseg(objectset)
            if len(line)>0:
                CMD="DATA UPDATE timezone %s"%(line)
                self.appendcmd(CMD, Op)
        elif (table.upper() == "FIRSTCARD"):
            line=""
            line_tuple = []
            for fo in objectset:
                if fo.door.device.id==self.id:
                    for emp in fo.emp.all():
                        line_tuple.append("\r\nDoorID=%d\tTimezoneID=%d\tPin=%s"%(fo.door.door_no,fo.timeseg.id,emp.PIN))
                        if len(line_tuple) == 10000:
                            line = ''.join(line_tuple).replace("\r\n","",1)
                            CMD="DATA UPDATE firstcard %s"%(line)
                            self.appendcmd(CMD, Op)
                            line = ""
                            line_tuple = []
            line = ''.join(line_tuple).replace("\r\n","",1)
            if len(line)>0:
                CMD="DATA UPDATE firstcard %s"%(line)
                self.appendcmd(CMD, Op)

        elif (table.upper() == "MULTIMCARD"):
            line=""
            line_tuple = []
            for moreopen in objectset:
                gc=[]
                for groupcard in moreopen.accmorecardgroup_set.all():
                    for num in range(groupcard.opener_number):
                            gc.append(groupcard.group.id)
                while len(gc)<5:
                    gc.append(0)
                line_tuple.append("\r\nIndex=%d\tDoorId=%d\tGroup1=%d\tGroup2=%d\tGroup3=%d\tGroup4=%d\tGroup5=%d"%(moreopen.id,moreopen.door.door_no,gc[0],gc[1],gc[2],gc[3],gc[4]))
                if len(line_tuple) == 10000:
                    line = ''.join(line_tuple).replace("\r\n","",1)
                    CMD="DATA UPDATE multimcard %s"%(line)
                    self.appendcmd(CMD, Op)
                    line = ""
                    line_tuple = []

            line = ''.join(line_tuple).replace("\r\n","",1)
            if len(line)>0:
                CMD="DATA UPDATE multimcard %s"%line
                self.appendcmd(CMD, Op)
        elif (table.upper() == "INOUTFUN"):
            line=""
            line_tuple = []
            for define in objectset:
                if define.out_address_hide:
                    line_tuple.append("\r\nIndex=%d\tEventType=%d\tInAddr=%d\tOutType=%d\tOutAddr=%d\tOutTime=%d"%(define.id,define.trigger_opt,define.in_address_hide, define.out_type_hide, define.out_address_hide, define.get_action_type()))
                    if len(line_tuple) == 10000:
                        line = ''.join(line_tuple).replace("\r\n","",1)
                        CMD="DATA UPDATE inoutfun %s"%(line)
                        self.appendcmd(CMD, Op)
                        line = ""
                        line_tuple = []
            line = ''.join(line_tuple).replace("\r\n","",1)
            if len(line)>0:
                CMD="DATA UPDATE inoutfun %s"%line
                self.appendcmd(CMD, Op)
        else:
            pass


    def get_data(self, table, data, filter, Op, immediate=True, timeout=30):
        CMD="DATA QUERY %s %s %s"%(table.lower(), data, filter)
        #self.appendcmd(CMD, Op)
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)

    def delete_data(self, table, filter, Op=None,immediate=False, timeout=0):
        CMD="DATA DELETE %s %s"%(table.lower(), filter)
        self.appendcmd(CMD, Op)

    #如远程开关门
    def set_device_state(self, door, index, state, Op, immediate=False, timeout=0):    #输入输出为紧急命令
        CMD="DEVICE SET %d %d %d"%(door, index, state)
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)

    #取消报警（准备某个控制器）
    def cancel_alarm(self):
        CMD = "CANCEL ALARM"
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)

    #控制门的常开状态no--normal open
    def control_door_no(self, door, state, Op, immediate=False, timeout=0):    #输入输出为紧急命令
        CMD = "CONTROL NO %d %d" % (door, state)
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)

    def get_device_state(self, door, index, Op, immediate=True, timeout=30):
        CMD="DEVICE GET %d %d"%(door, index)
        self.appendcmd(CMD)

    def set_options(self, items, Op=None, immediate=False, timeout=0):
        CMD="SET OPTION %s"%items
        self.appendcmd(CMD, Op)

    def get_optins(self, items, Op=None, immediate=True, timeout=30):
        CMD="OPTION GET %s"%items
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
    
#====================================IC消费===========================================
    def delete_pos_device_info(self,datalist,op,tablename):
        line_tuple = []
        if tablename.upper() == "STOREINFO":
            for obj in datalist:
                line = ("StoreNo=%s\n"%(obj.code))
                CMD="DELETE %s %s"%(tablename,line)
                self.appendcmd(CMD, op)
        elif tablename.upper() == "MEALTYPE":
            for obj in datalist:
                line = ("Mlid=%s\n"%(obj.code))
                CMD="DELETE %s %s"%(tablename,line)
                self.appendcmd(CMD, op)
        elif tablename.upper() == "TIMESEG":
            for obj in datalist:
                line = ("SegID=%s\tTsID=%s\tStart=%s\tEnd=%s\n"%(obj.code,obj.pos_time,obj.starttime.strftime("%H:%M").replace(':',''),obj.endtime.strftime("%H:%M").replace(':','')))
                CMD="DELETE %s %s"%(tablename,line)
                self.appendcmd(CMD, op)
        elif tablename.upper() == "PRESSKEY":
           for obj in datalist:
               line = ("KeyID=%s\n"%(obj.code))
               CMD="DELETE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        elif tablename.upper() == "CARDTYPE":
            from mysite.personnel.models.model_iccard import ICcard,get_device_code,get_meal_code
            for obj in datalist:
                line =("SortID=%s\n"%(obj.code))
                CMD="DELETE %s %s"%(tablename,line)
                self.appendcmd(CMD, op)
        elif tablename.upper() == "USERINFO":
            from mysite.personnel.models.model_iccard import ICcard,get_device_code,get_meal_code
            from mysite.personnel.models.model_emp import Employee,getuserinfo
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,PRIVAGE_CARD,OPERATE_CARD
            for obj in datalist:
               if obj.card_privage in [PRIVAGE_CARD,OPERATE_CARD]:
                    line = ("SysID=%s\tUserID=%s\tCardNo=%s\tPassWord=%s\tPrivage=%s\n"%(obj.sys_card_no,obj.sys_card_no,obj.sys_card_no,obj.Password,obj.card_privage))
               elif obj.cardstatus == CARD_VALID:#解除黑名单
                    line=("SysID=%s\tUserID=%s\tPIN=%s\tCardNo=%s\tName=%s\tPassWord=%s\tUserType=%s\tPrivage=%s\n"%(obj.sys_card_no,obj.sys_card_no,getuserinfo(obj.UserID_id,"PIN"),obj.sys_card_no,getuserinfo(obj.UserID_id,"EName"),obj.Password,1,0))
               else:#删除黑白名单（退卡）
                    line = ("SysID=%s\n"%(obj.sys_card_no))
               CMD="DELETE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        
        elif tablename.upper() == "FIXED":
            for obj in datalist:
               line =("TsID=%s\tStart=%s\tEnd=%s\tPrice=%s\n"%(obj.code,obj.starttime.strftime("%H:%M").replace(':',''),obj.endtime.strftime("%H:%M").replace(':',''),int(obj.fixedmonery*100)))
               CMD="DELETE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        
    def set_pos_device_info(self,datalist,op,tablename):
        line_tuple = []
        if tablename.upper() == "MEALTYPE":
            for obj in datalist:
                line = ("Mlid=%s\tName=%s\tStart=%s\tEnd=%s\n"%(obj.code,obj.name,obj.starttime.strftime("%H:%M").replace(':',''),obj.endtime.strftime("%H:%M").replace(':','')))
                CMD="UPDATE %s %s"%(tablename,line)
                self.appendcmd(CMD, op)
        elif tablename.upper() == "TIMESEG":
            for obj in datalist:
                line = ("SegID=%s\tTsID=%s\tStart=%s\tEnd=%s\n"%(obj.code,obj.pos_time,obj.starttime.strftime("%H:%M").replace(':',''),obj.endtime.strftime("%H:%M").replace(':','')))
                CMD="UPDATE %s %s"%(tablename,line)
                self.appendcmd(CMD, op)
        elif tablename.upper() == "STOREINFO":
            for obj in datalist:
               line =("StoreNo=%s\tName=%s\tPrice=%s\tagio=%s\n"%(obj.code,obj.name,obj.money*100,obj.rebate,))
               CMD="UPDATE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        elif tablename.upper() == "PRESSKEY":
            for obj in datalist:
               line=("KeyID=%s\tPrice=%s\n"%(obj.code,int(obj.money*100)))
               CMD="UPDATE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        elif tablename.upper() == "FIXED":
            for obj in datalist:
               line=("TsID=%s\tStart=%s\tEnd=%s\tPrice=%s\n"%(obj.code,obj.starttime.strftime("%H:%M").replace(':',''),obj.endtime.strftime("%H:%M").replace(':',''),int(obj.fixedmonery*100)))
               CMD="UPDATE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        elif tablename.upper() == "SUBSIDYLOG":
            for obj in datalist:
               allowdata = ((obj.valid_date.year-2000)*12+obj.valid_date.month)*31+obj.valid_date.day
               line=("SysID=%s\tCardNo=%s\tBatch=%s\tMoney=%s\tallowDate=%s"%(obj.sys_card_no,obj.sys_card_no,obj.batch,int(obj.money*100),allowdata))
               CMD="UPDATE %s %s"%(tablename,line)
               self.appendcmd(CMD, op)
        elif tablename.upper() == "CARDTYPE":
            from mysite.personnel.models.model_iccard import ICcard,get_device_code,get_meal_code
            for obj in datalist:
                meal = 0 #可用餐别
                enable = 1 #设备是否可用
                use_device =[a.sn for a in get_device_code(obj)] or 0#卡类可用设备
                if use_device and self.sn in use_device:
                    posmeal = [a.code for a in get_meal_code(obj)] or 0#卡类可用餐别
                    if posmeal:
                        for i in posmeal:
                            meal+=(1<<(int(i)-1))
                    batchtime = obj.pos_time or 0   
                    line=("SortID=%s\tName=%s\trebate=%s\tTimemaxmoney=%s\tDaymaxmoney=%s\tMealmaxmoney=%s\tDaymaxtimes=%s\tMealmaxtimes=%s\tLowlimit=%s\t Maxlimit=%s\tMealType=%s\tEnable=%s\tlimit=%s\tBatchNo=%s\tUseFinger=%s\n"%(obj.code,obj.name,obj.discount,obj.per_max_money,obj.date_max_money,obj.meal_max_money,obj.date_max_count,obj.meal_max_count,obj.less_money,obj.max_money,meal,enable,obj.use_date,batchtime,obj.use_fingerprint))
                    CMD="UPDATE %s %s"%(tablename,line)
                    self.appendcmd(CMD, op)
                else:
                   line =("SortID=%s\n"%(obj.code))
                   CMD="DELETE %s %s"%(tablename,line)
                   self.appendcmd(CMD, op)
        elif tablename.upper() == "USERINFO":
            from mysite.personnel.models.model_iccard import ICcard,get_device_code,get_meal_code
            from mysite.personnel.models.model_emp import Employee,getuserinfo
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_LOST,CARD_STOP,PRIVAGE_CARD,OPERATE_CARD,CARD_INVALID
            from mysite.pos.models.model_cardmanage import CardManage
            from base.cached_model import STATUS_INVALID
            for obj in datalist:
               line=""
               if obj.status <>STATUS_INVALID and obj.card_privage in [PRIVAGE_CARD,OPERATE_CARD]:#管理卡
                    obj_manage = CardManage.objects.get(sys_card_no = obj.sys_card_no)
                    if obj_manage.dining == self.dining:
                        line = ("SysID=%s\tUserID=%s\tCardNo=%s\tPassWord=%s\tPrivage=%s\n"%(obj.sys_card_no,obj.sys_card_no,obj.sys_card_no,obj.Password,obj.card_privage))
               elif obj.status <>STATUS_INVALID and obj.cardstatus == CARD_VALID:#白名单
                    line=("SysID=%s\tUserID=%s\tPIN=%s\tCardNo=%s\tName=%s\tPassWord=%s\tUserType=%s\tPrivage=%s\n"%(obj.sys_card_no,obj.sys_card_no,getuserinfo(obj.UserID_id,"PIN"),obj.sys_card_no,getuserinfo(obj.UserID_id,"EName"),obj.Password,0,0))
               elif obj.cardstatus in [CARD_LOST,CARD_STOP,CARD_INVALID]: #黑名单
                    line=("SysID=%s\tUserID=%s\tPIN=%s\tCardNo=%s\tName=%s\tPassWord=%s\tUserType=%s\tPrivage=%s\n"%(obj.sys_card_no,obj.sys_card_no,getuserinfo(obj.UserID_id,"PIN"),obj.sys_card_no,getuserinfo(obj.UserID_id,"EName"),obj.Password,1,0))
               if len(line)>0:
                   CMD="UPDATE %s %s"%(tablename,line)
                   self.appendcmd(CMD, op)
        elif tablename.upper() == "POSPARAM":
            from mysite.pos.models.model_posparam import PosParam
            from base.crypt import encryption,decryption
            from mysite.pos.pos_utils import enc
            obj_param = PosParam.objects.all()[0]
            CMD = "SET OPTION UseSection=%s\tBackSection=%s\tCardPass=%s\t\n" % (obj_param.main_fan_area,obj_param.minor_fan_area,enc(decryption(obj_param.system_pwd)))
            self.appendcmd(CMD, op)
        
        elif tablename.upper() == "CARDMANAGE":#同步消费管理卡
            from mysite.pos.models.model_cardmanage import CardManage
            obj_manage = CardManage.objects.filter(dining = self.dining,cardstatus = '1')#同步有效管理卡到设备
            for obj in obj_manage:
                line = ("SysID=%s\tUserID=%s\tCardNo=%s\tPassWord=%s\tPrivage=%s\n"%(obj.sys_card_no,obj.sys_card_no,obj.sys_card_no,obj.pass_word,obj.card_privage))
                if len(line)>0:
                    CMD="UPDATE %s %s"%("USERINFO",line)
                    self.appendcmd(CMD, op)
            
        
        
     

    def set_pos_device_option(self):
        from mysite.iclock.dataprocaction import appendDevCmdReturn
        CMD = "SET OPTION CardWitdh=8\tMachineType=%s\tOperatorcard=%s\tWhiteList=%s\t" % (self.device_use_type,int(self.is_check_operate),int(self.check_white_list))
        if self.device_use_type == 0:#消费机
            if self.consume_model == 1:#定值模式
                if self.dz_money is None:
                    CMD+="Consmod=%s\tTimeSegMod=1\tConsKeap=%s\t\n" % (self.consume_model,int(self.is_cons_keap))
                else:
                    CMD+="Consmod=%s\tFixMoney=%s\tTimeSegMod=0\tConsKeap=%s\t\n" % (self.consume_model,int(self.dz_money*100),int(self.is_cons_keap))
            elif self.consume_model == 6: #计时模式
                CMD+="Consmod=%s\tGetIntmod=%s\tHourPrice=%s\tConsKeap=%s\t\n"%(self.consume_model,self.long_time,int(self.time_price*100),int(self.is_cons_keap)) 
            else:
                CMD+="Consmod=%s\tConsKeap=%s\t\n" % (self.consume_model,int(self.is_cons_keap))
        elif self.device_use_type == 2:#补贴机
            CMD+="AllowUseOK=%s\tAddAllow=%s\tZeroAllow=%s\t\n" % (int(self.is_OK),int(self.is_add),int(self.is_zeor))
        elif self.device_use_type == 1:#出纳机
            if self.cash_model == 1:# 出纳金额模式
                CMD+="FullValueMod=%s\tFullType=%s\tFavourable=%s\tCardMaxMoney=%s\t\n" % (self.cash_model,self.cash_type,self.favorable,self.card_max_money)
            else:
                CMD+="FullValueMod=%s\tFullFixVaule=%s\tFullType=%s\tFavourable=%s\tCardMaxMoney=%s\t\n" % (self.cash_model,int(self.dz_money*100),self.cash_type,self.favorable,self.card_max_money)
        #return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)#appendcmdreturn
        return appendDevCmdReturn(self,CMD)

    def connect(self, save=True, immediate=True, timeout=30):
        from mysite.iaccess.devcomm import TDevComm
        from mysite.iaccess.models.accdoor import AccDevice
        devcom = TDevComm(self.getcomminfo())
        #print self.getcomminfo()
        cret = devcom.connect()
        #print "----device----connect-----cret=",cret
        if cret["result"] > 0:
            #连接成功取设备参数，序列号写入设备表，其他参数写入accdevice表
            qret = devcom.get_options("~SerialNumber,FirmVer,~DeviceName,LockCount,ReaderCount,AuxInCount,AuxOutCount,MachineType,~IsOnlyRFMachine,MThreshold,~ZKFPVersion")#SerialNumber,
            if qret["result"] > 0:
                try:
                    datdic = {}
                    optlist = qret["data"].split(',')
                    for opt in optlist:
                        opt1=opt.split('=')
                        datdic[opt1[0]] = opt1[1] or None
                    #print "dic=",datdic
                    #print "self=",self
                    #self._accdevice_cache.save()
                    #print "self.accdevice=",self.accdevice

                    #print save
                    #print self.accdevice.door_count
                    if save and not self.accdevice.door_count:#搜索控制器后手动添加设备时，Device->AccDevice两表会先后保存，故此处的判断可以保证不重复添加
                        #print self.acpanel_type
                        #print datdic['LockCount']
                        if self.acpanel_type == int(datdic['LockCount']):
                            self.sn = datdic['~SerialNumber']
                            self.Fpversion = datdic['~ZKFPVersion']
                            self.fw_version = datdic['FirmVer']
                            self.device_name = datdic['~DeviceName']
                            #新增获取三个容量参数--add by darcy 20101122
                            self.max_user_count = datdic.has_key("~MaxUserCount") and int(datdic["~MaxUserCount"])*100 or 0
                            self.max_attlog_count = datdic.has_key("~MaxAttLogCount") and int(datdic["~MaxAttLogCount"])*10000 or 0
                            self.max_finger_count = datdic.has_key("~MaxUserFingerCount") and int(datdic["~MaxUserFingerCount"]) or 0
                            self.fp_mthreshold = datdic.has_key("MThreshold") and int(datdic["MThreshold"]) or 0

                            self.save(force_update=True)
                            #print '---Device has been updated,SN FWVersion.....'

                            #self.accdevice.machine_type = int(datdic['ACPanelFunOn'])
                            self.accdevice.door_count = int(datdic['LockCount'])
                            self.accdevice.reader_count = int(datdic['ReaderCount'])
                            self.accdevice.aux_in_count = int(datdic['AuxInCount'])
                 
                            self.accdevice.aux_out_count = int(datdic['AuxOutCount'])
                            self.accdevice.machine_type = int(datdic['MachineType'])
                            self.accdevice.IsOnlyRFMachine = int(datdic['~IsOnlyRFMachine'])

                            self.accdevice.save(force_update=True)
                            #print '---AccDevice has been updated,LockCount AuxInCount AuxOutCount....'
                        else:
                            try:
                                d_server = start_dict_server()
                                #acmd = DevCmd(SN=self, CmdContent="DOOR_DIFFER", CmdReturn=0)
                                #q_server.set_to_dict(devs[devobj.id].comm_tmp, pickle.dumps(acmd))
                                d_server.set_to_dict(devs[devobj.id].comm_tmp, {'SN': self, 'CmdContent': "DOOR_DIFFER", 'CmdReturn': 0})
                                d_server.close()
                            except:
                                print_exc()
                except:
                    print_exc()
            return {"result":qret["result"], "data":datdic}
        return {"result":cret["result"], "data":""}


    def set_report_user(self, empobjs, Op, session_key=""):    #挂失
        self.report_user("user", empobjs, Op, session_key)

    def set_user(self, empobjs, Op, session_key=""):    #同步设备员工信息
        self.set_data("user", empobjs, Op, session_key)

    def set_acc_user_fingerprint(self, empobjs, Op):
        from mysite.iclock.models.model_bio import Template
        if self.accdevice.IsOnlyRFMachine>0: #不支持指纹
            return
        else:
#            u = [int(user.id) for user in empobjs]
#            temps = Template.objects.filter(UserID__in=u).filter(Fpversion=10)
            if empobjs :
                batch_lens = 900
                lens = len(empobjs)
                times = lens%batch_lens == 0 and lens/batch_lens or (lens/batch_lens + 1)
                for i in range(times):
                    es = empobjs[i*batch_lens:(i+1)*batch_lens]
                    u = [user.PIN for user in es]
                    temps = Template.objects.filter(UserID__in=u).filter(Fpversion=10)
                    self.set_data("templatev10", temps, Op)

    def set_user_fingerprint(self, empobjs, Op,FID=""):    #同步设备员工指纹
        from mysite.iclock.models.model_bio import Template
        if self.device_type==1:
            for user in empobjs:
                if len(str(FID).strip())>0:
                    temp=Template.objects.get(UserID=user.PIN,FingerID=int(FID),Fpversion=self.Fpversion)
                    temp=[temp]
                else:
                    temp=Template.objects.filter(UserID=user.PIN).filter(Fpversion=self.Fpversion)
                if len(temp)>0:
                    self.set_data("fingerprint", temp, Op)

    def set_user_face(self,empobjs,Op,FID=""): #---------------------同步人脸信息 FID 人脸编号
        '''
        下发人脸模板   FID 人脸编号
        '''
        from model_face import FaceTemplate
        if self.device_type==1:#---考勤机
            for user in empobjs:
                from mysite.personnel.models.emp_extend import send_dev_face
                send_dev_face(user,self)
#                if len(str(FID).strip())>0:
#                    face=FaceTemplate.objects.filter(user=user.id,faceid=int(FID))
#                else:
#                    face=FaceTemplate.objects.filter(user=user.id)  #----获取人员的人脸
#                if len(face)>0:
#                    if self.face_tmp_count == len(face) and self.face_ver == face.face_ver and dv.push_status[0]=='1' and dv.push_status[2]=='1':
#                        self.set_data("facetemplate", face, Op)  #---调用公共的数据处理方法
    

    def set_user_privilege(self, empobjs, Op, session_key=""):    #同步设备员工门禁权限
        from mysite.personnel.models import Employee
        from mysite.iaccess.models import AccLevelSet
        if empobjs is None:
            empobjs = Employee.objects.all()

#        if 'sqlserver' in str(type(connection)).lower():
#            sql ='''SELECT DISTINCT R4.badgenumber AS PIN,R2.level_timeseg_id,\
#               (select sum(power(2,door_no - 1)) from \
#                   (select L.acclevelset_id as La,NL.acclevelset_id,NR1.door_no \
#                       from acc_levelset_door_group as NL \
#                       INNER JOIN acc_levelset_emp as NR on NL.acclevelset_id=NR.acclevelset_id \
#                       LEFT JOIN acc_door as NR1 on NR1.id=NL.accdoor_id \
#                       where NL.acclevelset_id=L.acclevelset_id and NR.employee_id=R3.employee_id and NR1.device_id = R1.device_id \
#                   ) as NRz group by La \
#               ) as lev \
#               FROM acc_levelset_door_group AS L \
#               LEFT JOIN acc_door AS R1 ON R1.id=L.accdoor_id \
#               LEFT JOIN acc_levelset AS R2 ON R2.id = L.acclevelset_id \
#               LEFT JOIN acc_levelset_emp AS R3 ON R3.acclevelset_id = L.acclevelset_id \
#               LEFT JOIN userinfo AS R4 ON R4.userid = R3.employee_id \
#               WHERE R1.device_id=%s AND R3.employee_id in %s \
#               group by \
#               L.acclevelset_id,R1.device_id,R2.level_timeseg_id,R3.employee_id,R4.badgenumber '''
#
#        else:  #数据库为oracle或mysql时
#            sql = '''SELECT DISTINCT R4.badgenumber AS PIN,R2.level_timeseg_id,\
#               (SELECT SUM(POWER(2,NR1.door_no - 1)) \
#                       FROM acc_levelset_door_group NL \
#                       INNER JOIN acc_levelset_emp NR ON NL.acclevelset_id=NR.acclevelset_id \
#                       LEFT JOIN acc_door NR1 ON NR1.id=NL.accdoor_id \
#                       WHERE NL.acclevelset_id=L.acclevelset_id and NR.employee_id=R3.employee_id AND NR1.device_id=R1.device_id \
#               ) AS lev \
#               FROM acc_levelset_door_group L \
#               LEFT JOIN acc_door R1 ON R1.id=L.accdoor_id \
#               LEFT JOIN acc_levelset R2 ON R2.id = L.acclevelset_id \
#               LEFT JOIN acc_levelset_emp R3 ON R3.acclevelset_id = L.acclevelset_id \
#               LEFT JOIN userinfo R4 ON R4.userid = R3.employee_id \
#               WHERE R1.device_id=%s AND R3.employee_id in %s \
#               GROUP BY \
#               L.acclevelset_id,R1.device_id,R2.level_timeseg_id,R3.employee_id,R4.badgenumber '''
#
        emp_num = len(empobjs)
        i = 0
        empid_value = []
        levelline = ""
        each_query_rows = 3000
        import json
        import operator
        from mysite.iaccess import sqls
        emplevel = []
        while i < emp_num:
            #tempsql = sql  #sql查询随着表acc_levelset_emp数据量增加而变慢(lev的计算)
            cursor = connection.cursor()
            empid_value = [r.id for r in empobjs[i:i+each_query_rows]]
            empid_value = json.dumps(empid_value).replace('[','(').replace(']',')').replace('"',"'")
            #tempsql =  sql % (str(self.id),empid_value)
            tempsql=sqls.set_user_privilege_select(str(self.id),empid_value)
            try:
               cursor.execute(tempsql)
            except:
               i += each_query_rows
               continue

            rows = cursor.fetchall()

            for row in rows:
               line={}
               line['PIN']=row[0]
               line['leveltimeseg']=row[1]
               line['tAuthorizeDoorId']=row[2]
               emplevel.append(line.copy())
            i += each_query_rows
        if len(emplevel)>0:
            self.set_data("userauthorize", emplevel, Op)

    def set_timezone(self, Op):     #同步设备所有时间段
        from mysite.iaccess.models import AccTimeSeg
        timezoneobjs=AccTimeSeg.objects.all()
        self.delete_data("timezone", "", Op)
        self.set_data("timezone", timezoneobjs, Op)

    def del_timezone(self, tzid):
        #print "del timezone %d"%tzid
        if tzid>0:
            self.delete_data("timezone", "TimezoneId=%d"%tzid)
        else:
            self.delete_data("timezone", "")

    def set_holiday(self, Op):  #同步设备所有假日
        from mysite.iaccess.models import AccHolidays
        holidayobjs=AccHolidays.objects.all()
        self.delete_data("holiday", "", Op)
        self.set_data("holiday", holidayobjs, Op)

    def set_dooroptions(self, Op, door_set=None):  #同步设备门属性, doorid=0，设备所有门
        from mysite.iaccess.models import AccDoor
        if door_set is None:
            door_set=AccDoor.objects.filter(device=self)
        for d in door_set:
            optstr=""
            if d.door_sensor_status is not None:
                str="Door%dSensorType=%d,"%(d.door_no, d.door_sensor_status)   #门磁类型
            else:
                str="Door%dSensorType=0,"%(d.door_no)
            optstr += str;

            if d.lock_delay is not None:
                str="Door%dDrivertime=%d,"%(d.door_no, d.lock_delay)       #锁延时
            else:
                str="Door%dDrivertime=5,"%(d.door_no)
            optstr += str;

            if d.sensor_delay is not None:
                str="Door%dDetectortime=%d,"%(d.door_no, d.sensor_delay)   #门磁延时
            else:
                str="Door%dDetectortime=15,"%(d.door_no)
            optstr += str;
            
            if d.back_lock is not None:#一定不为空
                str = "Door%dCloseAndLock=%d," % (d.door_no, d.back_lock)#闭门回锁  1 启用，0不启用，默认1
            else:
                str = "Door%dCloseAndLock=0," % d.door_no
            optstr += str;

            if d.opendoor_type is not None:
                str="Door%dVerifyType=%d,"%(d.door_no, d.opendoor_type)      #开门方式
            else:
                str="Door%dVerifyType=6,"%(d.door_no)#仅5.0，字段中default由0改为4之后，此处不会进入-darcy20110317
            optstr += str;

            if d.lock_active is not None:
                str="Door%dValidTZ=%d,"%(d.door_no, d.lock_active.id)   #门激活时区
            else:
                str="Door%dValidTZ=1,"%(d.door_no)
            optstr += str;

            if d.long_open is not None:
                str="Door%dKeepOpenTimeZone=%d,"%(d.door_no, d.long_open.id)   #门常开 时区号
            else:
                str="Door%dKeepOpenTimeZone=0,"%(d.door_no)
            optstr += str;

            if d.wiegand_fmt is not None:
                str="Reader%dWGType=%d,"%(d.door_no, d.wiegand_fmt.id)    #读头wg格式
            else:
                str="Reader%dWGType=0,"%(d.door_no)
            optstr += str;

            if d.card_intervaltime is not None:
                str="Door%dIntertime=%d,"%(d.door_no, d.card_intervaltime)   #双卡间隔
            else:
                str="Door%dIntertime=0,"%(d.door_no)
            optstr += str;

            if d.reader_type is not None:
                str="Door%dReaderType=%d,"%(d.door_no, d.reader_type)   #读头类型
            else:
                str="Door%dReaderType=2,"%(d.door_no)
            optstr += str;

            if d.force_pwd is not None:
                str="Door%dForcePassWord=%s,"%(d.door_no, decryption(d.force_pwd)) #协迫密码
            else:
                str="Door%dForcePassWord=0,"%(d.door_no)
            optstr += str;
        
            #主流固件暂不支持
#            if d.global_apb:#---cwj201108023
#                str="Door%dGAPB=1,"%(d.door_no)   #全局反潜
#            else:
#                str="Door%dGAPB=0,"%(d.door_no)
#            optstr += str;            
            
            if d.supper_pwd is not None:
                str="Door%dSupperPassWord=%s"%(d.door_no, decryption(d.supper_pwd))   #超级密码
            else:
                str="Door%dSupperPassWord=0"%(d.door_no)
            optstr += str;

            #print  "optstr=", optstr
            self.set_options(optstr, Op)

    def set_firstcard(self, Op, mdoor):    #同步设备首卡开门
        from mysite.iaccess.models import AccFirstOpen
        if mdoor:
            self.delete_data("firstcard", "DoorID=%d"%(mdoor.door_no), Op)
            firstopen=AccFirstOpen.objects.filter(door=mdoor)
            if firstopen:
                self.set_data("firstcard", firstopen, Op)
                optstr="Door%dFirstCardOpenDoor=1"%mdoor.door_no
                self.set_options(optstr, Op)
            else:
                optstr="Door%dFirstCardOpenDoor=0"%mdoor.door_no
                self.set_options(optstr, Op)
    #检测是否启用首卡开门
    def check_firstcard_options(self, mdoor):
        from mysite.iaccess.models import AccFirstOpen
        if mdoor:
            firstopen=AccFirstOpen.objects.filter(door=mdoor)
            if firstopen:
                optstr="Door%dFirstCardOpenDoor=1"%mdoor.door_no
            else:
                optstr="Door%dFirstCardOpenDoor=0"%mdoor.door_no
            self.set_options(optstr, None)

    def delete_firstcard(self, Op, mdoor):
        from mysite.iaccess.models import AccFirstOpen
        if mdoor:
            self.delete_data("firstcard", "DoorID=%d"%(mdoor.door_no), Op)
        else:
            self.delete_data("firstcard", "", Op)
        self.check_firstcard_options(mdoor)

    def del_multicard(self, Op, morecard):
        if morecard:
            filter = "Index=%d\r\n"%morecard.id
            self.delete_data("multimcard", filter, Op)
            #self.delete_data("multimcard", "DoorId=%d"%(mdoor.door_no), Op)
        else:
            self.delete_data("multimcard", "", Op)
        self.check_muliticard_options(morecard.door)

    def set_multicard(self, Op, mdoor):    #同步设备多卡开门
        from mysite.iaccess.models import AccMoreCardSet
        from mysite.personnel.models import Employee
        from mysite.iaccess import sqls
        #filter="DoorId=%d"%mdoor.door_no
        morecard = AccMoreCardSet.objects.filter(door=mdoor)

        if morecard:
            filter = ""
            for mcard in morecard:
                filter = filter+"Index=%d\r\n"%mcard.id
            self.delete_data("multimcard", filter, Op)

            self.set_data("multimcard", morecard, Op)
            optstr="Door%dMultiCardOpenDoor=1"%mdoor.door_no
            self.set_options(optstr, Op)
            sql=sqls.set_multicard_select(mdoor.id)
            #sql="select userid from userinfo where morecard_group_id in (select group_id from acc_morecardgroup where comb_id in (select id from acc_morecardset where door_id=%d))"%mdoor.id
            #print "set_multicard sql=", sql
            cursor = connection.cursor()
            cursor.execute(sql)
            fet=set(cursor.fetchall())
            emp=[]
            ss=[emp.append(int(f[0])) for f in fet]
            #print emp
            empset=Employee.objects.filter(id__in=emp)
            if len(empset):
                self.set_user(empset, Op)
        else:
            optstr="Door%dMultiCardOpenDoor=0"%mdoor.door_no
            self.set_options(optstr, Op)
    #检测是否启用多卡开门
    def check_muliticard_options(self, mdoor):
        from mysite.iaccess.models import AccMoreCardSet
        if mdoor:
            morecard=AccMoreCardSet.objects.filter(door=mdoor)
            if morecard:
                optstr="Door%dMultiCardOpenDoor=1"%mdoor.door_no
            else:
                optstr="Door%dMultiCardOpenDoor=0"%mdoor.door_no
            self.set_options(optstr, None)

    def set_antipassback(self, Op): #同步设备反潜信息
        anti=0
        if self.accantiback_set.all():
            antibackobj=self.accantiback_set.all()[0]
            anti=antibackobj.getantibackoption()
        optstr="AntiPassback=%d"%anti
        self.set_options(optstr, Op)

    def clear_antipassback(self, Op):
        self.set_options("AntiPassback=0", Op)

    def set_interlock(self, Op): #同步设备互锁信息
        IntLock=0
        if self.accinterlock_set.all():
            interlock=self.accinterlock_set.all()[0]
            IntLock=interlock.getlockoption()
        optstr="InterLock=%d"%IntLock
        self.set_options(optstr, Op)

    def clear_interlock(self, Op):
        self.set_options("InterLock=0", Op)

    def delete_user_privilege(self, empobjs, Op, session_key=""): #删除员工门禁权限
        if self.device_type == DEVICE_ACCESS_CONTROL_PANEL:     #门禁机
            if empobjs == '*':#同步所有数据时需要删除所有权限。
                self.delete_data("userauthorize", "", Op)
            elif empobjs:
                filter = ""
                for emp in empobjs:
                    filter += ("\r\n" if filter else "") + "Pin=%s"%emp.PIN
                self.delete_data("userauthorize", filter, Op)
            else:
                pass#如果权限里并没有人员，不能下删除权限的命令，避免误将设备中权限表删除。-darcy20110428


    def delete_user(self, empobjs, Op):
        """
        删除员工信息,包括指纹信息,
        #判断是否有首卡权限及多卡权限，如果有包括删除首卡权限，多卡权限
        """
        from mysite.personnel.models.model_emp import device_pin
        if self.comm_type==COMMU_MODE_PUSH_HTTP:
            for emp in empobjs:
                if (self.device_type != 2) or ((self.device_type==2) and (self.accdevice.IsOnlyRFMachine==0)):
                    self.delete_data("fingerprint", "Pin=%s"%device_pin(emp.PIN), Op)
                self.delete_data("user", "Pin=%s"%device_pin(emp.PIN), Op)
        else:
            filter = ""
            #filter_templatev10 = ""
            for emp in empobjs:
                filter += ("\r\n" if filter else "") + "Pin=%s"%emp.PIN
                #filter_templatev10 += ("\r\n" if filter_templatev10 else "") + "PIN=%s"%emp.PIN#不能写成Pin，固件的兼容性

            if self.device_type==2 and self.accdevice.IsOnlyRFMachine==0:
                #self.delete_data("templatev10", filter_templatev10, Op)#北理工专用--darcy20110331
                self.delete_data("templatev10", filter, Op)

            self.delete_data("user", filter, Op)

    def delete_user_finger(self, table, empfp, Op):
        if self.comm_type==COMMU_MODE_PUSH_HTTP:
            if (self.device_type != 2) or ((self.device_type==2) and (self.accdevice.IsOnlyRFMachine==0)):
                self.delete_data(table, empfp, Op)
        else:
            self.delete_data(table, empfp, Op)

    def upload_acclog(self,new_record=False):
        if new_record:
            CMD="DATA QUERY %s %s %s"%("transaction", "*", "NewRecord")
        else:
            CMD="DATA QUERY %s %s %s"%("transaction", "*", "")

        if self.comm_type == COMMU_MODE_PULL_TCPIP:
            timeout = MAX_COMMAND_TIMEOUT_SECOND*120
        elif self.comm_type == COMMU_MODE_PULL_RS485:
            timeout = MAX_COMMAND_TIMEOUT_SECOND*120*3

        return self.appendcmdreturn(CMD, timeout)
    
    def get_data(self, table, data, filter, Op, immediate=True, timeout=30):
        CMD="DATA QUERY %s %s %s"%(table.lower(), data, filter)
        #self.appendcmd(CMD, Op)
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
    
    #从设备中获取人员信息与指纹数据
    def upload_user_info_template(self, table):
        CMD = "DATA QUERY %s %s %s"%(table.lower(), "*", "")
    
        if self.comm_type == COMMU_MODE_PULL_TCPIP:
            timeout = MAX_COMMAND_TIMEOUT_SECOND*60
        elif self.comm_type == COMMU_MODE_PULL_RS485:
            timeout = MAX_COMMAND_TIMEOUT_SECOND*60*3
    
        return self.appendcmdreturn(CMD, timeout)

    def upload_user_info(self,table):
        CMD = "DATA COUNT %s" % (table)
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)

    def delete_define_io(self, Op, defobj=None):
        if defobj:
            filter="Index=%d"%defobj.id
            self.delete_data("inoutfun", filter, Op)
        else:
            self.delete_data("inoutfun", "", Op)

    def set_define_io(self, Op, defobj=None):
        if defobj:
            self.set_data("inoutfun", [defobj], Op)
        else:
            defobj_set = self.acclinkageio_set.all()
            self.delete_data("inoutfun", "", Op)
            self.set_data("inoutfun", defobj_set, Op)

    #删除人员权限后，当该人员对当前设备的任一门都没有权限时，则把该人员从设备中删除
    def delete_emp_bylevel(self, empset):
        empset_ids_str = "("
        for e in empset:
            empset_ids_str += str(e.id)
            empset_ids_str += ","
        empset_ids_str = empset_ids_str[0:-1] + ")"
        cursor = connection.cursor()
        #当前设备中的所有权限组都不包含该人员时，则把该人员从设备中删除
#        sql = '''select distinct userinfo.userid from userinfo \
#               where userinfo.userid in %s \
#                     and userinfo.userid not in ( \
#               select acc_levelset_emp.employee_id from acc_levelset_emp \
#               where acc_levelset_emp.acclevelset_id in ( \
#               select acc_levelset_door_group.acclevelset_id from acc_levelset_door_group  \
#               where acc_levelset_door_group.accdoor_id  in( \
#               select acc_door.id from acc_door \
#               where acc_door.device_id= %s)))'''%(empset_ids_str, self.id)

        from mysite.iaccess import sqls
        #sql = sql.decode('latin1')
        sql=sqls.delete_emp_bylevel_select(empset_ids_str, self.id)
        cursor.execute(sql)
        empset_id_dev = cursor.fetchall()
        connection.close()
        empset_id_deleting = [] #=[emp[0] for emp in empset_id_dev]
        for emp in empset_id_dev:
            empset_id_deleting.append(emp[0])
        if empset_id_deleting:
            #print "###########deleting",empset_id_deleting,self.id
            from mysite.personnel.models import Employee
            empset_deleting = Employee.objects.filter(id__in = empset_id_deleting)
            from dev_comm_operate import save_operate_cmd
            Op = save_operate_cmd("DATA DELETE user")
            self.delete_user(empset_deleting, Op)


    def delete_transaction(self, Op=None):
        self.delete_data("transaction", "", Op)

    #设备替换,设备区域变更手动更新设备后
    def delete_all_data(self, Op=None):        #清除所有数据
        self.appendcmd("CLEAR DATA",Op)
        #if (self.device_type == DEVICE_TIME_RECORDER) or ((self.device_type==DEVICE_ACCESS_CONTROL_PANEL) and (self.accdevice.IsOnlyRFMachine==0)):

        if (self.device_type==DEVICE_ACCESS_CONTROL_PANEL):
            if self.accdevice.IsOnlyRFMachine == 0:
                self.delete_data("templatev10", "", Op)#清空门禁指纹
            self.delete_data("user", "", Op)
            self.delete_data("userauthorize", "", Op)
    
    def set_all_pos_data(self, Op=None):#同步所有数据到消费机
        from mysite.iclock.models.dev_comm_operate import update_pos_device_info
        from mysite.pos.pos_utils import get_cache_issuecard,get_cache_loseunitecard,get_cache_meal,get_cache_merchandise,get_cache_keyvalue,get_cache_splittime,get_cache_iccard,get_cache_batchtime
        mealobj = get_cache_meal()
        merchandise = get_cache_merchandise()
        keyvalue = get_cache_keyvalue(self)
        splittime = get_cache_splittime(self)
        batchtime= get_cache_batchtime()
        iccard = get_cache_iccard()
#        lose_card_list = get_cache_loseunitecard()# 挂失卡
        all_card_list = get_cache_issuecard()# 所有卡
        self.appendcmd("CLEAR DATA")
        update_pos_device_info([self],mealobj,"MEALTYPE")
        update_pos_device_info([self],merchandise,"STOREINFO")
        update_pos_device_info([self],keyvalue,"PRESSKEY")
        update_pos_device_info([self],batchtime,"TIMESEG")#批次时间段表
        update_pos_device_info([self],splittime,"FIXED")#分段定值表
        update_pos_device_info([self],iccard,"CARDTYPE")#卡类资料
#        update_pos_device_info([self],lose_card_list,"USERINFO")
        update_pos_device_info([self],all_card_list,"USERINFO")
        update_pos_device_info([self],None,"POSPARAM")
        
    def set_all_data(self, Op=None):       #同步所有数据
        if (self.device_type == DEVICE_ACCESS_CONTROL_PANEL):#门禁控制器
            empobjs=self.search_accuser_bydevice()
            self.delete_all_data()  #同步所有数据，先清除控制器数据
            if empobjs:
                self.set_user(empobjs, Op)
                if (self.accdevice.IsOnlyRFMachine==0):
                    self.set_acc_user_fingerprint(empobjs, Op)
                self.set_user_privilege(empobjs, Op)
            self.set_timezone(Op)
            self.set_holiday(Op)
            self.set_dooroptions(Op)
            for door in self.accdoor_set.all():
                self.set_firstcard(Op, door)
                self.set_multicard(Op, door)
            self.set_define_io(Op)
            self.set_antipassback(Op)
            self.set_interlock(Op)
        elif (self.device_type == DEVICE_VIDEO_SERVER):
            raise Exception (_(u"硬盘录像机不支持该操作！"))
        elif (self.device_type == DEVICE_CAMERA_SERVER):
            raise Exception (_(u"网络摄像机不支持该操作！"))
        else:#考勤
            empobjs=self.search_user_bydevice()
            self.set_user(empobjs, Op)
            self.set_user_fingerprint(empobjs, Op)
            self.set_user_face(empobjs, Op)
    #输入输出控制
    def set_output (self, doorid, addr, state):
        return self.set_device_state(doorid,addr,state)

    def get_input(self, doorid, addr):
        return self.get_device_state(doorid,addr)

    def set_ipaddress(self, newip, gateway, subnet_mask, timeout):
        CMD="SET OPTION IPAddress=%s,GATEIPAddress=%s,NetMask=%s" % (newip, gateway, subnet_mask)    #修改设备ip地址
        return self.appendcmdreturn(CMD, timeout)

    def set_time(self, ret=True):
        from mysite.iclock.dataprocaction import appendDevCmdReturn
        dt=encodetime()
        CMD="SET OPTION DateTime=%d"%(dt)   #同步控制器时间
        if ret:
            return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
        else:
            return appendDevCmdReturn(self, CMD)

    def set_commkey(self, new_commkey):
        CMD = "SET OPTION ComPwd=%s" % new_commkey#ComPwd为设备通讯密码，非串口密码
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)

    def set_dstime(self,dstime, immediately=True):#immediately  为True时只执行一次，失败就直接返回，为False时失败后会在设备下次连接上之后继续执行
        CMD = ""
        if dstime.mode == 0:
            time_st = dstime.start_time
            time_ed = dstime.end_time
            time_st = time_st.split(" ")
            time_st_mon = int(time_st[0].split("-")[0])
            time_st_d = time_st[0].split("-")[1]
            time_st_h = time_st[1].split(":")[0]
            time_st_mun = time_st[1].split(":")[1]
            time_st = ((int(time_st_mon)&0xFF) << 24)|((int(time_st_d)&0xFF)<<16)|((int(time_st_h)&0xFF)<<8)|(int(time_st_mun)&0xFF)

            time_ed = time_ed.split(" ")
            time_ed_mon = time_ed[0].split("-")[0]
            time_ed_d = time_ed[0].split("-")[1]
            time_ed_h = time_ed[1].split(":")[0]
            time_ed_mun = time_ed[1].split(":")[1]
            time_ed = ((int(time_ed_mon)&0xFF) << 24)|((int(time_ed_d)&0xFF)<<16)|((int(time_ed_h)&0xFF)<<8)|(int(time_ed_mun)&0xFF)

            CMD = "SET OPTION ~DSTF=%s,DaylightSavingTimeOn=%s,CurTimeMode=%s,DLSTMode=%s,DaylightSavingTime=%s,StandardTime=%s"%(1, 1, 0, 0, time_st, time_ed)
        else:
            time_st = dstime.start_time
            time_ed = dstime.end_time
            time_st = time_st.split(" ")
            time_st_mon = time_st[0].split("-")[0]
            time_st_w = time_st[0].split("-")[1]
            time_st_d = time_st[0].split("-")[2]
            time_st_h = time_st[1].split(":")[0]
            time_st_mun = time_st[1].split(":")[1]

            time_ed = time_ed.split(" ")
            time_ed_mon = time_ed[0].split("-")[0]
            time_ed_w = time_ed[0].split("-")[1]
            time_ed_d = time_ed[0].split("-")[2]
            time_ed_h = time_ed[1].split(":")[0]
            time_ed_mun = time_ed[1].split(":")[1]

            CMD = "SET OPTION ~DSTF=%s,DaylightSavingTimeOn=%s,CurTimeMode=%s,DLSTMode=%s,WeekOfMonth1=%s,WeekOfMonth2=%s,WeekOfMonth3=%s,WeekOfMonth4=%s,WeekOfMonth5=%s,WeekOfMonth6=%s,WeekOfMonth7=%s,WeekOfMonth8=%s,WeekOfMonth9=%s,WeekOfMonth10=%s"%(1, 1, 0, 1, int(time_st_mon), int(time_st_w), int(time_st_d), int(time_st_h), int(time_st_mun), int(time_ed_mon), int(time_ed_w), int(time_ed_d), int(time_ed_h), int(time_ed_mun))
        if immediately:
            return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
        else:
            return self.appendcmd(CMD)

    def set_dstime_disable(self):
        CMD = "SET OPTION ~DSTF=0,DaylightSavingTimeOn=0,CurTimeMode=0"
        return self.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
    
    
#            用来判断消费设备记录是否已经全部上传成功到服务器
#            消费机：通过比对三个月内的消费数据的最大设备流水号跟最小流水号之间是否有间断的情况
#            出纳机，补贴机：通过获取redis中的标示值来验证

    def pos_dev_status(self):
        if self.device_type == DEVICE_POS_SERVER:
            from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
            from mysite.pos.pos_ic.ic_sync_model import Pos_Device
            from mysite.sql_utils import p_query,p_execute,p_query_one
            if get_option("POS_IC") and self.device_use_type == 0 :#消费机
                sel_sql = """
                        select max_dev_serial,min_dev_serial,pos_count,max_dev_serial - min_dev_serial + 1 as dic_count from 
                        (
                            select max(dev_serial_num) as max_dev_serial,MIN(dev_serial_num) as min_dev_serial,COUNT(1) as pos_count from 
                            (
                                select * from 
                                (
                                    select dev_serial_num from pos_icconsumerlist where dev_sn = '%s' and  dev_serial_num is not null and pos_time> DateAdd(Month,-3,getdate())
                                    union all
                                    select dev_serial_num  from  pos_icerrorlog where dev_sn = '%s' and  dev_serial_num is not null and pos_time> DateAdd(Month,-3,getdate())
                                ) as a group by dev_serial_num
                            )as pos_log  
                        )
                        as device_data_info
                """
                q_list = p_query_one(sel_sql %(self.sn,self.sn))
                if q_list[2] == q_list[3] or q_list[2] == 0:
                    return True
                else:
                    return False
            else:#补贴机，出纳机
                r_device = Pos_Device(self.sn)
                try:
                    pos_device=r_device.get()
                except PosDeviceDoesNotExist:
                   return False
                if pos_device.pos_dev_data_status.lower()=="true":
                    return True
                else:
                    return False
    
    def show_status(self):
        if self.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            key = self.command_temp_list_name()
            d_server = start_dict_server()
            device_status = d_server.get_from_dict(key)
            d_server.close()
            #print 'device=', self.alias, device_status
            #由于当前手动启动数据中心再停止掉时没有清空CENTER_RUNING值，故设备监控以及此处的设备列表均没有变化。服务启动不存在该问题。-darcy20110408
            if device_status is None:#后台服务尚未开启或者开启了但尚未连接--darcy20110408
                return False
            else:
                ret = device_status['CmdReturn']
                if (-400 < ret < -200) or (ret < -10000) or (ret == -1001):#后台数据中心已经启动且设备连接失败--darcy20110408
                    return False
                else:#后台数据中心已经启动且 连接句柄>=0 在线--darcy20110408
                    return True

        elif self.device_type == DEVICE_TIME_RECORDER:
            from base.sync_api import SYNC_MODEL, get_device_status
            if SYNC_MODEL:
                return get_device_status(self.sn)
            else:
                from mysite.iclock.cache_cmds import get_device_last_activity
                last_activity = get_device_last_activity(self)
            
            if (datetime.datetime.now() - last_activity).seconds < min_delay+60:  #小于设置的时间+1分钟之内为联机状态
                return True
            else:
                return False
        elif self.device_type == DEVICE_POS_SERVER:
            if get_option("POS_ID") and self.last_activity:
                if (datetime.datetime.now() - self.last_activity).seconds < 60*5:  #小于五分钟之内为联机状态
                    return True
                else:
                    return False
            else:
                from mysite.pos.pos_ic.ic_sync_action import get_pos_device_status
                return get_pos_device_status(self.sn)
        else:
            return False
            
    def show_enabled(self):
        if self.enabled:
            return True
        else:
            return False
    
    def show_pos_log_count(self):
        path=settings.C_ADMS_PATH%"zkpos/"
        count = 0
        if get_option("POS_IC") and self.device_type == DEVICE_POS_SERVER and os.path.exists(path):
            file_list = os.listdir(path)
            for file_name in file_list:
                f_list =  file_name.split("_")
                if f_list[0] == self.sn:
                    count+=1
        return u"待解析文件:%s" % count
    
    def show_pos_deviec_cmd(self):
        from mysite.sql_utils import p_query,p_execute,p_query_one
        count = 0
        if get_option("POS_IC") and self.device_type == DEVICE_POS_SERVER :
            sql = "select count(*) from devcmds where SN_id = %s"%self.pk
            cmd_count = p_query_one(sql)
            if cmd_count:
                count = cmd_count[0]
            
        return u"待执行命令:%s" % count
    
        
    #搜索新增设备加入通讯线程 insert operate_cmd=1 update operate_cmd=2
    def add_comm_center(self, old_comm_info, operate_cmd):
        from mysite.iaccess.dev_comm_center import OPERAT_ADD, OPERAT_EDIT, OPERAT_DEL
        #print '---operate_cmd=',operate_cmd
        if operate_cmd==OPERAT_ADD:
            try:
                d_server = start_dict_server()
                devinfo = self.getdevinfo()
                devinfo["operatstate"] = OPERAT_ADD#设备信息基础上添加用于后台处理的操作类型标记
                minfo = True
                dev_opt = d_server.get_from_dict(DEVOPT) or []
                #print '--add_comm_center---len of devopt=',len
                for info in dev_opt:
                    try:
                        dinfo = pickle.loads(info)
                    except:
                        dinfo = False

                    if (dinfo["id"] == devinfo["id"]) and (dinfo["operatstate"] == devinfo["operatstate"]):
                        minfo = False
                #print '---@######--minfo=',minfo
                if minfo:
                   # print '----pickle.dumps(devinfo=',pickle.dumps(devinfo)
                    d_server.rpush_to_dict(DEVOPT, pickle.dumps(devinfo))
                    #print devinfo["id"], " operate add"
                #print '----@@@devopt=',q_server.get_from_dict(DEVOPT)
                d_server.set_to_dict(self.get_doorstate_cache_key(), "0,0,0")
                d_server.set_to_dict(self.get_last_activity(), "0")#??
                d_server.set_to_dict("DEVICE_ADDED", 1)#通知实时监控需要重新获取设备，避免缓存导致新增设备无法获取状态(修改删除可不考虑)-darcy20110902
                d_server.set_to_dict("DEVICE_ADDED_MONITOR", 1)#通知设备监控需要重新获取设备，避免缓存导致新增设备无法获取状态(修改删除可不考虑)-darcy20110902
                d_server.close()
            except:
                print_exc()
        elif operate_cmd == OPERAT_EDIT:  #对设备的新增，删除只能做一次，但修改可做多次操作
            try:                    #删除旧设备
                d_server = start_dict_server()
                old_comm_info["operatstate"] = OPERAT_DEL
                d_server.rpush_to_dict(DEVOPT, pickle.dumps(old_comm_info))
                d_server.set_to_dict("DEVICE_DELETE", 1)
                d_server.set_to_dict("DEVICE_DELETE_MONITOR", 1)
                d_server.close()
                self.add_comm_center(None, OPERAT_ADD)
            except:
                print_exc()

    def get_dstime_name(self):
        #print self.dstime.dst_name
        return self.dstime.dst_name

    def show_last_activity(self):
        if get_option("POS_IC") and self.device_type == DEVICE_POS_SERVER:
            from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
            from mysite.pos.pos_ic.ic_sync_model import Pos_Device
            device=Pos_Device(self.sn)
            try:
                device=device.get()
            except PosDeviceDoesNotExist:
                return ""
            try:
                last_activity_str = device.get("last_activity")
            except:
                return ""
            return last_activity_str
        else:
            from mysite.iclock.cache_cmds import get_device_last_activity
            last_activity = get_device_last_activity(self)        
            return last_activity.strftime("%Y-%m-%d %X")

    #当前仅门禁用
    def show_fp_mthreshold(self):#为0时为获取失败（设备问题）
        return self.fp_mthreshold or _(u"获取失败或不支持")

    def get_area(self):
        u"取得当前设备所属区域"
        from mysite.personnel.models.model_area import Area
        area=""
        try:
            area=Area.objects.get(pk = self.area_id)
        except:
            pass
        
        return area
    
    def get_area_name(self):
        u"取得area的名称"
        area = self.get_area()
        if area:
            return area.areaname
        return ""
    def att_cmd_cnt(self):
        count = 0
        if get_option("ATT") and self.device_type == DEVICE_TIME_RECORDER :
            from base.sync_api import get_count_cmd
            count =  get_count_cmd(self.sn)
        return count
    
    class Admin(CachingModel.Admin):
        from django.forms import RadioSelect
        from mysite.personnel.models.depttree import  ZDeptChoiceWidget
        sort_fields=["sn","last_activity","ipaddress"]
        default_give_perms=["contenttypes.can_AttDeviceDataManage","contenttypes.can_PosDeviceDataManage", "contenttypes.can_DoorSetPage","contenttypes.can_FloorSetPage"]
        menu_index=9991
        help_text = _(u'%s'%get_option("DEVICE_HELP_TEXT"))
        api_fields = get_option("DEVICE_API_FIELDS")
        list_display = get_option("DEVICE_LIST_DISPLAY")
        adv_fields=['alias','sn', 'ipaddress','area.areaname','last_activity']+DeviceAdvField
        newadded_column = { 
            'area.areaname':'get_area_name',
            'last_activity':'show_last_activity',
            'pos_file_count':'show_pos_log_count',
            'pos_cmd_count':'show_pos_deviec_cmd',
            'att_cmd_cnt':'att_cmd_cnt'
            #'status':'show_status'
        }
        query_fields = get_option("DEVICE_QUERY_FIELDS")
        hide_fields = get_option("DEVICE_DISABLE_COLS")
        query_fields_iaccess = ['alias', 'acpanel_type', 'iaccess:accdoor__door_name']#支持输入门查询设备
        query_fields_elevator = ['alias', 'acpanel_type']
        search_fields = ["sn", "alias"]
        default_widgets={
            'device_type': RadioSelect, 
            'comm_type': RadioSelect, 
            'comm_pwd': forms.PasswordInput,
            'area':ZDeptChoiceWidget(attrs={"async_model":"personnel__Area"}),
            'favorable':ZBaseSmallIntegerWidget,
            'card_max_money':ZBase3IntegerWidget,
            'dz_money':ZBaseMoneyWidget,
            'time_price':ZBaseMoneyWidget,
            'long_time':ZBaseSmallIntegerWidget,
        }
        detail_model = ['iaccess/AccDoor']
        cache=3600
#        layout_types=["table","photo"]
        #photo_path="photo"#指定图片的路径，如果带了".jpg",就用这个图片，没有带的话就找这个字符串所对应的字段的值
        disabled_perms = get_option("DEVICE_DISABLED_PERMS") + init_settings
        opt_perm_menu = { "opchangebaudrate_device": "iaccess.DoorMngPage", "uploaduserinfo_device": "iaccess.DoorMngPage", "uploadlogs_device": "iaccess.DoorMngPage", "opdisabledevice_device": "iaccess.DoorMngPage", "openabledevice_device": "iaccess.DoorMngPage", "opchangeipofacpanel_device": "iaccess.DoorMngPage", "syncacpaneltime_device": "iaccess.DoorMngPage", "resetpassword_device": "iaccess.DoorMngPage",  "opupgradefirmware_device": "iaccess.DoorMngPage", "opsetdstime_device": "iaccess.DoorMngPage", "opremovedstime_device": "iaccess.DoorMngPage",\
           "SyncACPanelTime": "pos.PosDeviceDataManage","SyncACPanelTime": "pos.PosDeviceDataManage","Reboot": "pos.PosDeviceDataManage","OpReloadICPOSData": "pos.PosDeviceDataManage","ClearPosData": "pos.PosDeviceDataManage","ClearData": "pos.PosDeviceDataManage", "cleartransaction_device": "att.AttDeviceDataManage", "refreshdeviceinfo_device": "att.AttDeviceDataManage" ,"clearpicture_device": "att.AttDeviceDataManage","cleardata_device": "att.AttDeviceDataManage", "opreloaddata_device": "att.AttDeviceDataManage", "opreloaddata_device": "att.AttDeviceDataManage",  "reboot_device": "att.AttDeviceDataManage","OpUpAttInfo_device":"att.AttDeviceDataManage","OpUpEmpInfo_device":"att.AttDeviceDataManage","RemoteUpgrade_device":"att.AttDeviceDataManage","OpAddDeviceMsg_device":"att.AttDeviceDataManage"}
        if get_option("ONLY_POS"):
            hide_perms = ["opchangemthreshold_device","opcloseauxout_device"]+get_option("DEVICE_HIDE_PERMS")
        else:
            hide_perms = ["opchangemthreshold_device","opcloseauxout_device"]
        #scroll_table=False#列表是否需要滚动
    class Meta:
        app_label='iclock'
        db_table = 'iclock'
        verbose_name = _(u'设备')
        verbose_name_plural=verbose_name
        #unique_together = (('com_port', 'com_address'),)

def device_op(func):
#    from mysite.iclock.models.model_device import Device
    setattr(Device,func.__name__,func)
    return func

installed_apps = settings.INSTALLED_APPS
#if ("mysite.iaccess" in installed_apps) and ("mysite.att" in installed_apps):
#    pass#默认
#elif "mysite.iaccess" in installed_apps:#门禁
#    Device.Admin.help_text = _(u'设备名称、各通信参数以及所属区域为必填项。<br>系统会验证用户提交的设备是否存在，并判断门禁控制器类型是否正确。')
#    Device.Admin.query_fields = ['alias', 'sn', 'comm_type','area__areaname']#Device处的列表
#    Device.Admin.adv_fields = ['alias','sn', 'ipaddress','area.areaname']+DeviceAdvField
#    api_fields = ('alias','device_type','sn', 'comm_type','ipaddress','com_address','area.areaname','Fpversion', 'acpanel_type')
#    list_display = ('alias','sn', 'device_type','comm_type','ipaddress','com_port',
#                'com_address','get_dstime_name','area.areaname','Fpversion','show_status|boolean_icon',
#                'show_enabled|boolean_icon', 'acpanel_type', 'device_name','user_count','fp_count','transaction_count','show_fp_mthreshold','fw_version',)
#elif "mysite.pos" in installed_apps:#消费
#    Device.Admin.help_text = _(u'设备名称、各通信参数以及所属餐厅,消费模式为必填项')
#    Device.Admin.query_fields = ['alias', 'sn','dining__name']#Device处的列表
#else:#考勤
#    Device.Admin.help_text = _(u'设备名称、各通信参数以及所属区域为必填项。')
#    Device.Admin.query_fields = ['alias', 'sn', 'area__areaname']#Device处的列表

if len(dict(DEVICE_TYPE).keys()) > 1:#只有设备类型多于一种时，才需要设备类型的查询
    Device.Admin.query_fields += ('device_type',)

class DeviceForeignKey(models.ForeignKey):
    def __init__(self, verbose_name="", **kwargs):
        super(DeviceForeignKey, self).__init__(Device, verbose_name=verbose_name, **kwargs)

class DeviceManyToManyFieldKeyForMeeting(models.ManyToManyField):#会议签到设备
    def __init__(self, verbose_name="", **kwargs):
        super(DeviceManyToManyFieldKeyForMeeting, self).__init__(Device, verbose_name=verbose_name, **kwargs)

class DeviceManyToManyFieldKey(models.ManyToManyField):
    def __init__(self, verbose_name="", **kwargs):
        super(DeviceManyToManyFieldKey, self).__init__(Device, verbose_name=verbose_name, **kwargs)

def update_device_widgets():
        from dbapp import widgets
        from pos_device_dropdown import ZDeviceChoiceWidget,ZDeviceMultiChoiceWidget
        from meeting_device_dropdown import ZDeviceChoiceWidgetForMeeting,ZDeviceMultiChoiceWidgetForMeeting
        if DeviceForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[DeviceForeignKey] = ZDeviceChoiceWidget
                
        if DeviceManyToManyFieldKeyForMeeting not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:#会议签到设备
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[DeviceManyToManyFieldKeyForMeeting] = ZDeviceChoiceWidgetForMeeting
        
        if DeviceManyToManyFieldKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[DeviceManyToManyFieldKey] = ZDeviceMultiChoiceWidget
            
update_device_widgets()

#解析门禁控制器的options参数
def options_split(acp_opts):#
    options = {}
    #print '----acp_opts=',acp_opts
    if acp_opts:#[u'']
        for acp_opt in acp_opts:
            if acp_opt:#不能为u''
                opt = acp_opt.split("=")
                options[opt[0]] = opt[1]
    return options

def data_pre_check(sender, **kwargs):
    model = kwargs['model']
    if model == Device:
        request = sender
        device_type = int(request.POST.get("device_type", -1))
        #print '-----device_type=',device_type
        if device_type == DEVICE_ACCESS_CONTROL_PANEL and not kwargs['oldObj']:#只考虑新增时，编辑时不涉及sn（门禁&&硬盘录像机）
            try:
                acp_opts = request.POST.get("ACPanelOptions", '').split(",")
                options = options_split(acp_opts)
                sn = options.has_key("~SerialNumber") and options["~SerialNumber"] or ''
                #Fpversion = options.has_key("~ZKFPVersion") and options["~ZKFPVersion"] or ''
                #print '----sn=',sn
                #print Device.objects.filter(sn=sn).exists()
                if sn and Device.objects.filter(sn=sn).exists():
                    raise Exception(_(u'该设备的序列号：%s 已存在') % sn)
            except:
                print_exc()

data_edit.pre_check.connect(data_pre_check)#不同于pre_save

def DataPostCheck(sender, **kwargs):
    oldObj=kwargs['oldObj']
    newObj=kwargs['newObj']
    request=sender
    if isinstance(newObj, Device):
        #此时Device对应的AccDevice记录已经生成
        if newObj.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            #print "device_args_save---door_count=",newObj.accdevice.door_count
            #print "sn=",newObj.accdevice.device.sn
            connected = request.POST.getlist("connect_result")
            #print '------------------------connected=',connected
            #新增时sn肯定为None
            if connected and not newObj.accdevice.door_count:#尚未写入门数量参数.如果sn没写入，说明没有连接成功（新增设备时）或者在大循环中已经连接成功，但设备参数已由check_acpanel_args写入，不需要重复连接设备
                #print "DataPostCheck---now beginning to get device arguments and save them."
                options = {}
                try:
                    acp_opts = request.POST.get("ACPanelOptions", '').split(",")
                    options = options_split(acp_opts)
                except:
                    print_exc()

                #is_rf_machine = options.has_key("~IsOnlyRFMachine") and int(options["~IsOnlyRFMachine"]) or 1 #判断设备类型，4.0-5.0
                is_rf_machine = 1
                if options.has_key("~IsOnlyRFMachine"):
                    is_rf_machine = int(options["~IsOnlyRFMachine"])
                    #print "########is_rf_machine=(medel_device)",is_rf_machine
                if is_rf_machine:
                    newObj.max_finger_count = 0
                    newObj.fp_mthreshold = 0
                    newObj.Fpversion = None
                else:#5.0
                    newObj.max_finger_count = options.has_key("~MaxUserFingerCount") and int(options["~MaxUserFingerCount"]) or 0
                    newObj.fp_mthreshold = options.has_key("MThreshold") and int(options["MThreshold"]) or 0
                    newObj.Fpversion = options.has_key("~ZKFPVersion") and options["~ZKFPVersion"] or ''

                newObj.sn = options.has_key("~SerialNumber") and options["~SerialNumber"] or ''
                newObj.fw_version = options.has_key("FirmVer") and options["FirmVer"] or ''
                newObj.device_name = options.has_key("~DeviceName") and options["~DeviceName"] or ''
                #新增获取三个容量参数--add by darcy 20101122
                newObj.max_user_count = options.has_key("~MaxUserCount") and int(options["~MaxUserCount"])*100 or 0
                newObj.max_attlog_count = options.has_key("~MaxAttLogCount") and int(options["~MaxAttLogCount"])*10000 or 0
                newObj.subnet_mask = options.has_key("NetMask") and options["NetMask"] or ''
                newObj.gateway = options.has_key("GATEIPAddress") and options["GATEIPAddress"] or ''

                try:
                    newObj.save(force_update=True)
                except:
                    print_exc()
                #print '---Device has been updated,SN FWVersion DeviceName.....'
                newObj.accdevice.door_count = options.has_key("LockCount") and int(options["LockCount"]) or 0
                newObj.accdevice.reader_count = options.has_key("ReaderCount") and int(options["ReaderCount"]) or 0
                newObj.accdevice.aux_in_count = options.has_key("AuxInCount") and int(options["AuxInCount"]) or 0

                newObj.accdevice.aux_out_count = options.has_key("AuxOutCount") and int(options["AuxOutCount"]) or 0
                try:
                    newObj.accdevice.machine_type = options.has_key("MachineType") and int(options["MachineType"]) or 0
                except ValueError:
                    pass
                newObj.accdevice.iclock_server_on = options.has_key("IclockSvrFun") and int(options["IclockSvrFun"]) or 0
                try:
                    newObj.accdevice.global_apb_on = options.has_key("OverallAntiFunOn") and int(options["OverallAntiFunOn"]) or 0
                except:
                    newObj.accdevice.global_apb_on = 0
                newObj.accdevice.IsOnlyRFMachine = is_rf_machine

                try:
                    newObj.accdevice.save(force_update=True)
                except:
                    print_exc()
                #print "SN FwVesion door_count......have been updated to Device and AccDevice......"

        from mysite.iclock.models.dev_comm_operate import sync_delete_all_data, sync_set_all_data
        from mysite.iclock.models.model_cmmdata import adj_device_cmmdata
        try:
            if oldObj is None:
#                if newObj.device_type==DEVICE_TIME_RECORDER:
#                    adj_device_cmmdata(newObj,newObj.area)
                if newObj.device_type==DEVICE_ACCESS_CONTROL_PANEL:#新增门禁控制器
                    #newObj.delete_transaction()#新增门禁控制器时删除所有的事件记录
                    whether_sync_all = request.POST.getlist("whether_sync_all")
                    #print '------------whether_sync_all=',whether_sync_all
                    if whether_sync_all:#[u'on']
                        #newObj.delete_transaction()#新增门禁控制器时删除所有的事件记录
                        sync_set_all_data(newObj)
                    from mysite.iaccess.dev_comm_center import OPERAT_ADD
                    newObj.add_comm_center(None, OPERAT_ADD)
            else:
                if newObj.device_type==DEVICE_TIME_RECORDER:
                    from base.sync_api import SYNC_MODEL
                    if not SYNC_MODEL:
                        if oldObj.area!=newObj.area or oldObj.Fpversion!=newObj.Fpversion:
                            adj_device_cmmdata(newObj,newObj.area)
                elif newObj.device_type==DEVICE_ACCESS_CONTROL_PANEL:
                    #控制器区域变化时，清空该控制器内所有门所在地图上的信息
                    if newObj.area != oldObj.area:
                        map_doors = newObj.accdoor_set.filter(map__isnull=False)
                        for map_door in map_doors:
                            map_door.accmapdoorpos_set.all().delete()
                            map_door.map = None
                            map_door.save(force_update=True)

                    from mysite.iaccess.dev_comm_center import OPERAT_EDIT, OPERAT_ADD, OPERAT_DEL
                    if oldObj.com_port != newObj.com_port:    # 修改串口号
                        try:                    #删除旧设备
                            d_server = start_dict_server()
                            devinfo = oldObj.getdevinfo()
                            devinfo["operatstate"] = OPERAT_DEL
                            d_server.rpush_to_dict(DEVOPT, pickle.dumps(devinfo))
                            d_server.close()
                        except:
                            print_exc()
                        newObj.add_comm_center(None, OPERAT_ADD)  #增新设备
                    elif oldObj.alias != newObj.alias:
                        newObj.add_comm_center(newObj.getdevinfo(), OPERAT_EDIT)
                        
                        
        except:
            import traceback;traceback.print_exc()
data_edit.post_check.connect(DataPostCheck)

def get_device(device_id):
    device_obj = ""
    try:
        device_obj = Device.objects.get(pk = device_id)
    except:
        pass
    
    return device_obj


def get_device_attr(device_id,attr):
    device_obj = get_device(device_id)
    if device_obj:
        return getattr(device_obj,attr)
    return None

def get_att_pic_path(sn):
    """获取服务器上设备对应的考勤图片路径"""
    from dbapp.additionfile import get_model_filename
    from model_trans import Transaction
    path= get_model_filename(Transaction,sn,"picture")[0]
    return path

def clear_pic(path):
    """删除指定文件夹下的图片"""
    if os.path.exists(path):
        try:
             for f in os.listdir(path):                 
                 if os.path.isfile(path+os.sep+f):
                    try:
                        os.remove(path+os.sep+f)
                    except:
                        print_exc()
                 else:
                     clear_pic(path+os.sep+f) 
             os.rmdir(path)
        except (WindowsError):
               print_exc()
                     
class DevicePoPForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
            super(DevicePoPForeignKey, self).__init__(Device, to_field=to_field, **kwargs)
