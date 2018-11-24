#coding=utf-8
from mysite.sql_utils import get_sql
#获取IC消费明细报表sql语句
def get_ic_list_record_sql(table_name,st,et,tag,operate,pos_model,dining,ids,userids,top_count = ""):
    params={}
    id_part={}
    params["table_name"] = table_name
    params["st"] = st
    params["et"] = et
    params["top_count"] = top_count
    id_part["and"] = []
    if operate!="9999":
        params["operate"] = operate
        id_part["and"].append("operate")
    if pos_model!="0":#消费模式
        params["pos_model"] = pos_model
        id_part["and"].append("pos_model")
    if dining!="0":#餐厅
        params["dining"] = dining
        id_part["and"].append("dining")
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
            id_part["and"].append("no_emp")
    else:
         params["userids"] = userids
         id_part["and"].append("userids")
    sql = get_sql("ic_report_sql",sqlid="get_ic_list_record_sql",app = "pos",params = params ,id_part = id_part )
    return sql


#ic消费明细表，统计结果汇总
def get_ic_list_summary__sql(table_name,st,et,tag,operate,pos_model,dining,ids,userids):
    params={}
    id_part={}
    params["table_name"] = table_name
    params["st"] = st
    params["et"] = et
    id_part["and"] = []
    if operate!="9999":
        params["operate"] = operate
        id_part["and"].append("operate")
    if pos_model!="0":#消费模式
        params["pos_model"] = pos_model
        id_part["and"].append("pos_model")
    if dining!="0":#餐厅
        params["dining"] = dining
        id_part["and"].append("dining")
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
            id_part["and"].append("no_emp")
    else:
         params["userids"] = userids
         id_part["and"].append("userids")
    sql = get_sql("ic_report_sql",sqlid="get_ic_list_summary__sql",app = "pos",params = params ,id_part = id_part )
    return sql


#充值明细表
def get_ic_recharge_report_sql(begin_time,end_time):
#    sql="select user_id,card,cardserial,money,blance,checktime,create_operator,convey_time,sys_card_no,sn_name,log_flag,type_id,serialnum from pos_carcashsz where type_id in (1,13) and checktime>='%s' and checktime <'%s'  "%(begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    sql = get_sql("ic_report_sql",sqlid="get_ic_recharge_report_sql",app = "pos",params = params ,id_part = id_part )
    return sql

#退款明细表
def get_ic_reimburese_report_sql(type_id,begin_time,end_time):
#    sql="select user_id,card,cardserial,money,blance,checktime,create_operator,convey_time,sys_card_no,sn_name,log_flag,serialnum from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["type_id"] = type_id
    sql = get_sql("ic_report_sql",sqlid="get_ic_reimburese_report_sql",app = "pos",params = params ,id_part = id_part )
    return sql

#补贴明细表
def get_ic_allow_report_sql(type_id,begin_time,end_time):
#    sql="select user_id,card,cardserial,money,blance,checktime,create_operator,convey_time,sys_card_no,sn_name,log_flag,allow_type,serialnum from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["type_id"] = type_id
    sql = get_sql("ic_report_sql",sqlid="get_ic_allow_report_sql",app = "pos",params = params ,id_part = id_part )
    
    return sql

#退卡明细表
def get_ic_return_card_report(type_id,begin_time,end_time):
#    sql="select user_id,card,cardserial,checktime,create_operator,money,sys_card_no from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["type_id"] = type_id
    sql = get_sql("ic_report_sql",sqlid="get_ic_return_card_report",app = "pos",params = params ,id_part = id_part )
    return sql

#卡成本表
def get_ic_cost_report_sql(type_id,begin_time,end_time):
#    sql="select user_id,card,cardserial,checktime,create_operator,money,sys_card_no from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["type_id"] = type_id
    sql = get_sql("ic_report_sql",sqlid="get_ic_cost_report_sql",app = "pos",params = params ,id_part = id_part )
    
    return sql

#发卡表
def get_ic_issuecard_report_sql(type_id,begin_time,end_time):
#    sql="select user_id,card,checktime,create_operator,sys_card_no from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["type_id"] = type_id
    sql = get_sql("ic_report_sql",sqlid="get_ic_issuecard_report_sql",app = "pos",params = params ,id_part = id_part )
    return sql

#卡余额表
def get_ic_card_blance_report(userids,ids,operate,tag,begin_time=None,end_time=None,card_type=None):
#    sql="select UserID_id,cardno,type_id,blance,create_operator,sys_card_no from personnel_issuecard where cardstatus in (1,3,4,5) and card_privage = 0 and status = 0 "
    params={}
    id_part={}
    id_part["and"] = []
    if card_type: #无卡退卡表
        params["card_type"] = card_type
        params["st"] = begin_time
        params["et"] = end_time
        id_part["and"].append("card_type")
    else:
        if operate!="9999":
            params["operate"] = operate
            id_part["and"].append("operate")
        if len(ids)==0:#没有选择人 
           if tag=="NoEmp":
               id_part["and"].append("no_emp")
        else:
            params["userids"] = userids
            id_part["and"].append("userids")
    sql = get_sql("ic_report_sql",sqlid="get_ic_card_blance_report",app = "pos",params = params ,id_part = id_part )
    return sql

#餐厅，部门，设备汇总
def ic_dining_or_dept_or_device_report_sql(dbname,op_id,begin_time,end_time):
#    sql = '''
#            select
#            sum(case when  pos_model=9 then money else 0 end) as back_money,
#            sum(case when  pos_model=9 then 1 else 0 end) as back_count,
#            sum(case when  type_name=6 then 1 else 0 end) as pos_count,
#            sum(case when  type_name in (6,8) then money else 0 end) as summary_money,
#            sum(case when  pos_model=4 then 1 else 0 end) as total_count,
#            sum(case when  type_name=8 then money else 0 end) as add_single_money %(where)s   
#        '''
    params={}
    id_part={}
    params['op_id'] = op_id
    params['st'] = begin_time
    params['et'] = end_time
    if dbname == 'Dininghall':
        id_part['where'] = "Dininghall"
#        sql_db = sql%({'where':" from pos_icconsumerlist where  dining_id = %s and pos_time>='%s' and pos_time <'%s'"%(op_id,begin_time,end_time)})
    elif dbname == 'Device':
        id_part['where'] = "Device"
#        sql_db = sql%({'where':" from pos_icconsumerlist where  dev_sn = '%s' and pos_time>='%s' and pos_time <'%s'"%(op_id,begin_time,end_time)})
    elif dbname == 'Department':
        id_part['where'] = "Department"
#        sql_db = sql%({'where':" from pos_icconsumerlist where  dept_id = %s and pos_time>='%s' and pos_time <'%s'"%(op_id,begin_time,end_time)})
    sql_db = get_sql("ic_report_sql",sqlid="ic_dining_or_dept_or_device_report_sql",app = "pos",params = params ,id_part = id_part )
    return sql_db


#设备异常明细汇总
def ic_device_or_dining_error_log_sql(dbname,op_id,begin_time,end_time):
    params={}
    id_part={}
    params['op_id'] = op_id
    params['st'] = begin_time
    params['et'] = end_time
    
    if dbname == 'Dininghall':
        id_part['where'] = "Dininghall"
        sql_db = get_sql("ic_report_sql",sqlid="ic_device_or_dining_error_log_sql",app = "pos",params = params ,id_part = id_part )
    elif dbname == 'Device':
        id_part['where'] = "Device"
        sql_db = get_sql("ic_report_sql",sqlid="ic_device_or_dining_error_log_sql",app = "pos",params = params ,id_part = id_part )
    return sql_db



#个人消费汇总
def ic_emp_summary_report_sql(userids,begin_time,end_time):
#    sql = '''
#        select
#           sum(case when  pos_model=9 then money else 0 end) as back_money,
#           sum(case when  pos_model=9 then 1 else 0 end) as back_count,
#           sum(case when  type_name=6 then 1 else 0 end) as pos_count,
#           sum(case when  type_name in (6,8) then money else 0 end) as summary_money,
#           sum(case when  pos_model=4 then 1 else 0 end) as total_count,
#           sum(case when  type_name=8 then money else 0 end) as add_single_money,user_id %(where)s   
#    '''
    params={}
    id_part={}
    params['userids'] = userids
    params['st'] = begin_time
    params['et'] = end_time
    db_sql = get_sql("ic_report_sql",sqlid="ic_emp_summary_report_sql",app = "pos",params = params ,id_part = id_part )
#    db_sql = sql%({'where':" from pos_icconsumerlist where  user_id in (%s) and pos_time>='%s' and pos_time <'%s'  group by user_id"%(userids,begin_time,end_time)})
    return db_sql


#现金收支汇总
def ic_SZ_summary_report(st,et,check_opreate):
    sql = '''
        select
        sum(case when  type_id=1 then money else 0 end) as recharge_money,
        sum(case when  type_id=1 then 1 else 0 end) as recharge_count,
        sum(case when  type_id=5 then money else 0 end) as refund_money,
        sum(case when  type_id=5 then 1 else 0 end) as refund_count,
        sum(case when  type_id=7 then money else 0 end) as cost_money,
        sum(case when  type_id=11 then money else 0 end) as manage_money,
        sum(case when  type_id=7 then 1 else 0 end) as hairpin_count,
        sum(case when  type_id=4 then 1 else 0 end) as back_card_count,
        sum(case when  type_id=4 then money else 0 end) as back_card_money %(where)s   
    '''
#        sql='''
#            select
#            sum(case when  type_id=1 then money else 0 end) as recharge_money,
#            sum(case when  type_id=1 then 1 else 0 end) as recharge_count,
#            sum(case when  type_id=5 then money else 0 end) as refund_money,
#            sum(case when  type_id=5 then 1 else 0 end) as refund_count,
#            sum(case when  type_id=7 then money else 0 end) as cost_money,
#            sum(case when  type_id=11 then money else 0 end) as manage_money,
#            sum(case when  type_id=7 then 1 else 0 end) as hairpin_count,
#            sum(case when  type_id=4 then 1 else 0 end) as back_card_count,
#            sum(case when  type_id=4 then money else 0 end) as back_card_money %(where)s   
#            
#        '''
    params={}
    id_part={}
    params['st'] = st
    params['et'] = et
    if check_opreate == 'checked':
         id_part['where'] = "check_opreate"
#        sql_db = sql%({'where':" ,create_operator from pos_CarCashSZ where  checktime>='%s' and checktime <'%s' and  create_operator !='0' group by create_operator"%(st,et)})
#        union_sql='''
#        union all 
#        select 
#                        sum(case when  type_id=1 then money else 0 end) as recharge_money,
#                        sum(case when  type_id=1 then 1 else 0 end) as recharge_count,
#                        sum(case when  type_id=5 then money else 0 end) as refund_money,
#                        sum(case when  type_id=5 then 1 else 0 end) as refund_count,
#                        sum(case when  type_id=7 then money else 0 end) as cost_money,
#                        sum(case when  type_id=11 then money else 0 end) as manage_money,
#                        sum(case when  type_id=7 then 1 else 0 end) as hairpin_count,
#                        sum(case when  type_id=4 then 1 else 0 end) as back_card_count,
#                        sum(case when  type_id=4 then money else 0 end) as back_card_money,
#                        sn_name 
#        from pos_carcashsz where  checktime>='%s' and checktime <'%s' and create_operator='0' group by sn_name
#        '''%(st,et)
#        sql_db = sql_db + union_sql
    else:
         id_part['where'] = "not_check_opreate"
#        sql_db = sql%({'where':" from pos_carcashsz where  checktime>='%s' and checktime <'%s'"%(st,et)})
    db_sql = get_sql("ic_report_sql",sqlid="ic_SZ_summary_report",app = "pos",params = params ,id_part = id_part )
    return db_sql
