#! /usr/bin/env python
#coding=utf-8
from traceback import print_exc
from django.db import models
from base.models import CachingModel
from base.operation import Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from model_leave import YESORNO
from django.db.models import Q
from django import forms

import datetime
import re
from  decimal import Decimal
from django.db import transaction
from django.conf import settings
from base.middleware import threadlocals
from mysite.utils import get_option
from dbapp.widgets import ZBaseIntegerWidget,ZBaseMoneyWidget,ZBaseNormalFloatWidget
from base.cached_model import cache_key
CARD_VALID = '1'
CARD_LOST = '3'
CARD_OVERDUE = '4'
CARD_STOP = '5'
CARD_INVALID = '6'

if get_option("POS"):
    CARDSTATUS = (
        (CARD_VALID, _(u'有效')),
        (CARD_LOST, _(u'挂失')),
        (CARD_OVERDUE, _(u'消费过期')),
        (CARD_STOP, _(u'停用')),
)
else:
    CARDSTATUS = (
        (CARD_VALID, _(u'有效')),
        (CARD_STOP, _(u'停用')),
)

POS_CARD = '0'
PRIVAGE_CARD = '1'
OPERATE_CARD = '2'
if get_option("POS_ID"):
    PRIVAGE = (
            (POS_CARD, _(u'普通卡')),
            (PRIVAGE_CARD, _(u'管理卡')),
    )
else:
    PRIVAGE = (
        (POS_CARD, _(u'普通卡')),
        (PRIVAGE_CARD, _(u'管理卡')),
        (OPERATE_CARD, _(u'操作卡')),
        )
    


#class CardType(CachingModel):
#        '''卡类型'''
#        cardtypecode = models.CharField(verbose_name=_(u'卡类型代码'), max_length=20, editable=True)
#        cardtypename = models.CharField(verbose_name=_(u'卡类型名称'), max_length=50, null=True, blank=True, editable=True)
#        def __unicode__(self):
#                return u"%s %s" % (self.cardtypecode, self.cardtypename)
#
#        class Admin(CachingModel.Admin):
#                app_menu = "personnel"
#                menu_index = 6
#                visible = False
#                @staticmethod
#                def initial_data():
#                        if CardType.objects.count() == 0:
#                                CardType(cardtypename=u'%s'%_(u"贵宾卡"), cardtypecode="01").save()
#                                CardType(cardtypename=u'%s'%_(u"普通卡"), cardtypecode="02").save()
#                        pass
#
#        class Meta:
#                app_label = 'personnel'
#                verbose_name = _(u'卡类型')
#                verbose_name_plural = verbose_name


from mysite.personnel.models.model_emp import Employee, EmpForeignKey, EmpMultForeignKey, EmpPoPForeignKey, EmpPoPMultForeignKey, format_pin
import datetime
from model_iccard import ICcardForeignKey
from django.core.cache import cache
#from mysite.pos.pos_constant import TIMEOUT
import datetime

#验证卡类余额
def blance_valid(type,newblance,user):
           from mysite.personnel.models.model_iccard import ICcard
           iccardobj= ICcard.objects.filter(pk=type)        
           lessmoney = iccardobj[0].less_money#卡类最小余额
           maxmoney = iccardobj[0].max_money#卡类最大余额
           if lessmoney>0 and lessmoney>newblance:
               raise Exception(_(u"人员编号%s超出卡最小余额")%user)
           if maxmoney>0 and newblance>maxmoney:
               raise Exception(_(u"人员编号%s超出卡最大余额")%user)
           if maxmoney==0 and newblance >9999 :
               raise Exception(_(u"人员编号%s超出系统允许最大余额")%user)
        


installed_apps = settings.INSTALLED_APPS  
class IssueCard(CachingModel):
        '''发卡表'''
        UserID = EmpPoPForeignKey(verbose_name=_(u"人员"), null=True, blank=True,editable=True)
        cardno = models.CharField(verbose_name=_(u'卡号'), max_length=20, null=False, blank=False, editable=True)
        effectivenessdate = models.DateField(verbose_name=_(u'有效日期'), null=True, blank=True, editable=False)
        isvalid = models.BooleanField(verbose_name=_(u'是否有效'), choices=YESORNO, editable=False, default=1)
        cardpwd = models.CharField(verbose_name=_(u'卡密码'), max_length=20, null=True, blank=True, editable=False)
        failuredate = models.DateTimeField(verbose_name=_(u'失效日期'), null=True, blank=True, editable=False)
        cardstatus = models.CharField(verbose_name=_(u'卡状态'), max_length=3, choices=CARDSTATUS, null=False, blank=True,editable=True)
        issuedate = models.DateField(verbose_name=_(u'发卡日期'), null=True, blank=True, editable=False, default=datetime.datetime.now().strftime("%Y-%m-%d"))
        #pos add_column
        
        type=ICcardForeignKey(verbose_name=_(u'消费卡类'), editable=True,null=True,blank=True,default=1)
        blance = models.DecimalField(verbose_name=_(u'金额'),max_digits=9,null=True, blank=True,default=0,decimal_places=2,editable=True)
        mng_cost = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"管理费（元）"),null=True, blank=True, default=0)
        card_cost = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"卡成本（元）"),null=True, blank=True, default=0)
        Password = models.CharField(_(u'超额密码'), max_length=6,default=123456,null=True, blank=True, editable=True)
        card_privage = models.CharField(_(u'卡类型'), max_length=20, null=True, blank=True, choices=PRIVAGE,default=POS_CARD)
        
        date_money = models.DecimalField(verbose_name=_(u"日消费最大金额"), max_digits=10,null=True, blank=True,default=0,decimal_places=2,editable=False)
        date_count = models.IntegerField(verbose_name=_(u"日消费次数"),default=0,null=True, blank=True,editable=False)
        meal_money = models.DecimalField(verbose_name=_(u"餐消费金额"), max_digits=10,null=True, blank=True,default=0,decimal_places=2,editable=False)
        meal_count = models.IntegerField(verbose_name=_(u"餐消费次数"), default=0,null=True, blank=True,editable=False)
        pos_date = models.DateField(verbose_name=_(u'消费日期'),blank=True,null=True,editable=False)
        pos_time = models.DateTimeField(verbose_name=_(u'最后消费时间'),blank=True,null=True,editable=False)
        meal_type = models.SmallIntegerField(verbose_name=_(u"消费餐别"),null=True,default=0,blank=True,editable=False)
        sys_card_no =  models.IntegerField(verbose_name=_(u"卡账号"),null=True, blank=True,editable=True)
        card_serial_num = models.IntegerField(_(u'卡流水号'),max_length=20,default=0, null=True, blank=True)
        def __unicode__(self):
            from mysite.personnel.models import Employee
            emp=""
            try:
                emp= Employee.objects.get(pk = self.UserID_id)
            except:
                if get_option("POS"):
                    return u"%s %s %s"%(self.UserID, self.cardno,self.blance)
                else:
                    return "%s"%self.cardno
            if get_option("POS"):
                return u"%s %s %s"%(emp, self.cardno,self.blance)
            else:
                return u"%s  %s" % (emp, self.cardno)
        
        def data_valid(self, sendtype):
            from mysite.iclock.models.modelproc import get_normal_card
            try:
                orgcard = str(self.cardno)
            except:
                raise Exception(_(u'卡号不正确'))
            import re
            tmp = re.compile('^[0-9]+$')
            if not tmp.search(orgcard):
                raise Exception(_(u'卡号不正确'))
            if int(self.cardno) == 0:
                raise Exception(_(u'卡号不能为0'))
            u = IssueCard.objects.filter(cardno=int(self.cardno))
            if u:
                raise Exception(_(u'卡号已使用'))
            if get_option("POS"):
                obj = IssueCard.objects.filter(UserID = self.UserID,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD)
            else:
                obj = IssueCard.objects.filter(UserID = self.UserID,cardstatus__in = [CARD_VALID])
                
            if obj:
                raise Exception(_(u'该人员已有正在使用的卡'))

            self.issuedate = datetime.datetime.now().date()
            if get_option("POS"):
                if not tmp.match(self.Password):
                   raise Exception(_(u'人员密码必须为整数'))
                if int(self.mng_cost)< 0:
                   raise Exception(_(u'管理费不能为负数'))
                if int(self.blance)< 0:
                    raise Exception(_(u'金额不能为负数'))
                if int(self.card_cost)< 0:
                    raise Exception(_(u'卡成本不能为负数'))

        def delete(self, Init_db=False):
            if get_option("POS_ID"):
                if self.blance<>0:
                    raise Exception(_(u'编号%s请先办理退款手续')%self)
            from django.db.models import Model
            key = "IssueCard_%s" %self.cardno
            cache.delete(key)
#            if self.card_privage == PRIVAGE_CARD:
#                from mysite.pos.models.model_cardmanage import CardManage
#                obj_card_manage = CardManage.objects.get(card_no = self.cardno)
#                obj_card_manage.delete()
            super(IssueCard, self).delete()
        @staticmethod
        def clear():
            import time
            IssueCard.can_restore=True
            for e in IssueCard.objects.all():
                if e.blance<>0:
                   raise Exception(_(u'卡号：%s请先办理退款手续')%e.cardno)
                else:
                    e.delete(Init_db = True)
                    time.sleep(0.2)
            IssueCard.can_restore = False
            
        @transaction.commit_on_success
        def save(self,*args, **kwargs):
            from mysite.pos.models import CarCashSZ, CarCashType
            from mysite.pos.pos_constant import TIMEOUT 
            is_manager_card = False#是否管理卡
            is_pos_id_save = False #ID消费通信保存
            is_new = False#是否新增
            self.cardno = int(self.cardno)
            if self.pk == None:
                is_new = True
            try:
                old_card = IssueCard.objects.get(UserID=self.UserID,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
            except:
                old_card = None
            
            if get_option("POS"):#消费
                if self.card_privage in [PRIVAGE_CARD,OPERATE_CARD]:#新增管理卡
                    if is_new:
                        self.card_privage = self.card_privage
                        is_manager_card = True
                else:
                    if get_option("POS_ID") and  is_new:
                        blance_valid(self.type_id,self.blance,self.UserID)#验证余额
                        try:
                            CarCashSZ(user=self.UserID,
                                   card = self.cardno,
                                   checktime = datetime.datetime.now(),
                                   type_id = 7,#cost type
                                   money = self.card_cost,
                                   hide_column = 7,blance = self.blance ).save()
                            CarCashSZ(user = self.UserID,
                                   card = self.cardno,
                                   checktime = datetime.datetime.now(),
                                   type_id =1,#cost type
                                   money = self.blance,
                                   hide_column = 1,blance = self.blance).save()
                            CarCashSZ(user = self.UserID,
                                   card = self.cardno,
                                   checktime = datetime.datetime.now(),
                                   type_id =11,#cost type
                                   money=self.mng_cost,
                                   hide_column=11,blance=self.blance).save()
                        except Exception, e:
                            import traceback;traceback.print_exc()
                    elif get_option("POS_ID"):
                        from django.db.models import Model
                        op=threadlocals.get_current_user()
                        if op:
                            self.create_operator = op.username
                        #zkeco包含ID消费，考勤的时候特殊处理一下，兼容redis同步考勤命令
                        from base.sync_hook import save_hook,SYNC_MODEL
                        if get_option("ATT") and SYNC_MODEL:
                            hk = save_hook(is_new,self,old_card).check()
                        models.Model.save(self,args)
                        if get_option("ATT") and SYNC_MODEL:
                            hk.sync()
                        is_pos_id_save = True

            if is_new: 
                self.cardstatus=CARD_VALID
            key = cache_key(self,self.pk)
            cache.delete(key)
            if not is_pos_id_save:
                super(IssueCard, self).save(**kwargs)

            if not is_manager_card:#普通卡
                key="IssueCard_%s" %self.cardno
                cache.set(key,self,TIMEOUT)
                
            if get_option("ATT") and is_new and not is_manager_card:#考勤
                if not is_manager_card:
                    from base.sync_api import SYNC_MODEL
                    if not SYNC_MODEL:
                        #更新了卡号
                        from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                        adj_user_cmmdata(self.UserID, [], self.UserID.attarea.all())

            #同步卡号到门禁控制器
            from mysite import settings
            if get_option("IACCESS") and is_new and not is_manager_card :#门禁
                if not is_manager_card:
                    from mysite.iclock.models.dev_comm_operate import sync_set_user
                    sync_set_user(self.UserID.search_accdev_byuser(), [self.UserID])
                
        class _add(ModelOperation):
            item_index = 1
            verbose_name = _(u"发卡")
            def action(self):
                pass   
        
        class OPUpdateCardInfo(ModelOperation):
            item_index = 10
            help_text=_(u"修改卡资料:需要连接发卡器！当前操作只对消费有效！")
            verbose_name = _(u"修改卡资料")
            visible= get_option("POS_IC")
            params=(
                ('sys_card_no',models.CharField(verbose_name = _(u'卡账号'), max_length = 10,null = True,blank = True,editable = False)),
                ('labor',models.CharField(verbose_name = _(u'工号'), max_length = 10,null = True,blank = True,editable = False)),
                ('name',models.CharField(verbose_name = _(u'姓名'), max_length = 10,null= True,blank = True,editable = False)),
                ('cardno',models.CharField(verbose_name=_(u"卡号"), max_length=20,null = True,blank = True )),
                ('blance',models.DecimalField(max_digits=20,decimal_places=2,null=True,blank=True,verbose_name=_(u"卡余额（元）"))),
                ('Password',models.CharField(verbose_name=_(u"超额密码"),max_length=6,default=123456,null=True, blank=True, editable=True)),
                ('operate_type',models.CharField(verbose_name = _(u'操作类型'),default='8',max_length = 4,null = True,blank = True,editable = False)),
                ('type',ICcardForeignKey(verbose_name=_(u'卡类'),null=False,blank=True)),
                ('card_serial_no',models.CharField(verbose_name = _(u'流水号'), max_length = 10,default=1,null = True,blank = True,editable = False)),
                ('allow_serial_no',models.CharField(verbose_name = _(u'补贴流水号'), max_length = 10,default=1,null = True,blank = True,editable = False)),
                ('issue_date',models.DateField(verbose_name=_(u'发卡日期'), null=True, blank=True, editable=False, default=datetime.datetime.now().strftime("%Y-%m-%d"))),
                ('Dept_name',models.CharField(verbose_name = _(u'部门'), max_length = 50,null= True,blank = True,editable = False)),
            )
            def action(self):
               pass  
        
        class Supplement(ModelOperation):
            if get_option("POS_ID"):
                help_text=_(u"充值：可以实现手工充值跟自动充值操作,自动充值的时候，需要连接读卡器！")
            else:
                help_text=_(u"充值：需要连接发卡器！当前操作只对消费有效！")
            verbose_name = _(u"充值")
            visible = get_option("POS")
            item_index = 3
            params =(
                    ('card',models.CharField(verbose_name = _(u'原始卡号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('sys_card_no',models.CharField(verbose_name = _(u'卡账号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('card_serial_no',models.CharField(verbose_name = _(u'卡流水号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('labor',models.CharField(verbose_name = _(u'工号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('name',models.CharField(verbose_name = _(u'姓名'), max_length = 10,null= True,blank = True,editable = False)),
                    ('Dept_name',models.CharField(verbose_name = _(u'部门名称'), max_length = 50,null= True,blank = True,editable = False)),
                    ('money',models.DecimalField(max_digits = 9,decimal_places = 2,default = Decimal('50'),null = False,blank = False, verbose_name=_(u"充值金额"),editable=False)),
                    ('blances',models.DecimalField(max_digits = 10,decimal_places = 2,default = Decimal('0'), null = True,blank = True,verbose_name=_(u"账上余额"),editable=False)),
                    ('card_blance',models.DecimalField(max_digits = 10,decimal_places = 2,default = Decimal('0'), null = True,blank = True,verbose_name=_(u"卡上余额"),editable=False)),
                    ('op_card_blance',models.DecimalField(max_digits = 10,decimal_places = 2,default = Decimal('0'), null = True,blank = True,verbose_name=_(u"加后金额"),editable=False)),
                    
               )
            @transaction.commit_manually
            def action(self,card,money,blances,name,labor,card_serial_no,op_card_blance,card_blance,Dept_name,sys_card_no):
                from mysite.pos.models import CarCashSZ, CarCashType
                if card:
                    objcard=IssueCard.objects.filter(cardno = int(card))
                    if objcard:
                        if objcard[0].card_privage == PRIVAGE_CARD:
                           raise Exception(_(u"管理卡，操作失败"))
                        if objcard[0].cardstatus == CARD_LOST:
                           raise Exception(_(u"该卡已经挂失，操作失败"))
                        if objcard[0].cardstatus ==CARD_STOP:
                           raise Exception(_(u"该卡已停用，操作失败"))
                        if objcard[0].cardstatus ==CARD_OVERDUE:
                           raise Exception(_(u"该卡已过期，操作失败"))
                        if int(money)<0:
                           raise Exception(_(u"充值金额不能为负数"))
                        if int(money) == 0:
                           raise Exception(_(u"充值金额不能为零"))
                        
                        newblance = objcard[0].blance + money
                        blance_valid(objcard[0].type_id,newblance,objcard[0].UserID)#验证余额
                        try:
                            objcard[0].blance = newblance
                            objcard[0].save()
                            CarCashSZ(user = objcard[0].UserID,
                                      card = int(card),
                                      checktime = datetime.datetime.now(),
                                      type_id = 1,#charge type
                                      money = money,
                                      blance = objcard[0].blance,
                                      hide_column = 1).save()
                            transaction.commit()
                        except:
                            raise Exception(_(u"充值失败"))
                            transaction.rollback()
                            import traceback;traceback.print_exc()
                        
                    else:
                         raise Exception(_(u"卡号不存在"))
                else:
                    pass
#                    raise Exception(_(u"卡号不能为空"))
                
        class OpBatchIssueCard(ModelOperation):
            verbose_name = _(u'批量发卡')
            help_text = _(u'已经发过卡的人员，将不会在生成人员列表时出现！')
            item_index=2
            from mysite import settings
            visible = not get_option("POS_IC")
            params=(
                ('pin_width',models.IntegerField(null=True,blank=True,default=settings.PIN_WIDTH)),
                ('card_cost', models.DecimalField (max_digits=8,decimal_places=2, null=True,blank=True,default=0,verbose_name=_(u"卡成本（元）"))),
                ('mng_cost',models.DecimalField (max_digits=8,decimal_places=2,null=True,blank=True,default=0,verbose_name=_(u"管理费（元）"))),
                ('cardtype',ICcardForeignKey(verbose_name=_(u'卡类'),null=True,blank=True)),
                ('blance',models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True,default=0,verbose_name=_(u"余额（元）"))),
                ('cardPwd', models.CharField(_(u'卡密码'), max_length=6,default=123456,null=True, blank=True, editable=True))
                )
            @transaction.commit_on_success
            def action(self,pin_width,mng_cost,card_cost,cardtype,blance,cardPwd):
                from mysite.pos.models import CarCashSZ, CarCashType
                import re
                tmp = re.compile('^[0-9]+$')
                if get_option("POS") and not tmp.match(cardPwd):
                   raise Exception(_(u'人员密码必须为整数'))
                
                if self.request:
                    empids=self.request.POST.get("empids","")
                    cardnos=self.request.POST.get("cardnos","")
                    empids=[int(i) for i in empids.split(",")]
                    #print empids
                    cardnos=[str(i) for i in cardnos.split(",")]
                    #print cardnos
                    where={'id__in':empids}
                    emps=Employee.objects.filter(Q(**where))
                    try:
                        for i in range(len(empids)):
                            tcard = IssueCard()
                            tuser = emps.get(pk=empids[i])
                            #sync to issuecard
                            tcard.cardno = int(cardnos[i])
                            tcard.UserID = tuser
                            tcard.blance = blance
                            tcard.card_cost = card_cost
                            tcard.mng_cost = mng_cost
                            tcard.type = cardtype
                            tcard.Password = cardPwd
                            tcard.issuedate = datetime.datetime.now().date()
                            tcard.save()
                            #sync cardno to user
#                            if not get_option("POS"):
#                                tuser.Card=cardnos[i]
#                                tuser.save()
                    except:
                           import traceback;traceback.print_exc()
                           pass
                        
        class ResetPassword(Operation):
            verbose_name = _(u"修改卡密码")#消费ID卡设置
            help_text = _(u"""最多6位字符，修改成功后服务器将会自动将软件中的密码同步为新的密码。""")
            item_index=9
            visible = get_option("POS_ID")
            params=(
                ('commkey', forms.CharField(label=_(u"新密码"), required=True, widget=forms.PasswordInput,max_length=6)),
                ('commkey_again',forms.CharField(label=_(u"确认密码"), required=True, widget=forms.PasswordInput,max_length=6)),
            )
            only_one_object=True
            def action(self,commkey,commkey_again):
                if self.object.card_privage == PRIVAGE_CARD:
                    raise Exception(_(u"该卡为管理卡，操作失败"))
                if self.object.cardstatus <> CARD_VALID :
                    raise Exception(_(u'该操作只对有效卡有用，操作失败！'))
                for key in commkey:
                    if key == ' ':
                        return Exception(_(u'密码不能包含空格！'))
                import re
                p = re.compile(r'^[0-9]+$')
                if not p.match(commkey) or not p.match(commkey_again):
                    raise Exception(_(u"密码必须为整数"))
                
                if commkey != commkey_again:  
                    raise Exception(_(u'两次输入密码不一致,请重新输入！'))
                else:
                    self.object.Password = commkey
                    self.object.save(force_update=True)
            
    #消费操作
        class CardTypeSet(Operation):
            verbose_name = _(u"""卡类设置""")
            help_text = _(u"""卡类设置:修改当前人员消费卡所属卡类，当前操作只对消费有效！""")
            item_index=1
            visible = get_option("POS_ID")
            params = (
                        ('cardtype',ICcardForeignKey(verbose_name=_(u'卡类'),null=False,blank=True)),
                     )
            def action(self,cardtype):
                from mysite.pos.pos_constant import TIMEOUT 
                blance_valid(cardtype.pk,self.object.blance,self.object.UserID)#验证余额
                if self.object.card_privage == PRIVAGE_CARD:
                    raise Exception(_(u"该卡为管理卡，操作失败"))
                if self.object.cardstatus==CARD_LOST:
                    raise Exception(_(u"该卡已挂失，操作失败"))
                if self.object.cardstatus==CARD_STOP:
                    raise Exception(_(u"该卡已停用，操作失败"))
                from mysite.personnel.models.model_iccard import ICcard
                nowtime = datetime.datetime.now().date()
                try:
                    objIccard = ICcard.objects.get(pk=cardtype.pk)
                except:
                    pass
                if type(self.object.issuedate) == type(datetime.datetime.now()):
                    iscardate = self.object.issuedate.date()
                else:
                    iscardate = self.object.issuedate
                daycount = (nowtime-iscardate).days
                maxday = objIccard.use_date
                if maxday>=daycount or maxday==0:
                    self.object.cardstatus=CARD_VALID
                if daycount>maxday and maxday >0:
                    self.object.cardstatus=CARD_OVERDUE
                try:                  
                    self.object.type = cardtype
                    self.object.save()
                    key1="use_mechine_"+str(cardtype.pk)
                    key2="posmeal_"+str(cardtype.pk)
                    use_device=objIccard.use_mechine.get_query_set()
                    cache.set(key1,list(use_device),TIMEOUT)
                    use_meal=objIccard.posmeal.get_query_set()
                    cache.set(key2,list(use_meal),TIMEOUT)
                except:
                    raise Exception(_(u"操作失败"))
                    import traceback;traceback.print_exc()
                    pass
        
        class OpLostNew(Operation):
            verbose_name=_(u"换卡")
            if get_option("POS_IC"):
                help_text = _(u"""原卡号必须先挂失,换卡之前请采集所有设备上的数据！当前操作只对消费有效！""")
            item_index=7
            only_one_object = True
            visible = get_option("POS_ID")
            params=(
                    ('labor',models.CharField(verbose_name = _(u'工号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('name',models.CharField(verbose_name = _(u'姓名'), max_length = 10,null= True,blank = True,editable = False)),
                    ('sys_card_no',models.CharField(verbose_name = _(u'新卡账号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('old_sys_card_no',models.CharField(verbose_name = _(u'原卡账号'), max_length = 10,null = True,blank = True,editable = False)),
                    ('cardno',models.CharField(verbose_name=_(u"卡号"), max_length=20 )),
                    ('blance',models.DecimalField(max_digits=20,decimal_places=2,null=True,blank=True,verbose_name=_(u"原卡金额（元）"))),
                    ('Password',models.CharField(verbose_name=_(u"超额密码"),max_length=6,default=123456,null=True, blank=True, editable=True)),
                    ('card_cost',models.DecimalField (max_digits=8,decimal_places=2,null=True,blank=True, verbose_name=_(u"卡成本（元）"))),
                    ('mng_cost',models.DecimalField (max_digits=8,decimal_places=2,null=True,blank=True, verbose_name=_(u"管理费（元）"))),
                    ('operate_type',models.CharField(verbose_name = _(u'操作类型'),default='12',max_length = 4,null = True,blank = True,editable = False)),
                    ('type',models.CharField(verbose_name = _(u'卡类型'),max_length = 2,null = True,blank = True,editable = False)),
                    ('UserID',models.CharField(verbose_name = _(u'用户ID'),max_length = 2,null = True,blank = True,editable = False)),
                    ('card_serial_no',models.CharField(verbose_name = _(u'卡流水号'), max_length = 10,default=1,null = True,blank = True,editable = False)),
                    ('card_privage',models.CharField(verbose_name = _(u'卡权限'), max_length = 10,default=POS_CARD,null = True,blank = True,editable = False)),
                )
            def __init__(self,obj):
                if get_option("POS"):
                    super(IssueCard.OpLostNew, self).__init__(obj)
                    isobj = IssueCard.objects.filter(pk=obj.pk)[0]
                    params = dict(self.params)
                    params['blance'].default=isobj.blance
                    params['card_cost'].default=isobj.card_cost
                    params['mng_cost'].default=isobj.mng_cost
                    if get_option("POS_IC"):
                        from mysite.personnel.models.model_emp import getuserinfo
                        params['labor'].default=getuserinfo(isobj.UserID_id,"PIN")
                        params['name'].default=getuserinfo(isobj.UserID_id,"ENAME")
                        params['old_sys_card_no'].default=isobj.sys_card_no
                        params['type'].default=isobj.type_id
                        params['UserID'].default=isobj.UserID_id
            @transaction.commit_on_success
            def action(self,cardno,blance,card_cost, mng_cost,labor,name,old_sys_card_no,type,UserID,operate_type,card_privage,card_serial_no,sys_card_no,Password):
                from mysite.pos.models import ReplenishCard
                from mysite.pos.models import CarCashSZ, CarCashType
                from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
                if self.object.card_privage == PRIVAGE_CARD:
                    raise Exception(_(u'该卡为管理卡，操作失败'))
                if self.object.UserID.status == STATUS_LEAVE:
                    raise Exception(_(u'该人员已经离职，操作失败'))
                if self.object.cardstatus == CARD_STOP:
                    raise Exception(_(u'该卡已停用，操作失败'))
                obj = IssueCard.objects.filter(UserID = self.object.UserID,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD)
                if obj:
                   raise Exception(_(u'该人员已有正在使用的卡'))
                if  IssueCard.objects.filter(cardno=cardno).count() <> 0:
                    raise Exception(_(u'卡号已使用'))
                try:
                    orgcard = str(cardno)
                except:
                    raise Exception(_(u'卡号不正确'))
                import re
                tmp = re.compile('^[0-9]+$')
                if not tmp.search(orgcard):
                    raise Exception(_(u'卡号不正确'))
                if int(cardno) == 0:
                    raise Exception(_(u'卡号不能为0'))
                if self.object.cardstatus == CARD_VALID or self.object.cardstatus==CARD_OVERDUE:
                    raise Exception(_(u"请先挂失"))

                try:
                    ReplenishCard(user=self.object.UserID,
                               oldcardno=self.object.cardno,
                               newcardno=int(cardno),
                               blance=self.object.blance).save()
                    card_blance = self.object.blance
                    if get_option("POS_ID"):
                        self.object.blance = 0
                        self.object.cardstatus = CARD_STOP
                        self.object.save()
                        key = cache_key(self.object,self.object.pk)
                        cache.delete(key)
                        CarCashSZ(user=self.object.UserID,
                             card=self.object.cardno,
                             checktime = datetime.datetime.now(),
                             type_id=5,#charge type
                             money=card_blance,
                             hide_column=5,blance=self.object.blance).save()
                        IssueCard(UserID = self.object.UserID,
                                cardno = int(cardno),
                                cardstatus = CARD_VALID,
                                blance = card_blance,
                                card_cost = self.object.card_cost,
                                mng_cost = self.object.mng_cost,
                                type = self.object.type ).save()
#                    else:
#                        self.object.cardstatus = CARD_STOP
#                        self.object.save()
#                        IssueCard(UserID = self.object.UserID,
#                                            cardno = cardno,
#                                            cardstatus = CARD_VALID,
#                                            card_cost = self.object.card_cost,
#                                            mng_cost = self.object.mng_cost,
#                                            type_id = self.object.type ).save()
#                        
#                    if get_option("IACCESS"):
#                        from mysite.iclock.models.dev_comm_operate import sync_set_user
#                        sync_set_user(self.object.UserID.search_accdev_byuser(), [self.object.UserID])
#                    if get_option("ATT"):
#                        from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
#                        adj_user_cmmdata(self.object.UserID, [], self.object.UserID.attarea.all())
                except:
                   raise Exception(_(u"换卡失败"))
                   pass
            
        class OpRetreatCard(ModelOperation):
            help_text=_(u"""退卡：退卡前请确认该卡的消费记录都已采集完成！退卡过程中系统将会清除卡内数据！""")
            verbose_name = _(u"退卡")
            visible = get_option("POS_IC")
            item_index = 5
            params =(
               ('card',models.CharField(verbose_name = _(u'原始卡号'), max_length = 10,null = True,blank = True,editable = False)),
               ('card_serial_no',models.CharField(verbose_name = _(u'卡流水号'), max_length = 10,null = True,blank = True,editable = False)),
               ('sys_card_no',models.CharField(verbose_name = _(u'卡账号'), max_length = 10,null = True,blank = True,editable = False)),
               ('labor',models.CharField(verbose_name = _(u'工号'), max_length =10,null = True,blank = True,editable = False)),
               ('name',models.CharField(verbose_name = _(u'姓名'), max_length = 10,null= True,blank = True,editable = False)),
               ('Dept_name',models.CharField(verbose_name = _(u'部门名称'), max_length = 50,null= True,blank = True,editable = False)),
               ('blances',models.DecimalField(max_digits = 10,decimal_places = 2, null = True,blank = True,verbose_name=_(u"账上余额"),editable=False)),
               ('card_blance',models.DecimalField(max_digits = 10,decimal_places = 2, null = True,blank = True,verbose_name=_(u"卡上余额"),editable=False)),
               ('money',models.DecimalField (max_digits=8,decimal_places=2,null=True,blank=True,default=0, verbose_name=_(u"退还成本（元）"))),
            )
        class Reimburse(ModelOperation):
            if get_option("POS_ID"):
                help_text=_(u"""退款：可以实现手工退款跟自动退款操作,自动退款的时候，需要连接读卡器！当前操作只对消费有效！""")
            else:
                help_text=_(u"""退款：需要连接发卡器！当前操作只对消费有效！""")
            verbose_name = _(u"退款")
            visible = get_option("POS")
            item_index=4
            params=(
                   ('card',models.CharField(verbose_name = _(u'原始卡号'), max_length = 10,null = False,blank = True,editable = False)),
                   ('sys_card_no',models.CharField(verbose_name = _(u'卡账号'), max_length = 10,null = True,blank = True,editable = False)),
                   ('card_serial_no',models.CharField(verbose_name = _(u'卡流水号'), max_length = 10,null = True,blank = True,editable = False)),
                   ('labor',models.CharField(verbose_name = _(u'工号'), max_length =10,null = True,blank = True,editable = False)),
                   ('name',models.CharField(verbose_name = _(u'姓名'), max_length = 10,null= True,blank = True,editable = False)),
                   ('Dept_name',models.CharField(verbose_name = _(u'部门名称'), max_length = 50,null= True,blank = True,editable = False)),
                   ('money',models.DecimalField(max_digits = 9,decimal_places = 2,default = Decimal('50'),null = True,blank = False, verbose_name=_(u"退款金额"),editable=False)),
                   ('blances',models.DecimalField(max_digits = 10,decimal_places = 2,default = Decimal('0'), null = True,blank = True,verbose_name=_(u"账上余额"),editable=False)),
                   ('card_blance',models.DecimalField(max_digits = 10,decimal_places = 2,default = Decimal('0'), null = True,blank = True,verbose_name=_(u"卡上余额"),editable=False)),
                   ('op_card_blance',models.DecimalField(max_digits = 10,decimal_places = 2,default = Decimal('0'), null = True,blank = True,verbose_name=_(u"退后金额"),editable=False)),
               )
            @transaction.commit_on_success
            def action(self,card,money,blances,name,labor,card_serial_no,op_card_blance,card_blance,Dept_name,sys_card_no):
                from mysite.pos.models import CarCashSZ, CarCashType,TimeBrush
                if card:
                    objcard=IssueCard.objects.filter(cardno=int(card))
                    if objcard:
                        if objcard[0].card_privage == PRIVAGE_CARD:
                            raise Exception(_(u"管理卡，操作失败"))
    #                    if  objcard[0].cardstatus == CARD_LOST:
    #                       raise Exception(_(u"该卡已挂失，操作失败"))
    #                    if  objcard[0].cardstatus == CARD_STOP:
    #                       raise Exception(_(u"该卡已停用，操作失败"))
                        if money<0:
                           raise Exception(_(u"退款金额不能为负数"))
                        if money==0:
                            raise Exception(_(u"退款金额不能为零"))
                        if money>objcard[0].blance:
                           raise Exception(_(u"退款金额超出卡余额"))
                        from mysite.pos.pos_id.posdevview import read_timebrush
                        objbatch = read_timebrush(card)
                        if objbatch:
                            type=objbatch.split(':')[0]
                            if type=='1':#计时开始
                                raise Exception(_(u'当前用户计时消费未结账，不能退款'))
                        newblance = objcard[0].blance - money
                        blance_valid(objcard[0].type_id,newblance,objcard[0].UserID)#验证余额
                        try:
                            objcard[0].blance = newblance
                            objcard[0].save()
                            CarCashSZ(user=objcard[0].UserID,
                                      card=int(card),
                                      checktime = datetime.datetime.now(),
                                      type_id=5,#charge type
                                      money=money,
                                      hide_column=5,blance=objcard[0].blance).save()
                            transaction.commit()
                        except:
                            raise Exception(_(u"退款失败"))
                            transaction.rollback()
                            import traceback;traceback.print_exc()
                            pass
                    else:
                        raise Exception(_(u"卡号不存在"))
                else:
                    pass
#                    raise Exception(_(u"卡号不能为空"))
                

        class OpCharge(Operation):
            help_text=_(u"""充值：当前操作只对消费有效！""")
            verbose_name = _(u"充值")
            only_one_object = True
            visible=get_option("POS_ID")
            item_index=2
            params=(
                  ('blance',models.DecimalField(max_digits=9,decimal_places=2,default=Decimal('0'), verbose_name=_(u"金额"))),
                )
            @transaction.commit_on_success
            def action(self,blance):
                from mysite.pos.models import CarCashSZ, CarCashType
                if  self.object.card_privage == PRIVAGE_CARD:
                    raise Exception(_(u"该卡是管理卡，操作失败"))
                if  self.object.cardstatus == CARD_LOST:
                    raise Exception(_(u"该卡已经挂失，操作失败"))
                if  self.object.cardstatus == CARD_STOP:
                    raise Exception(_(u"该卡已经停用，操作失败"))
                if  self.object.cardstatus == CARD_OVERDUE:
                    raise Exception(_(u"该卡已过期，操作失败"))
                if blance<0:
                    raise Exception(_(u"充值金额不能为负数"))
                if blance==0:
                   raise Exception(_(u"充值金额不能为零"))
                
                newblance = self.object.blance + blance
                blance_valid(self.object.type_id,newblance,self.object.UserID)#验证余额
                try:
                    self.object.blance = newblance
                    self.object.save()
                    CarCashSZ( user=self.object.UserID,
                               card=self.object.cardno,
                               checktime = datetime.datetime.now(),
                               type_id=1,#charge type
                               money=blance,
                               hide_column=1,blance = self.object.blance).save()
                except:
                    raise Exception(_(u"充值失败"))
                    import traceback;traceback.print_exc()
                    pass
            
        
        class OpRefund(Operation):
            only_one_object = True
            help_text=_(u"退款：当前操作只对消费有效！")
            verbose_name = _(u"退款")
            visible=get_option("POS_ID")
            item_index=2
            params=(
                    ('blance',models.DecimalField(max_digits=9,decimal_places=2,default=Decimal('0'),editable=True,verbose_name=_(u"金额"))),
                    )
            @transaction.commit_on_success
            def action(self, blance):
                from mysite.pos.models import CarCashSZ, CarCashType,TimeBrush
                if  self.object.card_privage == PRIVAGE_CARD:
                    raise Exception(_(u"该卡是管理卡，操作失败"))
#                if  self.object.cardstatus == CARD_STOP:
#                    raise Exception(_(u"该卡已停用，操作失败"))
                if blance==0:
                   raise Exception(_(u"退款金额不能为零"))
                if blance<0:
                    raise Exception(_(u"退款金额不能为负数"))
                from mysite.pos.pos_id.posdevview import read_timebrush
                objbatch = read_timebrush(self.object.cardno)
                if objbatch:
                    type=objbatch.split(':')[0]
                    if type=='1':#计时开始
                        raise Exception(_(u'当前用户计时消费未结账，不能退款'))
                newblance = self.object.blance - blance
                if newblance < 0:
                    raise Exception(_(u'余额不足'))
                blance_valid(self.object.type_id,newblance,self.object.UserID)#验证余额
                try:
                    self.object.blance = newblance
                    self.object.save()
                    #sync to carcashsz
                    CarCashSZ( user=self.object.UserID,
                               card = self.object.cardno,
                               checktime = datetime.datetime.now(),
                               type_id=5,
                               money=blance,
                               hide_column=5,blance = self.object.blance).save()
                except:
                    raise Exception(_(u"退款失败"))
                    import traceback;traceback.print_exc()
                    pass
                           
        class OpRetireCard(Operation):
            help_text=_(u"退卡成功后，系统会清除该人员卡信息！")
            verbose_name = _(u"退卡")
            only_one_object = False
            visible= not get_option("POS_IC")
            item_index=6
            params = (
                            ('card_cost',models.DecimalField (max_digits=8,decimal_places=2,default=Decimal('0'),null=True,blank=True, verbose_name=_(u"退还卡成本（元）"))),
                        )
            def __init__(self,obj):
               super(IssueCard.OpRetireCard, self).__init__(obj)
               params = dict(self.params)
               isobj = IssueCard.objects.filter(pk=obj.pk)[0]
               params['card_cost'].default=isobj.card_cost
            @transaction.commit_on_success
            def action(self,card_cost):
                from mysite.pos.models import CarCashSZ, CarCashType
                if get_option("POS"):
                    if self.object.blance > 0:
                        raise Exception(_(u'卡号%s请先退款')%self.object.cardno)
                    if  self.object.card_privage <> PRIVAGE_CARD:
                        cash = CarCashSZ( user=self.object.UserID,
                                   card=self.object.cardno,
                                   checktime = datetime.datetime.now(),
                                   type_id=4,#retire cost type
                                   money=card_cost,
                                   hide_column=4,blance=self.object.blance)
                        cash.save()
                    else:#删除管理卡
                        from mysite.pos.models.model_cardmanage import CardManage
                        obj_card_manage = CardManage.objects.get(card_no = self.object.cardno)
                        obj_card_manage.delete()
                try:
                    self.object.delete()
                    key="IssueCard_%s" %self.object.cardno
                    cache.delete(key)
                    from mysite.iclock.models.dev_comm_operate import sync_delete_user,sync_delete_user_privilege,sync_delete_user,sync_report_user
                    from mysite.personnel.models.model_leave import get_leave_user_info
                    if get_option("ATT") and self.object.card_privage <> PRIVAGE_CARD and not get_leave_user_info(self.object.UserID,"isClassAtt"):
                        from base.sync_api import SYNC_MODEL
                        if not SYNC_MODEL:
                            #更新了卡号
                            from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                            adj_user_cmmdata(self.object.UserID, [], self.object.UserID.attarea.all())
                        
                    if get_option("IACCESS") and self.object.card_privage <> PRIVAGE_CARD and not get_leave_user_info(self.object.UserID,"isClassAccess"):
                        from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege    #-----2012.02.02   xiaoxiaojun                 
                        newObj=self.object.UserID
                        accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
                        sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
#                        sync_set_user_privilege(accdev, [newObj]) #下放人员权限到设备
                except:
                    import traceback;traceback.print_exc()
                    raise Exception(_(u"退卡失败"))
                    
        
        class OpNoCardRetireCard(Operation):
            help_text=_(u"无卡退卡：挂失人员找不到原有卡或者原有卡损坏，可以通过当前操作进行退卡操作，结束当前卡账号的系统业务！为了保证账目准确，系统不支持无卡退款业务。请确保所有消费记录采集完整后，根据系统卡上余额，进行卡余额验证！当前操作只对消费挂失卡有效！")
            verbose_name = _(u"无卡退卡")
            only_one_object = True
            visible= get_option("POS_IC")
            item_index=9
            from model_emp import YESORNO
            params = (
#                ('card_cost',models.DecimalField (max_digits=8,decimal_places=2,default=Decimal('0'),null=True,blank=True, verbose_name=_(u"退还卡成本（元）"))),
                ('is_retire_money', models.BooleanField(verbose_name=_(u'是否退还卡上余额'),null=False,default=False,  editable=True)),
                ('re_money',models.DecimalField (max_digits=8,decimal_places=2,default=Decimal('0'),null=True,blank=True, verbose_name=_(u"卡余额（元）"))),
            )
            def __init__(self,obj):
                super(IssueCard.OpNoCardRetireCard, self).__init__(obj)
                params = dict(self.params)
                isobj = IssueCard.objects.filter(pk=obj.pk)[0]
#                params['card_cost'].default=isobj.card_cost
                params['re_money'].default=isobj.blance
            @transaction.commit_on_success
            def action(self,is_retire_money,re_money):
                from mysite.pos.models import CarCashSZ, CarCashType
                from base.cached_model import STATUS_INVALID,STATUS_LEAVE
                from mysite.personnel.models.model_leave import get_leave_user_info
#                if not self.object.sys_card_no:
#                    raise Exception(_(u'当前操作卡片没有登记卡账号，操作失败！'))
                if self.object.card_privage ==  PRIVAGE_CARD:
                    raise Exception(_(u'该卡为管理卡，操作失败'))
                if self.object.card_privage ==  OPERATE_CARD:
                    raise Exception(_(u'该卡为操作卡，操作失败'))
                if self.object.cardstatus in [CARD_VALID,CARD_OVERDUE]:
                    raise Exception(_(u'请先挂失，操作失败'))
                try:
                    card_blance = self.object.blance
                    self.object.status = STATUS_INVALID
                    self.object.cardstatus = CARD_INVALID
                    self.object.failuredate = datetime.datetime.now()
                    if is_retire_money:
                        self.object.blance = 0
                    self.object.save()
                    from mysite.iclock.models.dev_comm_operate import delete_pos_device_info,sync_report_user,sync_delete_user_privilege,sync_delete_user
                    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                    from mysite.pos.models.model_loseunitecard import LoseUniteCard
                    if self.object.sys_card_no:
                        dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                        delete_pos_device_info(dev,[self.object],"USERINFO")#删除白名单
#                        LoseUniteCard.objects.all().filter(UserID = self.object.UserID).delete()#删除挂失解挂记录
                    if get_option("ATT") and  not get_leave_user_info(self.object.UserID,"isClassAtt"):
                        from base.sync_api import SYNC_MODEL
                        if not SYNC_MODEL:
                            #更新了卡号
                            from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                            adj_user_cmmdata(self.object.UserID, [], self.object.UserID.attarea.all())
                    if get_option("IACCESS") and not get_leave_user_info(self.object.UserID,"isClassAccess"):
                        from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege    #-----2012.02.02   xiaoxiaojun                 
                        newObj=self.object.UserID
                        accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
                        sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
                        
#                    if self.object.cardstatus==CARD_VALID and  get_option("ATT"):
#                        oldObj=self.object.UserID
#                        devs=oldObj.search_device_byuser()
#                        sync_report_user(devs, [oldObj])
#                    if self.object.cardstatus==CARD_VALID and get_option("IACCESS"):
#                        oldObj=self.object.UserID
#                        if oldObj.check_accprivilege():
#                           devs=oldObj.search_accdev_byuser()
#                           sync_report_user(devs,[oldObj]) 
#                           #sync_delete_user_privilege(devs,[oldObj])
                    
                    if is_retire_money and card_blance > 0:
                        CarCashSZ(user = self.object.UserID,
                             card = self.object.cardno,
                             checktime = datetime.datetime.now(),
                             type_id = 5,#退款
                             money = card_blance,
                             blance = 0,
                             sys_card_no = self.object.sys_card_no,
                             log_flag = 2,
                             hide_column = 14).save()
                    CarCashSZ(user = self.object.UserID,
                            card = self.object.cardno,
                            checktime = datetime.datetime.now(),
                            type_id = 4,#退卡成本
                            money = 0,
                            blance = self.object.blance,
                            sys_card_no = self.object.sys_card_no,
                            log_flag = 2,
                            hide_column = 4).save()
                except:
#                    raise Exception(_(u"退卡失败"))
                    import traceback;traceback.print_exc()
        
        class RestateCard(Operation):
            help_text=_(u"启用卡：重新激活停用卡！")
            verbose_name = _(u"启用卡")
            only_one_object = True
            item_index=8
            visible = False
            @transaction.commit_on_success
            def action(self):
                from mysite.pos.models import CarCashSZ, CarCashType
                if get_option("POS_IC") and not self.object.sys_card_no:
                    raise Exception(_(u'当前操作卡片没有登记卡账号，操作失败！'))
                if self.object.card_privage ==  PRIVAGE_CARD:
                    raise Exception(_(u'该卡为管理卡，操作失败'))
                if self.object.card_privage ==  OPERATE_CARD:
                    raise Exception(_(u'该卡为操作卡，操作失败'))
                from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
                if self.object.UserID.status == STATUS_LEAVE:
                   raise Exception(_(u'该人员已经离职，操作失败'))
                if self.object.cardstatus <> CARD_STOP:
                    raise Exception(_(u'该操作只对停用卡有效，操作失败'))
                obj = IssueCard.objects.filter(UserID = self.object.UserID,cardstatus = CARD_VALID)
                if obj:
                    raise Exception(_(u'该人员已有正在使用的卡,操作失败'))
                try:
                    self.object.cardstatus = CARD_VALID
                    self.object.save()
                    key = cache_key(self.object,self.object.pk)
                    cache.delete(key)
                    if get_option("POS_IC"):#启用名单下发
                        from mysite.iclock.models.dev_comm_operate import delete_pos_device_info
                        from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                        dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                        delete_pos_device_info(dev,[self.object],"USERINFO")
                    if get_option("ATT"):
                        from mysite.iclock.device_http.constant import SYNC_MODEL
                        if SYNC_MODEL:
                            pass
                        #>>> 更新了卡号
                        else:
                            from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                            adj_user_cmmdata(self.object.UserID, [], self.object.UserID.attarea.all())
                       
                    if get_option("IACCESS"):
                        from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege                  
                        newObj=self.object.UserID
                        accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
                        sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
                        sync_set_user_privilege(accdev, [newObj]) #下放人员权限到设备

                    
                except:
                    raise Exception(_(u"启用卡失败"))
                    import traceback;traceback.print_exc()
                    pass
                
        class CancelManageCard(Operation):
            help_text=_(u"注销管理卡：注销管理卡跟操作卡！当前操作只对消费权限卡有效！")
            verbose_name = _(u"注销管理卡")
            only_one_object = True
            item_index=9
            visible = get_option("POS_IC")
            @transaction.commit_on_success
            def action(self):
                from mysite.pos.models.model_cardmanage import CardManage,CARD_CANCEL
                from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
                if self.object.card_privage not in [PRIVAGE_CARD,OPERATE_CARD]:
                    raise Exception(_(u'当前操作只对管理卡或者操作卡有效，操作失败'))
                try:
                    obj_manage = CardManage.objects.get(sys_card_no = self.object.sys_card_no)
                    obj_manage.cardstatus = CARD_CANCEL
                    obj_manage.save()
                    self.object.status = STATUS_INVALID
                    self.object.save()
                    from mysite.iclock.models.dev_comm_operate import delete_pos_device_info
                    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                    dev = Device.objects.filter(device_type = DEVICE_POS_SERVER,dining = obj_manage.dining)
                    delete_pos_device_info(dev,[self.object],"USERINFO")
                except:
#                    raise Exception(_(u"注销卡失败"))
                    import traceback;traceback.print_exc()
                    pass

        class InitCardPwd(ModelOperation):
            help_text=_(u"初始化IC卡扇区数据或者修改IC卡密码。当前操作只对消费有效！")
            verbose_name = _(u"初始化卡")
            only_one_object = True
            visible = get_option("POS_IC")
            item_index=8
            params=(
                    ('init_pwd', models.CharField(verbose_name=_(u"原密码"),max_length=6,null=True,blank=True)),
                    ('is_null_pwd', models.BooleanField(verbose_name=_(u'空密码'), default=False)),
                    )
            def action(self,init_pwd,is_null_pwd):
                pass 
            
        class _delete(Operation):
            help_text = _(u"删除选定记录") #删除选定的记录
            verbose_name = _(u"删除")
            visible = False
            def action(self):
                pass
                
        class _change(Operation):
            help_text = _(u"修改选定记录")
            verbose_name = _(u"修改")
            visible = False
            def action(self):
                pass
        
        def get_pin(self):
            from mysite.personnel.models.model_emp import getuserinfo
            return getuserinfo(self.UserID_id,"PIN")
        
        def get_ename(self):
            from mysite.personnel.models.model_emp import getuserinfo
            return getuserinfo(self.UserID_id,"EName")
            
        def get_dept_name(self):
            from mysite.personnel.models.model_emp import get_dept
            return get_dept(self.UserID_id).name
#       得到卡类型
        def get_type(self):
            from mysite.personnel.models.model_iccard import ICcard
            name=""
            if not self.type_id:
              return name
            try:
              name=ICcard.objects.get(id=self.type_id)
              name=u"%s"%name.name
            except:
               import traceback;traceback.print_exc()
               pass
            return name
        
        def get_dept_code(self):
            from mysite.personnel.models.model_emp import get_dept
            return get_dept(self.UserID_id).code
        
        def forma_issuedate(self):
            if type(self.issuedate) == type(datetime.datetime.now()):
                iscardate = self.issuedate.date()
            else:
                iscardate = self.issuedate
            return iscardate
        
        
        class OpLoseCard(Operation):
                if get_option("POS_IC"):
                    help_text = _(u'挂失卡：系统会下发挂失指令，同步挂失人员资料到设备！建议操作过程中保持设备与服务器处于连接状态！')
                else:
                    help_text = _(u'挂失卡')
                verbose_name = _(u'挂失')
                visible = get_option("POS")
                only_one_object = True
                item_index=4
                def action(self):
                    from mysite.pos.models.model_loseunitecard import LoseUniteCard
                    from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
                    from mysite.personnel.models.model_leave import get_leave_user_info
                    if get_option("POS_IC") and self.object.card_privage ==  PRIVAGE_CARD:
                        raise Exception(_(u'该卡为管理卡，操作失败'))
                    if get_option("POS_IC") and self.object.card_privage ==  OPERATE_CARD:
                        raise Exception(_(u'该卡为操作卡，操作失败'))
#                    if get_option("POS_IC") and not self.object.sys_card_no:
#                        raise Exception(_(u'当前操作卡片没有登记卡账号，操作失败！'))
                    if self.object.cardstatus==CARD_LOST:
                        raise Exception(_(u"该卡已挂失，操作失败"))
                    if self.object.cardstatus==CARD_STOP:
                        raise Exception(_(u"该卡已停用，操作失败"))
#                    if self.object.cardstatus==CARD_OVERDUE:
#                        raise Exception(_(u"该卡已过期，操作失败"))
                    try:
                        self.object.cardstatus=CARD_LOST
                        self.object.save()
                        if get_option("POS_ID"):
                            if self.object.card_privage == PRIVAGE_CARD:
                                from mysite.pos.models.model_cardmanage import CardManage
                                LoseUniteCard(
                                             cardno = self.object.cardno,
                                             type = self.object.type,
                                             cardstatus=CARD_LOST,
                                             time = datetime.datetime.now()).save()
                                obj_card_manage = CardManage.objects.get(card_no = self.object.cardno)
                                obj_card_manage.cardstatus = CARD_LOST
                                obj_card_manage.save()
                            else:
                                LoseUniteCard(UserID = self.object.UserID,
                                         cardno = self.object.cardno,
                                         type = self.object.type,
                                         cardstatus=CARD_LOST,
                                         time = datetime.datetime.now()).save()
                        from mysite.iclock.models.dev_comm_operate import update_pos_device_info,sync_delete_user,sync_delete_user_privilege,sync_delete_user,sync_report_user
                        if get_option("POS_IC") and self.object.sys_card_no:#挂失名单下发
                            LoseUniteCard(UserID = self.object.UserID,
                                         cardno = self.object.cardno,
                                         type = self.object.type,
                                         cardstatus=CARD_LOST,
                                         sys_card_no=self.object.sys_card_no,
                                         Password=self.object.Password,
                                         time = datetime.datetime.now()).save()
                            from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                            update_pos_device_info(dev,[self.object],"USERINFO")
                        if get_option("ATT") and self.object.card_privage <> PRIVAGE_CARD and not get_leave_user_info(self.object.UserID,"isClassAtt"):
                            from base.sync_api import SYNC_MODEL
                            if not SYNC_MODEL:
                                oldObj=self.object.UserID
                                devs=oldObj.search_device_byuser()
                                sync_report_user(devs, [oldObj])
                        if get_option("IACCESS") and self.object.card_privage <> PRIVAGE_CARD and not get_leave_user_info(self.object.UserID,"isClassAccess"):
                            oldObj=self.object.UserID
                            if oldObj.check_accprivilege():
                                devs=oldObj.search_accdev_byuser()
                                sync_report_user(devs,[oldObj]) 
                    except:
#                        raise Exception(_(u"操作失败"))
                        import traceback;traceback.print_exc()
                        pass
                        
        class OpRevertCard(Operation):
                if get_option("POS_IC"):
                    help_text = _(u'解挂卡：系统会下发解挂指令，清除设备挂失人员资料！建议操作过程中保持设备与服务器处于连接状态！')
                else:
                    help_text = _(u'解挂卡')
                verbose_name = _(u'解挂')
                visible = get_option("POS")
                only_one_object = True
                item_index=5
                def action(self):
                    from mysite.pos.models.model_loseunitecard import LoseUniteCard
                    from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
                    if get_option("POS_IC") and self.object.card_privage ==  PRIVAGE_CARD:
                       raise Exception(_(u'该卡为管理卡，操作失败'))
                    if get_option("POS_IC") and self.object.card_privage ==  OPERATE_CARD:
                       raise Exception(_(u'该卡为操作卡，操作失败'))
                    if self.object.card_privage <> PRIVAGE_CARD and self.object.UserID.status == STATUS_LEAVE:
                       raise Exception(_(u'该人员已经离职，操作失败'))
                    if self.object.cardstatus==CARD_VALID:
                        raise Exception(_(u"请先挂失"))  
                    if self.object.cardstatus==CARD_STOP:
                        raise Exception(_(u"该卡已经停用,操作失败")) 
                    if self.object.cardstatus==CARD_OVERDUE:
                        raise Exception(_(u"该卡已过期，操作失败"))
                    if self.object.card_privage <> PRIVAGE_CARD:#排场ID消费管理卡解挂
                        obj = IssueCard.objects.filter(UserID = self.object.UserID,cardstatus = CARD_VALID)
                    else:
                        obj = None
                    if obj:
                        raise Exception(_(u'该人员已有正在使用的卡,操作失败'))
                    try:
                        self.object.cardstatus=CARD_VALID
                        self.object.save()
                        if get_option("POS_ID"):
                            if self.object.card_privage == PRIVAGE_CARD:
                                from mysite.pos.models.model_cardmanage import CardManage
                                LoseUniteCard(
                                         cardno = self.object.cardno,
                                         type = self.object.type,
                                         cardstatus=CARD_VALID,
                                         time = datetime.datetime.now()).save()
                                obj_card_manage = CardManage.objects.get(card_no = self.object.cardno)
                                obj_card_manage.cardstatus = CARD_VALID
                                obj_card_manage.save()
                            else:
                                LoseUniteCard(UserID = self.object.UserID,
                                         cardno = self.object.cardno,
                                         type = self.object.type,
                                         cardstatus=CARD_VALID,
                                         time = datetime.datetime.now()).save()
                        if get_option("POS_IC") and self.object.sys_card_no:#解挂名单下发
                            LoseUniteCard(UserID = self.object.UserID,
                                cardno = self.object.cardno,
                                type = self.object.type,
                                cardstatus=CARD_VALID,
                                sys_card_no=self.object.sys_card_no,
                                Password=self.object.Password,
                                time = datetime.datetime.now()).save()
                            from mysite.iclock.models.dev_comm_operate import delete_pos_device_info
                            from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                            delete_pos_device_info(dev,[self.object],"USERINFO")
                        if get_option("ATT")  and self.object.card_privage <> PRIVAGE_CARD:
                            from mysite.iclock.device_http.constant import SYNC_MODEL
                            if SYNC_MODEL:
                                pass
                            #>>> 更新了卡号
                            else:
                                from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                                adj_user_cmmdata(self.object.UserID, [], self.object.UserID.attarea.all())
                            
                        if get_option("IACCESS")  and self.object.card_privage <> PRIVAGE_CARD:
                            from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege    #-----2012.02.02   xiaoxiaojun                 
                            newObj=self.object.UserID
                            accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
                            sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
#                            sync_set_user_privilege(accdev, [newObj]) #下放人员权限到设备
                    except:
#                        raise Exception(_(u"操作失败"))
                        import traceback;traceback.print_exc()
                        pass
    

        class Admin(CachingModel.Admin):
                sort_fields = ["UserID.PIN","issuedate","blance"]
                app_menu = "personnel"
                list_filter = ('UserID', 'cardno', 'isvalid')
                query_fields = get_option("ISSUECARD_QUERY_FIELDS")
                list_display = get_option("ISSUECARD_LIST_DISPLAY")
                adv_fields = get_option("ISSUECARD_ADV_FIELDS")
                default_widgets={
                'mng_cost':ZBaseMoneyWidget,
                'blance':ZBaseMoneyWidget,
                'card_cost':ZBaseMoneyWidget,}
                newadded_column = {
                   'UserID.DeptID.code':'get_dept_code',
                   'UserID.DeptID.name':'get_dept_name',
                   "UserID.PIN":"get_pin",
                   "UserID.EName":"get_ename",
                    "type.name":"get_type",
                    "issuedate":"forma_issuedate",
                                    }                            
                default_widgets = {
#                               'blance':ZBaseNormalFloatWidget,
#                               'mng_cost':ZBaseNormalFloatWidget,
#                               'card_cost':ZBaseNormalFloatWidget,
#                               'Password':ZBaseIntegerWidget,
                               }
                
                cache = 3600
                menu_index = 9
                hide_fields = get_option("ISSUECARD_DISABLE_COLS")
#                if get_option("POS_ID"):
                disabled_perms = ["dataimport_issuecard", "change_issuecard",'delete_issuecard']
#                else:
#                    disabled_perms = ["dataimport_issuecard", "change_issuecard",'delete_issuecard','opretirecard_issuecard','resetpassword_issuecard','opcharge_issuecard','cardtypeset_issuecard','oprefund_issuecard']
                    
                help_text = _(u'%s'%get_option("ISSUECARD_HELP_TEXT"))   #_(u"目前支持手动输入卡号、使用发卡器等其他外设发卡！")
        class Meta:
                app_label = 'personnel'
                if get_option("POS"):
                    verbose_name = _(u'卡管理')
                else:
                    verbose_name = _(u'人员发卡')
                verbose_name_plural = verbose_name




def set_cache_Allissucard():
    from mysite.pos.pos_constant import TIMEOUT 
    try:
        if IssueCard.objects.count() > 0:
            carcache = cache.get("ALLIssueCard")
            if not carcache and not type(carcache)==list:
                allcard = IssueCard.objects.all()
                if get_option("POS_ID"):
                    cache.set("ALLIssueCard","tag_ALLIssueCard",TIMEOUT)
                else:
                    cache.set("ALLIssueCard",list(allcard),TIMEOUT)
                for obj in allcard:
                   iskey="IssueCard_%s" %obj.cardno
                   cache.set(iskey,obj,TIMEOUT)
    except:
        pass

if get_option("POS_ID"):
    set_cache_Allissucard()


from dbapp import data_edit
def detail_resplonse(sender, **kargs):
    from mysite.iclock.models.model_dininghall import Dininghall
    from dbapp.widgets import form_field, check_limit
    if kargs['dataModel'] == IssueCard:
        form = sender['form']
        dining = models.ForeignKey(Dininghall,verbose_name=_(u'所属餐厅'),editable=True, blank=True,null=True)
        form.fields['dining'] = form_field(dining)
data_edit.pre_detail_response.connect(detail_resplonse)


def DataPostCheck(sender, **kwargs):
    from django.db.models import Model
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    card_dining = request.REQUEST.get("dining", "")
    cardno = request.REQUEST.get("cardno", "")
    pwd = request.REQUEST.get("Password", "")
    card_privage = request.REQUEST.get("card_privage", "")
    if isinstance(newObj, IssueCard):
        if get_option("POS_ID") and card_privage == PRIVAGE_CARD:
            from mysite.pos.models.model_cardmanage import CardManage
            CardManage(card_no = int(cardno),
            pass_word = pwd,
            dining_id = card_dining,
            cardstatus = CARD_VALID).save()
data_edit.post_check.connect(DataPostCheck)
