# Create your views here.
#coding=utf-8
from models.model_dept import Department
from models.model_position import Position
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from dbapp.modelutils import GetModel
from django.db.models import Q
from django.utils.simplejson  import dumps 
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from mysite.settings import MEDIA_ROOT
import datetime
from dbapp.dataviewdb import  model_data_list
from django.contrib.auth.decorators import login_required
from mysite.utils import get_option
from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE,ONLINE_ALLOWANCE


def get_max_in_ids(qs,ids,field_name = "pk__in"):
    u"超过一千个组织后的问题"
    emp_ids = []
    ids = [list(e)[0] for e in ids]
    if len(ids)>10000:
        query = []
        while ids:
            query.append(Q(**{field_name:ids[:900]}))
            ids = ids[900:]
        
        combine_query = query[0]
        for qq in query[1:]:
            combine_query |= qq
        qs = qs.filter(combine_query)
    else:
        qs = qs.filter(**{field_name:ids})
    return qs



def select_emp_data(request):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_LOST,CARD_OVERDUE,POS_CARD
    from mysite.iclock.iutils import get_dept_from_all,get_max_in,contruct_q
    all_emp = request.REQUEST.get("all_emp",None)
    orgdept = request.REQUEST.get("PIN__range","")
    op_type = request.REQUEST.get("op_type","")
    para=dict(request.REQUEST)
    if all_emp == "all":
        qs = Employee.all_objects.all()
    elif all_emp == "filed_card":#获取没发卡人员
        if get_option("POS_IC"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).values_list('UserID')
        elif get_option("POS_ID"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD).values_list('UserID')
        else:
            ids=IssueCard.objects.filter(cardstatus=CARD_VALID).values_list('UserID')
        if orgdept:#批量发卡
            where={}
            for p in para:
                if p.find("__")>0:
                    t=p.split("__")
                    if p.find("__range")>0:
                        where[str(p)]=eval(para[p])
                    elif p.find("__in")>0:
                        where[str(p)]=para[p].split(",")
                    else:
                        where[str(p)]=para[p].decode("utf-8") 
            qs = Employee.objects.all().filter(Q(**where)).exclude(id__in=ids)
        else:
            qs = Employee.objects.all().exclude(id__in=ids)
#        qs = Employee.objects.all().filter(using_card="")
    elif all_emp == "filed_having_card":#获取已发卡人员
        if get_option("POS_IC"):
            if op_type == "allowance":#补贴特殊处理
                from mysite.pos.models.model_allowance import Allowance
                now_time = datetime.datetime.now()
                if ONLINE_ALLOWANCE:
                    batch = ((now_time.year-2000)*12+now_time.month)*31+now_time.day
                else:
                    batch = now_time.strftime("%Y%m")[2:]
                allow_sys_card = Allowance.objects.filter(batch = batch).values_list('sys_card_no')#已领取补贴卡账号
                ids = IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).exclude(sys_card_no__in=allow_sys_card).values_list('UserID')#获取没领取补贴人员ID 
            else:
                ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).values_list('UserID')#获取已发卡人员ID
        elif get_option("POS_ID"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD).values_list('UserID')#获取已发卡人员ID
        else:
            ids=IssueCard.objects.filter(cardstatus=CARD_VALID).values_list('UserID')#获取已发卡人员ID
        
#        q_data = Employee.objects.all()
#        try:
#            qs = get_max_in_ids(q_data,ids)
#        except:
#            import traceback;traceback.print_exc()
        qs = Employee.objects.all().filter(id__in=ids)
#        qs = Employee.objects.all().exclude(using_card="")
    else:
        qs = Employee.objects.all()
    
    ignore_keys = []
    checked_child = request.REQUEST.get("checked_child",None)
    if checked_child == "true":
        dept_ids = request.REQUEST.get("DeptID__id__in",None)
        if dept_ids:
            dept_ids = dept_ids.split(",")
            dept_ids = [int(e) for e in dept_ids]
            dept_obj = get_dept_from_all(dept_ids,request)
            
            if len(dept_obj)>1000:
                query = []
                while dept_obj:
                    query.append(Q(DeptID__in = dept_obj[:900]))
                    dept_obj = dept_obj[900:]
                combine_query = query[0]
                for qq in query[1:]:
                    combine_query |= qq
                qs = qs.filter(combine_query)
            else:
                qs = qs.filter(DeptID__in = dept_obj)
            ignore_keys = ["DeptID__id__in"]
    
    return model_data_list(request, Employee, qs,ignore_keys=ignore_keys)



def select_emp_data2(request):
    '''筛选会议人员，会议系统专用 scott add'''
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_LOST,CARD_OVERDUE,POS_CARD
    from mysite.meeting.models.meeting_emp import MeetingEmp
    mes = MeetingEmp.objects.all()
    pins = []
    for me in mes:
        pins.append(me.user.PIN)
    all_emp = request.REQUEST.get("all_emp",None)
    if all_emp == "all":
        qs = Employee.all_objects.filter(PIN__in = pins)
    elif all_emp == "filed_card":#获取没发卡人员
        if get_option("POS_IC"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).values_list('UserID')#获取已发卡人员ID
        elif get_option("POS_ID"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD).values_list('UserID')#获取已发卡人员ID
        else:
            ids=IssueCard.objects.filter(cardstatus=CARD_VALID).values_list('UserID')#获取已发卡人员ID
        qs = Employee.objects.all().exclude(id__in=ids).filter(PIN__in = pins)
#        qs = Employee.objects.all().filter(using_card="")
    elif all_emp == "filed_having_card":#获取已发卡人员
        if get_option("POS_IC"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).values_list('UserID')#获取已发卡人员ID
        elif get_option("POS_ID"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD).values_list('UserID')#获取已发卡人员ID
        else:
            ids=IssueCard.objects.filter(cardstatus=CARD_VALID).values_list('UserID')#获取已发卡人员ID
        qs = Employee.objects.all().filter(id__in=ids).filter(PIN__in = pins)
#        qs = Employee.objects.all().exclude(using_card="")
    else:
        qs = Employee.objects.filter(PIN__in = pins)
    return model_data_list(request, Employee, qs)


#def base_data_view(request):
#    from dbapp.urls import dbapp_url
#    from base import get_all_app_and_models
#    from mysite.personnel.models import BaseData
#    
#    request.dbapp_url = dbapp_url          
#    apps = get_all_app_and_models()
#    return render_to_response("base_data.html", RequestContext(request, {
#        "app_label": "personnel",
#        "dbapp_url": dbapp_url,
#        "MEDIA_ROOT": MEDIA_ROOT,
#        "apps": apps,
#        "myapp": [a for a in apps if a[0]=="personnel"][0][1],
#        "current_app": "personnel",
#        "menu_focus": "BaseData",
#        "position": _(u'人员->基础资料'),
#        "help_model_name": "BaseData",
#    }))

def get_dept_tree_data(request):
    selected=request.REQUEST.getlist("K")
    selected=[int(item) for item in selected]
    level=request.REQUEST.get("LEVEL","1")
    root=request.REQUEST.get("root","1")
    try:
        root=int(root)
    except:
        root=None
        if level=='1': level=2
    from models import depttree
    html=depttree.DeptTree(Department.objects.all()).html_jtree(selected,root_id=root, next_level=int(level))
    return getJSResponse(html)

def getchange(request):
    from mysite.personnel.models import Employee    
    id=request.GET.get("k")
    u=Employee.objects.get(pk=id)
    data={}
    if u:
        data['dept']=int(u.DeptID_id)
        data['position']=u.position.pk 
        data['hiretype']=u.emptype and str(u.emptype) or 1
        data['attarea']=[int(i.pk) for i in u.attarea.all()]
    return getJSResponse(smart_str(data))

def funGetModelData(request,app_lable,model_name):
        from mysite.personnel.models.model_emp  import format_pin
        from mysite.utils import get_option
        model=GetModel(app_lable,model_name)
        fields=request.REQUEST.get("fields","")
        userid=request.REQUEST.get("userid","")
        orgdept=request.REQUEST.get("orgdept","")
        para=dict(request.REQUEST)
        where={}
        for p in para:
                
                if p.find("__")>0:
                    t=p.split("__")
                    
                        
                    if p.find("__range")>0:
                        where[str(p)]=eval(para[p])
                    elif p.find("__in")>0:
                        where[str(p)]=para[p].split(",")
                    else:
                        where[str(p)]=para[p].decode("utf-8")                
                    
        #print where
        #print model
        if fields:
                fields=fields.split(",")
        if model:
                if userid:
                        data=model.objects.filter(id__in=userid)
                else:
                        data=model.objects.all()
                if where:
                        data=model.objects.filter(Q(**where))
                if fields:
                        data=data.values_list(*fields)
                #print data
                xdata=[]
                i=0 
                while i<len(data):
                        tmpdata=data[i]
                        j=0
                        ndata=[]
                        while j<len(tmpdata):
                                #print type(tmpdata[j])
                                if type(tmpdata[j])==datetime.time:
                                        #print "1"
                                        ndata.append(tmpdata[j].strftime("%H:%M:%S"))
                                elif type(tmpdata[j])==datetime.date:
                                        ndata.append(tmpdata[j].strftime("%Y-%m-%d"))
                                else:
                                        ndata.append(tmpdata[j])
                                j+=1
                        xdata.append(ndata)
                        i+=1
                #print xdata
                if orgdept:
                    xdata=processdept(xdata)
                return getJSResponse(smart_str(dumps(xdata)))
        else:
                return NoFound404Response(request)
            
            
def processdept(xdata):
    first=0
    ret=[]    
    tmp=[]
    for d in xdata:
        if d[2]==None or d[2]==d[0]:
            ret.append(d)
        else:
            tmp.append(d)
    cur=0
    while cur<len(ret):
        xtmp=[]
        for i in tmp:
            if i[2]==ret[cur][0]:
                ret.append(i)
            else:
                xtmp.append(i)
        tmp=xtmp
        cur+=1
   # print ret
    return ret

#人事导航-darcy20111018
@login_required
def fun_personnel(request):
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    request.dbapp_url = dbapp_url
    apps = get_all_app_and_models()
    return render_to_response('personnel_guide.html',
        RequestContext(request,{
            'dbapp_url': dbapp_url,
            'MEDIA_URL': MEDIA_ROOT,
            "current_app": 'personnel', 
            'apps': apps,
            "help_model_name": "PersonnelGuide",
            "myapp": [a for a in apps if a[0]=="personnel"][0][1],
            'app_label': 'personnel',
            'model_name': 'PersonnelGuide',
            'menu_focus': 'PersonnelGuide',
            'position': _(u'人事->导航'),
        })
    )


def get_dept_child(depts,current_dept):
    ret=[]
    for e in depts:
        if e.parent_id==current_dept.pk:
            ret.append(e)
            ret.extend(get_dept_child(depts,e))
    return ret


#@app_label应用名称
#model_name 模型名称
#field_name 树形字段名称
#data_key 当前编辑对象ID
def get_children_nodes(request):
    from django.db import models
    from dbapp.datautils import filterdata_by_user
    from mysite.personnel.models.depttree import DeptTree
    from base.middleware import threadlocals
    import json
    from mysite.iclock.iutils import get_max_in
    limit = request.REQUEST.get("limit")
    multiple = request.REQUEST.get("multiple") #是否多选
    async_checked = request.REQUEST.get("checked") #当前异步节点是否选中
    edit_object_id = request.REQUEST.get("edit_object_id") #当前编辑的对象，如人员ID，如果是树形控件本身对象，可能需要按照这个iD进行过滤limit_to_parent
    checked_ids = request.REQUEST.get("checked_ids") #需要选中的记录
    async_id = request.REQUEST.get("id") #异步加载的ID
    has_checked_nodes = request.REQUEST.get("has_checked_nodes") #前端是否有选中的记录
    select_childrens = request.REQUEST.get("select_childrens",None) #是否选择下级
    
    app_label,model_name = request.REQUEST.get("async_model").split("__")
    TreeModel=GetModel(app_label,model_name)#当前模型对象
    
    obj_tree = None
    async_obj = None
    try:
        if edit_object_id != "" and limit == "true":
            try:
                obj_tree=TreeModel.objects.get(pk=edit_object_id)#当前树形控件选中的记录
            except:
                pass
        async_obj = TreeModel.objects.get(pk=async_id)
    except:
        pass
    m_id = "id"
    m_p = "parent_id"
    m_n = "name"
    s_id="dept_id"
    r_m="deptadmin"
    sup_name="supdeptid"
    if TreeModel.__name__ == "Department":
        m_id = "id"
        m_p = "parent_id"
        m_n = "name"
        s_id="dept_id"
        r_m="deptadmin"
        sup_name="supdeptid"
    elif TreeModel.__name__ == "Area":
        m_id = "id"
        m_p = "parent_id"
        m_n = "areaname"
        s_id="area_id"
        r_m="areaadmin"
        sup_name="parent_id"
    
    #新增的时候不需要限制
    uobj= threadlocals.get_current_user()
    vdata = TreeModel.objects.all().order_by(m_n)
    if obj_tree and hasattr(obj_tree,"limit_parent_to"):
        vdata = obj_tree.limit_parent_to(vdata)
    else:
        vdata = filterdata_by_user(vdata,uobj)
    async_fields = [m_id, m_p ,m_n]
    if not uobj.is_superuser: #不是超级管理员    
        select="select  distinct %s from %s where user_id=%s and %s.%s=%s"%(s_id,r_m,request.user.pk,TreeModel._meta.db_table,sup_name,s_id)
        #print "select",select
        vdata=vdata.extra(select={m_p:select} )
    vdata = list(vdata.values(*async_fields))
    checked = False
    checked_objs = None
    
    if multiple == "true" \
        and async_checked == "true" \
        and select_childrens == "true": #多选，并且该节点选中了,包含下级选中了
        checked = True
    elif multiple == "false" and has_checked_nodes == "true": #单选，前端已经选中了节点，后端就不要传选中的记录了。
        checked = False
    else:#选中本来应该有关联的数据
        if checked_ids:
            checked_ids = checked_ids.split(",")
            qs  =TreeModel.objects.all()
            checked_objs = get_max_in(qs,checked_ids,"pk__in")
    children=[]
    for e in vdata:
        tmp_data = {}
        if e[m_p] == async_obj.id:
            tmp_data = { "id":e[m_id], "pId":e[m_p], "name":e[m_n],"isParent":False,"checked":checked }
            if checked_objs:
                for ce in checked_objs:
                    if e[m_id] == ce.pk:
                        tmp_data["checked"] = True
            for ee in vdata:
                if ee[m_p] == e[m_id]:
                    tmp_data["isParent"] = True
                    break
        if tmp_data:
            children.append( tmp_data )
    
    return getJSResponse(json.dumps(children))

def select_state(request,app_label,model_name):
    from dbapp.datautils import QueryData
    from dbapp.modelutils import GetModel
    from dbapp.utils import getJSResponse
    import json
    from django.http import HttpResponseRedirect,HttpResponse
    from mysite.personnel.models.model_state import State
    from mysite.personnel.models.model_emp import format_pin
    
    ModelCls = GetModel(app_label, model_name)
    ret = []
    keys = ["country",]
    filter_dict = {}
    qs = []
    for e in keys:
        value = request.REQUEST.get(e,None)
        if value:
          filter_dict[e] = value
    
    if filter_dict:
        qs = ModelCls.all_objects.filter(**filter_dict)
        for elem in qs:
            ret.append([elem.id,elem.state_code,elem.state_name])  
    return getJSResponse(json.dumps(ret))

def select_city(request,app_label,model_name):
    from dbapp.datautils import QueryData
    from dbapp.modelutils import GetModel
    from dbapp.utils import getJSResponse
    import json
    from django.http import HttpResponseRedirect,HttpResponse
    from mysite.personnel.models.model_city import City
    from mysite.personnel.models.model_emp import format_pin

    ModelCls = GetModel(app_label, model_name)
    
    ret = []
    keys = ["state",]
    filter_dict = {}
    qs = []
    for e in keys:
        value = request.REQUEST.get(e,None)
        if value:
          filter_dict[e] = value

    if filter_dict:
        qs = ModelCls.all_objects.filter(**filter_dict)
        for elem in qs:
            ret.append([elem.id,elem.city_code,elem.city_name])  
    return getJSResponse(json.dumps(ret))

def select_position(request, app_label, model_name):
    from dbapp.datautils import QueryData
    from dbapp.modelutils import GetModel
    from dbapp.utils import getJSResponse
    import json
    from django.http import HttpResponseRedirect,HttpResponse
    from mysite.personnel.models.model_position import Position
    from mysite.personnel.models.model_emp import format_pin
    
    ModelCls = GetModel(app_label, model_name)
    
    ret = []
#    keys = ["DeptID",]
    filter_dict = {}
    qs = []
#    print "request",request.REQUEST.get("newdept")
#    for e in keys:
#        value = request.REQUEST.get(e,None)
#        print "------------------",value
#        if value:
#            filter_dict[e] = value
#    if not filter_dict:
#        newdept=request.REQUEST.get("newdept",None)
#        filter_dict['DeptID'] = newdept
    dept_id = request.REQUEST.get("DeptID",None)
    new_dept = request.REQUEST.get("newdept",None)
    department = request.REQUEST.get("department",None)
    if dept_id:
        filter_dict["DeptID"] = dept_id
    if new_dept:
        filter_dict["DeptID"] = new_dept
    if department:
        filter_dict["DeptID"] = department
#    print "++++++++++++++++",filter_dict         
    if filter_dict:
        qs = ModelCls.all_objects.filter(**filter_dict)
        for elem in qs:
            ret.append([elem.id, elem.code, elem.name])
#    print "=====================",ret        
    return getJSResponse(json.dumps(ret))

def get_card_info(request):
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,PRIVAGE_CARD,POS_CARD,CARD_STOP,CARD_OVERDUE
    from mysite.personnel.models.model_emp import get_dept
    from mysite.personnel.models.model_emp import getuserinfo
    from django.utils import simplejson 
    card_no = request.REQUEST.get("cardno", "")
    try:
        if get_option("POS_IC"):
            type = request.REQUEST.get("type", "")
            if type=="issuing":  #发卡 检测卡片已登记人员
                card_obj = IssueCard.objects.get(cardno=card_no,cardstatus=CARD_VALID)
            else:
                card_obj = IssueCard.objects.get(sys_card_no=card_no)
        else:
            card_obj = IssueCard.objects.get(cardno=card_no)
        dept_name = get_dept(card_obj.UserID_id).name
        user_pin = getuserinfo(card_obj.UserID_id,"PIN")
        user_name = getuserinfo(card_obj.UserID_id,"EName")
        if get_option("POS_IC"):
            return getJSResponse(smart_str(simplejson.dumps({'ret':1,'user_pin': user_pin,'user_name':user_name,'dept_name':dept_name,'blance':str(card_obj.blance),'cardstatus':card_obj.cardstatus,'sys_card_no':card_obj.sys_card_no})))
        else:
            return getJSResponse(smart_str(simplejson.dumps({'ret':1,'user_pin': user_pin,'user_name':user_name,'dept_name':dept_name,'blance':str(card_obj.blance),'cardstatus':card_obj.cardstatus})))
    except:
        return getJSResponse(smart_str(simplejson.dumps({'ret': -1})))
    
