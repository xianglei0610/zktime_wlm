#coding=utf-8
from django.conf import settings
import datetime
import time
from mysite.iclock.models import  Template
from mysite.personnel.models.model_emp import Employee,format_pin
from db_utils import append_dev_cmd
from django.core.exceptions import ObjectDoesNotExist

from device_response import unknown_device_response,unknown_data_response,ok_response,device_response_write,none_response
from db_utils import get_employee
from mysite.utils import get_option
from mysite.iclock.models.modelproc import get_normal_card

def postuser_photo(data_dict,e,device):
    u'''
    处理设备上传过来的照片
    '''
    if device.alg_ver<'2.2.0':
        return
    from mysite.personnel.models import Employee
    userpin=data_dict["PIN"]
    filename=data_dict["FileName"]
    size =data_dict["Size"]
    content = data_dict["Content"].decode('base64')
    try:  
        savepath = "photo/" +datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")+".jpg"
        photopath = settings.ADDITION_FILE_ROOT +savepath
        f=file(photopath, "w+b")
        f.write(content)
        f.close()
        e.photo = savepath
        e.save()
    except:
        raise
    
def postuser_face(flds,e,device,Op):
    from mysite.iclock.models.model_face import FaceTemplate
    emps=e
    size=flds["SIZE"] #---数据长度            
    fp = flds["TMP"]  #---面部模板数据  
    d_len=len(fp.decode("base64"))
    if fp and (len(fp)==int(size) or d_len==int(size) ):
        devs=set(e.search_device_byuser())  #---获取该人员所在区域的所有设备
        if devs:
            try:
                devs.remove(device)
            except:
                pass
        e = FaceTemplate.objects.filter(user=e.id, faceid=int(flds["FID"]),face_ver=device.face_ver) #---得到面部模板对象
        if len(e)>0:
            e=e[0]
            if fp[:100] == e.facetemp[:100]:#----对比前100个字符
                pass # Template is same
            else:                        
                e.facetemp=fp
                #e.SN=device
                e.utime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                e.save()
                #-----同步到其他设备中去  这里需要不需要区分是不是人脸设备
                for dev in devs:
                    dev.set_user_face([emps], Op, int(flds["FID"]))
                    time.sleep(0.01)
                    
        else: #-----如果是新增的
            e=FaceTemplate()
            e.user=emps
            e.facetemp=fp
            e.utime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            e.faceid=int(flds["FID"])
            e.face_ver = device.face_ver
            e.valid=1
            e.save()
            for dev in devs:
                dev.set_user_face([emps], Op, int(flds["FID"])) #-------------------------自动更新到同区域的其他设备
                time.sleep(0.01)
        return True
    else:
        raise

def card_to_num(card):
    if card and len(card) == 12 and card[0] == '[' and card[-3:] == '00]':
        card = "%s" % (int(card[1:3], 16) + int(card[3:5], 16) * 256 + int(card[5:7], 16) * 256 * 256 + int(card[7:9], 16) * 256 * 256 * 256)
    return card

def line_to_emp(cursor, device, line, Op,event=True):
    '''
    解析设备命令    
    line：设备post过来的命令字符串
    device：传送命令的设备
    '''
    from mysite import settings
    import os
    try:    #---行数据以空格分割标志名和键值对数据
        if line.find("\tName=") > 0:
            ops = unicode(line.decode("gb18030")).split(" ", 1)
        else:
            ops = line.split(" ", 1)
    except:
        ops = line.split(" ", 1)

    if ops[0] == 'OPLOG':   #-------------管理员操作记录        ops[0] 为标志名
        from conv_device import line_to_oplog
        return line_to_oplog(cursor, device, ops[1], event)
    
    flds = {};  #-----------行数据中包含的所以键值对
    for item in ops[1].split("\t"):
        index = item.find("=")
        if index > 0: flds[item[:index]] = item[index + 1:]
        
    try:
        pin = flds["PIN"] #---得到用户编号
        if pin in settings.DISABLED_PINS or len(pin)>settings.PIN_WIDTH: #----用户编号有效性验证
            return
    except:
        return
    
    e = get_employee(pin, device)   #--- 得到命令对应的人员对象  必须有
    if not e:
        return
    if str(ops[0]).strip() == "USER":   #----------用户基本信息
        if not settings.DEVICE_CREATEUSER_FLAG:
            return 
        try:
            ename = unicode(flds["Name"])[:40]
        except:
            ename = ' '
        passwd = flds.get("Passwd","")
        card = flds.get("Card", "")
        tmp_card = "" #卡号保存在isssuecard里面
        agrp = flds.get("Grp", "")
        tz = flds.get("TZ","")
        priv = flds.get('Pri', 0)
        fldNames = ['SN', 'utime']
        values = [device.id, str(datetime.datetime.now())[:19]]
        if ename and (ename != e.EName):
            fldNames.append('name')
            values.append(ename)
            e.EName = ename
        from base.crypt import encryption#设备传过来的密码没加密   需要加密再和数据库中的比较
        if passwd and (encryption(passwd) != e.Password):
            fldNames.append('password')
            values.append(passwd)
            e.Password = passwd
        if priv and (str(priv) !=str(e.Privilege)):#考虑下数据字段类型
            fldNames.append('privilege')
            values.append(str(priv))
            e.Privilege = str(priv)
        if card and (card_to_num(card) != e.Card):
            if str(card_to_num(card)).strip()!="0":
                vcard=card_to_num(card)
            else:
                vcard=""
            fldNames.append('Card')
            values.append(vcard)
            tmp_card = vcard
        elif card=="" and e.Card:  #机器是否删除卡号
            fldNames.append('Card')
            values.append("")
            tmp_card = ""
        if agrp and (str(agrp) != str(e.AccGroup)):
            fldNames.append('AccGroup')
            values.append(str(agrp))
            e.AccGroup = str(agrp)
        if tz != e.TimeZones:
            fldNames.append('TimeZones')
            values.append(tz)
            e.TimeZones = tz
        try:
            e.IsNewEmp
        except:
            e.IsNewEmp = False
        if e.IsNewEmp:    #新增用户
            e.IsNewEmp = False     
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
            if tmp_card and not get_option("POS"):
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID
                obj_card = IssueCard()
                obj_card.UserID = e
                obj_card.cardno = tmp_card
                obj_card.cardstatus = CARD_VALID
                obj_card.save()
            devs=set(e.search_device_byuser()) 
            if devs:
                try:
                    devs.remove(device)
                except:
                    pass
            for dev in devs:
                dev.set_user([e], Op,"")
                dev.set_user_fingerprint([e], Op)
                time.sleep(0.01)    
            sql = ''
        elif len(fldNames) > 2: #有新的用户信息
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP
            devs=set(e.search_device_byuser()) 
            e.save()
            
            try:
                obj_card  = IssueCard.objects.get(UserID=e,cardno=tmp_card)  
            except:
                obj_card = None
            
                
                if not obj_card and not get_option("POS"):
                    try:
                        temp_card  = IssueCard.objects.get(UserID=e,cardstatus=CARD_VALID)  
                        temp_card.cardstatus = CARD_STOP     #停用之前的卡号
                        temp_card.save() 
                    except:
                        pass
                    if tmp_card:#卡处理
                        obj_card = IssueCard()
                        obj_card.UserID = e
                        obj_card.cardno = tmp_card
                        obj_card.cardstatus = CARD_VALID
                        obj_card.save()
                else:
                    if not get_option("POS"):#消费的时候不能覆盖
                        obj_card.cardno = tmp_card
                        obj_card.save()
            if devs:
                try:
                    devs.remove(device)
                except:
                    pass
            for dev in devs:
                dev.set_user([e], Op,"")
                dev.set_user_fingerprint([e], Op)
                time.sleep(0.01)
        else:
            pass
        return e
    
    elif str(ops[0]).strip() == "FP":   #----------------用户的指纹模板
        if not settings.DEVICE_CREATEBIO_FLAG:
            return
          
        if e.IsNewEmp:    #新增用户               
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
        emps=e
        try:
            size=flds["Size"]            
            fp = flds["TMP"]    
            d_len=len(fp.decode("base64"))
            if fp and (len(fp)==int(size) or d_len==int(size) ):
                devs=set(e.search_device_byuser())
                if devs:
                    try:
                        devs.remove(device)
                    except:
                        pass
                e = Template.objects.filter(UserID=e.id, FingerID=int(flds["FID"]),Fpversion=device.Fpversion)
                if len(e)>0:
                    e=e[0]
                    if fp[:100] == e.Template[:100]:
                        pass # Template is same
                    else:                        #指纹有修改
                        e.Template=fp
                        e.Fpversion=device.Fpversion
                        e.UTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        e.save()
                        for dev in devs:
                            dev.set_user_fingerprint([emps], Op, int(flds["FID"]))
                            time.sleep(0.01)
                else:     #新增指纹
                    e=Template()
                    e.UserID=emps
                    e.Template=fp
                    e.UTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    e.FingerID=int(flds["FID"])
                    e.Fpversion=device.Fpversion
                    e.Valid=1
                    e.save()
                    for dev in devs:
                        dev.set_user_fingerprint([emps], Op, int(flds["FID"]))
                        time.sleep(0.01)
                return True
            else:
                print "size:%s   TMP size:%s"%(size,len(fp))
                print "template length error"
        except:
            import traceback; traceback.print_exc();            
        else:
            return False
        
    elif str(ops[0]).strip() == "FACE" :    ######################## 新增人脸模板相关命令处理  ##################
        if e.IsNewEmp:    #-----保存设备新增用户的其他信息               
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
        emps=e
        try:
            postuser_face(flds,e,device,Op)
            return True
        except:
            import traceback; traceback.print_exc();            
        else:
            return False
    elif str(ops[0]).strip() == "USERPIC" :    #####################加入用户照片 处理
        if e.IsNewEmp:    #-----保存设备新增用户的其他信息               
            e.DeptID_id=1       
            e.attarea=(device.area,)
            e.save()
        emps=e
        try:
            postuser_photo(flds,e,device)
            return True
        except:
            import traceback; traceback.print_exc(); 
        else:
            return False

def fingerprint_data(pin,Fpversion):
    if type(pin)==type(u'type'):
        try:
            emp = Employee.objects.get(PIN=format_pin(pin))
        except ObjectDoesNotExist:
            return None
    else:
        emp = pin
    fingerprint = Template.objects.filter(UserID=emp,Fpversion=Fpversion)
    cc = u''
    for fp in fingerprint:
        try:
            cc += u"DATA FP PIN=%s\tFID=%d\tTMP=%s\n" % (emp.pin(), fp.FingerID, fp.temp())
        except:
            return None
    return cc

def face_data(emp,device):
    from mysite.personnel.models.emp_extend import get_face_from_emp
    from protocol_content import face_prot
    data = ''
    faces = get_face_from_emp(emp)
    for face in faces:
        if face.face_ver ==device.face_ver:
            data += face_prot(face)
    return data
     
def emp_info_data(pin):
    if type(pin)==type(u'type'):
        try:
            emp = Employee.objects.get(PIN=format_pin(pin))
        except ObjectDoesNotExist:
            return None
    else:
        emp = pin
    from base.crypt import encryption,decryption
    cc = u"DATA USER PIN=%s\tName=%s\tPasswd=%s\tGrp=%d\tCard=%s\tTZ=%s\tPri=%s\n" % (emp.pin(), emp.EName or "", decryption(emp.Password) or "", emp.AccGroup or 1, get_normal_card(emp.Card), emp.TimeZones or "", emp.Privilege or 0)
    return cc

def delete_emp_data(pin):
    endTime = datetime.datetime.now() + datetime.timedelta(0, 5 * 60)
    append_dev_cmd(device, "DATA DEL_USER PIN=%s" % emp.pin(), None, endTime)

def get_emp(pin):
    try:
        emp = Employee.objects.get(PIN=format_pin(pin))
        return emp
    except ObjectDoesNotExist:
        return None
    
def get_emp_from_card(card):
    '''根据卡号获取人员信息'''
    try:
        from mysite.personnel.models.model_issuecard import IssueCard, CARD_VALID,CARD_OVERDUE
        IssueCard.can_restore=True
        isobj=IssueCard.objects.get(cardno=card,cardstatus__in=[CARD_VALID,CARD_OVERDUE])
        IssueCard.can_restore=False
        if isobj :
            return Employee.objects.get(pk=isobj.UserID_id) 
    except:
        IssueCard.can_restore=False
        import traceback;traceback.print_exc()
    return None
        
def cdata_get_pin(request, device):
    '''
    请求中 带人员PIN参数时的处理 返回人员基本信息和指纹模板信息、删除人员
    涉及 http参数：pin、save 
    '''
    resp=""
#    save = request.REQUEST.has_key('save') and (request.REQUEST['save'] in ['1', 'Y', 'y', 'yes', 'YES']) or False
    pin = request.REQUEST.get('PIN', '')
    card = request.REQUEST.get('Card', '')
    Expect = request.REQUEST.get('Expect', '')
    emp = None
    if len(pin)>0:
        emp = get_emp(pin)
    elif len(card)>0:
        emp = get_emp_from_card(card_to_num(card))
    if emp:
        emp_info = emp_info_data(emp)
        if Expect=="FACE":
            f = face_data(emp,device)
        elif Expect=="USER":
            f = ""
        else:
            f = fingerprint_data(emp,device.Fpversion)
        cc = emp_info + f
        try:
            resp += cc.encode("gb18030")
        except:
            resp += cc.decode("utf-8").encode("gb18030")
#        if not save:
#            delete_emp_data(emp.pin())
        return device_response_write(resp)
    else:
        return ok_response()
