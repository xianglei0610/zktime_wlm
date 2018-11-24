#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 

from mysite.personnel.models.model_emp import Employee,EmpPoPForeignKey
from model_carcashtype import CarCashType,CashTypeForeignKey
import datetime
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
import os
from base.middleware import threadlocals
from mysite.utils import get_option
CASHTYPE=(
            (1,_(u'充值')),
            (2,_(u'补贴')),
            #(3,_(u'批量充值')),
            (7,_(u'卡成本')),
            (4,_(u'支出卡成本')),
            (5,_(u'退款')),
            (6,_(u'发卡')),
            (11,_(u'管理费')),
            (10,_(u'计次')),
            (8,_(u'手工补消费')),
            (9,_(u'纠错')),
            (10,_(u'计次')),
            (12,_(u'换卡')),
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


class CarCashSZBak(CachingModel):    
    user_pin =  models.CharField(_(u'人员编号'),null=False, max_length=20)
    user_name = models.CharField(_(u'姓名'),  null=True, max_length=24, blank=True, default="")
    user_dept_name = models.CharField(_(u'部门名称'),db_column="DeptName",max_length=100)
    physical_card_no = models.CharField(_(u'原始卡号'), max_length=20, null=False, blank=True, editable=True, default='')
    sys_card_no = models.CharField(_(u'卡账号'), max_length=20, null=False, blank=True, editable=True, default='')
    cardserial = models.IntegerField(_(u'卡流水号'),max_length=20, null=True, blank=True)
    blance = models.DecimalField(verbose_name=_(u'余额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
    money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'操作金额(元)'),null=False,blank=False,editable=True)
#    type= CashTypeForeignKey(verbose_name=_(u'类型'),null=False,blank=False,editable=True)
    hide_column = models.SmallIntegerField(_(u'操作类型'), max_length=10, null=True, blank=True,choices=CASHTYPE)
    checktime= models.DateTimeField(verbose_name=_(u'操作时间'),default=datetime.datetime.now(),blank=True,editable=True,null=True)
    
    convey_time = models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
    sn_name = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
    serialnum = models.IntegerField(_(u'设备流水号'),max_length=20,null=True,blank=True)
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
             type=u"%s"%_(u"收入")
        except:
           import traceback;traceback.print_exc()
           pass
        return type
        
        if self.type.type==2:
            return u"%s"%_(u'支出')
        elif self.type.type==1:
            return u"%s"%_(u"收入")
    def save(self,*args, **kwargs):
        op=threadlocals.get_current_user()
        self.create_operator = op.username
        models.Model.save(self,args)
#    def delete(self):  
#        raise Exception(_(u'该人员的消费记录不允许删除'))
    def get_pin(self):
        from mysite.personnel.models.model_emp import getuserinfo
        return getuserinfo(self.user_id,"PIN")
          
    def get_ename(self):
        from mysite.personnel.models.model_emp import getuserinfo
        return getuserinfo(self.user_id,"EName")
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
        sort_fields=["-checktime","money","cardserial","checktime"]
        app_menu="pos"
        visible = False
        menu_group = 'pos'
        menu_index =5
        cache = 3600
        query_fields = ['sn_name','user_pin','physical_card_no','sys_card_no','serialnum','money','hide_column','checktime']
        adv_fields = ['sn_name','user_pin','physical_card_no','sys_card_no','serialnum','money','blance','create_operator','checktime']
        
        disabled_perms=['change_carcashszbak','add_carcashszbak']
        
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
        verbose_name=_(u'卡现金收支备份表')
        verbose_name_plural=verbose_name
               
