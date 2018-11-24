#coding=utf-8
from django.db import models, connection
from base.models import CachingModel#, Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from base.operation import Operation, ModelOperation
from base.models import AppOperation
from django.core.exceptions import ValidationError
from datetime import time
import datetime
from django.core.cache import cache
#from mysite.pos.pos_constant import TIMEOUT
from dbapp.widgets import ZBaseIntegerWidget
from mysite.utils import get_option
YESORNO = (
        (1, _(u'有效')),
        (0, _(u'无效')),
)

class Meal(CachingModel):
    code = models.CharField(verbose_name=_(u'餐别编号'), blank=False,max_length=20,editable=False)
    name = models.CharField(verbose_name=_(u"餐别名称"), max_length=100, blank=False)
    
    available = models.IntegerField(verbose_name=_(u"是否有效"), choices=YESORNO)
    money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"成本（元）"), blank=False)
    starttime = models.TimeField(verbose_name=_(u"开始时间"),blank=False)
    endtime = models.TimeField(verbose_name=_(u"结束时间"), blank=False)
    
    remark = models.CharField(verbose_name=_(u"备注"),max_length=100,blank=True)
    
    def save(self,*args, **kwargs):
        from mysite.pos.pos_constant import TIMEOUT
        if self.pk is not None:
            self.endtime=self.endtime.replace(second=59)
        super(Meal,self).save()
        cacheobj = Meal.objects.all().filter(available=1)
        cache.set("Meal",list(cacheobj),TIMEOUT)
        from mysite.personnel.models.model_iccard import ICcard
        objICcard = ICcard.objects.all()
        if objICcard:
            for obj in objICcard:
                key="posmeal_"+str(obj.pk)
                mealcache=obj.posmeal.get_query_set()
                cache.set(key,list(mealcache),TIMEOUT)
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,delete_pos_device_info
            from mysite.iclock.models.model_device import DEVICE_POS_SERVER,Device
            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER)
            if dev:
                if self.available == 1:
                    update_pos_device_info(dev,[self],"MEALTYPE")
                else:
                    delete_pos_device_info(dev,[self],"MEALTYPE")
        
        
    def get_endtime(self):
           return self.endtime.strftime("%H:%M")
    def get_begintime(self):
           return self.starttime.strftime("%H:%M")
    
    
    def data_valid(self, sendtype):
        """验证"""
        try:
            int(self.code)
        except:
            raise Exception(_(u'编号必须是整数'))
        if int(self.code)< 0:
            raise Exception(_(u'编号不能为负数'))
        if int(self.code) == 0:
            raise Exception(_(u'编号不能为0'))
        try:
            self.money = str(int(self.money))
        except:
            raise Exception(_(u'金额只能为数字'))
        if int(self.money)< 0:
            raise Exception(_(u'金额不能为负数'))
        
        if self.starttime > self.endtime:
                raise Exception(_(u'结束时间不能小于开始时间'))
        if int(self.code)<>1:
            tmp = Meal.objects.get(code=int(self.code)-1)
            minute1 = tmp.endtime.minute+1
            second1 = tmp.endtime.second
            hour1 = tmp.endtime.hour
            hour2 = self.starttime.hour
            if minute1==60:
                minute1 =0
                hour1=tmp.endtime.hour+1
            minute2 = self.starttime.minute
            second2 =  self.starttime.second
            
            if hour1<>hour2:
               raise Exception(_(u'本餐别的开始时间必须是上一餐别的结束时间加一秒钟'))
            if (second1-second2) <> 59:
               raise Exception(_(u'本餐别的开始时间必须是上一餐别的结束时间加一秒钟'))
            if minute2 <> minute1 and self.available==1:
                raise Exception(_(u'本餐别的开始时间必须是上一餐别的结束时间加一秒钟'))
#        if starttime > 0 and tmp[0].id != self.id:   #编辑状态
#            raise Exception(_(u'编号: %s 已存在') % self.code)
        
            
    class _delete(Operation):
        verbose_name = u'删除'
        def action(self):
            if self.object.pk not in range(9):
                self.object.delete()
    def __unicode__(self):
        return u"%s %s %s" %(self.name,self.starttime,self.endtime)#can't use lazy here
    
    class Admin(CachingModel.Admin):
        #default_give_perms = ["personnel.browse_issuecard", "att.browse_setuseratt"]
#        layout_types = ["table"]#显示方式
        sort_fields = ["code","starttime","endtime"]#对列进行排序
        app_menu = "pos"
        menu_group = 'pos'
        visible=False
        menu_index = 33#在菜单按钮的位置
        query_fields = ['name','available']#显示的查询项
        cache = 3600
        if get_option("POS_IC"):
            list_display = ['code','name','starttime','endtime','available','remark']#显示的列
        else:
            list_display = ['code','name','money','starttime','endtime','available','remark']#显示的列
            
        adv_fields = ['code','name','available']#高级查询显示的列
        newadded_column={'endtime':'get_endtime','starttime':'get_begintime'}
        help_text = _(u'当本餐别选择有效时，本餐别的开始时间必须是上一餐别的结束时间加一秒钟。')
#        default_widgets={'money':ZBaseIntegerWidget}
        default_give_perms = ["contenttypes.can_PosFormPage",]
        @staticmethod
        def initial_data():#初始化数据
            if Meal.objects.count() == 0:
                Meal(code=1,name=u"%s"%_(u"早餐"),money=2,starttime=time(0,0),endtime=time(10,0,59),available=1).save()
                Meal(code=2,name=u"%s"%_(u"中餐"),money=3,starttime=time(10,1),endtime=time(14,0,59),available=1).save()
                Meal(code=3,name=u"%s"%_(u"晚餐"),money=4,starttime=time(14,1),endtime=time(20,0,59),available=1).save()
                Meal(code=4,name=u"%s"%_(u"夜宵"),money=2,starttime=time(20,1),endtime=time(23,59,59),available=1).save() 
                Meal(code=5,name=u"%s"%_(u"餐别05"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()
                Meal(code=6,name=u"%s"%_(u"餐别06"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()
                Meal(code=7,name=u"%s"%_(u"餐别07"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()
                Meal(code=8,name=u"%s"%_(u"餐别08"),money=2,starttime=time(0,0),endtime=time(0,0),available=0).save()           
     
    class Meta:
        app_label = 'personnel'#属于的app
        verbose_name = _(u"餐别资料")#上部按钮
        verbose_name_plural = verbose_name
        
class MealForeignKey(models.ForeignKey):
    def __init__(self, *args, **kwargs):
            super(MealForeignKey, self).__init__(Meal,*args, **kwargs) 
            
class MealManyToManyField(models.ManyToManyField):
        def __init__(self, *args, **kwargs):
                super(MealManyToManyField, self).__init__(Meal, *args, **kwargs)
                
def update_meal_widgets():
        from dbapp import widgets
        from mysite.personnel.mealdropdown import ZMealChoiceWidget,ZMealMultiChoiceWidget
        if MealForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[MealForeignKey] = ZMealChoiceWidget
        if MealManyToManyField not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[MealManyToManyField] = ZMealMultiChoiceWidget
            
update_meal_widgets()

