# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from base.operation import ModelOperation,Operation
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models.model_device import Device
from mysite.utils import get_option
from django import forms
from model_dstime import DSTime
from model_device import DEVICE_TIME_RECORDER ,DEVICE_ACCESS_CONTROL_PANEL ,DEVICE_ACCESS_CONTROL_DEVICE ,DEVICE_VIDEO_SERVER,DEVICE_POS_SERVER ,DEVICE_CAMERA_SERVER 
from model_device import MAX_COMMAND_TIMEOUT_SECOND
from redis_self.server import queqe_server, start_dict_server
from traceback import print_exc

#启用PUSH功能-darcy20110831
class OpEnableAccPush(Operation):
    verbose_name = _(u"""启用PUSH功能""")
    help_text = _(u"""启用PUSH功能""")
    visible = False

    def action(self):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            ret = self.object.set_acc_push_params(enable=1)
            if ret >= 0:
                self.object.accdevice.iclock_server_on = 1
                self.object.accdevice.save(force_update=True)
                d_server = start_dict_server()
                d_server.set_to_dict(ACCDEVICE_PUSH_ON%self.object.sn, 1)
                d_server.close()
                raise Exception(_(u"操作成功！"))
            else:
                raise Exception(_(u"操作失败！"))
Device.OpEnableAccPush = OpEnableAccPush


#启用区域反潜-darcy20110831
class OpEnableAccGAPB(Operation):
    verbose_name = _(u"""启用区域反潜""")
    help_text = _(u"""启用区域反潜""")
    visible = False

    def action(self):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            if not self.object.accdevice.iclock_server_on:
                raise Exception(_(u"该设备未启用PUSh功能！")) 
            ret = self.object.set_acc_gapb(enable=1)
            if ret >= 0:
                self.object.accdevice.global_apb_on = 1
                self.object.accdevice.save(force_update=True)
                raise Exception(_(u"操作成功！"))
            else:
                raise Exception(_(u"操作失败！"))
Device.OpEnableAccGAPB = OpEnableAccGAPB

#禁用区域反潜-darcy20110831
class OpDisableAccGAPB(Operation):
    verbose_name = _(u"""禁用区域反潜""")
    help_text = _(u"""禁用区域反潜""")
    visible = False

    def action(self):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            if not self.object.accdevice.iclock_server_on:
                raise Exception(_(u"该设备未启用PUSh功能！"))
            ret = self.object.set_acc_gapb(enable=0)
            if ret >= 0:
                self.object.accdevice.global_apb_on = 0
                self.object.accdevice.save(force_update=True)
                raise Exception(_(u"操作成功！"))
            else:
                raise Exception(_(u"操作失败！"))
Device.OpDisableAccGAPB = OpDisableAccGAPB

class OpChangeMThreshold(Operation):
    verbose_name = _(u"""修改指纹比对阈值""")
    help_text = _(u"""修改设备中进行指纹比对时的阈值。请首先确认当前设备是否支持指纹。""")
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    params = (
        ('threshold', models.IntegerField(_(u"指纹比对阈值"), null=True, blank=False, max_length=3, help_text=_(u'(范围35-70)'))),
    )
    #非紧急命令
    def action(self, threshold):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            #print '--self.object.accdevice.IsOnlyRFMachine=',self.object.accdevice.IsOnlyRFMachine                
            if self.object.accdevice.IsOnlyRFMachine == 1:#为仅卡 后续支持其他类型设备时，此处需修改
                raise Exception(_(u"当前设备不支持指纹！"))
            if threshold > 70 or threshold < 35:
                raise Exception(_(u"指纹比对阈值范围为35-70！"))
            if threshold != self.object.fp_mthreshold:#相等直接返回，不重复下
                self.object.fp_mthreshold = threshold
                self.object.save(force_update=True)
                self.object.set_mthreshold(threshold)
Device.OpChangeMThreshold = OpChangeMThreshold

class OpChangeElevatorParamters(Operation):
    verbose_name = _(u"""配置电梯控制器参数""")
    help_text = _(u"""配置电梯的刷卡间隔、按键有效时长及电梯按键常开时间段""")
    visible = False
    params = (
        ('interval_swip_card', models.IntegerField(_(u"刷卡间隔"), null=True, blank=False, max_length=3, help_text=_(u'(范围35-70)'))),
        ('keepkeyopen_time', models.IntegerField(_(u"按键有效时长"), null=True, blank=False, max_length=3, help_text=_(u'(范围35-70)'))),
        #('elevator_normallyopen_time', models.ForeignKey(AccTimeSeg, verbose_name=_(u'电梯常开时间段'))),
    )
    def action(self, interval_swip_card, keepkeyopen_time):
        if self.object.is_elevator == ACPANEL_AS_ELEVATOR:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            save_elevatorsettings_todb(self.object,interval_swip_card, keepkeyopen_time)
            self.object.set_elevator_params(interval_swip_card, keepkeyopen_time)
Device.OpChangeElevatorParamters = OpChangeElevatorParamters

#    #修改设备波特率--仅对门禁控制器有效，其他无效--darcy20111014
#    class OpChangeBaudrate(Operation):
#        verbose_name = _(u"""修改波特率""")
#        help_text = _(u"""修改波特率""")
#    
#        params = (
#            ('baudrate', models.SmallIntegerField(_(u"波特率"), null=True, blank=True, max_length=6, default=2, choices=BAUDRATE_CHOICES)),
#        )
#        #紧急命令
#        def action(self, baudrate):
#            if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
#                if not self.object.enabled:
#                    raise Exception(_(u'设备已被禁用！'))
#                
#                #print '-----baudrate=',baudrate
#                ret = self.object.set_acc_baudrate(dict(BAUDRATE_CHOICES)[baudrate])
#                if ret >= 0:#
#                    self.object.baudrate = baudrate
#                    self.object.save(force_update=True)
#                else:
#                    raise Exception(_(u'操作失败！'))
#    Device.OpChangeBaudrate = OpChangeBaudrate
class OpCloseAuxOut(Operation):
    verbose_name = _(u"""关闭辅助输出""")
    help_text = _(u"""该操作只对当前打开的辅助输出点有效，如果选择的辅助输出点是关闭的，那么该操作无效。""")
    only_one_object = True
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    def action(self):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            from dev_comm_operate import save_operate_cmd
            save_operate_cmd("DATA SET output")#写入操作日志
            auxout = self.request.POST.getlist("auxout")#选择全部时，该值为空
            #print '---auxout=',auxout

            for aux in auxout:
                CMD = "DEVICE SET %d 2 0" % int(aux)#最后一个0表示关  ControlDevice(self.hcommpro, 1, doorid, index, state, 0 , "")
                self.object.appendcmdreturn(CMD, MAX_COMMAND_TIMEOUT_SECOND)
Device.OpCloseAuxOut = OpCloseAuxOut               
                
class OpUpgradeFirmware(Operation):
    verbose_name = _(u"""升级固件""")
    help_text = _(u"""升级设备中的固件。""")
    only_one_object = True
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    params = (
        ('firmware_file', models.FileField(verbose_name=_(u"选择目标文件"), blank=True, null=True)),#, max_length=80  forms
    )

    def action(self, firmware_file):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:#门禁
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            
            if not self.request.FILES.has_key('firmware_file'):
                raise Exception(_(u"目标文件不存在"))

            file = self.request.FILES['firmware_file']
            if not file:
                raise Exception(_(u"目标文件不存在"))
            if file.name != "emfw.cfg":
                raise Exception(_(u"目标文件名错误"))
            #for chunk in file.chunks():
                #buffer.write(chunk)
            buffer = file.read()
            from mysite.iaccess.devcomm import TDevComm
            devcomm = TDevComm(self.object.getcomminfo())
            d_server = None
            service_running = True#门禁后台服务

            from mysite.iaccess.dev_comm_center import check_service_commcenter
            d_server = start_dict_server()
            #print '--------before wait_com_pause'
            service_running = check_service_commcenter(d_server)
            if service_running:
                if self.object.comm_type == COMMU_MODE_PULL_RS485:#485通讯
                    from mysite.iaccess.dev_comm_center import wait_com_pause
                    if wait_com_pause(d_server, self.object.com_port, 60) == False: #等待后台停止进程
                        #print '------wait_com_pause failed'
                        d_server.close()
                        raise Exception(_(u"升级固件失败，原因：后台串口进程忙"))
                    else:
                        os.system("taskkill /im plrscagent.* /f")
                elif self.object.comm_type == COMMU_MODE_PULL_TCPIP:
                    from mysite.iaccess.dev_comm_center import wait_thread_pause
                    if wait_thread_pause(d_server, self.object.id, 60) == False: #等待后台停止进程
                        #print '------wait_com_pause failed'
                        d_server.close()
                        raise Exception(_(u"升级固件失败，原因：后台设备线程忙"))

            cret = devcomm.connect()
            #print '----cret = ',cret
            #print '------after connect the device cret=',cret

            if cret['result'] > 0:
                #print '----before upgrade_firmware'
                ret = devcomm.upgrade_firmware(file.name, buffer, file.size)
                #print '---after upgrade firmware'
                #无论成功与否，先让后台进程继续
                if self.object.comm_type == COMMU_MODE_PULL_RS485 and service_running:
                    from mysite.iaccess.dev_comm_center import set_comm_run
                    #print '-set_comm_run-=',set_comm_run
                    set_comm_run(d_server, self.object.com_port) #后台进程继续
                elif self.object.comm_type == COMMU_MODE_PULL_TCPIP and service_running:
                    from mysite.iaccess.dev_comm_center import set_thread_run
                    #print '---set_thread_run time=',datetime.datetime.now()
                    set_thread_run(d_server, self.object.id) #后台线程继续
                d_server.close()

                if ret['result'] >= 0:#
                    devcomm.reboot()
                    devcomm.disconnect()
                    raise Exception(_(u"<font color='blue'>操作成功</font>"))
                else:
                    devcomm.disconnect()
                    raise Exception(_(u"升级固件失败，错误码：%d") % ret['result'])
            else:

                from mysite.iaccess.dev_comm_center import DEVICE_COMMAND_RETURN
                #print '----connect failed'
                try:
                    reason = unicode(dict(DEVICE_COMMAND_RETURN)[str(cret["result"])])
                    raise Exception(_(u"连接设备失败（原因：%s），无法升级固件。") % reason)
                except:
                    raise Exception(_(u"设备连接失败（错误码：%d），无法升级固件。") % cret['result'])
Device.OpUpgradeFirmware = OpUpgradeFirmware

class UploadLogs(Operation):
    verbose_name = _(u"""获取事件记录""")
    help_text = _(u"""获取设备中的事件记录到服务器中。""")
    only_one_object = True
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    visible = get_option("IACCESS")
    params = (
            ('get_records', forms.ChoiceField(label=_(u"获取事件记录"), choices=(("1", _(u"获取新记录")), ("0", _(u"获取所有记录")), ("2", _(u"通过SD卡获取记录"))), widget=forms.RadioSelect(), initial="1")),
            ('sd_file', models.FileField(verbose_name=_(u"选择目标文件"), blank=True, null=True))
    )

    def action(self, get_records, sd_file):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            
            from mysite.iaccess.devcomm import TDevComm
            from mysite.iaccess.dev_comm_center import process_event_log
            #获取事件记录时先检查数据中心是否开启                
            d_server = start_dict_server()                
            if not d_server.get_from_dict("CENTER_RUNING"):                    
                ret = -1003                    
                raise Exception(_(u"获取事件记录失败，错误码：%s")%ret)                
            d_server.close()                                
            if get_records == "1":
               ret = self.object.upload_acclog(True)
            elif get_records == "2":
               if not self.request.FILES.has_key('sd_file'):
                   raise Exception(_(u"请选择目标文件"))
               file = self.request.FILES['sd_file']
               if not file:
                   raise Exception(_(u"目标文件不存在"))
#                   try:
#                       if not file.name.endswith(".dat"):
#                           raise Exception(_(u"目标文件格式错误"))
#                   except:
#                       raise Exception(_(u"目标文件格式错误"))
               file_buffer = file.read()
               tdev = TDevComm({})
               result = tdev.get_transaction("SD", file_buffer, file.size)
               ret = result["result"]
               sn = result["data"][0].split(',')[0]
               if sn != self.object.sn:
                   raise Exception(_(u"当前文件里的记录不属于该设备！")) 
               #result["data"].pop(0)
               process_event_log(self.object, result)
            else:
               ret = self.object.upload_acclog(False)
            if ret >= 0:
               raise Exception(_(u"<font color='blue'>获取事件记录成功，共 %d 条</font>") % ret)
            else:
               raise Exception(_(u"获取事件记录失败，错误码：%s")%ret)
Device.UploadLogs=UploadLogs

#    #暂只有门禁使用
#    class OpGetMoreOptions(Operation):
#        verbose_name = _(u"""获取更多参数""")
#        help_text = _(u"""获取设备中的更多参数。""")
#        only_one_object = True
#
#        def action(self):
#            pass
#    Device.OpGetMoreOptions=OpGetMoreOptions

class UploadUserInfo(Operation):
    verbose_name = _(u"""获取人员信息""")
    if not get_option("IACCESS_5TO4"):
        help_text = _(u"""重新获取设备中当前的人员基本信息和指纹数据。""")
    else:
        help_text = _(u"""重新获取设备中当前的人员基本信息。""")
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']

    def action(self):
        from django.db import connection
        from mysite.iaccess import sqls
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            try:
                if not self.object.enabled:                        
                    raise Exception(_(u'设备已被禁用！'))                                        
                dev_id = self.object.id
                user_count = self.object.upload_user_info_template("user")
                if user_count == None:
                    user_count = -1
                if self.object.accdevice.IsOnlyRFMachine == 0:
                    fp_count  = self.object.upload_user_info_template("templatev10")
                    #face_count  = self.object.upload_user_info_template("FACE")
                    if fp_count == None:
                        fp_count = -1 
#                        if face_count == None:
#                            face_count = -1
                    if user_count >= 0 and fp_count < 0:
                        raise Exception(_(u"获取人员基本信息成功，但获取人员指纹数据失败！"))
                    elif user_count < 0 and fp_count >= 0:
                        raise Exception(_(u"获取人员指纹数据成功，但获取人员基本信息失败！"))
                    elif user_count < 0 and fp_count < 0:
                        raise Exception(_(u"获取人员基本信息和指纹数据均失败！"))    
#                        elif face_count < 0:
#                            raise Exception(_(u"获取人脸模板数据均失败！"))
                    else:
                        cursor = connection.cursor()
#                            sql = 'update iclock set user_count=%s,fp_count=%s,face_count=%s where id=%s'%(user_count, fp_count, face_count,dev_id)
                        #sql = 'update iclock set user_count=%s,fp_count=%s where id=%s'%(user_count, fp_count, dev_id)
                        sql=sqls.UploadUserInfoz_update(user_count,dev_id,fp_count)
                        cursor.execute(sql)
                        connection._commit()
                        connection.close()
                else:
                    if user_count < 0:
                        raise Exception(_(u"获取人员信息失败！"))  
                    else:
                        cursor = connection.cursor()
                        #sql = 'update iclock set user_count=%s where id=%s'%(user_count, dev_id)
                        sql=sqls.UploadUserInfoz_update(user_count, dev_id,None)
                        cursor.execute(sql)
                        connection._commit()
                        connection.close()
            except:#None不能比较
                print_exc()
                raise Exception(_(u"获取人员信息失败！"))
Device.UploadUserInfo=UploadUserInfo

class OpSearchACPanel(ModelOperation):
    verbose_name = _(u'''搜索门禁控制器''')
    help_text = _(u"搜索局域网内存在的门禁控制器。")
    perm_model_menu = ['iclock.Device']
    
    def action(self, **kwargs):
        pass
Device.OpSearchACPanel=OpSearchACPanel

class OpDisableDevice(Operation):
    verbose_name = _(u'''禁用''')
    help_text = _(u"设备禁用后在重新启用前将无法使用。")
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    visible = get_option("IACCESS")
    def action(self, **kwargs):
        d_server = start_dict_server()
        self.object.set_dev_disabled(d_server)
        d_server.close()
Device.OpDisableDevice=OpDisableDevice

class OpEnableDevice(Operation):
    verbose_name = _(u'''启用''')
    help_text = _(u"启用设备后设备将恢复正常的使用状态。")
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    visible = get_option("IACCESS")
    def action(self, **kwargs):
        d_server = start_dict_server()
        self.object.set_dev_enabled(d_server)
        d_server.close()
Device.OpEnableDevice=OpEnableDevice

class ResetPassword(Operation):
    verbose_name = _(u"""修改通讯密码""")#门禁控制器设备
    help_text = _(u"""最多15位字符，空值代表取消通讯密码。修改成功后服务器将会自动将软件中的密码同步为新的密码。""")
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    params=(
        ('commkey', forms.CharField(label=_(u"新密码"), required=False, widget=forms.PasswordInput, max_length=15)),
        ('commkey_again', forms.CharField(label=_(u"确认密码"), required=False, widget=forms.PasswordInput, max_length=15)),
    )
    only_one_object=True

    def action(self, commkey, commkey_again):
        if not self.object.enabled:
            raise Exception(_(u'设备已被禁用！'))
        for key in commkey:
            if key == ' ':
                return Exception(_(u'设备通讯密码不能包含空格！'))

        if commkey != commkey_again:
            raise Exception(_(u'两次输入密码不一致,请重新输入！'))

        ret = self.object.set_commkey(commkey)
        if ret >= 0:#?
            dev_info = self.object.getdevinfo()
            self.object.comm_pwd = commkey
            self.object.save(force_update=True)
            from mysite.iaccess.dev_comm_center import OPERAT_EDIT
            #self.object.add_comm_center(dev_info, OPERAT_EDIT)
            #raise Exception(_(u'操作成功！'))
        else:
            raise Exception(_(u'操作失败！'))
Device.ResetPassword=ResetPassword

class OpChangeIPOfACPanel(Operation):
    verbose_name = _(u"""修改IP地址""")
    help_text = _(u"""修改设备IP地址，每次只能修改一台设备。修改成功后服务器将会自动将软件中的设备IP地址同步为新的IP地址。""")#门禁控制器设备
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    params=(
        ('newip', forms.CharField(label=_(u"输入新的IP地址"), widget=forms.TextInput, max_length=20)),
        ('subnet_mask', forms.CharField(label=_(u"输入子网掩码"), widget=forms.TextInput, max_length=20)),#, default="255.255.255.0"
        ('gateway', forms.CharField(label=_(u"输入网关地址"), widget=forms.TextInput, max_length=20)),
    )
    only_one_object=True

    def action(self, newip, gateway, subnet_mask):
        #print 'newip=',newip
        #print 'ip=',self.object.ipaddress
        #print 'ip=',self.object.ipaddress
        if not self.object.enabled:
            raise Exception(_(u'设备已被禁用！'))
        ret = self.object.set_ipaddress(newip, gateway, subnet_mask, 10)#发送指令10秒后使用新IP试连接

        if ret >= 0:
            dev_info = self.object.getdevinfo()
            self.object.alias = newip
            self.object.ipaddress = newip
            self.object.subnet_mask = subnet_mask
            self.object.gateway = gateway
            self.object.save(force_update=True)
            from mysite.iaccess.dev_comm_center import OPERAT_EDIT
            #self.object.add_comm_center(dev_info, OPERAT_EDIT)#设备的save中已经处理过。-darcy20120221
            #raise Exception(_(u'操作成功！'))
        else:
            raise Exception(_(u'操作失败！'))
Device.OpChangeIPOfACPanel=OpChangeIPOfACPanel

class OpSetDSTime(Operation):    #仅门禁使用
    verbose_name = _(u"""启用夏令时""")
    help_text = _(u"""给设备设置夏令时，每次可以同时对多台设备进行设置，修改成功后服务器将会自动同步到选中设备当中。""")
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    visible = get_option("IACCESS")
    params = (
        ('dstime', models.ForeignKey(DSTime, verbose_name=_(u"夏令时"))),
    )
    def action(self, dstime):
        if not self.object.enabled:
            raise Exception(_(u'设备已被禁用！'))
        ret = self.object.set_dstime(dstime)
        if ret >= 0:
            dev_info = self.object.getdevinfo()
            self.object.dstime = dstime
            self.object.save(force_update=True)
            from mysite.iaccess.dev_comm_center import OPERAT_EDIT
            self.object.add_comm_center(dev_info, OPERAT_EDIT)
        else:
            raise Exception(_(u'操作失败！'))
Device.OpSetDSTime=OpSetDSTime

class OpRemoveDSTime(Operation):    #仅门禁使用
    verbose_name = _(u'''禁用夏令时''')
    help_text = _(u'''禁用夏令时''')
    perm_model_menu = ['iclock.Device','iaccess.DoorSetPage']
    visible = get_option("IACCESS")
    def action(self, **kwargs):
        if not self.object.enabled:
            raise Exception(_(u'设备已被禁用！'))
        if self.object.dstime == None:
            raise Exception(_(u'该设备未启用夏令时！'))
        ret = self.object.set_dstime_disable()
        if ret >= 0:
            dev_info = self.object.getdevinfo()
            self.object.dstime = None
            self.object.save(force_update=True)
            from mysite.iaccess.dev_comm_center import OPERAT_EDIT
            self.object.add_comm_center(dev_info, OPERAT_EDIT)
        else:
            raise Exception(_(u'操作失败！'))
Device.OpRemoveDSTime=OpRemoveDSTime
