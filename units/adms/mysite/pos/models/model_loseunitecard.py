# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _

from mysite.personnel.models.model_emp import Employee, EmpForeignKey
from mysite.personnel.models.model_iccard import ICcardForeignKey
from django.conf import settings
import datetime
from mysite.utils import get_option

CARDSTATUS = (
        ('3', _(u'挂失')),
        ('1', _(u'解挂')),
)

POS_CARD = '0'
PRIVAGE_CARD = '1'
OPERATE_CARD = '2'

PRIVAGE = (
        (POS_CARD, _(u'普通卡')),
        (PRIVAGE_CARD, _(u'管理卡')),
        (OPERATE_CARD, _(u'操作卡')),
        )

class LoseUniteCard(CachingModel):
    sys_card_no = models.CharField(max_length=20,verbose_name=_(u'卡账号'),editable=False, null=True, blank=True,)
    UserID = EmpForeignKey(verbose_name=_(u"人员"), null=True, editable=True)
    cardno = models.CharField(verbose_name=_(u'卡号'), max_length=20,null=False, blank=True, editable=True)
    type=ICcardForeignKey(verbose_name=_(u'卡类'),editable=True,null=True,blank=True)
    cardstatus = models.CharField(verbose_name=_(u'卡状态'), max_length=3, choices=CARDSTATUS, null=True, blank=True,editable=False)
    Password = models.CharField(_(u'卡密码'), max_length=6, null=True, blank=True, editable=False)
    time = models.DateTimeField(verbose_name=_(u'操作日期'), null=True, blank=True, editable=False, auto_now_add=True)#default=datetime.datetime.now().strftime("%Y-%m-%d"))
    card_privage = models.CharField(_(u'卡类型'), max_length=20, null=True, blank=True, choices=PRIVAGE,default=POS_CARD)
    def __unicode__(self): 
        try:
            return u"%s,%s"%(self.UserID,self.cardno)
        except:
            return u"%s,%s"%(self.UserID,self.cardno)
#    def save(self,*args, **kwargs):
#        from base.middleware import threadlocals
#        op=threadlocals.get_current_user()
#        self.create_operator = op.username
#        super(LoseUniteCar,self).save()
    class Admin(CachingModel.Admin):
        sort_fields=["-time",'time']
        app_menu="pos"
        menu_group = 'pos'
        menu_index = 50
        cache = 3600
        visible = False
        default_give_perms = ["contenttypes.can_consumeAppReport"]
        if get_option("POS_IC"):
            list_display=['UserID.PIN', 'UserID.EName', 'cardno','sys_card_no', 'type','cardstatus','time','create_operator']
            query_fields=['UserID.PIN', 'UserID.EName', 'cardno','sys_card_no', 'type','cardstatus','time']
            adv_fields = ['UserID.PIN', 'UserID.EName', 'cardno','sys_card_no','type','cardstatus','time']
        else:
            list_display=['UserID.PIN', 'UserID.EName', 'cardno', 'type','cardstatus','time','create_operator']
            query_fields=['UserID.PIN', 'UserID.EName', 'cardno', 'type','cardstatus','time']
            adv_fields = ['UserID.PIN', 'UserID.EName', 'cardno', 'type','cardstatus','time']
            
    class _delete(Operation):
                help_text = _(u"删除选定记录") #删除选定的记录
                verbose_name = _(u"删除")
                visible=False
                def action(self):
                    pass   
              
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
        verbose_name = _(u"挂失解挂表")
        verbose_name_plural=verbose_name
