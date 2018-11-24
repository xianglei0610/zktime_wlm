#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel, Operation
from django.utils.translation import ugettext_lazy as _
from dbapp import data_edit
from django import forms
from mysite.utils import get_option
DLSTMODE_CHOICES = (
    (0, _(u'模式一')), (1, _(u'模式二'))
)

DICT_MONTH = (
    (1,_(u'一月')), (2,_(u'二月')), (3,_(u'三月')), (4,_(u'四月')), (5,_(u'五月')), (6,_(u'六月')),
     (7,_(u'七月')), (8,_(u'八月')), (9,_(u'九月')), (10,_(u'十月')), (11,_(u'十一月')), (12,_(u'十二月')),
)


DICT_WEEK = (
    (1,_(u'星期一')), (2,_(u'星期二')), (3,_(u'星期三')), (4,_(u'星期四')), (5,_(u'星期五')), (6,_(u'星期六')), (7,_(u'星期日')),
)

DICT_TH = (
    (1,_(u'第一个')), (2,_(u'第二个')), (3,_(u'第三个')), (4,_(u'第四个')), (5,_(u'第五个')),
)


class DSTime(CachingModel):
    u"""
           夏令时表
    """
    dst_name = models.CharField(verbose_name=_(u'夏令时名称'), max_length=20, null=False, blank=False, unique=True, editable=True)
    mode = models.SmallIntegerField(verbose_name=_(u'模式'), default=0, null=True, blank=False, editable=True, choices=DLSTMODE_CHOICES)
    start_time = models.CharField(verbose_name=_(u'开始时间'), max_length=20, null=True, blank=False, editable=True)
    end_time = models.CharField(verbose_name=_(u'结束时间'), max_length=20, null=True, blank=False, editable=True)

    def __unicode__(self):
        return self.dst_name

    def data_valid(self, sendtype):
        tmp = DSTime.objects.filter(dst_name=self.dst_name.strip())
        if tmp and tmp[0] != self:#新增时
            raise Exception(_(u'内容：%s 设置重复！')%self.dst_name)

    @staticmethod
    #初始化数据库
    def clear():
        for obj in DSTime.objects.all():
            if obj.device_set.all():
                obj.device_set.clear()
            obj.delete(init=True)


    def delete(self, *args, **kwargs):
        init = 'init' in kwargs.keys() and kwargs['init'] or False
        if init:
            super(DSTime, self).delete()
        else:
            from mysite.iclock.models.model_device import Device
            devs = Device.objects.filter(dstime=self)
            if devs:
                raise Exception(_(u'夏令时 %s 正在使用中，不能删除') %self.dst_name)
            super(DSTime, self).delete()

    class OpSetDSTime(Operation):
        from django.db import models
        help_text = _(u"将当前夏令时设置到某个或某些设备")
        verbose_name = _(u"设置夏令时")
        params = (
                ('devices', forms.CharField(label=_(u"设置夏令时"), required=False, widget=forms.TextInput)),
        )
        only_one_object=True

        def action(self, devices):
            from dbapp.modelutils import GetModel
            Device = GetModel("iclock","Device")
            devs_id = devices.split("-")[0:-1];
            devs = Device.objects.filter(id__in=devs_id)
            failed_devs = ""
            if devs:
                for dev in devs:
                    ret = dev.set_dstime(self.object)
                    if ret < 0:
                        failed_devs = failed_devs+dev.alias+", "
                    else:
                        dev.dstime = self.object
                        dev.save(force_update=True)
                if failed_devs:
                    failed_devs = failed_devs[0:-2]
                    raise Exception(_(u'设备%s夏令时设置失败！') % failed_devs)
    def get_start_time(self):
        if self.mode == 0:
            return self.start_time
        else:
            return show_dstime(self.start_time)

    def get_end_time(self):
        if self.mode == 0:
            return self.end_time
        else:
            return show_dstime(self.end_time)

    class Admin(CachingModel.Admin):
        from django.conf import settings
        help_text = _(u'夏令时')
        visible = False#get_option("IACCESS")#暂只有门禁使用
        list_display = ('dst_name', 'mode', 'get_start_time', 'get_end_time')
        query_fields = ['dst_name', 'mode']

    class Meta:
        app_label = 'iclock'
        db_table = 'iclock_dstime'
        verbose_name = _(u'夏令时')
        verbose_name_plural = verbose_name

def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    try:
        if isinstance(newObj, DSTime) and oldObj:
            from mysite.iclock.models.model_device import Device
            devs = Device.objects.filter(dstime=oldObj)
            if devs:
                if oldObj.start_time != newObj.start_time or oldObj.end_time != newObj.end_time:
                    for dev in devs:
                        dev.set_dstime(newObj,False)
    except:
        from traceback import print_exc
        print_exc()
data_edit.post_check.connect(DataPostCheck)

def show_dstime(time):
    from base.options import options
    language = options['base.language']
    time_st = time.split(" ")
    time_st_mon = time_st[0].split("-")[0]
    time_st_w = time_st[0].split("-")[1]
    time_st_d = time_st[0].split("-")[2]
    time_st_h = time_st[1].split(":")[0]
    time_st_mun = time_st[1].split(":")[1]
    if language == 'zh-cn':
        return _(u'%(a)s %(b)s %(c)s %(d)s:%(e)s') % {"a": dict(DICT_MONTH)[int(time_st_mon)], "b": dict(DICT_TH)[int(time_st_w)], "c": dict(DICT_WEEK)[int(time_st_d)], "d": time_st_h, "e": time_st_mun}
    else:
        return _(u'At %(a)s:%(b)s the %(c)s %(d)s in %(e)s') % {"a": time_st_h, "b": time_st_mun, "c": dict(DICT_TH)[int(time_st_w)], "d": dict(DICT_WEEK)[int(time_st_d)], "e": dict(DICT_MONTH)[int(time_st_mon)]}

