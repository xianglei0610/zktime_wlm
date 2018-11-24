#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel, Operation
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL,DEVICE_VIDEO_SERVER
from django.db.models.signals import post_save
from acctimeseg import AccTimeSeg
from accmap import AccMap
from accwiegandfmt import AccWiegandFmt
from dbapp import data_edit
from django import forms
import re
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from base.crypt import encryption, decryption
from django.conf import settings
from mysite.utils import get_option

#各种机型常量
DEVICE_C3_100 = 4
DEVICE_C3_200 = 1
DEVICE_C3_400 = 2
DEVICE_C3_400_TO_200 = 7
DEVICE_C4_200 = 5
DEVICE_C4_400 = 3
DEVICE_C4_400_TO_200 = 6
DEVICE_C3_160 = 8
DEVICE_C3_260 = 9
DEVICE_C3_460 = 10
DEVICE_ELEVATOR   = 11
DEVICE_ACCESS_CONTROL_DEVICE = 12 #一体机


    
INOUT_CHOICES = (
        (0, _(u'入')), (1, _(u'出')),
)

READER_CHOICES = (
        (1, _(u'卡读头')), (2, _(u'指纹读头')),
)

LCHANNEL_CHOICES = (
    (0, _(u'通道1')),
    (1, _(u'通道2')),
    (2, _(u'通道3')),
    (3, _(u'通道4')),
    (4, _(u'通道5')),
    (5, _(u'通道6')),
    (6, _(u'通道7')),
    (7, _(u'通道8')),
)

#开门方式 即验证方式
OPENDOOR_CHOICES = (   
        #(3, _(u'仅密码')),  
        (4, _(u'仅卡')), 
        (11, _(u'卡加密码')),
    )
if get_option("IACCESS_5TO4"):
    OPENDOOR_CHOICES_DEFAULT = 4
else:
    OPENDOOR_CHOICES_FINGERPRINT = (
           (1, _(u'仅指纹')),  
           (6, _(u'卡或指纹')),
           (10, _(u'卡加指纹')),       
       )
    OPENDOOR_CHOICES += OPENDOOR_CHOICES_FINGERPRINT
    OPENDOOR_CHOICES_DEFAULT = 6
        
STATUS_CHOICES = (
        (0, _(u'无')), (1, _(u'常开')), (2, _(u'常闭')),
)

IS_GLOBAL_ANTIPASSBACK = (
        (0, _(u'否')), (1, _(u'是')),
)


def save_door_objects(cur_obj, objs):
    for door in objs:
        if door != cur_obj:
            try:
                door.lock_delay = cur_obj.lock_delay
                door.back_lock = cur_obj.back_lock
                door.sensor_delay = cur_obj.sensor_delay
                door.opendoor_type = cur_obj.opendoor_type
                door.inout_state = cur_obj.inout_state
                door.lock_active = cur_obj.lock_active
                door.long_open = cur_obj.long_open
                door.wiegand_fmt = cur_obj.wiegand_fmt
                door.card_intervaltime = cur_obj.card_intervaltime
                door.duration_apb = cur_obj.duration_apb
                door.reader_type = cur_obj.reader_type
                door.is_att = cur_obj.is_att
                p2 = re.compile(r'^([0-9]+)$')
                if not p2.match(cur_obj.force_pwd):
                    door.force_pwd = decryption(cur_obj.force_pwd)
                if not p2.match(cur_obj.supper_pwd):
                    door.supper_pwd = decryption(cur_obj.supper_pwd)
                door.door_sensor_status = cur_obj.door_sensor_status
                #新增
                door.global_apb = cur_obj.global_apb
                door.save(force_update=True)
            except:
                import traceback;traceback.print_exc()
    

class AccDoor(CachingModel):
        u"""
        门表
        """
        device = models.ForeignKey(Device, verbose_name=_(u'设备名称'), editable=True, null=True, blank=False)
        door_no = models.PositiveSmallIntegerField(_(u'门编号'), null=True, blank=False, editable=True)
        door_name = models.CharField(_(u'门名称'), null=True, max_length=30, blank=False, default="")
        lock_delay = models.PositiveSmallIntegerField(_(u'锁驱动时长'), help_text=_(u'秒(范围0-254)'), default=5, null=True, blank=False, editable=True)#锁驱动时长
        back_lock = models.BooleanField(_(u'闭门回锁'), default=True, editable=True)
        sensor_delay = models.PositiveSmallIntegerField(_(u'门磁延时'), help_text=_(u'秒(范围1-254)'), default=15, null=True, blank=True, editable=True)#门开超时---门磁报警延时
        opendoor_type = models.SmallIntegerField(_(u'验证方式'), null=True, default=OPENDOOR_CHOICES_DEFAULT, blank=False, editable=True, choices=OPENDOOR_CHOICES)#
        inout_state = models.SmallIntegerField(_(u'出入状态'), default=0, null=True, blank=True, editable=True, choices=INOUT_CHOICES)#该字段暂时废弃 当前已写死
        lock_active = models.ForeignKey(AccTimeSeg, verbose_name=_(u'门有效时间段'), default=1, related_name='lockactive_set', blank=False, editable=True, null=True)#default=0,
        long_open = models.ForeignKey(AccTimeSeg, verbose_name=_(u'门常开时间段'), related_name='longopen_set', blank=True, editable=True, null=True)#default=0, 
        wiegand_fmt = models.ForeignKey(AccWiegandFmt, verbose_name=_(u'韦根卡格式') ,default=1, related_name='wiegandfmt_set', null=True, blank=False, editable=False)#default=0, 
        card_intervaltime = models.PositiveSmallIntegerField(_(u'刷卡间隔'), help_text=_(u'秒(范围:0-254)'), default=2, null=True, blank=False, editable=True)
        reader_type = models.SmallIntegerField(_(u'读头类型'), default=0, null=True, blank=True, editable=True, choices=READER_CHOICES)
        is_att = models.BooleanField(_(u'考勤'), blank=True, editable=True)
        #force_pwd = models.CharField(_(u'胁迫密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=8, blank=True, default="")
        force_pwd = models.CharField(_(u'胁迫密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=18, blank=True, default="")#存储加密后的密码，将字段的最大长度增加为128
        #supper_pwd = models.CharField(_(u'紧急状态密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=8, blank=True, default="")
        supper_pwd = models.CharField(_(u'紧急状态密码'), help_text=_(u'(最大8位整数)'), null=True, max_length=18, blank=True, default="")#存储加密后的密码，将字段的最大长度增加为128
        door_sensor_status = models.SmallIntegerField(_(u'门磁类型'), default=0, null=True, blank=False, editable=True, choices=STATUS_CHOICES)
        #video_linkageio = models.ForeignKey(Device, verbose_name=_(u'硬盘录像机'), related_name='videoserver_set', null=True, blank=True, editable=True)
        #lchannel_num = models.SmallIntegerField(_(u'绑定通道'), default=0, null=True, blank=True, editable=True, choices=LCHANNEL_CHOICES)
        map = models.ForeignKey(AccMap, verbose_name=_(u'所属地图'), null=True, blank=True, editable=False)#当前门所属地图
        duration_apb = models.PositiveSmallIntegerField(_(u'入反潜时长'), help_text=_(u'分(5-120)'), default=0, null=True, blank=True, editable=False)#反潜时长 
        global_apb = models.BooleanField(_(u'启用区域反潜'), blank=True, editable=False, choices=IS_GLOBAL_ANTIPASSBACK)
        

#        def limit_video_linkageio_to(self, queryset):
#            print '-----------------------', filterdata_by_user(queryset.filter(device_type = DEVICE_VIDEO_SERVER), threadlocals.get_current_user()) #只要门禁控制器
#            return filterdata_by_user(queryset.filter(device_type = DEVICE_VIDEO_SERVER), threadlocals.get_current_user()) #只要门禁控制器

        #对密码进行加密
        def encrypt_password(self,password):
           return encryption(password)

        def check_password(self, raw_password,password):
           password = decryption(password)
           if raw_password == password:return True
           else: return False
        
        def data_valid(self, sendtype):#此处只有编辑的情况
            tmp = AccDoor.objects.filter(door_name=self.door_name.strip()) 
            if tmp and tmp[0] != self:#新增时(该名称的记录已存在且不是编辑）
                raise Exception(_(u'内容：%s 设置重复！')%self.door_name)
            
            if self.card_intervaltime:
                if self.card_intervaltime > 254 or self.card_intervaltime < 0:   
                    raise Exception(_(u"刷卡间隔范围为0-254秒"))

            if self.door_sensor_status != 0:
                if self.sensor_delay <= 0 or self.sensor_delay > 254:
                    raise Exception(_(u"门磁延时范围为1-254秒"))
            
                if self.sensor_delay and self.sensor_delay <= self.lock_delay:
                    raise Exception(_(u"门磁延时需大于锁驱动时长"))

            if self.lock_delay < 0  or self.lock_delay > 254:
                raise Exception(_(u"锁驱动时长范围为0-254秒"))#255为常开   远程开关门也取此值
            
            if self.duration_apb and self.duration_apb < 5  or self.duration_apb > 120:
                raise Exception(_(u"反潜时长范围为5-120分"))            
            
            if self.force_pwd:
                from mysite.personnel.models import Employee
                emps = Employee.objects.all()#系统里所有的，不需要权限过滤
                password_existed = [e.Password for e in emps]#[int(d.force_pwd) for d in doors if d.force_pwd]
                if self.force_pwd in password_existed or encryption(self.force_pwd) in password_existed:#不含‘’
                    raise Exception(_(u"胁迫密码不能与任意人员密码相同"))
                accdoor = AccDoor.objects.filter(id=self.pk)
                p1 = re.compile(r'^([0-9]+)$')
                if (accdoor[0].force_pwd != self.force_pwd) and (not p1.match(self.force_pwd)):
                    raise Exception(_(u"胁迫密码必须为整数"))
            
            if self.supper_pwd:
#                print self.supper_pwd,'---super'
#                if self.supper_pwd == self.force_pwd or self.encrypt_password(self.supper_pwd)==self.force_pwd:
#                    raise Exception(_(u"紧急状态密码不能和胁迫密码相同"))
                accdoor = AccDoor.objects.filter(id=self.pk)
                p2 = re.compile(r'^([0-9]+)$')
                if (accdoor[0].supper_pwd != self.supper_pwd) and (not p2.match(self.supper_pwd)):
                    raise Exception(_(u"紧急状态密码必须为整数"))
            

        def save(self, *args, **kwargs):
            #门磁类型为无
            accdoor = AccDoor.objects.filter(id=self.pk)
            if self.door_sensor_status == 0:
                self.back_lock = 0#False
                self.sensor_delay = None
            if self.force_pwd!="" or None:
                if accdoor[0].force_pwd == self.force_pwd:
                    pass
                else:
                    self.force_pwd = self.encrypt_password(self.force_pwd)
            if self.supper_pwd!="" or None:
                if accdoor[0].supper_pwd == self.supper_pwd:
                    pass
                else:
                    self.supper_pwd = self.encrypt_password(self.supper_pwd)

            try:
                if accdoor and accdoor[0].global_apb != self.global_apb:
                    if self.global_apb:
                        self.device.set_acc_push_params(1)
                    else:
                        self.device.set_acc_push_params(0)                
                
                super(AccDoor, self).save()#log_msg=False
                #print "door set save"
                #print '--add_device=',kwargs['add_device']
                add_device = kwargs.has_key('add_device') and kwargs['add_device'] or None
                #print '----add_device=',add_device
                if not add_device:#非新增设备
                    #print '--in add_device'
                    from mysite.iclock.models.dev_comm_operate import sync_set_door_options
                    sync_set_door_options(self)
                    from mysite.iaccess.dev_comm_center import OPERAT_EDIT
                    self.device.add_comm_center(self.device.getdevinfo(), OPERAT_EDIT)
                    

            except: 
                import traceback; traceback.print_exc()

        def __unicode__(self):
            return self.door_name  
        
#        def delete(self):
#            print '-----------------------delete doors--------'
#            super(AccDoor, self).delete()
        
        class Admin(CachingModel.Admin):
            #master_field = 'device'
            child_fk_field = 'device'
            menu_focus = 'DoorSetPage'
            parent_model = 'DoorSetPage'
            disabled_perms = ['add_accdoor', 'delete_accdoor', 'clear_accdoor', 'dataexport_accdoor', 'dataimport_accdoor', 'view_accdoor']#有 change和browse
            menu_group = 'acc_doorset_'
            menu_index = 100026
            list_display = ('door_no', 'door_name', 'lock_active', 'accfirstopen_set|detail_list_set', 'accmorecardset_set|detail_list_set',)# 'lock_delay', 'card_intervaltime'
            query_fields = ('door_no', 'door_name',)
            #newadded_column = {'firstcard': 'get_firstcard','morecard': 'get_morecard'}
            blankerror_text = _(u'没有可以选择的门，请先添加设备！')#_('No doors to be choosen! Pls add first!')#当其他模型和此表有多对多关系时，如果该模型尚无数据，将在多对多多选控件中显示此处信息
            default_widgets = {'force_pwd': forms.PasswordInput, 'supper_pwd': forms.PasswordInput}
            help_text = _(u'必须设定门有效时间段才能启用该门。门磁类型如果不设置（即为无），在实时监控中将无法检测到门的当前状态。<br>将当前的设置信息应用于其他门，这里的所有控制器指的是当前用户权限管理范围内的控制器。')
            #_cancel_perms = [("can_MonitorAllPage.can_MonitorAlarmPage","can_RTMonitorPage")]
            default_give_perms = ["can_FloorMngPage","can_FloorSetPage"]
        class Meta:
            app_label = 'iaccess'
            db_table = 'acc_door'
            verbose_name = _(u'门')
            verbose_name_plural = verbose_name

class AccMapDoorPos(CachingModel):
        u"""
        门坐标---暂时限制一个门只在一张地图上---AccMap AccDoor任何一方删除此记录都需要删除
        """
        map_door = models.ForeignKey(AccDoor, verbose_name=_(u'门'), null=True, blank=True, editable=True)#当前门
        map = models.ForeignKey(AccMap, verbose_name=_(u'所属地图'), null=True, blank=True, editable=True)#当前门所属地图
        width = models.FloatField(_(u'门图标宽度'), null=True, blank=True, default=40, editable=True)#高度是auto（默认和width相等）
        left = models.FloatField(_(u'左边距'), null=True, blank=True, default=8, editable=True)#
        top = models.FloatField(_(u'上边距'), null=True, blank=True, default=8, editable=True)

        def __unicode__(self):
            return u"%s(%s)" % (self.map_door, self.map)

        class Admin(CachingModel.Admin):
            visible = False

        def delete(self):
            super(AccMapDoorPos, self).delete()

        class Meta:
            app_label = 'iaccess'
            db_table = 'acc_mapdoorpos'
            verbose_name = _(u'门坐标')
            verbose_name_plural = verbose_name

class AccDevice(CachingModel):
    device = models.OneToOneField(Device, verbose_name = _(u'设备名称'), null=True, blank=True, editable=False)
    door_count = models.IntegerField(_(u'门数量'), null=True, blank=True, editable=False)
    reader_count = models.IntegerField(_(u'读头数量'), null=True, blank=True, editable=False)
    aux_in_count = models.IntegerField(_(u'辅助输入数量'), null=True, blank=True, editable=False)
    aux_out_count = models.IntegerField(_(u'辅助输出数量'), null=True, blank=True, editable=False)
    machine_type = models.IntegerField(_(u'设备类型'), null=True, blank=True, editable=False)#类似于DeviceName仅供内部使用-- C3_200 1， C3_400 2，C4-400 3 ， C3_100 4， C4_200 5 ， C4_400To_200 6 ，C3_400To_200 7 ,C3_160 8,C3_260 9, C3_460 10
    IsOnlyRFMachine = models.IntegerField(_(u'只支持RF卡'), default=1, null=True, blank=True, editable=False)
    iclock_server_on = models.BooleanField(_(u'启用PUSH'), null=False, default=False, blank=True, editable=True)
    global_apb_on = models.BooleanField(_(u'启用区域反潜'), null=False, default=False, blank=True, editable=True)
#    emp_capacity = models.IntegerField(_(u'设备用户容量'), null=True, blank=True, editable=False)
#    record_capacity = models.IntegerField(_(u'设备记录容量'), null=True, blank=True, editable=False)
#    fp_capacity = models.IntegerField(_(u'设备指纹容量'), null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.device.device_type == DEVICE_ACCESS_CONTROL_PANEL:#限制设备类型只能为控制器
            super(AccDevice, self).save()

    class Admin(CachingModel.Admin):
        master_field = 'device'
        visible = False
        
    class Meta:
        app_label='iaccess'
        db_table = 'acc_device'
        verbose_name = _(u'门禁设备扩展参数')
        verbose_name_plural = verbose_name
    
#用于向控制器中添加门
def auto_add_door(dev_ins, door_count):
    from mysite.iclock.models.model_device import ACCESS_CONTROL_DEVICE
    if door_count == ACCESS_CONTROL_DEVICE: #一体机 单门
        door_count = 1
    for ndoor in range(door_count):
        AccDoor(device = dev_ins, door_no = (ndoor+1), door_name = '%s-%s' % (dev_ins.alias, str(ndoor+1))).save(force_insert=True, add_device=True)

#新增控制器时自动新增门
def door_save(sender, instance, created, **kwargs):
    if instance.device_type == DEVICE_ACCESS_CONTROL_PANEL:
        value_list = set([(item['device'] and int(item['device']) or 0) for item in AccDoor.objects.values('device')])
        #if not created: #只在第一次添加控制器时添加门，编辑时return
        
        #print 'value_list=',value_list
        if instance.pk in value_list:
            #print 'true'
            return

        #print 'The device itself has been saved already, system will add the doors of the device immediately...'
        #print 'Serial Number and Firmware Version have not been inserted by far...'
        #print 'Table AccDevice has not been built...'
        auto_add_door(instance, instance.acpanel_type)
        #print "Method 'door_save' implements,that is, you have added %s doors(door_count=%s) successfully,then system will create the one_to_one table AccDevice"%(instance.acpanel_type, instance.acpanel_type)
post_save.connect(door_save, sender = Device)    

def DataPostCheck(sender, **kwargs):
    oldObj=kwargs['oldObj']
    newObj=kwargs['newObj']
    request=sender
    if isinstance(newObj, AccDoor):
        current = request.POST.getlist("applytocur")
        all = request.POST.getlist("applytoall")
        
        #print 'current=',current#[u'on'] or []所有控制器优先
        #将当前门设置应用于某些门
        #print request.user.is_superuser
        if all:
            u = request.user
            aa = u.areaadmin_set.all()
            if u.is_superuser or not aa:#为超级管理员或者没有配置区域（默认全部区域）
                doors = AccDoor.objects.all()
            else:
                areas = [a.area for a in aa]
                doors = AccDoor.objects.filter(device__area__in=areas)
            #print '------------doors=',doors
            save_door_objects(cur_obj=newObj, objs=doors)
        elif current:
            doors = newObj.device.accdoor_set.all()
            save_door_objects(cur_obj=newObj, objs=doors)

data_edit.post_check.connect(DataPostCheck)
