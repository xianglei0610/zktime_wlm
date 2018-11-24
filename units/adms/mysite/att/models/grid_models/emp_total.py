# coding=utf-8
import datetime

from django.utils.translation import ugettext as _
from django.conf import settings

def GetHead(userids,d1,d2,reportType=0):
    from mysite.att.att_param import GetLeaveClasses
    from mysite.att.calculate.global_cache import C_ATT_RULE,C_LEAVE_CLASS
    C_ATT_RULE.action_init()
    C_LEAVE_CLASS.action_init()
    if reportType==0:
        dic = [('userid',u'用户ID'),('badgenumber',u'人员编号'),('username',u'姓名'),('deptid',u'部门名称'),('duty',u'应到'),('realduty',u'实到'),('late',u'迟到'),('early',u'早退'),('absent',u'旷工'),
            ('dutyinout',u'应签次数'),('clockin',u'应签到'),('clockout',u'应签退'),('noin',u'未签到'),('noout',u'未签退'),('worktime',u'出勤时长'),
            ('overtime',u'加班时间'),('SSpeDayNormalOT',u'平日加班'),('SSpeDayWeekendOT',u'休息日加班'),('SSpeDayHolidayOT',u'节假日加班'),
            ('Leave',u'请假')]
    elif reportType==1:
        dic = [('userid',u'用户ID'),('badgenumber',u'人员编号'),('username',u'姓名'),('deptid',u'部门名称'),]
        t=d1
        while t<=d2:
            f=str(t.day)
            dic.append((f,f))
            t=t+datetime.timedelta(1)
        dic =dic + [('duty',u'应到'),('realduty',u'实到'),('late',u'迟到'),('early',u'早退'),('absent',u'旷工'),
                                ('overtime',u'加班时间'), ('SSpeDayNormalOT',u'平日加班'),('SSpeDayWeekendOT',u'休息日加班'),('SSpeDayHolidayOT',u'节假日加班'),
                                ('Leave',_(u'请假'))]
    elif reportType==2:
        dic = [('userid',u'用户ID'),('badgenumber',u'人员编号'),('username',u'姓名'),('deptid',u'部门名称'),]
    LClasses1=GetLeaveClasses(1)
    for t in LClasses1:
        fName='Leave_'+str(t['LeaveId'])
        dic.append((fName,t['LeaveName']))
    return dic

def ForMakeData(hander,userids,d1,d2,reportType=0):
    '''考勤汇总表/每日考勤统计表'''
    from mysite.personnel.models import Employee
    from mysite.att.models import AttException,attShifts,EmpSpecDay
    from mysite.att.calculate.global_cache import C_ATT_RULE,C_LEAVE_CLASS
    from mysite.att.att_param import GetLeaveClasses,GetRptIndex
    from mysite.att.report_utils import NormalAttValue,SaveValue,formatdTime
    import mysite.att.report_sql as report_sql
    from mysite.att.models.modelproc import customSql
    from mysite.sql_utils import p_query
    C_ATT_RULE.action_init()
    C_LEAVE_CLASS.action_init()
    AbnomiteRptItems=GetLeaveClasses()
    AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
    
    auHour = 1
    aaBLeave = 1003

    ct = 0
    hander.grid.InitItems()
    useridstr = userids and ",".join(userids) or "-1"
    user_sql = """
        select u.userid,u.badgenumber,u.name,d.DeptID,d.DeptName,d.code from userinfo u    
            left join departments d on u.defaultdeptid = d.DeptID
            where u.userid in (%s)
    """%useridstr
    userinfo_res = p_query(user_sql)
    userinfo_dict = {}
    for u in userinfo_res:
        if not userinfo_dict.has_key(u[0]):
          userinfo_dict[u[0]]=u      
    for uid in userids:
        ct +=1
        rmdAttday = hander.grid.NewItem()
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
            rmdAttday['userid']=uid
            rmdAttday['deptid']=userinfo_dict[uid][4]
            rmdAttday['badgenumber']=userinfo_dict[uid][1]
            rmdAttday['username']=userinfo_dict[uid][2]
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
        hander.grid.AddItem(rmdAttday)
        
def ForMakeDataExcepSum(hander,userids,d1,d2):
    from mysite.personnel.models import Employee
    from mysite.att.models import AttException,attShifts
    from mysite.att.calculate.global_cache import C_ATT_RULE
    from mysite.att.att_param import GetLeaveClasses,GetRptIndex
    from mysite.att.report_utils import NormalAttValue,SaveValue
    C_ATT_RULE.action_init()
    AbnomiteRptItems=GetLeaveClasses()
    AttAbnomiteRptIndex=GetRptIndex(AbnomiteRptItems)
    auHour = 1
    aaBLeave = 1003
    hander.grid.InitItems()
    for uid in userids:
        rmdAttday = hander.grid.NewItem()
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
        rmdAttday['Leave'] = 0
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
                            rmdAttday['Leave']=SaveValue(rmdAttday['Leave'],v)
        except:
            import traceback;traceback.print_exc()
        hander.grid.AddItem(rmdAttday)