# -*- coding: utf-8 -*-
'''
上传用户信息：OpUpEmpInfo
远程固件升级：RemoteUpgrade
上传考勤数据：OpUpAttInfo
考勤数据校对：OpCheckAttInfo
'''
from django.conf import settings
from django.db import models
from base.operation import ModelOperation,Operation
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.models.model_emp import Employee,EmpMultForeignKey,device_pin,format_pin
#from mysite.personnel.models.model_emp import format_pin,device_pin,Employee, EmpForeignKey,EmpPoPForeignKey
from mysite.iclock.models.model_device import Device
from mysite.iclock.models.model_device import  clear_pic
from model_device import DEVICE_TIME_RECORDER ,DEVICE_ACCESS_CONTROL_PANEL ,DEVICE_ACCESS_CONTROL_DEVICE ,DEVICE_VIDEO_SERVER,DEVICE_POS_SERVER ,DEVICE_CAMERA_SERVER
from model_device import get_att_pic_path
from traceback import print_exc
import os

def append_devcmd(dev,CmdContent):
    from mysite.iclock.models import DevCmd
    import datetime
    devcmd=DevCmd(SN=dev ,CmdContent=CmdContent,CmdCommitTime=datetime.datetime.now())
    devcmd.save()

def create_att_cmd(device,StartTime,EndTime,type):
    try:
        data = None
        if type==1:
            data = 'DATA QUERY ATTLOG StartTime=%s\tEndTime=%s'%(StartTime,EndTime)
        elif type==2:
            data = 'DATA QUERY ATTPHOTO StartTime=%s\tEndTime=%s'%(StartTime,EndTime)
        elif type==3:
            data = 'VERIFY SUM ATTLOG StartTime=%s\tEndTime=%s'%(StartTime,EndTime)
        if data:
            append_devcmd(device,data)
    except:
        print_exc()    

def create_emp_cmd(device,PIN=None):
    if PIN:
        data = 'DATA QUERY USERINFO PIN=%s'%device_pin(PIN)
    else:
        data = 'DATA QUERY USERINFO'
    if data:
        append_devcmd(device,data)
    

def push_emp_cmd(emps=None,pin=None):
#    try:
        if pin:
            tmp = Employee.objects.filter(PIN__exact=pin)
            if not len(tmp)>0:
                '用户不存在'
                for dev in Device.objects.all():
                    create_emp_cmd(dev,pin)
            else:
                if emps:
                    emps = emps|tmp
                else:
                    emps = tmp
                
        if len(emps):
            for user in emps:
                attarea = user.attarea.all()#得到用户的考勤区域
                if attarea:
                    for att in attarea:
                        devs = att.device_set.all() #---得到区域里的设备
                        if devs:
                            for dev in devs:
                                create_emp_cmd(dev,user.PIN)
        elif not pin:
            for dev in Device.objects.all():
                create_emp_cmd(dev)
#    except:
#        print_exc()

def get_att_file_count():
 # 获取考勤文件夹下待解析文件数量
    import os
    cnt = 0
    path=settings.C_ADMS_PATH%u"zkatt" 
    if os.path.exists(path):
         cnt = len(os.listdir(path))
    return cnt
class OpUpEmpInfo(ModelOperation):
    help_text=_(u'''手动上传设备上的用户的基本信息(如果即没选择人员也没填写人员编号则默认从所有设备上传所有用户基本信息)''')
    verbose_name=_(u"上传用户信息")
    perm_model_menu = ['att.AttDeviceDataManage']
    
    params=(
        ('user' , EmpMultForeignKey(verbose_name=_(u'选择人员'),null=True, blank=True)),  
        ('PIN' , models.CharField(_(u'或者填写人员编号'), max_length=9,null=True, blank=True)),
    )
    def action(self, **args):
        users=[]
        users = args['user']
        print 'users:',users
        if self.request:
               depts=self.request.POST.getlist('deptIDs')
               if len(depts)>0:
                   users=Employee.objects.filter(DeptID__in=depts)
                   
        pin = None
        if len(args['PIN'])>0:
            try:
               pin = str(int(args['PIN']))
            except:
               raise Exception(_(u'人员编号只能为数字'))
            if int(args['PIN']) == 0:
                raise Exception(_(u'人员编号不能为0'))
            if len(args['PIN']) > settings.PIN_WIDTH:
                raise Exception(_(u'%(f)s 人员编号长度不能超过%(ff)s位') % {"f":args['PIN'], "ff":settings.PIN_WIDTH})
            pin = format_pin(args['PIN'])
        
        push_emp_cmd(users,pin)


DATATYPE = (
        (1, _(u'考勤记录')),
        (2, _(u'考勤照片')),
)

class OpUpAttInfo(Operation):
    help_text=_(u'''手动上传设备上指定时间段的考勤数据''')
    verbose_name=_(u"上传考勤数据")
    visible = False
    perm_model_menu = ['att.AttDeviceDataManage']
    params=(
#        ('device' , DeviceMultForeignKey(verbose_name=_(u'选择设备'))),
        ('DataType', models.IntegerField(verbose_name=_(u'数据类型'), choices=DATATYPE)),    
        ('StartTime',models.DateTimeField(_(u'开始时间'))),
        ('EndTime',models.DateTimeField(_(u'结束时间'))),
    )
    def action(self, **args):
        create_att_cmd(self.object,args['StartTime'],args['EndTime'],args['DataType'])
#        devices=args.pop('device')  
#        if self.request:
#               if not devices:
#                   depts=self.request.POST.getlist('deptIDs')
#                   devices=Device.objects.filter(area__in=depts)
#        if not devices:
#            raise Exception(_(u'请选择设备'))
#        
#        for device in devices: 
#            create_att_cmd(device,args['StartTime'],args['EndTime'],args['DataType'])
            
class OpCheckAttInfo(Operation):
    help_text=_(u'''校对服务器和设备上指定时间段的考勤数据是否一致''')
    verbose_name=_(u"考勤数据校对")
    visible = False
    perm_model_menu = ['att.AttDeviceDataManage']
    params=(
#        ('device' , DeviceMultForeignKey(verbose_name=_(u'选择设备'))),    
        ('StartTime',models.DateTimeField(_(u'开始时间'))),
        ('EndTime',models.DateTimeField(_(u'结束时间'))),
    )
    def action(self, **args):
        create_att_cmd(self.object,args['StartTime'],args['EndTime'],3)
#        devices=args.pop('device')   
#        if self.request:
#               if not devices:
#                   depts=self.request.POST.getlist('deptIDs')
#                   devices=Device.objects.filter(area__in=depts)
#        if not devices:
#            raise Exception(_(u'请选择设备'))
#        
#        for device in devices: 
#             create_att_cmd(device,args['StartTime'],args['EndTime'],3)
            
Device.OpCheckAttInfo = OpCheckAttInfo
Device.OpUpAttInfo = OpUpAttInfo
Device.OpUpEmpInfo = OpUpEmpInfo

def getFW(dev):
        ds=dev.device_name

        if not ds:
                ds=''
        else:
                ds=ds+"/"
        return ("file/remote_upgrade/%smain.gz"%ds, "%sremote_upgrade/%smain.gz"%(settings.ADDITION_FILE_ROOT,ds))

class RemoteUpgrade(Operation):
    help_text = _(u"""远程固件升级""")
    verbose_name = _(u"""远程固件升级""")
    visible = False
    perm_model_menu = ['att.AttDeviceDataManage']
    params = (
        ('upgrade_file', models.FileField(verbose_name=_(u"选择升级包文件"), blank=True, null=True)),
    )
    def action(self,upgrade_file):
        import os
        import datetime
        if not self.request.FILES.has_key('upgrade_file'):
            raise Exception(_(u"升级包文件不存在"))
        file_ = self.request.FILES['upgrade_file']
        if not file_:
            raise Exception(_(u"升级包文件不存在"))
        if file_.name[-4:] != ".tgz":
            raise Exception(_(u"文件类型错误"))
        
        dt=datetime.datetime.now()        
        dtstr='remote_upgrade/'+str(dt.year)+str(dt.month)+str(dt.day)+str(dt.hour)+str(dt.minute)+str(dt.second)+"/"
        uploadpath=settings.ADDITION_FILE_ROOT+"/"+dtstr
        try:
            os.makedirs(uploadpath)
        except: pass
        upgrade_file_path = uploadpath+file_.name
        wr=file(upgrade_file_path,"w+b",)
        data=file_.read()
        wr.write(data)
        wr.close()
        
        url = 'file/'+dtstr+file_.name
#        url,path = getFW(self.object)
        if os.path.exists(upgrade_file_path):
            cmd = "PutFile %s\t/mnt/mtdblock"%url
            append_devcmd(self.object,cmd)
        else:
            raise Exception(_(u'升级包上传失败'))
            
Device.RemoteUpgrade = RemoteUpgrade

class OpReloadData(Operation):
       help_text = _(u"重新上传数据")
       verbose_name = _(u"重新上传数据")
       perm_model_menu = ['iclock.Device','att.AttDeviceDataManage']
       params = (
               ('upload_user', models.BooleanField(verbose_name=_(u"是否上传人员信息与指纹"), blank=False, null=False,default=True)),
               ('upload_attlog', models.BooleanField(verbose_name=_(u"是否上传考勤记录"), blank=False, null=False,default=True)),
       )
       
       def __init__(self,obj):
           from mysite.iclock.iutils import stamp_to_datetime, datetime_to_stamp
           super(Device.OpReloadData,self).__init__(obj)
           if self.object.log_stamp and self.object.log_stamp != u"0" :
               self.object.att_time = stamp_to_datetime(self.object.log_stamp).strftime("%Y-%m-%d %H:%M:%S")
       def action(self,upload_user,upload_attlog):
           from mysite.iclock.iutils import stamp_to_datetime, datetime_to_stamp
           from base.sync_api import SYNC_MODEL, do_collect_device_employee, do_collect_device_att, do_collect_device_data
           att_time = self.request.POST.get("att_time","")
           if self.object.device_type == DEVICE_POS_SERVER :
               raise Exception(_(u'消费机不允许当前操作！'))
           else:
               #检查当前是否有记录待解析,否则不能执行此操作
#               from device_extend import get_att_file_count
               cnt = get_att_file_count()
               if cnt:
                  raise Exception(_(u'后台还有数据待解析,待解析文件数量%d个,解析完毕后才能执行此操作！'%cnt)) 
               if SYNC_MODEL:
                   if upload_user and upload_attlog:
                       do_collect_device_data(self.object.sn)
                   elif upload_user:
                       do_collect_device_employee(self.object.sn)
                   elif upload_attlog:
                       do_collect_device_att(self.object.sn)
                    
               else:
                   if upload_user:
                       self.object.oplog_stamp='0'
                   if upload_attlog:
                       if att_time:
                           dt_time = datetime.datetime.strptime(att_time,"%Y-%m-%d %H:%M:%S")
                           self.object.log_stamp = '%s'%datetime_to_stamp(dt_time)
                       else:
                           self.object.log_stamp = '0'
                   if upload_user and upload_attlog:
                       self.object.photo_stamp='0'
                   self.object.save(force_update=True)
                   #print "self.object.oplog_stamp",self.object.oplog_stamp
                   self.object.appendcmd("CHECK")
Device.OpReloadData =OpReloadData

class ClearTransaction(Operation):
    verbose_name = _(u"清除考勤记录")
    help_text = _(u"清除考勤记录")
    perm_model_menu = ['iclock.Device','att.AttDeviceDataManage']
    
    def action(self):
        if self.object.device_type == DEVICE_POS_SERVER :
            raise Exception(_(u'消费机不允许当前操作！'))
        else:
            from base.sync_api import SYNC_MODEL,do_clean_att
            if SYNC_MODEL:
                do_clean_att(self.object.sn)
            else:
                self.object.appendcmd("CLEAR LOG")
Device.ClearTransaction =ClearTransaction

class ClearPicture(Operation):
    verbose_name = _(u"清除考勤照片")
    help_text = _(u"清除考勤照片")
    perm_model_menu = ['iclock.Device','att.AttDeviceDataManage']
    
    def action(self):
        if self.object.device_type == DEVICE_POS_SERVER :
            raise Exception(_(u'消费机不允许当前操作！'))
        else:
            #先清除服务器上缓存的图片文件
            filepath = get_att_pic_path(self.object.sn).replace("/",os.sep)
            clear_pic(filepath)
            #给设备发送命令
            from base.sync_api import SYNC_MODEL,do_clean_attpic
            if SYNC_MODEL:
                do_clean_attpic(self.object.sn)
            else:
                self.object.appendcmd("CLEAR PHOTO")
Device.ClearPicture =ClearPicture