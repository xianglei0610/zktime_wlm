# coding=utf-8
import datetime

from django.conf import settings
from commen_utils import server_time_delta, normal_state, normal_verify

from sync_models import Employee,ObjectDoesNotExist,DEVICE_CREATEUSER_FLAG
from sync_store import save_attrecord

def line_to_log(device, lines, event=True):
    '''
    处理一批考勤记录数据
    '''
    from mysite.personnel.models.model_emp import format_pin
    m_result=[]
    for line in lines:
        if line:
            flds = line.split("\t") + ["", "", "", "", "", "", "",""]
            #检查员工号码的合法性
            pin = flds[0]   #---第一个元素为人员编号
    
            logtime = datetime.datetime.strptime(flds[1], "%Y-%m-%d %H:%M:%S")  #---第二个元素为打卡时间
    
            #---检查考勤记录时间的合法性
    #        if event:
    #            if (now + datetime.timedelta(1, 0, 0)) < logtime: 
    #                print u"时间比当前时间还要多一天"
    #                return None
    #            if logtime<now-datetime.timedelta(days=settings.VALID_DAYS): 
    #                print u"时间比当前要早...天", settings.VALID_DAYS
    #                return None
        
            #根据考勤机的时区矫正考勤记录的时区，使之同服务器的时区保持一致
    #        if device.tz_adj <> None:
    #            count_minutes = None
    #            tz_adj = int(device.tz_adj)
    #            if abs(tz_adj)<=13:
    #                count_minutes = tz_adj*3600
    #            else:
    #                count_minutes = tz_adj*60
    #            logtime = logtime - datetime.timedelta(0, count_minutes) + server_time_delta() #UTC TIM
                
            attrecord = {"pin": format_pin(pin),
                                "checktime":logtime, 
                                "checktype":normal_state(flds[2]), 
                                "verifycode":normal_verify(flds[3]), 
                                "WorkCode":flds[4], 
                                "Reserved":flds[5],
                                "sn_name":device.sn}
            m_result.append(attrecord)
    rtn = save_attrecord(m_result,event)
    return rtn
            