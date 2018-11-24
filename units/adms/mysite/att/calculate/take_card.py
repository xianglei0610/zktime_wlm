# -*- coding: utf-8 -*-
'''
取卡相关
'''
import datetime
import copy

from mysite import sql_utils
        
def get_initial_record(emp,start_date=None,end_date=None):
    '''
    功能: 获取人员某期间的原始签卡记录
    返回:  ((ID, 人员ID, 签卡时间, 签卡类型, 引用计数), )
    ((id, userid, checktime, checktype,counter),)
    '''
    sql = '''
select c.id,u.userid, c.checktime, c.checktype, 0 as counter 
    from checkinout as c
    left join userinfo as u on u.badgenumber = c.pin
    where u.userid=%s and c.checktime>='%s' and c.checktime<='%s' 
    order by c.checktime
    '''%(emp,start_date.strftime('%Y-%m-%d %H:%M:%S'),end_date.strftime('%Y-%m-%d %H:%M:%S'))
    rows = sql_utils.p_query(sql)
    return rows

def get_att_record(initial_record_origin,initial_record,start_date=None,end_date=None):
    '''
    功能: 从签卡记录集合中取出某个考勤区的签卡记录
    返回: [index1, index2, index3,...]
    '''
    att_record = []#取到的卡的索引列表
    pop_list = []   #要去除掉卡
    len_ = len(initial_record)
    for r in initial_record:
        e = initial_record_origin[r[-1]]
        if e[2]<start_date:
            pop_list.append(r)  #既然在这个时段的左边那必定也在下个时段的左边, 所以pop掉
            continue
        else:
            if e[2]<=end_date:
                '''保存记录索引值'''
                att_record.append(r[-1])
                e[4] +=1 #取一次引用计数就加1
            else:
                break
    for e in pop_list:
        initial_record.remove(e)
    return att_record

def deal_take_card_type(set_time,record_time,type):
    '''
    取卡就近/最早/最晚规则的运用
    
    set_time: 设定时间
    record_time: 打卡时间
     type　1:上班　2:下班
    '''
    from global_cache import C_ATT_RULE
    AttRule=C_ATT_RULE.value
    update_flag= False
    if type==1:
        if AttRule['TakeCardIn'] == 2:
            update_flag= False
        else:
            if record_time<=set_time:
                update_flag= True
            else:
                update_flag= False
    elif type==2:
        if AttRule['TakeCardOut'] == 1:
            update_flag= False
        else:
            if record_time>=set_time:
                update_flag= True
            else:
                update_flag= False
    return update_flag

def get_run_att(initial_record_origin,run_att_record,set_time,type):
    '''
    功能: 从考勤区间的签卡集合中取出考勤记录(即取卡)    type　０:上下班　1:上班　2:下班
    initial_record_origin    [(id, userid, checktime, checktype,counter),]
    run_att_record    [index1, index2, index3,...]
    返回 取到的目标卡、目标卡ID
    '''
    pre = None#目标卡指针
    ''' 上下班 '''
    len_ = len(run_att_record)
    for i in range(len_):
        '''当前卡data: (id, userid, checktime, checktype,counter)'''
        data = initial_record_origin[run_att_record[i]]
        if data[4]==-1:
            '''此签卡被上一个区间取过了'''
            continue
        if data[4]==1:
            ''' 区间正常签卡'''
            if pre:
                '''上次取过卡'''
                update_flag= deal_take_card_type(set_time,data[2],type) #通过应用取卡规则来判断是否做更新
                if update_flag:
                    pre = data
                else:
                    pass
            else:
                pre = data
        else:
            '多区间公用签卡'
            if data[4]>10:
                '''此公共签卡未被曾被上一个区间"考虑"过 (待用接口)'''
                pass
            else:
                '''此公共签卡第一次被"考虑" (待用接口)'''
                pass
            if pre:
                '''上次取过卡'''
                update_flag= deal_take_card_type(set_time,data[2],type)
                if update_flag:
                    '''做取卡处理'''
                    pre = data
                    initial_record_origin[run_att_record[i]][4] = -1
                else:
                    '''做考虑卡处理'''
                    initial_record_origin[run_att_record[i]][4] += 10
            else:
                '''做取卡处理'''
                pre = data
                initial_record_origin[run_att_record[i]][4] = -1
    if pre:
        return pre[0],pre[2]
    else:
        return None,None

def get_run_att_flex(initial_record_origin,run_att_record,in_time,out_time):
    '''
    功能: 弹性时段取卡
    返回: ( ( (上班签卡ID, 上班签卡时间),(下班签卡ID, 下班签卡时间) ),...)
    '''
    pre = None#上/下班标识指针
    in_list = []#上班卡列表
    out_list = []#下班卡列表
    len_ = len(run_att_record)
    for i  in range(len_):
        e = run_att_record[i]
        '''当前卡data: (id, userid, checktime, checktype,counter)'''
        data = initial_record_origin[e]
        if data[4]==-1:
            '''此签卡被上一个区间或上一次取了'''
            continue
        if data[4]>=2:
            ''' 区间正常签卡(包括多区间共用卡)'''
            result = (data[0],data[2])
            initial_record_origin[e][4] = -1
            if pre==1:
                '''上班'''
                if i !=len_-1:
                    initial_record_origin[e][4] = -1
                    in_list.append(result)
                    pre = 2
            elif pre==2:
                '''上班'''
                initial_record_origin[e][4] = -1
                out_list.append(result)
                pre = 1
            else:
                '''首次'''
                if i !=len_-1:
                    initial_record_origin[e][4] = -1
                    in_list.append(result)
                    pre = 2
        else:
            ''' 不合理的签卡 '''
            pass
    ret = []
    count = min((len(in_list),len(out_list)))
    for i in range(count):
        ret.append((in_list[i],out_list[i])) 
    return ret


def take_card(emp,start_date=None,end_date=None):
    '''
    功能: 计算出人员某期间的考勤记录列表
    返回: ((人员ID, 时段ID, 设定时间, 考勤时间, 打卡ID, 上/下班标识, [ 覆盖类型标识, 工作类型, 排班ID ]),...)
        例 ((empID, SchclassID, set_time, att_time, att_ID, type, [-1,-1,run_id] ),...) 按 set_time 先后顺序排列
    '''
#    start_date = datetime.datetime(2011,6,1,0,0,0)
#    end_date = datetime.datetime(2011,7,1,23,59,59)
    
#    from schedul_calculate import get_emp_run_time
#    run_time = get_emp_run_time(emp,start_date,end_date)
    from get_run_temp import get_run_time,get_temp_flex_id
    '''run_time: ((上班时间，下班时间，时段ID，开始签到，结束签到，开始签退，结束签退,  [ 覆盖类型标识, 工作类型, 排班ID ] ),)'''
    run_time = get_run_time(emp,start_date,end_date)    #---得到时间段数据
    
    #temp_flex_id = get_temp_flex_id(emp,start_date,end_date)    #---得到临时班次数据中的弹性时段类型ID
    if run_time:
        initial_record_origin = get_initial_record(emp,run_time[0][3],run_time[-1][6])  #---取时间区间范围内的原始记录
        initial_record_origin = [list(e) for e in initial_record_origin]    #---原始数据
    else:
        initial_record_origin = []
    initial_record = [] #---在原始数据的基础上添加尾部索引字段
    count = 0
    for e in  initial_record_origin:
        data = copy.deepcopy(e)
        data.append(count)
        initial_record.append(data)
        count +=1
 
    att_result = []
    len_ = len(run_time)
    att_record_in_next = []
    att_record_out_next = []
    for i in range(len_):########### 循环所有时段来取卡
        e = run_time[i]
        if i==0:
            att_record_in = get_att_record(initial_record_origin,initial_record,e[3],e[4])
            att_record_out = get_att_record(initial_record_origin,initial_record,e[5],e[6])
        else:
            att_record_in = att_record_in_next
            att_record_out = att_record_out_next
        if i<len_-1:###下一个时段的区间卡
            e_next = run_time[i+1]
            att_record_in_next = get_att_record(initial_record_origin,initial_record,e_next[3],e_next[4])
            att_record_out_next = get_att_record(initial_record_origin,initial_record,e_next[5],e_next[6])

        if e[2]==1:# or e[2] in temp_flex_id:
            ''' 弹性时段 '''
            att_record_flex = att_record_in + att_record_out
            att_record_flex.sort()
            flex_result = get_run_att_flex(initial_record_origin,att_record_flex,e[0],e[1])
            for ret in flex_result:
                att_result.append([emp,e[2],e[0],ret[0][1],ret[0][0],1,e[-1]])
                att_result.append([emp,e[2],e[1],ret[1][1],ret[1][0],2,e[-1]])
        else:
            run_att__in = get_run_att(initial_record_origin,att_record_in,e[0],1)
            run_att__out = get_run_att(initial_record_origin,att_record_out,e[1],2)
            att_result.append([emp,e[2],e[0],run_att__in[1],run_att__in[0],1,e[-1]])
            att_result.append([emp,e[2],e[1],run_att__out[1],run_att__out[0],2,e[-1]])
    return att_result

    for e in att_result:
        print e 