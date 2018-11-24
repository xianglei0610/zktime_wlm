#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 


from model_carcashtype import CarCashType,CashTypeForeignKey
#from mysite.personnel.models.model_issuecard import IssueCard
import datetime
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
import os
from base.middleware import threadlocals
from mysite.utils import get_option
from mysite.personnel.models.model_meal import MealForeignKey,Meal
from base.operation import OperationBase, Operation, ModelOperation
from mysite.personnel.models.model_dept import DeptForeignKey, Department
from mysite.iclock.models.model_dininghall import Dininghall
CASHTYPE=(
#            (1,_(u'充值')),
#            (2,_(u'补贴')),
            #(3,_(u'批量充值')),
#            (7,_(u'卡成本')),
#            (4,_(u'支出卡成本')),
#            (5,_(u'退款')),
            (6,_(u'消费')),
#            (11,_(u'管理费')),
#            (10,_(u'计次')),
            (8,_(u'补单')),
            (9,_(u'纠错')),
            (10,_(u'计次')),
#            (12,_(u'计次纠错')),
)

CONSUMEMODEL=(
            (1,_(u'定值模式')),
            (2,_(u'金额模式')),
            (3,_(u'键值模式')),
            (4,_(u'计次模式')),
            (5,_(u'商品模式')),
            (6,_(u'计时模式')),
            (7,_(u'记账模式')),
            (8,_(u'手工补消费')),
            (9,_(u'设备纠错')),
                  )
                
LOGFLAG=(
            (1,_(u'设备上传')),
            (2,_(u'手工补单')),
            (3,_(u'纠错补入')),
            (8888,_(u'逃卡补单')),
            (5,_(u'消费日期异常')),
                  )


class ICConsumerList(models.Model,OperationBase):  
    user_id =  models.CharField(_(u'人员ID'),null=False, max_length=20)  
    user_pin =  models.CharField(_(u'人员编号'),null=False, max_length=20)
    user_name = models.CharField(_(u'姓名'),  null=True, max_length=24, blank=True, default="")
    dept = DeptForeignKey(verbose_name=_(u'部门'), editable=True, null=True)
#    user_dept_name = models.CharField(_(u'部门名称'),max_length=100)
    card = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
    sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
    dev_sn = models.CharField(_(u'设备序列号'), max_length=40, null=True, blank=True)
    card_serial_num = models.IntegerField(_(u'卡流水号'),max_length=20, null=True, blank=True)
    dev_serial_num = models.IntegerField(_(u'设备流水号'),max_length=20,null=True,blank=True)
    pos_time= models.DateTimeField(verbose_name=_(u'消费时间'),blank=True,editable=True,null=True)
    convey_time= models.DateTimeField(verbose_name=_(u'上传时间'),blank=True,editable=True,null=True)
    type_name = models.SmallIntegerField(_(u'类型名称'), max_length=10, null=True, blank=True,choices=CASHTYPE)
    money = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'操作金额(元)'),null=False,blank=False,editable=True)
    balance = models.DecimalField (max_digits=19,decimal_places=2,verbose_name=_(u'余额(元)'),null=False,blank=False,editable=True)
    pos_model = models.IntegerField(_(u'消费类型'),null=True, blank=True,choices=CONSUMEMODEL)
    dining = models.ForeignKey(Dininghall,verbose_name=_(u'餐厅'),editable=True, blank=True,null=True)
#    dining = models.CharField(_(u'餐厅'),max_length=20,null=True,blank=True,editable=True)
    meal = MealForeignKey(verbose_name=_(u"餐别"),null=True,editable=True)
    meal_data= models.DateTimeField(verbose_name=_(u'记餐日期'),blank=True,editable=True,null=True)
    create_operator =  models.CharField(_(u'操作员'),null=False, max_length=20)
    log_flag = models.SmallIntegerField(_(u'记录标志'), null=True, blank=True, editable=False,choices=LOGFLAG)
    discount = models.SmallIntegerField(verbose_name=_(u"折扣"),default=0,max_length=3,null=True,blank=True,editable=False)#Integer
    def __unicode__(self):
        return u"%s"%self.pk
#    def save(self,*args, **kwargs):
#  
#        op=threadlocals.get_current_user()
#        self.create_operator = op.username
#        if get_option("POS"):
#            serino=get_cardserial_from_txt(self.card)
#            self.cardserial=serino
##        super(CarCashSZ, self).save()
#        models.Model.save(self,args)
##    def delete(self):  
##        raise Exception(_(u'该人员的消费记录不允许删除'))
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
    def get_dept_name(self):
        u'''从缓存中得到部门的Name'''
        from mysite.personnel.models import Department
        dept_name=""
        try:
            dept_obj=Department.objects.get(id=self.dept_id)
            dept_name=dept_obj.name
        except:
            pass
        return dept_name
    
    def get_dept_code(self):
        u'''从缓存中得到部门的code'''
        from mysite.personnel.models import Department
        dept_code=""
        try:
           dept_obj=Department.objects.get(id=self.dept_id)
           dept_code=dept_obj.code
        except:
           pass
        return dept_code
    
    def get_dinging_name(self):
        u'''从缓存中得到餐厅的Name'''
        from mysite.iclock.models.model_dininghall import Dininghall
        dining_name=""
        try:
            dining_obj=Dininghall.objects.get(id=self.dining_id)
            dining_name=dining_obj.name
        except:
            pass
        return dining_name
     
    
    class Admin:
        sort_fields=["-pos_time","money","dev_serial_num","card_serial_num","pos_time","convey_time"]
        app_menu="pos"
        menu_group = 'pos'
        menu_index =19
        visible = get_option("POS_IC")
        cache = 0
        query_fields=["user_pin","dev_sn","pos_model","pos_time"]
        adv_fields= ["user_pin","user_name","dept","card","sys_card_no","type_name","money","balance","pos_model","dining","meal","dev_sn","dev_serial_num","card_serial_num","pos_time","convey_time","log_flag","create_operator"]
        list_display= ["user_pin","user_name","dept.code","dept.name","card","sys_card_no","type_name","money","balance","pos_model","dining.name","meal.name","dev_sn","dev_serial_num","card_serial_num","pos_time","convey_time","log_flag","create_operator"]
        search_fields=['pos_time']
        newadded_column = {
                  "meal.name":"get_meal_name",
                  'dept.name':'get_dept_name',
                  'dept.code':'get_dept_code',
                  'dining.name':'get_dinging_name'
                }
        
        tstart_end_search={
                "pos_time":[_(u"起始时间"),_(u"结束时间")]
        }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        disabled_perms=['change_icconsumerlist','add_icconsumerlist','delete_icconsumerlist']
    class _change(ModelOperation):
        visible=False
        def action(self):
            pass 
        
    class _add(ModelOperation):
        visible=False
        def action(self):
            pass     
    
    class OpUploadPosLog(ModelOperation):
        u"导入u盘记录"
        help_text = _(u'''设备原始记录文件上传''')
        verbose_name = _(u"u盘文件上传")
        visible=True
        params = (
               ('upload_attlog', models.FileField(verbose_name=_(u'选择消费记录文件'), blank=True, null=True)),
        )
        def action(self,upload_attlog):
            if self.request.FILES:
                f=self.request.FILES['upload_attlog']
                f_format=str(f).split('.')
                format_list=['txt']
                ret = []
                try:
                    format_list.index(str(f_format[1]))
                except:
                    raise Exception (_(u"消费文件格式无效！"))
#                try:
                filename=f.name
                sn = f_format[0].split('_')[0]
                objpath=settings.C_ADMS_PATH%"zkpos/"
#                objpath=path%sn+"new/"
                fname = os.path.join(objpath,filename)
                
                if not os.path.exists(objpath):
                    os.makedirs(objpath)
                
                if os.path.exists(fname):  #判断文件夹是否存在
                    os.remove(fname)
        
                if os.path.isfile(fname):  #判断是否为文件，是true,不是False,
                    os.remove(fname) 
                fp = open(fname, 'wb')  #读写打开这个要上传的文件
        
                for content in f.chunks(): #写文件
                    fp.write(content)
                fp.close()
                raise Exception (_(u"文件上传成功！"))
            else:
                raise Exception (_(u"文件选择错误！"))
#                except:
#                    pass
               
    class Meta:
        app_label='pos'
        verbose_name = _(u"消费明细")
        verbose_name_plural = verbose_name
        unique_together = (("dev_sn", "sys_card_no","money","card_serial_num","dev_serial_num","pos_time"),)
        
    
               
