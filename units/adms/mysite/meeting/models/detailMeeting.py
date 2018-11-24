#! /usr/bin/env python
#coding=utf-8
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
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey
from model_meeting import MeetingEntity,MeetingForeignKey,MeetingManyToToManyField          
from mysite.iclock.models.model_device import Device, DeviceForeignKey



ATTSTATES=(
    (1,_(u"正常")),
    (2,_(u"缺席")),
    (3,_(u"请假")),
    (4,_(u"签退未签到")),
    (5,_(u"签到未签退")),
    (6,_(u"迟到")),
    (7,_(u"早退")),
    (8,_(u"迟到、早退")),
#    (9,_(u"迟到、未签到")),
    (10,_(u"迟到、未签退")),
  #  (11,_(u"早退")),
    (12,_(u"早退、未签到")),
 #   (13,_(u"早退、未签退")),

)



class DetailMeeting(CachingModel):
    id = models.AutoField(db_column="id", primary_key=True)
    user = EmpForeignKey(verbose_name=_(u"人员"),db_column='userid')
    meetingID = MeetingForeignKey(verbose_name=_(u'会议'))
    checkInTime = models.DateTimeField(verbose_name=_(u'会议签到'),null=True,blank=True)
    checkOutTime = models.DateTimeField(verbose_name=_(u'会议签退'),null=True,blank=True)
    checkType = models.IntegerField(verbose_name=_(u'考勤状态'),choices=ATTSTATES,null=True,blank=True)
    lateTime = models.IntegerField(verbose_name=_(u'迟到时长（分钟）'),null=True,blank=True)     
    leaveEarlyTime = models.IntegerField(verbose_name=_(u'早退时长（分钟）'),null=True,blank=True)    
    
    
    
    def __unicode__(self):
        return '%s %s' %(self.meetingID.nameMeeting,self.user.EName)
    
    def limit_detailmeeting_to(self, queryset, user):
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
                                    user_list = get_max_in(DetailMeeting.objects.filter(meetingID__in = meetingid,checkType__in = typeid),depts,"user__DeptID__in")
                                 else:
                                    user_list = get_max_in(DetailMeeting.objects.filter(meetingID__in = meetingid),depts,"user__DeptID__in")   
                            elif len(typeids)>0:
                                  typeid = typeids
                                  if typeid[0]!="":
                                     user_list = get_max_in(DetailMeeting.objects.filter(checkType__in = typeid),depts,"user__DeptID__in") 
                            else:
                                user_list = get_max_in(DetailMeeting.objects.filter(),dept_id,"user__DeptID__in")              
                        elif typeids[0]!="":
                             typeid = typeids 
                             user_list = get_max_in(DetailMeeting.objects.filter(checkType__in = typeid),depts,"user__DeptID__in")
                        else:
                            user_list = get_max_in(DetailMeeting.objects.all(),depts,"user__DeptID__in")
                    else:
                        user_list = get_max_in(DetailMeeting.objects.filter(meetingID__in = meetingid,checkType__in = typeid),depts,"user__DeptID__in")   
                
                if dept_id[0]=="":
                    if len(meetingids)>0:
                          meetingid = meetingids
                          if meetingid[0]!="":
                              if len(typeids)>0: 
                                 typeid = typeids
                                 if typeid[0]!="":
                                    if users!=None:
                                        user_list = DetailMeeting.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                    else:
                                        user_list = DetailMeeting.objects.filter(meetingID__in = meetingid,checkType__in = typeid)
                                 else:
                                    user_list = DetailMeeting.objects.filter(meetingID__in = meetingid)                                             
                              if users!=None:
                                  if len(typeids)>0:
                                      typeid = typeids
                                      if typeid[0]!="":
                                         user_list = DetailMeeting.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                      else:  
                                          user_list = DetailMeeting.objects.filter(meetingID__in = meetingid,user__in=list_user)       
                          else:
                              if len(typeids)>0 and users!=None: 
                                 typeid = typeids
                                 if typeid[0]!="":
                                    user_list = DetailMeeting.objects.filter(checkType__in = typeid,user__in=list_user)
                                 else:
                                    user_list = DetailMeeting.objects.filter(user__in=list_user)                                                    
                    else:
                        user_list = DetailMeeting.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                         
        return user_list
        

    class Admin(CachingModel.Admin):
        visible=False
        default_give_perms=["contenttypes.can_MeetingCalculate"]
        sort_fields=["meetingID.numberMeeting","user.PIN","-checkInTime","checkType"]
        list_display = ['meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','checkInTime',
                        'checkOutTime','checkType','lateTime','leaveEarlyTime',]
        app_menu="meeting"
        menu_group = 'meeting'
                   
        menu_index=6

    class Meta:
        app_label='meeting'
        verbose_name = _(u"会议统计详情")
        verbose_name_plural = verbose_name
        
