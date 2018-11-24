# Create your views here.
#coding=utf-8
from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from mysite.iclock.datas import *
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from mysite.att.models.nomodelview  import forget,saveCheckForget,submitAttParam,attrule,shift_detail,worktimezone,assignedShifts#,dailycalcReport,calcReport,calcLeaveReport
from django.utils.simplejson  import dumps 
from mysite.iclock.schedule import deleteShiftTime,deleteAllShiftTime,addShiftTimeTable,deleteEmployeeShift,FetchSchPlan,ConvertTemparyShifts
from mysite.att.models import *
from mysite.att.reports import reportindex
from dbapp.modelutils import GetModel
from mysite.settings import MEDIA_ROOT
from django.db.models import Q
from dbapp.datalist import save_datalist
from dbapp.datautils import *
from report_view import le_reprot, yc_report, cardtimes_report,calcLeaveReport,calcReport,dailycalcReport
from dbapp.dataviewdb import  model_data_list
from mysite.iclock.iutils import get_max_in,get_dept_from_all
from mysite.att.models.user_temp_sch import USER_TEMP_SCH
from mysite.att.models.user_of_run import USER_OF_RUN

def funGetShifts(request):
        nrun = NUM_RUN.objects.all().order_by('Num_runID')
        len(nrun)
        re = []
        ss = {}
        for t in nrun:
                ss['shift_id'] = t.Num_runID
                ss['shift_name'] = t.Name
                t = ss.copy()
                re.append(t)
        return getJSResponse(smart_str(dumps(re)))

def funTmpShifts(request):
        return ConvertTemparyShifts(request)

def funFetchSchPlan(request):
        return FetchSchPlan(request)
        
def funAssignedShifts(request):
        return assignedShifts(request)

def funDeleteEmployeeShift(request):
        return deleteEmployeeShift(request)

def funWorkTimeZone(request):
        return worktimezone(request)

def funAttrule(request):
        return attrule(request)
def funShift_detail(request):
        return shift_detail(request)
def funDeleteShiftTime(request):
        return deleteShiftTime(request)
def funDeleteAllShiftTime(request):
        return deleteAllShiftTime(request)
def funAddShiftTimeTable(request):
        return addShiftTimeTable(request)
def fundailycalcReport(request):
        return dailycalcReport(request)
    
def funCalcReport(request):
        return calcReport(request)
    
def funCalcLeaveReport(request):
        return calcLeaveReport(request)

def GenerateEmpPunchCard(request):
     from mysite.iclock.models.model_trans import Transaction
     import datetime
     cudt = datetime.datetime.now().strftime("%Y-%m-%d")
     
     d1=request.POST.get("starttime",cudt) + " 00:00:00"
     d2=request.POST.get("endtime",cudt) +" 23:59:59"
    
     empids = request.POST.get("empids")
     deptids =request.POST.get("deptids")
     sql ="""
     select a.badgenumber,a.name,b.checktime 
     from userinfo a inner join checkinout b on a.userid = b.userid 
     where b.checktime>='%s' and b.checktime<='%s' 
     """%(d1,d2)
     if empids:
        sql=sql+" and a.userid in (%s) "%(empids)
     if deptids and not empids:
            sql =sql + " and a.defaultdeptid in (%s) "%(deptids)
     sql = sql + " order by a.badgenumber,b.checktime "
     dts=[]

     d1_dt = datetime.datetime.strptime(request.POST.get("starttime",cudt),"%Y-%m-%d")
     d2_dt = datetime.datetime.strptime(request.POST.get("endtime",cudt),"%Y-%m-%d")
     diffdays = (d2_dt-d1_dt).days
     
     i =0
     while i<=diffdays:
         dts.append(d1_dt+datetime.timedelta(days=i))
         i+=1
     readybaseEmp=[]
     if empids:
        requiredAtt =Employee.objects.filter(isatt='1',id__in=empids).order_by("PIN").values_list("PIN","EName")
     elif deptids:
        requiredAtt =Employee.objects.filter(isatt='1',DeptID__in=deptids).order_by("PIN").values_list("PIN","EName")
     else:
        requiredAtt =Employee.objects.filter(isatt='1').order_by("PIN").values_list("PIN","EName")
     if not requiredAtt.count():
         tmp_name=save_datalist({"data":[],"fields":fields,"heads":header})
         return getJSResponse([[]])
     else:
         for i in requiredAtt:
              for dt_temp in dts:
                 l = list(i)
                 l.append(dt_temp.strftime("%Y-%m-%d"))
                 readybaseEmp.append(l)
     
     cs = connection.cursor()
     cs.execute(sql)
     data = cs.fetchall()
     datas=[]
     for row in data:
        datas.append(list(row))

     for item in datas:
         if item[2]:
             item.append(item[2].strftime("%Y-%m-%d"))
             item.append(item[2].strftime("%H:%M"))
             item.remove(item[2])
     
     i=0
     ii=len(datas)
     
     for emp in readybaseEmp:
         cc=  filter(lambda x:x[0]==emp[0] and x[2]==emp[2],datas)
         punchcarddetail = ",".join( [i[3] for i in cc])
         emp.append(punchcarddetail)
    
     fields=['badgenumber','name','checkdate','time']
     header0=[{'badgenumber':_(u'人员编号')},{'name':_(u'姓名')},{'checkdate':_(u'打卡日期')},{'time':_(u'打卡时间')}]
     header={'badgenumber':u'%s'%_(u'人员编号'),'name':u'%s'%_(u'姓名'),'checkdate':u'%s'%_(u'打卡日期'),'time':u'%s'%_(u'打卡时间')}
     headers= "["+",".join([u"'%s'"%i.values()[0] for i in header0])+"]"
    
     r={}
     datatotmp=[]
     for row in readybaseEmp:
          datatotmp.append({'badgenumber':row[0],'name':row[1],'checkdate':row[2],'time':row[3]})
     tmp_name=save_datalist({"data":datatotmp,"fields":fields,"heads":header})
    
     if len(readybaseEmp)==0:readybaseEmp.append([])
     try:
           offset = int(request.REQUEST.get(PAGE_VAR, 1))
     except:
           offset=1
     limit= int(request.REQUEST.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
     mnp=request.REQUEST.get(MAX_NO_PAGE, 0)
     if len(data)<=int(mnp):
        limit=int(mnp)
    
     paginator = Paginator(readybaseEmp, limit)
     item_count = paginator.count
     if offset>paginator.num_pages: offset=paginator.num_pages
     if offset<1: offset=1
     pgList = paginator.page(offset)
     cc={}
     cc["page_count"]=paginator.num_pages
     cc["record_count"]=item_count
     cc["page_number"]=offset
     cc["heads"] =headers
     cc["data"] =pgList.object_list
     cc["fields"]= fields
     cc["tmp_name"]=tmp_name
     return GenerateEmpPunchCardJsonData(request,cc)

def GenerateEmpPunchCardJsonData(request,data):
     temp="""{tmp_name:{% autoescape off %}"{{tmp_name}}"{% endautoescape %},heads:{% autoescape off %}{{heads}}{% endautoescape %},fields:{% autoescape off %}{{fields}}{% endautoescape %},page_count:{{page_count}},record_count:{{record_count}},page_number:{{page_number}},data:[{% for i in data %}\
             [""" +"\"{{i.0}}\"," + "\"{{i.1}}\"," +"\"{{i.2}}\","+"\"{{i.3}}\"]" \
             """{%if not forloop.last%},{%endif%}{% endfor %}]}"""
     cc = Context(data)
     d = Template(temp).render(RequestContext(request,cc))
     return getJSResponse(d)

@login_required
def funGetSchclass(request):
        schclasses = GetSchClasses()
        re = []
        ss = {}
        for t in schclasses:
                #print t
                ss['SchclassID'] = t['schClassID']
                ss['SchName'] = t['SchName']
                ss['StartTime'] = t['TimeZone']['StartTime'].time().strftime('%H:%M')
                ss['EndTime'] = t['TimeZone']['EndTime'].time().strftime('%H:%M')
                t = ss.copy()
                re.append(t)
                #print re
        return getJSResponse(smart_str(dumps(re)))
        
def funAttCalculate(request):
        return reportindex(request)
def funAttReCalculate(request):
    try:
        #from mysite.att.models.nomodelview  import reCaluateAction
        from mysite.iclock.attcalc import reCaluateAction
        
        if settings.ATT_CALCULATE_NEW:
            from mysite.att import calculate
            return calculate.main(request)
        else:
            return reCaluateAction(request)
    except:
        import traceback;traceback.print_exc()
def funAttParamSetting_o(request):
        InitData()
        la = LoadAttRule(True)# 0607  考勤参数 界面刷新 显示问题
        lc = LoadCalcItems()
        qs = la.copy()
        qs['LeaveClass'] = lc
        #print lc
        return getJSResponse(smart_str(dumps(qs)))

def funAttParamSetting_n(request):
        from mysite.att.att_param import LoadAttRule
        qs = LoadAttRule()
        return getJSResponse(smart_str(dumps(qs)))
    
def funAttParamSetting(request):
    if settings.ATT_CALCULATE_NEW:
        return funAttParamSetting_n(request)
    else:
        return funAttParamSetting_o(request)
        
def SaveAttParamSetting(request):
        '''
        考勤参数设置
        '''
        if settings.ATT_CALCULATE_NEW:
            from mysite.att.att_param import submitAttParam
        else:
            from mysite.att.models.nomodelview  import submitAttParam 
        return submitAttParam(request)

def funForget(request):
        return forget(request)
        
def SaveForget(request):
    return saveCheckForget(request)
@permission_required("contenttypes.can_AttUserOfRun")
def funAttUerOfRun(request):
        from dbapp.urls import dbapp_url
        from base import get_all_app_and_models
        from mysite.att.models import USER_OF_RUN
        request.dbapp_url=dbapp_url
        apps=get_all_app_and_models()
        export=False
        export_name=USER_OF_RUN._meta.app_label+".browse_"+USER_OF_RUN.__name__.lower()
        from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
        from mysite.utils import GetFormField
        ''' 定义模型字段 '''
        m_field = EmpPoPMultForeignKey(verbose_name=_(u'选择人员'),blank=True,null=True)
        ''' 得到表单字段供前端使用 '''
        emp = GetFormField("emp",m_field)   #得到表单字段
        
        return render_to_response('att_USER_OF_RUN.html',
                RequestContext(request,{
                        'dbapp_url': dbapp_url,
                        'MEDIA_URL':MEDIA_ROOT,
                        'position':_(u'考勤->排班'),
                        "current_app":'att', 
                        'apps':apps,
                        "help_model_name":"attUserOfrun",
        				"myapp": [a for a in apps if a[0]=="att"][0][1],
                        'menu_focus':'AttUserOfRun',
                        'export_perm':export_name,
                        'empfield': emp,
                        })
                
                )
        
def funGetModelData(request,app_lable,model_name):
        from mysite.personnel.views import funGetModelData as fungetdata
        return fungetdata(request,app_lable,model_name)
    

@login_required
def funAttDeviceUserManage(request):
        from dbapp.urls import dbapp_url
        from base import get_all_app_and_models
        from mysite.personnel.models.model_area import Area
        request.dbapp_url =dbapp_url
        apps=get_all_app_and_models()
        if hasattr(Area,"get_all_operation_js"):
            actions=Area.get_all_operation_js(request.user)
        return render_to_response('att_DeviceUSERManage.html',
                RequestContext(request,{
                        'dbapp_url': dbapp_url,
                        'MEDIA_URL':MEDIA_ROOT,
                        "current_app":'att', 
                        'apps':apps,
                        "help_model_name":"DeviceUserManage",
        				"myapp": [a for a in apps if a[0]=="att"][0][1],
                        'specific_actions':actions,
                        'menu_focus':'AttDeviceUserManage',
                        'position':_(u'考勤->区域用户'),
                        })
                
                )


@login_required
def funAttDeviceDataManage(request):
       from dbapp.urls import dbapp_url
       from base import get_all_app_and_models
#       from mysite.personnel.models.model_area import Area
       request.dbapp_url =dbapp_url
       apps=get_all_app_and_models()
#       if hasattr(Area,"get_all_operation_js"):
#           actions=Area.get_all_operation_js(request.user)
       return render_to_response('att_DeviceDataManage.html',
               RequestContext(request,{
                       'dbapp_url': dbapp_url,
                       'MEDIA_URL':MEDIA_ROOT,
                       "current_app":'att', 
                       'apps':apps,
                       "help_model_name":"DeviceDataManage",
        			   "myapp": [a for a in apps if a[0]=="att"][0][1],
                       'app_label':'iclock',
                       'model_name':'Device',
                       'menu_focus':'AttDeviceDataManage',
                       'position':_(u'考勤->考勤设备'),
                       })
               
               )
def funGetAllExcept(request):
    from mysite.att.models import LeaveClass,LeaveClass1
    from mysite.att.models.model_leaveclass1    import LEAVE_UNITS
    ret={}
    ret['data']=[]
    l=LeaveClass.objects.all()
    for i in l:
        tmp=[]
        tmp.append(u"%s"%_(i.LeaveName))
        tmp.append(i.ReportSymbol)
        if i.Unit>=4 :
            tmp.append("")
        else:
            tmp.append(u"%s"%_(LEAVE_UNITS[i.Unit-1][1]))
        ret['data'].append(tmp)
    l=LeaveClass1.objects.all()
    for i in l:
        tmp=[]
        tmp.append(u"%s"%_(i.name))
        tmp.append(i.ReportSymbol)
        if i.Unit>=4 or i.pk in [1009,1008]:
            tmp.append("")
        else:        
            tmp.append(u"%s"%_(LEAVE_UNITS[i.Unit-1][1]))
        ret['data'].append(tmp)
    return getJSResponse(smart_str(dumps(ret)))

def funGetAllExcept_fast(request):
    from mysite.att.models import LeaveClass
    from mysite.att.models.model_leaveclass1 import LEAVE_UNITS
    from mysite.att.att_param import LoadAttRule
    qs = LoadAttRule()
    ret={}
    ret['data']=[]
    l=LeaveClass.objects.all()
    for i in l:
        tmp=[]
        tmp.append(u"%s"%_(i.LeaveName))
        tmp.append(i.ReportSymbol)
        if i.Unit>=4 :
            tmp.append("")
        else:
            tmp.append(u"%s"%_(LEAVE_UNITS[i.Unit-1][1]))
        ret['data'].append(tmp)
    l=qs['LeaveClass']
    for i in l:
        tmp=[]
        tmp.append(u"%s"%_(i['LeaveName']))
        tmp.append(i['ReportSymbol'])
        if i['Unit']>=4 or i['LeaveId'] in [1009,1008]:
            tmp.append("")
        else:        
            tmp.append(u"%s"%_(LEAVE_UNITS[i['Unit']-1][1]))
        ret['data'].append(tmp)
    return getJSResponse(smart_str(dumps(ret)))


def funLEReport(request):
    '''统计每天第一次打卡与最后一次打卡'''
    return le_reprot(request)

def funYCReport(request):
    return yc_report(request)

def funCardTimesReport(request):
    return cardtimes_report(request)
    
def funAttGuide(request):
   from dbapp.urls import dbapp_url
   from base import get_all_app_and_models
   request.dbapp_url =dbapp_url
   apps=get_all_app_and_models()
   return render_to_response('att_guide.html',
           RequestContext(request,{
                   'dbapp_url': dbapp_url,
                   'MEDIA_URL':MEDIA_ROOT,
                   "current_app":'att', 
                   'apps':apps,
                   "help_model_name":"AttGuide",
                   "myapp": [a for a in apps if a[0]=="att"][0][1],
                   'app_label':'att',
                   'model_name':'AttGuide',
                   'menu_focus':'AttGuide',
                   'position':_(u'考勤->导航'),
                   })
           
           )

def select_all_emp_data(request,model_name):
    model = {
        "USER_TEMP_SCH":USER_TEMP_SCH,
        "USER_OF_RUN":USER_OF_RUN,
        }
    try:
        ignore_keys = []
        Cls = model[model_name]
        qs = Cls.objects.all()
        dept_emp_all = request.REQUEST.get("dept_emp_all",None)
        if dept_emp_all=='true':
            dept_childrens = request.REQUEST.get("dept_childrens",None)
            if dept_childrens=='true':
                depts = request.REQUEST.get("UserID__DeptID__in",None)
                if depts:
                    depts = depts.split(",")
                    depts = get_dept_from_all(depts,request)
                    qs = get_max_in(qs,depts,"UserID__DeptID__in")
                    ignore_keys.extend(["UserID__DeptID__in","UserID__in"])
        else:
            ignore_keys.append("UserID__DeptID__in")
        return model_data_list(request, Cls,qs,ignore_keys=ignore_keys)
    except:
        import traceback
        traceback.print_exc()
        
def funImportSelfData(request):
    from import_data import import_self_data_action
    return import_self_data_action (request)
def funImportUdata(request):
    from import_data import import_u_data_action
    return import_u_data_action(request)