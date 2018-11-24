#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
import datetime
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.models import Department
from mysite.personnel.models.model_emp import Employee, EmpForeignKey,EmpPoPForeignKey
from base.operation import OperationBase, Operation, ModelOperation
from model_meeting import MeetingForeignKey

#from base.models import CachingModel

ATTSTATES=(
    (1,_(u"会议签到")),
    (2,_(u"会议签退")),

)


VERIFYS=(
#(3, _("Card")),
(0, _(u"密码")),
(1, _(u"指纹")),
(2, _(u"卡")),
(5, _(u"增加")),
(9, _(u"其他")),
(6, _(u"补签卡")),
)

class ValidRecord(models.Model,OperationBase):
        id = models.AutoField(db_column="id", primary_key=True)
        user = EmpForeignKey(verbose_name=_(u"人员"),db_column='userid')
        meetingID = MeetingForeignKey(verbose_name=_(u'会议'),blank=True)
        checkTime = models.DateTimeField(_(u'考勤时间'),null=False,blank=True)
        checkType = models.IntegerField(_(u'考勤状态'),default=1, choices=ATTSTATES)
        verifyType = models.IntegerField(_(u'验证方式'),default=0, choices=VERIFYS)

        def __unicode__(self):
            return '(%s-%s-%s)' %(self.user.EName,self.meetingID.nameMeeting,self.checkTime)
        
        def limit_validrecord_to(self, queryset, user):
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
                                        user_list = get_max_in(ValidRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid),depts,"user__DeptID__in")
                                     else:
                                        user_list = get_max_in(ValidRecord.objects.filter(meetingID__in = meetingid),depts,"user__DeptID__in")  
                                elif len(typeids)>0:
                                      typeid = typeids
                                      if typeid[0]!="":
                                         user_list = get_max_in(ValidRecord.objects.filter(checkType__in = typeid),depts,"user__DeptID__in") 
                                else:
                                    user_list = get_max_in(ValidRecord.objects.filter(),dept_id,"user__DeptID__in")              
                            elif typeids[0]!="":
                                 typeid = typeids
                                 user_list = get_max_in(ValidRecord.objects.filter(checkType__in = typeid),depts,"user__DeptID__in")
                            else:
                                user_list = get_max_in(ValidRecord.objects.all(),depts,"user__DeptID__in")
                        else:
                            user_list = get_max_in(ValidRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid),depts,"user__DeptID__in")   
#               
                    if dept_id[0]=="":
                        if len(meetingids)>0:
                           meetingid = meetingids
                           if meetingid[0]!="":
                               if len(typeids)>0: 
                                  typeid = typeids
                                  if typeid[0]!="":
                                       if users!=None:
                                          user_list = ValidRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                       else:
                                           user_list = ValidRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid)
                                  else:
                                    user_list = ValidRecord.objects.filter(meetingID__in = meetingid)                                          
                               if users!=None:
                                   if len(typeids)>0:
                                       typeid = typeids
                                       if typeid[0]!="":
                                          user_list = ValidRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)
                                       else:
                                           user_list = ValidRecord.objects.filter(meetingID__in = meetingid,user__in=list_user)                
                           else:
                               if len(typeids)>0 and users!=None: 
                                  typeid = typeids
                                  if typeid[0]!="":
                                     user_list = ValidRecord.objects.filter(checkType__in = typeid,user__in=list_user)
                                  else:
                                     user_list = ValidRecord.objects.filter(user__in=list_user)                                                    
                        else:
                         user_list = ValidRecord.objects.filter(meetingID__in = meetingid,checkType__in = typeid,user__in=list_user)                     
 
            return user_list
            
        
        def save(self):
            
            super(ValidRecord,self).save()
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
        class Meta:
                app_label='meeting'
#                unique_together = (("user", "checkTime"),)
                verbose_name = _(u"会议考勤明细")
                verbose_name_plural = verbose_name
                            
        class Admin:#会议有效记录，会议统计汇总以此为依据
                visible = False
                app_menu="meeting"
                menu_group = 'meeting'
                default_give_perms=["contenttypes.can_MeetingCalculate"]
                sort_fields=["meetingID.numberMeeting","user.DeptID","user.PIN","-checkTime"]
                list_filter = ('empMeeting','checkTime','checkType')
                list_display=('meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','user.DeptID','checkTime','checkType',)
                newadded_column={
                    "user.DeptID":"get_dept_name",             
                }
                