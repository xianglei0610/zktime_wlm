#! /usr/bin/env python
#coding=utf-8
from base.models import AppOperation
from django.db import models
from django.conf import settings
import datetime
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from mysite.meeting.models.meeting_emp import MeetingEmp,MeetingEmpForeignKey
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey
#from model_ycm import MeetingIDForeignKey,Meeting
from model_meeting import MeetingForeignKey,MeetingManyToToManyField          
from mysite.iclock.models.model_device import Device, DeviceForeignKey
from model_meeting import MeetingEntity

ATTSTATES=(
    (1,_(u"会议签到")),
    (2,_(u"会议签退")),

)
#ATTSTATES=(
#("I",_(u"上班签到")),
#("O",_(u"下班签退")),
#
#("8",_(u"就餐开始")),
#("9",_(u"就餐结束")),
##("i",_("Break in")),
##("o",_("Break out")),
##("0",_("Check in")),
##("1",_("Check out")),
#("2",_(u"外出")),
#("3",_(u"外出返回")),
#("4",_(u"加班签到")),
#("5",_(u"加班签退")),
#("255",_(u"未设置状态")),
##("160",_("Test Data")),
#)


VERIFYS=(
#(3, _("Card")),
(0, _(u"密码")),
(1, _(u"指纹")),
(2, _(u"卡")),
(5, _(u"增加")),
(9, _(u"其他")),
(6, _(u"补签卡")),
)


class OriginalRecord(CachingModel):
    id = models.AutoField(db_column="id", primary_key=True)
    user = EmpForeignKey(verbose_name=_(u"人员"),db_column='userid')
    meetingID = MeetingForeignKey(verbose_name=_(u'会议'),blank=True)
    checkTime = models.DateTimeField(_(u'考勤时间'),null=False,blank=True)
    checkType = models.CharField(_(u'考勤状态'),max_length=5,default='I', choices=ATTSTATES)
    verifyCode = models.IntegerField(_(u'验证方式'),default=0, choices=VERIFYS)
    sn = DeviceForeignKey(verbose_name=_(u'设备'), null=True, blank=True)
    sensorid = models.CharField(verbose_name=u'Sensor ID', null=True, blank=True, max_length=5, editable=False)
    workCode = models.CharField(_(u'工作号码'), max_length=20, null=True, blank=True)
    nameSN = models.CharField(_(u'序列号'),max_length=40, null=True, blank=True)
    reserved = models.CharField(_(u'保留字段一'), max_length=20, null=True, blank=True)
    
    
    def __unicode__(self):
        return '%s' %(self.pk)
    
    def limit_originalrecord_to(self, queryset, user):
         from base.middleware.threadlocals import get_current_request
         request=get_current_request()
         from mysite.iclock.iutils import get_dept_from_all,get_max_in
         deptids=request.GET.get('UserID__DeptID__in',"").split(',')
         meetingids=request.GET.get('meetingID__in',"").split(',')
         typeids = request.GET.get('checkType__in',"").split(',')
         users = request.GET.get('user__in',"")
         if users=="":
            users = None
         list_user = list(str(users).split(','))
         user_list = []
         if request:
             if len(deptids)>0:
                 dept_id = deptids
                 checked_child=request.GET.get('deptIDschecked_child',None)
                 if checked_child == "on" and dept_id:#包含部门下级
                     depts = get_dept_from_all(dept_id,request)  
                     if len(meetingids)>0:
                         meetingid = meetingids
                         if meetingid[0]!="":
                             if len(typeids)>0: 
                                  typeid = typeids
                                  if typeid[0]!="":   
                                     user_list = get_max_in(OriginalRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid),depts,"user__DeptID__in")
                                  else:
                                     user_list = get_max_in(OriginalRecord.objects.filter(meetingID__in = meetingid),depts,"user__DeptID__in")
                             elif len(typeids)>0:
                                   typeid = typeids
                                   if typeid[0]!="":
                                      user_list = get_max_in(OriginalRecord.objects.filter(checkType__in = typeid),depts,"user__DeptID__in") 
                             else:
                                 user_list = get_max_in(OriginalRecord.objects.filter(),dept_id,"user__DeptID__in")            
                         elif typeids[0]!="":
                              typeid = typeids                               
                              user_list = get_max_in(OriginalRecord.objects.filter(checkType__in = typeid),depts,"user__DeptID__in")
                         else:
                             user_list = get_max_in(OriginalRecord.objects.all(),depts,"user__DeptID__in")
                     else:
                         user_list = get_max_in(OriginalRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid),depts,"user__DeptID__in")   
             
                 if dept_id[0]=="":
                      if len(meetingids)>0:
                          meetingid = meetingids
                          if meetingid[0]!="":
                              if len(typeids)>0: 
                                 typeid = typeids
                                 if typeid[0]!="":
                                    if users!=None:
                                        user_list = OriginalRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                    else:
                                        user_list = OriginalRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid)                                      
                                 else:
                                    user_list = OriginalRecord.objects.filter(meetingID__in = meetingid)
                                 
                              if users!=None:
                                  if len(typeids)>0:
                                      typeid = typeids
                                      if typeid[0]!="":
                                         user_list = OriginalRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                      else:  
                                          user_list = OriginalRecord.objects.filter(meetingID__in = meetingid,user__in=list_user)
                          else:
                              if len(typeids)>0 and users!=None: 
                                 typeid = typeids
                                 if typeid[0]!="":
                                    user_list = OriginalRecord.objects.filter(checkType__in = typeid,user__in=list_user)
                                 else:
                                    user_list = OriginalRecord.objects.filter(user__in=list_user)                                                    
                      else:
                        user_list = OriginalRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)                     
                                                               
                                          
         return user_list
         
    
    def delete(self):
        super(OriginalRecord,self).delete()
        
    def save(self):
        super(OriginalRecord,self).save()             

    def _delete(ModelOperation):
        visible = False
        help_text = _(u'删除')
        verbose_name = _(u'删除')
        def action(self):
            pass
        
    class _change(Operation):
        visible = False
        help_text = _(u"修改选定记录")
        verbose_name = _(u"修改")
        def action(self):
            pass
    
    
    class _add(ModelOperation):
        visible = False
        help_text = _(u'新增')
        verbose_name = _(u'新增')
        def action(self):
            pass
        
    class getOriginalData(ModelOperation):
        visible=False
        help_text=_(u"获取会议原始记录")
        verbose_name=_(u"获取数据")
            
        params = (
            ('meetingIds',MeetingForeignKey(verbose_name=_(u'会议'))),
        )
        def action(self,meetingIds):
            from mysite.meeting.statistics import getPrimitiveMeetingData
#            print 'meetingIDS(Original):%s' % meetingIds
            try:
                getPrimitiveMeetingData(meetingIds)
            except:
                raise Exception(_(u"导入数据出错"))
            
    def get_dept_name(self):
        u'''从缓存中得到部门的Name'''
        from mysite.personnel.models import Department
        dept_name=""
        try:
            dept_obj=Department.objects.get(id=self.user.DeptID_id)
            dept_name=dept_obj.name
        except:
            pass
        return dept_name
    
    def get_device_name(self):
        u'''设备名称'''
        from mysite.iclock.models import Device
        if self.nameSN:
            dev=Device.objects.get(sn=self.nameSN)
            if dev:
                return dev.alias                
        else:
            return ""
    
    def get_checkType(self):
        u'''考勤状态'''
        if self.checkType=='I' or self.checkType=='1':
            self.checkType = '1'
            return u"会议签到"
        else:
            self.checkType = '2'
            return u"会议签退"

    class Admin(CachingModel.Admin):
        visible = False
#        read_only=True
        default_give_perms=["contenttypes.can_MeetingCalculate"]
        sort_fields=["meetingID.numberMeeting","user.DeptID","user.PIN","-checkTime"]
        app_menu="meeting"
        menu_group = 'meeting'
        list_filter = ('empMeeting','checkTime','checkType','sn')
        query_fields=['meetingID.numberMeeting','meetingID.nameMeeting','checkTime']

        list_display=('meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','user.DeptID','checkTime','get_checkType','get_device_name','nameSN')
        newadded_column={
            "user.DeptID":"get_dept_name",             
        }            
                        
        
        search_fields=('checkTime',)
        tstart_end_search={
            "checkTime":[_(u"起始考勤时间"),_(u"结束考勤时间")]
        }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
                        
        menu_index=6

    class Meta:
        app_label='meeting'
        unique_together = (("user", "checkTime"),)
        verbose_name = _(u"原始记录")
        verbose_name_plural = verbose_name
        
