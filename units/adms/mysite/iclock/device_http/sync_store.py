# -*- coding: utf-8 -*-
'''
此文件包含与通讯有关的文件系统或者数据库存取接口
'''
import os
import datetime
import time
import base64

from django.conf import settings
from mysite.sql_utils import p_query,p_execute,p_mutiexec,test_conn
from mysite.personnel.models.model_emp import format_pin 
from commen_utils import get_logger
from django.db import IntegrityError
import os

log_dir = settings.APP_HOME+"/tmp/deal_attrecord"
faild_dir = settings.APP_HOME+"/tmp/deal_attrecord/faild"

def write_log(wstr,filename,wdir):
    try:
        if not os.path.exists(wdir):
            os.mkdir(wdir)
        mfile='%s/%s'%(wdir,filename)
        f=open(mfile,'a')
        f.write(wstr)
        f.close()
    except:
        import traceback
        traceback.print_exc()
        pass

def att_deal_logger(str):
    filename="%s.log"%datetime.datetime.now().strftime("%Y_%m")
    str = '%s: %s\n'%(datetime.datetime.now(), str)
    write_log(str,filename,log_dir)
    
def att_deal_faild_accord(sn,data):
    filename = "%s_%s.dat"%(datetime.datetime.now().strftime("%Y_%m"),sn)
    write_log(data,filename,faild_dir)

def load_emp_fg(key):
    u"""
      根据人员 PIN 获取该人员指纹信息
    """
    pin, ver = key.split('|')
    pin = format_pin(pin)
    sql = """
        select FingerID,Template from finger_template
            where finger_template.pin = '%s' and finger_template.Fpversion= '%s'
    """%(pin,ver)
    temps = p_query(sql)
    res = {}
    if temps:
        for e in temps:
            res["fp"+str(e[0])] = e[1]
    else:
        res = None
    return  res

def load_emp_face(key):
    u"""
      根据人员 PIN 获取该人员面部信息
    """
    pin, ver = key.split('|')
    pin = format_pin(pin)
    sql = """
        select faceid,facetemp from face_template
            where face_template.pin = '%s' and face_template.face_ver = '%s'
    """%(pin,ver)
    temps = p_query(sql)
    res = {}
    if temps:
        for e in temps:
            res["face"+str(e[0])] = e[1]
    else:
        res = None
    return  res

def delete_finnger(pin):
    u"""
      根据人员 PIN 删除该人员指纹信息
    """
    pin = format_pin(pin)
    sql = """
        delete from finger_template
        where finger_template.pin = '%s'
    """%pin
    return p_execute(sql)

def delete_face(pin):
    u"""
      根据人员 PIN 删除该人员面部信息
    """
    pin = format_pin(pin)
    sql = """
        delete from face_template
        where face_template.pin = '%s'
    """%pin
    return p_execute(sql)

def save_attphoto(fname, raw_data, catalog=None):
        fname="model/%s/%s%s"%(\
                'iclock.Transaction', 
                catalog and catalog+"/" or "",
                fname or "")
        path = settings.ADDITION_FILE_ROOT+fname
        url = settings.ADDITION_FILE_URL+"/"+fname
        fn=os.path.split(path)
        try:
                os.makedirs(fn[0])
        except: pass
        f=file(path, "w+b")
        f.write(raw_data)
        f.close()
        return url
    
def save_finnger(key, field, data,force):
    '''
        保存指纹到数据库
    '''
    from mysite.iclock.models.model_bio import Template
    pin,ver = key.split('|')
    pin = format_pin(pin)
    fingger = field
    template = data
    Valid = force and "3" or "1"
    dict_val={
                  "pin":pin,
                  "FingerID":fingger,
                  "Fpversion":ver,
                  "template":template,
                  "Valid":Valid
              }
    sql_update ="""
         update 
                finger_template 
             set Template = '%(template)s',
                 Valid = %(Valid)s
        where 
             pin = '%(pin)s' and FingerID='%(FingerID)s' and Fpversion = '%(Fpversion)s' 
    """ %dict_val
    
    sql_insert = """
        insert into 
            finger_template (pin,Template,FingerID,Fpversion,Valid) 
            values('%(pin)s','%(template)s','%(FingerID)s','%(Fpversion)s',%(Valid)s)
    """ % dict_val
    res = p_execute(sql_update)
    if res == 0 :
        res = p_execute(sql_insert)
    return res
    
def save_face(key,field,data):
    u'''
        保存面部到数据库
    '''
    from mysite.iclock.models import FaceTemplate
    
    pin,ver = key.split('|')
    pin = format_pin(pin)
    faceid = field
    template = data
    dict_val={
                  "pin":pin,
                  "faceid":field,
                  "face_ver":ver,
                  "template":template
              }
    sql_update ="""
         update 
                face_template 
             set facetemp = '%(template)s'
        where 
             pin = '%(pin)s' and faceid='%(faceid)s' and face_ver = '%(face_ver)s' 
    """ %dict_val
    
    sql_insert = """
        insert into 
            face_template (pin,facetemp,faceid,face_ver) 
            values('%(pin)s','%(template)s','%(faceid)s','%(face_ver)s')
    """ % dict_val
    res = p_execute(sql_update)
    if res == 0 :
        res = p_execute(sql_insert)
    return res

        
    
def save_attrecord(att_dict_list,event=True):
    '''
    保存考勤原始记录到数据库 , 格式
    [
        {
        "pin": format_pin(pin),
        "checktime":logtime, 
        "checktype":normal_state(flds[2]), 
        "verifycode":normal_verify(flds[3]), 
        "WorkCode":flds[4], 
        "Reserved":flds[5],
        "sn_name":device.sn
        },
    ]
    realtime:
        True:  设备实时上传过来的数据
        False: 文件解析过来的数据 
    '''
    if att_dict_list:
        insert_sql = """
            if not exists(select id from checkinout where pin = '%(pin)s' and checktime= '%(checktime)s') 
            insert into checkinout (pin, checktime, checktype, verifycode, WorkCode, Reserved,sn_name) 
                            values('%(pin)s', '%(checktime)s', '%(checktype)s','%(verifycode)s', '%(WorkCode)s', '%(Reserved)s', '%(sn_name)s'); 
        """                 
        batch_sql = []
        for ad in att_dict_list:
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
    
def get_photourl_by_uid(uid):
    photo_select = """
        select photo from userinfo where userid = %s 
    """%uid
    res = p_query(photo_select) 
    return res and res[0][0] or None
    
def save_EmployeePic(key, data):
    u'''
    处理设备上传过来的照片
    '''
    pin = format_pin(key)
    empid = check_employee(pin)
    old_photo = get_photourl_by_uid(empid)
    update_sql = """
        update userinfo set photo= '%s' where userid = %s
    """
    content = data
    try:  
        savepath = "photo/" +datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")+".jpg"
        photopath = settings.ADDITION_FILE_ROOT +savepath
        f=file(photopath, "w+b")
        f.write(content)
        f.close()
        p_execute(update_sql%(savepath,empid))
        # 删除旧的照片
        if old_photo:
            oldpath = settings.ADDITION_FILE_ROOT +old_photo
            os.remove(oldpath)
    except:
        import traceback; traceback.print_exc()
        pass

def get_photo_by_pin(pin):
    select_sql = """
       select photo from userinfo where  badgenumber = '%s' 
    """%(format_pin(pin))
    res = p_query(select_sql) 
    return res and res[0][0] or None 

def load_emp_pic(key):
    u"""
      根据人员 PIN 获取该人员照片
    """
    import base64
    pin = key
    pin = format_pin(pin)
    photo=get_photo_by_pin(pin)
    if photo:
        e = settings.ADDITION_FILE_ROOT+photo
        try:
            f = open(e,'rb')
            base64_photo=base64.b64encode(f.read())
            f.close()
        except:
            import traceback; traceback.print_exc()
            return None
        len_photo = len(base64_photo)
        if len_photo>16*1024/0.75:
            print 'sync error 106'
            return  None
        else:
            return {'data':base64_photo}
    else:
        return None

def load_att_file(f=None):
    '''
    从文件中加载考勤记录
    '''  
    path=settings.C_ADMS_PATH%u"zkatt"
    if f:
        try:
            fs=open(f,"r+")
            data=fs.read()
            m_data = base64.decodestring(data).splitlines()
            fs.close()
            return None,None,m_data
        except:
            return None,None,None
    files = os.listdir(path)
    m_fn = None
    m_data = []
    if len(files)>0:
        m_fn = files[0]
        fs=open(path+m_fn,"r+")
        data=fs.read()
        m_data = base64.decodestring(data).strip().splitlines()                  
        fs.close()
        sn = m_fn.split('-')[0]
        return path+m_fn, sn, m_data
    else:
        return None,None,None

def save_att_file(sn,data):
    '''
    保存考勤记录到文件
    '''
    import datetime
    tnow=datetime.datetime.now()
    m_f=("000"+str(tnow.microsecond/1000))[-3:]
    filename=sn+'-'+tnow.strftime("%Y%m%d%H%M%S")+m_f+".dat"
    path=settings.C_ADMS_PATH%u"zkatt"
    if not os.path.exists(path):
        os.makedirs(path)
    f= file(path+filename,"a+")
    f.write(base64.encodestring(data))
    f.close()
    
def save_area(eid,epin):
    '''
    将人员的redis区域信息保存到数据库
    '''
    from mysite.iclock.models import Area
    from sync_action import get_area
    from protocol_content import device_pin
    pin = device_pin(epin)
    m_list = get_area(pin)
    delete_sql="""
      delete  userinfo_attarea where employee_id = %s
    """
    insert_sql = """
        if not exists(select id from userinfo_attarea where employee_id = %(employee_id)s and area_id= %(area_id)s) 
        insert into userinfo_attarea (employee_id,area_id) values(%(employee_id)s,%(area_id)s)
    """
    sqlList = []
    p_execute(delete_sql%eid)
    for a in m_list:
        p_execute(insert_sql%{'employee_id':eid,'area_id':a})
    
def get_uid_by_pin(pin):
    select_sql = """
        select userid from userinfo where badgenumber = '%s'
    """ %(format_pin(pin))
    res = p_query(select_sql) 
    return res and res[0][0] or None
    
def check_employee(pin):
    '''
    检测人员外键不存在则将人员新增到数据库
    '''
    uid = get_uid_by_pin(pin)
    if not uid:
        uid = save_addition_emp(pin)
    return uid

def save_addition_emp(pin):
    '''
    将人员新增到数据库
    '''
    from mysite.personnel.models import Employee    
    pin = format_pin(pin)
    emp = Employee()
    emp.PIN = pin
    emp.EName = ''#str(pin)
    emp.DeptID_id=1
    emp.from_dev = True
    try:
        super(Employee,emp).save()
        eid = emp.id
    except IntegrityError:
        eid=get_uid_by_pin(pin)
    finally:
#        '''保存区域'''
        save_area(eid,pin)
        return  eid