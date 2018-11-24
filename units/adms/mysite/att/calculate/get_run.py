# -*- coding: utf-8 -*-
import datetime

from mysite import sql_utils

def get_emp_run(emp,start_date,end_date):
    '''
    功能: 获取人员在某期间的【排班】
    返回: ( (人员ID, 开始时间, 结束时间, 班次ID, 排班ID), ) 
            例 ((14, datetime.date(2011, 6, 1), datetime.date(2012, 10, 1), 22),)
    '''
    sql = '''
select UserID,StartDate,EndDate,NUM_OF_RUN_ID,id
from user_of_run 
where UserID=%s and (enddate>'%s' and startdate<'%s') 
order by user_of_run.StartDate 
    '''%(emp,start_date.strftime('%Y-%m-%d %H:%M:%S'),end_date.strftime('%Y-%m-%d %H:%M:%S'))
    rows = sql_utils.p_query(sql)
    return rows

def get_emp_num_run():
    '''
    获取所有班次
    返回" {班次ID : [周期单位, 周期数]}
    {id:[Units,Cyle]}
    '''
    sql = '''
select Num_runID,Units,Cyle from num_run
    '''
    rows = sql_utils.p_query(sql)
    ret = {}
    for r in rows:
        ret[r[0]]=[r[1],r[2]]
    return ret

def get_run_detail(num_run_ID):
    '''
    功能: 获取某个班次的班次详细
    返回：( (开始时间, 结束时间, 第几天, 时段ID, 开始签到时间, 结束签到时间, 开始签退时间, 结束签退时间) )
            ((datetime.time(7, 0), datetime.time(15, 0), 0, 15, ...), 
            (datetime.time(23, 0), datetime.time(7, 0), 0, 17, ...), 
            (datetime.time(19, 0), datetime.time(7, 0), 1, 14, ...),
            (datetime.time(19, 0), datetime.time(7, 0), 2, 14, ...),  ...
    '''
    sql = '''
select d.StartTime,d.EndTime,d.Sdays,d.SchclassID,s.CheckInTime1, s.CheckInTime2,s.CheckOutTime1,s.CheckOutTime2
from num_run_deil as d,schclass as s
where num_runid = %s and d.SchclassID = s.SchclassID
order by d.Sdays,d.StartTime
    '''%num_run_ID
    rows = sql_utils.p_query(sql)
    return rows

def deal_cross_day(begin,end,e):
    '''
    开始签到,签退 结束签到,签退的跨天处理
    
    begin 上班日期
    end 下班日期
    e 待处理的数据 [上班时间，下班时间，覆盖类型，ID，开始签到，结束签到，开始签退，结束签退]   
    返回处理后的  [开始签到，结束签到，开始签退，结束签退] 
    '''
    e = list(e)
    m_len = len(e)
    for i in range(m_len):
        if type(e[i])==datetime.datetime:
            e[i]= e[i].time()
    d4 = datetime.datetime(begin.year,begin.month,begin.day,e[4].hour,e[4].minute,e[4].second)    
    if e[4]>e[0]:
        CheckInTime1 = d4+datetime.timedelta(days=-1)
    else:
        CheckInTime1 = d4
    d5 = datetime.datetime(begin.year,begin.month,begin.day,e[5].hour,e[5].minute,e[5].second) 
    if e[5]< e[0]:
        CheckInTime2 = d5+datetime.timedelta(days=1)
    else:
        CheckInTime2 = d5
    
    
    d6 = datetime.datetime(end.year,end.month,end.day,e[6].hour,e[6].minute,e[6].second)    
    if e[6]>e[1]:
        CheckOutTime1 = d6+datetime.timedelta(days=-1)
    else:
        CheckOutTime1 = d6
    d7 = datetime.datetime(end.year,end.month,end.day,e[7].hour,e[7].minute,e[7].second)
    if e[7]< e[1]:
        CheckOutTime2 = d7+datetime.timedelta(days=1)
    else:
        CheckOutTime2 = d7
    return CheckInTime1,CheckInTime2,CheckOutTime1,CheckOutTime2

def get_start_index(start,num_run_attr):
    '''
    获取起始索引和周期长
    '''
    Units = num_run_attr[0]
    Cyle = num_run_attr[1]
    if Units==0:#天
        return 0,Cyle
    elif Units==1:#周
        wd = start.weekday()
        index = wd+1
        if index==7:
            index=0
        return index,Cyle*7
    elif Units==2:#月
        day = start.day
        return day-1,Cyle*31

def get_emp_run_time(emp=None,start_date=None,end_date=None):
    '''
    功能: 获取人员某期间的【时段列表】
    返回: ((设定的签到时间,    设点的签退时间,    时段ID,    开始签到,    结束签到,    开始签退,    结束签退, [ 覆盖类型标识, 工作类型, 排班ID ] ),)
         例 ((begin,    end,    SchclassID,    CheckInTime1,    CheckInTime2,    CheckOutTime1,    CheckOutTime2, [-1,-1,run_id] ),)
    '''
    from global_cache import C_NUM_RUN
    num_run_dic = C_NUM_RUN.value
    emp_run = get_emp_run(emp,start_date,end_date)
    run_time = []
    '''r: ( (人员ID, 开始时间, 结束时间, 班次ID, 排班ID), ) '''
    for r in emp_run:######### 循环该期间的所有排班
        '''run_detail:  ( (开始时间, 结束时间, 第几天, 时段ID, 开始签到时间, 结束签到时间, 开始签退时间, 结束签退时间) )'''
        run_detail = get_run_detail(r[3])   #获取班次详细 r[3]为班次ID
        num_run_dic = get_emp_num_run()
        num_run_attr = num_run_dic[r[3]]#获取班次属性
        emp_run_id = r[4]
        d1 = datetime.datetime(r[1].year,r[1].month,r[1].day,0,0,0) 
        d2 = datetime.datetime(r[2].year,r[2].month,r[2].day,23,59,59) 
        day_current = d1 #定义'当前天'
        '''起始索引(周期的第几天), 周期长'''
        index_current, cycle_len= get_start_index(d1,num_run_attr)
        while day_current<=d2:
            if day_current< start_date or day_current>end_date: #'当前天'不在统计的时间范围时
                pass
            else:
                ''' 获取当前天的所有时段 '''
                day_current_sch = [e for e in run_detail if e[2]==index_current]
                '''e:  ( (开始时间, 结束时间, 第几天, 时段ID, 开始签到时间, 结束签到时间, 开始签退时间, 结束签退时间) )'''
                for e in day_current_sch:
                    begin = datetime.datetime(day_current.year,day_current.month,day_current.day,e[0].hour,e[0].minute,e[0].second)
                    end = datetime.datetime(day_current.year,day_current.month,day_current.day,e[1].hour,e[1].minute,e[1].second)
                    if e[0]>e[1]:
                        end = end+datetime.timedelta(days=1)
                        
                    result = deal_cross_day(begin,end,e)
                    
                    run_time.append((begin,end,e[3],result[0],result[1],result[2],result[3],[-1,-1,emp_run_id]))
            day_current = day_current + datetime.timedelta(days=1)
            index_current = index_current +1
            if index_current == cycle_len:
            	index_current = 0
    return run_time
    for e in run_time:
        print e