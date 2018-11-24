#! /usr/bin/env python
#coding=utf-8

from base.models import AppOperation
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _

from mysite.personnel.models.model_emp import format_pin,device_pin,Employee, EmpForeignKey,EmpPoPForeignKey,EmpMultForeignKey
from mysite.iclock.models.model_device import Device,DevicePoPForeignKey
import datetime
from traceback import print_exc
from mysite.utils import get_option


def get_user_device(user):
    '''根据用户得到用户所在的所有设备'''
    try:
        attarea = user.attarea.all()#得到用户的考勤区域
        user_devs =[]
        if attarea:
            for att in attarea:
                devs = att.device_set.all() #---得到区域里的设备
                if devs:
                    for dev in devs:
                        user_devs.append(dev)
        return user_devs
    except:
        print_exc()

def append_devcmd(dev,CmdContent):
    from mysite.iclock.device_http.sync_action import _device_cmd
    _device_cmd(dev.sn,CmdContent)
#    from mysite.iclock.models import DevCmd
#    import datetime
#    devcmd=DevCmd(SN=dev ,CmdContent=CmdContent,CmdCommitTime=datetime.datetime.now())
#    devcmd.save()
    
def sync_set_notice(code,context,startdatetime,min,user=None,device=None):
    data = "DATA UPDATE SMS MSG=%s\tTAG=%s\tUID=%s\tMIN=%s\tStartTime=%s"%(context,user and '254' or '253',code,min,startdatetime)
    try:
        if user:
            user_data = "DATA UPDATE USER_SMS PIN=%s\tUID=%s"%(device_pin(user.PIN),code)
            device_list = get_user_device(user) #---得到用户对应的设备
            if device_list:
                for dev in device_list:
                    append_devcmd(dev,data)
                    append_devcmd(dev,user_data)
            else:
                pass
        elif device:
            append_devcmd(device,data)
    except:
        print_exc() 
        
def sync_del_notice(notice_id,user=None,device=None):
    data = 'DATA DELETE SMS UID=%d\t'%notice_id
    try:
        if user:
            device_list = get_user_device(user) #---得到用户对应的设备
            if device_list:
                for dev in device_list:
                    append_devcmd(dev,data)
        elif device:
            append_devcmd(device,data)
    except:
        print_exc()         
    
 
BIANHAO=(
(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),
(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20),
)
YESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),

)

#短消息 模型
class Notice(CachingModel):
    id =models.AutoField(verbose_name=_(u'编号'),primary_key=True, null=False, editable=False)
    context=models.TextField(verbose_name=_(u'短消息内容'),max_length=320)
    starttime=models.DateTimeField(_(u'开始时间'),null=True)
    lasttime = models.IntegerField(verbose_name=_(u'短消息持续时间(分)'), max_length=20,default=60)
    device = DevicePoPForeignKey(verbose_name=_(u'设备'),db_column='DeviceID',null=True, blank=True,editable=False)    
    user = EmpPoPForeignKey(verbose_name=_(u'人员'), db_column='UserID',null=True, blank=True,editable=False)  
    isset =  models.IntegerField(_(u'是否下发'),choices=YESORNO,default=0,editable=False)
    
    def __unicode__(self):
        return u"短消息(ID:%s)"%self.id
    
    def save(self, **args):
        self.context = self.context.replace('\r','').replace('\n','').replace('\t','')
        clen = len(self.context.encode('ascii','ignore'))
        tlen = clen+(len(self.context)-clen)*2
        if tlen>320:
            raise Exception(_(u'短消息内容不能超过320个字符'))
        
        super(Notice, self).save(**args)
        
    def delete(self, **args):
        sync_del_notice(self.id,user=self.user,device=self.device)
        super(Notice, self).delete()
            
    class _add(ModelOperation):
        visible=False
        help_text=_(u"新增记录") #新增记录
        verbose_name=_(u"新增")
        def action(self):
            pass
                
#    class OpAddUserMsg(ModelOperation):
#        help_text=_(u'''新增对私信息''')
#        verbose_name=_(u"新增对私公告")
#        params=(
##            ('device' , DeviceMultForeignKey(verbose_name=_(u'设备'),db_column='DeviceID',null=False, blank=False)),    
#            ('user' , EmpMultForeignKey(verbose_name=_(u'人员'), db_column='UserID',null=True, blank=True)),  
#            ('context', models.TextField(verbose_name=_(u'公告内容'),max_length=320)),
#            ('starttime', models.DateTimeField(_(u'开始时间'),null=True)),
#            ('lasttime', models.IntegerField(verbose_name=_(u'公告持续时间(分)'), max_length=20,default=60)),
#        )
#        def action(self, **args):
#            users=args.pop('user')   
#            if self.request:
#                   if not users:
#                       depts=self.request.POST.getlist('deptIDs')
#                       users=Employee.objects.filter(DeptID__in=depts)
#            if not users:
#                raise Exception(_(u'请选择人员'))
#            for user in users: 
#                Notice(user=user, **args).save()         
        
    class AddCmd(Operation):
        help_text = _(u"""把信息下发到设备中去""")
        verbose_name = _(u'短消息下发')
        def action(self):
            starttime=self.object.starttime.strftime("%Y-%m-%d %H:%M:%S")
            users = self.object.user
            devices = self.object.device
            if users:
                sync_set_notice(self.object.id,self.object.context,starttime,self.object.lasttime,user=users)
            if devices:
                sync_set_notice(self.object.id,self.object.context,starttime,self.object.lasttime,device=devices)
            aa=self.object
            aa.isset=1
            aa.save()
            
    def get_area(self):
        return u",".join([a.areaname for a in self.area.all()])
    def get_user(self):
        
        return u",".join([u.EName for u in self.user.all()])
    
    class Admin(CachingModel.Admin):    #管理该模型
        sort_fields=['id','starttime']      #需要排序的字段，放在列表中
        menu_group = 'personnel'          #在哪个app应用下
        menu_index=5               #菜单的摆放的位置
        list_display = ['starttime','lasttime','isset','context','user.PIN']
        
        query_fields=['device__sn','user__PIN','user__EName']      #需要查找的字段
        adv_fields=list_display
        visible = get_option("NOTICE_VISIBLE")
    class Meta:
        verbose_name=_(u'设备短消息')#名字
        verbose_name_plural=verbose_name
        app_label=  'iclock' #属于哪个app
    

class OpAddDeviceMsg(Operation):
    help_text=_(u'''新增对公短消息''')
    verbose_name=_(u"新增对公设备短消息")
    perm_model_menu = ['att.AttDeviceDataManage']
    params=(
#        ('device' , DeviceMultForeignKey(verbose_name=_(u'设备'),db_column='DeviceID',null=True, blank=True)),    
#            ('user' , EmpMultForeignKey(verbose_name=_(u'人员'), db_column='UserID',null=True, blank=True)),  
        ('context', models.TextField(verbose_name=_(u'短消息内容'),max_length=320)),
        ('starttime', models.DateTimeField(_(u'开始时间'),null=True)),
        ('lasttime', models.IntegerField(verbose_name=_(u'短消息持续时间(分)'), max_length=20,default=60)),
    )
    def action(self, **args):
        Notice(device=self.object, **args).save()
        
Device.OpAddDeviceMsg = OpAddDeviceMsg
            
class OpAddUserMsg(Operation):
    help_text=_(u'''新增对私短消息''')
    verbose_name=_(u"新增对私短消息")
    params=(
#            ('device' , DeviceMultForeignKey(verbose_name=_(u'设备'),db_column='DeviceID',null=False, blank=False)),    
#        ('user' , EmpMultForeignKey(verbose_name=_(u'人员'), db_column='UserID',null=True, blank=True)),  
        ('context', models.TextField(verbose_name=_(u'短消息内容'),max_length=320)),
        ('starttime', models.DateTimeField(_(u'开始时间'),null=True)),
        ('lasttime', models.IntegerField(verbose_name=_(u'短消息持续时间(分)'), max_length=20,default=60)),
    )
    def action(self, **args):
        Notice(user=self.object, **args).save()
          
Employee.OpAddUserMsg = OpAddUserMsg