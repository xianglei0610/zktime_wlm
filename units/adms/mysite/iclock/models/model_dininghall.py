#coding=utf-8
from django.db import models, connection
from base.models import CachingModel#, Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from base.operation import Operation, ModelOperation
from base.models import AppOperation
from dbapp.widgets import ZBaseIntegerWidget,ZBase5IntegerWidget
class Dininghall(CachingModel):
    code = models.IntegerField(verbose_name=_(u'餐厅编号'),blank=False,max_length=20)
    name = models.CharField(verbose_name=_(u"餐厅名称"),max_length=100,blank=False)
    remark = models.CharField(verbose_name=_(u"备注"),max_length=200, blank=True)
    
    def __unicode__(self):
        return u"%s"%self.name#can't use lazy here
    
    def data_valid(self, sendtype):
        """验证"""
        try:
            int(self.code)
        except:
            raise Exception(_(u'编号必须是整数'))
        if self.code == 0:
            raise Exception(_(u'编号不能为0'))
        
        tmp = Dininghall.objects.filter(code=self.code)
        if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
            raise Exception(_(u'编号: %s 已存在') % self.code)
    
    def delete(self):
        if self.id <> 1:
           super(Dininghall, self).delete()
        
    class _delete(Operation):
        help_text = _(u"删除选定记录") #删除选定的记录
        verbose_name = _(u"删除")
        def action(self):
            from mysite.iclock.models.model_device import Device
            from mysite.pos.models.model_cardmanage import CardManage
            from mysite.pos.models import ICConsumerList 
            obj_consum_list = ICConsumerList.objects.filter(dining = self.object)
            obj_card_manage = CardManage.objects.filter(dining = self.object)
            obj = Device.objects.filter(dining = self.object)
            if obj:
               raise Exception(_(u'当前餐厅已有在使用设备，不可删除！'))
            if obj_consum_list:
               raise Exception(_(u'当前餐厅已存在消费记录，不可删除！'))
            if obj_card_manage:
               raise Exception(_(u'当前餐厅已有在使用管理卡，不可删除！'))
            if self.object.id <> 1:
              super(Dininghall, self.object).delete()
            else:
                raise Exception(_(u'系统默认餐厅不允许删除！'))
                
        
    
    class Admin(CachingModel.Admin):
        #default_give_perms = ["personnel.browse_issuecard", "att.browse_setuseratt"]
#        layout_types = ["table"]#显示方式
        sort_fields = ["code",]#对列进行排序
        app_menu = "pos"
        menu_group = 'pos'
        visible=False
        cache = 3600
        menu_index = 32#在菜单按钮的位置
        query_fields = ['code','name','remark']#显示的查询项
        
        list_display = ['code','name','remark']#显示的列
        adv_fields = ['code','name','remark']#高级查询显示的列
        default_give_perms = ["contenttypes.can_PosFormPage",]
        help_text = _(u'下述所填项目中，餐厅编号不能为空且不能重复,系统自动验证：')
        #import_fields = ['name','code','desc',]#可导入的字段
        default_widgets={'code':ZBase5IntegerWidget}
        @staticmethod
        def initial_data():#初始化数据
            if Dininghall.objects.count() == 0:
                Dininghall(code=1,name=u"%s"%_(u"总部")).save()
            
    class Meta:
        app_label = 'iclock'#属于的app
        verbose_name = _(u"餐厅资料")#上部按钮
        verbose_name_plural = verbose_name
        
class DininghallForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):            
        super(DininghallForeignKey, self).__init__(Dininghall, to_field=to_field, **kwargs)
