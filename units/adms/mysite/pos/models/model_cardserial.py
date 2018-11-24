# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
from django.conf import settings
import datetime

class CardSerial(CachingModel):
    cardno = models.CharField(_(u'卡号'),max_length=20, null=True, blank=True)
    serialnum = models.CharField(_(u'卡流水号'),max_length=20,null=True,blank=True)
    def __unicode__(self): 
        return u"%s,%s"%(self.cardno,self.serialnum)
    def save(self, **args):
       super(CardSerial, self).save()
    
    class Admin(CachingModel.Admin):
        app_menu="pos"
        menu_group = 'pos'
        menu_index = 11
        cache = 3600
        query_fields=['cardno','serialnum']
        
        visible = False
        
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
        verbose_name = _(u"卡流水号")
        verbose_name_plural=verbose_name
