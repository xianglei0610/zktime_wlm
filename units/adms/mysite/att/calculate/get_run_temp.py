# -*- coding: utf-8 -*-
import datetime

from mysite import sql_utils

def get_temp_flex_id(emp=None,start_date=None,end_date=None):
    '''
    得到临时班次数据中的弹性时段类型ID
    '''
    sql = '''
select t.id
from user_temp_sch as t,schclass as s
where t.UserID=%s and t.SchClassID = s.SchclassID and (t.LeaveTime>'%s' and t.ComeTime<'%s') and t.SchClassID=1 
order by t.ComeTime 
    '''%(emp,start_date.strftime('%Y-%m-%d %H:%M:%S'),end_date.strftime('%Y-%m-%d %H:%M:%S'))
    rows = sql_utils.p_query(sql)
    id_list = [e[0] for e in rows]
    return id_list

def get_emp_run_time_temp(emp=None,start_date=None,end_date=None):
    '''
    返回处理后的时间段数据 
        例 ( (设定的签到时间,    设点的签退时间，时段ID，开始签到，结束签到，开始签退，结束签退, [ 覆盖类型标识, 工作类型, 排班ID ] ), )
    '''
    sql = '''
select t.ComeTime,t.LeaveTime,t.Flag,t.SchClassID,s.CheckInTime1, s.CheckInTime2,s.CheckOutTime1,s.CheckOutTime2,t.WorkType,t.id
from user_temp_sch as t,schclass as s
where t.UserID=%s and t.SchClassID = s.SchclassID and (t.LeaveTime>'%s' and t.ComeTime<'%s') 
order by t.ComeTime 
    '''%(emp,start_date.strftime('%Y-%m-%d %H:%M:%S'),end_date.strftime('%Y-%m-%d %H:%M:%S'))
    rows = sql_utils.p_query(sql)
    run_time_temp = []  
    for e in rows:
        begin = [e[0]][0]
        end = [e[1]][0]
        e_ = list(e)
        e_[0] = e_[0].time()
        e_[1] = e_[1].time()
        from get_run import deal_cross_day
        result = deal_cross_day(begin,end,e_)
        run_time_temp.append((begin,end,e[3],result[0],result[1],result[2],result[3],[e[2],e[8],e[9]]))
    return run_time_temp

def get_run_time(emp=None,start_date=None,end_date=None):
    '''
    得到时间段数据(包含正常时间段数据和临时时间段数据的取舍处理)
    返回 ((上班时间，下班时间，时段ID，开始签到，结束签到，开始签退，结束签退,  [ 覆盖类型标识, 工作类型, 排班ID ] ),)
    '''
    from get_run import get_emp_run_time
    run_time = get_emp_run_time(emp,start_date,end_date)
    run_time_temp = get_emp_run_time_temp(emp,start_date,end_date)
    run_time_all = run_time + run_time_temp
    run_time_all.sort(cmp=lambda x,y:cmp(x[0],y[0]))
    #run_time_all_for = run_time_all[:]
    pop_list = [] #要去掉的时段列表
    pre = None  #上一个时段
    for e in run_time_all:
        if not pre:
            pre = e
        else:
            ''' 非第一次 '''
            if e[0]>pre[1]:
                ''' 无交集 '''
                pre = e
            else:
                ''' 有交集 '''
                if pre[-1][0]==-1:
                    ''' 上一个为正常时段 '''
                    if e[-1][0]==-1:
                        pop_list.append(e[:])
                    elif e[-1][0]==1:#临时时段优先
                        pop_list.append(pre[:])
                        pre = e
                    elif e[-1][0]==2:#正常时段优先
                        pop_list.append(e[:])
                else:
                    ''' 上一个为临时时段 '''
                    if pre[-1][0]==1:
                        ''' 三种情况均pop '''
                        pop_list.append(e[:])
                    elif pre[-1][0]==2:
                        if e[-1][0]==-1:
                            pop_list.append(pre[:])
                            pre = e
                        else:
                            pop_list.append(e[:])
    
    for p in  pop_list:
        run_time_all.remove(p)
    return run_time_all