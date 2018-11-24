# -*- coding: utf-8 -*-

from sync_models import Device, Employee,FingerPrint,Face,EmployeePic,ObjectDoesNotExist, server_update
from sync_batchs import att_batch
from constant import DEVELOP_MODEL
import time

def set_info(pin,info_dic,call_sync=True):
    '''
    更新人员信息(只用于info的更新,区域的更新另作处理 如果是新人员则在redis中创建)
    call_sync 是否触发同步
    '''
    if DEVELOP_MODEL:print 'set_info...'
    try:
        e=Employee(pin)
        try:
            e=e.get()
        except ObjectDoesNotExist:
            pass
        e.sets(info_dic)
        if call_sync:
            e.call_sync(dev=False)
        return 0
    except:
        import traceback;traceback.print_exc()
        return u'操作失败'
        
def set_area(pin,area_list,call_sync=True):
    '''
    更新区域 (此操作会向老区域里下发del,向新区域下发info)
    call_sync 是否触发同步
    '''
    if DEVELOP_MODEL:print 'set_area...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        e.sync = call_sync
        m_list = [str(id) for id in area_list]
        e.set_areas(m_list)
        return 0
    except:
        return u'操作失败'

def get_area(pin):
    '''
    获得人员在redis中的区域
    '''
    e=Employee(pin)
    return e.get_area()

def set_FingerPrint(pin,fpversion,fid,data, call_sync=True,force=False):
    '''
    更新指纹 (主要供登记指纹的操作调用, 这里会将新指纹存储并触发sync同步到各设备) 
    '''
    if DEVELOP_MODEL:print 'set_FingerPrint...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        fp=FingerPrint(e.PIN, fpversion)
        m_key = 'fp%s'%int(fid)
        fp.init_counter()
        if data:
            setattr(fp, m_key , data)
            fp.set(m_key,force)
        if call_sync:
            fp.call_sync(dev=False)
        return 0 
    except:
        return u'操作失败'

def set_EmployeePic(pin,data,call_sync=True):
    '''
    更新用户照片 (这里会将新用户照片加载到redis, 并触发sync同步到各设备) 
    '''
    if DEVELOP_MODEL:print 'set_EmployeePic...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        pic = EmployeePic(e.PIN)
        pic.init_counter()
        if data:
            pic.data = data
            pic.set("data")
        if call_sync:
            pic.call_sync(dev=False)
        return 0
    except:
        return u'操作失败'

def set_Face(pin,face_ver, fid, data, call_sync=True):
    '''
    更新指纹 (目前暂无客户端界面登录面部,功能 这里会将新面部存储并触发sync同步到各设备) 
    '''
    if DEVELOP_MODEL:print 'set_Face...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        fc=Face(e.PIN, face_ver)
        m_key = 'face%s'%int(fid)
        fc.init_counter()
        if data:
            setattr(fc, m_key , data)
            fc.set(m_key)
        if call_sync:
            fc.call_sync(dev=False)
        return 0
    except:
        return u'操作失败'
    
def del_Employee(pin):
    '''
    删除人员(此操作会删除redis中该人员的所有数据 触发机器删除该人员
    并删除对应的指纹,面部和人员照片的本地存储和设备存储)
    '''
    if DEVELOP_MODEL:print 'del_Employee...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        e.delete()
        del_FingerPrint(e.PIN)
        del_Face(e.PIN)
        del_EmployeePic(e.PIN)
        return 0
    except:
        return u'操作失败'

def del_FingerPrint(pin):
    '''
    删除人员指纹
    '''
    if DEVELOP_MODEL:print 'del_FingerPrint...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        FingerPrint.deletes(e.getoo(),e.PIN)
        return 0
    except:
        return u'操作失败'

def del_EmployeePic(pin):
    '''
    删除人员照片
    '''
    if DEVELOP_MODEL:print 'del_EmployeePic...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        ep=EmployeePic(e.PIN)
        ep.delete()
        #磁盘操作
        return 0
    except:
        return u'操作失败'

def del_Face(pin):
    '''
    删除人员面部
    '''
    if DEVELOP_MODEL:print 'del_Face...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        Face.deletes(e.getoo(),e.PIN)
        return 0
    except:
        import traceback; traceback.print_exc()
        return u'操作失败'

def get_FingerPrint_count(pin):
    '''
    获取指纹数 
    '''
    e=Employee(pin)
    return e.getc_fp()
    
def get_face_count(pin):
    '''
    获取面部数
    '''
    e=Employee(pin)
    return e.getc_face()

######################## 数据修整操作(一般情况下不需要做这些操作) ################

def spread_FingerPrint(pin):
    '''
    重新分发人员指纹
    '''
    if DEVELOP_MODEL:print 'spread_FingerPrint...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        fp=FingerPrint(e.PIN,'10')
        #读取磁盘数据到redis
        fp.call_sync(dev=False)
        return 0
    except:
        return u'操作失败'
    

def spread_EmployeePic(pin):
    '''
    重新分发人员照片
    '''
    if DEVELOP_MODEL:print 'spread_EmployeePic...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        ep=EmployeePic(e.PIN)
        #读取磁盘数据到redis
        ep.call_sync(dev=False)
        return 0
    except:
        return u'操作失败'

def spread_face(pin):
    '''
    重新分发人员面部
    '''
    if DEVELOP_MODEL:print 'spread_face...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        fc=Face(e.PIN,'7')
        fc.call_sync(dev=False)
        #读取磁盘数据到redis
        return 0
    except:
        return u'操作失败'

def spread_employee(pin):
    '''
    重新分发人员 (基本信息、指纹、面部)
    '''
    if DEVELOP_MODEL:print 'spread_employee...'
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        return u'人员不存在'
    try:
        e.call_sync(dev=False)
        time.sleep(0.01)
        fp=FingerPrint(e.PIN,'10')
        fp.call_sync(dev=False)
        time.sleep(0.01)
        fc=Face(e.PIN,'7')
        fc.call_sync(dev=False)
        time.sleep(0.01)
        ep=EmployeePic(e.PIN)
        ep.call_sync(dev=False)
        #读取磁盘数据到redis
        return 0
    except:
        return u'操作失败'

######################## 针对设备的一些操作(命令) ################
def _device_cmd(sn,cmd):
    '''
    下发设备命令
    '''
    if DEVELOP_MODEL:print 'device_cmd: ',cmd
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist: #---设备没有登记过
        return u'设备未注册'
    try:
        device.add_cmd(cmd)
        return 0
    except:
        return u'操作失败'
    
def set_device(sn,info_dic):
    '''
    注册和更新设备信息
    '''
    if DEVELOP_MODEL:print 'set_device...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    try:
        device=Device(m_sn)
        try:
            device=device.get()
        except ObjectDoesNotExist:
            pass
        if info_dic.has_key('area'):
            m_area = info_dic.pop('area')
        device.sets(info_dic)
        if m_area:
            device.set_area(m_area)
        return 0
    except:
        import traceback;traceback.print_exc()
        return u'操作失败'

def del_device(sn):
    '''
    删除设备
    '''
    if DEVELOP_MODEL:print 'del_device...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
        return u'设备未注册'
    try:
        device.set_area('')
        device.delete()
        return 0
    except:
        return u'操作失败'
    

def clean_attpic(sn):
    '''
    清除考勤照片
    '''
    return _device_cmd(sn,"CLEAR PHOTO")
    
def clean_att(sn):
    '''
    清除考勤记录
    '''
    return _device_cmd(sn,"CLEAR LOG")
    
def clean_data(sn):
    '''
    清除所有数据
    '''
    return _device_cmd(sn,"CLEAR DATA")

def check_data(sn):
    '''
    清除所有数据
    '''
    return _device_cmd(sn,"CHECK")
    
def reboot_device(sn):
    '''
    重启设备
    '''
    return _device_cmd(sn,"REBOOT")
    
def get_info(sn):
    '''
    重新获取设备信息
    '''
    return _device_cmd(sn,"INFO")

def collect_device_employee(sn):
    '''
    重新收集人员 (基本信息和指纹)
    '''
    if DEVELOP_MODEL:print 'collect_device_employee...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
        return u'设备未注册'
    device.oplog_stamp='0'
    device.set("oplog_stamp")
    check_data(device.sn)
    return 0
    
def collect_device_att(sn):
    '''
    重新收集考勤记录
    '''
    if DEVELOP_MODEL:print 'collect_device_att...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
        return u'设备未注册'
    device.log_stamp = '0'
    device.set("log_stamp")
    check_data(device.sn)
    return 0
    
def collect_device_data(sn):
    '''
    重新收集数据
    '''
    if DEVELOP_MODEL:print 'collect_device_data...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
        return u'设备未注册'
    try:
        device.oplog_stamp='0'
        device.set("oplog_stamp")
        device.log_stamp = '0'
        device.set("log_stamp")
        device.photo_stamp='0'
        device.set("photo_stamp")
        check_data(device.sn)
        return 0
    except:
        return u'操作失败'

def spread_device_employee(sn):
    '''
    重新分发人员 (基本信息和指纹)
    '''
    if DEVELOP_MODEL:print 'spread_device_employee...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
        return u'设备未注册'
    try:
        device.spread()
        return 0
    except:
        import traceback;traceback.print_exc()
        return u'操作失败'

def get_device_status(sn):
    '''
    获取设备状态
    '''
    import datetime
    from mysite.settings import MIN_REQ_DELAY as min_delay
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return False
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
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
    
def get_count_cmd(sn):
    '''
    获取设备任务
    '''
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return 0
    device=Device(m_sn)
    return device.count_cmd()
    
def clean_cache_data(sn):
    if DEVELOP_MODEL:print 'clean_cache_data...'
    try:
        m_sn = str(sn)
    except:
        print 'deive sn:%s is incorrect'%sn
        return u'设备序列号不合法'
    device=Device(m_sn)
    try:
        device=device.get()
    except ObjectDoesNotExist:
        device.clean_update()
        return u'设备未注册'
    device.clean_cache()
    return 0

def get_att_record_file():
    '''
    从文件中获取原始考勤数据
    '''
    from sync_store import load_att_file
    try:
        m_store, m_sn, m_list = load_att_file()
        dev = Device(m_sn).get()
    except:
        return None,None,None
    return dev,m_list,m_store

def get_att_record():
    '''
    获取原始考勤数据
    '''
    bat = att_batch()
    try:
        m_list = bat.get()
        dev = Device(bat.get_sn()).get()
    except:
        return None,None
    return dev,m_list

def init_att_batch():
    bat = att_batch()
    bat.init_data()

def server_update_data():
    '''
    获取web server需要更新的数据
    '''
    try:
        return server_update()
    except:
        import traceback;traceback.print_exc()
        return {'employee':[],'device':[]}
    
