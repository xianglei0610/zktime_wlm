# -*- coding: utf-8 -*-

import datetime

def get_emp_jdb(emp):
    from global_cache import JBD_DATA
    _data = JBD_DATA.get(emp,'None')
    if _data!='None':
        return _data
    else:
        from mysite.att.models.model_overtime import OverTime
        overtimedata = OverTime.objects.filter(emp = emp,audit_status=2).values_list('starttime', 'endtime').order_by('emp','starttime')
        JBD_DATA[emp] = overtimedata
        return overtimedata

def get_sch_overtime(real_long,IsOverTime, set_out, att_out, type, OverTime):
    '''
    计算时段的加班时间
    real_long 实到时间
    IsOverTime，时段是否延时计为加班
    type 时段的工作类型
    '''
    if type in (1,2,3):
        '''加班时段'''
        if IsOverTime:
            '''延时计为加班'''
            if att_out and att_out>set_out:
                _val = (att_out-set_out).seconds
                if _val>=OverTime*60:
                    return type,_val+real_long
                else:
                    return type,real_long
            else:
                return type,real_long
        else:
            return type,real_long
    else:
        if IsOverTime:
            '''延时计为加班'''
            if att_out and att_out>set_out:
                _val = (att_out-set_out).seconds
                if _val>=OverTime*60:
                    return 1,_val
                else:
                    return 1,0
            else:
                return 1,0
        else:
            return 1,0
        
def get_jbd_overtime(emp,start,end,init_overtime):
    '''
    加班单计算
    '''
    from global_cache import C_ATT_RULE
    AttRule=C_ATT_RULE.value
    action_type = AttRule['jbd_action_type']
    time = datetime.timedelta(minutes=0)
    ret = ''
    val = 0
    _data = get_emp_jdb(emp)
    for e in  _data:
        start_time = e[0].time()
        start_date = e[0].date()
        if start_date ==end.date() and e[0]>=start and  e[0]<=end:
            time += e[1] - e[0]
    time = time.seconds
    if init_overtime>0:
        if time>0:
            if action_type == 1:
                ret = init_overtime
            elif action_type == 2:
                ret =  time
            elif action_type == 3:
                ret =  min(init_overtime,time)
            val = ret
            ret = ''
        else:
            ret = u'(加班单暂缺)'
            val = init_overtime
    else:
        if time>0:
            ret = u'(主计算为零)'
            val = time
        else:
            ret = ''
            val = 0
    return ret,val