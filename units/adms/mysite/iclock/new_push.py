#! /usr/bin/env python
#coding=utf-8
from mysite.personnel.models.model_emp import Employee,format_pin,device_pin
from django.conf import settings
import os
from mysite.iclock.models import DevCmd
import base64
import datetime
from traceback import print_exc
from ctypes import windll,create_string_buffer
from django.core.cache import cache
from models import Template
import cPickle
import time

FP_IDENTIFY_SUCCESS = 1     # 10.0指纹验证成功 
FP_NO_LICENCES = 2      # 10.0许可失败
CACHE_BIO_KEY = "all_bio_for_compare" 

def get_all_bio_from_cache():
    cache_bio = cache.get(CACHE_BIO_KEY)
    if cache_bio:
        print 'a'
        f = open(cache_bio)
        bio_data = cPickle.load(f)
        return bio_data
    else:
        print 'b'
        data = list(Template.objects.all())
        data_list = [(e.Template,e.UserID) for e in data]
        path = "%sall_bio_for_compare.cache"%settings.ADDITION_FILE_ROOT
        cache.set(CACHE_BIO_KEY,path,60*60*24*7)
        f = open(path,"w")
        cPickle.dump(data_list,f)
        return data_list
def compare_cache_bio_emp(tmp):
    try:
        mathpro = windll.LoadLibrary("match.dll")
        send_tmp = create_string_buffer(tmp.decode())
        cache_bio = get_all_bio_from_cache()
        print 'cache_bio:',len(cache_bio)
        for e in cache_bio:
            user_tep = create_string_buffer(e[0])
            math_result = mathpro.process10(user_tep, send_tmp)
            if math_result == FP_IDENTIFY_SUCCESS:
                return e[1]
    except:
        return None
    return None

def get_photo(photo,rstr):
    if photo:
        f = open(photo.file.name,'rb')#base64.b64encode(f.read())
        base64_photo=base64.b64encode(f.read())
        f.close()
        len_photo = len(base64_photo)
        if len_photo<=16*1024/0.75:
            rstr += '\tPhotoSize=%s\tPhoto=%s'%(str(len_photo),base64_photo)
    rstr +='\n'
    return rstr.encode("gb18030")

def verification(Auty,rawData,device):
    '''
    后台验证(后台比对)的几个方式
    '''
    xx=rawData.split("\t")
    data_dict={}
    for x in xx:
        d=x.split("=",1)
        data_dict[d[0]]=d[1]
    
    devpin=data_dict["PIN"]
    tmp = data_dict["TMP"]
    size = data_dict["Size"]
    if int(size) !=len(tmp):
        return 'AUTH=Failed\n'
    
    re_succ="AUTH=Success\tPIN=%s\tName=%s\tPri=%s\tGrp=%s\tTZ=%s"
    if Auty == 'CARD':####################卡比对
        emp = Employee.objects.filter(Card=tmp)
        if len(emp)>0:
            emp = emp[0]
        else:
            emp = None
        if devpin=='0':
            if emp:
                re_succ = re_succ%(device_pin(emp.PIN),emp.EName,str(emp.Privilege),str(emp.AccGroup),str(emp.TimeZones))
                return get_photo(emp.photo,re_succ)
        else:
            if emp.PIN==format_pin(devpin):
                re_succ = re_succ%(device_pin(emp.PIN),emp.EName,str(emp.Privilege),str(emp.AccGroup),str(emp.TimeZones))
                return get_photo(emp.photo,re_succ)
    elif Auty == 'FP':####################指纹比对
        if devpin=='0':
            emp = compare_cache_bio_emp(tmp)
            if emp:
                re_succ = re_succ%(device_pin(emp.PIN),emp.EName,str(emp.Privilege),str(emp.AccGroup),str(emp.TimeZones))
                return get_photo(emp.photo,re_succ)
#            emps = Employee.objects.all()
#            mathpro = windll.LoadLibrary("match.dll")
#            send_tmp = create_string_buffer(tmp.decode())
#            for emp in emps:
#                tmps =emp.template_set.all()
#                if tmps:
#                    for t in tmps:
#                        try:
#                            user_tep = create_string_buffer(t.Template)
#                            math_result = mathpro.process10(user_tep, send_tmp)
#                            if math_result == FP_IDENTIFY_SUCCESS:
#                                re_succ = re_succ%(device_pin(emp.PIN),emp.EName,str(emp.Privilege),str(emp.AccGroup),str(emp.TimeZones))
#                                return get_photo(emp.photo,re_succ)
#                        except:
#                            print_exc()
        else:
            emps = Employee.objects.filter(PIN=format_pin(devpin))
            if emps and len(emps)>0:
                emp = emps[0]
            else:
                return 'AUTH=Failed\t'
            tmps =Template.objects.filter(UserID=emp,Fpversion=device.Fpversion)
            mathpro = windll.LoadLibrary("match.dll")
            send_tmp = create_string_buffer(tmp.decode()) 
            for t in tmps:
                source_tmp = create_string_buffer(t.Template) 
                if device.Fpversion=='10':
                    math_result = mathpro.process10(source_tmp, send_tmp)
                else:
                    math_result = mathpro.process(source_tmp, send_tmp)
                if math_result == FP_IDENTIFY_SUCCESS:
                    re_succ = re_succ%(device_pin(emp.PIN),emp.EName,str(emp.Privilege),str(emp.AccGroup),str(emp.TimeZones))
                    return get_photo(emp.photo,re_succ)
    elif Auty == 'Face':####################面部模板比对
        pass
    else:
        pass
    return 'AUTH=Failed\t'



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
        photopath = settings.ADDITION_FILE_ROOT +savepath#settings.ADDITION_FILE_ROOT + "photo/" + e.PIN + ".jpg"
        f=file(photopath, "w+b")
        f.write(content)
        f.close()
        e.photo = savepath
        e.save()
    except:
        raise
    
def postuser_face(flds,e,device,Op):
    from models.model_face import FaceTemplate
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
#        print "size:%s   TMP size:%s"%(size,len(fp))
#        print "facetemplate length error"            
        
def debug_print(name,value):
    print '------------------------------------ %s [start] ---------------------------------'%name
    print value
    print '------------------------------------ %s [end]---------------------------------'%name    
        
def resolve_line(line,splitstr):
    try:
        if line.find("\tName=") > 0:
            ops = unicode(line.decode("gb18030")).split(" ", 1)
        else:
            ops = line.split(" ", 1)
    except:
        ops = line.split(" ", 1)
    flds = {};
    if len(ops)>1:
        for item in ops[1].split(splitstr):
            index = item.find("=")
            if index > 0: flds[item[:index]] = item[index + 1:]
    return (ops[0],flds)

def resolve_lines(line,splitstr):
    flds = {};
    if len(line)>1:
        for item in line.split(splitstr,3):
            index = item.find("=")
            if index > 0: flds[item[:index]] = item[index + 1:]
    return flds        
    
         

                        
                        
        
        
    
        
        


        