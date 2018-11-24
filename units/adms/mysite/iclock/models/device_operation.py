# -*- coding: utf-8 -*-
from django.conf import settings
from base.operation import ModelOperation,Operation
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
from mysite.utils import get_option 
from model_device import DEVICE_TIME_RECORDER ,DEVICE_ACCESS_CONTROL_PANEL ,DEVICE_ACCESS_CONTROL_DEVICE ,DEVICE_VIDEO_SERVER,DEVICE_POS_SERVER ,DEVICE_CAMERA_SERVER 

class Syncdata(Operation):
    #help_text = _(u"""同步所有数据主要用来将服务器中的数据同步到设备中，一般情况下只有在由于客观因素（如网络异常或其他情况）导致设备中数据和服务器不一致时才需要使用该操作。由于该操作会先将设备中的既有数据删除掉，然后同步新的数据，所以删除数据的过程势必会导致设备脱机使用受到一定程度的影响，所以建议用户使用该操作时尽量选择好时机，以免影响设备正常使用。""")
    help_text = _(u"""将服务器中的数据同步到设备中，一般情况下只有在由于客观因素（如网络异常或其他情况）导致设备中数据和服务器不一致时才需要使用该操作。""")
    verbose_name = _(u"""同步软件数据到设备""")
    perm_model_menu = ['iclock.Device','att.AttDeviceDataManage', 'pos.PosDeviceDataManage']
    only_one_object = True
    from base.sync_api import SYNC_MODEL
    def action(self):
        if get_option("POS_ID") and self.object.device_type==DEVICE_POS_SERVER:
            raise Exception(_(u'消费机不允许当前操作！'))
        else:
            #d_server = start_dict_server()
            if self.object.device_type==DEVICE_TIME_RECORDER:
                from base.sync_api import SYNC_MODEL,do_spread_device_employee
                if SYNC_MODEL:
                    do_spread_device_employee(self.object)
                else:
                    from model_cmmdata import adj_device_cmmdata,sync_for_server
                    sync_for_server(self.object,self.object.area)
            elif self.object.device_type==DEVICE_POS_SERVER:
                self.object.set_all_pos_data()
            else:    
                if not self.object.enabled:
                    raise Exception(_(u'设备已被禁用！'))
                self.object.set_all_data()#考勤门禁通用
Device.Syncdata = Syncdata

class SyncACPanelTime(Operation):
    verbose_name = _(u"""同步时间""")
    help_text = _(u"""同步设备时间为服务器时间。""")
    perm_model_menu = ['iclock.Device','pos.PosDeviceDataManage', 'iaccess.DoorSetPage','pos.PosDeviceDataManage']
    def action(self):
        if self.object.device_type == DEVICE_ACCESS_CONTROL_PANEL:
            if not self.object.enabled:
                raise Exception(_(u'设备已被禁用！'))
            self.object.set_time()
        if get_option("POS_IC") and self.object.device_type == DEVICE_POS_SERVER :
            dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            CMD="SET OPTION Time=%s\t\n"%(dt)
            self.object.appendcmd(CMD) 
        #else:
            #raise Exception(_(u"设备：%s 并非门禁控制器，该操作只能同步门禁控制器时间")%self.object.alias)
Device.SyncACPanelTime = SyncACPanelTime

class RefreshDeviceInfo(Operation):
    help_text = _(u"""获取设备信息""")
    verbose_name = _(u"""获取设备信息""")
    perm_model_menu = ['iclock.Device','att.AttDeviceDataManage','iclock.Device']
    def action(self):
        if self.object.device_type == DEVICE_POS_SERVER :
            raise Exception(_(u'消费机不允许当前操作！'))
        else:
            if self.object.device_type!=DEVICE_ACCESS_CONTROL_PANEL:
                from base.sync_api import SYNC_MODEL, do_get_info
                if SYNC_MODEL:
                    do_get_info(self.object.sn)
                else:
                    self.object.appendcmd("INFO")
Device.RefreshDeviceInfo = RefreshDeviceInfo

class Reboot(Operation):
    verbose_name = _(u"""重启设备""")
    help_text = _(u"""重启设备""")
    perm_model_menu = ['iclock.Device','att.AttDeviceDataManage', 'pos.PosDeviceDataManage']
    
    def action(self):
        if get_option("POS_ID") and self.object.device_type == DEVICE_POS_SERVER :
            raise Exception(_(u'消费机不允许当前操作！'))
        else:
            if self.object.device_type!=DEVICE_ACCESS_CONTROL_PANEL:
                from base.sync_api import SYNC_MODEL, do_reboot_device
                if SYNC_MODEL and self.object.device_type == DEVICE_TIME_RECORDER:
                    do_reboot_device(self.object.sn)
                else:
                    self.object.appendcmd("REBOOT")
            else:
                raise Exception(_(u'门禁控制器不允许当前操作！'))
Device.Reboot = Reboot