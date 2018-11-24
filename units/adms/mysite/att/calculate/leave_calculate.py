# -*- coding: utf-8 -*-
'''
考勤例外计算相关
'''
import datetime
import copy

from mysite import sql_utils

def get_holiday(start_date=None,end_date=None):
    '''
    功能: 获取在某期间的节假日
    返回:  ((id, datetime.date(2011, 6, 1), datetime.date(2012, 10, 1), 22),)
    '''
    sql = '''
select HolidayID,StartTime,Duration from holidays
order by StartTime
    '''
    rows = sql_utils.p_query(sql)
    result = []
    for e in rows:
        StartTime = datetime.datetime(e[1].year,e[1].month,e[1].day,0,0,0)
        EndTime = datetime.datetime(e[1].year,e[1].month,e[1].day,23,59,59) + datetime.timedelta(days=e[2]-1)
        result.append((e[0],StartTime,EndTime))
    return result

def get_askleave(emp,start_date,end_date):
    '''
    功能: 获取人员在某期间的审核通过的请假
    返回:  ((ID, 开始时间, 结束时间),...)
        例 ((id, datetime.date(2011, 6, 1), datetime.date(2012, 10, 1)),...)
    '''
    sql = '''
select id,StartSpecDay,EndSpecDay from user_speday 
where audit_status=2 and UserID=%s and (EndSpecDay>'%s' and StartSpecDay<'%s')
order by StartSpecDay
    '''%(emp,start_date.strftime('%Y-%m-%d %H:%M:%S'),end_date.strftime('%Y-%m-%d %H:%M:%S'))
    rows = sql_utils.p_query(sql)
    return rows

def get_setleave(emp,start_date,end_date):
    '''
    功能: 获取人员在某期间的调休里的休息类型
    返回:  ((id, datetime.date(2011, 6, 1), datetime.date(2012, 10, 1), 22),)
    '''
    sql = '''
select id,starttime,endtime from setuseratt
where UserID_id = %s and atttype=2 and (endtime>'%s' and starttime<'%s')
order by starttime
    '''%(emp,start_date.strftime('%Y-%m-%d %H:%M:%S'),end_date.strftime('%Y-%m-%d %H:%M:%S'))
    rows = sql_utils.p_query(sql)
    return rows

def calc_leave(att_records_origin,att_records,leave_periods,type):
    '''
    功能 假休计算
    
    att_records_origin: 计算结果数据结构
    att_records: 带尾部索引的计算结果数据结构
    leave_periods: 假休数据
    type: 类型标识 7:请假 8:调休 9:节假
    '''    
    for p in leave_periods: ###### 循环所有假休时段
        pass
        start_time = p[1] #假休开始
        end_time = p[2] #假休结束
        plong_delta = end_time-start_time #假休时长
        plong = plong_delta.days*24*3600 + plong_delta.seconds
        pid = p[0]  #假休ID
        pre_att_rec = None#上一卡记录指针
        pop_list = []
        for r in att_records:###### 循环所有卡
            if r[5]==1:
                if r[2]>=end_time:#-----------对应模型1
                    pre_att_rec = r
                    break
                else:   #----------------------对应模型2
                    val = end_time-r[2]# val 为假休对考勤点的影响值
                    att_records_origin[r[-1]][type].append((pid,plong, val.days*24*3600 +val.seconds )) #= '%s:%s'%(pid,val.seconds)
                    #pop_list.append(r)
            elif r[5]==2:
                if r[2]>end_time:#-----------对应模型3
                    val = r[2] - start_time
                    att_records_origin[r[-1]][type].append((pid,plong, val.days*24*3600 +val.seconds ))
                elif r[2]<=start_time:#--------对应模型4
                    pop_list.append(r)
                    if pre_att_rec:
                        pop_list.append(pre_att_rec)
                        #att_records_origin[pre_att_rec[-1]][type] = []
                        m_val = end_time-pre_att_rec[2]
                        m_del = (pid,plong, m_val.days*24*3600 +m_val.seconds )
                        try:
                            att_records_origin[pre_att_rec[-1]][type].remove(m_del)
                        except:
                            print 'Att calculate error 101'
                else:#------------------------对应模型5
                    val = r[2] - start_time
                    att_records_origin[r[-1]][type].append((pid,plong, val.days*24*3600 +val.seconds ))
                    pop_list.append(r)
                    if pre_att_rec:
                        pop_list.append(pre_att_rec)
            pre_att_rec = r
        for e in pop_list:
            try:
                att_records.remove(e)
            except:
                print 'Att calculate error 102'

def calc_leave_old(att_records_origin,att_records,leave_periods,type):       
    for p in leave_periods: ###### 循环所有假休时段
        pass
        start_time = p[1]
        end_time = p[2]
        pid = p[0]
        pre_att_rec = None
        pop_list = []
        for r in att_records:###### 循环所有卡
            if r[2]<=start_time:
                pop_list.append(r)
                pre_att_rec = r
                continue
            else:
                if r[2]<end_time:
                    pop_list.append(r)
                    if r[5]==1:
                        val = end_time - r[2] 
                        '''type: ask, set, hol (6, 7, 8) '''
                        att_records_origin[r[-1]][type] = '%s:%s'%(pid,val.seconds)
                    if r[5]==2:
                        if not pre_att_rec:
                            ''' 第一次 签退 '''
                            val = r[2] - start_time
                            '''type: ask, set, hol (6, 7, 8) '''
                            att_records_origin[r[-1]][type] = '%s:%s'%(pid,val.seconds)
                        else:
                            ''' 非第一次 签退'''
                            val = r[2] - start_time
                            p_len = r[2] - pre_att_rec[2]
                            if val >= p_len:
                                att_records_origin[pre_att_rec[-1]][type] = '%s:%s'%(pid,p_len.seconds)
                                val = p_len
                            '''type: ask, set, hol (6, 7, 8) '''
                            att_records_origin[r[-1]][type] = '%s:%s'%(pid,val.seconds)
                else:
                    break
                pre_att_rec = r
        for e in pop_list:
            att_records.remove(e)

def deal_att_leave(emp,start_date=None,end_date=None):
    '''
    功能: 计算某人员某期间的考勤记录列表(含假休处理结果)
    返回:  (  (人员ID, 时段ID, 设定时间, 考勤时间, 打卡ID, 上/下班标识, [ 覆盖类型标识, 工作类型, 排班ID ],\
                 [(请假ID,请假时长, 影响值),... ], [(调休ID,请假调休, 影响值),... ], [(节假日ID,节假日时长, 影响值),... ] ),... ) 
        例 (  (empID, SchclassID, set_time, att_time, att_ID, type, attrs, ask, set, hol),... ) 按 set_time 先后顺序排列
    '''
    from global_cache import C_HOLIDAY
    ''' 获得人员的 1. 请假 2. 调休 3. 节假日 信息 '''
    askleave = get_askleave(emp,start_date,end_date)
    setleave = get_setleave(emp,start_date,end_date)
    holiday = C_HOLIDAY.value
    ''' 获得取卡计算结果 '''
    from take_card import take_card
    initial_att_records = take_card(emp,start_date,end_date)
    '''####################向取卡结果中加入假休计算数据位和尾部索引字段'''
    '''添加假休计算数据位'''
    att_records_origin = []
    for e in  initial_att_records:
        data = copy.deepcopy(e)
        data.append([])
        data.append([])
        data.append([])
        att_records_origin.append(data)
    '''加入索引位'''        
    att_records = []
    count = 0
    for e in  initial_att_records:
        data = copy.deepcopy(e)
        data.append(count)
        att_records.append(data)
        count +=1
    '''释放原数据占用的内存'''    
    del initial_att_records
    ''' 假休计算 '''
    calc_leave(att_records_origin, copy.deepcopy(att_records), askleave,7)
    calc_leave(att_records_origin, copy.deepcopy(att_records), setleave,8)
    calc_leave(att_records_origin, copy.deepcopy(att_records), holiday,9)
    
    return att_records_origin

            