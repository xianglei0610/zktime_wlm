#coding=utf-8

from mysite.settings import MEDIA_ROOT
from base import get_all_app_and_models
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps 
from django.utils import simplejson 

from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required, login_required
from  datetime   import datetime,date,time,timedelta
#from report import pos_danne,get_pos_record,get_add_record,get_subsidies_record,get_diningcalculate_record
#from report import funPosReport
from report_data import posStatisticalReports,get_ic_list_record,pos_list_Reports,get_id_list_record,get_ic_error_list_record
from dbapp.datalist import save_datalist
from mysite.pos.pos_utils import LoadPosParam
from django.db import transaction
from  decimal import Decimal
from mysite.utils import get_option
#import datetime

            
            
def funposParamSetting(request):
    la = LoadPosParam(True)
    qs = la.copy()
    return getJSResponse(smart_str(dumps(qs)))

       
def get_pin(self):
        from mysite.personnel.models.model_emp import getuserinfo
        return getuserinfo(self.pk,"PIN")
          
def get_ename(self):
    from mysite.personnel.models.model_emp import getuserinfo
    return getuserinfo(self.pk,"EName")
def get_dept_name(self):
    u'''从缓存中得到部门的Name'''
    from mysite.personnel.models import Department
    dept_name=""
    try:
        dept_obj=Department.objects.get(id=self.DeptID_id)
        dept_name=dept_obj.name
    except:
        pass
    return dept_name



     
def get_diningroom(request):
    select_dininghall= request.REQUEST.get("dininghall", "")
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.personnel.models.model_meal import Meal
    from django.contrib.auth.models import User
    from mysite.pos.models.model_cardmanage import CardManage
    from mysite.utils import get_option
    if select_dininghall:
       pass
    else:
        halls= Dininghall.objects.all().order_by('id').values_list('id','code','name')
        meals=Meal.objects.all().order_by('id').values_list('id','code','name')
        operates=User.objects.all().exclude(username = 'employee').order_by('id').values_list('id','username')
        if get_option("POS_IC"):
            operate_card = CardManage.objects.all().order_by('id').values_list('id','sys_card_no')
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all', 'operate_card':[op_card for op_card in operate_card],'operates':[operate for operate in operates],'meals':[meal for meal in meals],'halls': [hall for hall in halls]})))
        else:
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all','operates':[operate for operate in operates],'meals':[meal for meal in meals],'halls': [hall for hall in halls]})))
      
 

def get_pos_list_record(hander,request,userids,**arg):
    '''
    消费明细
    '''
    deptids=request.REQUEST.get('DeptIDs',"")
#    userids=request.POST.get('UserIDs',"")
#    print "userids============",request.POST.get('UserIDs',"")
#    type=request.GET.get('type','')
 
    st=request.REQUEST.get('ComeTime','')
    et=request.REQUEST.get('EndTime','')
    st=datetime.strptime(st,'%Y-%m-%d')
    et=datetime.strptime(et,'%Y-%m-%d')
    operate=request.REQUEST.get('operate','')
    et=et+timedelta(days=1)
    pos_model =  request.REQUEST.get('pos_model','')
    dining =  request.REQUEST.get('Dining','')
    loadall=request.REQUEST.get('pa','')
    try:
        if get_option("POS_IC"):
            get_ic_list_record(hander,request,deptids,userids,dining,st,et,pos_model,operate,**arg)
        else:
            get_id_list_record(hander,request,deptids,userids,dining,st,et,pos_model,operate,**arg)
    except:
        import traceback;traceback.print_exc()


#@login_required  
def posreport(hander,request,userids,report_typeid,**arg):
    '''
    消费统计报表入口点 开始统计  typeid为统计报表类型
    # 报表类型  
    #    110 表示  餐厅汇总表 
    #    120 表示  部门汇总
    #    130 表示  个人消费汇总表
    #    140 表示  设备汇总
    #    150 表示  收支统计
    
    '''
    deptids=request.REQUEST.get('DeptIDs',"")
#    userids=request.REQUEST.get('UserIDs',"")
    dining=request.REQUEST.get('Dining',"")
    meal = request.REQUEST.get('Meal','')
    operate=request.REQUEST.get('Operate','')
    
    st=request.REQUEST.get('ComeTime','')
    et=request.REQUEST.get('EndTime','')

    st=datetime.strptime(st,'%Y-%m-%d')
    et=datetime.strptime(et,'%Y-%m-%d')
    et=et+timedelta(days=1)
    
    pos_model =  request.REQUEST.get('pos_model','')
    check_opreate =  request.REQUEST.get('check_operate','')
    loadall=request.REQUEST.get('pa','')
    
    allr=posStatisticalReports(hander,request,deptids,userids,st,et,dining,meal,report_typeid,operate,pos_model,check_opreate,**arg)

def get_all_dept_from_all(depts_ids = [],request = None):
    u"从所有组织中得到depts_ids的子集组织"
    from dbapp.datautils import filterdata_by_user
    from mysite.iclock.iutils import get_list_children
    from mysite.iclock.models import Department
    
    qs_all = Department.all_objects.all()
    if request:
        qs_all = filterdata_by_user(qs_all,request.user)
    ret  =  get_list_children(qs_all,depts_ids)
    return ret


def get_emps_by_deptidlist(deptlist,child = False):
    from mysite.sql_utils import p_query
    if child :
        # 包含下级
        sql = """
            
            WITH NODES     
             AS (   
             SELECT DeptID,supdeptid FROM DBO.departments par WHERE par.DeptID in (%s)
             UNION ALL     
             SELECT child.DeptID,child.supdeptid FROM departments AS child INNER JOIN   
              NODES  AS RC ON child.supdeptid = RC.DeptID)    
              select userid from userinfo  where userinfo.defaultdeptid in( (SELECT DeptID  FROM NODES N )
            )
        """%deptlist
    else:
        sql = """
           select u.userid from userinfo u
            left join departments d on u.defaultdeptid=d.DeptID
            where d.DeptID in (%s)
        """%deptlist
    res = p_query(sql)
    if res:
        return [u"%d"%(r[0]) for r in res]
    else:
        return ["-1"]

def get_report_MultiSelect_objs(model,request):
    '''
    用来返回报表查询中选人控件选中了包含下级时的人员列表
    model 选择的对象模型 例: Employee
    request 请求上下文
    
    return  返回所选择的对象列表
    '''
    from mysite.iclock.iutils import get_max_in
    userids=request.REQUEST.getlist('UserIDs')
    deptids=request.REQUEST.get('DeptIDs',"")
    u = []
    if request:
        if userids[0]:
              u=userids
        elif len(deptids)>0:
            dept_id = request.REQUEST.getlist("deptIDs")
            checked_child=request.REQUEST.get('deptIDschecked_child',None)
            if len(dept_id)>0:
               dept_id= ','.join(dept_id).split(',')
            else:
               dept_id = []
            if checked_child == "on" and dept_id:#包含部门下级
#                depts = get_all_dept_from_all(dept_id,request)
                u = get_emps_by_deptidlist(deptids,True)
#                user_list = get_max_in(model.all_objects.all(),depts,"DeptID__in")
#                u=[e.pk for e in a_list]
            else:
                u = get_emps_by_deptidlist(deptids,False)
#                user_list = get_max_in(model.all_objects.all(),dept_id,"DeptID__in")
#                u=[e.pk for e in user_list]
    return u

def get_grid_arg(request):
    '''
    获取usderid
    '''
    from mysite.personnel.models import Employee
    import time
    try:
        userids = get_report_MultiSelect_objs(Employee,request)
        userids = [str(e) for e in userids if e!=""]
        if len(userids)>0:
            userids = ','.join(userids).split(',')
        else:
            userids = []
        return userids
    except:
        import traceback;traceback.print_exc();
        return [],None,None




def pos_list_report(hander,request,userids,report_typeid,**arg):
    '''
    消费报表入口点 开始统计  typeid为统计报表类型
    # 报表类型  
    #    13 表示  发卡表 
    #    1 表示  充值表
    #    4 表示  退卡表
    #    5 表示  退款表
    #    2 表示  补贴表
    #    12 表示  卡余额表
    #    7 表示	卡成本表
    #    14 表示	消费异常明细表
    '''
    deptids=request.REQUEST.get('DeptIDs',"")
#    userids=request.POST.get('UserIDs',"")
    dining=request.REQUEST.get('Dining',"")
    meal = request.REQUEST.get('Meal','')
    operate=request.REQUEST.get('operate','')
    st=request.REQUEST.get('ComeTime','')
    et=request.REQUEST.get('EndTime','')
    
    
    st=datetime.strptime(st,'%Y-%m-%d')
    et=datetime.strptime(et,'%Y-%m-%d')
    et=et+timedelta(days=1)
    typeid=report_typeid
    pos_model =  request.REQUEST.get('pos_model','')
    check_opreate =  request.REQUEST.get('check_operate','')
    loadall=request.REQUEST.get('pa','')
    try:
        allr=pos_list_Reports(hander,request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,**arg)
    except:
        import traceback;traceback.print_exc()


 
 

    
