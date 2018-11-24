# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from base.cached_model import CachingModel

GENDER_CHOICES = (
    ('M', _(u'男')),
    ('F', _(u'女')),
)

HOLIDAY_NATIONS = (
    ('0', _(u'汉族')),
    ('1', _(u'蒙古族')),
    ('2', _(u'回族')),
    ('3', _(u'藏族')),
    ('4', _(u'维吾尔族')),
    ('5', _(u'苗族')),
    ('6', _(u'彝族')),
    ('7', _(u'壮族')),
    ('8', _(u'布依族')),
    ('9', _(u'朝鲜族')),
    ('10', _(u'满族')),
    ('11', _(u'侗族')),
    ('12', _(u'瑶族')),
    ('13', _(u'白族')),
    ('14', _(u'土家族')),
    ('15', _(u'哈尼族')),
    ('16', _(u'哈萨克族')),
    ('17', _(u'傣族')),
    ('18', _(u'黎族')),
    ('19', _(u'僳僳族')),
    ('20', _(u'佤族')),
    ('21', _(u'畲族')),
    ('22', _(u'高山族')),
    ('23', _(u'拉祜族')),
    ('24', _(u'水族')),
    ('25', _(u'东乡族')),
    ('26', _(u'纳西族')),
    ('27', _(u'景颇族')),
    ('28', _(u'柯尔克孜族')),
    ('29', _(u'土族')),
    ('30', _(u'达斡尔族')),
    ('31', _(u'仫佬族')),
    ('32', _(u'羌族')),
    ('33', _(u'布朗族')),
    ('34', _(u'撒拉族')),
    ('35', _(u'仡佬族')),
    ('36', _(u'锡伯族')),
    ('37', _(u'阿昌族')),
    ('38', _(u'普米族')),
    ('39', _(u'塔吉克族')),
    ('40', _(u'怒族')),
    ('41', _(u'乌孜别克族')),
    ('42', _(u'俄罗斯族')),
    ('43', _(u'鄂温克族')),
    ('44', _(u'德昂族')),
    ('45', _(u'保安族')),
    ('46', _(u'裕固族')),
    ('47', _(u'京族')),
    ('48', _(u'塔塔尔族')),
    ('49', _(u'独龙族')),
    ('50', _(u'鄂伦春族')),
    ('51', _(u'赫哲族')),
    ('52', _(u'门巴族')),
    ('53', _(u'珞巴族')),
    ('54', _(u'基诺族')),

)
YESORNO = (
    (0, _(u'否')),
    (1, _(u'是')),
)
    ##节假日表##
class Holiday(CachingModel):
    id = models.AutoField(primary_key=True, null=False, db_column="HolidayID", editable=False)
    name = models.CharField(_(u'节假日名称'), db_column="HolidayName", max_length=20, null=False, blank=False)
    year = models.SmallIntegerField(_(u'年'), db_column="HolidayYear", null=True, blank=True, editable=False)
    month = models.SmallIntegerField(_(u'月'), db_column="HolidayMonth", null=True, blank=True, editable=False)
    day = models.SmallIntegerField(_(u'日'), db_column="HolidayDay", null=True, default=1, blank=True, editable=False)
    start_time = models.DateField(_(u'开始时间'), db_column="StartTime")
    duration = models.SmallIntegerField(_(u'持续时间(天)'), db_column="Duration", null=False, blank=False, default=1)
    IsCycle = models.SmallIntegerField(_(u'是否按年循环'), null=False, blank=False, default=0, choices=YESORNO, editable=False)
    type = models.SmallIntegerField(_(u'节假日类型'), db_column="HolidayType", null=True, blank=True, editable=False)
    gender = models.CharField(_(u'节假日性别'), max_length=4, null=True, db_column="XINBIE", editable=False, blank=True, choices=GENDER_CHOICES,)
    nation = models.CharField(_(u'节假日民族'), max_length=50, db_column="MINZU", null=True, editable=False, blank=True, choices=HOLIDAY_NATIONS)
    def save(self, *args, **kwargs):
        h = Holiday.objects.filter(name__exact=self.name,start_time__exact= self.start_time)
        if h and h[0].pk!=self.pk:
            raise Exception(_(u"节假日 %s 已经存在!")%self.name)
        if self.IsCycle == 1:
            self.year = None
        else:
            if type(self.start_time) != datetime.date:
                self.start_time = datetime.datetime.strptime(self.start_time, "%Y-%m-%d").date()
            self.year = self.start_time.year
        self.month = self.start_time.month
        self.day = self.start_time.day
        super(Holiday, self).save()
        from mysite.att.calculate.global_cache import C_HOLIDAY
        C_HOLIDAY.refresh()
        
    def delete(self):
        super(Holiday, self).delete()
        from mysite.att.calculate.global_cache import C_HOLIDAY
        C_HOLIDAY.refresh()

    def __unicode__(self):
        return unicode(u"%s" % (self.name))
    class Admin(CachingModel.Admin):
        from dbapp.widgets import ZBaseSmallIntegerWidget, ZBaseHolidayIntegerWidget
        import datetime
        list_display = ('name', 'start_time', 'duration')
        initial_data = [
                {'id':1, 'name': _(u'元旦节'), 'month':1, 'day':1, 'duration':3, 'IsCycle':1, 'start_time':datetime.date(2010, 01, 01)},
                {'id':2, 'name': _(u'中国国庆节'), 'month':10, 'day':1, 'duration':7, 'IsCycle':1, 'start_time':datetime.date(2010, 10, 01)}
                ]
        menu_index = 13
        default_widgets = {'year':ZBaseSmallIntegerWidget,

        'duration':ZBaseHolidayIntegerWidget, }
        disabled_perms = ['dataimport_holiday']
    class Meta:
        app_label = 'att'
        db_table = 'holidays'
        verbose_name = _(u'节假日')
        verbose_name_plural = verbose_name
        unique_together = (("name", "start_time"),)

