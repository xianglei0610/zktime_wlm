#coding=utf-8
from mysite.sql_utils import get_sql
#设备汇总查询
def get_id_device_query(device_sn,begin_time,end_time):
#    sql="select user_id,card,cardserial,money,blance,checktime,create_operator from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["device_sn"] = device_sn
    sql = get_sql("id_posdevview_sql",sqlid="get_id_device_query",app = "pos",params = params ,id_part = id_part )
    return sql

#个人汇总查询
def get_id_emp_query(card,begin_time,end_time,device_sn):
#    sql="select user_id,card,cardserial,money,blance,checktime,create_operator from pos_carcashsz where type_id='%s' and checktime>='%s' and checktime <'%s'  "%(type_id,begin_time,end_time)
    params={}
    id_part={}
    params["st"] = begin_time
    params["et"] = end_time
    params["card"] = card
    params["device_sn"] = device_sn
    sql = get_sql("id_posdevview_sql",sqlid="get_id_emp_query",app = "pos",params = params ,id_part = id_part )
    return sql
