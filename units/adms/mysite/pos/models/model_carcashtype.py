#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType 
from mysite.utils import get_option


CASHTYPE=(
            (1,_(u'支入')),
            (2,_(u'支出')),
)


class CarCashType(CachingModel):
    name = models.CharField(max_length=50,verbose_name=_(u'类型名称'),null=False,blank=False,editable=True)
    type= models.SmallIntegerField(verbose_name=_(u'类型'),null=False,blank=False,editable=True,choices=CASHTYPE)
    remark= models.CharField(max_length=100,verbose_name=_(u'备注'),blank=True,editable=True,null=True)
    
    
    
    def __unicode__(self):
        return u"%s"%self.name
    
    class Admin(CachingModel.Admin):
                sort_fields=[""]
                visible = False
                app_menu="pos"
                menu_group = 'pos'
                menu_index =1
                query_fields=['name','type','remark']
                #default_widgets={'parent': ZDeptChoiceWidget}
                adv_fields=['name','type','remark']
                list_display=['name','type','remark']
                cache = 3600

                @staticmethod
                def initial_data(): 
                        if CarCashType.objects.count()==0:                           
                            CarCashType(id=1,name=u"%s"%_(u"充值"), type=1).save()#1
                            CarCashType(id=2,name=u"%s"%_(u"补贴"), type=1).save()#2
                           # CarCashType(id=3,name=u"%s"%_(u"批量充值"), type=1).save()#3
                            CarCashType(id=4,name=u"%s"%_(u"支出卡成本"), type=2).save()#4
                            CarCashType(id=5,name=u"%s"%_(u"退款"), type=2).save() #5                   
                            CarCashType(id=6,name=u"%s"%_(u"消费"), type=2).save()  #6
                            CarCashType(id=7,name=u"%s"%_(u"卡成本"), type=1).save()  #7
                            CarCashType(id=8,name=u"%s"%_(u"手工补消费"), type=2).save()  #8
                            CarCashType(id=9,name=u"%s"%_(u"纠错"), type=1).save()  #9
                            CarCashType(id=10,name=u"%s"%_(u"计次"), type=2).save()
                            CarCashType(id=11,name=u"%s"%_(u"管理费"), type=1).save() #11
                            CarCashType(id=12,name=u"%s"%_(u"计次纠错"), type=1).save()
                            if get_option("POS_IC"):
                                CarCashType(id=13,name=u"%s"%_(u"优惠充值"), type=1).save()
                           
                        pass
    def delete(self):
        if self.id not in  range(13):
            super(CarCashType, self).delete()                
    def __unicode__(self):
        return u"%s"%self.name               

    class Meta:
            verbose_name=_(u'卡现金类别')
            verbose_name_plural=verbose_name
            app_label='pos'    
            
class CashTypeForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):            
        super(CashTypeForeignKey, self).__init__(CarCashType, to_field=to_field, **kwargs)                  
