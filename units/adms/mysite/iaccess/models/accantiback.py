#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _
from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL, ACPANEL_1_DOOR, ACPANEL_2_DOOR, ACPANEL_4_DOOR, ACPANEL_AS_USUAL_ACPANEL
from mysite.iclock.models.dev_comm_operate import sync_set_antipassback, sync_clear_antipassback
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

#ONEDOOR_MODE = (
#    ('one_mode', _(u'1号门读头间反潜')),#单门双向（1）
#)
#
#TWODOORS_MODE = (
#    ('one_mode', _(u'1号门读头间反潜')),#两门双向（1）
#    ('two_mode', _(u'2号门读头间反潜')),#两门双向（2）
#    ('three_mode', _(u'1,2号门间反潜')),#两门双向（4）+ 两门单向（1）
#)
#
#FOURDOORS_MODE = (
#    ('one_mode', _(u'1-2门反潜')),#四门单向（1）
#    ('two_mode', _(u'3-4门反潜')),#四门单向（2）
#    ('three_mode', _(u'1/2-3/4门反潜')),#四门单向（4）
#    ('four_mode', _(u'1-2/3门反潜')),#四门单向（5）
#    ('five_mode', _(u'1-2/3/4门反潜')),#四门单向（6）

#)

#综上，五种mode只有four_mode可能存在多个值 ，1和4，即两门双向和四门单向为4，两门单向为1

class AccAntiBack(CachingModel):
        u"""
        反潜 两门：1（1-1）、2（2-2）、(1-1，2-2)、1-2互锁 四门：1-2门反潜、3-4门反潜、（1-2 and 3-4）、1/2-3/4门反潜、1-2/3门反潜、1-2/3/4门反潜 ，单门：门自身反潜
        """
        device = models.ForeignKey(Device, verbose_name=_(u'设备'), null=True, blank=False, editable=True)
        one_mode = models.BooleanField(_(u'反潜模式1'), null=False, default=False, blank=True, editable=True)
        two_mode = models.BooleanField(_(u'反潜模式2'), null=False, default=False, blank=True, editable=True)
        three_mode = models.BooleanField(_(u'反潜模式3'), null=False, default=False, blank=True, editable=True)
        four_mode = models.BooleanField(_(u'反潜模式4'), null=False, default=False, blank=True, editable=True)
        five_mode = models.BooleanField(_(u'反潜模式5'), null=False, default=False, blank=True, editable=True)
        six_mode = models.BooleanField(_(u'反潜模式6'), null=False, default=False, blank=True, editable=True)
        seven_mode = models.BooleanField(_(u'反潜模式7'), null=False, default=False, blank=True, editable=True)
        eight_mode = models.BooleanField(_(u'反潜模式8'), null=False, default=False, blank=True, editable=True)
        nine_mode = models.BooleanField(_(u'反潜模式9'), null=False, default=False, blank=True, editable=True)
        
        def limit_device_to(self, queryset):
            if self.device:
                v = AccAntiBack.objects.exclude(device=self.device).values("device")
            else:    
                v = AccAntiBack.objects.values("device")
            q = queryset.filter(device_type = DEVICE_ACCESS_CONTROL_PANEL).filter(is_elevator = ACPANEL_AS_USUAL_ACPANEL)
            return filterdata_by_user(q.exclude(pk__in=[item["device"] for item in v]), threadlocals.get_current_user()) 
        
        def __unicode__(self):
            return _(u'设备 %s 的反潜信息') % self.device.alias
        
        def data_valid(self, sendtype):
            if not(self.one_mode or self.two_mode or self.three_mode or self.four_mode or self.five_mode or self.six_mode or self.seven_mode or self.eight_mode or self.nine_mode):
                raise Exception(_(u'请设置设备的反潜信息'))
            
        def save(self, *args, **kwargs):
            super(AccAntiBack, self).save()#log_msg=False
            sync_set_antipassback(self.device)

        def delete(self):
            sync_clear_antipassback(self.device)
            return super(AccAntiBack,self).delete()

        def getantibackoption(self):
            anti = 0#无反潜
            #if self.one_mode and self.two_mode: #双门双向
               # anti += 3
            if self.one_mode:#单门双向，双门双向，四门单向
                anti += 1
            if self.two_mode:
                anti += 2
            if self.three_mode:
                #if self.device.accdevice.reader_count == 4:#两门双向+四门单向（均为四个读头）
                anti += 4
                #elif self.device.accdevice.reader_count == 2:#两门单向（两个读头，如C4-200）
                   # anti = 1
            if self.four_mode:
                anti += 5
            if self.five_mode:
                anti += 6
            if self.six_mode:
                anti += 16
            if self.seven_mode:
                anti += 32
            if self.eight_mode:
                anti += 64
            if self.nine_mode:
                anti += 128

            return anti

        def get_details(self):
            result = []
            names = self.device.accdoor_set.order_by('id').values_list('door_no','door_name')
            door_name_1 = u'%s(%s)' % (names[0][1], names[0][0])
            
            if self.device.acpanel_type == ACPANEL_1_DOOR:#单门双向
                if self.one_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_1)
            
            elif self.device.acpanel_type == ACPANEL_2_DOOR and self.device.accdevice.reader_count == 4:#两门双向 含C4-200和C3400-200
                door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
                if self.one_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_1)
                if self.two_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_2)
                if self.three_mode:
                    result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2})
            
            elif self.device.acpanel_type == ACPANEL_2_DOOR and self.device.accdevice.reader_count == 2:#两门单向
                door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
                if self.three_mode:
                    result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2})
           
            elif self.device.acpanel_type == ACPANEL_4_DOOR:
                door_name_2 = u'%s(%s)' % (names[1][1], names[1][0])
                door_name_3 = u'%s(%s)' % (names[2][1], names[2][0])
                door_name_4 = u'%s(%s)' % (names[3][1], names[3][0])
                if self.one_mode:
                    result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_1, "b": door_name_2})
                if self.two_mode:
                    result.append(_(u"%(a)s 与 %(b)s 反潜") % {"a": door_name_3, "b": door_name_4})
                if self.three_mode:
                    result.append(_(u"%(a)s与%(b)s 或 %(c)s与%(d)s 反潜") % {"a": door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})
                if self.four_mode:
                    result.append(_(u"%(a)s 与 %(b)s或%(c)s 反潜") % {"a": door_name_1, "b": door_name_2, "c": door_name_3})
                if self.five_mode:
                    result.append(_(u"%(a)s 与 %(b)s或%(c)s或%(d)s 反潜") % {"a":door_name_1, "b": door_name_2, "c": door_name_3, "d": door_name_4})            
                if self.six_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_1)
                if self.seven_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_2)
                if self.eight_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_3)
                if self.nine_mode:
                    result.append(_(u"%s 读头间反潜") % door_name_4)

            return result and u','.join(result) or _(u'暂无反潜设置信息')

        class Admin(CachingModel.Admin):
            menu_group = 'acc_doorset'
            disabled_perms = ['clear_accantiback', 'dataimport_accantiback', 'dataexport_accantiback', 'view_accantiback']
            parent_model = 'DoorSetPage'
            menu_focus = 'DoorSetPage'
            menu_index = 100023
            help_text = _(u"如果设备通讯不成功或者其他原因导致服务器无法获取设备参数，那么该设备将无法进行反潜设置。<br>已经设置过反潜功能的控制器将不会出现在设备列表中。<br>单门双向、两门双向控制器可设置读头间反潜和门之间的反潜，两门单向、四门单向控制器只能设置门之间的反潜。")
            list_display = ('device', 'antiback_details')
            newadded_column = {'antiback_details': 'get_details'}
            position = _(u'门禁系统 -> 门设置 -> 反潜设置')

        class Meta:
            app_label = 'iaccess'
            db_table = 'acc_antiback'
            verbose_name = _(u'反潜设置')
            verbose_name_plural = verbose_name
