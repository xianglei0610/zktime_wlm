#coding=utf-8
from django.db import models, connection
from base.models import CachingModel#, Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from base.operation import Operation, ModelOperation
from base.models import AppOperation
from django.core.exceptions import ValidationError

from mysite.personnel.models.model_emp import EmpPoPForeignKey,getuserinfo,get_dept
from mysite.iclock.models.model_device import DeviceForeignKey,Device

from mysite.pos.models.model_carcashsz import CarCashSZ
from mysite.pos.models.model_carcashtype import CarCashType
from mysite.personnel.models.model_meal import MealForeignKey,Meal
from mysite.pos.pos_constant import TIMEOUT
from django.core.cache import cache
from mysite.utils import get_option 
import datetime
def get_issuecard(key):
    cacheobj = cache.get(key)
    if cacheobj==None:
       cardno=key.split('_')[1]
       try:
         from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID
         obj=IssueCard.objects.get(cardno=int(cardno),cardstatus = CARD_VALID)
       except:
         obj=None
       if obj:
           iskey="IssueCard_"+obj.cardno
           cache.set(iskey,obj,TIMEOUT)
           cacheobj = obj
    return cacheobj


def get_card_user_info(cardno):
    u'''根据卡号获取人员信息'''
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
    try:
#        IssueCard.can_restore=True
        isobj=IssueCard.objects.get(cardno=int(cardno),cardstatus__in=[CARD_VALID,CARD_OVERDUE])
#        IssueCard.can_restore=False
        if isobj :
            return u"%s"%isobj.UserID_id
#        if hasattr(isobj,attr):
#            return getattr(isobj,attr)
    except:
#        IssueCard.can_restore=False
        import traceback;traceback.print_exc()
    return ""

class HandConsume(CachingModel):
#    user=EmpPoPForeignKey(verbose_name=_(u"人员"),null=False,editable=True)
    sys_card_no = models.CharField(max_length=20,verbose_name=_(u'卡账号'),editable=True, null=True, blank=True,)
    card = models.CharField(verbose_name=_(u'卡号'), max_length=20, null=False, blank=True, editable=True)
    card_serial_no = models.IntegerField(_(u'卡流水号'),max_length=20, null=True, blank=True)
    labor = models.CharField(verbose_name=_(u'人员编号'), max_length=20, null=True, blank=True, editable=True)
    name = models.CharField(verbose_name=_(u'姓名'), max_length=20, null=True, blank=True, editable=True)
#   pos_type = models.SmallIntegerField(verbose_name=_(u"消费类型"), choices=((1,'设备自动'),(2,'手工补单'),))#choices=...)
    meal = MealForeignKey(verbose_name=_(u"餐别"),null=False,editable=True)
    date = models.DateTimeField(verbose_name=_(u"消费时间"),blank=False,null=False)
    money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"消费金额"))
    posdevice = DeviceForeignKey(verbose_name=_(u'设备'), null=False,editable=True)#关联设备
    blance = models.DecimalField(verbose_name=_(u'余额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
    
    def __unicode__(self):
        return ""
        #return u"%s" % self.user#can't use lazy here
    
    def data_valid(self, sendtype):
       postime = self.date.time()
       nowtime = datetime.datetime.now()
       if self.date > nowtime:
            raise Exception(_(u'消费时间不能大于当前时间'))
       mealobj = Meal.objects.filter(starttime__lte=postime,endtime__gte=postime,available=1)
       if mealobj:
            if mealobj[0].id<>self.meal_id:
                raise Exception(_(u'消费时间不属于当前餐别'))
       else:
            raise Exception(_(u'消费时间不属于当前餐别'))
    def get_device_sn(self):
        """得到设备序列号"""
        name=""
        if not self.posdevice_id:
           return dev
        try:
           dev=Device.objects.get(id=self.posdevice_id)
           name = u"%s"%dev.sn
        except:
            pass
        return name
    
    def save(self):
        from  decimal import Decimal
        if self.pk == None:
            try:
                key = "IssueCard_%s" % int(self.card)
                iscarobj = get_issuecard(key) 
            except:
                iscarobj = None
            if iscarobj:
                self.card = int(self.card)
                if get_option("POS_ID"):
                    newblan = iscarobj.blance-self.money
                    if newblan<0:
                        raise Exception(_(u"余额不足"))
                    if iscarobj.type is not None:
                       from mysite.personnel.models.model_iccard import ICcard
                       #iccardobj= get_cache_iccard("ICcard_"+str(iscarobj.type_id))
                       iccardobj= ICcard.objects.get(pk=iscarobj.type_id)
                       lessmoney = iccardobj.less_money#卡类最小余额
                       maxmoney = iccardobj.max_money#卡类最大余额
                       if lessmoney>newblan and lessmoney>0:
                           raise Exception(_(u"编号%s超出卡最小余额")%iscarobj.UserID)
                       if newblan>maxmoney and maxmoney>0:
                           raise Exception(_(u"编号%s超出卡最大余额")%iscarobj.UserID)
                    CarCashSZ(user_id=get_card_user_info(self.card),
                             dept_id = get_dept(get_card_user_info(self.card)).id,
                             card = self.card,
                             checktime=self.date,
                             type=CarCashType.objects.get(id=8),#消费类型
                             money=self.money,
                             sn_name=self.posdevice.sn,
                             hide_column=8,
                             dining = self.posdevice.dining,
                             blance = newblan,
                           ).save()
                    iscarobj.blance=newblan
                    iscarobj.save()
                    self.blance = newblan
                else:
                    from mysite.pos.models.model_icconsumerlist import ICConsumerList
                    from base.middleware import threadlocals
                    op=threadlocals.get_current_user()
                    ICConsumerList(user_id=get_card_user_info(self.card),
                    user_pin = self.labor,
                    user_name = self.name,
                    dept_id = get_dept(get_card_user_info(self.card)).id,
                    card = self.card,
                    sys_card_no = self.sys_card_no,
                    dev_sn = self.get_device_sn(),
                    card_serial_num =  self.card_serial_no,
                    pos_time = self.date,
                    type_name = 8,
                    money = self.money,
                    balance = self.blance,
                    dining = self.posdevice.dining,
                    meal = self.meal,
                    pos_model = 8,
                    create_operator = op.username,
                    log_flag = 2
                    ).save()
                    iscarobj.blance=self.blance
                    iscarobj.save()
                super(HandConsume, self).save()#保存本身 
            else:
                raise Exception(_(u"当前操作卡片不是有效卡，操作失败"))
                
                
    class _change(Operation):
        help_text = _(u"修改选定记录")
        visible=False
        def action(self):
            """这个操作不执行，根据save方法有没有pk参数来做"""
            pass
        
    class _delete(Operation):
           help_text = _(u"删除选定记录")
           visible=False
           def action(self):
               """这个操作不执行，根据save方法有没有pk参数来做"""
               pass
    
        
    
    
    def get_meal_name(self):
        """得到餐别名称"""
        meal_name=""
        if not self.meal_id:
           return meal_name
        try:
           obj_meal=Meal.objects.get(id=self.meal_id)
           meal_name = u"%s"%obj_meal.name
        except:
            pass
        return meal_name
    def get_pin(self):
       
       from mysite.personnel.models.model_emp import getuserinfo
       from mysite.personnel.models.model_issuecard import get_card_user_info
       return getuserinfo(get_card_user_info(self.card),"PIN")
         
    def get_ename(self):
       from mysite.personnel.models.model_emp import getuserinfo
       from mysite.personnel.models.model_issuecard import get_card_user_info
       return getuserinfo(get_card_user_info(self.card),"EName")
    
    class Admin(CachingModel.Admin):
        #default_give_perms = ["personnel.browse_issuecard", "att.browse_setuseratt"]
        #layout_types = ["table"]#显示方式
        sort_fields = ["-date","money","date"]#对列进行排序
        app_menu = "pos"
        menu_group = 'pos'
        menu_index = 4#在菜单按钮的位置
        cache = 3600
        if get_option("POS_ID"):
            query_fields = ["labor","date"]#显示的查询项
            list_display = ["labor","name","card","money","blance","meal.name","posdevice.sn","date",'create_time','create_operator',]#显示的列
            adv_fields = ["labor","name","card","money","blance","meal.name","posdevice.sn","date",'create_time','create_operator',]#高级查询显示的列
        else:
            query_fields = ["labor","date"]#显示的查询项
            list_display = ["labor","name","sys_card_no","card_serial_no","card","money","blance","meal.name","posdevice.sn","date","create_time","create_operator",]#显示的列
            adv_fields = ["labor","name","sys_card_no","card_serial_no","card","money","blance","meal.name","posdevice.sn","date","create_time","create_operator",]#高级查询显示的列
            
        newadded_column = {
                          "user.PIN":"get_pin",
                          "user.EName":"get_ename",
                          "posdevice.sn":"get_device_sn",
                          "meal.name":"get_meal_name"
                        }
        report_fields=['user.PIN','user.EName']
        if get_option("POS_ID"):
            help_text = _(u'手工补消费管理:手工添加的消费记录，不能再删除。消费时间受餐别时间限制！')
        else:
            help_text = _(u'手工补消费管理:手工添加的消费记录，不能再删除。')
        search_fields=['date']
        tstart_end_search={
                        "date":[_(u"起始时间"),_(u"结束时间")]
                }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        disabled_perms=['change_handconsume','delete_handconsume']
        #import_fields = ['name','num','desc',]#可导入的字段
        
    class Meta:
        app_label = 'pos'#属于的app
        verbose_name = _(u"手工补消费")
        verbose_name_plural = verbose_name
