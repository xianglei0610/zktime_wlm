# -*- coding: utf-8 -*-
import datetime
from mysite.att.models import attShifts,AttException,attRecAbnormite

from utils import deal_param,intdata,Decimal
from django.db import IntegrityError

def parse_leave(data_in,data_out):
    '''
    例外数据截取
    [[(412:43200)], [], [] ] ,    [[(412:43200)], [], []] 
    '''
    askleave = (data_in[0],data_out[0])
    setleave = (data_in[1],data_out[1])
    holiday =  (data_in[2],data_out[2])
    return askleave, setleave, holiday

def leave_analyse(data,schclass_seconds,emp,set_in,set_out,save=False,today=None,schclass_long=None):
    '''
    例外数据计算和保存 (例外包括请假、调休、节假)
    ( [(id,schclass_long, long), ] ,[(id,schclass_long, long), ] )
    '''
    data_in = data[0]
    data_out = data[1]
    if len(data_in)!=len(data_out):
        print u'error on leave count is not equal'
        return 0,[]
    try:
        _len = len(data_in)
        sum = 0
        ret_pk = []
        for i in range(_len):
            _in = data_in[i]
            _out = data_out[i]
            if _in[0]!=_out[0]:
                print 'error on leave id is not equal'
                return 0,[]
            _mid = 0
            if _in[2]<schclass_seconds:
                if _out[2]<schclass_seconds:
                    _mid = (_in[2]+_out[2] - schclass_seconds)
                else:
                    _mid = _in[2]
            else:
                if _out[2]<schclass_seconds:
                    _mid = _out[2]
                else:
                    _mid = schclass_seconds
            if _mid>schclass_long:
                _mid = schclass_long
            if save and _mid>0:
                att_exp = AttException()
                att_exp.UserID_id =emp
                att_exp.InScopeTime =  _mid
                att_exp.ExceptionID = _in[0]
                att_exp.AttDate = today
                att_exp.StartTime = set_in
                att_exp.EndTime = set_out
                att_exp.OverlapWorkDayTail = 0
                att_exp.save()
                ret_pk.append(str(att_exp.pk))
            else:
                ret_pk.append(str(_in[0]))
            sum = sum + _mid
        return sum,ret_pk
    except:
        import traceback; traceback.print_exc()
        print 'error in try '
        return 0,[]
    
def get_symbols(itemcontent,attdays,askleave):
    '''
    获取时段的符号描述
    '''
    symbols = ''
    if attdays.NoIn and not attdays.Absent>0:
        symbols += itemcontent[6]['ReportSymbol']
    if attdays.NoOut and not attdays.Absent:
        symbols += itemcontent[7]['ReportSymbol']
    if attdays.Late>0:
        symbols += itemcontent[1]['ReportSymbol'] + str(attdays.Late)
    if attdays.Early>0:
        symbols += itemcontent[2]['ReportSymbol'] + str(attdays.Early)
    if attdays.Absent>0:
        symbols += itemcontent[4]['ReportSymbol'] + str(attdays.Absent)
    if askleave>0:
        symbols += itemcontent[3]['ReportSymbol'] + str(askleave)
    if attdays.OverTime>0:
        symbols += itemcontent[5]['ReportSymbol'] + str(attdays.OverTime)
    return symbols

def save_attRecAbnormite(emp_id,att_time,type):
    '''
    保存统计(取卡)结果详情
    '''
    attrecord = attRecAbnormite()        
    attrecord.UserID_id = emp_id
    attrecord.checktime = att_time
    attrecord.CheckType = (type==1 and "I" or "O")
    attrecord.NewType =  (type==1 and "I" or "O")
    attrecord.AbNormiteID=0
    attrecord.SchID=0
    attrecord.OP=0
    attrecord.AttDate=att_time.date()
    try:
        attrecord.save()
    except IntegrityError:
        pass

def schclass_report(records_in,records_out):
    '''
    时段考勤报告
    '''
    from global_cache import C_ATT_RULE,C_SCH_CLASS
    AttRule=C_ATT_RULE.value
    SchClass_list=C_SCH_CLASS.value
    from get_param import get_calc_items
    calc_items = get_calc_items()
    '''数据合法性校验'''
    if (not records_in) or (not records_out):
        print '时段计算有误'
    if records_in[5]!=1 or records_out[5]!=2:
        print '时段计算有误'
    if records_in[1]!=records_out[1]:
        print  '时段计算有误'
    '''一般数据的处理'''
    schclass_id = records_in[1]
    emp_id = records_in[0]
    att_date = records_in[2].date()
    
    set_in = records_in[2]
    set_out = records_out[2]
    att_in = records_in[3]
    att_out = records_out[3]
    
    schclass_seconds = (set_out - set_in).seconds
    schclass_obj = SchClass_list.get(schclass_id)#SchClass.objects.get(pk=schclass_id)
    '''是否必须签到、必须签退 是:1 否:0 '''
    must_in = schclass_obj['CheckIn']#get_mustin_from_schclass_id(schclass_id)
    must_out = schclass_obj['CheckOut']#get_mustout_from_schclass_id(schclass_id)
    schclass_long = schclass_obj['shiftworktime']*60  #时段时长
    schclass_days= schclass_obj['WorkDay'] #工作日数
    '''例外数据处理(包括请假、调休、节假)'''
    askleave, setleave, holiday = parse_leave(records_in[7:10],records_out[7:10])
    holiday,holiday_pks = leave_analyse(holiday,schclass_seconds,emp_id,set_in,set_out, schclass_long=schclass_long)
    if holiday==0:
        askleave,except_pks = leave_analyse(askleave,schclass_seconds,emp_id,set_in,set_out,True,att_date,schclass_long)
        setleave,set_pks = leave_analyse(setleave,schclass_seconds,emp_id,set_in,set_out, schclass_long=schclass_long)
    else:
        askleave,except_pks = 0,[]
        setleave,set_pks = 0,[]
    _leave = False
    if schclass_id==1 or (records_out[6][1]==-1 and (askleave>0 or setleave>0 or holiday>0)):
        _leave = True
        MustIn = 0
        MustOut = 0
    else:
        MustIn = must_in
        MustOut = must_out
    '''是否未签到、未签退 是:1 否:0 '''
    if MustIn == 0:
        NoIn = 0
    else:
        if att_in:
            NoIn = 0
        else:
            NoIn = 1
    if MustOut == 0:
        NoOut = 0
    else:
        if att_out:
            NoOut = 0
        else:
            NoOut = 1
    '''迟到、早退 (单位/秒)'''
    if MustIn==0:
        Late=0
    else:
        if att_in:
            if att_in>set_in:
                _val = (att_in - set_in).seconds
                if _val>schclass_obj['LateMinutes']*60:
                    Late = _val
                else:
                    Late = 0
            else:
                Late = 0
        else:
            Late=0
    if MustOut==0:
        Early=0
    else:
        if att_out:
            if set_out>att_out:
                _val = (set_out - att_out).seconds
                if _val>schclass_obj['EarlyMinutes']*60:
                    Early = _val
                else:
                    Early = 0
            else:
                Early = 0
        else:
            Early=0
    if MustIn and (not att_in) and  AttRule['NoInAbsent']==1:
        Late = AttRule['MinsNoIn']*60
    if MustOut and (not att_out) and AttRule['NoOutAbsent']==1:
        Early = AttRule['MinsNoOut']*60
    '''是否旷工 是:True 否:False '''    
    Absent = False      
    if MustIn and (not att_in) and  AttRule['NoInAbsent']==2:
        #print '旷工类型 A'
        Absent = True
    if MustOut and (not att_out) and AttRule['NoOutAbsent']==2:
        #print '旷工类型 B'
        Absent = True
    if Late>AttRule['MinsLateAbsent']*60 or Early>AttRule['MinsEarlyAbsent']*60:
        #print '旷工类型 C'
        Absent = True
    if MustIn and MustOut and (not att_in) and (not att_out):
        #print '旷工类型 D'
        Absent = True
    '''相互影响的处理'''     
    if Absent:
        Late = 0
        Early = 0
    
    attdays = attShifts()
    attdays.UserID_id = emp_id
    attdays.AttDate = att_date
    attdays.SchIndex = schclass_id
    attdays.SchId_id = schclass_id
    attdays.ClockInTime = set_in
    attdays.ClockOutTime = set_out
    attdays.StartTime = att_in
    attdays.EndTime = att_out
    if _leave:
        must_long = 0
    else:
        must_long = schclass_long
    if Absent:
        absent_long = schclass_long
    else:
        absent_long = 0
    real_long = must_long - absent_long - Late - Early
    if real_long<0:real_long=0
    '''出勤时长 (单位/秒)'''
    WorkTime = real_long
    
    if schclass_id==1:
        if att_in and att_out:
            WorkTime = real_long = (att_out - att_in).seconds
        else:
            WorkTime = real_long = 0
    
    '''加班计算'''
    from overtime_calculate import get_sch_overtime,get_jbd_overtime
    sch_overtype = 0
    sch_overtime = 0
    overtime_desc = ''
    _overtime_pr = 0
    _overtime_xx = 0
    _overtime_jj = 0
    if not Absent and schclass_id!=1 and (not holiday>0 or records_out[6][1]!=-1):
        sch_overtype,sch_overtime = get_sch_overtime(real_long,schclass_obj['IsOverTime'],set_out,att_out,records_out[6][1], schclass_obj['OverTime'])
        overtime_desc,sch_overtime = get_jbd_overtime(emp_id,set_in,set_out,sch_overtime)
    _sch_overtime = deal_param(sch_overtime,calc_items[5],schclass_long,schclass_days)
    if sch_overtype==1:
        _overtime_pr = _sch_overtime
    if sch_overtype==2:
        _overtime_xx = _sch_overtime
    if sch_overtype==3:
        _overtime_jj = _sch_overtime
    
    attdays.WorkDay=deal_param(must_long,calc_items[0],schclass_long,schclass_days)
    attdays.RealWorkDay=deal_param(real_long,calc_items[0],schclass_long,schclass_days)
    attdays.MustIn=MustIn
    attdays.MustOut=MustOut
    attdays.NoIn=NoIn
    attdays.NoOut=NoOut
    attdays.Late = deal_param(Late,calc_items[1],schclass_long,schclass_days)
    attdays.LateCount = attdays.Late>0 and 1 or 0
    attdays.Early = deal_param(Early,calc_items[2],schclass_long,schclass_days)
    attdays.EarlyCount = attdays.Early>0 and 1 or 0
    attdays.Absent = deal_param(absent_long,calc_items[4],schclass_long,schclass_days)
    attdays.AbsentCount = attdays.Absent>0 and 1 or 0
    attdays.AbsentR= deal_param(absent_long,calc_items[4],schclass_long,schclass_days)
    attdays.ExceptionID = 0
    attdays.WorkTime = intdata(Decimal(WorkTime)/60,1,1)
    attdays.AttTime = schclass_obj['shiftworktime']  #时段时间(分钟)
    attdays.Exception=",".join(except_pks)

    attdays.SSpeDayNormalOT=_overtime_pr
    attdays.SSpeDayWeekendOT=_overtime_xx
    attdays.SSpeDayHolidayOT=_overtime_jj
    attdays.OverTime = _overtime_pr + _overtime_xx + _overtime_jj   #加班时间
    if attdays.OverTime==0:
        overtime_desc = ''
    attdays.OverTime_des = str(attdays.OverTime) + overtime_desc#加班单作用后的描述
    if askleave>schclass_long:
        askleave = schclass_long
    _askleave = deal_param(askleave,calc_items[3],schclass_long,schclass_days)
    attdays.Symbol = get_symbols(calc_items,attdays,_askleave)
    attdays.save()
    '''保存统计(取卡)结果详情'''
    if att_in:
        save_attRecAbnormite(emp_id,att_in,1)
    if att_out:
        save_attRecAbnormite(emp_id,att_out,2)