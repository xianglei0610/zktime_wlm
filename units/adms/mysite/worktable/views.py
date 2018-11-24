# -*- coding: utf-8 -*-
from django.http import HttpResponse
from dbapp.utils import getJSResponse
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.shortcuts import render_to_response
from dbapp.datautils import NoFound404Response
from dbapp.modelutils import GetModel
from mysite.worktable.models  import InstantMsg,GroupMsg,UsrMsg,MsgType
import datetime
from base.middleware import threadlocals
from django.utils.translation import ugettext as _
from django.conf import settings
import os
from django.db.models import Q
from threading import Event, Semaphore
from django.utils.encoding import force_unicode
import json

def Employee_objects(request):
    from dbapp.datautils import filterdata_by_user
    from mysite.personnel.models import Employee
    return filterdata_by_user(Employee.objects.all(),request.user) 


def outputEmpStructureImage(request):
    import os
    from mysite.personnel.models.model_emp import Employee
    
    type= request.GET.get("t","1")
    try:
        if type=="1":
            qs = list(Employee_objects(request).filter(Hiredday__isnull=False))
            if len(qs)==0:
                return getJSResponse(json.dumps([]))
            curr_dt =datetime.datetime.now()
            curr_date = datetime.date(curr_dt.year,curr_dt.month,curr_dt.day)
            ten_years=0
            eight_years=0
            five_years=0
            three_years=0
            two_years=0
            one_years=0
            for e in qs:
                hire_date= datetime.date(e.Hiredday.year,e.Hiredday.month,e.Hiredday.day)
                if (curr_date -hire_date).days >=365 *10:
                    ten_years+=1
                elif (curr_date -hire_date).days >=365 *8:
                    eight_years+=1
                elif (curr_date -hire_date).days >=365 *5:
                    five_years+=1
                elif (curr_date -hire_date).days >=365 *3:
                    three_years+=1
                elif (curr_date -hire_date).days >=365 *2:
                    two_years+=1
                elif (curr_date -hire_date).days <365 *2:
                    one_years+=1
            if not qs:
                one_years=100
            data = [
                        {"label":_(u'十年 ') + str(ten_years),"data": [[0,ten_years]]},
                        {"label":_(u'八年 ')+str(eight_years), "data":[[0,eight_years]]},
                        {"label":_(u'五年 ')+str(five_years), "data":[[0,five_years]]}, 
                        {"label":_(u'三年 ') +str(three_years),"data":[[0,three_years]]},
                        {"label":_(u'两年 ')+str(two_years), "data":[[0,two_years]]},
                        {"label":_(u'一年 ')+str(one_years), "data":[[0,one_years]]}
                    ]

        elif type=="2":
             qs = list(Employee_objects(request).filter(Gender__isnull=False))             
             if len(qs)==0:
                return getJSResponse(json.dumps([]))
             males= len(filter(lambda e: e.Gender=="M", qs))
             females = len(filter(lambda e: e.Gender=="F", qs))
             if not males and not females:
                return  getJSResponse(json.dumps([]))
             data = [
                        {"label":_(u'男 ') + str(males),"data":[[0,males]]},
                        {"label":_(u'女 ') +str(females) ,"data":[[0,females]] }
                    ]
        elif type=="3":
             emCounts = Employee_objects(request).count()
             qs = list(Employee_objects(request).filter(education__isnull=False))
             if emCounts==0:
                return getJSResponse(json.dumps([]))
             t0= len(filter(lambda e: e.education_id==1, qs))
             t1= len(filter(lambda e: e.education_id==2, qs))
             t2= len(filter(lambda e: e.education_id==3, qs))
             t3= len(filter(lambda e: e.education_id==8, qs))
             t4= len(filter(lambda e: e.education_id==9, qs))
             t5= len(filter(lambda e: e.education_id==10, qs))
             t6= emCounts-t0-t1-t2-t3-t4-t5
             data = [
                        {"label" : u"%s"%_(u'小学 ')+str(t0),"data":[[0,t0]]},
                        {"label" : u"%s"%_(u'初中 ')+str(t1),"data":[[0,t1]]},
                        {"label" : u"%s"%_(u'普通高中 ')+str(t2),"data":[[0,t2]]},
                        {"label" : u"%s"%_(u'本科 ')+str(t3),"data":[[0,t3]]},
                        {"label" : u"%s"%_(u'硕士研究生 ')+str(t4),"data":[[0,t4]]},
                        {"label" : u"%s"%_(u'博士研究生 ')+str(t5),"data":[[0,t5]]},
                        {"label" : u"%s"%_(u'其他 ')+str(t6),"data":[[0,t6]]}
                    ]
        data.sort(lambda x1,x2:x1["data"][0][1]-x2["data"][0][1])
        return getJSResponse(json.dumps(data))
    except:
        import traceback; traceback.print_exc()
    finally:
        pass
    return getJSResponse(json.dumps([]))



def outputattrate(request):
    from dbapp.datautils import QueryData
    json_data=[]
    try:
       from mysite.personnel.models.model_emp import Employee
       emCounts = Employee_objects(request).count()
       if emCounts==0:
           return getJSResponse(json.dumps([]))
       from mysite.iclock.models.model_trans import Transaction
       from mysite.att.models.model_empspecday import EmpSpecDay
       from mysite.sql_utils import p_query
       curr_dt= datetime.datetime.now()
       d1= datetime.datetime(curr_dt.year,curr_dt.month,curr_dt.day,0,0,1)
       d2= datetime.datetime(curr_dt.year,curr_dt.month,curr_dt.day,23,59,59)
       d3 = datetime.datetime(curr_dt.year,curr_dt.month,curr_dt.day)
       sql_emps_count = """
           select count(1) from userinfo u where u.isatt = 1 and  u.status = 0
       """
       sql_trans_emps = """
           select count(1) from
           (select distinct u.userid from checkinout c
            inner join userinfo u on u.badgenumber = c.pin
            where u.isatt = 1 and u.status = 0
                and c.checktime between '%s' and '%s') as t
       """%(d1,d2)
       sql_spe_cont="""
             select count(1) from 
                (select distinct u.userid from  user_speday us
                  inner  join userinfo u on us.UserID = u.userid
                where u.isatt = 1 and u.status=0
                and us.EndSpecDay >= '%s'
                and us.StartSpecDay <= '%s') as t
       """%(d1,d2)
       
       emps_att_count = p_query(sql_emps_count)[0][0]
       qs_atts_emp = p_query(sql_trans_emps)[0][0]
       specialDays_count = p_query(sql_spe_cont)[0][0]
       absents= emps_att_count -qs_atts_emp - specialDays_count 
#       qs_atts_emp=Transaction.objects.select_related().filter(TTime__range=(d1,d2),UserID__isatt=True).distinct().values("UserID__PIN").values_list("UserID")
       #atts = Transaction.objects.select_related().filter(TTime__range=(d1,d2),UserID__isatt=True).distinct().values("UserID__PIN").count()
#       atts,cl=QueryData(request,Transaction,None,qs_atts_emp)
#       atts=atts.count()
#    
#       specialDays = EmpSpecDay.objects.select_related() \
#                    .filter(Q(end__gte=d3,start__lte=d3)
#                            |Q(start__year=d3.year,start__month=d3.month,start__day=d3.day)
#                            |Q(end__year=d3.year,end__month=d3.month,end__day=d3.day)
#                        ) \
#                    .exclude(emp__in=qs_atts_emp)
#       specialDays,cl=QueryData(request,EmpSpecDay,None,specialDays)
#                    
#       specialDays=specialDays.distinct().values("emp__PIN").count()
#       emps,cl=QueryData(request,EmpSpecDay,None,Employee_objects(request).filter(isatt='1'))
#       absents= emps.count() -atts - specialDays
       json_data.append({
            "label":u"%s"%_(u'签到 ')+ str(qs_atts_emp),
            "data":[[20,qs_atts_emp]]
       })
       json_data.append({
            "label":u"%s"%_(u'其他 ')+str(absents),
            "data":[[20,absents]]
       })
       json_data.append({
            "label":u"%s"%_(u'请假 ') + str(specialDays_count),
            "data":[[20,specialDays_count]]
       })
    
       json_data.sort(lambda x1,x2:x1["data"][0][1]-x2["data"][0][1])
       return getJSResponse(json.dumps(json_data))
    except:
        import traceback; traceback.print_exc()
    finally:
        pass
    return getJSResponse(json.dumps([]))


def set_msg_read(request,datakey):
    u=threadlocals.get_current_user()
    try:
        um=UsrMsg()
        um.user=u
        um.msg=InstantMsg.objects.filter(pk=datakey)[0]
        um.readtype="1"
        um.save()
        return getJSResponse('{ Info:"OK" }')
    except:
        import traceback; traceback.print_exc()
        return getJSResponse('{ Info:"exception!" }')

def get_instant_msg(request):
    from dbapp.dataviewdb import model_data_list
    from django.contrib.auth.models import User,Group
    from django.template.defaultfilters import escapejs
    from django.db.models import Q
    import json
    u=threadlocals.get_current_user()
    if u and u.is_anonymous():
        return getJSResponse(u"[]")
    d={}
    qs=None
    [SYSMSG,ATTMSG,IACCESSMSG,PERSONNELMSG]=[1,2,3,4 ]
    exclude_msgtype=[]
    if "mysite.att" not in settings.INSTALLED_APPS:
        exclude_msgtype.append(ATTMSG)
    if "mysite.iaccess" not in settings.INSTALLED_APPS:
        exclude_msgtype.append(IACCESSMSG)

    msgtypes=MsgType.objects.exclude(pk__in=exclude_msgtype)
    dt=datetime.datetime.now()
    dt=datetime.datetime(year=dt.year,month=dt.month,day=dt.day)

    #持续时间过滤条件
    querys=[]
    for elem in msgtypes:
        begin_date=dt-datetime.timedelta(days=elem.msg_keep_time)
        querys.append((Q(change_time__gte=begin_date)&Q(msgtype=elem)))
    combine_query=querys[0]
    for i in querys[1:]:
        combine_query|=i

    #不是超级管理员过滤条件
    if not u.is_superuser:
        ms=GroupMsg.objects.filter(group__user=u).values_list("msgtype")
        d["msgtype__in"]=ms

    #是否已读过滤条件
    has_read=UsrMsg.objects.filter(user=u).values_list("msg")

    qs=InstantMsg.objects.filter(**d).exclude(id__in=has_read)
    qs=qs.filter(combine_query).order_by("-pk")

    json_data={"fields":["id","msgtype","content","change_time"],"data":[]}
    for ee in qs:
        json_data["data"].append([ee.id,u"%s"%ee.msgtype,ee.content,ee.change_time.strftime("%Y-%m-%d")])

    return getJSResponse(json.dumps(json_data))




def download_fingerprint_driver(request):
    '''
    下载驱动驱动
    '''
    from mysite.settings import APP_HOME
    response =  HttpResponse(mimetype="application/octet-stream")
    try:
        
        fingerpath = ""
        file_path = APP_HOME.split("\\")
        file_path.remove(file_path[-1]) 
        file_path.remove(file_path[-1])  
        file_path.remove(file_path[-1])
        for f in file_path:
            fingerpath = fingerpath + f +"\\"
        
        file_name = "Fingerprint Reader Driver.exe"
        
        file_path_name = fingerpath+file_name
       
        response['Content-Disposition'] = 'attachment; filename=Fingerprint Reader Driver.exe' 
        file_object = open(file_path_name, 'rb')
    except :                
        return HttpResponse("Sorry,there is not resource to download temporarily!")
    try:
        while True:
            chunk = file_object.read(100)
            if not chunk:
                break
            response.write(chunk)
    finally:
        file_object.close()   
    return response
