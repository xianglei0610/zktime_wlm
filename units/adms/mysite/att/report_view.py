# coding=utf-8
'''
考勤计算报表集合
'''

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps 
from mysite.personnel.models import Employee
from mysite.iclock.models import Transaction
from mysite.iclock.models.model_trans import ATTSTATES

import datetime
from django.db.models import connection as conn

from django.db import models
from dbapp.utils import save_tmp_file

from mysite.att.models.modelproc import customSql
from report_utils import AttCalculateBase, parse_report_arg, formatdTime,get_ExceptionID
import report_sql

@login_required
def attRecAbnormite_report(request):
    '''
    统计结果详情表
    '''
    userids,deptids,d1,d2,offset = parse_report_arg(request)
    dic =(('pin',_(u'人员编号')),('name',_(u'姓名')),('checktime',_(u'考勤时间')),('CheckType',_(u'考勤状态')), ('NewType',_(u'更正状态')))
    calculate = AttCalculateBase(dic)
    sql = report_sql.get_tjjgxq_report_sql(','.join(userids),d1,d2)
    ret_data=[]
    try:
        cur=conn.cursor()            
        cur.execute(sql)
        ret_data=cur.fetchall()
        conn._commit()
    except:
        import traceback;traceback.print_exc()
    ATTSTATES=(("I",u"上班签到"),("O",u"下班签退"),("0", u"上班签到"),("1", u"下班签退"),("8",u"就餐开始"),("9",u"就餐结束"),("2",u"外出"),("3",u"外出返回"),("4",u"加班签到"),("5",u"加班签退"),("255",u"未设置状态"))
    m_dic = {}
    m_dic.update(ATTSTATES)
    for d in ret_data:
        try:
            r = calculate.NewItem()
            r["pin"]=d[0]
            r["name"]=d[1]
            r["checktime"]=d[2].strftime('%Y-%m-%d %H:%M:%S')
            if not d[3]:
                d = list(d)
                d[3] = "I"
                d = tuple(d)
            r["CheckType"]=m_dic[str(d[3])]
            r["NewType"]=m_dic[str(d[4])]
            calculate.AddItem(r)
        except:
            import traceback
            traceback.print_exc()
    return getJSResponse(smart_str(dumps(calculate.ResultDic(offset))))
    

@login_required
def attShifts_report(request):
    '''
    考勤明细表
    '''
    userids,deptids,d1,d2,offset = parse_report_arg(request)
    dic =(('code',_(u'部门编号')),('DeptName',_(u'部门名称')),('badgenumber',_(u'人员编号')),('name',_(u'姓名')),('AttDate',_(u'日期')),('SchName',_(u'时段名称')), ('ClockInTime',_(u'上班时间')),('ClockOutTime',_(u'下班时间')),('StartTime',_(u'签到时间')),('EndTime',_(u'签退时间')),('WorkDay',_(u'应到')),('RealWorkDay',_(u'实到')),('MustIn',_(u'应签到')),('MustOut',_(u'应签退')),('NoIn',_(u'未签到')),('NoOut',_(u'未签退')),('Late',_(u'迟到')),('Early',_(u'早退')),('AbsentR',_(u'旷工')),('WorkTime',_(u'出勤时长')),('Exception',_(u'例外情况')),('OverTime_des',_(u'加班时间')),('AttTime',_(u'时段时间')),('SSpeDayNormalOT',_(u'平日加班')),('SSpeDayWeekendOT',_(u'休息日加班')),('SSpeDayHolidayOT',_(u'节假日加班')))
    calculate = AttCalculateBase(dic)
    sql = report_sql.attShifts_report_sql(','.join(userids),d1,d2)
    ret_data=[]
    try:
        cur=conn.cursor()            
        cur.execute(sql)
        ret_data=cur.fetchall()
        conn._commit()
    except:
        import traceback;traceback.print_exc()
    for d in ret_data:
        r = calculate.NewItem()
        r["code"]=d[0]; r["DeptName"]=d[1]; r["badgenumber"]=d[2];  r["name"]=d[3]; r["AttDate"]=d[4].strftime("%Y-%m-%d"); r["SchName"]=d[5]
        r["ClockInTime"]=d[6] and d[6].strftime('%H:%M') or '';    r["ClockOutTime"]=d[7] and d[7].strftime('%H:%M') or ''
        r["StartTime"]=d[8] and d[8].strftime('%H:%M') or '';   r["EndTime"]=d[9] and d[9].strftime('%H:%M') or ''
        r["WorkDay"]=d[10]; r["RealWorkDay"]=d[11]; r["MustIn"]=d[12]; r["MustOut"]=d[13]; r["NoIn"]=d[14]; r["NoOut"]=d[15]
        r["Late"]=d[16];r["Early"]=d[17]; r["AbsentR"]=d[18]; r["WorkTime"]=d[19]
        r["Exception"]=get_ExceptionID(d[20],d[30],d[4])
        r["OverTime_des"]=d[21]#r["WorkMins"]=d[22]; r["SSpeDayNormal"]=d[23]; r["SSpeDayWeekend"]=d[24]; r["SSpeDayHoliday"]=d[25]
        r["AttTime"]=d[26]; r["SSpeDayNormalOT"]=d[27]; r["SSpeDayWeekendOT"]=d[28]; r["SSpeDayHolidayOT"]=d[29]
        calculate.AddItem(r)
    return getJSResponse(smart_str(dumps(calculate.ResultDic(offset))))


@login_required
def le_reprot(request):
    '''
    汇总最早与最晚
    '''
    ids,deptids,d1,d2,offset = parse_report_arg(request,True)
    dic =(('userid',_(u'用户ID')),('badgenumber',_(u'人员编号')),('username',_(u'姓名')),('deptid',_(u'部门编号')),('deptname',_(u'部门名称')),('date',_(u'日期')),('firstchecktime',_(u'最早打卡时间')),('latechecktime',_(u'最晚打卡时间')))
    calculate = AttCalculateBase(dic)
    for e in ids:
        userid =int (e)
        emp_pin = Employee.all_objects.filter(pk=userid)
        if emp_pin:
            emp_pin = emp_pin[0]
        else:
            continue
        check = Transaction.objects.filter(UserID=userid,TTime__range=(d1,d2)).values_list("UserID__PIN","UserID__EName","UserID__DeptID__code","UserID__DeptID__name","TTime").order_by("TTime")
        pos=0
        day_current = d1
        while day_current<=d2:
            r = calculate.NewItem()
            cur=day_current.date()        
            some_day=[]
            first=True
            while pos<len(check) and check[pos][4].date()==cur:
                if first:   
                    some_day.append(check[pos][4])#当天第一条
                    first=False
                pos+=1
            if not first and some_day[len(some_day)-1]!=check[pos-1][4]:
                some_day.append(check[pos-1][4])#当天最晚一条
            r["userid"] = emp_pin.id
            r["badgenumber"]=emp_pin.PIN
            r["username"]=emp_pin.EName
            r["deptid"]=emp_pin.DeptID.code
            r["deptname"]=emp_pin.DeptID.name
            r["date"] = u"%s"%cur
            if some_day:
                if len(some_day)==1:
                    r["firstchecktime"]=str(some_day[0])
                    r["latechecktime"]=""
                if len(check)>=2:
                    r["firstchecktime"]=str(some_day[0])
                    r["latechecktime"]=str(some_day[-1])
            else:
                r["firstchecktime"]=""
                r["latechecktime"]=""
            calculate.AddItem(r)
            day_current = day_current + datetime.timedelta(days=1)
    return getJSResponse(smart_str(dumps(calculate.ResultDic(offset))))

@login_required
def yc_report(request):
    '''
    考勤异常明细表
    '''
    userids,deptids,d1,d2,offset = parse_report_arg(request)
    dic =(('userid',_(u'用户ID')),('super_dept',_(u'上级部门')),('deptname',_(u'部门名称')),('badgenumber',_(u'人员编号')),('username',_(u'姓名')),('date',_(u'日期')),\
    ('late',_(u'迟到分钟')),('early',_(u'早退分钟')),('absent',_(u'旷工时间')),('late_times',_(u'迟到次数')),('early_times',_(u'早退次数')),('absent_times',_(u'旷工次数')),('worktime',_(u'上班时间')),('card_times',_(u'打卡时间')))
    calculate = AttCalculateBase(dic)
    sql = report_sql.get_yc_report_sql(','.join(userids),','.join(deptids),d1,d2)
    ret_data=[]
    try:
        cur=conn.cursor()            
        cur.execute(sql)
        ret_data=cur.fetchall()
        conn._commit()
    except:
        import traceback;traceback.print_exc()
    for d in ret_data:
        r = calculate.NewItem()
        r["userid"]=d[1]
        r["super_dept"]=d[2] or " "
        r["deptname"]=d[3] or " "
        r["badgenumber"]=d[4]
        r["username"]=d[5] or " "
        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
            r["date"]=d[6].strftime("%Y-%m-%d")
        else:
            r["date"]=d[6]
        r["late"]=d[7] or " "
        r["early"]=d[8] or " "
        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
            r["absent"]=str(d[9]) or " "
        else:
            r["absent"]=d[9]
        r["late_times"]=d[10] or " "
        r["early_times"]=d[11] or " "
        r["absent_times"]=d[12] or " "
        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":            
            r["worktime"]=str(d[13])
        else:
            r["worktime"]=d[13]
        r["card_times"]=d[14] or " "
        calculate.AddItem(r)
    return getJSResponse(smart_str(dumps(calculate.ResultDic(offset))))

@login_required
def cardtimes_report(request):
    '''
    打卡详情表
    '''
    userids,deptids,d1,d2,offset = parse_report_arg(request)
    dic = (('userid',_(u'用户ID')),('super_dept',_(u'上级部门')),('deptname',_(u'部门名称')),('badgenumber',_(u'人员编号')),('username',_(u'姓名')),('date',_(u'日期')),('times',_(u'打卡次数')),('card_times',_(u'打卡时间')))
    calculate = AttCalculateBase(dic)
    sql = report_sql.get_cardtimes_report_sql(','.join(userids),','.join(deptids),d1,d2)
    ret_data=[]
    try:
        cur=conn.cursor()            
        cur.execute(sql)
        ret_data=cur.fetchall()
        conn._commit()
    except:
        import traceback;traceback.print_exc()
    for d in ret_data:
        r = calculate.NewItem()
        r["userid"]=d[1]
        r["super_dept"]=d[2] or " "
        r["deptname"]=d[3] or " "
        r["badgenumber"]=d[4]
        r["username"]=d[5] or " "
        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql" :
            r["date"]=d[6].strftime("%Y-%m-%d")
        else:
            r["date"]=d[6]
        r["times"]=d[7]
        r["card_times"]=d[8] or " "
        calculate.AddItem(r)
    return getJSResponse(smart_str(dumps(calculate.ResultDic(offset))))


@login_required
def calcLeaveReport(request):
    '''
    请假汇总表
    '''
    from mysite.att.models import AttException,attShifts
    if settings.ATT_CALCULATE_NEW:
        from mysite.att.calculate.global_cache import C_ATT_RULE
        from mysite.att.att_param import GetLeaveClasses,GetRptIndex
        from mysite.att.report_utils import NormalAttValue,SaveValue
        C_ATT_RULE.action_init()
    else:
        from mysite.iclock.datas import GetLeaveClasses,GetRptIndex,NormalAttValue,SaveValue
    AbnomiteRptItems=GetLeaveClasses()
    AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
    userids,deptids,d1,d2,offset = parse_report_arg(request,True)
    auHour = 1
    aaBLeave = 1003
    dic = [('userid',_(u'用户ID')),('badgenumber',_(u'人员编号')),('username',_(u'姓名')),('deptid',_(u'部门名称')),('Leave',_(u'请假'))]
    LClasses1=GetLeaveClasses(1)
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        dic.append((fName,t['LeaveName']))
    calculate = AttCalculateBase(dic)
    for uid in userids:
        rmdAttday = calculate.NewItem()
        uid=int(uid)
        try:
            emp=Employee.objByID(uid)
        except: 
            continue
        attExcept=AttException.objects.filter(UserID=uid,AttDate__gte=d1,AttDate__lte=d2)
        if not len(attExcept)>0:
            continue
        rmdAttday['userid']=uid
        rmdAttday['deptid']=emp.DeptID.name
        rmdAttday['badgenumber']=emp.PIN
        rmdAttday['username']=emp.EName
        try:        
            for ex in attExcept:             
                    exceptid=ex.ExceptionID
                    if settings.ATT_CALCULATE_NEW:
                        from mysite.att.models import EmpSpecDay
                        ask_obj = EmpSpecDay.objects.get(pk=ex.ExceptionID)
                        exceptid = ask_obj.leaveclass.pk
                    InScopeTime=ex.InScopeTime
                    wd=attShifts.objects.filter(AttDate__exact=ex.AttDate,UserID=ex.UserID)
                    wdmins=0
                    for w in wd:
                        wdmins=wdmins+w.AttTime
                    if exceptid in [-4, -3, -2, -1]:
                        continue
                    elif exceptid>0:
                        AbnomiteRptItem = AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]           
                        v=NormalAttValue(InScopeTime,AbnomiteRptItem['MinUnit'],AbnomiteRptItem['Unit'] ,AbnomiteRptItem['RemaindProc'],auHour,wdmins)
                        rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],v)
                        
                        if AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]['IsLeave']==1:    #只有计为请假时才累计
                            aaBLeave_RptItem = AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]
                            v=NormalAttValue(InScopeTime,aaBLeave_RptItem['MinUnit'],aaBLeave_RptItem['Unit'] ,aaBLeave_RptItem['RemaindProc'],auHour,wdmins)
                            #print 'hhhhhhhhhhhhh',v,InScopeTime,ex.ExceptionID
                            rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
        except:
            import traceback;traceback.print_exc()
        calculate.AddItem(rmdAttday)
    return getJSResponse(smart_str(dumps(calculate.ResultDic(offset))))


def mainReport(request,reportType=0):
    '''考勤汇总表/每日考勤统计表'''
    from mysite.att.models import AttException,attShifts,EmpSpecDay
    if settings.ATT_CALCULATE_NEW:
        from mysite.att.calculate.global_cache import C_ATT_RULE
        from mysite.att.att_param import GetLeaveClasses,GetRptIndex
        from mysite.att.report_utils import NormalAttValue,SaveValue
        C_ATT_RULE.action_init()
    else:
        from mysite.iclock.datas import GetLeaveClasses,GetRptIndex,NormalAttValue,SaveValue
    from mysite.iclock.datasproc import FetchDisabledFields
    AbnomiteRptItems=GetLeaveClasses()
    AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
    
    userids,deptids,d1,d2,offset = parse_report_arg(request,True)
    auHour = 1
    aaBLeave = 1003
    if reportType==0:
        dic = [('userid',_(u'用户ID')),('badgenumber',_(u'人员编号')),('username',_(u'姓名')),('deptid',_(u'部门名称')),('duty',_(u'应到')),('realduty',_(u'实到')),('late',_(u'迟到')),('early',_(u'早退')),('absent',_(u'旷工')),
            ('dutyinout',_(u'应签次数')),('clockin',_(u'应签到')),('clockout',_(u'应签退')),('noin',_(u'未签到')),('noout',_(u'未签退')),('worktime',_(u'出勤时长')),
            ('overtime',_(u'加班时间')),('SSpeDayNormalOT',_(u'平日加班')),('SSpeDayWeekendOT',_(u'休息日加班')),('SSpeDayHolidayOT',_(u'节假日加班')),
            ('Leave',_(u'请假'))]
    elif reportType==1:
        dic = [('userid',_(u'用户ID')),('badgenumber',_(u'人员编号')),('username',_(u'姓名')),('deptid',_(u'部门名称')),]
        t=d1
        while t<=d2:
            f=str(t.day)
            dic.append((f,f))
            t=t+datetime.timedelta(1)
        dic =dic + [('duty',_(u'应到')),('realduty',_(u'实到')),('late',_(u'迟到')),('early',_(u'早退')),('absent',_(u'旷工')),
                                ('overtime',_(u'加班时间')), ('SSpeDayNormalOT',_(u'平日加班')),('SSpeDayWeekendOT',_(u'休息日加班')),('SSpeDayHolidayOT',_(u'节假日加班')),
                                ('Leave',_(u'请假'))]
    LClasses1=GetLeaveClasses(1)
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        dic.append((fName,t['LeaveName']))

    calculate = AttCalculateBase(dic)
    ct = 0
    for uid in userids:
        ct +=1
        rmdAttday = calculate.NewItem()
        uid=int(uid)
        sql = report_sql.get_calc_report_sql(uid,d1,d2)
        cs=customSql(sql,False)
        desc=cs.description
        fldNames={}
        i=0
        for c in desc:
            fldNames[c[0].lower()]=i
            i=i+1
        rows=cs.fetchall()
        if not len(rows)>0:
            try:
                emp=Employee.objByID(uid)
            except: 
                continue
            rmdAttday['userid']=uid
            rmdAttday['deptid']=emp.DeptID.name
            rmdAttday['badgenumber']=emp.PIN
            rmdAttday['username']=emp.EName
        try: 
            ##################################### 常规计算结果汇总统计 ################################       
            for t in rows: 
                    if not rmdAttday['userid']:
                        rmdAttday['userid']=t[fldNames['userid']]
                        rmdAttday['deptid']=t[fldNames['deptname']]
                        rmdAttday['badgenumber']=t[fldNames['pin']]
                        rmdAttday['username']=t[fldNames['name']]
                    ################# 应到、实到、迟到、早退、旷工 ###################
                    rmdAttday['duty']=SaveValue(rmdAttday['duty'],t[fldNames['workday']])
                    rmdAttday['realduty']=SaveValue(rmdAttday['realduty'],t[fldNames['realworkday']])
                    rmdAttday['late']=SaveValue(rmdAttday['late'],t[fldNames['late']])
                    rmdAttday['early']=SaveValue(rmdAttday['early'],t[fldNames['early']])
                    if t[fldNames['absent']]>0:
                        try:
                            rmdAttday['absent']=SaveValue(rmdAttday['absent'],t[fldNames['absent']])
                        except:
                            import traceback;traceback.print_exc()
                    ######################### 加班时间计算 #########################
                    rmdAttday['overtime']=SaveValue(rmdAttday['overtime'],t[fldNames['overtime']])
                    rmdAttday['SSpeDayNormalOT']=SaveValue(rmdAttday['SSpeDayNormalOT'],t[fldNames['sspedaynormalot']])
                    rmdAttday['SSpeDayWeekendOT']=SaveValue(rmdAttday['SSpeDayWeekendOT'],t[fldNames['sspedayweekendot']])
                    rmdAttday['SSpeDayHolidayOT']=SaveValue(rmdAttday['SSpeDayHolidayOT'],t[fldNames['sspedayholidayot']])
                    ################# 应签次数、应签到、应签退、未签到、未签退、出勤时长、工作时间 ####################
                    if reportType==0:
                        if t[fldNames['mustin']]:
                            rmdAttday['dutyinout']=int(float(SaveValue(rmdAttday['dutyinout'],1)))
                            rmdAttday['clockin']=int(float(SaveValue(rmdAttday['clockin'],1)))
                        if t[fldNames['mustout']]:
                            rmdAttday['dutyinout']=int(float(SaveValue(rmdAttday['dutyinout'],1)))
                            rmdAttday['clockout']=int(float(SaveValue(rmdAttday['clockout'],1)))
                        if t[fldNames['mustin']] and t[fldNames['starttime']] is None:
                            rmdAttday['noin']=int(float(SaveValue(rmdAttday['noin'],1)))
                        if t[fldNames['mustout']] and t[fldNames['endtime']] is None:
                            rmdAttday['noout']=int(float(SaveValue(rmdAttday['noout'],1)))
                        rmdAttday['worktime']=SaveValue(rmdAttday['worktime'],t[fldNames['worktime']])
                        #rmdAttday['workmins']=SaveValue(rmdAttday['workmins'],t[fldNames['workmins']])
                    ######################### 每日考勤情况 #########################    
                    if reportType==1:
                        dt=t[fldNames['attdate']]
                        dof=str(dt.day)
                        tt=t[fldNames['symbol']]
                        if tt:
                            rmdAttday[dof]=rmdAttday[dof]+tt
            ##################################### 异常计算结果汇总统计 ################################                                     
            if len(rows)>0 and (reportType==0 or reportType==1):
                attExcept=AttException.objects.filter(UserID=uid,AttDate__gte=d1,AttDate__lte=d2)    
                for ex in attExcept: 
                    if ex.UserID_id!=rmdAttday['userid']:
                        continue
                    exceptid=EmpSpecDay.objects.get(pk=ex.ExceptionID).leaveclass.pk#ex.ExceptionID
                    wd=attShifts.objects.filter(AttDate__exact=ex.AttDate,UserID=ex.UserID)
                    wdmins=0    #当天时段分钟数之和                
                    for w in wd:
                        wdmins=wdmins+w.AttTime                
                    if exceptid in [-4, -3, -2, -1]:
                        pass
                    elif exceptid>0:
                        if exceptid in AttAbnomiteRptIndex:
                            if (reportType==0) or (reportType==1):
                                AbnomiteRptItem = AbnomiteRptItems[AttAbnomiteRptIndex[exceptid]]
                                if AbnomiteRptItem['RemaindCount']==0:
                                    v=NormalAttValue(ex.InScopeTime,AbnomiteRptItem['MinUnit'],AbnomiteRptItem['Unit'] ,AbnomiteRptItem['RemaindProc'],auHour,wdmins)
                                else:
                                    v=ex.InScopeTime
                                    v=NormalAttValue(ex.InScopeTime,AbnomiteRptItem['MinUnit'],AbnomiteRptItem['Unit'] ,AbnomiteRptItem['RemaindProc'],auHour,wdmins)
                                rmdAttday['Leave_'+str(exceptid)]=SaveValue(rmdAttday['Leave_'+str(exceptid)],v)
                                if AbnomiteRptItem['IsLeave']==1:   #请假汇总
                                    aaBLeave_RptItem = AbnomiteRptItems[AttAbnomiteRptIndex[aaBLeave]]
                                    v=NormalAttValue(ex.InScopeTime,aaBLeave_RptItem['MinUnit'],aaBLeave_RptItem['Unit'] ,aaBLeave_RptItem['RemaindProc'],auHour,wdmins)
                                    rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
                ################## 计算结果的后处理 ################
                if reportType==0:
                    rmdAttday['worktime']=formatdTime(rmdAttday['worktime'])
                    #rmdAttday['workmins']=formatdTime(rmdAttday['workmins'])
                for ttt in rmdAttday.keys():              
                    if type(rmdAttday[ttt])==type(1.0):
                        if rmdAttday[ttt]>int(rmdAttday[ttt]):
                            rmdAttday[ttt]=smart_str(rmdAttday[ttt])
        except:
            import traceback;traceback.print_exc()
        calculate.AddItem(rmdAttday)
    ################## 返回字典的属性补充 ###################
    Result = calculate.ResultDic(offset)
    if reportType==0:
        Result['disableCols']=FetchDisabledFields(request.user,'attTotal')
    elif reportType==1:
        Result['disableCols']=FetchDisabledFields(request.user,'attDailyTotal')
    return getJSResponse(smart_str(dumps(Result)))

@login_required
def calcReport(request):
    '''
    考勤汇总表
    '''
    return mainReport(request,0)

@login_required
def dailycalcReport(request):
    '''
    每日考勤统计表
    '''
    return mainReport(request,1)