#coding=utf-8
from django.db import models, connection
from base.models import CachingModel#, Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from base.operation import Operation, ModelOperation
from base.models import AppOperation
from django import forms
from django.forms import ModelForm
from django.db import transaction,IntegrityError
from mysite.personnel.models.model_emp import Employee,EmpPoPForeignKey,EmpMultForeignKey,getuserinfo
import datetime
from mysite.pos.pos_constant import TIMEOUT
from dbapp.widgets import ZBaseIntegerWidget,ZBaseMoneyWidget
from django.core.cache import cache
from mysite.utils import get_option
from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE,ONLINE_ALLOWANCE
class AllowanceSetting(CachingModel):
    isadd = models.BooleanField(verbose_name=_(u"累加"), default=False)#对未发的批次金额进行累计再下发
    iszeor = models.BooleanField(verbose_name=_(u"清零"), default=False)#每次只下发最后一次补贴金额
    
    def __unicode__(self):
        return _(u"补贴设置")
    
    class Admin(CachingModel.Admin):
        pass
    
    class Meta:
        app_label = 'pos'#属于的app

class AllowanceSettingForm(ModelForm):
    class Meta:
        model = AllowanceSetting

YESORNO = (
       (1, _(u'是')),
       (0, _(u'否')),)


def get_issuecard(key,IssueCard):
    cacheobj = cache.get(key)
    if cacheobj==None:
       cadno=key.split('_')[1]
       try:
         obj=IssueCard.objects.get(cardno=cadno)
       except:
         obj=None
       if obj:
           iskey="IssueCard_"+obj.cardno
           cache.set(iskey,obj,TIMEOUT)
           cacheobj = obj
    return cacheobj

class Allowance(CachingModel):
    user = EmpPoPForeignKey(verbose_name=_(u"人员"), null=False,blank=False,editable=True)
#    pin = models.CharField(_(u'人员编号'), db_column="badgenumber", null=False, max_length=20)
#    ename = models.CharField(_(u'姓名'), db_column="name", null=True, max_length=24, blank=True, default="")
#    cardno = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
    money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"补贴金额"))
    receive_money = models.DecimalField (max_digits=8,decimal_places=2,verbose_name=_(u"领取金额"),null=True,blank=True,editable=False)
    is_pass = models.IntegerField(verbose_name=_(u"是否通过审核"), editable=True,default=0,choices=YESORNO,blank=True,null=False)
    pass_name = models.CharField(max_length=100,verbose_name=_(u"审核通过人员"),blank=True,null=True,editable=False)
    valid_date = models.DateField(verbose_name=_(u"补贴有效日期"),blank=True,null=True,editable=True)
    receive_date = models.DateTimeField(verbose_name=_(u"补贴领取时间"),blank=True,null=True,editable=False)
    date = models.DateTimeField(verbose_name=_(u"补贴时间"),blank=False,null=False,editable=False)
    remark = models.CharField(max_length=200,verbose_name=_(u"备注"),blank=True,null=True)
    batch = models.CharField(max_length=20,verbose_name=_(u"补贴批次"),blank=True,null=True,editable=True)
    base_batch = models.CharField(max_length=20,verbose_name=_(u"补贴基次"),blank=True,null=True,editable=False)
    is_ok = models.IntegerField(verbose_name=_(u"是否领取"), editable=True,default=0,choices=YESORNO,blank=True,null=True)
    is_transfer = models.IntegerField(verbose_name=_(u"是否下发"), editable=False,default=0,choices=YESORNO,blank=True,null=True)
    sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=False)
   
    def __unicode__(self):
        return u"%s"%self.user      
    def data_valid(self,sendtype):
        if self.is_pass==1:
            raise Exception(_(u'该数据已经审核通过,不能修改'))
        
    def save(self,*args, **kwargs):
        try:
            self.date = datetime.datetime.now()
            if get_option("POS_IC") and self.pk is not None:
                now = datetime.datetime.now().date()
                if self.valid_date is None:
                    raise Exception(_(u"补贴有效日期不能为空"))
                if now>self.valid_date:
                    raise Exception(_(u"有效日期必须大于当前日期"))
                     
            if get_option("POS_IC") and self.pk is None:
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
                now_time = datetime.datetime.now()
                if ONLINE_ALLOWANCE:#在线补贴模式
                    self.batch = ((now_time.year-2000)*12+now_time.month)*31+now_time.day
                else:
                    self.batch = now_time.strftime("%Y%m")[2:]
                objcard = IssueCard.objects.get(UserID=self.user,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                if objcard:
                    self.sys_card_no = objcard.sys_card_no
                else:
                    raise Exception(_(u"编号%s人员没有发卡")%self.user)
            super(Allowance, self).save()
        except IntegrityError:
            raise Exception(_(u"所选补贴人员中编号%s人员当月补贴已经登记！")%self.user)
    
    class OpReloadAllowance(Operation):
        help_text=_(u"重新下发审核通过，但未能领取的补贴到补贴设备")
        verbose_name = _(u"重新下发补贴")
        visible = get_option("POS_IC") and not ONLINE_ALLOWANCE
        def action(self):
            if self.object.is_pass == 0:
                raise Exception(_(u"编号%s人员补贴没有通过审核，操作失败")%self.object.user)
            if self.object.is_ok == 1:
                raise Exception(_(u"编号%s人员补贴已被领取，操作失败")%self.object.user)
            from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info
            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER,device_use_type = 2)#查找补贴机
            if dev:
                update_pos_device_info(dev,[self.object],"SUBSIDYLOG")
            else:
                raise Exception(_(u"当前系统，没有补贴设备,操作失败"))
                
    class dataimport(ModelOperation):
        if get_option("POS_IC"):
            help_text = _(u"导入补贴数据：1.导入的人员必须是登记过卡帐号的人员，并且该人员的卡帐号必须是有效的卡。员工每月只支持一次补贴！2.卡状态为挂失，停用，过期的人员不能进行补贴登记，系统自动过滤！3.补贴导入成功后系统会自动下发设备指令，（直接审核通过）不可以再做修改！") #导入
        else:
            help_text = _(u"导入补贴数据：1.卡状态为挂失，停用，过期的人员不能进行补贴登记，系统自动过滤！2.补贴导入成功后系统会直接审核通过，不可以再做修改！") #导入
        verbose_name = _(u"导入")
        visible = True
        def action(self):
            from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
            if get_option("POS_IC"):
                devlist=Device.objects.filter(device_type=DEVICE_POS_SERVER,device_use_type = 2)#查找补贴机
                if not devlist:
                    raise Exception(_(u"当前系统，没有补贴设备,操作失败"))
            if get_option("POS_IC"):
                from mysite.pos.ic_allowance_import import ICImportAllowData
                obj_import = ICImportAllowData(req = self.request,input_name = "import_data")
            else:
                from mysite.pos.id_allowance_import import IDImportAllowData
                obj_import = IDImportAllowData(req = self.request,input_name = "import_data")
            obj_import.exe_import_data()
            ret_error = obj_import.error_info
            if ret_error:
               import traceback
               traceback.extract_stack()
               raise Exception(u"%(ret)s"%{
                           "ret":";".join(ret_error)
                     })
    
    class OpAudit(Operation):
        if get_option("POS_ID"):
            help_text=_(u"审核通过时系统会在卡现金收支表中增加一条补贴记录，审核通过的记录不允许再修改")
        else:
            help_text=_(u"审核通过时系统会自动下发指令，审核通过的记录不允许再修改")
        verbose_name = _(u"审核补贴")
        @transaction.commit_on_success
        def action(self):
            if self.object.is_pass ==0:
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
                from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                try:
                    if get_option("POS_ID"):
                        key = "IssueCard_%s" % self.object.user.Card
                        iscarobj = get_issuecard(key,IssueCard)
#                        iscarobj = IssueCard.objects.get(cardno=self.object.user.Card,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                    else:
                        from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
                        iscarobj = IssueCard.objects.get(sys_card_no=self.object.sys_card_no,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                except:
                   iscarobj = None
                try:
                    if iscarobj:
                        now = datetime.datetime.now().date()
                        dev = []
                        valid_date = self.object.valid_date
                        if get_option("POS_IC"):
                            batch = self.object.batch
                            allowance_list = Allowance.objects.filter(sys_card_no=self.object.sys_card_no,batch__lt= batch,is_pass=0)#获取小余当前记录的批次的没有审核的补贴记录
                            if allowance_list:
                                raise Exception(_(u"编号%s人员存在小于当前补贴批次号的未审核的补贴记录，请先审核小批次的记录！") % self.object.user)
                        if get_option("POS_IC") and now > valid_date:
                            raise Exception(_(u"编号%s人员补贴记录已超过补贴有效期")%self.object.user)
                        if  iscarobj.cardstatus != CARD_VALID:
                            raise Exception(_(u"编号%s卡已挂失或过期，无法补贴") % self.object.user)
                        if get_option("POS_IC"):
                            dev=Device.objects.filter(device_type=DEVICE_POS_SERVER,device_use_type = 2)#查找补贴机
                            if not dev:
                                raise Exception(_(u"当前系统，没有补贴设备,操作失败"))
                        newblan = iscarobj.blance+self.object.money
                        if iscarobj.type is not None:
                           from mysite.personnel.models.model_iccard import ICcard
                           iccardobj= ICcard.objects.get(pk=iscarobj.type_id)        
                           lessmoney = iccardobj.less_money#卡类最小余额
                           maxmoney = iccardobj.max_money#卡类最大余额
                           if lessmoney>newblan and lessmoney>0:
                                raise Exception(_(u"人员编号%s超出卡类最小余额")%self.object.user)
                           if newblan>maxmoney and maxmoney>0:
                                raise Exception(_(u"人员编号%s超出卡类最大余额")%self.object.user)
                           if maxmoney==0 and newblan > 10000 :
                                raise Exception(_(u"人员编号%s超出系统允许最大余额")%self.object.user)
                            
                        self.object.is_pass = 1
                        self.object.pass_name = unicode(self.request.user)
                        self.object.save()
                        if get_option("POS_ID"):
                            from mysite.pos.models.model_carcashsz import CarCashSZ
                            from mysite.pos.models.model_carcashtype import CarCashType
                            newblan = iscarobj.blance+self.object.money
                            CarCashSZ(user=self.object.user,
                                          card=iscarobj.cardno,
                                          checktime=datetime.datetime.now(),
                                          type=CarCashType.objects.get(id=2),#消费类型
                                          money=self.object.money,
                                          hide_column=2,
                                          blance =newblan,
                                    ).save()
                            iscarobj.blance=newblan
                            iscarobj.save()
                        else:
                            from mysite.iclock.models.dev_comm_operate import update_pos_device_info
                            if dev:
                                update_pos_device_info(dev,[self.object],"SUBSIDYLOG")
                    else:
                        raise Exception(_(u"编号%s人员没有有效的卡号")%self.object.user)
                except Exception, e:
#                    raise Exception(_(u"审核失败"))
                    import traceback;traceback.print_exc()
                    raise e
            else:
                raise Exception(_(u"编号%s人员已经通过审核")%self.object.user)
    
    class _add(ModelOperation):
        visible=False
        def action(self):
            pass   
                        
    class OpAddAllowance(ModelOperation):
        verbose_name=_(u"补贴登记")
        if get_option("POS_ID"):
            help_text=_(u'新增的补贴数据需要审核才真正下发到每个人员。卡状态为挂失，停用，过期的人员不能进行补贴登记，系统自动过滤')
        else:
            help_text=_(u'新增的补贴数据需要审核才真正下发到每个人员。卡状态为挂失，过期的人员不能进行补贴登记，已登记卡账号的人员，每个月只允许登记一次补贴，系统自动过滤')
        params=[
               ('UserID',EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)),            
               ('money',models.DecimalField(_(u'补贴金额'),max_digits=8,decimal_places=2)),
               ('remark',models.CharField(_(u'备注'),blank=True,null=True,max_length=100)),
              ]
        def __init__(self,obj):
            super(Allowance.OpAddAllowance, self).__init__(obj)
            if get_option("POS_IC"):
                self.params.append(('valid_date',models.DateField(verbose_name=_(u'补贴有效日期'))))
        def action(self, **args):
            from mysite.personnel.models.model_emp import Employee
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_LOST,CARD_OVERDUE,POS_CARD
            emps=args.pop('UserID')
            if len(emps)>1000:
                raise Exception(_(u'人员选择过多，最大支持1000人同时登记补贴!超出范围的情况下，请使用补贴导入功能!',))
            if not emps:
                raise Exception(_(u'请选择所需补贴人员！'))
            if  args['money'] == 0:
                raise Exception(_(u'补贴金额不能为0'))
            if args['money'] < 0:
                raise Exception(_(u'补贴金额不能为负数'))
            now = datetime.datetime.now().date()
            if get_option("POS_IC") and now>args['valid_date']:
                raise Exception(_(u"有效日期必须大于当前日期"))
            for emp in emps: 
                Allowance(user=emp, **args).save()
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

   

    class Admin(CachingModel.Admin):
        #default_give_perms = ["personnel.browse_issuecard", "att.browse_setuseratt"]
        #layout_types = ["table"]#显示方式
        sort_fields = ["-date","money","date"]#对列进行排序
        app_menu = "pos"
        menu_group = 'pos'
        cache = 3600
        menu_index = 3#在菜单按钮的位置
        adv_fields = ['money','is_pass','pass_name','user','date']#高级查询显示的列
        help_text = _(u'新增的补贴数据需要审核才真正下发到每个人员 ')
        if get_option("POS_IC"):
            list_display = ["user.PIN","user.EName","sys_card_no","money","receive_money","batch","is_ok","is_pass","pass_name","receive_date","valid_date","date","remark"]
            query_fields = ['user.PIN','money','batch','is_ok','is_pass','date']#显示的查询项
        else:
            list_display = ["user.PIN","user.EName","money","is_pass","pass_name","date","remark"]
            query_fields = ['user.PIN','money','is_pass','date']#显示的查询项
        newadded_column = {
                         "user.PIN":"get_pin",
                         "user.EName":"get_ename",
                            }
        default_widgets={'money':ZBaseMoneyWidget}
        disabled_perms=['add_allowance']
        search_fields=['date']
        tstart_end_search={
                        "date":[_(u"起始时间"),_(u"结束时间")]
                        }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
        
    
    class _delete(Operation):
        help_text = _(u"删除选定记录") #删除选定的记录
        verbose_name = _(u"删除")
        def action(self):
            if self.object.is_pass == 1:
                raise Exception(_(u'该数据已经审核通过,不能删除'))
#            from mysite.personnel.models.model_issuecard import IssueCard
#            iscarobj = IssueCard.objects.filter(UserID=self.object.user)
#            newblan = iscarobj.blance-self.object.money
#            iscarobj.update(UserID=self.object.user,blance=newblan)
#            if iscarobj.cardstatus != '1':
#                raise Exception(_(u"该卡无效或已经挂失，无法删除补贴记录"))
            self.object.delete()
    class Meta:
        app_label = 'pos'#属于的app
        verbose_name = _(u"补贴")#上部按钮
        verbose_name_plural = verbose_name
        if get_option("POS_IC"):
            unique_together = (("batch", "sys_card_no"))