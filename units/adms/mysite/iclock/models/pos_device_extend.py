# -*- coding: utf-8 -*-
'''
下发采集命令:OpReloadICPOSData
在线采集数据：IcPosOnlineReloadData
清除消费机设置：ClearData
清除刷卡数据：ClearPosData
'''
from django.conf import settings
from django.db import models
from base.operation import ModelOperation,Operation
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.models.model_emp import Employee,EmpMultForeignKey,device_pin,format_pin
from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
from traceback import print_exc
from mysite.utils import get_option 
from mysite.sql_utils import p_query,p_execute,p_query_one

#检查设备记录流水号是否有间断的情况
def check_device_pos_log(sn):
    from mysite.pos.models.model_icconsumerlist import ICConsumerList
    check_sql = """
    select * from(
    select dev_serial_num from pos_icconsumerlist where dev_sn = '%s' and  dev_serial_num is not null 
    union all
    select dev_serial_num  from  dbo.pos_icerrorlog where dev_sn = '%s' and  dev_serial_num is not null 
    ) a group by dev_serial_num order by dev_serial_num
    """
    #    pos_data = ICConsumerList.objects.filter(dev_sn = sn,type_name__in=[6,10,9]).values_list('dev_serial_num','user_pin').order_by('dev_serial_num')
    pos_data = p_query(check_sql%(sn,sn))
    pos_data_bak = pos_data
    item = 0
    data_len = len(pos_data)
    b = pos_data[0][0]
    e = pos_data[data_len-1][0]
    err_log = []
    for i in range(b,e):
        if(i!=int(pos_data[item][0])):
            item = item-1
            err_log.append(i)
        item = item + 1
    return err_log
    
    
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
                            select dev_serial_num from 
                             (
                                 select dev_serial_num from pos_icconsumerlist where dev_sn = '%s' and  dev_serial_num is not null and pos_time> DateAdd(Month,-3,getdate())
                                 union all
                                 select dev_serial_num  from  dbo.pos_icerrorlog where dev_sn = '%s' and  dev_serial_num is not null and pos_time> DateAdd(Month,-3,getdate())
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


class OpIcDeviceDataCheck(Operation):
        help_text = _(u"当设备列表中当前设备的记录是否上传完整列显示为红色的时候，可以通过当前操作来检查设备的消费记录！")
        verbose_name = _(u"消费记录检测")
        perm_model_menu = ['iclock.Device','pos.PosDeviceDataManage']
        visible = get_option("POS_IC")
        only_one_object=True

        def action(self):
            from mysite.iclock.models.model_devcmd import DevCmd
            from mysite.pos.pos_ic.ic_sync_model import Pos_Device
            from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
            import os
            path=settings.C_ADMS_PATH%"zkpos/"
            if self.object.device_use_type != 0:
                raise Exception(_(u'当前操作只针对消费机!'))
            if pos_dev_status(self.object):
                raise Exception(_(u'当前设备的消费数据已经完整上传，操作失败!'))
            if os.path.exists(path):
                file_list = os.listdir(path)
                for file_name in file_list:
                    if file_name.split("_")[0] == self.object.sn:
                        raise Exception(_(u'当前设备的消费数据正在解析处理中，请不要重复操作!'))
            error_data = check_device_pos_log(self.object.sn)
            if error_data:
                for i in error_data:
                    cmd = "SYNC POSLOG START=%s\tEND=%s\t\n"%(i,i)
#                if len(error_data) > 100:
#                    b_g = error_data[0]
#                    e_d = error_data[-1]
#                    print "HECK ALLLOG",b_g,e_d
#                else:
#                    b_g = error_data[0]
#                    e_d = error_data[0]
#                    print "HECK ALLLOG",b_g,e_d
                    self.object.appendcmd(cmd)
                raise Exception(_(u'成功检测到%s条未上传记录，系统已自动下发获取未上传记录命令，请命令执行完之后再核对结果！')%len(error_data))
            else:
                raise Exception(_(u'当前设备的消费数据已经完整上传！'))
 
Device.OpIcDeviceDataCheck = OpIcDeviceDataCheck


class OpReloadICPOSData(Operation):
        help_text = _(u"采集设备上所有数据，包括：消费数据，补贴数据，充值.退款数据！当前操作只会下发一条采集所有数据的命令到设备，由于数据量比较大，服务器解析过程需要一定的时间，请不要重复操作！")
        verbose_name = _(u"下发采集命令")
        perm_model_menu = ['iclock.Device','pos.PosDeviceDataManage']
        visible = get_option("POS_IC")
        only_one_object=True
#        params = (
#                ('upload_pos_log', models.BooleanField(verbose_name=_(u"是否上传消费记录"), blank=False, null=False,default=False)),
#                ('upload_allow_log', models.BooleanField(verbose_name=_(u"是否上传补贴记录"), blank=False, null=False,default=False)),
#                ('upload_full_log', models.BooleanField(verbose_name=_(u"是否上传出纳记录"), blank=False, null=False,default=False)),
#                ('upload_all_log', models.BooleanField(verbose_name=_(u"重新上传所有记录"), blank=False, null=False,default=False)),
#            )
        def action(self):
            from mysite.iclock.models.model_devcmd import DevCmd
            from mysite.pos.pos_ic.ic_sync_model import Pos_Device
            from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
            import os
            cmd_obj = DevCmd.objects.filter(SN=self.object,CmdContent='CHECK ALLLOG')
            path=settings.C_ADMS_PATH%"zkpos/"
#            objpath=path%self.object.sn+"new/"

            if pos_dev_status(self.object):
                raise Exception(_(u'当前设备的消费数据已经完整上传，操作失败!'))
            if os.path.exists(path):
                file_list = os.listdir(path)
                for file_name in file_list:
                    if file_name.split("_")[0] == self.object.sn:
                        raise Exception(_(u'当前设备的消费数据正在解析处理中，请不要重复操作!'))
            if not cmd_obj:
                self.object.appendcmd("CHECK ALLLOG")
            else:
                raise Exception(_(u'设备命令重复，当前设备命令列表已经存在！'))
#            from mysite.iclock.iutils import stamp_to_datetime, datetime_to_stamp
#            if upload_all_log:
##               self.object.pos_all_log_stamp = '0'
#               self.object.pos_log_stamp = '0'
#               self.object.full_log_stamp = '0'
#               self.object.allow_log_stamp = '0'
#               self.object.appendcmd("CHECK ALLLOG")
#
#            if upload_pos_log:
#               self.object.appendcmd("CHECK POSLOG")
#            if upload_full_log:
#               self.object.appendcmd("CHECK FULLLOG")
#            if upload_allow_log:
#               self.object.appendcmd("CHECK ALLOWLOG")
#            self.object.save(force_update=True)
#            self.object.appendcmd("CHECK OPTION")  
Device.OpReloadICPOSData = OpReloadICPOSData



class ClearData(Operation):
    verbose_name = _(u"清除消费机设置")
    help_text = _(u"清除消费设备基本资料设置，不包含设备刷卡数据")
    visible = get_option("POS_IC")
    perm_model_menu = ['iclock.Device','pos.PosDeviceDataManage']
    only_one_object=True
    def action(self):
        from mysite.iclock.models.model_devcmd import DevCmd
        cmd_obj = DevCmd.objects.filter(SN=self.object,CmdContent='CLEAR DATA')
        if cmd_obj:
            raise Exception(_(u'当前设备命令列表已经存在，设备命令重复！'))
        else:
            self.object.appendcmd("CLEAR DATA")
Device.ClearData = ClearData

class IcPosOnlineReloadData(Operation):
        help_text = _(u"实时连接设备采集设备上对应的数据！注意：<开始时间>为空的时候，代表采集设备所有数据！当前操作只支持设备跟服务器处于同一网段内的部署环境，不支持夸网段实时采集！服务器解析过程需要一定的时间，请不要重复操作！")
        perm_model_menu = ['iclock.Device','pos.PosDeviceDataManage']
        verbose_name = _(u"在线采集数据")
        visible = get_option("POS_IC")
        only_one_object=True
        params = (
                ('start_time',models.DateTimeField(_(u'设备记录开始时间'),blank=True, null=True)),
#                ('end_time',models.DateTimeField(_(u'在线采集结束时间'),blank=True, null=True)),
                ('upload_pos_log', models.BooleanField(verbose_name=_(u"在线采集消费记录"), blank=False, null=False,default=True)),
                ('upload_allow_log', models.BooleanField(verbose_name=_(u"在线采集补贴记录"), blank=False, null=False,default=False)),
                ('upload_full_log', models.BooleanField(verbose_name=_(u"在线采集出纳记录"), blank=False, null=False,default=False)),
            )
        def action(self,upload_pos_log,upload_full_log,upload_allow_log,start_time):
            from mysite.iclock.models.model_devcmd import DevCmd
            from mysite.pos.pos_ic.ic_sync_model import Pos_Device
            from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
            from mysite.pos.pos_utils import online_getdata
            import os
            if start_time:
                st = start_time.strftime("%Y%m%d%H%M%S")
#            if end_time:
#                et = end_time.strftime("%Y%m%d%H%M%S")
            path=settings.C_ADMS_PATH%"zkpos/"
#            objpath=path%self.object.sn+"new/"
            device=Pos_Device(self.object.sn)
            try:
                pos_device=device.get()
            except PosDeviceDoesNotExist:
                raise Exception(_(u'无效设备'))
#            request = 'http://192.168.10.192/data/?Action=Query&Table=PosLog&Fields=*&Filter='
            if upload_pos_log:
                data_type = "POSLOG"
                if start_time:
                    data_url = "http://%s/data/?Action=Query&Table=PosLog&Fields=*&Filter=PosTime>%s"%(str(self.object.ipaddress),st)
                else:
                    data_url = "http://%s/data/?Action=Query&Table=PosLog&Fields=*&Filter="%str(self.object.ipaddress)
            if upload_full_log:
                data_type = "FULLLOG"
                if start_time:
                    data_url = "http://%s/data/?Action=Query&Table=FullValue&Fields=*&Filter=Suptime>%s"%(str(self.object.ipaddress),st)
                else:
                    data_url = "http://%s/data/?Action=Query&Table=FullValue&Fields=*&Filter="%str(self.object.ipaddress)
                    
            if upload_allow_log:
                data_type = "ALLOWLOG"
                if start_time:
                    data_url = "http://%s/data/?Action=Query&Table=SidyLog&Fields=*&Filter=AllowTime>%s"%(str(self.object.ipaddress),st)
                else:
                    data_url = "http://%s/data/?Action=Query&Table=SidyLog&Fields=*&Filter="%str(self.object.ipaddress)
            if not self.object.show_status():
                raise Exception(_(u'当前设备不在线，操作失败!'))
            if pos_dev_status(self.object):
                raise Exception(_(u'当前设备的消费数据已经完整上传，操作失败!'))
            if os.path.exists(path):
                file_list = os.listdir(path)
                for file_name in file_list:
                    f_list =  file_name.split("_")
                    if f_list[0] == self.object.sn and len(f_list)== 3 and f_list[2].split(".")[0] == data_type:
                        raise Exception(_(u'当前实时采集的数据正在解析处理中，请不要重复操作!'))
            
            return_value,data_count = online_getdata(self.object,data_url,data_type)
            if return_value== "SN_FAIL":
                raise Exception(_(u'设备序列号验证失败，请检查IP地址是否为目标设备的IP!'))
            elif return_value== "CONTENT_FAIL":
                raise Exception(_(u'联机失败,请联系网络管理员，确认IP地址是否设置准确。（当前操作不支持跨网段采集！）'))
            elif return_value== "OK":
                raise Exception(_(u'设备数据已经成功采集到服务器！剩余%s条记录等待服务器解析!')%data_count)
            elif return_value== "FAIL":
                raise Exception(_(u'数据采集失败！请检测网络是否畅通！'))
            elif return_value== "NO_DATA":
                raise Exception(_(u'当前设备没有数据可采集！'))
Device.IcPosOnlineReloadData = IcPosOnlineReloadData



class ClearPosData(Operation):
        help_text = _(u"当前操作会将消费设备里面对应的数据清除掉,清除之前请同步设备数据！")
        verbose_name = _(u"清除刷卡数据")
        perm_model_menu = ['iclock.Device','pos.PosDeviceDataManage']
        visible = get_option("POS_IC")
        only_one_object=True
        params = (
                ('clear_pos_log', models.BooleanField(verbose_name=_(u"是否清除消费刷卡记录"), blank=False, null=False,default=False)),
                ('clear_allow_log', models.BooleanField(verbose_name=_(u"是否清除补贴刷卡记录"), blank=False, null=False,default=False)),
                ('clear_full_log', models.BooleanField(verbose_name=_(u"是否清除出纳刷卡记录"), blank=False, null=False,default=False)),
#                ('clear_store_detail', models.BooleanField(verbose_name=_(u"是否清除商品消费明细记录"), blank=False, null=False,default=False)),
#                ('clear_key_detail', models.BooleanField(verbose_name=_(u"是否清除键值消费明细记录"), blank=False, null=False,default=False)),
#                ('clear_time_detail', models.BooleanField(verbose_name=_(u"是否清除计时消费明细记录"), blank=False, null=False,default=False)),
        )
        def action(self,clear_pos_log,clear_allow_log,clear_full_log):
            from mysite.iclock.iutils import stamp_to_datetime, datetime_to_stamp
            from mysite.pos.pos_ic.ic_sync_model import Pos_Device
            if get_option("POS_ID"):
                raise Exception(_(u'消费机不允许当前操作！'))
            device=Pos_Device(self.object.sn)
            try:
                pos_device=device.get()
            except PosDeviceDoesNotExist:
                raise Exception(_(u'无效设备'))
            if pos_device.pos_dev_data_status.lower()=="false" or not pos_dev_status(self.object):
                raise Exception(_(u'当前设备的消费数据没有完整上传，操作失败!'))
            elif self.object.device_type == DEVICE_POS_SERVER:
                if clear_pos_log:
                   self.object.appendcmd("CHECK POSLOG")
                   self.object.appendcmd("CLEAR POSLOG")
                if clear_full_log:
                   self.object.appendcmd("CHECK FULLLOG")
                   self.object.appendcmd("CLEAR FULLVALUE")
                if clear_allow_log:
                   self.object.appendcmd("CHECK ALLOWLOG")
                   self.object.appendcmd("CLEAR SIDYLOG")
#                if clear_store_detail:
#                   self.object.appendcmd("CLEAR PAYDETAIL")
#                if clear_key_detail:
#                   self.object.appendcmd("CLEAR KEYDETAIL")
#                if clear_time_detail:
#                   self.object.appendcmd("CLEAR TMPOS")
#                   self.object.appendcmd("CLEAR TMPOSLOG")
Device.ClearPosData = ClearPosData