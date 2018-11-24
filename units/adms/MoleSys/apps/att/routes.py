# coding = utf-8
from mole import route
from mole import request
from mole import response
from mole import redirect

@route('/manager/getDevInfo/', method='POST')
def getDevInfo():
    device_type =  request.params.get("device_type","1")
    from mosys.sql_utils import p_query
    sql = 'select sn,alias,ipaddress from iclock where device_type = %s'%device_type
    devs_list = p_query(sql)
    ret = {}
    ret["data"] = devs_list
    return ret