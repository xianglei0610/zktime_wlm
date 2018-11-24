#! /usr/bin/env python
#coding=utf-8
from django.db import models
from django.utils import simplejson
from django.http import HttpResponse
from django.utils.encoding import smart_str
from base.middleware import threadlocals
from django.utils.translation import ugettext_lazy as _
from models import AccDoor
from mysite.iclock.models import Device 
from mysite.personnel.models import Employee, Area
from redis_self.server import start_dict_server, queqe_server
from django.contrib.auth.decorators import login_required
import redis_self, re, os, dict4ini, datetime
import re
from traceback import print_exc
from mysite.personnel.models.model_emp import format_pin
from django.db.models import Q  
from mysite.iclock.models.model_device import DEVICE_ACCESS_CONTROL_PANEL, ACCDEVICE_DISABLED, ACCDEVICE_ENABLE_CHANGED

from models.accmonitorlog import EVENT_CHOICES, VERIFIED_CHOICES, IN_ADDRESS_CHOICES, OUT_ADDRESS_CHOICES, STATE_CHOICES, EVENT_CHOICES
from dev_comm_center import DEVICE_COMMAND_RETURN, check_service_commcenter, get_cmd_content
from dbapp.datautils import filterdata_by_user
from mysite.iaccess.models import AccLinkageIO
from base.crypt import decryption
from mysite.utils import printf, delete_log, write_log
from mysite.personnel.models.model_issuecard import IssueCard

try:
    import cPickle as pickle
except:
    import pickle
import time
g_monitor_server = None
g_monitor_devices = None
g_dev_comm_error_list = None
g_monitor_doors = {}
g_monitor_emps = None
g_dev_door_id = {}
g_area_dev_door_change = ""
g_dev_doors = {}#不能为None

FIRSTVISIT_OR_DELBACKEND = -1 #初始为-1代表为第一次请求（初始化）， 不能为0，否则可能与rtid_all产生冲突   redis最小为1

#门状态可以具体到某个或某几个控制器（不具体到门），事件则具体到门
#控制服务器只将符合当前用户条件的门状态信息发送给前端
@login_required
def obtain_valid_devices(request):
    u = request.user
    aa = u.areaadmin_set.all()#如果新增用户时设定区域，那么aa不为空，否则为空代表全部（包含普通用户和超级管理员）
    a_limit = aa and [int(a.area_id) for a in aa] or [int(area.pk) for area in Area.objects.all()]#非超级管理员且没有配置有效区域（默认全部）的有效区域id列表（即用户手动配置过用户区域的）    
    
    area_id = int(request.GET.get("area_id", 0))#不为0.前端随已经过过滤，但是考虑用户可以手动修改url
    #print '----area_id=',area_id
    if area_id and area_id in a_limit:
        #devices = Device.objects.filter(area__pk=area_id)#权限范围内的全部
        devices = Device.objects.filter(Q(area__pk=area_id)|Q(area__in=Area.objects.get(id=area_id).area_set.all()))#权限范围内的全部,且要处理区域的上下级
    else:
        device_id = int(request.GET.get("device_id", 0))
        #print '----device_id=',device_id
        dev_limit = [int(d.pk) for d in Device.objects.filter(area__pk__in=a_limit)]#权限范围内的设备
        if device_id and device_id in dev_limit:
            devices = Device.objects.filter(pk=device_id)
        else:
            door_limit = [int(door.id) for door in AccDoor.objects.filter(device__area__pk__in=a_limit)]#所有有效的
            doors_id = request.GET.get("door_id", '0')#此处可能是单个数字也可以能是多个 0代表默认情况（全部门）
            global g_monitor_server
            if not g_monitor_server:
               g_monitor_server = start_dict_server()
            g_monitor_server.set_to_dict("VALID_DOORS", doors_id)#前端获取到的需要监控的门，若此值改变需重新获取g_monitor_devices
            #print '--first--doors_id=',doors_id ,'type=',type(doors_id)
            
            is_many_doors = doors_id.__contains__(',')

            if is_many_doors:#多门
                doors_id = doors_id.split(",")#默认0，取全部
                #print '----doors_id=',doors_id
                doors_id_left = [int(id) for id in doors_id if int(id) in door_limit]#当前需要的---不过滤也可以
                devices = Device.objects.filter(accdoor__pk__in=doors_id_left).distinct()
                #print '---devices=',devices
            elif doors_id == '0':#没有area_id,device_id,door_id的请求--door_id实际不可能为0
                #print '----none----'
                devices = Device.objects.filter(area__pk__in=a_limit)
            else:#单门
                devices = Device.objects.filter(accdoor__pk=int(doors_id)).distinct()
    
    valid_devices_dict = {}
    valid_devices = devices.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL)
    for dev in valid_devices:
        valid_devices_dict[int(dev.id)] = dev
    #print '--@@@@@valid_devices_dict values=', valid_devices_dict.values()
    global g_dev_door_id#记录dev和door id的关系
    for dev in valid_devices_dict.values():
        ids = dev.accdoor_set.values_list("id")
        g_dev_door_id[int(dev.id)] = [int(id[0]) for id in ids]#[(12L,), (11L,), (9L,), (10L,)]
    return valid_devices_dict

def obtain_valid_doors(request, devices_keys, g_dev_door_id):
    doors_id = request.GET.get("door_id", 0)
    #print '---000131'
    if doors_id:
        #print '---000132'
        doors_id = doors_id.split(",")#默认0，取全部
        return [int(id) for id in doors_id]
    else:
        #print '---000133'
        #doors = 
        #print '---000134'
        doors_id = []
        for dev_key in devices_keys:
            if g_dev_door_id.has_key(dev_key):
                doors_id += g_dev_door_id[dev_key]

        return doors_id#[int(d.id) for d in g_monitor_doors.values.filter(device__in=devices)]


#处理门禁数据，提供给第三方使用
def process_acc_data(request):
    from mysite.authurls import logon
#    from django.contrib.auth.views import login
#    global g_login_result
#    print '----g_login_result=',g_login_result
#    if g_login_result is None:
    g_login_result = logon(request)#<class 'django.http.HttpResponse'>
    try:
        if g_login_result.content == "ok": #验证通过
            if request.GET.get('func', '') == 'doors':#查询数据库门信息 
                from mysite.iaccess.view import get_data
                return get_data(request)
            return get_redis_rtlog(request)
        else:
            return g_login_result
    except:
        print_exc()


#从缓存中获取实时事件的记录，数据经过组织后返回客户端
@login_required
def get_redis_rtlog(request):
    rtdata = {}
    try:
        #print '----in here request=',request
        changed_value = request.GET.get("change","")#默认情况下为“”。决定是否需要重新获取所有有效设备，避免将设备缓存后前段无效。--darcy20110731
        #print '-----changed_value=',changed_value
        global g_area_dev_door_change
        
        logid = int(request.GET.get('logid', FIRSTVISIT_OR_DELBACKEND))
        step = int(request.GET.get('step', 0))#步长：即要log的最大条数
        rt_type = request.GET.get('type', '')#all alarm 
        devid = request.REQUEST.get("devid", 0)#默认为0，表示监控所有设备的所有门的状态
        doors_id = request.GET.get("door_id", '0')
        #再获取实时监控记录
        #print '----before g_monitor_server'
        #print '----00001'
        global g_monitor_server
        #print '----after g_monitor_server'
        if not g_monitor_server:
            #print '--rtlog--first time=',g_monitor_server
            g_monitor_server = start_dict_server()

        #控制后台是否需要开启实时监控
        rtmonitor_stamp = datetime.datetime.now()     
        g_monitor_server.set_to_dict("RTMONITOR_STAMP", rtmonitor_stamp)
        
        rtid_all = 0#缓存里所有的记录条数
        rtid_alarm = 0#缓存里所有的报警事件记录
        log_count = 0#返回的有效记录条数
        valid_devices_dict = {} 
        deleted = g_monitor_server.get_from_dict("MONITOR_RT_DEL")#没有该值时返回None，如果为True,实时监控需要重新取
        g_monitor_server.delete_dict("MONITOR_RT_DEL")
        #print '----deleted=',deleted
        #print '----00003'
        rtlog = []
        if rt_type == "all":
            #rtid_all = g_monitor_server.lock_rlen("MONITOR_RT")#被锁住时以及文件缓存为空时都返回-1，即该值不可能为0 此时前端继续使用原来的logid取数据
            rtid_all = g_monitor_server.llen_dict("MONITOR_RT")
            
            #print '-REALLOG--deleted=',deleted,'   -rtid_all=',rtid_all, '---logid=',logid
            #from mysite.utils import printf
            #printf("---deleted=%s, rtid_all=%s, logid=%s"%(deleted, rtid_all, logid))
            #获取门状态door_states
            #为提高监控页面的用户体验，降低该页面的数据库查询，使用全局变量，避免查询数据库，这样就要求，用户添加或者修改设备信息后必须手动刷新页面，由于对于设备的操作不会过于频繁，所以可以接受--darcy20110728
            #print '----00004'
            
            global g_monitor_devices
            changed_break = False
            device_added = g_monitor_server.get_from_dict("DEVICE_ADDED")#新增
            device_delete = g_monitor_server.get_from_dict("DEVICE_DELETE")#删除和编辑
            check_enable = g_monitor_server.get_from_dict(ACCDEVICE_ENABLE_CHANGED)#禁用或者启用任何一台设备，实时监控都需要重新获取设备。--darcy20111012
            
            last_doors_id = g_monitor_server.get_from_dict("VALID_DOORS")
            valid_door_changed = (doors_id!=last_doors_id)#前端门改变了重新获取g_monitor_devices
            #print '=======$$$$$valid_door_changed=%s'%valid_door_changed
            if (not g_monitor_devices) or (changed_value != g_area_dev_door_change) or device_added or device_delete or check_enable or valid_door_changed:
                #printf('=======$$$$$valid_door_changed=%s'%valid_door_changed, True)
                #print '--- not exist or get again'
                g_area_dev_door_change = changed_value
                try:
                    valid_devices_dict = obtain_valid_devices(request)
                except Exception, e:
                    print '-----e=',e
                #print '---valid_devices_dict=',valid_devices_dict
                g_monitor_devices = valid_devices_dict
                changed_break = True
                if device_added:
                    g_monitor_server.set_to_dict("DEVICE_ADDED", 0)
                if device_delete:
                    g_monitor_server.set_to_dict("DEVICE_DELETE", 0)
            else:
                valid_devices_dict = g_monitor_devices
                #sprint '--- exist'
            
            #print '----00012'
            global g_monitor_doors
            if not g_monitor_doors or device_added or device_delete:#只用到id，没有用到其他的设备或者门的属性
                #print '--g_monitor_doors not exist=',g_monitor_doors
                for door in AccDoor.objects.all():
                    g_monitor_doors[int(door.id)] = door 
            #print '----00013'
            #print '---g_dev_door_id=',g_dev_door_id

            #print '----00005'
 
            if deleted == True or rtid_all < logid:
                logid = -1
            if logid != -1:
                #print '----00006'
                if logid == FIRSTVISIT_OR_DELBACKEND:#监控全部时获取报警记录的初始id值
                    rtid_alarm = g_monitor_server.llen_dict("ALARM_RT")
                    #rtid_alarm = g_monitor_server.llen("ALARM_RT")
                #rtlog = g_monitor_server.lrange_from_file("MONITOR_RT", logid, logid + step)
                #print '--all real log-rtlog=',g_monitor_server.get_from_dict("MONITOR_RT")
                
                #取出来的是列表           
                timeout = 0
#                print '----000061'
                while True:
                    rtlog = g_monitor_server.lrange_from_dict("MONITOR_RT", logid, logid + step)
                    if not rtlog:
                        doorstate_changed = g_monitor_server.get_from_dict("GET_DOORSTATE_AGAIN")#接受到后台通知，实时监控线程立即返回门状态数据--darcy20110805
                        #print '----doorstate_changed=',doorstate_changed
                        if doorstate_changed:
                            g_monitor_server.set_to_dict("GET_DOORSTATE_AGAIN", 0)
                            break
                        
                        check_enable = g_monitor_server.get_from_dict(ACCDEVICE_ENABLE_CHANGED)
                        if check_enable:
                            try:
                                valid_devices_dict = obtain_valid_devices(request)
                            except Exception, e:
                                print '-----e2=',e
                            #print '---valid_devices_dict=',valid_devices_dict
                            g_monitor_devices = valid_devices_dict
                            g_monitor_server.delete_dict(ACCDEVICE_ENABLE_CHANGED)
                            break
                            
                        #print '----changed_break=',changed_break
                        if changed_break:
                            break
                        timeout += 1
#                        print '--timeout=',timeout
                        if timeout > 30:#60
                            #g_monitor_server.set_to_dict("GET_DOORSTATE_AGAIN", 0)
                            break#超时后HttpResponse
                        time.sleep(0.3)
                        continue
                    else:
                        g_monitor_server.set_to_dict("GET_DOORSTATE_AGAIN", 0)
                        break
                
                #print '----000062'
            #print '---valid_devices_dict=',valid_devices_dict
            door_states = door_state_monitor(valid_devices_dict.values(), g_monitor_server)#门状态不涉及辅助输入点，故不需调整
#            print 'door_states==',door_states
        elif rt_type == "alarm":
            #rtid_alarm = g_monitor_server.lock_rlen("ALARM_RT")
            rtid_alarm = g_monitor_server.llen_dict("ALARM_RT")
            
            door_states = { "data": []}
            if deleted == True or rtid_alarm < logid:
                logid = -1
            if logid != -1:
                #取出来的是列表           
                timeout = 0
                #print '----000061'
                while True:
                    rtlog = g_monitor_server.lrange_from_dict("ALARM_RT", logid, logid + step)
                    if not rtlog:
                        timeout += 1
                        #print '--timeout=',timeout
                        if timeout > 60:#60:#一分钟
                            break#超时后HttpResponse
                        time.sleep(0.2)
                        continue
                    else:
                        break
            
        #print '----000063'
        #rtlog数据格式如下“0-时间 + 1-PIN号 + 2-门id + 3-事件类型 + 4-出入状态 +5-验证方式 +6-卡号+7-设备号”
        #print 'door_states=',door_states
        #print "----------------------rtlog=", rtlog
        
        #print '---monitor log=',g_monitor_server.get_from_dict("MONITOR_RT")
        #g_monitor_server.close()
        #g_monitor_server.connection.disconnect()
        
        cdatas = []
        a_logids = []
        #如下代码测试时请注释掉
        if logid == FIRSTVISIT_OR_DELBACKEND:
            cc={
                'log_id': logid,
                'all_id': (rtid_all != FIRSTVISIT_OR_DELBACKEND) and rtid_all or 0,#redis中所有记录条数
                'alarm_id': rtid_alarm,
                'log_count': log_count,#返回的记录条数
                'data': cdatas,
                'door_states': door_states["data"],
            }
            rtdata = simplejson.dumps(cc)
            return HttpResponse(smart_str(rtdata))
        #print '----00007'
        #rtlog不存在，不需要获取有效设备--darcy20110729
        if rtlog and not valid_devices_dict:#如果之前没有进入“all”则需要重新获取有效设备（主要是避免重新获取，每次请求只获取一次即可）
            valid_devices_dict = obtain_valid_devices(request)#通过设备找到对应的门以及辅助输入，作为事件点
        
        #print '----00008'
        #rtlog = ['2010-03-07 09:53:51,370,4,6,0,221,36656656']
        #rtlog = ['2010-03-07 09:53:51,1,2,101,0,4,36656656,2']#自动生成报警事件 需修改PIN号，门id以及设备id方可使用
        
        #print '----rtlog=',rtlog
        global g_monitor_emps
        
        for alog in rtlog:
            log = alog.strip()#log = alog.strip()
            #print "---current log=", log
            #验证数据合法性，保证了除了时间之外的数据都是数字字符，从而可以使用int()而不会出错
            p1 = re.compile(r'(((^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(10|12|0?[13578])([-\/\._])(3[01]|[12][0-9]|0?[1-9]))|(^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(11|0?[469])([-\/\._])(30|[12][0-9]|0?[1-9]))|(^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(0?2)([-\/\._])(2[0-8]|1[0-9]|0?[1-9]))|(^([2468][048]00)([-\/\._])(0?2)([-\/\._])(29))|(^([3579][26]00)([-\/\._])(0?2)([-\/\._])(29))|(^([1][89][0][48])([-\/\._])(0?2)([-\/\._])(29))|(^([2-9][0-9][0][48])([-\/\._])(0?2)([-\/\._])(29))|(^([1][89][2468][048])([-\/\._])(0?2)([-\/\._])(29))|(^([2-9][0-9][2468][048])([-\/\._])(0?2)([-\/\._])(29))|(^([1][89][13579][26])([-\/\._])(0?2)([-\/\._])(29))|(^([2-9][0-9][13579][26])([-\/\._])(0?2)([-\/\._])(29)))((\s+(0?[1-9]|1[012])(:[0-5]\d){0,2}(\s[AP]M))?$|(\s+([01]\d|2[0-3])(:[0-5]\d){0,2})?$))')
            p2 = re.compile(r'^,(((\d+),){6}\d+)$')#r'^,(((\d+),){4}\d+)?$'  5-6
            if p1.match(log[0:19]) and p2.match(log[19:]):
                log_count += 1
                str = log.split(",",8)#0-7 共8部分
                #print "accmonitorlog=", str
                
                #设备名称
                dev_id = int(str[7])
                #print '----00009'
                if not valid_devices_dict.has_key(dev_id):
                    #print '--continue---dev_id=',dev_id,' -----valid_devices_dict=',valid_devices_dict
                    continue
                else:
                    dev = valid_devices_dict[dev_id]
                    
                #print '----00010'
                #if dev and dev[0] not in valid_devices:#设备级别的过滤--辅助输入（含联动中触发条件为辅助输入点的）
#                if not dev:#从有效的设备中查询不到该设备，直接返回
#                    continue
#                else:
                alias = unicode(dev.alias)
                #print '----00011'
                #print 'alias=',alias
                #事件类型
                event = int(str[3])
                try:
                    event_content = unicode(dict(EVENT_CHOICES)[event])#description of the triggered event
                except:
                    event_content = unicode(_(u"未知状态"))
                
                #验证方式（或源事件类型）,但是当事件为联动事件时为联动事件的原事件
                veri_event = int(str[5])
                #卡号-联动时复用为联动id号（pk）
                card_no = int(str[6]) and str[6] or ''
                
                #print '---card_no=',card_no
                door_id = 0
                link_video = []
                #print '---vari_event=',veri_event,'  event=',event
                
                if event in [12, 13, 220, 221]:#辅助输入（220 221）输出（12 13）点的事件
                    #事件点
                    address_id = int(str[2])#辅助输入点，如1,2,3,4  9，10,11,12 辅助输出点 如 1,2,3,4， 9 10
                    if event in [220, 221]:
                        event_point = unicode(dict(IN_ADDRESS_CHOICES)[address_id])
                    else:#12 13
                        event_point = unicode(dict(OUT_ADDRESS_CHOICES)[address_id])
                    #验证方式
                    try:
                        verified = unicode(dict(VERIFIED_CHOICES)[veri_event])#the true verified method("others" included)
                    except:
                        verified = unicode(_(u"未知状态"))
                
                else:#与门相关---包含设备
                    #print '-----!!!!!!!!g_dev_door_id=',g_dev_door_id
                    door_id_limit = obtain_valid_doors(request, valid_devices_dict.keys(), g_dev_door_id)#可控的ip地址，不包含辅助输入点
                    #print '-----!!door_id_limit=',door_id_limit
                    #print '----00014'
                    if event == 6:#事件类型为联动事件
                        #print '----------------event=',event
                        #verified = ''#联动事件验证方式为空-固件字段复用--触发的原事件
                        verified = unicode(dict(VERIFIED_CHOICES)[200])#其他

                        if veri_event == 220 or veri_event == 221:
                            number = int(str[2]) #如C4 9，10,11,12
                            event_point = unicode(dict(IN_ADDRESS_CHOICES)[number])
                            #linkage = AccLinkageIO.objects.filter(Q(device__id=dev_id), Q(trigger_opt=veri_event), Q(in_address_hide=number)|Q(in_address_hide=0))#输入点inout或0只能居其一
                        else:
                            door_id = int(str[2])#门id（不同于门编号）
                            if door_id not in door_id_limit:#门级别的过滤
                                #print '----break---filter door_id=',door_id,' ---door_id_limit=',door_id_limit
                                break #跳出for循环，该记录无效
                            #事件点
                            #print '----00015'
                            door = g_monitor_doors[door_id]
                            event_point = door and unicode(door) or ""
                            #print '----00016'
                        #视频联动处理
                        try:
                            link_id = int(card_no) or 0#联动时卡号复用为联动id号
                        except:
                            link_id = 1#??????why?
                        card_no = ''#联动时不需要显示卡号
                        #print "link_id=", link_id
                        try:
                            #print '----00017'
                            if link_id:#不为0
                                linkage = AccLinkageIO.objects.filter(id = link_id)
                                if linkage:
                                    event_content = "%s(%s)" % (event_content, linkage[0].linkage_name)
                                try:
                                    if linkage[0].video_linkageio:
                                        pwd = linkage[0].video_linkageio.comm_pwd
                                        link_video.append(linkage[0].video_linkageio.ipaddress)
                                        link_video.append(linkage[0].video_linkageio.ip_port)
                                        link_video.append(linkage[0].video_linkageio.video_login)
                                        link_video.append(pwd and decryption(pwd) or "")
                                        link_video.append(linkage[0].lchannel_num)
                                except:
                                    #print_exc() 调试5.0时请打开，5.0与4.0当前文件对拷之用
                                    pass
                                
                                #print '---event_content=',event_content
                                #print '----00018'
                        except:
                            print_exc()
                        

                    else:#其他事件--门相关或设备相关
                        door_id = int(str[2])#门id--如果为0,指的是事件点为设备（如取消报警事件）
                        if door_id:#不为0
                            #print '---door_id=',door_id,door_id_limit
                            if door_id not in door_id_limit:#门级别的过滤
                                #print '--break2-door_id=',door_id,door_id_limit
                                continue #跳出for循环，该记录无效
                            #事件点
                            #print '----00019'
                            try:
                                event_point = unicode(g_monitor_doors[door_id])
                            except:
                                event_point = ""
                        else:
                            event_point = ""#如取消报警事件
                        #print '----00020'
                        try:
                            verified = unicode(dict(VERIFIED_CHOICES)[veri_event])#the true verified method("others" included)
                        except:
                            verified = unicode(_(u"未知状态"))
                        #print '----00022'

                #print 'str[1]=',str[1]
                #print '----00026'
                emps = ''
                emp_changed = g_monitor_server.get_from_dict("EMP_CHANGED")
                if not g_monitor_emps or emp_changed:
                    g_monitor_emps = Employee.objects.all()
                    g_monitor_server.set_to_dict("EMP_CHANGED", 0)
                
                if str[1] != '0':
                    pin_str = int(str[1]) and unicode(format_pin(str[1])) or ''
                    #print '----00027'
                    #print '---card_no=',card_no, pin_str
                    emps = pin_str and g_monitor_emps.get(PIN = pin_str) or '' 
                    #print "========type(emps)=-----",type(emps)
                    #print '----00028'

                else:
                    if event == 27 and card_no:#处理卡未注册(卡未注册韦根信号接反时可能也没有卡号)
                        #print "card_no========",card_no
                        #emps = g_monitor_emps.filter(Card = card_no) or ''
                        try:
                            issue_card = IssueCard.objects.get(cardno=card_no)
                            emps = issue_card.UserID
                            #print "=================================",type(emps)
                        except:
                            emps = ""
                        
                        #print "---emps=",emps
                    pin_str = emps and emps.PIN or ''
 
                #中央党校--zhangy20110718
                empname = ''
                photo = ''
                if emps:#查询不到（含数据库断开）
                    #print '-----3333333333333=',pin_str, emps[0].EName, emps[0].lastname
                    firstname = emps.EName
                    lastname = emps.lastname
                    if firstname or lastname:
                        if lastname:
                            empname = u"%s(%s %s)"%(emps.PIN, firstname, lastname) or (u"%s"%(emps.PIN))
                        else:
                            empname = u"%s(%s)"%(emps.PIN, firstname) or (u"%s"%(pin_str))
                    else:
                        empname = u"%s"%(pin_str)
                    photo = emps.photo and '/file/' + unicode(emps.photo) or ''
                
                #print '----00029'
                #print '--str[6]=',str[6]
                
                #state = int(str[4])!=2 and unicode(dict(STATE_CHOICES)[int(str[4])]) or ''#2直接显示空
                #连动视频
                if not link_video:#非联动事件
                    in_addresses = int(str[2])
                    if event not in [220, 221]:
#                        print '----00021'
                        try:
                            if not g_monitor_doors:
                                #print '--g_monitor_doors not exist=',g_monitor_doors
                                for door in AccDoor.objects.all():
                                    g_monitor_doors[door.id] = door 
                            in_addresses = g_monitor_doors[int(str[2])].door_no
                        except:
                            in_addresses = 0

                        if in_addresses:
                            linkage = AccLinkageIO.objects.filter(in_address_hide__in=[0, in_addresses]).filter(trigger_opt=event).filter(device__id=dev_id)
                            #print '---linkage=',linkage #是否唯一？
                            if linkage and linkage[0].email_address:
                                subject = "联动事件 \t"
#                                print "subject:---",subject
                                message = str[0] + "        " + alias + "       " + event_point + "     " + event_content + "       " + card_no + "     " + empname + "     " + unicode(dict(STATE_CHOICES)[int(str[4])]) + "       " + verified + "\t"
#                                print "message:---",message
                                temp_list = [subject,message,linkage[0].email_address+"\n"]
                                email_info = g_monitor_server.get_from_dict("EMAIL_INFO")
                                if not email_info:
                                    g_monitor_server.set_to_dict("EMAIL_INFO",[temp_list])
                                elif temp_list not in email_info:
                                    email_info.append(temp_list)
                                    g_monitor_server.set_to_dict("EMAIL_INFO",email_info)
#                                print "message:---",g_monitor_server.get_from_dict("EMAIL_INFO")
                                
                            if linkage and linkage[0].video_linkageio:
                                link_video.append(linkage[0].video_linkageio.device_type)#视频设备类型
                                pwd = linkage[0].video_linkageio.comm_pwd
                                link_video.append(linkage[0].video_linkageio.ipaddress)
                                link_video.append(linkage[0].video_linkageio.ip_port)
                                link_video.append(linkage[0].video_linkageio.video_login)
                                link_video.append(pwd and decryption(pwd) or "")
                                link_video.append(linkage[0].lchannel_num)
        

                #print "link_video=", link_video
                #print '---photo=',photo
                #print '----00029'
                cdata={
                    'time': str[0],
                    'card': card_no,
                    #'door': doorname,#输入点，包含门名称或者辅助输入点
                    'device': alias,#设备名称
                    'event_point': event_point,#输入点，包含门名称或者辅助输入点
                    'door_id': door_id,#doorid
                    'event_type': int(str[3]),
                    'content': event_content,
                    'state': unicode(dict(STATE_CHOICES)[int(str[4])]),#0出，1入
                    'verified': verified,
                    'emp': empname,#用户名(包含用户编号)
                    'photo': photo,#有人员照片的要显示,如/file/photo/000000121.jpg 空代表无照片（或无此人）
                    'link_video': link_video,
                }
                #print '----00030'
                cdatas.append(cdata)
            else:
                print "DATA ERROR"
        
        cc={
            'log_id': logid,
            'all_id': rtid_all,#无效
            'alarm_id': rtid_alarm,
            'log_count': log_count,#返回的有效的记录条数，用于改变logid
            'data':cdatas,
            'door_states':door_states["data"],#门状态数据
        }
        #print '----00031'
        #print "**########**cc=",cc
        rtdata = simplejson.dumps(cc)
        #print '----00032'
        return HttpResponse(smart_str(rtdata))
    except Exception, e:
        print_exc()
        print '---get rt log e=',e
        printf('----e=%s'%e, True)
        return HttpResponse(smart_str(rtdata))
    
#进行设备监控--iclock
#新增-删除设备后请先手动刷新页面
@login_required
def get_device_monitor(request):
    try:
        global g_monitor_server
        if not g_monitor_server:
            g_monitor_server = start_dict_server()
        service_enable = check_service_commcenter(g_monitor_server)

        dev_monitor_list = g_monitor_server.get_from_dict("DEV_MONITOR_LIST")
        device_added = g_monitor_server.get_from_dict("DEVICE_ADDED_MONITOR")#新增
        device_delete = g_monitor_server.get_from_dict("DEVICE_DELETE_MONITOR")#删除和编辑        
        #print '------dev_monitor_list=',dev_monitor_list
        if not dev_monitor_list or device_added or device_delete:#意味着有新增、编辑或者删除操作的（任意一个）
            #print '---monitor device not exist'
            u = request.user
            aa = u.areaadmin_set.all()
            a_limit = aa and [int(a.area_id) for a in aa] or [int(area.pk) for area in Area.objects.all()]#非超级管理员且没有配置有效区域（默认全部）的有效区域id列表（即用户手动配置过用户区域的）
            dev_monitor_list = Device.objects.filter(area__pk__in=a_limit).filter(device_type=DEVICE_ACCESS_CONTROL_PANEL).order_by('id')#当前用户授权范围内的门禁控制器
            #g_dev_monitor_list = dev_list
            g_monitor_server.set_to_dict("DEV_MONITOR_LIST", [dev for dev in dev_monitor_list])#QuerySet无法直接pickle
            if device_added:
                g_monitor_server.set_to_dict("DEVICE_ADDED_MONITOR", 0)
            if device_delete:
                g_monitor_server.set_to_dict("DEVICE_DELETE_MONITOR", 0)
            
        cdatas = []

        for dev in dev_monitor_list:
            ret = 0
            op_type = ""
            op_state = ""
            
            key = dev.command_temp_list_name()#ICLOCK_%s_TMP#
            #print '-!!!!!!!!!!!-key=',key
            ucmd = g_monitor_server.get_from_dict(key)#tmp 获取设备通讯状态
            #print '-----get device monitor =',g_monitor_server.llen_file(key)
            #print '--------get-device-monitor====ucmd====',ucmd
            q_server = queqe_server()
            #cmdcount = q_server.llen_file(dev.new_command_list_name())#新命令NEWCMDS_%scmdcount = g_monitor_server.llen(dev.new_command_list_name())#NEWCMDS_%s
            q_server.connection.disconnect()
            cntkey = dev.command_count_key()#ICLOCK_%s_CMD
            #print '---------cntkey=',cntkey
            cnt = g_monitor_server.get_from_dict(cntkey)#从缓存dict中获取命令总条数

            if cnt is None:
                cnt = "0"
            if cnt.find('\x00'):
                cnt = cnt.strip('\x00')
            try:
                cnt = int(cnt)
            except:
                cnt = 0
                
            reason = ""
            if service_enable:
                if ucmd is None:#ucmd为None代表没有其他状态
                    if not dev.enabled:#设备被禁用
                        #g_monitor_server.set_to_dict()
                        op_type = get_cmd_content("CONNECT")#
                        ret = '-1002' #警告 <-1000
                        op_state = unicode(DEVICE_COMMAND_RETURN[ret])
                        
                    else:#没有其他状态时的默认状态
                        op_type = get_cmd_content("CONNECT")#
                        ret = '1001' # 正在连接
                        op_state = unicode(DEVICE_COMMAND_RETURN[ret])
                else:
                    #print '----ucmd=',ucmd,'----type=',type(ucmd)
                    #print '---ret=',ret
                    ret = ucmd['CmdReturn']
                    op_type = get_cmd_content(ucmd['CmdContent'])
                    if ret >= 0:
                        op_state = unicode(DEVICE_COMMAND_RETURN["0"])
                    else:
                        try:
                            op_state = unicode(DEVICE_COMMAND_RETURN[str(ret)])
                        except:
                            op_state = _(u"%(f)s:错误代码%(ff)d")%{"f":DEVICE_COMMAND_RETURN["-1001"], "ff": ret}
            else:
                op_type = get_cmd_content("CHECK_SERVICE")
                ret = '-1003' #警告 <-1000
                op_state = unicode(DEVICE_COMMAND_RETURN[ret])        
                
            cdata = {
                'id':dev.id,
                'devname':dev.alias,
                'sn':dev.sn,
                'op_type':op_type,#操作类型
                'op_state':op_state,#当前操作状态
                'retmemo': reason,
                'ret': ret,
                'CmdCount':cnt,
            }
           
            cdatas.append(cdata)

        cc = {
            'data':cdatas
        }
        #g_monitor_server.close()
        #g_monitor_server.connection.disconnect()
        rtdata = simplejson.dumps(cc)
        return HttpResponse(smart_str(rtdata))
    except Exception, e:
        print '---e=',e


#设备监控中清空命令缓存的操作-darcy20110408
@login_required
def ClearCmdCache(request):
    dev_id = request.GET.get("devid", 0)
    if dev_id:
        dev = Device.objects.get(id=dev_id)
        q_server = queqe_server()
        q_server.delete_file(dev.new_command_list_name())#手动删除新命令
        q_server.connection.disconnect()

        d_server = start_dict_server()
        d_server.delete_dict(dev.command_temp_list_name())
        d_server.delete_dict(dev.command_count_key())
        d_server.close()
        return HttpResponse(smart_str({'ret':1}))
    else:
        return HttpResponse(smart_str({'ret':0}))

#界面右上角通讯失败的的判断。--darcy20110408
@login_required
def comm_error_msg(request):
    global g_monitor_server
    if not g_monitor_server:
        #print '--error--first time=',g_monitor_server
        g_monitor_server = start_dict_server()

    cdatas = []
    cc = {}
    global g_dev_comm_error_list
    if g_dev_comm_error_list:
        #print '---dev_list exist'
        dev_list = g_dev_comm_error_list
    else:
        #print '---dev_list not exist'
        dev_list = filterdata_by_user(Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL),request.user)
        g_dev_comm_error_list = dev_list
    #print '----dev_list=',dev_list, dev_list.count()
    #print '-----dev_list=', dev_list
    icount=0
    for dev in dev_list:
        if not dev.enabled:#不监控已禁用的设备
            continue
        
        key = dev.command_temp_list_name()
        ucmd = g_monitor_server.get_from_dict(key)
        if ucmd is None:
            continue
        ret = ucmd['CmdReturn']
        #print ret
        if (-400 < ret < -200) or (ret < -10000) or (ret == -1001):    
            icount += 1
            cdata = {
                'devname':ucmd['SN'].alias,
            }
            cdatas.append(cdata)
    cc={
        'cnt':icount,
        'data':cdatas,
    }
    #g_monitor_server.close()
    rtdata=simplejson.dumps(cc)
    return HttpResponse(smart_str(rtdata))

@login_required
def downdata_progress(request): #进度条后台控制
    global g_monitor_server
    if not g_monitor_server:
        g_monitor_server = start_dict_server()

    cdatas = []
    skey = request.session.session_key
    #print "downdata_progress=", skey
    cur_gress = g_monitor_server.get_from_dict("DEV_COMM_PROGRESS_%s"%skey)
    tol_gress = g_monitor_server.get_from_dict("DEV_COMM_SYNC_%s"%skey)
    if cur_gress and tol_gress:
        cur_strs = cur_gress.split(",", 2)
        tol_gress = tol_gress.split(",", 2)
        try:
            icur = int(cur_strs[1])
        except:
            icur = 0
        try:
            itol = (int(tol_gress[1])*100)/int(tol_gress[0])
        except:
            itol = 0
        cdata = {
            'dev': cur_strs[0].decode("gb18030"),
            'progress':icur,
            'tolprogress':itol,
        }
        cdatas.append(cdata)
        #g_monitor_server.close()
        cc = {
            'index': 1,
            'data': cdatas,
        }
    else:
        cdata = {
            'dev': "",
            'progress':0,
            'tolprogress':0,
        }
        cdatas.append(cdata)
        #g_monitor_server.close()
        cc = {
            'index': 0,
            'data': cdatas,
        }            
    rtdata = simplejson.dumps(cc)
    return HttpResponse(smart_str(rtdata))

# 获取某个门的状态，为了适应梯控，扩充到11个门
def get_door_state(val, doorno):
  if doorno==1:
      return (val & 0x00000000000000000000FF)
  elif doorno == 2:
      return (val & 0x000000000000000000FF00) >> 8
  elif doorno == 3:
      return (val & 0x0000000000000000FF0000) >> 16
  elif doorno == 4:
      return (val & 0x00000000000000FF000000) >> 24
  elif doorno == 5:
      return (val & 0x000000000000FF00000000) >> 32
  elif doorno == 6:
      return (val & 0x0000000000FF0000000000) >> 40
  elif doorno == 7:
      return (val & 0x00000000FF000000000000) >> 48
  elif doorno == 8:
      return (val & 0x000000FF00000000000000) >> 56
  elif doorno == 9:
      return (val & 0x0000FF0000000000000000) >> 64
  elif doorno == 10:
      return (val & 0x00FF000000000000000000) >> 72
  elif doorno == 11:
      return (val & 0xFF00000000000000000000) >> 80


#门状态监控
# state（0无门磁，1门关,2门开） alarm（1报警 2门开超时）connect(0不在线，1在线)
def door_state_monitor(dev_list, d_server):#dev_list为QuerySet---devids需为list
    service_enable = check_service_commcenter(d_server)
    #print '----dev_list=',dev_list
    cdatas = []
    global g_dev_doors#保存设备对应的门-darcy20110729中央党校项目
    for dev in dev_list:
        key = dev.get_doorstate_cache_key()
        doorstate = d_server.get_from_dict(key)
        #print 'doorstate=',doorstate
        if not dev.enabled:#设备被禁用
            vdoor = 0
            valarm = 0
            vcon = 0
            enabled = 0
            #check_enabled = d_server.get_from_dict(ACCDEVICE_DISABLED%dev.pk)#获取到False或者返回None均为未禁用（启用）
            #print '---check_enabled=',check_enabled
        #print '-!!!-doorstate=', doorstate
        elif doorstate and service_enable:#服务没有启动（含手动），前端门显示不在线
            val = doorstate.split(",", 3)
            enabled = 1
            try:
                vdoor = int(val[0])#设备中所有门的开关状态
            except:
                #print_exc()
                vdoor = 0
            try:
                valarm = int(val[1])#设备中所有门的 报警 门开超时
            except:
                #print_exc()
                valarm = 0
            try:
                vcon = int(val[2])#是否在线
            except:
                #print_exc()
                vcon = 0
        else:
            vdoor = 0
            valarm = 0
            vcon = 0
            enabled = 1

        #door = dev.accdoor_set.all()
        dev_id = dev.id
        if not g_dev_doors.has_key(dev_id):
            g_dev_doors[dev_id] = dev.accdoor_set.values_list("id","door_no")
        
        #print '---g_dev_doors=',g_dev_doors
        doors = g_dev_doors[dev_id]
        for d in doors:
            state = get_door_state(vdoor, int(d[1]))
            alarm = get_door_state(valarm, int(d[1]))
            cdata = {
                'id': int(d[0]),
                'state': int(state),
                'alarm': int(alarm),
                'connect': int(vcon),
                'enabled': enabled,
            }
            cdatas.append(cdata)
    cc={
        'data':cdatas,
    }
    #print cc
    #rtdata=simplejson.dumps(cc)
    return cc
