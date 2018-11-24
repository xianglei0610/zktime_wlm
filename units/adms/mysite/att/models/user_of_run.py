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
#from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey
from mysite.personnel.models.model_emp import EmpMultForeignKey,EmpPoPForeignKey
from num_run import NUM_RUN
from base.cached_model import CachingModel
from base.operation import Operation,ModelOperation
from user_temp_sch import   USER_TEMP_SCH as uts
from mysite.iclock.schedule import *
from mysite.personnel.models.empwidget import ZMulEmpChoiceWidget
from dbapp.datautils import  filterdata_by_user
def customSql(sql,action=True):
    from django.db import connection
    cursor = connection.cursor()
    
    cursor.execute(sql)
    if action:
        connection._commit()
    return cursor


    ##员工排班表##
class USER_OF_RUN(CachingModel):
    UserID=EmpPoPForeignKey(verbose_name=_(u"人员"), db_column='UserID')
    StartDate = models.DateField(_(u'开始日期'),null=False,default=datetime.datetime.now(), blank=True)
    EndDate = models.DateField(_(u'结束日期'),null=False,default='2099-12-31', blank=True)
    NUM_OF_RUN_ID=models.ForeignKey(NUM_RUN, verbose_name=_(u'班次'), db_column='NUM_OF_RUN_ID', null=False, blank=False)
    ISNOTOF_RUN=models.IntegerField(null=True,default=0,blank=True ,editable=False)
    ORDER_RUN=models.IntegerField(null=True,blank=True,editable=False)
#    def save(self):
#        self.EndDate=datetime.datetime(self.EndDate.year,self.EndDate.month,self.EndDate.day,23,59,59)
#        return models.Model.save(self)
    def get_all_Shift_Name(self):
        datas = NUM_RUN.objects.all()
        s = []
        for row in datas:
            s.append (row["Name"])
        return s
    def __unicode__(self):
            return u"%s"%self.UserID.EName
           #return u"%s(%s--%s)"%(self.UserID.PIN,self.StartDate.strftime("%Y-%m-%d"),self,EndDate.strftime("%Y-%m-%d"))
    
    class OpAddUserOfRun(ModelOperation):
        help_text=_(u"""新增员工排班""")
        verbose_name=_(u"新增排班")
        params=(
            ('UserID', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)), 
            ('StartDate',models.DateField(_(u'开始日期'),default=datetime.datetime.now().strftime("%Y-%m-01"))),
            ('EndDate',models.DateField(_(u'结束日期'),default=(datetime.datetime.now()+datetime.timedelta(days=31)).strftime("%Y-%m")+"-01")),
         )
        def action(self,UserID,StartDate,EndDate):
#            from mysite.personnel.models.model_emp import Employee
#            deptIDs=self.request.POST.getlist('deptIDs')
#            UserIDs=self.request.POST.getlist('UserID')
#            dept_all=self.request.POST.get('dept_all','')
#            if len(UserIDs)>0:
#                users=Employee.objects.filter(id__in=UserIDs)
#            else:
#                if dept_all:
#                   users=Employee.objects.filter(DeptID__in=deptIDs)
#                else:
#                    users=[]
            users=UserID
#            print users
            if not users:
                raise Exception(_(u'请选择人员'))
            if len(users)>1000:
                raise Exception(_(u'人员选择过多，最大支持1000人同时新增记录!'))
            sAssigned_shifts=self.request.POST.get('sAssigned_shifts','')
            #print "sAssigned_shifts:%s"%sAssigned_shifts
            if not sAssigned_shifts:
                raise Exception(_(u'请选择班次'))
            if StartDate>EndDate:
                raise Exception(_(u'结束日期不能小于开始日期!'))
            
            sAssigned_shifts=eval(sAssigned_shifts)
            print sAssigned_shifts[0]
            num_run=NUM_RUN.objects.get(pk=int(sAssigned_shifts[0]['SchId']))
            for u in  users:
                USER_OF_RUN.objects.filter(UserID=u,StartDate=StartDate,EndDate=EndDate,NUM_OF_RUN_ID=num_run).delete()
                t=USER_OF_RUN()
                t.UserID=u
                t.StartDate=StartDate
                t.EndDate=EndDate
                t.NUM_OF_RUN_ID=num_run
                t.save()
                from mysite.att.models.__init__ import get_autocalculate_time as gct
                from model_waitforprocessdata import WaitForProcessData as wfpd
                import datetime
                gct_time=gct()
                gct_date=datetime.date(gct_time.year,gct_time.month,gct_time.day)
                
                if StartDate<gct_date or EndDate<=gct_date:                    
                        wtmp=wfpd()                
                        st=datetime.datetime(StartDate.year,StartDate.month,StartDate.day,0,0,0)
                        et=datetime.datetime(EndDate.year,EndDate.month,EndDate.day,23,59,59)
                        wtmp.UserID=u
                        wtmp.starttime=st
                        wtmp.endtime=et
                        #wtmp.customer=self.customer
                        wtmp.save()
                
#            if self.request:                
#                FetchSchPlan(self.request)
    class OpAddTempShifts(ModelOperation):
         from mysite.att.models.user_temp_sch import USER_TEMP_SCH
         help_text=_(u"""新增员工临时排班""")
         verbose_name=_(u"新增临时排班")
         params=(
            ('UserID', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)), 
            ('StartDate',models.DateField(_(u'开始日期'),default=datetime.datetime.now().strftime("%Y-%m-%d"))),
            ('EndDate',models.DateField(_(u'结束日期'),default=(datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d"))),
            ('WorkType',USER_TEMP_SCH._meta.get_field('WorkType')),
         )
         def action(self,UserID,StartDate,EndDate,WorkType):
            from mysite.personnel.models.model_emp import Employee
            from mysite.att.models.schclass import SchClass
            from mysite.att.models.user_temp_sch import USER_TEMP_SCH
            import datetime
            from mysite.personnel.models import Department
            if self.request:
                
                #addTemparyShifts(self.request)
                st=self.request.POST.get('StartDate',"")
                et=self.request.POST.get('EndDate',"")
                start=st.replace("/","-")
                endt=et.replace("/","-")
                chklbSchClass=self.request.POST.getlist("sTimeTbl")
                chklbDates=self.request.POST.getlist("sDates")
                OverTime=self.request.POST.get('OverTime','')
                users=UserID

                flag=self.request.POST.get('Flag','1')    
                #print 'flag:%s'%flag
                is_OT=self.request.POST.get('is_OT','')
                is_OT=(str(is_OT)=='on')
                
#                #获取用户
#                if len(UserIDs)>0:
#                    users=Employee.objects.filter(id__in=UserIDs)
#                else:
#                    if dept_all:
#                       users=Employee.objects.filter(DeptID__in=deptIDs)
#                    else:
#                        users=[]
                    
                if not users:
                    raise Exception(_(u'请选择人员'))
                if len(users)>1000:
                    raise Exception(_(u'人员选择过多，最大支持1000人同时新增记录!'))
                if not chklbDates:
                    raise Exception(_(u'请选择日期'))
                if not chklbSchClass:
                    raise Exception(_(u'请选择时段'))
                #获取时间段
                schs=SchClass.objects.filter(pk__in=chklbSchClass)
#                for sch in schs:
#                    st=datetime.strptime(start+' '+ sch.StartTime.strftime('%H:%M:%S'),"%Y-%m-%d %H:%M:%S")
#                    et=datetime.strptime(endt+' '+ sch.EndTime.strftime('%H:%M:%S'),"%Y-%m-%d %H:%M:%S")
#                    
#                    for u in users:                   
#                        
#                        sql="delete from %s where UserID=%s and SchClassID=%s and ComeTime>='%s' and LeaveTime<='%s'"%( USER_TEMP_SCH._meta.db_table,
#                                                                      u.pk,sch.pk,st.strftime("%Y-%m-%d %H:%M:%S"),et.strftime("%Y-%m-%d %H:%M:%S"))
#                        print "sql:%s"%sql
#                        customSql(sql)
#                 
                #循环保存临时排班
                for day in chklbDates:
                    day=day.replace("/","-")
                    
                    for sch in schs:

                        #格式化时间
                        st=datetime.datetime.strptime(day+' '+sch.StartTime.strftime('%H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                        et=datetime.datetime.strptime(day+' '+sch.EndTime.strftime('%H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                        
                        if et<st:           #判断时间段是否跨天
                            et=et+datetime.timedelta(days=1)
                        
                        #清除已经排过的临时排班
                        #USER_TEMP_SCH.objects.filter(UserID__in=users,SchclassID__exact=sch.pk,ComeTime__exact=st,LeaveTime__exact=et).delete()
                        
                        #保存
                        for u in users:    
                            USER_TEMP_SCH.objects.filter(UserID__exact=u,SchclassID__exact=sch.pk,ComeTime__exact=st,LeaveTime__exact=et).delete()
                            t=USER_TEMP_SCH()
                            t.UserID=u
                            t.ComeTime=st
                            t.LeaveTime=et
                            t.WorkType=WorkType
                            t.Flag=flag
                            if is_OT:
                                t.OverTime=OverTime                            
                            t.SchclassID=sch.pk
                            t.save()
    class OpDeleteShift(Operation):
        help_text=_(u"""删除排班记录""")
        verbose_name=_(u"删除排班记录")
        def action(self):
           self.object.delete()                        
    class OpClearShift(ModelOperation):
        help_text=_(u"""清空排班记录""")
        verbose_name=_(u"清空排班记录")
        tips_text =  _(u"确认要清空所有排班记录")
        def action(self):
            filterdata_by_user(self.model.objects.all(),self.request.user).delete()
#            self.model.objects.all().delete()
    class OpClearEmpShift(ModelOperation):
        help_text=_(u"""清空临时排班记录""")
        verbose_name=_(u"清空临时排班记录")
        tips_text =  _(u"确认要清空所有临时排班记录")
        def action(self):
            from mysite.att.models.user_temp_sch import USER_TEMP_SCH
            filterdata_by_user(USER_TEMP_SCH.objects.all(),self.request.user).delete()
            
    class Admin(CachingModel.Admin):
        default_give_perms=["contenttypes.can_AttUserOfRun"]
        sort_fields=["UserID.PIN"]
        default_widgets={'UserID': ZMulEmpChoiceWidget}
        list_filter = ('UserID','NUM_OF_RUN_ID','StartDate','EndDate',)
        search_fields = ['UserID','NUM_OF_RUN_ID']
        api_fields= ['UserID.PIN','UserID.EName','NUM_OF_RUN_ID.Name','StartDate','EndDate']
        list_display= ['UserID_id','UserID.PIN','UserID.EName','NUM_OF_RUN_ID_id','NUM_OF_RUN_ID.Name','StartDate','EndDate','create_time']
        
        log=True
        visible=False
    class Meta:
        app_label='att'
        db_table = 'user_of_run'
        verbose_name = _(u'员工排班')
        verbose_name_plural=verbose_name
        unique_together = (("UserID","NUM_OF_RUN_ID", "StartDate","EndDate"),)
