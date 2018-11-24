#! /usr/bin/env python
#coding=utf-8

from django.db import models
from django.conf import settings
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _

class AccWiegandFmt(CachingModel):
        u"""
        韦根卡格式
        """
        wiegand_name = models.CharField(_(u'韦根卡格式名称'), null=False, max_length=30, blank=False, default="")
        wiegand_count = models.IntegerField(_(u'总位数'), null=True, blank=True, editable=True)
        odd_start = models.IntegerField(_(u'奇校验开始位'), null=True, blank=True, editable=True)
        odd_count = models.IntegerField(_(u'奇校验结束位'), null=True, blank=True, editable=True)
        even_start = models.IntegerField(_(u'偶校验开始位'), null=True, blank=True, editable=True)
        even_count = models.IntegerField(_(u'偶校验结束位'), null=True, blank=True, editable=True)
        cid_start = models.IntegerField(_(u'CID开始位'), null=True, blank=True, editable=True)#CID (Character identifier)就是字符识别码 or control id
        cid_count = models.IntegerField(_(u'CID结束位'), null=True, blank=True, editable=True)
        comp_start = models.IntegerField(_(u'公司码开始位'), null=True, blank=True, editable=True)
        comp_count = models.IntegerField(_(u'公司码结束位'), null=True, blank=True, editable=True)

        def __unicode__(self):
            return self.wiegand_name

        @staticmethod
        def clear():
            for obj in AccWiegandFmt.objects.all():
                print 'wiegandfmt_set=', obj.wiegandfmt_set.all()
                print 'obj=', obj
                if obj.wiegandfmt_set.all():
                    obj.wiegandfmt_set.clear()

                print 'wiegandfmt_set=', obj.wiegandfmt_set.all()

                obj.delete(init=True)

        def save(self, *args, **kwargs):
            super(AccWiegandFmt, self).save(log_msg=False)

        def delete(self, *args, **kwargs):
            init = 'init' in kwargs.keys() and kwargs['init'] or False
            if init:
                if self.id not in [1, 2]:
                    super(AccWiegandFmt, self).delete()
            else:
                if self.id in [1, 2]:
                    raise Exception(_(u"初始化的数据 %s 不能删除" % self.wiegand_name))

                if self.wiegandfmt_set.all():
                    raise Exception(_(u"%s 正在使用中，不能删除！") % self.wiegand_name)

                super(AccWiegandFmt, self).delete()

        def data_valid(self, sendtype):
            tmp = AccWiegandFmt.objects.filter(wiegand_name=self.wiegand_name.strip())
            if tmp and tmp[0] != self:   #新增时不能重复。
                raise Exception(_(u'内容：%s 设置重复！')%self.wiegand_name)

        class Admin(CachingModel.Admin):
            visible = False
            parent_model = 'DoorSetPage'
            menu_group = 'acc_doorset_'#不显示
            disabled_perms = ['clear_accwiegandfmt', 'dataimport_accwiegandfmt', 'dataexport_accwiegandfmt', 'view_accwiegandfmt']
            menu_focus = 'DoorSetPage'
            position = _(u'门禁系统 -> 门设置 -> 韦根卡格式')
            menu_index = 100026
            list_display = ('wiegand_name',)#,'wiegandfmt'
            initial_data = [
                {'id':1, 'wiegand_name': _(u'标准韦根26'), 'wiegand_count':26, 'odd_start':1, 'odd_count':10, 'even_start':11, 'even_count':26},
                {'id':2, 'wiegand_name': _(u'标准韦根34'), 'wiegand_count':34, 'odd_start':1, 'odd_count':10, 'even_start':11, 'even_count':34}
            ]
        class Meta:
            app_label = 'iaccess'
            db_table = 'acc_wiegandfmt'
            verbose_name = _(u'韦根卡格式')
            verbose_name_plural = verbose_name
