#! /usr/bin/env python
#coding=utf-8
from base.models import AppOperation
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from mysite.iclock.models.model_device import Device,DeviceManyToManyFieldKeyForMeeting,DeviceManyToManyFieldKey
import re

class Room(CachingModel):
    #sn = DeviceManyToManyFieldKey(verbose_name=_(u'设备'), null=True, blank=True)
    numberRoom = models.CharField(verbose_name=_(u'会议室编号'),  max_length=20)
    nameRoom = models.CharField(verbose_name=_(u'会议室名称'),null=False, max_length=40, blank=False)
    addressRoom = models.CharField(verbose_name = _(u'会议室地址'),max_length=100,null=True,blank=True)
    empLimit = models.IntegerField(verbose_name = _(u'会议室人数上限'),max_length=10,editable=True,default=20)
    isUse = models.BooleanField(verbose_name=_(u'是否可以使用'), editable=False, default=True)
    devices = DeviceManyToManyFieldKeyForMeeting(verbose_name=_(u'签到设备'),max_length=10,null=True,blank=True)
    
    def save(self):
        #print '1111111'
        #print self.devices.all()
        #print self.pk,'-------'
        if len(self.nameRoom)>20:
            raise Exception(_(u'会议室名称长度不能超过20个有效字符'))
        p = re.compile(r'^[a-zA-Z0-9]{1,8}$')
        if not p.match(self.numberRoom):
            raise Exception(_(u"会议室编号长度不能超过8个数字或字母")) 
        
        r = Room.objects.filter(numberRoom=self.numberRoom)
        if len(r)>0 and not self.pk:
            raise Exception(_(u'会议室编号已存在'))
        r = Room.objects.filter(nameRoom=self.nameRoom)
        if len(r)>0 and not self.pk:
            raise Exception(_(u'会议室名称已存在'))
        if self.pk:
            rNum = Room.objects.filter(numberRoom=self.numberRoom)
            rNam = Room.objects.filter(nameRoom=self.nameRoom)
            if len(rNum)>0 and len(rNam)>0 and rNum[0].pk != rNam[0].pk:
                raise Exception(_(u'会议室编号或名称已存在'))
            
        if self.empLimit < 1:
            raise Exception(_(u'会议室人数上限设置无效'))
        if self.empLimit > 2000:
            raise Exception(_(u'会议室人数上限不应超过2000人'))
#        if self.devices.all() == None:
#            raise Exception(_(u'请选择签到考勤设备'))
        super(Room, self).save()
    
    def __unicode__(self):
          return u"%s %s" % (self.numberRoom, self.nameRoom)
    def get_device_name(self):
        r=""
        for i in [d.alias for d in self.devices.all()]:
            r+=str(i)+","
        return  r[:-1]
    def delete(self):
        from model_meeting import MeetingEntity
        room = Room.objects.get(numberRoom=self.numberRoom)
        meetings = MeetingEntity.objects.filter(roomMeeting= room)
        if len(meetings)>0:
            raise Exception(_(u"该会议室还有会议，不可删除"))
        super(Room,self).delete()
        
    class OpAddDev(Operation):#继承ModelOperation 类
        visible=False
        help_text=_(u"添加设备") #删除选定的记录
        verbose_name=_(u"添加会议签到设备")
        params = (
                ('sns', DeviceManyToManyFieldKeyForMeeting(verbose_name=_(u'请选择签到设备'))),
        )
        
        def action(self,sns):
            pass
        
#    def limit_devices_to(self, queryset,limitleveltype=0):#待修改
#        #通过时间段类型，过滤时间段
#        from mysite.iaccess.models.acctimeseg import AccTimeSeg
#        if limitleveltype:
#            queryset = queryset.filter(timeseg_type=limitleveltype).order_by('id')
#        else:
#            pass 
#        return  queryset.order_by('id') 


    class Admin(CachingModel.Admin):    #管理该模型
        disabled_perms = ['clear_model_meeting', 'dataimport_model_meeting', 'view_model_meeting']
        sort_fields=["numberRoom","empLimit"]      #需要排序的字段，放在列表中
        menu_group = 'meeting'          #在哪个app应用下
        menu_index=1                #菜单的摆放的位置
        query_fields=['numberRoom','nameRoom','empLimit']     #需要查找的字段
        
        list_display=['numberRoom','nameRoom','addressRoom','empLimit','get_device_name'] #列表显示那些字段
        
        
    class Meta:
        verbose_name=_(u'会议室')#名字
        verbose_name_plural=verbose_name
        app_label=  'meeting' #属于哪个app
        
        
class RoomManyToManyFieldKey(models.ManyToManyField):
    def __init__(self, to_field=None, **kwargs):
        super(RoomManyToManyFieldKey, self).__init__(Room, to_field=to_field, **kwargs)
