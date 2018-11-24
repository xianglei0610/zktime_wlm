# -*- coding: utf-8 -*-

import datetime

from mysite.sql_utils import p_query,p_execute,p_mutiexec

def save_attrecord(att_dict_list,event=True):
    '''
    保存考勤原始记录到数据库 
    realtime:
        True:  设备实时上传过来的数据
        False: 文件解析过来的数据 
    '''
    from mysite.personnel.models.model_emp import format_pin
    if att_dict_list:
        insert_sql = """
            if not exists(select id from checkinout where pin = '%(pin)s' and checktime= '%(checktime)s') 
            insert into checkinout (pin, checktime, checktype, verifycode, WorkCode, Reserved,sn_name) 
                            values('%(pin)s', '%(checktime)s', '%(checktype)s','%(verifycode)s', '%(WorkCode)s', '%(Reserved)s', '%(sn_name)s'); 
        """                 
        batch_sql = []
        for ad in att_dict_list:
            ad["pin"] = format_pin(pin)
            batch_sql.append(insert_sql%ad) 
        success,res = p_mutiexec(batch_sql)
        if not success:
            # 出现异常,一条一条插入:
            if res and res[0]==-2:
                att_deal_logger("Insert attrecord failed ,Database has been disconnected!")
                if event <> "files":
#                        # 数据库连接失败,导致数据没有插入,由设备直接传过来的数据,写成文件,返回 True
#                        data_list = []
#                        for d in att_dict_list:
#                            data_list.append(u"%s\t%s\t%s\t%s"%(d["pin"],d["checktime"],d["checktype"],d["verifycode"]))
#                        save_att_file(att_dict_list[0]["sn_name"],("\r\n").join(data_list))
                    time.sleep(2*60)  # 机器post 数据,如果服务器一段时间没有返回,则机器会默认为服务器没有收到,会再次post.
                    
                return False
            
            else:
                for bs in batch_sql:
                    num = p_execute(bs)
                    if num is None:
                        att_deal_logger("Error sql -->%s"%bs)
                        if event <> "files":
                            # 设备上传数据,数据异常导致保存失败
                            time.sleep(2*60)
                        return True
        return True


def line_to_log(device, lines, event=True):
    '''
    处理一批考勤记录数据
    返回 rtn 成功执行的条数
    '''
    from comm.commen_utils import normal_state, normal_verify
    m_result=[]
    for line in lines:
        if line:
            flds = line.split("\t") + ["", "", "", "", "", "", "",""]
            pin = flds[0]
            logtime = datetime.datetime.strptime(flds[1], "%Y-%m-%d %H:%M:%S")
            attrecord = {"pin": pin,
                                "checktime":logtime, 
                                "checktype":normal_state(flds[2]), #考勤状态
                                "verifycode":normal_verify(flds[3]), #验证方式
                                "WorkCode":flds[4], #工作号码
                                "Reserved":flds[5], #保留字段
                                "sn_name":device.sn}
            m_result.append(attrecord)
    rtn = save_attrecord(m_result,event)
    return rtn