#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from base.operation import Operation
from mysite.personnel.models.model_area import AreaForeignKey
from django.utils.translation import ugettext_lazy as _
from dbapp import data_edit
from mysite import settings
import datetime
import os
from base.cached_model import SAVETYPE_EDIT


class AccMap(CachingModel):
    u"""
    电子地图 top和left均为0
    """
    map_name = models.CharField(_(u'地图名称'), max_length=30, null=True, blank=False, default="", unique=True)
    map_path = models.CharField(_(u'地图路径'), max_length=30, null=True, blank=True, default="", editable=True)#路径
    #mdoors = models.ManyToManyField(AccDoor, verbose_name=_(u'门信息'), null=True, blank=True, default="", editable=False)#当前Map和Door为一对多关系，ManyToMany为后期做一个门可放到多个地图上预留
    area = AreaForeignKey(verbose_name=_(u'所属区域'), null=True, blank=False, editable=True)# default=1, 
    width = models.FloatField(_(u'宽度'), null=True, blank=True, default=0, editable=False)#单位px 0为无效值
    height = models.FloatField(_(u'高度'), null=True, blank=True, default=0, editable=False)#px 0为无效值

    def __unicode__(self):
        return self.map_name
    
    def data_valid(self, sendtype):
        tmp = AccMap.objects.filter(map_name=self.map_name.strip()) 
        if tmp and tmp[0] != self:#新增时(该名称的记录已存在且不是编辑）
            raise Exception(_(u'内容：%s 设置重复！')%self.map_name)
        

    def save(self, **kargs):
        #if sendtype == SAVETYPE_EDIT:
        #编辑时如果修改了区域则将该地图上门清空
        if self.pk:
            tmp = AccMap.objects.get(pk=self.pk)
            if tmp.area != self.area:
                tmp.accdoor_set.clear()
                tmp.accmapdoorpos_set.clear()
            #用户选择不修改路径，则将保留原有图片
            if not self.map_path:
                self.map_path = tmp.map_path or u'/files/map/%s.jpg' % self.pk
                
        super(AccMap, self).save(**kargs)
    def delete(self):
        #删除地图记录时需要删除地图本身
        file = os.getcwd() + self.map_path
        try:
            os.remove(file)
        except:
            #print_exc()
            pass#如果没有地图直接略过
        
        if self.accdoor_set.all():#避免删除地图时删除门
            self.accdoor_set.clear()
        
        super(AccMap, self).delete()
        
    class OpAddDoorsOntoMap(Operation):
        verbose_name = _(u"添加门")
        def action(self):
            pass
    
    class OpRemoveDoorFromMap(Operation):
        verbose_name = _(u"移除门")
        def action(self):
            pass
    
    class OpSaveMapDoorPos(Operation):
        verbose_name = _(u"保存位置信息")
        def action(self):
            pass
    
    class OpEnlargeMapDoor(Operation):
        verbose_name = _(u"放大")
        def action(self):
            pass
        
    class OpReduceMapDoor(Operation):
        verbose_name = _(u"缩小")
        def action(self):
            pass
        
    class Admin(CachingModel.Admin):
        #visible = False权限也无法显示
        menu_index = 100053
        menu_group = 'acc_monitor'
        parent_model = 'ElectroMapPage'
        disabled_perms = ['clear_accmap', 'dataimport_accmap', 'view_accmap', 'dataexport_accmap']
        list_display = ('map_name', 'map_path')
        position = _(u'门禁系统 -> 实时监控 -> 电子地图')
        menu_focus = 'RTMonitorPage'
        help_text = _(u"更改地图所属区域将清空地图上所有门！<br>(上传地图最佳尺寸600*400像素,最佳大小300KB)")

    class Meta:
        app_label = 'iaccess'
        db_table = 'acc_map'
        verbose_name = _(u'电子地图')
        verbose_name_plural = verbose_name


def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, AccMap):
        from mysite.personnel.models.model_emp import saveUploadImage
        map_path = settings.ADDITION_FILE_ROOT + "map/"
        if saveUploadImage(request, str(newObj.pk) + ".jpg", map_path):
            newObj.map_path = "/files/map/" + str(newObj.pk) + ".jpg"#files为实际路径(src中的‘file’用来处理url（dbapp中）定位静态文件，而非实际路径)
            newObj.save()
        

data_edit.post_check.connect(DataPostCheck)
