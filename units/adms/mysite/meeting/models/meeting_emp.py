#! /usr/bin/env python
#coding=utf-8
from base.models import AppOperation
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from mysite.personnel.models.model_dept import DeptForeignKey
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey,format_pin
from model_meeting import MeetingEntity,MeetingForeignKey,MeetingManyToToManyField  
from  datetime   import datetime,date,time,timedelta
from detailMeeting import DetailMeeting

import datetime

      
IDENTITY=(
    (1, _(u'主讲')),
    (2, _(u'旁听')),          
    (3, _(u'成员')),
    (4, _(u'列席')),
    (5, _(u'书记官')),
)


class MeetingEmp(CachingModel):
    id = models.AutoField(db_column="id",primary_key=True,editable=False)
    meetingID = MeetingForeignKey(verbose_name=_(u'会议'),blank=True,null=True)
    user =  EmpForeignKey(verbose_name=_(u'人员'),db_column='userid',null=True,blank=True,editable=True) 
    PIN = models.CharField(verbose_name=_(u'人员编号'), db_column="badgenumber",blank=True,null=True, max_length=20,editable=False)
    EName = models.CharField(verbose_name=_(u'姓名'), db_column="name",null=True,blank=True,max_length=24,editable=False)
    empRank = models.IntegerField(verbose_name=_(u'出席身份'), max_length=20,choices=IDENTITY,default = 3,editable=False)
    
    def __unicode__(self):
        return u"%s %s" % (self.meetingID, self.EName)
    
    def save(self):
        from meeting_leave import Leave
        from meeting_exact import MeetingExact
        if self.user == None:
            raise Exception(_(u'请选择人员'))
        if self.id:
            me = MeetingEmp.objects.get(id=self.id)
            if me.meetingID != self.meetingID:
                raise Exception(_(u'会议不可更改'))
            if me.user != self.user:
                try:
                    lEmp = Leave.objects.get(employee=me.user,meetingID=me.meetingID)
                    lEmp.delete()
                except:
                    pass
                try:
                    mExact = MeetingExact.objects.get(user=me.user,meetingID=me.meetingID)
                    mExact.delete()
                except:
                    pass
            
            
        super(MeetingEmp,self).save()
        detailMeeting = DetailMeeting()
        detailMeeting.user = self.user
        detailMeeting.meetingID = self.meetingID
        detailMeeting.save()
        
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
    
    def delete(self):
        from meeting_exact import MeetingExact
        from meeting_leave import Leave
        try:
            mEx = MeetingExact.objects.get(meetingID=self.meetingID,user=self.user)
            mEx.delete()
        except:
            pass
        try:
            leave = Leave.objects.get(meetingID=self.meetingID,employee=self.user)
            leave.delete()
        except:
            pass
        try:
            detail = DetailMeeting.objects.get(meetingID=self.meetingID,user=self.user)
            detail.delete()
            sm = StatisticsMeeting.objects.get(meetingID=self.meetingID)
            sm.dueMeetingEmpCount = None   
            sm.arrivalMeetingEmpCount = None
            sm.nonArrivalMeetingEmpCount = None
            sm.vacateMeetingEmpCount = None
            sm.absentMeetingEmpCount = None
            sm.lateEmpCount = None
            sm.leaveEarlyEmpCount = None
            sm.unCheckInCount = None
            sm.unCheckOutCount = None
            sm.save()
        except:
            pass
        super(MeetingEmp,self).delete()
        
    class _add(ModelOperation):
        visible=False
        help_text=_(u"新增记录") #新增记录
        verbose_name=_(u"新增")
        def action(self):
            pass
    class _change(ModelOperation):
        visible=False
        def action(self):
            pass
    class OpAddMeetingEmp(ModelOperation):
        visible=True
        verbose_name=_(u"添加会议人员")
        help_text=_(u"新增会议人员")
        params=(
               ('meeting',MeetingForeignKey(verbose_name=_(u'会议'))),
               ('user', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True)),            
        )
        def action(self,user,meeting):
#            print "len(user)",len(user)
            if len(user)<1:
                raise Exception(_(u'请选择人员'))
            if self.request:
                ce=MeetingEmp.objects.filter(user__in=user,meetingID=meeting)
                if ce.count()>0:
                    raise Exception(_(u'%s %s 已经添加到该会议')%(ce[0].user.PIN,ce[0].user.EName))
                limit = meeting.roomMeeting.empLimit
                if len(user)>limit:
                    raise Exception(_(u'已超过会议室的最大容量(%s)') %limit)
                meetngE = MeetingEmp.objects.filter(meetingID=meeting)
                if len(meetngE)+len(user)>limit:
                    raise Exception(_(u'已超过会议室的最大容量(%s)') %limit)
                
                st = meeting.startTime
                et = meeting.endTime

                me_f = list(MeetingEntity.objects.filter(startTime__year=et.year,startTime__month=et.month,startTime__day=et.day,startTime__lt= et,endTime__gt= st))
                me_s = list(MeetingEntity.objects.filter(startTime__year=et.year,startTime__month=et.month,startTime__day=et.day,startTime__gt=st,endTime__lt= et))
                emp_have = MeetingEmp.objects.filter(meetingID__in = list(me_f+me_s))
                empHave = []

                for emp in emp_have:
                    e = Employee.objects.get(PIN__iexact=emp.PIN)
                    empHave.append(e.PIN)
                for emp in user:
                    e = Employee.objects.get(pk__iexact=emp.pk)
                    if e.PIN in empHave:
                        raise Exception(_(u"%s 在这个会议时间段已参加其他会议，无法参加此次会议") %emp)
                    ck=MeetingEmp()
                    ck.user=emp
                    ck.PIN=emp.PIN
                    ck.EName=emp.EName
                    ck.meetingID=meeting
                    ck.save()
                    
    class ImportMeetingEmp(ModelOperation):
            """
                导入的人员信息必须为人事中的人员信息
            """
            visible = True
            help_text=_(u"""1、批量导入会议人员，导入的会议人员信息应该为人事中的部分或全部人员信息<br/>
                            2、按确定后开始保存，出错后请按取消返回会议人员主界面进行查询导入结果""") 
            verbose_name=u"导入会议人员"
            params = (
                    ('meeting',MeetingForeignKey(verbose_name=_(u'会议'))),
                    ('upload_data', models.FileField(verbose_name=_(u'选择导入名单文件'),upload_to='file', blank=True, null=True)),
            )
            def action(self,meeting,upload_data):
                from django.conf import settings
                from django.core.files.storage import default_storage
                from django.db import connection
                import datetime
                import xlrd
                errorMsg = []#不存在人员信息列表
                existexistMsg = []#已存在人员信息列表
                filePath = settings.ADDITION_FILE_ROOT+'importMeetingEmpData.xls'
                if self.request.FILES:
                    f=self.request.FILES['upload_data']
#                    meeting = self.request.get("meeting",None)
                    f_format=str(f).split('.')
                    format_list=['xls']
                    try:
                       format_list.index(str(f_format[1]))
                    except:
                       raise Exception (_(u"文件格式无效，请选择 .xls文件！"))
                    if self.request.method == 'POST':
                        
                        destination = open(filePath, 'wb+')
                        for chunk in f.chunks():
                            destination.write(chunk)
                        destination.close()
                        try:
                           excel = xlrd.open_workbook(filePath)
                        except:
                           raise Exception (_(u"文件上传失败！"))
                       
                        sheet =excel.sheet_by_index(0)#第一个工作单元
#                        headLine = sheet.row_values(0)
                        if meeting == None:
                            raise Exception (_(u"请选择会议"))
                        isExistexistMeetingEntity = meeting
                        limit = meeting.roomMeeting.empLimit #改会议最多人数限
                        #查询出该会议已经存在的人员数
                        #select count(*)from meeting_MeetingEntity m join meeting_room r on m.roomMeeting_id = r.idjoin meeting_MeetingEmp me on m.id = me. meetingID_id where numberMeeting ='0321'
                        sql_count = u''' 
                        select count(*)from meeting_MeetingEntity m
                        join meeting_room r
                        on m.roomMeeting_id = r.id
                        join meeting_MeetingEmp me
                        on m.id = me. meetingID_id
                        where numberMeeting ='%s'
                        '''%(meeting.numberMeeting)
                        cursor = connection.cursor()
                        cursor.execute(sql_count)
                        ret_data=cursor.fetchall()
                        connection._commit()                   
                        number = int(ret_data[0][0]) #改会议已有的人员数
                        needImport = int(sheet.nrows)-1
                        if number:
                            if number+needImport >limit:
                                raise Exception(_(u'现已有人数(%s)导入人数(%s)超过会议室的最大容量(%s)') %(number,needImport,limit))
                                
                        if needImport > limit:
                            raise Exception(_(u'导入人数(%s)超过会议室的最大容量(%s)') %(needImport,limit))
                        #判断会议是否存在
                        sql = []
                        sqlDetail = []
                        SQLSERVER_INSERT = u'''INSERT INTO meeting_meetingemp(status,meetingID_id,userid,badgenumber,name,empRank) VALUES(0,'%(meetingId)s','%(user)s','%(pin)s','%(name)s',2)'''
                        SQLSERVER_INSERT_Detail = u'''INSERT INTO meeting_detailmeeting(status,meetingID_id,userid) VALUES(0,'%(meetingId)s','%(user)s')'''
                        for rowId in range(1,sheet.nrows,1):#从第5行开始读取数据
                            empPin = format_pin(int(sheet.row_values(rowId)[2]))
                            meetingName = sheet.row_values(rowId)[1]
                            meetingCode = sheet.row_values(rowId)[0]
                            empName = sheet.row_values(rowId)[3]
                            meetingE = MeetingEntity.objects.get(numberMeeting=meetingCode)
                            #判断人员是否存在MeetingEmp
                            #isExistexistEmp = list(Employee.objects.filter(PIN=empPin,EName = empName))
                            isExistexistEmp = list(MeetingEmp.objects.filter(PIN=empPin,meetingID = meetingE.id))
                            if len(isExistexistEmp) != 0:
                                errorMsg.append((empPin,empName))
#                                raise Exception (_(u"请检查 %s %s 人员信息是否存在") % (empPin,empName))
                            #meetingEmp = MeetingEmp(meetingID=isExistexistMeetingEntity[0],user=isExistexistEmp[0],PIN=empPin,EName=empName)
                            else:
#                                print 'isHave-----------------------------'
#                                isHave = MeetingEmp.objects.filter(meetingID=isExistexistMeetingEntity,user=isExistexistEmp[0])
#                                if len(isHave) >0:
#                                    print 'len(isHave)=======',len(isHave)
#                                    existexistMsg.append((empPin,empName))
#                                else:
                                    e = Employee.objects.get(PIN=empPin)
                                    sql.append(SQLSERVER_INSERT%{
                                            "meetingId":isExistexistMeetingEntity.id,
                                            "user":e.id,
                                            "pin":empPin,
                                            "name":empName,
                                            })
                                    sqlDetail.append(SQLSERVER_INSERT_Detail%{
                                        "meetingId":isExistexistMeetingEntity.id,
                                        "user":e.id,
                                    })
       
                        cursor = connection.cursor()
                        
                            
                        for record in sql:
                            try:
                                cursor.execute(record)
                            except Exception,e:
                                raise Exception(_(u"保存到数据库出错，请检查数据合法性") )
                        for detailSQL in sqlDetail:
                            try:
                                cursor.execute(detailSQL)
                            except Exception,e:
                                raise Exception(_(u"出错") )
                        connection._commit()
                        
                        f.close()
                        errorMsgCount = len(errorMsg)
#                        exiCount = len(existexistMsg)
#                        print '=-=========',errorMsgCount,exiCount
                        if errorMsgCount > 0 :
                            msg1 = ""
                            msg2 = ""
                            for i in range(errorMsgCount):
				#msg1 += _(u"(%s,%s)" %(errorMsg[i][0],errorMsg[i][1]))
				#msg1 += "("+str(errorMsg[i][0])+","+str(errorMsg[i][1])+"),"
                                msg1 += "("+errorMsg[i][0]+","+errorMsg[i][1]+"),"
                                if i % 5 == 0:
                                    msg1 += "<br/>"
#                            for i in range(exiCount):
#				#msg2 += _(u"(%s,%s)" %(existexistMsg[i][0],existexistMsg[i][1]))
#                                print 'existexistMsg[i][0]-----',existexistMsg[i][0],existexistMsg[i][1] 
#                                msg2 += "("+existexistMsg[i][0]+","+existexistMsg[i][1]+"),"
#                                if i % 5 == 0:
#                                    msg2 += "<br/>"
                            #raise Exception(_(u"请检查[%s]人员信息是否存在 ,<br/>其中[%s]数据已经存在，其余(%s条)数据已成功保存") % (msg1,msg1,(needImport-errorMsgCount)))
                            raise Exception(_(u"人员[%s]数据已经存在该会议中，<br/>其余(%s条)数据已成功保存") % (msg1,(needImport-errorMsgCount)))
                            
    def limit_meetingID_to(self, queryset):
#	print 'meetingID limit.......1111............',queryset
	queryset = queryset.filter(endTime__gt = datetime.datetime.now())
#	print 'meetingID limit...................',queryset
        return  queryset.order_by('startTime')   


    class Admin(CachingModel.Admin):   
        menu_index=4 
        query_fields=['meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','user.DeptID']                
        list_display = ['meetingID.numberMeeting','meetingID.nameMeeting','user.PIN','user.EName','user.DeptID']
        sort_fields=['-meetingID.numberMeeting','user.DeptID','user.PIN']
        newadded_column = {
            'user.DeptID':'get_dept_name',
        }
        menu_group = 'meeting'
        
    class Meta:
        verbose_name=_(u'会议人员')
        verbose_name_plural=verbose_name
        app_label=  'meeting' 
        
        
        
    
class MeetingEmpForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
        super(MeetingEmpForeignKey, self).__init__(MeetingEmp, to_field=to_field, **kwargs)
        
class Emp_MeetingMultFK(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(Emp_MeetingMultFK, self).__init__(Employee, *args, **kwargs)
    
class MeetingEmpMultForeignKey(models.ManyToManyField):
        def __init__(self, *args, **kwargs):
                super(MeetingEmpMultForeignKey, self).__init__(MeetingEmp, *args, **kwargs)

def update_dept_widgets():
    from dbapp import widgets
    if MeetingEmpForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
        from meeting_empwidget import ZEmpChoiceWidget, ZMulEmpChoiceWidget, ZMulPopEmpChoiceWidget, ZPopEmpChoiceWidget
        widgets.WIDGET_FOR_DBFIELD_DEFAULTS[Emp_MeetingMultFK] = ZMulEmpChoiceWidget
        widgets.WIDGET_FOR_DBFIELD_DEFAULTS[MeetingEmpForeignKey] = ZEmpChoiceWidget
        widgets.WIDGET_FOR_DBFIELD_DEFAULTS[MeetingEmpMultForeignKey] = ZMulEmpChoiceWidget
        
        

update_dept_widgets()
        
def GetMeetingEmp(meetingid):
    mm=MeetingEmp.objects.filter(meetingid=meetingid)
    
    return mm

