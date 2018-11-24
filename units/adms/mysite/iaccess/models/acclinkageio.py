#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, DEVICE_VIDEO_SERVER,DEVICE_CAMERA_SERVER,ACPANEL_AS_USUAL_ACPANEL
from mysite.iclock.models.dev_comm_operate import sync_set_define_io, sync_delete_define_io
from accmonitorlog import EVENT_CHOICES
from accdoor import LCHANNEL_CHOICES, DEVICE_C3_100, DEVICE_C3_200, DEVICE_C3_400, DEVICE_C3_400_TO_200, DEVICE_C4_200, DEVICE_C4_400, DEVICE_C4_400_TO_200, DEVICE_C3_160, DEVICE_C3_260, DEVICE_C3_460
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from dbapp import data_edit
from django.conf import settings

TRIGGEROPT_CHOICES = EVENT_CHOICES
#DISABLED_TRIGGEROPT_CHOICES = [-1, 6, 7, 11, 12, 13, 206,]#事件中不能用来触发联动事件的事件列表
#DISABLED_TRIGGEROPT_CHOICES = [-1, 6, 7, 10, 11, 12, 13, 42, 47, 100, 200, 201, 204, 205, 206, 210, 212, 213]#事件中不能用来触发联动事件的事件列表
DISABLED_TRIGGEROPT_CHOICES = [-1, 6, 7, 10, 11, 12, 13, 40,42, 47,48,49,50,51,52, 53,100, 200, 201, 204, 205, 206, 207,208,209,210,211, 212, 213,214,215,216,]#事件中不能用来触发联动事件的事件列表

FIRE_TRIGGEROPT_CHOICES = (
        (220, _(u'辅助输入点断开')),
        (221, _(u'辅助输入点短路')),
)#消防联动触发条件，只有“辅助输入短路”、“辅助输入断开”

#输入点
INADDRESS_CHOICES = (
    (0, _(u'任意')),
    (1, _(u'门1')),#wiegand+in1+in2
    (2, _(u'门2')),
    (3, _(u'门3')),
    (4, _(u'门4')),
    #C3 C3-100 无 ，inBIO160: 1，  C3-200 inBIO260: 1,2  C3-400，inBIO460 :1,2,3,4
    (301, _(u'辅助输入1')),
    (302, _(u'辅助输入2')),
    (303, _(u'辅助输入3')),
    (304, _(u'辅助输入4')),
    #C4 C4-200: C4-400 : 9,10,11,12
    (409, _(u'辅助输入9')),
    (410, _(u'辅助输入10')),
    (411, _(u'辅助输入11')),
    (412, _(u'辅助输入12')),
)
#输出点
OUTADDRESS_CHOICES = (
    #(0, _(u'无')),
    #lockcount
    (1, _(u'门锁1')),
    (2, _(u'门锁2')),
    (3, _(u'门锁3')),
    (4, _(u'门锁4')),
    #C3  C3-100，inBIO160: 1  C3-200，inBIO260: 1,2 C3-400，inBIO460:1,2,3,4 C3-400_to_200:1,2,3,4
    (301, _(u'辅助输出1')),
    (302, _(u'辅助输出2')),
    (303, _(u'辅助输出3')),
    (304, _(u'辅助输出4')),
    #C4  C4-200: 2,4,9,10 C4-400:2,4,6,8,9,10 C4-400_to_200:2,4,6,8,9,10
    (402, _(u'辅助输出2')),
    (404, _(u'辅助输出4')),
    (406, _(u'辅助输出6')),
    (408, _(u'辅助输出8')),
    (409, _(u'辅助输出9')),
    (410, _(u'辅助输出10')),
)



#根据设备型号获取辅助输出
def get_device_auxout(dev):
    auxout_list = []
    index_list = []#特定的index
    out_all = dict(OUTADDRESS_CHOICES)

    if dev.accdevice.machine_type in [DEVICE_C3_100, DEVICE_C3_160]:
        index_list = [301]
    elif dev.accdevice.machine_type in [DEVICE_C3_200, DEVICE_C3_260]:
        index_list = [301, 302]
    elif dev.accdevice.machine_type in [DEVICE_C3_400, DEVICE_C3_400_TO_200, DEVICE_C3_460]:
        index_list = [301, 302, 303, 304]
    elif dev.accdevice.machine_type == DEVICE_C4_200:
        index_list = [402, 404, 409, 410]
    elif dev.accdevice.machine_type in [DEVICE_C4_400 or DEVICE_C4_400_TO_200]:
        index_list = [402, 404, 406, 408, 409, 410]

    for index in index_list:
        if index > 400:
            auxout_list.append((index-400, unicode(out_all[index])))
        else:
            auxout_list.append((index-300, unicode(out_all[index])))
    return auxout_list#tuple(auxout_list)


ACTION_CLOSE = 0
ACTION_OPEN = 1
ACTION_LONGOPEN = 255
ACTIONTYPE_CHOICES = (
    (ACTION_CLOSE, _(u'关闭')),
    (ACTION_OPEN, _(u'打开')),#只有打开时才需要设置延时时间
    (ACTION_LONGOPEN, _(u'常开')),
)


#视频联动模式
VIDEO_LINK_MODE = (
    (0, _(u'弹出视频')),
    (1, _(u'抓图')),
    #(2, _(u'弹出视频的同时抓图')),
    (3, _(u'录像')),
)


class AccLinkageIO(CachingModel):
        u"""
        联动设置-当前只支持单控制器的联动设置.输入点根据事件判断是门还是辅助输入。输出点则是根据out_type_hide来判断是锁还是辅助输出
        """
        linkage_name = models.CharField(_(u'联动设置名称'), null=False, max_length=30, blank=False, unique=True)
        device = models.ForeignKey(Device, verbose_name=_(u'设备'), null=True, blank=False, editable=True)#控制器id
        trigger_opt = models.SmallIntegerField(_(u'触发条件'), default=0, null=True, blank=False, editable=True, choices=TRIGGEROPT_CHOICES)
        in_address_hide = models.SmallIntegerField(_(u'输入点地址'), null=True, blank=False, editable=False)
        in_address = models.SmallIntegerField(_(u'输入点地址'), default=0, null=True, blank=False, editable=True, choices=INADDRESS_CHOICES)
        out_type_hide = models.SmallIntegerField(_(u'输出类型'), null=True, blank=True, editable=False)
        out_address_hide = models.SmallIntegerField(_(u'输出点地址'), null=True, blank=True, editable=False)
        out_address = models.SmallIntegerField(_(u'输出点地址'), null=True, blank=True, editable=True, choices=OUTADDRESS_CHOICES)
        action_type = models.SmallIntegerField(_(u'动作类型'), default=0, null=True, blank=True, editable=True, choices=ACTIONTYPE_CHOICES)#联动动作类型，非复位动作类型
        delay_time = models.PositiveSmallIntegerField(_(u'延时'), default=20, help_text=_(u'秒 (范围:1-254)'), null=True, blank=False, editable=True)#延时（复位时间）
        video_linkageio = models.ForeignKey(Device, verbose_name=_(u'视频设备'), related_name='video_set', null=True, blank=True, editable=True)
        lchannel_num = models.SmallIntegerField(_(u'绑定通道'), null=True, blank=True, editable=True, choices=LCHANNEL_CHOICES)
        email_address = models.EmailField(_(u'发送到邮箱'), max_length=50, null=True, blank=True, editable=True)
        #video_delay_time = models.PositiveSmallIntegerField(_(u'录像延时'), default=20, help_text=_(u'秒 (范围:1-254)'), null=True, blank=True, editable=True)#延时（复位时间）

        video_link_mode = models.SmallIntegerField(_(u'视频联动输出模式'),null=True,default=0,blank=True, editable=True,choices=VIDEO_LINK_MODE)#0表示只弹视频，1表示只抓图，2表示弹视频的同时抓图，3表示录像--lhj20110921
        def limit_device_to(self, queryset):
            #print '--------------------------queryset=',queryset
            return filterdata_by_user(queryset.filter(device_type = DEVICE_ACCESS_CONTROL_PANEL).filter(is_elevator = ACPANEL_AS_USUAL_ACPANEL), threadlocals.get_current_user()) #只要门禁控制器

        def limit_video_linkageio_to(self, queryset):
            #print '-----------------------', filterdata_by_user(queryset.filter(device_type = DEVICE_VIDEO_SERVER), threadlocals.get_current_user()) #只要门禁控制器
            return filterdata_by_user(queryset.filter(device_type__in = [DEVICE_VIDEO_SERVER,DEVICE_CAMERA_SERVER]), threadlocals.get_current_user()) #只要门禁控制器

        def __unicode__(self):
            return u'%s'%self.linkage_name

        def delete(self):
            sync_delete_define_io(self)
            super(AccLinkageIO, self).delete()

        def get_action_type(self):
            return self.delay_time if self.action_type == ACTION_OPEN else self.action_type

        def data_valid(self, sendtype):
            import re
            
            tmp = AccLinkageIO.objects.filter(linkage_name=self.linkage_name.strip())
            if tmp and tmp[0] != self:   #新增时不能重复。
                raise Exception(_(u'内容：%s 设置重复！')%self.linkage_name)

#            tmp_a = AccLinkageIO.objects.filter(device=self.device, trigger_opt=self.trigger_opt, in_address=self.in_address)
#            if tmp_a and tmp_a[0] != self:
#                raise Exception(_(u'系统中已存在该设备在该触发条件下输入点相同的联动设置'))
            if (not self.out_address) and (not self.video_linkageio) and (not self.email_address):
                if "mysite.video" in settings.INSTALLED_APPS:
                    raise Exception(_(u'请选择联动动作或视频设备'))
                else:
                    raise Exception(_(u'请选择输出点地址或邮箱地址'))

            if self.in_address == 0:
                tmp_b = AccLinkageIO.objects.filter(device=self.device, trigger_opt=self.trigger_opt, in_address__gt=0)#id_address不为0
                if tmp_b and tmp_b[0] != self:
                    raise Exception(_(u'系统中已存在该设备在该触发条件下输入点不为“任意”的联动设置'))
            else:
                tmp_c = AccLinkageIO.objects.filter(device=self.device, trigger_opt=self.trigger_opt, in_address=0)
                if tmp_c and tmp_c[0] != self:
                    raise Exception(_(u'系统中已存在该设备在该触发条件下输入点为“任意”的联动设置'))

            tmp_c = AccLinkageIO.objects.filter(device=self.device, trigger_opt=self.trigger_opt, in_address=self.in_address, out_address=self.out_address)
            if tmp_c and tmp_c[0] != self:
                raise Exception(_(u'系统中已存在该设备在该触发条件下输入点和输出点都相同的联动设置'))

            #动作类型为打开时
            if self.action_type != ACTION_LONGOPEN and self.action_type != ACTION_CLOSE and (self.delay_time < 1 or self.delay_time > 254):
                raise Exception(_(u'延时时间的设置范围为 1-254(秒)'))
            
            email = re.compile('^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$')
            if self.email_address and not email.search(self.email_address):
                raise Exception(_(u'邮箱格式不正确'))
            
      
        #此方法用于获取跟此消防联动相关联的门
        def get_doors(self):
            return u",".join([door.door_name for door in self.door_address_fire.all().order_by("id")]) or _(u'暂未设置门信息')
        #此方法用于获取跟此消防联动相关联的辅助输入
      
        def get_auxins(self):
            return u",".join([auxin.auxin_name for auxin in self.auxin_address_fire.all().order_by("id")]) or _(u'暂未设置消防信号接入点信息')
      
        def get_auxins_ids(self):
            auxin_ids = ([auxin.id for auxin in self.auxin_address_fire.all().order_by("id")])
            print "-----auxin_ids=",auxin_ids
            return auxin_ids
       
        def save(self, *args, **kwargs):
            if (not self.out_address) and self.action_type != None:#可能为0
                self.action_type = None
                 
            if (not self.video_linkageio) and self.lchannel_num != None:
                self.lchannel_num = None
            #print '--self.out_address ===',self.out_address
#            if self.out_address == None:#0仅前端使用
#                self.out_address = None
            if self.in_address < 300:
                self.in_address_hide = self.in_address
            else:
                if self.out_address < 400:#200 < a <400 C3
                    self.in_address_hide = self.in_address - 300
                else:#C4
                    self.in_address_hide = self.in_address - 400

            #try:
            if self.out_address:#因视频联动可以不设置输出点地址
                if self.out_address < 300:#门锁
                    self.out_type_hide = 0
                    self.out_address_hide = self.out_address
                else:#辅助输出
                    self.out_type_hide = 1
                    if self.out_address < 400:#300 < a <400  C3
                        self.out_address_hide = self.out_address - 300
                    else:#>400 C4
                        self.out_address_hide = self.out_address - 400
                super(AccLinkageIO, self).save()#log_msg=False

            else:#仅视频联动不需要下数据
                self.out_type_hide = None
                self.out_address_hide = None
                super(AccLinkageIO, self).save()#log_msg=False
            #except:
                #import traceback;traceback.print_exc()

        class Admin(CachingModel.Admin):
            parent_model = 'DoorSetPage'
            menu_group = 'acc_doorset'
            disabled_perms = ['clear_acclinkageio', 'dataimport_acclinkageio', 'dataexport_acclinkageio', 'view_acclinkageio']
            menu_focus = 'DoorSetPage'
            menu_index = 100025
            position = _(u'门禁系统 -> 门设置 -> 联动设置')
            list_display = ('linkage_name', 'device', 'trigger_opt', 'in_address', 'out_address', 'email_address', 'action_type', 'video_linkageio', 'lchannel_num')
            query_fields =('linkage_name', 'device__alias', 'trigger_opt', 'action_type') #list_filter
            help_text = _(u'请先输入联动设置名称再选择要设置的设备。每台设备可进行多次联动设置。')

        class Meta:
            app_label='iaccess'
            db_table = 'acc_linkageio'
            verbose_name = _(u'联动设置')
            verbose_name_plural=verbose_name

#处理联动表单（仅5.0）
def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, AccLinkageIO):
        try:
            if oldObj and oldObj.out_address:  #修改权限组
                #if oldObj.out_address or newObj.out_address:#只有新的和旧的输出地址均为None时不下载
                    #sync_set_define_io(newObj)
                if oldObj.out_address and not newObj.out_address:
                    sync_delete_define_io(newObj)
                elif newObj.out_address:
                    sync_set_define_io(newObj)
            elif newObj and newObj.out_address:#新增时输出地址不为空时，下载数据
                sync_set_define_io(newObj)
        except:
            import traceback;traceback.print_exc()

data_edit.post_check.connect(DataPostCheck)
