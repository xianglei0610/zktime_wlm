#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

from mysite.personnel.models.model_emp import Employee,EmpPoPForeignKey
from model_carcashtype import CarCashType,CashTypeForeignKey
#from mysite.personnel.models.model_issuecard import IssueCard
import datetime
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
import os
from base.middleware import threadlocals
from mysite.utils import get_option
from mysite.personnel.models.model_dept import DeptForeignKey, Department
#from mysite.personnel.models.model_dept import DeptForeignKey, Department
from mysite.iclock.models.model_dininghall import Dininghall
if get_option("POS_ID"):
    CASHTYPE=(
                (1,_(u'充值')),
                (2,_(u'补贴')),
                #(3,_(u'批量充值')),
                (7,_(u'卡成本')),
                (4,_(u'支出卡成本')),
                (5,_(u'退款')),
                (6,_(u'消费')),
                (11,_(u'管理费')),
                (8,_(u'手工补消费')),
                (9,_(u'纠错')),
                (10,_(u'计次')),
                (12,_(u'计次纠错')),
#                (13,_(u'优惠记录')),
    )
else:
     CASHTYPE=(
                    (1,_(u'充值')),
                    (2,_(u'补贴')),
                    #(3,_(u'批量充值')),
                    (7,_(u'卡成本')),
                    (4,_(u'支出卡成本')),
                    (5,_(u'退款')),
#                    (6,_(u'消费')),
                    (11,_(u'管理费')),
#                    (10,_(u'计次')),
#                    (8,_(u'手工补消费')),
#                    (9,_(u'纠错')),
#                    (10,_(u'计次')),
#                    (12,_(u'计次纠错')),
                    (13,_(u'充值优惠')),
                    (14,_(u'无卡退卡')),
        )
    


AllOW_TYPE = (
            (0,_(u'累加补贴')),
            (1,_(u'清零补贴')),

)

LOGFLAG=(
            (1,_(u'设备上传')),
            (2,_(u'系统添加')),
            (8888,_(u'纠错补入')),
            (5,_(u'日期异常')),
        )

def get_cardserial_from_cache(cardno):
    from model_cardserial import CardSerial
    try:
        obj = CardSerial.objects.get(cardno=int(cardno))
        number = int(obj.serialnum)+1
        obj.serialnum=number
        obj.save(force_update=True,log_msg=False)
    except:
#        import traceback;traceback.print_exc()
        number =1
        CardSerial(serialnum=number,cardno=int(cardno)).save()    
    return number



class CarCashSZ(CachingModel):    
    user=EmpPoPForeignKey(verbose_name=_(u"人员"),null=False,editable=True)
    card = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
    sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
#    dept_id = models.IntegerField(_(u'部门id'),max_length=10, null=True, blank=True,editable=False)
    dept = DeptForeignKey(verbose_name=_(u'部门'), editable=True, null=True)
    sn_name = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
    cardserial = models.IntegerField(_(u'卡流水号'),max_length=20, null=True, blank=True)
    serialnum = models.IntegerField(_(u'设备流水号'),max_length=20,null=True,blank=True)
    checktime= models.DateTimeField(verbose_name=_(u'操作时间'),default=datetime.datetime.now(),blank=True,editable=True,null=True)
    type= CashTypeForeignKey(verbose_name=_(u'类型'),null=False,blank=False,editable=True)
    money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'金额(元)'),null=False,blank=False,editable=True)
    discount = models.SmallIntegerField(verbose_name=_(u"折扣"),default=0,max_length=3,null=True,blank=True,editable=False)#Integer
    hide_column = models.SmallIntegerField(_(u'类型名称'), max_length=10, null=True, blank=True,choices=CASHTYPE)
    dining = models.ForeignKey(Dininghall,verbose_name=_(u'餐厅'),editable=True, blank=True,null=True)
#    dining = models.CharField(_(u'餐厅'),max_length=20,null=True,blank=True,editable=False)
    blance = models.DecimalField(verbose_name=_(u'余额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
    
    convey_time = models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
    allow_type = models.SmallIntegerField(_(u'补贴类型'), max_length=10, null=True, blank=True,choices=AllOW_TYPE)
    allow_batch = models.SmallIntegerField(_(u'补贴批次'), max_length=10, null=True, blank=True)
    allow_base_batch = models.SmallIntegerField(_(u'补贴基次'), max_length=10, null=True, blank=True)
    log_flag = models.SmallIntegerField(_(u'记录类型'), null=True,default=2, blank=True, editable=False,choices=LOGFLAG)
    
    def __unicode__(self):
        return ""
#        return u"%s"%self.user
    def get_montype(self):
        u"得到卡类型get具有缓存"
        type=""
        if not self.type_id:
          return type
        try:
          type=CarCashType.objects.get(id=self.type_id)
          if type.type ==2:
             type=u"%s"%_(u'支出')
          else:
             type=u"%s"%_(u'支入')
        except:
           import traceback;traceback.print_exc()
           pass
        return type
        
        if self.type.type==2:
            return u"%s"%_(u'支出')
        elif self.type.type==1:
            return u"%s"%_(u"收入")
    def save(self,*args, **kwargs):
        try:
            if get_option("POS_ID"):
                if self.serialnum and self.sn_name:
                    iskey="CarCashSZ_%s%s" %(self.serialnum,self.sn_name)
                    cache.set(iskey,self,TIMEOUT)
                op=threadlocals.get_current_user()
                self.create_operator = op.username
                serino=get_cardserial_from_cache(self.card)
                self.cardserial=serino
                models.Model.save(self,args)
            else:
                super(CarCashSZ, self).save()
        except:
            import traceback;traceback.print_exc()
#    def delete(self):  
#        raise Exception(_(u'该人员的消费记录不允许删除'))
    def get_pin(self):
        emp_pin=""
        try:
            Employee.can_restore=True
            emp_obj=Employee.objects.get(id=self.user_id)
            Employee.can_restore=False
            emp_pin=emp_obj.PIN
        except:
            pass
        return emp_pin
        
    def get_ename(self):
        emp_name=""
        try:
            Employee.can_restore=True
            emp_obj=Employee.objects.get(id=self.user_id)
            Employee.can_restore=False
            emp_name=emp_obj.EName
        except:
            pass
        return emp_name
        
    def get_dept_name(self):
        u'''从缓存中得到部门的Name'''
        from mysite.personnel.models.model_emp  import get_dept
        dept_name=""
        try:
            dept_obj=get_dept(self.user_id)
            dept_name=dept_obj.name
        except:
            pass
        return dept_name
        
        
    def get_type_name(self):
        u"得到卡类型get具有缓存"
        name=""
        if not self.type_id:
           return name
        try:
           name=CarCashType.objects.get(id=self.type_id)
           name = u"%s"%name.name
        except:
            pass
        return name
            
    class Admin(CachingModel.Admin):
        sort_fields=["-checktime","money","serialnum","cardserial","checktime"]
        app_menu="pos"
        menu_group = 'pos'
        menu_index =5
        cache = 3600
        visible = True
        if get_option("POS_ID"):
            query_fields = ['user.PIN','card','hide_column','checktime',]
            adv_fields = ['card','type.type','money','blance','discount','checktime','create_operator','sn_name','serialnum','cardserial',]
            list_display = ['user.PIN','user.EName','user.DeptID','card','hide_column','type.type','money','blance','discount','checktime','create_operator','sn_name','serialnum','cardserial',]
        else:
            query_fields = ['user.PIN','hide_column','sn_name','checktime',]
            adv_fields = ['card','sys_card_no','type','serialnum','money','blance','create_operator','checktime','log_flag']
            list_display = ['user.PIN','user.EName','user.DeptID','card','sys_card_no','cardserial','hide_column','type.type','allow_type','money','blance','convey_time','checktime','sn_name','serialnum','create_operator','log_flag']
            
        search_fields=['checktime']
        newadded_column = {
                          "user.PIN":"get_pin",
                          "user.EName":"get_ename",
                          "type.type":"get_montype",
                          "user.DeptID":"get_dept_name"
                        }
        tstart_end_search={
                "checktime":[_(u"起始时间"),_(u"结束时间")]
        }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        disabled_perms=['change_carcashsz','add_carcashsz']
        
    class _delete(Operation):
        help_text = _(u"删除选定记录") #删除选定的记录
        verbose_name = _(u"删除")
        visible=False
        def action(self):
            raise Exception(_(u'该人员的消费记录不允许删除'))
          
    class _change(ModelOperation):
        visible=False
        def action(self):
            pass 
        
    class _add(ModelOperation):
        visible=False
        def action(self):
            pass      
               
    class Meta:
        app_label='pos' 
        verbose_name=_(u'卡现金收支')
        verbose_name_plural=verbose_name
        if get_option("POS_IC"):
            unique_together = (("sn_name","hide_column","sys_card_no","money","checktime"),)       
