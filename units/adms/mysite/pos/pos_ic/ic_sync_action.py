# -*- coding: utf-8 -*-

from ic_sync_batch import ic_pos_batch
from ic_sync_model import PosDeviceDoesNotExist
from mysite.pos.pos_constant import IS_DISTRIBUTED
import datetime
def get_pos_record():
    '''
    获取原始消费数据
    '''
    bat = ic_pos_batch()
    try:
        if IS_DISTRIBUTED:
            m_list = bat.get_is_sistributed()#分布式情况
        else:
            m_list = bat.get()#非分布式情况
        head_data = bat.get_head_data()
#        dev = Device(bat.get_sn()).get()
    except:
        import traceback;traceback.print_exc()
        return None,None
    return head_data,m_list

def init_pos_batch():
    bat = ic_pos_batch()
    bat.init_data()


def pos_ic_write_data(head_data,raw_data, device=None,Op=None):
    from mysite.pos.pos_ic.ic_pos_devview import get_device,cdata_post_trans,conn
    from django.core.exceptions import ObjectDoesNotExist
    from django.db.backends.sqlserver_ado.dbapi import OperationalError,InternalError,ProgrammingError
    import time
#    head_data, raw_data=raw_data.split("\n",1)
    stamp_name, head=head_data.split(": ")
    stamp_name=stamp_name[1:]
    head=dict([item.split("=",1) for item in head.split("\t")])
    bat = ic_pos_batch()
    if device is None:
        try:
            cursor = conn.cursor()
            device=get_device(head['SN'])
        except ObjectDoesNotExist:
            print u"设备不存在========>>>>>>>",datetime.datetime.now()
            bat.del_oo_item() #找不到设备的记录直接跳过
            time.sleep(10)
            pass
#            bat.del_oo_item() #找不到设备的记录直接跳过
        except(OperationalError,InternalError):
            time.sleep(120)
            print u"数据库连接失败=======pos_ic_write_data>%s",datetime.datetime.now()
            import traceback;traceback.print_exc()
            return
            
    msg=None
    c=0
    ec=0
    
    if device:
        c, ec, msg,db_contion_error=cdata_post_trans(device, raw_data,stamp_name, head,head_data)
    
        if not IS_DISTRIBUTED and not db_contion_error:#不做分布式部署情况
            bat.del_oo_item()                   
#    print u"成功解析设备上传数据===",msg
    #写入上传记录日志表
#    if msg is not None:
#        try:
#            DevLog(SN=device, Cnt=c, OP=stamp_name, ECnt=ec, Object=msg[:20], OpTime=datetime.datetime.now()).save(force_insert=True)
#        except:
#            print_exc()
#    return (c, ec+c, msg)


def init_ic_pos_device(device):
    '''
    初始化设备信息
    '''
    from mysite.pos.pos_ic.ic_sync_model import Pos_Device
    import datetime
    m_dict = {}
    m_dict["sn"] = device.sn
    m_dict["pos_log_stamp_id"] = device.pos_log_stamp_id
    m_dict["full_log_stamp_id"] = device.full_log_stamp_id
    m_dict["allow_log_stamp_id"] = device.allow_log_stamp_id
    m_dict["pos_log_bak_stamp_id"] = device.pos_log_bak_stamp_id
    m_dict["full_log_bak_stamp_id"] = device.full_log_bak_stamp_id
    m_dict["allow_log_bak_stamp_id"] = device.allow_log_bak_stamp_id
    m_dict["pos_dev_data_status"] = device.pos_dev_data_status
    
    m_dict["pos_all_log_stamp"] = device.pos_all_log_stamp or 0
    m_dict["pos_log_stamp"] = device.pos_log_stamp or 0
    m_dict["full_log_stamp"] = device.full_log_stamp or 0 
    m_dict["allow_log_stamp"] = device.allow_log_stamp or 0 
    m_dict["last_activity"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r_device=Pos_Device(device.sn)
    r_device.sets(m_dict)
    
    
def get_pos_device_status(sn):
    '''
    获取设备状态
    '''
    from mysite.pos.pos_ic.ic_sync_model import Pos_Device
    from mysite.settings import MIN_REQ_DELAY as min_delay
    import datetime
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return False
    device=Pos_Device(m_sn)
    try:
        device=device.get()
    except PosDeviceDoesNotExist:
        return False
    try:
        last_activity_str = device.get("last_activity")
    except:return False
    if last_activity_str:
        last_activity = datetime.datetime.strptime(last_activity_str, "%Y-%m-%d %H:%M:%S")
    else:
        return False
    '''小于设置的时间+1分钟之内为联机状态'''
    if (datetime.datetime.now() - last_activity).seconds < min_delay+60:
        return True
    else:
        return False

    
