# -*- coding: utf-8 -*-
from dbapp.views import customSql
from dbapp.utils import getJSResponse
from django.db import connection
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator
from django.conf import settings
from dbapp.datautils import *
from mysite.personnel.models.model_emp import Employee
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from mysite.iclock.iutils import userDeptList
from dbapp.datalist import save_datalist
import  django.utils.simplejson  as sj
import datetime
from django.conf import settings
from mysite.personnel.sql import GenerateEmpFlow_sql

def GenerateEmpFlow(request):
    cudt = datetime.datetime.now().strftime("%Y-%m-%d")
    d1=request.POST.get("starttime",cudt)
    d2=request.POST.get("endtime",cudt)
    deptids = request.POST.get("deptids")
    sql=GenerateEmpFlow_sql(request,deptids,d1,d2)
    
    cs = connection.cursor()
    cs.execute(sql)

    header0=[{'DeptName':_(u'部门')},{'newin':_(u'新进')},{'transferin':_(u'调入')},{'transferout':_(u'调出')},{'selfleave':_(u'自离')},{'passiveleave':_(u'辞退')},{'normalleave':_(u'辞职')}]
    header={'DeptName':u'%s'%_(u'部门'),'newin':u'%s'%_(u'新进'),'transferin':u'%s'%_(u'调入'),
            'transferout':u'%s'%_(u'调出'),'selfleave':u'%s'%_(u'自离'),'passiveleave':u'%s'%_(u'辞退'),
            'normalleave':u'%s'%_(u'辞职')}
    headers= "["+",".join([u"'%s'"%i.values()[0] for i in header0])+"]"
    
    fields=['DeptName','newin','transferin','transferout','selfleave','passiveleave','normalleave']
    cc={}
    data = cs.fetchall()
    r={}
    datatotmp=[]
    for row in data:
        r[fields[6]] = row[6]
        r[fields[5]] = row[5]
        r[fields[4]] = row[4]
        r[fields[3]] = row[3]
        r[fields[2]] = row[2]
        r[fields[1]] = row[1]
        r[fields[0]] = row[0]
        datatotmp.append(r.copy())

    tmp_name=save_datalist({"data":datatotmp,"fields":fields,"heads":header})
    
    if len(data)==0:
        data =[]
        data.append([])
    try:
           offset = int(request.REQUEST.get(PAGE_VAR, 1))
    except:
           offset=1
    
    limit= int(request.REQUEST.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
    
    mnp=request.REQUEST.get(MAX_NO_PAGE, 0)
    if len(data)<=int(mnp):
        limit=int(mnp)
    
    paginator = Paginator(data, limit)
    item_count = paginator.count
    if offset>paginator.num_pages: offset=paginator.num_pages
    if offset<1: offset=1
    pgList = paginator.page(offset)

    cc["page_count"]=paginator.num_pages
    cc["record_count"]=item_count
    cc["page_number"]=offset
    cc["heads"] =headers
    cc["data"] =pgList.object_list
    cc["fields"]= fields
    cc["tmp_name"]=tmp_name
    return GenerateEmpFlowJsonData(request,cc)
   
def GenerateEmpFlowJsonData(request,data):
     temp="""{tmp_name:{% autoescape off %}"{{tmp_name}}"{% endautoescape %},heads:{% autoescape off %}{{heads}}{% endautoescape %},fields:{% autoescape off %}{{fields}}{% endautoescape %},page_count:{{page_count}},record_count:{{record_count}},page_number:{{page_number}},data:[{% for i in data %}\
             [""" +"\"{{i.0}}\"," + "\"{{i.1}}\"," +"\"{{i.2}}\","+"\"{{i.3}}\","+"\"{{i.4}}\","+"\"{{i.5}}\"," +"\"{{i.6}}\"]" \
             """{%if not forloop.last%},{%endif%}{% endfor %}]}"""
     cc = Context(data)
     d = Template(temp).render(RequestContext(request,cc))
     return getJSResponse(d)

def GenerateDeptRoster(request):
    from mysite.personnel.sql import GenerateDeptRoster_sql
    deptids = request.POST.get("deptids")
    #emps =Employee.objects.filter(DeptID__in=deptids).order_by('DeptID','PIN').values_list('PIN','EName','DeptID__name','Title','Mobile','Birthday','birthplace','Education')
    sql=GenerateDeptRoster_sql(request,deptids)    
    cs = connection.cursor()
    cs.execute(sql)
    header0=[_(u'工号'),_(u'姓名'),_(u'部门'),_(u'职位'),_(u'手机'),_(u'年龄'),_(u'籍贯'),_(u'学历')]
    header={'PIN':u'%s'%_(u'工号'),'EName':u'%s'%_(u'姓名'),'Department':u'%s'%_(u'部门'),
            'position':u'%s'%_(u'职位'),'mobile':u'%s'%_(u'手机'),'age':u'%s'%_(u'年龄'),
            'native':u'%s'%_(u'籍贯'),'education':u'%s'%_(u'学历') }
    headers= "["+",".join([u"'%s'"%i for i in header0])+"]"
    
    fields=['PIN','EName','Department','position','mobile','age','native','education']
    
    cc={}
    data = cs.fetchall()
    
    r={}
    datatotmp=[]
    
    cudt = datetime.datetime.now()
    cudd = datetime.date(cudt.year,cudt.month,cudt.day)
    for row in data:
        r[fields[7]] = row[7]
        r[fields[6]] = row[6]
        if row[5]:
            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
                cudd = datetime.datetime(cudt.year,cudt.month,cudt.day)
            r[fields[5]] = (cudd - row[5]).days /365
        else:
            r[fields[5]] = row[5]
        r[fields[4]] = row[4]
        r[fields[3]] = row[3]
        r[fields[2]] = row[2]
        r[fields[1]] = row[1]
        r[fields[0]] = row[0]
        datatotmp.append(r.copy())
    
    tmp_name=save_datalist({"data":datatotmp,"fields":fields,"heads":header})
    
    
    try:
        
        data_list =[]
        for item in data:
            tmp= list(item)
            if tmp[5]:
                tmp[5]=(cudd - tmp[5]).days /365
            data_list.append(list(tmp))

        if len(data_list)==0:
            data_list=[]
            data_list.append([])
        try:
               offset = int(request.REQUEST.get(PAGE_VAR, 1))
        except:
               offset=1
        
        limit= int(request.REQUEST.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
        mnp=request.REQUEST.get(MAX_NO_PAGE, 0)
        if len(data_list)<=int(mnp):
            limit=int(mnp)
        
        paginator = Paginator(data_list, limit)
        
        item_count = paginator.count
        if offset>paginator.num_pages: offset=paginator.num_pages
        if offset<1: offset=1
        pgList = paginator.page(offset)
        
        cc={}
        cc["page_count"]=paginator.num_pages
        cc["record_count"]=item_count
        cc["page_number"]=offset
        cc["heads"] =headers
        cc["data"] =pgList.object_list
        cc["fields"]= fields
        cc["tmp_name"]=tmp_name
    except:
        import traceback; traceback.print_exc()
    return GenerateEmpRosterJsonData(request,cc)

def GenerateEmpRosterJsonData(request,data):
    temp="""{tmp_name:{% autoescape off %}"{{tmp_name}}"{% endautoescape %},heads:{% autoescape off %}{{heads}}{% endautoescape %},fields:{% autoescape off %}{{fields}}{% endautoescape %},page_count:{{page_count}},record_count:{{record_count}},page_number:{{page_number}},data:[{% for i in data %}\
             [""" +"\"{{i.0}}\"," + "\"{{i.1}}\"," +"\"{{i.2}}\","+"\"{{i.3}}\","+"\"{{i.4}}\","+"\"{{i.5}}\"," +"\"{{i.6}}\","+ "\"{{i.7}}\"]" \
             """{%if not forloop.last%},{%endif%}{% endfor %}]}"""
    cc = Context(data)
    d = Template(temp).render(RequestContext(request,cc))
    return getJSResponse(d)
    

def GenerateEmpEducation(request):
    from mysite.personnel.sql import GenerateEmpEducation_sql
    deptids = request.POST.get("deptids")
    sql=GenerateEmpEducation_sql(request,deptids)
        
    
    header0=[_(u'部门'),_(u'小学'),_(u'初中'),_(u'普通高中'),_(u'本科'),_(u'硕士研究生'),_(u'博士研究生')]
    headers= "["+",".join([u"'%s'"%i for i in header0])+"]"
    
    header={'DeptName':u'%s'%_(u'部门'),'pupil':u'%s'%_(u'小学'),
           'middle_studemt':u'%s'%_(u'初中'),'high_studemt':u'%s'%_(u'普通高中'),
           'university_studemt':u'%s'%_(u'本科'),'graduate_studemt':u'%s'%_(u'硕士研究生'),
           'doctor':u'%s'%_(u'博士研究生')}
    
    fields=['DeptName','pupil','middle_studemt','high_studemt','university_studemt','graduate_studemt','doctor']
    cs = connection.cursor()
    cs.execute(sql)
#    data=[]
#    while True:
#       t=cs.fetchone()
#       if t is None:
#            break
#       data.append(list(t))
    data = cs.fetchall()
    r={}
    datatotmp=[]
    for row in data:
        r[fields[6]] = row[6]
        r[fields[5]] = row[5]
        r[fields[4]] = row[4]
        r[fields[3]] = row[3]
        r[fields[2]] = row[2]
        r[fields[1]] = row[1]
        r[fields[0]] = row[0]
        datatotmp.append(r.copy())
    
    tmp_name=save_datalist({"data":datatotmp,"fields":fields,"heads":header})
    
    if len(data)==0:data.append([])
    try:
           offset = int(request.REQUEST.get(PAGE_VAR, 1))
    except:
           offset=1
    
    limit= int(request.REQUEST.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
    mnp=request.REQUEST.get(MAX_NO_PAGE, 0)
    if len(data)<=int(mnp):
        limit=int(mnp)
    
    paginator = Paginator(data, limit)
    
    item_count = paginator.count
    if offset>paginator.num_pages: offset=paginator.num_pages
    if offset<1: offset=1
    pgList = paginator.page(offset)
    
    cc={}
    cc["page_count"]=paginator.num_pages
    cc["record_count"]=item_count
    cc["page_number"]=offset
    cc["heads"] =headers
    cc["data"] =pgList.object_list
    cc["fields"]= fields
    cc["tmp_name"]=tmp_name
    return GenerateEmpEducationJsonData(request,cc)
    
def GenerateEmpEducationJsonData(request,data):
    temp="""{tmp_name:{% autoescape off %}"{{tmp_name}}"{% endautoescape %},heads:{% autoescape off %}{{heads}}{% endautoescape %},fields:{% autoescape off %}{{fields}}{% endautoescape %},page_count:{{page_count}},record_count:{{record_count}},page_number:{{page_number}},data:[{% for i in data %}\
             [""" +"\"{{i.0}}\"," + "\"{{i.1}}\"," +"\"{{i.2}}\","+"\"{{i.3}}\","+"\"{{i.4}}\","+"\"{{i.5}}\"," +"\"{{i.6}}\"]" \
             """{%if not forloop.last%},{%endif%}{% endfor %}]}"""
    cc = Context(data)
    d = Template(temp).render(RequestContext(request,cc))
    return getJSResponse(d)

def GenerateEmpCardList(request):
    from mysite.personnel.models.model_issuecard import IssueCard
    try:
        depts =userDeptList(request.user)
        if depts:
            data=IssueCard.objects.filter(UserID__DeptID__in=userDeptList(request.user)).order_by("UserID__PIN").values_list("UserID__PIN","UserID__EName","cardno","issuedate","effectivenessdate","cardstatus")
        else:
            data=IssueCard.objects.all().order_by("UserID__PIN").values_list("UserID__PIN","UserID__EName","cardno","issuedate","effectivenessdate","cardstatus")
        header0=[_(u'工号'),_(u'姓名'),_(u'卡号'),_(u'发卡日期')] #,_(u'有效日期'),_(u'卡状态')
        headers= "["+",".join([u"'%s'"%i for i in header0])+"]"
        fields=['PIN','EName','cardno','issuedate'] #,'effectivenessdate','cardstatus'
        
        header={'PIN':u'%s'%_(u'工号'),'EName':u'%s'%_(u'姓名'),
                'cardno':u'%s'%_(u'卡号'),'issuedate':u'%s'%_(u'发卡日期')}
#                'effectivenessdate':u'%s'%_(u'有效日期'),
#                'cardstatus':u'%s'%_(u'卡状态')}    
        
        r={}
        datatotmp=[]
        for row in data:
#            r[fields[5]] = row[5]
#            r[fields[4]] = row[4]
            r[fields[3]] = row[3]
            r[fields[2]] = row[2]
            r[fields[1]] = row[1]
            r[fields[0]] = row[0]
            datatotmp.append(r.copy())

        tmp_name=save_datalist({"data":datatotmp,"fields":fields,"heads":header})
        
        try:
               offset = int(request.REQUEST.get(PAGE_VAR, 1))
        except:
               offset=1
        if len(data)==0:
            data=[]
            data.append([])
        limit= int(request.REQUEST.get(PAGE_LIMIT_VAR, settings.PAGE_LIMIT))
        mnp=request.REQUEST.get(MAX_NO_PAGE, 0)
        if len(data)<=int(mnp):
            limit=int(mnp)

        paginator = Paginator(data, limit)
        item_count = paginator.count
        if offset>paginator.num_pages: offset=paginator.num_pages
        if offset<1: offset=1
        pgList = paginator.page(offset)
        
        cc={}
        cc["page_count"]=paginator.num_pages
        cc["record_count"]=item_count
        cc["page_number"]=offset
        cc["heads"] =headers
        cc["data"] =pgList.object_list
        cc["fields"]= fields
        cc["tmp_name"]= tmp_name
    except:
        import traceback; traceback.print_exc()
    return GenerateEmpCardJsonData(request,cc)

def GenerateEmpCardJsonData(request,data):
    temp="""{tmp_name:{% autoescape off %}"{{tmp_name}}"{% endautoescape %},heads:{% autoescape off %}{{heads}}{% endautoescape %},fields:{% autoescape off %}{{fields}}{% endautoescape %},page_count:{{page_count}},record_count:{{record_count}},page_number:{{page_number}},data:[{% for i in data %}\
             [""" +"\"{{i.0}}\"," + "\"{{i.1}}\"," +"\"{{i.2}}\","+"\"{{i.3}}\"]" \
             """{%if not forloop.last%},{%endif%}{% endfor %}]}"""
    cc = Context(data)
    d = Template(temp).render(RequestContext(request,cc))
    return getJSResponse(d)

    
