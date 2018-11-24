# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _

from mysite.personnel.models.model_emp import Employee, EmpForeignKey
from django.conf import settings
import datetime

class ReplenishCard(CachingModel):
    user = EmpForeignKey(verbose_name=_(u"人员"), null=False, editable=True)
    oldcardno = models.CharField(verbose_name=_(u'原卡号'), max_length=20,null=True, blank=True, editable=True)
    newcardno = models.CharField(verbose_name=_(u'现卡号'), max_length=20,null=True, blank=True, editable=True)
    blance = models.DecimalField(verbose_name=_(u'卡金额'),max_digits=20,null=True, blank=True,decimal_places=2,editable=True)
    time = models.DateTimeField(verbose_name=_(u'补卡日期'), null=True, blank=True, editable=False,auto_now_add=True)
    def __unicode__(self): 
         return ""
#        try:
#            return u"%s,%s"%(self.user,self.newcardno)
#        except:
#            return u"%s,%s"%(self.user,self.newcardno)
    def get_pin(self):
           from mysite.personnel.models.model_emp import getuserinfo
           return getuserinfo(self.user_id,"PIN")
             
    def get_ename(self):
           from mysite.personnel.models.model_emp import getuserinfo
           return getuserinfo(self.user_id,"EName")
#    def save(self,*args, **kwargs):
#        from base.middleware import threadlocals
#        op=threadlocals.get_current_user()
#        self.create_operator = op.username
#        super(ReplenishCard,self).save()
    
    class Admin(CachingModel.Admin):
        sort_fields=["-time",'time']
        app_menu="pos"
        menu_group = 'pos'
        menu_index = 50
        cache = 3600
        visible = False
        default_give_perms = ["contenttypes.can_consumeAppReport"]
        list_display=['user.PIN', 'user.EName', 'oldcardno', 'newcardno','blance','time','create_operator']
        query_fields=['user.PIN', 'user.EName', 'oldcardno', 'newcardno', 'time']
        adv_fields = ['user.PIN', 'user.EName', 'oldcardno', 'newcardno', 'time']
        newadded_column = {
                         "user.PIN":"get_pin",
                         "user.EName":"get_ename",
                        }                               
        
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
        verbose_name = _(u"换卡表")
        verbose_name_plural=verbose_name
