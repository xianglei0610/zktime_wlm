# coding=utf-8
import datetime
import time
import os 

from mysite.personnel.models.model_emp import format_pin
from device_response import device_response_write

from django.conf import settings
from constant import DEVICE_CREATEUSER_FLAG, DEVICE_CREATEBIO_FLAG, DEVICE_CREATECARD_FLAG


from sync_models import Employee,FingerPrint,Face,EmployeePic,ObjectDoesNotExist

from commen_utils import card_to_num

def line_to_emp(cursor, device, line, Op,event=True):
    '''
    设备更新人员信息的总接口    
    line：设备post过来的命令字符串
    device：传送命令的设备
    '''
    try:    #---行数据以空格分割标志名和键值对数据
        if line.find("\tName=") > 0:
            ops = unicode(line.decode("gb18030")).split(" ", 1)
        else:
            ops = line.split(" ", 1)
    except:
        ops = line.split(" ", 1)

    if ops[0] == 'OPLOG':   #设备操作记录
        from sync_conv_device import line_to_oplog
        return line_to_oplog(device, ops[1])
    
    flds = {};  #获取行数据中包含的所有键值对
    for item in ops[1].split("\t"):
        index = item.find("=")
        if index > 0: flds[item[:index]] = item[index + 1:]
        
    try:#工号有效性验证
        pin = flds["PIN"]
        if len(pin)>settings.PIN_WIDTH:
            return
    except:
        return
    
    e=Employee(pin)
    try:
        e=e.get()
    except ObjectDoesNotExist:
        if not DEVICE_CREATEUSER_FLAG:
            return None
        e.EName = pin
        
    data_type = str(ops[0]).strip()
    ########################### 人员基本信息 #########################
    if data_type == "USER":
        if not DEVICE_CREATEUSER_FLAG:
            return
        try:
            ename = unicode(flds["Name"])[:40]
        except:
            ename = ''
        passwd = flds.get("Passwd","")
        if DEVICE_CREATECARD_FLAG:
            card = flds.get("Card", "")
        else:
            card = None
        vcard=card_to_num(card)
        agrp = flds.get("Grp", "")
        tz = flds.get("TZ","")
        priv = flds.get('Pri', 0)
        if ename:
            e.EName = ename
        if passwd:
            e.Password = passwd
        if priv:
            e.Privilege = str(priv)
        if card:
            e.Card = vcard
        if agrp:
            e.AccGroup = str(agrp)
        if tz:
            e.TimeZones = tz  
        e.set()#触发redis保存
        if e.isnew():
            e.set_area(device.area,dev=device.sn)#dev 用于指定不下发的设备
            e.call_sync(dev=device.sn,just=device.sn)# 只触发webserver 更新
        else:
            if device.area in e.get_area():
                e.call_sync(device.sn)#触发其他所有终端(包括webserver)更新
            else:
                e.set_area(device.area,dev=device.sn)
                e.call_sync(dev=device.sn,just=device.sn)# 只触发webserver 更新
        return True
    ########################### 人员指纹模板 #########################
    elif data_type == "FP":
        if not DEVICE_CREATEBIO_FLAG:
            return
        try:
            size=flds["Size"]            
            data = flds["TMP"]    
            d_len=len(data.decode("base64"))
            if data and (len(data)==int(size) or d_len==int(size) ):
                fp=FingerPrint(e.PIN,device.Fpversion or '10')
                m_key = 'fp%s'%int(flds["FID"])
                setattr(fp, m_key , data)
                try:
                    if e.isnew():   
                        e.set()
                        e.set_area(device.area,dev=device.sn)
                        e.call_sync(dev=device.sn,just=device.sn)
                    fp.set(m_key)#触发保存指纹到数据库
                    fp.call_sync(device.sn)#触发其他设备更新
                except:
                    import traceback;traceback.print_exc()
                    print 'sync error 201'
                return True
            else:
                print "template length error"
                return False
        except:
            import traceback; traceback.print_exc();
            return False            
    ########################### 人员人脸模板 #########################
    elif data_type == "FACE" :
        try:
            size=flds["SIZE"]
            data = flds["TMP"]  
            d_len=len(data.decode("base64"))
            if data and (len(data)==int(size) or d_len==int(size) ):
                fc=Face(e.PIN,device.face_ver or '7')
                m_key = 'face%s'%int(flds["FID"])
                setattr(fc, m_key , data)
                try:
                    if e.isnew():   
                        e.set()
                        e.set_area(device.area,dev=device.sn)
                        e.call_sync(dev=device.sn,just=device.sn)
                    fc.set(m_key)
                    fc.call_sync(device.sn)
                except:
                    import traceback;traceback.print_exc()
                    print 'sync error 202 '
                return True
            else:
                print "face length error"
                return False
        except:
            import traceback; traceback.print_exc();
            return False            
    ########################### 人员照片 #########################
    elif data_type == "USERPIC" :
        if device.alg_ver<'2.2.0':
            return
        try:
            userpin=flds["PIN"]
            filename=flds["FileName"]
            size =flds["Size"]
            pic = EmployeePic(e.PIN)
            pic.data = flds["Content"].decode('base64')
            try:
                if e.isnew():   
                    e.set()
                    e.set_area(device.area,dev=device.sn)
                    e.call_sync(dev=device.sn,just=device.sn)
                pic.set("data")
                pic.call_sync(device.sn)
            except:
                import traceback;traceback.print_exc()
                print 'sync error 203'
            return True
        except:
            import traceback; traceback.print_exc();
            return False 

def cdata_get_pin(request, device):
    '''
    请求中 带人员PIN参数时的处理 返回人员基本信息和指纹模板信息、删除人员
    涉及 http参数：pin、save 
    '''
    resp=""
    pin = request.REQUEST['PIN']
    #pin = format_pin(pin)
    try:
        emp=Employee(pin).get()
        emp_info = emp.get_info()
        emp_fp = ''#emp.get_fp()
        cc = emp_info + emp_fp
        try:
            resp += cc.encode("gb18030")
        except:
            resp += cc.decode("utf-8").encode("gb18030")
        return device_response_write(resp)
    except ObjectDoesNotExist: #---人员不存在
        return none_response()
