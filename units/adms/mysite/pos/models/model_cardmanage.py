#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
from mysite.iclock.models.model_dininghall import Dininghall
from mysite.utils import get_option
from mysite.pos.pos_id.pos_id_util import set_pos_info_record
CARD_VALID = '1'
CARD_LOST = '3'
CARD_CANCEL = '2'

PRIVAGE_CARD = '1'
OPERATE_CARD = '2'
PRIVAGE = (
       (PRIVAGE_CARD, _(u'管理卡')),
       (OPERATE_CARD, _(u'操作卡')),
       )

CARDSTATUS = (
        (CARD_VALID, _(u'有效')),
        (CARD_LOST, _(u'挂失')),
        (CARD_CANCEL, _(u'注销')),
)

class CardManage(CachingModel):
    sys_card_no = models.CharField(max_length=20,verbose_name=_(u'卡账号'),editable=False, null=True, blank=True,)
    card_no = models.CharField(max_length=20,verbose_name=_(u'卡号'),editable=False)
    pass_word = models.CharField(_(u'卡密码'), max_length=6, null=True, blank=True, editable=False)
    dining = models.ForeignKey(Dininghall,verbose_name=_(u'所属餐厅'),editable=True, blank=True,null=True)
    cardstatus = models.CharField(verbose_name=_(u'卡状态'), max_length=3, choices=CARDSTATUS, null=False, blank=True,editable=True)
    time = models.DateTimeField(verbose_name=_(u'发卡日期'), null=True, blank=True, editable=False, auto_now_add=True)
    card_privage = models.CharField(_(u'卡权限'), max_length=20, null=True, blank=True,default=1,choices = PRIVAGE)
    def __unicode__(self):
        return u"%s" %(self.card_no)
    
    def delete(self):
        super(CardManage, self).delete()     
        cache.delete("CardManage")
        key="CardManage_%s_%s" %(self.dining_id,self.card_no)
        cache.delete(key)
        set_pos_info_record()
    def save(self,*args, **kwargs):
        super(CardManage,self).save()
        cacheobj = CardManage.objects.all()
        cache.set("CardManage",list(cacheobj),TIMEOUT)
        key="CardManage_%s_%s" %(self.dining_id,self.card_no)
        cache.set(key,self,TIMEOUT)
        set_pos_info_record()
    class Admin(CachingModel.Admin):
        visible=False
        default_give_perms = ["contenttypes.can_consumeAppReport"]
        if get_option("POS_ID"):
            list_display=['card_no', 'dining.name','time','cardstatus','create_operator']
        else:
            list_display=['card_no','sys_card_no','dining.name','card_privage','cardstatus','time','create_operator']
            
    class Meta:
            verbose_name=_(u'管理卡表')
            verbose_name_plural=verbose_name
            app_label='pos'

