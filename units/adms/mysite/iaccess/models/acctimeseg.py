# -*- coding: utf-8 -*-
from django.db import models
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _
from dbapp.models import TimeField2
from dbapp import data_edit

import datetime

MAX_TIMESEG_COUNT = 255#支持设置的时间段的最大数量。

#用户验证两个时间点的有效性（开始时间和结束时间）
def check_start_end_time(start_time, start_vname, end_time, end_vname):
    zero = datetime.time(0, 0)
    if start_time > end_time:
        raise Exception(_(u'%(f)s 不能大于 %(ev)s') % {"f":start_vname, "ev": end_vname})
    elif start_time == end_time:
        if end_time != zero:
            raise Exception(_(u'%(f)s 不能等于 %(ev)s') % {"f":start_vname, "ev":end_vname})
    else:
        pass

#用于验证时间段的有效性的算法
def check_timeseg(start1, start1_vname, end1, end1_vname, start2, start2_vname, end2, end2_vname, start3, start3_vname, end3, end3_vname):
    #处理两个时间点的有效性--#处理时间区间间的有效性-
    check_start_end_time(start1, start1_vname, end1, end1_vname)
    check_start_end_time(start2, start2_vname, end2, end2_vname)
    check_start_end_time(start3, start3_vname, end3, end3_vname)
    
    #处理时间区间间的有效性-下一个时区的开始时间要大于前一个的结束时间（都为0时可以等于），后面的全为0， 那么也可能小于
    zero = datetime.time(0, 0)
    if start1 == zero and end1 == zero:
        if start2 != zero:
            raise Exception(_(u'%s 填写错误，请先使用时间区间1') % start2_vname)
        if end2 != zero:
            raise Exception(_(u'%s 填写错误，请先使用时间区间1') % end2_vname)
        if start3 != zero:
            raise Exception(_(u'%s 填写错误，请先使用时间区间1') % start3_vname)
        if end3 != zero:
            raise Exception(_(u'%s 填写错误，请先使用时间区间1') % end3_vname)

    elif start2 == zero and end2 == zero:##时间区间1使用且合法（已check）二全为0，则不能使用三
        if start3 != zero:
            raise Exception(_(u'%s 填写错误，请先使用时间区间2') % start3_vname)
        if end3 != zero:
            raise Exception(_(u'%s 填写错误，请先使用时间区间2') % end3_vname)

    elif start2 <= end1:#2也使用了(1的结尾此时肯定不为0,2的结尾也肯定不为0)
        raise Exception(_(u'%(a)s 不能小于等于 %(b)s') % {"a": start2_vname, "b": end1_vname})

    elif end3 != zero and start3 <= end2:#使用全部三个区间时，验证第三个时间区间的有效性。#start3 != zero and 去掉该条件，否则会出现时间区间1时间设置为09：:0-12:00 时间区间2设置为12:01-18:00，时间区间3可以设置为00：00-10:00
        raise Exception(_(u'%(a)s 不能小于等于 %(b)s') % {"a": start3_vname, "b": end2_vname})
                
    #可以选择只使用前两个时间区间，最后一个留空。
ACCESS_TIMESEG = 1            
ELEVATOR_TIMESEG = 2  

TIMESEG_TYPE_CHOICES =(
    (ACCESS_TIMESEG,_(u'门禁时间段')),
    (ELEVATOR_TIMESEG,_(u'梯控时间段')),
)

class AccTimeSeg(CachingModel):
    """
    时间段
    """
    timeseg_name = models.CharField(_(u'时间段名称'), null=False, max_length=30, blank=False, unique=True)
    memo = models.CharField(_(u'备注'), null=True, max_length=70, blank=True, default='')
    sunday_start1 = TimeField2(_(u'周日时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    sunday_end1 = TimeField2(_(u'周日时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    sunday_start2 = TimeField2(_(u'周日时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    sunday_end2 = TimeField2(_(u'周日时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    sunday_start3 = TimeField2(_(u'周日时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    sunday_end3 = TimeField2(_(u'周日时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    monday_start1 = TimeField2(_(u'周一时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    monday_end1 = TimeField2(_(u'周一时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    monday_start2 = TimeField2(_(u'周一时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    monday_end2 = TimeField2(_(u'周一时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    monday_start3 = TimeField2(_(u'周一时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    monday_end3 = TimeField2(_(u'周一时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    tuesday_start1 = TimeField2(_(u'周二时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    tuesday_end1 = TimeField2(_(u'周二时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    tuesday_start2 = TimeField2(_(u'周二时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    tuesday_end2 = TimeField2(_(u'周二时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    tuesday_start3 = TimeField2(_(u'周二时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    tuesday_end3 = TimeField2(_(u'周二时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    wednesday_start1 = TimeField2(_(u'周三时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    wednesday_end1 = TimeField2(_(u'周三时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    wednesday_start2 = TimeField2(_(u'周三时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    wednesday_end2 = TimeField2(_(u'周三时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    wednesday_start3 = TimeField2(_(u'周三时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    wednesday_end3 = TimeField2(_(u'周三时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    thursday_start1 = TimeField2(_(u'周四时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    thursday_end1 = TimeField2(_(u'周四时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    thursday_start2 = TimeField2(_(u'周四时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    thursday_end2 = TimeField2(_(u'周四时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    thursday_start3 = TimeField2(_(u'周四时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    thursday_end3 = TimeField2(_(u'周四时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    friday_start1 = TimeField2(_(u'周五时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    friday_end1 = TimeField2(_(u'周五时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    friday_start2 = TimeField2(_(u'周五时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    friday_end2 = TimeField2(_(u'周五时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    friday_start3 = TimeField2(_(u'周五时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    friday_end3 = TimeField2(_(u'周五时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    saturday_start1 = TimeField2(_(u'周六时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    saturday_end1 = TimeField2(_(u'周六时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    saturday_start2 = TimeField2(_(u'周六时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    saturday_end2 = TimeField2(_(u'周六时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    saturday_start3 = TimeField2(_(u'周六时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    saturday_end3 = TimeField2(_(u'周六时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype1_start1 = TimeField2(_(u'假日类型1时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype1_end1 = TimeField2(_(u'假日类型1时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype1_start2 = TimeField2(_(u'假日类型1时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype1_end2 = TimeField2(_(u'假日类型1时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype1_start3 = TimeField2(_(u'假日类型1时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype1_end3 = TimeField2(_(u'假日类型1时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype2_start1 = TimeField2(_(u'假日类型2时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype2_end1 = TimeField2(_(u'假日类型2时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype2_start2 = TimeField2(_(u'假日类型2时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype2_end2 = TimeField2(_(u'假日类型2时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype2_start3 = TimeField2(_(u'假日类型2时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype2_end3 = TimeField2(_(u'假日类型2时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype3_start1 = TimeField2(_(u'假日类型3时间区间1开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype3_end1 = TimeField2(_(u'假日类型3时间区间1结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype3_start2 = TimeField2(_(u'假日类型3时间区间2开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype3_end2 = TimeField2(_(u'假日类型3时间区间2结束时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype3_start3 = TimeField2(_(u'假日类型3时间区间3开始时间'), null=False, default='00:00', blank=False, editable=True)
    holidaytype3_end3 = TimeField2(_(u'假日类型3时间区间3结束时间'), null=False, default='00:00', blank=False, editable=True)

    timeseg_type = models.IntegerField(_(u'时间段类型'), choices=TIMESEG_TYPE_CHOICES, default=1, null=False, blank=True, editable=True,)

    def __unicode__(self):
        return self.timeseg_name

    def data_valid(self, sendtype):
        tmp = AccTimeSeg.objects.filter(timeseg_name=self.timeseg_name.strip())
        
        if self.id == 1:

            raise Exception(_(u'初始化的数据 %s 不能编辑！') % self.timeseg_name)

        
        if tmp and tmp[0] != self:   #新增时不能重复。
            raise Exception(_(u'内容：%s 设置重复！')%self.timeseg_name)


        if AccTimeSeg.objects.count() == MAX_TIMESEG_COUNT:#默认255
            raise Exception(_(u'时间段不能超过%s个') % MAX_TIMESEG_COUNT)

        #verbose_name
        sun_start1_vname = unicode(AccTimeSeg._meta.get_field("sunday_start1").verbose_name)
        sun_end1_vname = unicode(AccTimeSeg._meta.get_field("sunday_end1").verbose_name)
        sun_start2_vname = unicode(AccTimeSeg._meta.get_field("sunday_start2").verbose_name)
        sun_end2_vname = unicode(AccTimeSeg._meta.get_field("sunday_end2").verbose_name)
        sun_start3_vname = unicode(AccTimeSeg._meta.get_field("sunday_start3").verbose_name)
        sun_end3_vname = unicode(AccTimeSeg._meta.get_field("sunday_end3").verbose_name)
        check_timeseg(self.sunday_start1, sun_start1_vname, self.sunday_end1, sun_end1_vname, self.sunday_start2, sun_start2_vname, self.sunday_end2, sun_end2_vname, self.sunday_start3, sun_start3_vname, self.sunday_end3, sun_end3_vname)

        mon_start1_vname = unicode(AccTimeSeg._meta.get_field("monday_start1").verbose_name)
        mon_end1_vname = unicode(AccTimeSeg._meta.get_field("monday_end1").verbose_name)
        mon_start2_vname = unicode(AccTimeSeg._meta.get_field("monday_start2").verbose_name)
        mon_end2_vname = unicode(AccTimeSeg._meta.get_field("monday_end2").verbose_name)
        mon_start3_vname = unicode(AccTimeSeg._meta.get_field("monday_start3").verbose_name)
        mon_end3_vname = unicode(AccTimeSeg._meta.get_field("monday_end3").verbose_name)
        check_timeseg(self.monday_start1, mon_start1_vname, self.monday_end1, mon_end1_vname, self.monday_start2, mon_start2_vname, self.monday_end2, mon_end2_vname, self.monday_start3, mon_start3_vname, self.monday_end3, mon_end3_vname)

        tues_start1_vname = unicode(AccTimeSeg._meta.get_field("tuesday_start1").verbose_name)
        tues_end1_vname = unicode(AccTimeSeg._meta.get_field("tuesday_end1").verbose_name)
        tues_start2_vname = unicode(AccTimeSeg._meta.get_field("tuesday_start2").verbose_name)
        tues_end2_vname = unicode(AccTimeSeg._meta.get_field("tuesday_end2").verbose_name)
        tues_start3_vname = unicode(AccTimeSeg._meta.get_field("tuesday_start3").verbose_name)
        tues_end3_vname = unicode(AccTimeSeg._meta.get_field("tuesday_end3").verbose_name)
        check_timeseg(self.tuesday_start1, tues_start1_vname, self.tuesday_end1, tues_end1_vname, self.tuesday_start2, tues_start2_vname, self.tuesday_end2, tues_end2_vname, self.tuesday_start3, tues_start3_vname, self.tuesday_end3, tues_end3_vname)

        wednes_start1_vname = unicode(AccTimeSeg._meta.get_field("wednesday_start1").verbose_name)
        wednes_end1_vname = unicode(AccTimeSeg._meta.get_field("wednesday_end1").verbose_name)
        wednes_start2_vname = unicode(AccTimeSeg._meta.get_field("wednesday_start2").verbose_name)
        wednes_end2_vname = unicode(AccTimeSeg._meta.get_field("wednesday_end2").verbose_name)
        wednes_start3_vname = unicode(AccTimeSeg._meta.get_field("wednesday_start3").verbose_name)
        wednes_end3_vname = unicode(AccTimeSeg._meta.get_field("wednesday_end3").verbose_name)
        check_timeseg(self.wednesday_start1, wednes_start1_vname, self.wednesday_end1, wednes_end1_vname, self.wednesday_start2, wednes_start2_vname, self.wednesday_end2, wednes_end2_vname, self.wednesday_start3, wednes_start3_vname, self.wednesday_end3, wednes_end3_vname)

        thurs_start1_vname = unicode(AccTimeSeg._meta.get_field("thursday_start1").verbose_name)
        thurs_end1_vname = unicode(AccTimeSeg._meta.get_field("thursday_end1").verbose_name)
        thurs_start2_vname = unicode(AccTimeSeg._meta.get_field("thursday_start2").verbose_name)
        thurs_end2_vname = unicode(AccTimeSeg._meta.get_field("thursday_end2").verbose_name)
        thurs_start3_vname = unicode(AccTimeSeg._meta.get_field("thursday_start3").verbose_name)
        thurs_end3_vname = unicode(AccTimeSeg._meta.get_field("thursday_end3").verbose_name)
        check_timeseg(self.thursday_start1, thurs_start1_vname, self.thursday_end1, thurs_end1_vname, self.thursday_start2, thurs_start2_vname, self.thursday_end2, thurs_end2_vname, self.thursday_start3, thurs_start3_vname, self.thursday_end3, thurs_end3_vname)

        fri_start1_vname = unicode(AccTimeSeg._meta.get_field("friday_start1").verbose_name)
        fri_end1_vname = unicode(AccTimeSeg._meta.get_field("friday_end1").verbose_name)
        fri_start2_vname = unicode(AccTimeSeg._meta.get_field("friday_start2").verbose_name)
        fri_end2_vname = unicode(AccTimeSeg._meta.get_field("friday_end2").verbose_name)
        fri_start3_vname = unicode(AccTimeSeg._meta.get_field("friday_start3").verbose_name)
        fri_end3_vname = unicode(AccTimeSeg._meta.get_field("friday_end3").verbose_name)
        check_timeseg(self.friday_start1, fri_start1_vname, self.friday_end1, fri_end1_vname, self.friday_start2, fri_start2_vname, self.friday_end2, fri_end2_vname, self.friday_start3, fri_start3_vname, self.friday_end3, fri_end3_vname)

        satur_start1_vname = unicode(AccTimeSeg._meta.get_field("saturday_start1").verbose_name)
        satur_end1_vname = unicode(AccTimeSeg._meta.get_field("saturday_end1").verbose_name)
        satur_start2_vname = unicode(AccTimeSeg._meta.get_field("saturday_start2").verbose_name)
        satur_end2_vname = unicode(AccTimeSeg._meta.get_field("saturday_end2").verbose_name)
        satur_start3_vname = unicode(AccTimeSeg._meta.get_field("saturday_start3").verbose_name)
        satur_end3_vname = unicode(AccTimeSeg._meta.get_field("saturday_end3").verbose_name)
        check_timeseg(self.saturday_start1, satur_start1_vname, self.saturday_end1, satur_end1_vname, self.saturday_start2, satur_start2_vname, self.saturday_end2, satur_end2_vname, self.saturday_start3, satur_start3_vname, self.saturday_end3, satur_end3_vname)

        ht1_start1_vname = unicode(AccTimeSeg._meta.get_field("holidaytype1_start1").verbose_name)
        ht1_end1_vname = unicode(AccTimeSeg._meta.get_field("holidaytype1_end1").verbose_name)
        ht1_start2_vname = unicode(AccTimeSeg._meta.get_field("holidaytype1_start2").verbose_name)
        ht1_end2_vname = unicode(AccTimeSeg._meta.get_field("holidaytype1_end2").verbose_name)
        ht1_start3_vname = unicode(AccTimeSeg._meta.get_field("holidaytype1_start3").verbose_name)
        ht1_end3_vname = unicode(AccTimeSeg._meta.get_field("holidaytype1_end3").verbose_name)
        check_timeseg(self.holidaytype1_start1, ht1_start1_vname, self.holidaytype1_end1, ht1_end1_vname, self.holidaytype1_start2, ht1_start2_vname, self.holidaytype1_end2, ht1_end2_vname, self.holidaytype1_start3, ht1_start3_vname, self.holidaytype1_end3, ht1_end3_vname)

        ht2_start1_vname = unicode(AccTimeSeg._meta.get_field("holidaytype2_start1").verbose_name)
        ht2_end1_vname = unicode(AccTimeSeg._meta.get_field("holidaytype2_end1").verbose_name)
        ht2_start2_vname = unicode(AccTimeSeg._meta.get_field("holidaytype2_start2").verbose_name)
        ht2_end2_vname = unicode(AccTimeSeg._meta.get_field("holidaytype2_end2").verbose_name)
        ht2_start3_vname = unicode(AccTimeSeg._meta.get_field("holidaytype2_start3").verbose_name)
        ht2_end3_vname = unicode(AccTimeSeg._meta.get_field("holidaytype2_end3").verbose_name)
        check_timeseg(self.holidaytype2_start1, ht2_start1_vname, self.holidaytype2_end1, ht2_end1_vname, self.holidaytype2_start2, ht2_start2_vname, self.holidaytype2_end2, ht2_end2_vname, self.holidaytype2_start3, ht2_start3_vname, self.holidaytype2_end3, ht2_end3_vname)

        ht3_start1_vname = unicode(AccTimeSeg._meta.get_field("holidaytype3_start1").verbose_name)
        ht3_end1_vname = unicode(AccTimeSeg._meta.get_field("holidaytype3_end1").verbose_name)
        ht3_start2_vname = unicode(AccTimeSeg._meta.get_field("holidaytype3_start2").verbose_name)
        ht3_end2_vname = unicode(AccTimeSeg._meta.get_field("holidaytype3_end2").verbose_name)
        ht3_start3_vname = unicode(AccTimeSeg._meta.get_field("holidaytype3_start3").verbose_name)
        ht3_end3_vname = unicode(AccTimeSeg._meta.get_field("holidaytype3_end3").verbose_name)
        check_timeseg(self.holidaytype3_start1, ht3_start1_vname, self.holidaytype3_end1, ht3_end1_vname, self.holidaytype3_start2, ht3_start2_vname, self.holidaytype3_end2, ht3_end2_vname, self.holidaytype3_start3, ht3_start3_vname, self.holidaytype3_end3, ht3_end3_vname)


    #该方法只是删除了和该时间段对应的关系，不会删除关联的对象本身。
    #如某个door使用了该时间段，只会该door使用该时间段的字段置为None
    @staticmethod
    def clear():
        for obj in AccTimeSeg.objects.all():
            if obj.lockactive_set.all():
                obj.lockactive_set.clear()
            if obj.longopen_set.all():
                obj.longopen_set.clear()
            if obj.acclevelset_set.all():
                obj.lockactive_set.clear()
            if obj.accfirstopen_set.all():
                obj.accfirstopen_set.clear()

            obj.delete(init=True)


    def delete(self, *args, **kwargs):
        init = 'init' in kwargs.keys() and kwargs['init'] or False
        if init:
            if self.id != 1:
                from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL
                Devset = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL)
                for dev in Devset:
                    dev.del_timezone(self.id)
                super(AccTimeSeg, self).delete()
        else:
            if self.id == 1:

                raise Exception(_(u'初始化的数据 %s 不能删除') % self.timeseg_name)

            if self.acclevelset_set.all() or self.lockactive_set.all() or self.longopen_set.all() or self.accfirstopen_set.all():

                raise Exception(_(u'%s 正在使用中，不能删除！') % self.timeseg_name)

            from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL
            Devset = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL)
            for dev in Devset:
                dev.del_timezone(self.id)
            super(AccTimeSeg, self).delete()
    
    class Admin(CachingModel.Admin):
        menu_index = 10000
        default_give_perms = ['contenttypes.can_ElevatorTimesegSetPage']
        disabled_perms = ['clear_acctimeseg', 'dataimport_acctimeseg', 'view_acctimeseg']
        #hide_perms = ['add_acctimeseg','change_acctimeseg','delete_acctimeseg']
        #opt_perm_menu = { 'add_acctimeseg':"contenttypes.can_ElevatorTimesegSetPage", "change_acctimeseg":"contenttypes.can_ElevatorTimesegSetPage" }
        list_display = ("timeseg_name","timeseg_type", "memo")    
        query_fields = ('timeseg_name', 'memo')
        search_field = ('timeseg_name',)#过滤器
        help_text = _(u"如果开始时间不为‘00:00’，那么开始时间需小于结束时间。<br>如果不设置某个时间区间，只需默认开始时间和结束时间为‘00:00’到‘00:00’即可。")
        initial_data = [
        {'id': 1, 'timeseg_name':  _(u'24小时通行'), 'memo': _(u'24小时通行'), \
            'sunday_start1': '00:00', 'sunday_end1':'23:59', 'sunday_start2':'00:00', 'sunday_end2':'00:00', 'sunday_start3':'00:00', 'sunday_end3':'00:00', \
            'monday_start1':'00:00', 'monday_end1':'23:59', 'monday_start2':'00:00', 'monday_end2':'00:00', 'monday_start3':'00:00', 'monday_end3':'00:00', \
            'tuesday_start1':'00:00', 'tuesday_end1':'23:59', 'tuesday_start2':'00:00', 'tuesday_end2':'00:00', 'tuesday_start3':'00:00', 'tuesday_end3':'00:00', \
            'wednesday_start1':'00:00', 'wednesday_end1':'23:59', 'wednesday_start2':'00:00', 'wednesday_end2':'00:00', 'wednesday_start3':'00:00', 'wednesday_end3':'00:00', \
            'thursday_start1':'00:00', 'thursday_end1':'23:59', 'thursday_start2':'00:00', 'thursday_end2':'00:00', 'thursday_start3':'00:00', 'thursday_end3':'00:00', \
            'friday_start1':'00:00', 'friday_end1':'23:59', 'friday_start2':'00:00', 'friday_end2':'00:00', 'friday_start3':'00:00', 'friday_end3':'00:00', \
            'saturday_start1':'00:00', 'saturday_end1':'23:59', 'saturday_start2':'00:00', 'saturday_end2':'00:00', 'saturday_start3':'00:00', 'saturday_end3':'00:00', \
            'holidaytype1_start1':'00:00', 'holidaytype1_end1':'23:59', 'holidaytype1_start2':'00:00', 'holidaytype1_end2':'00:00', 'holidaytype1_start3':'00:00', 'holidaytype1_end3':'00:00', \
            'holidaytype2_start1':'00:00', 'holidaytype2_end1':'23:59', 'holidaytype2_start2':'00:00', 'holidaytype2_end2':'00:00', 'holidaytype2_start3':'00:00', 'holidaytype2_end3':'00:00', \
            'holidaytype3_start1':'00:00', 'holidaytype3_end1':'23:59', 'holidaytype3_start2':'00:00', 'holidaytype3_end2':'00:00', 'holidaytype3_start3':'00:00', 'holidaytype3_end3':'00:00'}
        ]
        position = _(u'门禁系统 -> 门禁时间段')
        
    class Meta:
        app_label = 'iaccess'
        db_table = 'acc_timeseg'
        verbose_name = _(u'门禁时间段')
        verbose_name_plural = verbose_name
        


def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, AccTimeSeg):
        from mysite.iclock.models.dev_comm_operate import sync_acctimeseg
        from mysite.iclock.models.model_device import decode_timeseg
        if oldObj is None:
            sync_acctimeseg(newObj)
        else:
            if decode_timeseg([oldObj]) != decode_timeseg([newObj]):    #edit deiff
                #print "newObj--", newObj
                sync_acctimeseg(newObj)

data_edit.post_check.connect(DataPostCheck)
