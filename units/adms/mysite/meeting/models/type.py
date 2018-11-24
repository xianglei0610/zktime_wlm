#! /usr/bin/env python
#coding=utf-8
from base.models import AppOperation
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

YESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),
)

RULE_of_ATT_CHECKIN = (
    (0,_(u'最早原则')),
    (1,_(u'就近原则')),
)
RULE_of_ATT_CHECKOUT = (
    (0,_(u'最晚原则')),
    (1,_(u'就近原则')),
)


class Type(CachingModel):
    '''
        会议绩效暂时不考虑
    '''
    numberType = models.CharField( verbose_name=_(u'编号'),max_length=20)
    nameType = models.CharField(primary_key=True,verbose_name=_(u'会议类别'),max_length=50)
    inRules = models.IntegerField(verbose_name=_(u'会议签到取卡规则'),choices=RULE_of_ATT_CHECKIN,default=0)
    outRules = models.IntegerField(verbose_name=_(u'会议签退取卡规则'),choices=RULE_of_ATT_CHECKOUT,default=0)
#    performance = models.IntegerField(verbose_name=_(u'会议绩效'),null=False,blank=False,default=0)
    remark =models.CharField(verbose_name= _(u'备注'),max_length=100,editable=True,null=True,blank=True)
    
    def save(self,**args):
        types = Type.objects.filter(nameType=self.nameType)
        if len(types):
            raise Exception(_(u'会议类型已存在'))
        super(Type,self).save()
    def __unicode__(self):
        return u"%s %s" % (self.numberType,self.nameType)

    class Admin(CachingModel.Admin):    #管理该模型
#        sort_fields=[]      #需要排序的字段，放在列表中
        menu_group = 'meeting'          #在哪个app应用下
        menu_index=2                #菜单的摆放的位置
        visible=False
        query_fields=['nameType','inRules','outRules']     #需要查找的字段
        list_display=['nameType','inRules','outRules','remark'] #列表显示那些字段

        @staticmethod
        def initial_data(): 
            if Type.objects.count()==0:
                Type(nameType=u"%s"%_(u"小会"),).save()
                Type(nameType=u"%s"%_(u"周会"),).save()
                Type(nameType=u"%s"%_(u"例会"),).save()
            
    class Meta:
        verbose_name=_(u'会议类型')#名字
        verbose_name_plural=verbose_name
        app_label=  'meeting' #属于哪个app
        
        
class TypeForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
        super(TypeForeignKey, self).__init__(Type, to_field=to_field, **kwargs)



