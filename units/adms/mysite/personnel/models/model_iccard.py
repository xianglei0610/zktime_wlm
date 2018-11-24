#coding=utf-8
from django.db import models, connection
from base.models import CachingModel#, Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from base.operation import Operation, ModelOperation
from base.models import AppOperation

from model_meal import Meal,MealManyToManyField
from mysite.iclock.models.model_device import DeviceManyToManyFieldKey,DEVICE_POS_SERVER,Device
from django.core.cache import cache
#from mysite.pos.pos_constant import TIMEOUT
import datetime
from mysite.utils import get_option
from dbapp import data_edit
from dbapp.widgets import ZBase5IntegerWidget,ZBaseIntegerWidget,ZBaseSmallIntegerWidget,ZBaseHolidayIntegerWidget,ZBaseDayMinsIntegerWidget,ZBase3IntegerWidget
YESORNO = (
        (1, _(u'使用')),
        (0, _(u'不使用')),
)
TIMENAME =(
('1',_(u'固定时间段')),
('2',_(u'第二批')),
('3',_(u'第三批')),
('4',_(u'第四批')),
('5',_(u'第五批')),
('6',_(u'第六批')),
('7',_(u'第七批')),
('8',_(u'第八批')),
('9',_(u'第九批')),
)

def get_isscard_cache(self):
    try:
        from mysite.personnel.models.model_issuecard import IssueCard,CARD_OVERDUE,CARD_VALID
        from mysite.pos.pos_constant import TIMEOUT
        from base.cached_model import cache_key
        objcard = IssueCard.objects.filter(type=self,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
        nowtime = datetime.datetime.now().date()
        if objcard:
            for obj in objcard:
                if type(obj.issuedate) == type(datetime.datetime.now()):
                    iscardate = obj.issuedate.date()
                else:
                    iscardate = obj.issuedate
                daycount = (nowtime-iscardate).days
                maxday = self.use_date
                if maxday>=daycount or maxday==0:
                    obj.cardstatus = CARD_VALID
                if daycount>maxday and maxday >0:
                    obj.cardstatus = CARD_OVERDUE
#                obj.save()
                models.Model.save(obj,force_update=True)
                key = cache_key(obj,obj.pk)
                cache.delete(key)
                if get_option("POS_ID"):
                    key="IssueCard_%s" %obj.cardno
                    cache.set(key,obj,TIMEOUT)
    except:
        import traceback
        traceback.print_exc()
        
        
class ICcard(CachingModel):
    code = models.IntegerField(verbose_name=_(u'卡类编号'), max_length=20, blank=False, unique=True)
    name = models.CharField(verbose_name=_(u"卡类名称"), max_length=24, blank=False)
    discount = models.SmallIntegerField(verbose_name=_(u"折扣"),max_length=3, default=0)#Integer
    #pos_time = TimeSliceForeignKey(verbose_name=_(u"消费时间段"), blank=True,null=True)#从分段消费选择
    pos_time = models.CharField(verbose_name=_(u"消费时间段"),max_length=10, blank=False,null=False,choices=TIMENAME,default=1)
    #DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
    date_max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"日消费最大金额（元）"), default=0)
    date_max_count = models.IntegerField(verbose_name=_(u"日消费最大次数"),max_length=10, default=0)
    per_max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"次消费最大金额（元）"), default=0)
    meal_max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"餐消费最大金额（元）"), default=0)
    meal_max_count = models.IntegerField(verbose_name=_(u"餐消费最大次数"), default=0)
    less_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"最小卡余额（元）"), default=0)
    max_money = models.DecimalField(max_digits=8,decimal_places=0,verbose_name=_(u"最大卡余额（元）"), default=9999)
    posmeal = MealManyToManyField(verbose_name=_(u"可用餐别"), blank=True,null=True,editable=True)#从餐厅登记中选择
    use_date = models.SmallIntegerField(verbose_name=_(u"有效使用天数"), default=0)
    
    use_mechine = DeviceManyToManyFieldKey(verbose_name=_(u"可用设备"), blank=True, null=True)#从设备登记中获取
    remark = models.CharField(verbose_name=_(u"备注"),max_length=200,blank=True)
    use_fingerprint = models.IntegerField(verbose_name=_(u"使用指纹卡"), null=False, default=0, blank=True, editable=False, choices=YESORNO)
    
    def __unicode__(self):
        return u"%s---%s"%(self.name,self.code)#can't use lazy here
    def save(self,*args, **kwargs):
        super(ICcard, self).save()
    def data_valid(self, sendtype):
        """验证"""
        try:
            int(self.code)
        except:
            raise Exception(_(u'编号必须是整数'))
        tmp = ICcard.objects.filter(code=self.code)
        if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
               raise Exception(_(u'编号: %s 已存在') % self.code)
        if self.date_max_money<self.meal_max_money and self.date_max_money>0 and self.meal_max_money>0:
            raise Exception(_(u'日消费最大金额应该大于餐消费最大金额'))
        if int(self.date_max_count)<int(self.meal_max_count)and int(self.date_max_count)>0 and int(self.meal_max_count)>0:
            raise Exception(_(u'日消费最大次数应该大于餐消费最大次数'))
        if self.date_max_money<self.per_max_money and self.date_max_money>0 and self.per_max_money>0:
            raise Exception(_(u'日消费最大金额应该大于次消费最大金额'))
        if self.meal_max_money<self.per_max_money and self.meal_max_money>0 and self.per_max_money>0 :
            raise Exception(_(u'餐消费最大金额应该大于次消费最大金额'))
        if self.max_money<self.less_money and self.less_money>0 and self.max_money>0 :
            raise Exception(_(u'最大卡余额应该大于最小卡余额'))

    def get_posmeal(self):
        return u",".join([a.name for a in self.posmeal.all()])
    
#    def get_splitTime(self):
#        return u",".join([a.name for a in self.pos_time.all()])
    
    def get_device(self):
        return u",".join([a.sn for a in self.use_mechine.all()])
    
    class _delete(Operation):
        help_text = _(u"删除选定记录") #删除选定的记录
        verbose_name = _(u"删除")
        def action(self):
            if self.object.id <> 1:
                from mysite.personnel.models.model_issuecard import IssueCard
                iscarobj = IssueCard.objects.filter(type=self.object.pk)
                if iscarobj:
                    raise Exception(_(u'当前卡类已有卡片所属，删除失败！'))
                super(ICcard, self.object).delete()     
                key="ICcard_%s" %self.object.pk
                cache.delete(key)
                key1="use_mechine_"+str(self.object.pk)
                key2="posmeal_"+str(self.object.pk)
                cache.delete(key1)
                cache.delete(key2)
                if get_option("POS_IC"):
                    from mysite.iclock.models.dev_comm_operate import delete_pos_device_info
                    dev=Device.objects.filter(device_type=DEVICE_POS_SERVER)
                    delete_pos_device_info(dev,[self.object],"CARDTYPE")#卡类资料
            else:
                raise Exception(_(u'系统默认卡类不允许删除！'))
            
    def delete(self):
        if self.id <> 1:
            super(ICcard, self).delete()     
            
    class Admin(CachingModel.Admin):
#        layout_types = ["table"]#显示方式
        sort_fields = ["code"]#对列进行排序
        app_menu = "pos"
        menu_group = 'pos'
        visible=get_option("POS")
        cache = 3600
        menu_index = 5#在菜单按钮的位置
        
        query_fields = ['code','name','discount']#显示的查询项
        list_display = ['code','name','discount','date_max_money','date_max_count',
                        'per_max_money','meal_max_money','meal_max_count','less_money',
                        'max_money','posmeal','use_date','pos_time','use_mechine','remark','create_operator']#显示的列
        adv_fields = ['code','name','discount','posmeal','date_max_money','date_max_count',
                        'per_max_money','meal_max_money','meal_max_count','less_money',
                        'max_money','use_date','pos_time','use_mechine','remark','create_operator']#高级查询显示的列
        newadded_column = { 'posmeal': 'get_posmeal','use_mechine':'get_device'}
        api_m2m_display = { "use_mechine" : "sn","posmeal":"name"}
        help_text = _(u'下述所填项目中，卡类资料不能为空且编号不能重复，系统默认数据编号为1.下列各项中为0值或为空值表示不限制，折扣为0表示不打折，系统自动验证。可用设备，可用餐别需自定义下发到设备，系统默认不会下发！')
        default_widgets = {
                       'date_max_count':ZBase3IntegerWidget,
                        'meal_max_count':ZBase3IntegerWidget,
                        'use_date':ZBaseDayMinsIntegerWidget,
                        'discount':ZBaseSmallIntegerWidget,
                        'code':ZBaseSmallIntegerWidget,
                       }
        
        @staticmethod
        def initial_data(): 
                if ICcard.objects.count()==0:
                    ICcard(code='1',name=u"%s"%_(u"员工卡"),discount=0,date_max_money=0,
                           date_max_count=0,per_max_money=0,meal_max_money=0,meal_max_count=0,
                           less_money=0,max_money=0,use_date=0).save()
    class Meta:
        app_label = 'personnel'#属于的app
        verbose_name = _(u"卡类资料")#上部按钮
        verbose_name_plural = verbose_name
        
class ICcardForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
            super(ICcardForeignKey, self).__init__(ICcard, to_field=to_field, **kwargs)


def get_device_code(self):
    from mysite.pos.pos_constant import TIMEOUT 
    key = "use_mechine_"+str(self.pk)
    use_device = cache.get(key)
    try:
        if not use_device and not type(use_device)==list:
            use_device=self.use_mechine.get_query_set()
            cache.set(key,list(use_device),TIMEOUT)
    except:
        pass
    return use_device
   
def get_meal_code(self):
    from mysite.pos.pos_constant import TIMEOUT 
    key = "posmeal_"+str(self.pk)
    use_meal = cache.get(key)
    try:
        if not use_meal and not type(use_meal)==list:
            use_meal=self.posmeal.get_query_set()
            cache.set(key,list(use_meal),TIMEOUT)
    except:
        pass
    return use_meal

def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    from mysite.pos.pos_constant import TIMEOUT 
    if isinstance(newObj, ICcard):
        iskey="ICcard_%s" %newObj.pk
        cache.set(iskey,newObj,TIMEOUT)
        key1="use_mechine_"+str(newObj.pk)
        key2="posmeal_"+str(newObj.pk)
        use_device=newObj.use_mechine.all()
        cache.set(key1,list(use_device),TIMEOUT)
        use_meal=newObj.posmeal.all()
        cache.set(key2,list(use_meal),TIMEOUT)
        if oldObj and oldObj.use_date <> newObj.use_date:
            get_isscard_cache(newObj)
        if get_option("POS_IC"):
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info
            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER)
            if dev:
                update_pos_device_info(dev,[newObj],"CARDTYPE")#卡类资料
if get_option("POS"):
    data_edit.post_check.connect(DataPostCheck)
