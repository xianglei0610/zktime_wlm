#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from django.template import  RequestContext 
from django.shortcuts import render_to_response
from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import permission_required
#from mysite.iclock.iutils import *
from django.conf import settings
#REBOOT_CHECKTIME, PAGE_LIMIT, ENABLED_MOD, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
import datetime
from django.core.paginator import Paginator
#from mysite.iclock.dataview import *
#from pyExcelerator import *
#from mysite.iclock.templatetags.iclock_tags import shortDate4, onlyTime,AbnormiteName,StateName,isYesNo,getSex,schName
import copy
from mysite.iclock.datasproc import *
from django.core.cache import cache
from mysite.iclock.models.model_trans import Transaction
from django.utils.simplejson  import dumps 
from mysite.settings import MEDIA_ROOT

VERIFYS1={
  3: _(u"刷卡"),
  0:_(u"密码"),
  1:_(u"指纹"),
  2:_(u"刷卡"),
  5:_(u"新增"),
  9:_(u"其他"),
}
#ATTSTATES={
#        "I":_("Check in"),
#        "O":_("Check out"),
#        "8":_("Meal start"),
#        "9":_("Meal end"),
#        "2":_("Break out"),
#        "3":_("Break in"),
#        "4":_("Overtime in"),
#        "5":_("Overtime out"),
#        }

def exportXLS(exp,Title,head,head_i18n,content):   #导出xls格式文件
        eee=datetime.datetime.now()
        wb = Workbook()
        ws = wb.add_sheet(exp)
        al = Alignment()
        al.horz = Alignment.HORZ_CENTER
        al.vert = Alignment.VERT_CENTER
        
        a2 = Alignment()
        a2.horz = Alignment.HORZ_LEFT
        a2.vert = Alignment.VERT_CENTER
        
        
        font0 = Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        
        font1 = Font()
        font1.name = 'Arial'
        font1.bold = True
        font1.height = 400
        
        pat1 = Pattern()
        pat1.pattern = Pattern.SOLID_PATTERN
        pat1.pattern_fore_colour = 0x22
        
        borders = Borders()
        borders.left = 0x11
        borders.right = 0x11
        borders.top = 0x11
        borders.bottom = 0x11
        
        borders1 = Borders()
        borders1.top = 0x11
        
        style = XFStyle()
        style.alignment = al
        style.borders = borders
        style.num_format_str = 'general'
        
        
        style0 = XFStyle()
        style0.font = font0
        style0.alignment = al
        style0.pattern = pat1
        style0.borders = borders
        style0.num_format_str = 'general'
        
        
        style1 = XFStyle()
        style1.alignment = al
        style1.font = font1
        style1.borders = borders
        style1.num_format_str = 'general'

        
        style2 = XFStyle()
        style2.alignment = al
        style2.borders = borders
        style2.num_format_str = 'general'
        
        style3 = XFStyle()
        style3.alignment = a2
        style3.borders = borders
        style3.num_format_str = 'general'
        
        
        tt=datetime.datetime.now()
        today = datetime.date.today() 
        
        
        ws.write_merge(0, 1, 0, len(head_i18n)-1, Title, style1)
        
        for i in range(0, len(head_i18n)):
                ws.write(2, i, head_i18n[i],style0)
        j=3
        for t in content:
                k=0
                for l in head:
                        if t[l] is None:
                                t[l]=''
                        if type(t[l])==type(today):
                                style.num_format_str = 'YY/MM/DD'
                        elif type(t[l])==type(tt):
                                style.num_format_str = 'YY/MM/DD hh:mm:ss'
                        else:
                                style.num_format_str = 'general'
                        ws.write(j, k, t[l], style)
                        k+=1
                j+=1        
#        if exp=='attDailyTotal':
#                sy=GetCalcSymbol()
#                ws.write_merge(j+3, j+3, 0, len(head_i18n)-1, sy, style3)
        wb.save("mysite/files/reports/%s.xls"%exp)
        
#        content=open("mysite/files/reports/%s.xls"%exp,'rb').read()
#        response=HttpResponse(mimetype="application/vnd.ms-excel")
#        response["Pragma"]="no-cache"
#        response["Cache-Control"]="no-store"
#        response['Content-Disposition'] = 'attachment; filename=%s.xls'%exp
        return HttpResponseRedirect("/iclock/file/reports/%s.xls"%exp)
#        response.write(content);
#        return getJSResponse("result=0")


LeaveClassD={}
def getLeaveClass(id): #获得例外情况名称
        global LeaveClassD
        if id==None or id=='':
                return None
        else:
                try:
                        if LeaveClassD=={}:
                                LeaveClassD = LeaveClass.objects.values('LeaveID','LeaveName')
                        for k in LeaveClassD:
                                if k['LeaveID']==id:
                                        LeaveNa=k['LeaveName']
                                        break
                        return         transLeaveName(LeaveNa)        
                except:
                        return ''
                        
        

def getList(list_C,obj):#组合成传给页面的数据
        kkk=datetime.datetime.now()
        #print 'getlistTime:',kkk
        li=[]
        for t in obj:
                d={}
                for k in list_C:
                        if k=='PIN':
                                try:
                                        d['PIN']=t.employee().PIN
                                except:
                                        d['PIN']=t.PIN
                        elif k=='EName':
                                try:
                                        d['EName']=t.employee().EName
                                except:
                                        d['EName']=t.EName
                        elif k=='DeptID':
                                try:
                                        d['DeptID']=t.employee().Dept().DeptName
                                except:
                                        d['DeptID']=t.objByID(t.DeptID).DeptName
                        elif k=='SchId':
                                d['SchId']=schName(t.SchId_id)
                        elif k in ['CheckType','CHECKTYPE']:
                                d[k]=t.__getattribute__(k) and transAttState(t.__getattribute__(k)) or ''
                        elif k=='NewType':
                                d['NewType']=t.NewType and transAttState(t.NewType) or ''
                        elif k=='AbNormiteID':
                                d['AbNormiteID']=AbnormiteName(t.AbNormiteID).title()
                        elif k=='Absent':
                                d['Absent']=isYesNo(t.Absent).title()
                        elif k=='MustIn':
                                d['MustIn']=isYesNo(t.MustIn).title()
                        elif k=='MustOut':
                                d['MustOut']=isYesNo(t.MustOut).title()
                        elif k=='AttDate':
                                d['AttDate']=shortDate4(t.AttDate)
                        elif k=='ExceptionID':
                                d['ExceptionID']=getLeaveClass(t.ExceptionID)
                        elif k=='SN':
                                try:
                                        d['SN']=getDevice(t.SN_id).Alias
                                except:
                                        d['SN']=''
                        elif k=='State':
                                d['State']=t.State and transAttState(t.State) or ''
                        elif k=='Verify':
                                try:
                                        d['Verify']=VERIFYS1[t.Verify]
                                except:
                                        d['Verify']=''
                        elif k in ['ClockInTime','ClockOutTime','StartTime','EndTime']:
                                d[k]=onlyTime(t.__getattribute__(k))
                        elif k=='Gender':
                                d[k]=getSex(t.Gender)
                        elif k in ['NoIn','NoOut']:
                                d[k]=isYesNo(t.__getattribute__(k)).title()
                        else:
                                d[k]=t.__getattribute__(k)
                                if isinstance(d[k],long):
                                        d[k]=int(d[k])
                li.append(d.copy())
        #print 'totallisttime:',datetime.datetime.now()-kkk
        return li
nameDic={"attRecAbnormite":_(u'恢复设备上的人员数据'),
                 "attShifts":_(u'班次详情'),
                "LateAndEarly":_(u'异常报表'),
                "AttException":_(u'例外情况'),
                "attTotal":_(u'重新计算报表'),
                "Transaction":_(u'原始记录'),
                "checkexact":_(u'无新记录'),
                "attDailyTotal":_(u'报表'),
                "employeeList":_(u'人员管理'),
                "attTotalLeave":_(u'重新计算报表'),
                "originalReport":_(u'报表'),
                }
def formatTime(l_st,l_et):#格式化时间
        l_st=datetime.datetime.strptime(l_st,'%Y-%m-%d')
        l_et=datetime.datetime.strptime(l_et,'%Y-%m-%d %H:%M:%S')
        return l_st,l_et
        
@permission_required("iclock.browse_itemdefine")
def exportReport(request):
        request.user.iclock_url_rel='../..'
        request.model = Transaction        
        l_user=request.POST.get('UserIDs',"")
        deptID=request.POST.get('deptIDs',"")
        l_st=request.POST['ComeTime']
        l_et=request.POST['EndTime']+" 23:59:59"
        exp=request.POST['tblName']
        sss=datetime.datetime.now()
        #print 'start time:',sss
        userlist=[]
        li=[]
        obj=None
        list_H=[]
        list_C=[]
        list_CA=[]
        dis=[]
        lookup_params={}

        if exp == 'attRecAbnormite':
                lookup_params={'checktime__gte':l_st,'checktime__lte':l_et}
        elif exp == 'Transaction':
                lookup_params={'TTime__gte':l_st,'TTime__lte':l_et}
        elif exp == 'checkexact':
                lookup_params={'CHECKTIME__gte':l_st,'CHECKTIME__lte':l_et}
#        elif exp == 'attpriReport':
#                lookup_params={'CHECKTIME__gte':l_st,'CHECKTIME__lte':l_et}
        else:
                lookup_params={'AttDate__gte':l_st,'AttDate__lte':l_et}
        
        if l_user=='null' or l_user=='':
                deptidlist=[int(i) for i in deptID.split(",")]
                deptids=[]
                for d in deptidlist:#支持选择多部门
                        deptids+=getAllAuthChildDept(d,request)
                lookup_params['UserID__DeptID__in']=deptids
                
        else:
                lookup_params['UserID__in']=[int(i) for i in l_user.split(',')]
        
        if exp=='attRecAbnormite':
                obj=attRecAbnormite.objects.all().filter(**lookup_params)
                list_H=[_(u'部门名称'),_(u'考勤号码'),_(u'人员姓名'),_(u'考勤时间'),_(u'验证方式'),_(u'考勤类型'),_(u'更正状态'),_(u'备注'),_(u'设备')]
                list_C=['DeptID','PIN','EName','checktime','Verify','CheckType','NewType','AbNormiteID','SN']
                orderStr=['UserID__DeptID__DeptID','UserID__PIN','checktime']
                obj=obj.order_by(*orderStr)
        elif exp =='LateAndEarly':
                obj=attShifts.objects.all().filter(**lookup_params)
                obj = obj.filter(Q(Late__gt=0)|Q(Early__gt=0)|Q(StartTime__isnull=True)|Q(EndTime__isnull=True)|Q(Absent__exact=1))
                obj = obj.exclude(ExceptionID__gt=0)
                orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
                obj=obj.order_by(*orderStr)
                list_H=[_(u'部门名称'),_(u'考勤号码'),_(u'人员姓名'),_(u'日期'),_(u'时段名称'),_(u'状态'),_(u'早退'),_(u'无'),_(u'结束签退时间'),_(u'旷工')]
                list_C=['DeptID','PIN','EName','AttDate','SchId','Late','Early','NoIn','NoOut','Absent']
        
        elif exp =='attShifts':
                l_st,l_et=formatTime(l_st,l_et)
                list_CA,list_H,r=ConstructAttshiftsFields1()
                re=CalcAttShiftsReportItem(request,deptID,l_user,l_st,l_et)
                obj=re['datas']
                list_CA.remove('userid')
                list_H.remove('UserID')
                
                dis=FetchDisabledFields(request.user,exp)
        elif exp == 'AttException':
                obj=AttException.objects.all().filter(**lookup_params)
                orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
                obj=obj.order_by(*orderStr)

                list_H=[_(u'部门名称'),_(u'考勤号码'),_(u'人员姓名'),_(u'日期'),_(u'开始时间'),_(u'结束时间'),_(u'异常'),_(u'总时长'),_(u'有效时长')]
                                
                list_C=['DeptID','PIN','EName','AttDate','StartTime','EndTime','ExceptionID','TimeLong','InScopeTime']
        elif exp=='attTotal':
                l_st,l_et=formatTime(l_st,l_et)
                re=CalcReportItem(request,deptID,l_user,l_st,l_et)
                obj=re['datas']        
                dis=FetchDisabledFields(request.user,exp)
                list_CA=re['fieldnames'][1:]
                list_H=re['fieldcaptions'][1:]
        elif exp=='attDailyTotal':
                l_st,l_et=formatTime(l_st,l_et)
                re=CalcReportItem(request,deptID,l_user,l_st,l_et,1)
                obj=re['datas']        
                dis=FetchDisabledFields(request.user,exp)
                
                list_H=re['fieldcaptions']
                list_CA=re['fieldnames']
        elif exp=='Transaction':
                obj=Transaction.objects.all().filter(**lookup_params)
                orderStr=['UserID__DeptID__DeptID','UserID__PIN','TTime']
                obj=obj.order_by(*orderStr)
                list_H=[_(u'部门名称'),_(u'考勤号码'),_(u'人员姓名'),_(u'考勤时间'),_(u'考勤状态'),_(u'验证方式'),
                                                        _(u'设备名称')]
                                                
                list_C=['DeptID','PIN','EName','TTime','State','Verify','SN']
        elif exp=='checkexact':        
                obj=checkexact.objects.all().filter(**lookup_params)
                orderStr=['UserID__DeptID__DeptID','UserID__PIN','CHECKTIME']
                obj=obj.order_by(*orderStr)
                list_H=[_(u'部门名称'),_(u'考勤号码'),_(u'人员姓名'),_(u'考勤时间'),_(u'考勤状态'),_(u'原因'),
                                                        _(u'修改'),_(u'员工考勤修改日志日期')]
                                                
                list_C=['DeptID','PIN','EName','CHECKTIME','CHECKTYPE','YUYIN','MODIFYBY','DATE']
        elif exp=='attTotalLeave':
                l_st,l_et=formatTime(l_st,l_et)
                re=CalcLeaveReportItem(request,deptID,l_user,l_st,l_et)
                obj=re['datas'] 
                list_H=re['fieldcaptions']
                list_C=re['fieldnames']
        elif exp=='originalReport': 
                obj=attpriReport.objects.filter(**lookup_params)
                list_H=[_(u'部门名称'),_(u'考勤号码'),_(u'人员姓名'),_(u'日期'),_(u'班次名称'),_(u'原始考勤'),_(u'考勤时间'),_(u'假类编号')]
                list_C=['DeptID','PIN','EName','AttDate','SchName','AttChkTime','AttAddChkTime','AttLeaveTime']
                orderStr=['UserID__DeptID__DeptID','UserID__PIN','AttDate']
                obj=obj.order_by(*orderStr)
                
        if exp in ['attShifts','attTotal','attDailyTotal',]:
                list_C=copy.copy(list_CA)        
                k=0
                ln=[]
                for f in list_CA:
                        if f in dis:
                                ln.append(k)
                                list_C.remove(f)
                        k=k+1
                t=0
                for n in ln:
                        num=n-t
                        list_H.pop(num)
                        t+=1
                
        len(obj)
        if exp in ['attTotal','attDailyTotal','attTotalLeave','attShifts']:
                for l in obj:
                        for k in l.keys():
                                if isinstance(l[k],long):
                                        l[k]=int(l[k])
                li=obj
        else:
                li=getList(list_C,obj)
        #print 'end time:',datetime.datetime.now()-sss
        Title=nameDic[exp]
        return exportXLS(exp,Title,list_C,list_H,li)


@permission_required("iclock.browse_itemdefine")
def exportaffairsReports(request):
        request.user.iclock_url_rel='../..'
        request.model = Transaction        
        l_user=request.GET.get('UserIDs',"")
        deptID=request.GET.get('deptIDs',"")
        exp=request.GET['tblName']
        userlist=[]
        li=[]
        obj=None
        list_H=[]
        list_C=[]
        list_CA=[]
        dis=[]
        lookup_params={}
        if l_user=='null' or l_user=='':
                deptidlist=[int(i) for i in deptID.split(",")]
                deptids=[]
                for d in deptidlist:#支持选择多部门
                        deptids+=getAllAuthChildDept(d,request)
                lookup_params['UserID__DeptID__in']=deptids
                
        else:
                lookup_params['UserID__in']=[int(i) for i in l_user.split(',')]
        if exp=='employeeList':
                try:
                        lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
                        del lookup_params['UserID__DeptID__in']
                except:
                        pass
                obj=employee.objects.filter(**lookup_params)
                list_H=[_(u'部门名称'),_(u'考勤编号'),_(u'人员姓名'),_(u'性别'),_(u'民族'),_(u'职务'),_(u'办公电话')]
                list_C=['DeptID','PIN','EName','Gender','National','Title','Tele']
                orderStr=["DeptID__DeptID","PIN"]
                obj=obj.order_by(*orderStr)
        elif exp == 'noFingerPrint':
                try:
                        lookup_params['DeptID__in']=lookup_params['UserID__DeptID__in']
                        del lookup_params['UserID__DeptID__in']
                except:
                        pass
#                obj=employee.objects.filter(DeptID__DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
                obj=employee.objects.filter(**lookup_params).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
                list_H=[_(u'部门名称'),_(u'考勤编号'),_(u'人员姓名'),_(u'性别'),_(u'民族'),_(u'职务'),_(u'办公电话')]
                list_C=['DeptID','PIN','EName','Gender','National','Title','Tele']
                orderStr=["DeptID__DeptID","PIN"]
                obj=obj.order_by(*orderStr)
        li=getList(list_C,obj)
        Title=nameDic[exp]
        return exportXLS(exp,Title,list_C,list_H,li)


#@permission_required("iclock.browse_itemdefine")
@permission_required("contenttypes.can_AttCalculate")
def reportindex(request):
        from mysite.urls import surl
        from dbapp.urls import dbapp_url
        from base import get_all_app_and_models
        
        from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
        from mysite.utils import GetFormField
        ''' 定义模型字段 '''
        m_field = EmpPoPMultForeignKey(verbose_name=_(u'选择人员'),blank=True,null=True)
        ''' 得到表单字段供前端使用 '''
        emp = GetFormField("emp",m_field)   #得到表单字段
        
        request.dbapp_url=dbapp_url
        apps=get_all_app_and_models()
        return render_to_response('calculateReport.html',
            RequestContext(request, {
                        'surl': surl,
                        'from': 1,
                        'page': 1,
                        'limit': 10,
                        'item_count': 4,
                        'page_count': 1,
                        'dbapp_url': dbapp_url,
                        'MEDIA_URL':MEDIA_ROOT,
                        "current_app":'att', 
                        'position':_(u'考勤->考勤报表'),
                        'apps':apps,
                        "help_model_name":"AttCalculate",
                        "myapp": [a for a in apps if a[0]=="att"][0][1],
                        'menu_focus':'AttCalculate',
                        'perm_export':True,
                        'empfield': emp,
                    }
            )
        )
