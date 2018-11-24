#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, ACPANEL_1_DOOR, ACPANEL_4_DOOR, ACPANEL_AS_USUAL_ACPANEL
from mysite.iclock.models.dev_comm_operate import sync_set_interlock, sync_clear_interlock
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

#def interlock_details(device, door_count, ):
#    names = self.device.accdoor_set.order_by('id').values_list('door_no','door_name')
#    door_name_1 = u'%s(%s)' % (names[0][1], names[0][0])
#    door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])

class AccInterLock(CachingModel):
        u"""
        互锁门 1-2、3-4、1-2 3-4,1-2-3,1-2-3-4
        """
        device = models.ForeignKey(Device, verbose_name=_(u'设备'), editable=True, null=True, blank=False, unique=True)
        one_mode = models.BooleanField(_(u'1-2两门互锁'), null=False, default=False, blank=True, editable=True)
        two_mode = models.BooleanField(_(u'3-4两门互锁'), null=False, default=False, blank=True, editable=True)
        three_mode = models.BooleanField(_(u'1-2-3三门互锁'), null=False, default=False, blank=True, editable=True)
        four_mode = models.BooleanField(_(u'1-2-3-4四门互锁'), null=False, default=False, blank=True, editable=True)

        def limit_device_to(self, queryset):
            #需要过滤掉已经配置过的，当前自身（编辑时）以及单门控制器
            if self.device:
                v = AccInterLock.objects.exclude(device = self.device).values("device")
            else:    
                v = AccInterLock.objects.values("device")
            q = queryset.filter(device_type = DEVICE_ACCESS_CONTROL_PANEL).filter(is_elevator = ACPANEL_AS_USUAL_ACPANEL).exclude(acpanel_type = ACPANEL_1_DOOR)#门禁控制器
            return filterdata_by_user(q.exclude(pk__in = [item["device"] for item in v]), threadlocals.get_current_user()) 
        
        def data_valid(self, sendtype):
            if not(self.one_mode or self.two_mode or self.three_mode or self.four_mode):
                raise Exception(_(u'请设置设备的互锁信息'))

        def save(self, *args, **kwargs):
            super(AccInterLock, self).save()#log_msg=False
            sync_set_interlock(self.device)
        
        def __unicode__(self):
            return _(u'设备 %s 的互锁信息')%self.device.alias
        
        def get_details(self):
            result = []
            #opts = AccInterLock._meta
            names = self.device.accdoor_set.order_by('id').values_list('door_no','door_name')
            door_name_1 = u'%s(%s)' % (names[0][1], names[0][0])
            door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
            if self.one_mode:
                result.append(_(u"%(a)s 与 %(b)s 互锁") % {"a": door_name_1, "b": door_name_2})
            if self.device.acpanel_type == ACPANEL_4_DOOR:
                door_name_3 = u'%s(%s)' % (names[2][1], names[2][0])
                door_name_4 = u'%s(%s)' % (names[3][1], names[3][0])
                
            if self.two_mode:
                result.append(_(u"%(a)s 与 %(b)s 互锁") % {"a": door_name_3, "b": door_name_4})
            if self.three_mode:
                result.append(_(u"%(a)s 与 %(b)s 与 %(c)s 互锁") % {"a": door_name_1, "b": door_name_2, "c": door_name_3})
            if self.four_mode:
                result.append(_(u"%(a)s 与 %(b)s 与 %(c)s 与 %(d)s 互锁") % {"a": door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})
  
            return result and ','.join(result) or _(u'暂无互锁设置信息')

        def getlockoption(self):
            IntLock = 0
            if self.one_mode and self.two_mode: #1、2两种模式的组合
                IntLock = 4
            elif self.one_mode:
                IntLock = 1
            elif self.two_mode:
                IntLock = 2
            elif self.three_mode:
                IntLock = 3
            elif self.four_mode:
                IntLock = 5
            return IntLock
        
        def delete(self):
            sync_clear_interlock(self.device)
            super(AccInterLock,self).delete()
            return self

        class Admin(CachingModel.Admin):
            parent_model = 'DoorSetPage'
            disabled_perms = ['clear_accinterlock', 'dataimport_accinterlock', 'dataexport_accinterlock', 'view_accinterlock']
            menu_group = 'acc_doorset'
            menu_focus = 'DoorSetPage'
            menu_index = 100022
            position = _(u'门禁系统 -> 门设置 -> 互锁设置')
            list_display = ('device', 'interlock_details')
            newadded_column = {'interlock_details': 'get_details'}
            help_text = _(u'互锁设置是门与门之间的互锁，故单门控制器不能设置互锁。已经设置过互锁功能的控制器将不会出现在设备列表中。')
            #query_field = ('device')
            #master_field='device'
        class Meta:
            app_label = 'iaccess'
            db_table = 'acc_interlock'
            verbose_name = _(u'互锁设置')
            verbose_name_plural = verbose_name

