# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from mysite.personnel.models import Employee, EmpForeignKey
from base.cached_model import CachingModel
from base.operation import Operation,ModelOperation

WORKTYPE=(
    (0,_(u'正常工作')),
    (1,_(u'平日加班')),
    (2,_(u'休息日加班')),
    (3,_(u'节假日加班')),
)
FLAG=(
    (1,_(u'仅临时排班有效')),
    (2,_(u'追加于员工排班之后')),

)
    ##员工临时排班表##
class USER_TEMP_SCH(CachingModel):
    UserID=EmpForeignKey(db_column='UserID',verbose_name=_(u'人员'), default=1,null=False, blank=False)
    ComeTime = models.DateTimeField(_(u'开始时间'),null=False, blank=False)
    LeaveTime = models.DateTimeField(_(u'结束时间'),null=False, blank=False)
    OverTime = models.IntegerField(_(u'加班时长'),null=False,default=0,blank=True)
    Type=models.SmallIntegerField(_(u'临时排班类型'),null=True,default=0,blank=True)
    Flag=models.SmallIntegerField(_(u'当天存在员工排班时'),null=True,default=1,blank=True,editable=True,choices=FLAG)
    SchclassID=models.IntegerField(null=True,default=1,db_column='SchClassID',blank=True,editable=False)
    WorkType=models.SmallIntegerField(_(u'工作类型'),default=0,editable=True,choices=WORKTYPE)
#    SchclassID=models.ForeignKey("SchClass",db_column='SchclassID',verbose_name=_('shift time-table'),null=False,default=-1,blank=True)
    def save(self):
        super(USER_TEMP_SCH,self).save()
        from mysite.att.models.__init__ import get_autocalculate_time as gct
        from model_waitforprocessdata import WaitForProcessData as wfpd
        import datetime
        gct_time=gct()
        if self.ComeTime<gct_time or self.LeaveTime<=gct_time:
            wtmp=wfpd()                
            st=self.ComeTime
            et=self.LeaveTime
            wtmp.UserID=self.UserID
            wtmp.starttime=st
            wtmp.endtime=et
            #wtmp.customer=self.customer
            try:
                wtmp.save()
            except:
                raise Exception(_(u'排班时间有重复'))
    
    def __unicode__(self):
            return u"%s %s"%(self.UserID.PIN,self.UserID.EName)
    
    def get_all_Sch_Name():
        datas = SchClass.objects.all()
        sch = []
        for row in datas:
            sch.append (row["SchName"])
        return sch

    class dataexport(Operation):
        help_text = _(u"数据导出") #导出
        verbose_name = _(u"临时排班导出")
        visible = False
        def action(self):
            pass
    class OpDeleteTempShift(Operation):
        help_text=_(u"""删除临时排班记录""")
        verbose_name=_(u"删除临时排班记录")
        def action(self):
           self.object.delete()
    
    class Admin(CachingModel.Admin):
        default_give_perms=["contenttypes.can_AttUserOfRun"]
        visible=False
        list_filter = ('UserID','SchclassID','LeaveTime','ComeTime','OverTime')
        list_display= ('UserID.PIN','UserID.EName','ComeTime','LeaveTime','WorkType','Flag')
        search_fields = ['UserID','SchclassID']
    class Meta:
        app_label='att'
        db_table = 'user_temp_sch'
        verbose_name=_(u'临时排班')
        verbose_name_plural=verbose_name
        unique_together = (("UserID","ComeTime", "LeaveTime"),)
