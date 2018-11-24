#! /usr/bin/env python
#coding=utf-8
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from traceback import print_exc
from django.utils import simplejson 
import datetime
from django.utils.translation import ugettext_lazy as _
import dict4ini, os
from django.db import connection
from models.model_report import ReportManage

#处理访客参数信息
@login_required
def process_visitor_option(request):
    func = request.GET.get("func", "")
    cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini", values={"visitor":{"time_length":5, "time_table":3, "times":3, "is_warn":1, "photo_path": "D:\\trunk\\units\\adms\\files\\photo"}}) #初始化访客参数初始值
    if func == "set_option":#设置信息
        try:
            cfg.visitor.time_length = request.POST.get("time_length", "")
            cfg.visitor.time_table = request.POST.get("time_table", "")
            cfg.visitor.times = request.POST.get("times", "")
            cfg.visitor.is_warn = request.POST.get("is_warn", "")
            cfg.visitor.is_warn = request.POST.get("photo_path", "")
            cfg.save()
            return HttpResponse(smart_str(simplejson.dumps({"ret": 0})))
        except:
            return HttpResponse(smart_str(simplejson.dumps({"ret": -1})))#未知错误
        
    if func == "get_option":#获取信息
        param_info = {
                "time_length": cfg.visitor.time_length,
                "time_table": cfg.visitor.time_table,
                "times": cfg.visitor.times,
                "is_warn": cfg.visitor.is_warn,
                "photo_path": cfg.visitor.photo_path,
        }
        return HttpResponse(smart_str(simplejson.dumps(param_info)))
   

#获取参数:来访时长
@login_required
def get_visitor_option():
    time_length = get_appconfig_value("visitor", "time_length")
    return int(time_length)


##读取图片的保存路径
#@login_required
#def get_photo_save_path(request):
#    print '---ddfdfdfd----'
#    func = request.GET.get("func", "")
#    cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini", values={"photo":{"photo_path": "D:\\trunk\\units\\adms\\files\\photo"}}) #初始化访客参数初始值
#    photo_path = {}
#    if func == "photo_path":
#        #photo_path["photo_path"] = cfg.photo.photo_path
#    print '---photo_path=', photo_path
#    return HttpResponse(smart_str(simplejson.dumps(photo_path)))

    

#根据键值读取attsite文件
@login_required
def get_appconfig_value(p_key, key):
    from django.conf import settings
    import dict4ini

    current_path = settings.APP_HOME
    app_config = dict4ini.DictIni(current_path+"/appconfig.ini")
    return app_config[p_key][key]


#获取进入登记的人员
@login_required
def get_visitor_in():
    cursor = connection.cursor()
    sql = "select distinct pin, enter_time from visitor_manage where visit_state=1 and is_alarm=0"#查出所有访客的编号和进入时间
    cursor.execute(sql)
    connection.close()
    
    alarm_pin_set = []#需要监控的访客编号
    alarm_time_list = []#需要监控的来访时间
    time_length = get_visitor_option()
    try:
        for emp in cursor.fetchall():
            emp = list(emp)
            alarm_time = emp[1] + datetime.timedelta(hours=time_length)#缓存中存储报警时间：进入时间+来访时长
            alarm_pin_set.append(int(emp[0]))
            alarm_time_list.append(alarm_time)
    except Exception, e:
        print_exc()
        pass

    if alarm_pin_set:
        ret = {
            "alarm_pin_set": alarm_pin_set,
            "alarm_time_list": alarm_time_list,
        }
        return ret
    else:
        return {}

##按访客编号获取访客来访信息
#@login_required
#def get_visitor_by_pin(pin):
#    visitor = None
#    try:
#        cursor = connection.cursor()
#        sql = "select u.name, v.pin, u.card, v.visit_company, v.visit_reason, v.visit_number, v.place, v.visit_time from visitor_manage as v, userinfo as u where v.pin=u.badgenumber and v.pin=%s"%pin
#        cursor.execute(sql)
#        visitor = cursor.fetchone()
#    except Exception, e:
#        print '----get_visitor_by_pin---e=',e
#    finally:
#        connection.close()
#    
#    return visitor

#向报表插入记录
def add_record_to_report(alarm_info):
#    report = ReportManage()
#    report.visited_person_pin = "test" #被访人姓名
#    report.visited_person = "test" #被访人姓名
#    report.dept = "test"
#    report.title = "test"
#
#    report.visitor_pin = alarm_info["pin"]
#    report.visitor = alarm_info["name"]#访客姓名
#    report.card = alarm_info["card"]#访客的卡号
#    report.visitor_company = alarm_info["visit_company"]#来访单位
#    report.visit_reason = alarm_info["visit_reason"]#来访事由
#    report.visit_number =  alarm_info["visit_number"]#来访人数
#    report.visit_time = alarm_info["visit_time"]#来访时间
#    report.visit_state = 3#来访状态为来访超时
#    report.place = alarm_info["place"]#来访地点
#    #report.is_overtime = 1 #来访超时
#    report.save()
    pass

#按被访人编号获取被访人信息
@login_required
def get_visited_emp(request):
    from mysite.personnel.models import Employee
    emp_id = request.GET.get("emp_id", "")
   # print '----emp_id=', emp_id
    emp_info = {}
    try:
        emp = Employee.objects.get(id=emp_id)
        emp_info["emp_id"] = emp.id
        emp_info["dept"] = emp.DeptID.name
        emp_info["name"] = emp.EName
        emp_info["ophone"] = emp.Tele
        #print '------emp_ifno===',emp_info
      
    except Exception, e:
        print '--get_visited_emp--ee==', e
    return HttpResponse(smart_str(simplejson.dumps(emp_info))) 

#自动生成访客编号
@login_required
def get_visitor_pin(request):
    cursor = connection.cursor()
    try:
        sql = "select max(badgenumber) from userinfo"
        cursor.execute(sql)
        connection.close()
        pin = cursor.fetchone()
        if pin[0] == None or pin[0] == "":
            pin = 1
        else:
            pin = int(pin[0]) + 1
        #print '-----get_visitor_pin--pin-==',pin
        return HttpResponse(smart_str(simplejson.dumps({"pin": pin})))        
    except Exception, e:
        print '----get_visitor_pin---e==',e
    finally:
        connection.close()

#统计当日进入的人数、离开的人数和未离开的人数
@login_required
def get_total_info(request):
    date = datetime.date.today()
    cursor = connection.cursor()
    #获取当日进入的次数、人数
    sql = '''select count(visitor_pin), sum(visitor_number) from visitor_manage where enter_time > '%s' union \
        select count(visitor_pin), sum(visitor_number) from visitor_manage where visit_state=2 and leave_time > '%s'
    '''%(date, date)
    cursor.execute(sql)
    total = cursor.fetchall()
    connection.close()

    temp = []
    times = None
    number = None
    for info in total:
        if info[0]:
            times = int(info[0])
        else:
            times = 0
        if info[1]:
            number = int(info[1])
        else:
            number = 0
        temp.append(times)
        temp.append(number)
    if len(total) == 1:
        temp.append(times)  
        temp.append(number)

    visitor_in_out_info = {
        "enter_times_total": temp[0],#进入的总次数
        "enter_number_total": temp[1],#进入的总人数
        "leave_times": temp[2],#离开的次数
        "leave_number": temp[3],#离开的人数
        "surplus_times": temp[0] - temp[2],#未离开的次数
        "surplus_number": temp[1]- temp[3],#未离开的人数
    }
    return HttpResponse(smart_str(simplejson.dumps(visitor_in_out_info)))      
    

#访客编辑时渲染选项
@login_required
def get_visitor_by_edit(request):
    from mysite.visitor.models import VisitorManage
    
    certificate_number = request.GET.get("c_number", "")
    #print 'certificate=====', certificate_number
    visitor_info_dict = {}
    try:
        sql = "select e.name, e.gender, e.homeaddress, v.visitor_pin, v.entrance from userinfo e, visitor_manage v where e.badgenumber=v.visitor_pin and v.certificate_number='%s'"%certificate_number
        #print '-----sql==',sql
        cursor = connection.cursor()
        cursor.execute(sql)
        visitor_info = cursor.fetchall()[0]
        visitor_info_dict["visitor_name"] = visitor_info[0]
        visitor_info_dict["gender"] = visitor_info[1]
        visitor_info_dict["home_address"] = visitor_info[2]
        visitor_info_dict["visitor_pin"] = visitor_info[3]
        visitor_info_dict["entrance"] = visitor_info[4]
        
        visitor = VisitorManage.objects.filter(certificate_number=certificate_number)[0]
        if visitor.visited_emp:
            visitor_info_dict["visited_name"] = visitor.visited_emp.EName
            visitor_info_dict["dept"] = visitor.visited_emp.DeptID.name
            visitor_info_dict["tele"] = visitor.visited_emp.Tele
            visitor_info_dict["visited_emp_id"] = visitor.visited_emp.id

    except:
        pass
    finally:
        if connection:
            connection.close()
    return HttpResponse(smart_str(simplejson.dumps(visitor_info_dict)))      


#新增访客，按证件号或者卡号判断是否有来访历史记录
@login_required
def get_visitor_by_add(request):
    func = request.GET.get("func", "")
    number = request.GET.get("number", "")
    visitor_info_dict = {}
    cursor = connection.cursor()
    try:
        #print '-------func=', func
        if func == "c_number":#证件登记，证件上基本的信息都有，只需获取访客原有的编号、单位、车牌号
            sql = "select visitor_pin, visitor_company, car_number from visitor_manage where certificate_number='%s'"%number
            #print '----sql==', sql
            cursor.execute(sql)
            visitor_info = cursor.fetchall()
            if visitor_info:
                visitor_info = visitor_info[0]
                #print '-----visitor_info[0]==', visitor_info[0]
                visitor_info_dict["visitor_pin"] = visitor_info[0]
                visitor_info_dict["company"] = visitor_info[1]
                visitor_info_dict["car_number"] = visitor_info[2]
#        elif func == "card":#常访卡登记
#            sql = ""
#            cursor.execute(sql)
#            visitor_info = cursor.fetchall()[0]
#            visitor_info_dict["visitor_pin"] = visitor_info[0]
#            visitor_info_dict["gender"] = visitor_info[1]
#            visitor_info_dict["home_address"] = visitor_info[2]
#            visitor_info_dict["visitor_pin"] = visitor_info[3]
#            visitor_info_dict["entrance"] = visitor_info[4]
    except Exception, e:
        print '----get_visitor_by_add==', e
    finally:
        if connection:
            connection.close()
    print visitor_info_dict
    return HttpResponse(smart_str(simplejson.dumps(visitor_info_dict))) 
    
    
    
    