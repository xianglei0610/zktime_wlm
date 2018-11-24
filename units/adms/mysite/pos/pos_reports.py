#! /usr/bin/env python
#coding=utf-8
from django.utils.encoding import  force_unicode
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps 
from django.utils import simplejson 
from dbapp.datalist import save_datalist
from  datetime   import datetime,date,time,timedelta
#from mysite.pos.models import CarCashSZ
from  get_reportsfields  import get_posreprots_fields
import datetime
from mysite.utils import get_option
#sql语句生产报表的时候，需要引入的：
from django.conf import settings
#from mysite.att.models.modelproc import customSql,customSqlEx
from django.db import  connection
from django.core.cache import cache

from mysite.pos.id_report_sql import *
from mysite.pos.ic_report_sql import *
from mysite.pos.report_action import dict_dept_obj,dict_dining_obj,dict_meal_obj,dict_card_type_obj,save_pos_tmp_datalist,pos_load_tmp_file,dict_all_emp_obj,dict_cash_type_obj
from mysite.sql_utils import p_query,p_execute,p_query_one
db_select=1
MYSQL=1
SQLSERVER=2
ORACLE=3
POSTGRESSQL=4
if 'mysql' in connection.__module__:#mysql 数据库
    db_select=1
elif 'sqlserver_ado' in connection.__module__:#sqlserver 2005 数据库 
    db_select=2
elif 'oracle' in connection.__module__: #oracle 数据库 
    db_select=3
elif 'postgresql_psycopg2' in connection.__module__: # postgresql 数据库
    db_select=4
from mysite.personnel.models.model_meal import Meal



def customSql(sql,action=True):
#    from django.db import connection
    cursor = connection.cursor()
    
    cursor.execute(sql)
    if action:
        connection._commit()
    return cursor

def customSqlEx(sql,params=[],action=True):
	try:
		cursor = connection.cursor()
		if settings.DATABASE_ENGINE == 'ibm_db_django':
			if not params:params=()
		if params:
			cursor.execute(sql,params)
		else:
			cursor.execute(sql)
		
		if action:
			connection._commit()
		return cursor
	except:
		return None

#
#def get_dining_room(request):
#    '''
#    得到所有的餐厅 并在前台显示
#    '''
#    select_dininghall= request.REQUEST.get("dininghall", "")
#    from mysite.pos.models import Dininghall,Meal
#    from django.contrib.auth.models import User
#    print 'select_dininghall',select_dininghall
#    #select_meeting="abcdef"
#    if select_dininghall:
#       pass
#    else:
#        
#        halls= Dininghall.objects.all().order_by('id').values_list('id','code','name')
#        meals=Meal.objects.all().order_by('id').values_list('id','code','name')
#        operates=User.objects.all().order_by('id').value_list('id','username')
#        return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all', 'operates':[operate for operate in operates],'meals':[meal for meal in meals],'halls': [hall for hall in halls]})))
def get_sql_data(postype_id,d1,d3,sql_add=""):
    day_money=0
    day_count=0
    if db_select==MYSQL or db_select==SQLSERVER:
        sql="select money from pos_carcashsz where type_id='%d' and checktime>='%s' and checktime <'%s'  "%(postype_id,d1,d3)
    else:
        sql=""
    sql+=sql_add
    print sql
    cs=customSql(sql,False)
    desc=cs.description
    fldNames={}
    i=0
    for c in desc:#            
        fldNames[c[0].lower()]=i
        i=i+1
    rows=cs.fetchall()
    for t in rows:
        day_money+=  t[fldNames['money']]
        day_count+=1
    return [day_money,day_count]
    

CONSUMEMODEL={
            1:_(u'定值模式'),
            2:_(u'金额模式'),
            3:_(u'键值模式'),
            4:_(u'计次模式'),
            5:_(u'商品模式'),
            6:_(u'计时模式'),
            7:_(u'记账模式'),
            8:_(u'手工补消费'),
            9:_(u'消费纠错'),
                  }
LOGFLAG={
            1:_(u'设备上传'),
            2:_(u'系统添加'),
            3:_(u'纠错补入'),
            4:_(u'逃卡补单'),
            5:_(u'消费日期异常'),
            6:_(u'卡账号异常'),
            
                  }

#页面参数设置
def from_page_item(request,Result,item_count):
    if item_count>0:
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #每页显示 多少数据
        if item_count % limit==0:#page_count获取总页数
           page_count =item_count/limit
        else:
           page_count =int(item_count/limit)+1   
        try:
           offset = int(request.REQUEST.get('p', 1))
        except:
           offset=1
        if offset>page_count and page_count:
           offset=page_count
        #定义一些显 总数
        Result['item_count']=item_count
        Result['page']=offset
        Result['limit']=limit
        Result['from']=(offset-1)*limit+1
        Result['page_count']=page_count
    else:
        Result['item_count']=0
        Result['page']=1
        Result['limit']=int(request.POST.get('l', settings.PAGE_LIMIT))
        Result['page_count']=1
        

#ic消费异常明细报表
def get_ic_error_list_record(request,st,et,totalall=False):
    from mysite.personnel.models import Employee,Department
    from mysite.pos.models import IcErrorLog    
    from  get_reportsfields import get_ic_pos_list
    from mysite.personnel.models.model_meal import Meal
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.utils import get_MultiSelect_objs
    import time
    datas=[]#储存统计记录   储存的是每行记录
    Result={}#返回结果 字典
    sql_add="select user_pin,user_name,dept,card,sys_card_no,money,balance,pos_model,dining_id,meal_id,meal_data,dev_sn,dev_serial_num,card_serial_num,log_flag,create_operator,pos_time,convey_time from %s where pos_time>='%s' and pos_time <'%s'" %(IcErrorLog._meta.db_table,st,et)
    r_base,FieldNames,FieldCaption=get_ic_pos_list()
    Result['fieldnames']=FieldNames
    Result['fieldcaptions']=FieldCaption
#    print "sql===============",sql_add
    if not totalall:
        rows = p_query(sql_add)
        b= time.time()
        item_count=len(rows)
        sum_pos_money = 0
        back_money = 0
        sum_back_money = 0
        sum_test_card_money = 0
        sum_test_card_back_money = 0
        try:
            from_page_item(request,Result,item_count)
            all_dining = dict_dining_obj()
            all_meal = dict_meal_obj()
            #开始进行统计
            r_b = r_base.copy()
            for row in rows:
                r = r_base.copy()
                pos_money = row[5]
                r['user_pin'] = row[0]
                r['user_name'] = row[1]
                r['dept_name'] = row[2]
                r['card'] = row[3]
                r['sys_card_no'] = row[4]
                r['money'] = '￥'+ str(pos_money)
                r['balance'] = '￥'+ str(row[6])
                if row[7] == 9:#纠错
                    back_money =pos_money
                    sum_back_money += pos_money
                    pos_money = 0
                if row[7]:
                    r['pos_model'] = CONSUMEMODEL[int(row[7])]
                r['dining'] = all_dining[row[8]]
                if row[9]:
                    r['meal_id'] = all_meal[row[9]]
                else:
                    r['meal_id'] = None
                if row[10]:
                    r['meal_data'] = row[10].strftime("%Y-%m-%d")
                r['dev_sn'] = row[11]
                r['dev_serial_num'] = row[12]
                r['card_serial_num'] = row[13]
                r['log_flag'] = LOGFLAG[int(row[14])]
                r['create_operator'] = row[15]
                r['pos_time'] = row[16].strftime("%Y-%m-%d %H:%M:%S")
                if row[17]:
                    r['convey_time'] = row[17].strftime("%Y-%m-%d %H:%M:%S")
                datas.append(r)
                sum_pos_money += pos_money
            try:
                offset = int(request.REQUEST.get('p', 1))
            except:
                offset=1
            limit= int(request.POST.get('l', settings.PAGE_LIMIT))
            re=datas[((offset-1)*limit):(offset*limit)]
            all_export_data = Result.copy()
            rr = r_base.copy()
            rr['user_pin'] = _(u"合计：")
            rr['money'] = _(u"实消费总额：") + '￥'+ str(sum_pos_money - sum_back_money)
            cache.set("ic_error_list_item_count",item_count,3600)
            cache.set("ic_error_llist_sum_data",rr,3600)
            re.append(rr)
            datas.append(rr)
            Result['datas'] =re
            all_export_data['datas'] = datas
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("ic_error_llist_tmp_name",tmp_name,3600)
            return Result
        except:
            import traceback;traceback.print_exc()
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
#        datas = cache.get("all_data")
        item_count = cache.get("ic_error_llist_item_count")
        rr = cache.get("ic_error_llist_sum_data")
        from_page_item(request,Result,item_count)
        tmp_name = cache.get("ic_error_llist_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(rr)
        Result['datas'] =re
        return Result



#ic消费明细报表
def get_ic_list_record(request,deptids,userids,dining,st,et,pos_model,operate,totalall=False):
    from mysite.personnel.models import Employee,Department
    from mysite.pos.models import ICConsumerList    
    from  get_reportsfields import get_ic_pos_list
    from mysite.personnel.models.model_meal import Meal
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.utils import get_MultiSelect_objs
    from mysite.sql_utils import p_query,p_execute,p_query_one
    import time
    ids=[]
    deptIDS = []
    datas=[]#储存统计记录   储存的是每行记录
    tag="" #部门是否有人员
    ids = get_MultiSelect_objs(Employee,request)
    ot=['PIN','DeptID']
#       ids=Employee.all_objects.filter(DeptID__in=deptIDS,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)
    if len(ids)==0:
       tag="NoEmp"
    else:
       userids=','.join([str(i) for i in ids])
    Result={}#返回结果 字典
#    sql_add="select user_pin,user_name,dept_id,card,sys_card_no,money,balance,pos_model,dining_id,meal_id,meal_data,dev_sn,dev_serial_num,card_serial_num,log_flag,create_operator,pos_time,convey_time from %s where pos_time>='%s' and pos_time <'%s'" %(ICConsumerList._meta.db_table,st,et)
#    if operate!="9999":
#        sql_add +="and create_operator='%s' "%operate
#    if pos_model!="0":#消费模式
#        sql_add +=" and pos_model='%s' "%pos_model
#    if dining!="0":#餐厅
#          sql_add +=" and dining_id='%s' "%dining
#    if len(ids)==0:#没有选择人 
#        if tag=="NoEmp":
#            sql_add += "and user_id ='0' "
#    else:
#         sql_add += "and user_id in (%s)  order by  pos_time desc "%userids

    if db_select == POSTGRESSQL:
        id_list = userids.split(',')
        user_list = ','.join(("'%s'"%str(i) for i in id_list))
        sql_add = get_ic_list_record_sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,user_list)
    else:
       sql_add = get_ic_list_record_sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,userids)
    r_base,FieldNames,FieldCaption=get_ic_pos_list()
    Result['fieldnames']=FieldNames
    Result['fieldcaptions']=FieldCaption
#    print "sql===============",sql_add
    if not totalall:
        a= time.time()
#        rows = customSql(sql_add,False).fetchall()
        rows = p_query(sql_add)
        b= time.time()
        print "sql____time===================",b-a,r_base
        item_count=len(rows)
        sum_pos_money = 0
        back_money = 0
        sum_back_money = 0
        sum_test_card_money = 0
        sum_test_card_back_money = 0
        try:
            from_page_item(request,Result,item_count)
            all_department = dict_dept_obj()
            all_dining = dict_dining_obj()
            all_meal = dict_meal_obj()
#            Dininghall.objects.all().order_by('id').values_list('id','name')
            #开始进行统计
            r_b = r_base.copy()
            for row in rows:
                r = r_base.copy()
                pos_money = row[5]
                r['user_pin'] = row[0]
                r['user_name'] = row[1]
                r['dept_name'] = all_department[row[2]]
                r['card'] = row[3]
                r['sys_card_no'] = row[4]
                r['money'] = '￥'+ str(pos_money)
                r['balance'] = '￥'+ str(row[6])
                if row[7] == 9:#纠错
                    back_money =pos_money
                    sum_back_money += pos_money
                    pos_money = 0
                if row[7]:
                    r['pos_model'] = CONSUMEMODEL[int(row[7])]
                r['dining'] = all_dining[row[8]]
                if row[9]:
                    r['meal_id'] = all_meal[row[9]]
                else:
                    r['meal_id'] = None
                if row[10]:
                    r['meal_data'] = row[10].strftime("%Y-%m-%d")
                r['dev_sn'] = row[11]
                r['dev_serial_num'] = row[12]
                r['card_serial_num'] = row[13]
                r['log_flag'] = LOGFLAG[int(row[14])]
                r['create_operator'] = row[15]
                r['pos_time'] = row[16].strftime("%Y-%m-%d %H:%M:%S")
                if row[17]:
                    r['convey_time'] = row[17].strftime("%Y-%m-%d %H:%M:%S")
                datas.append(r)
                if pos_model == '9':#纠错
                    sum_pos_money += back_money
                else:
                    sum_pos_money += pos_money
                if int(row[14]) == 5:#发卡日期大于消费时间的卡消费金额
                    sum_test_card_money+=pos_money
                if int(row[14]) == 5 and row[7] == 9:#发卡日期大于消费时间的纠错金额
                    sum_test_card_back_money+=back_money
            try:
                offset = int(request.REQUEST.get('p', 1))
            except:
                offset=1
            d = time.time()
            print "data_list============",d-b
            limit= int(request.POST.get('l', settings.PAGE_LIMIT))
            re=datas[((offset-1)*limit):(offset*limit)]
            all_export_data = Result.copy()
            rr = r_base.copy()
            rr['user_pin'] = _(u"合计：")
            if pos_model == '9':#纠错
                rr['money'] = _(u"纠错总额：") + '￥'+ str(sum_back_money)
                rr['pos_model'] = _(u"消费日期异常：") + '￥'+ str(sum_test_card_back_money)
            else:
                rr['money'] = _(u"实消费总额：") + '￥'+ str(sum_pos_money - sum_back_money)
                rr['pos_model'] = _(u"消费日期异常：") + '￥'+ str(sum_test_card_money - sum_test_card_back_money)
            cache.set("ic_list_item_count",item_count,3600)
            cache.set("ic_list_sum_data",rr,3600)
            re.append(rr)
            datas.append(rr)
            Result['datas'] =re
            all_export_data['datas'] = datas
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("ic_list_tmp_name",tmp_name,3600)
            return Result
        except:
            import traceback;traceback.print_exc()
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
#        datas = cache.get("all_data")
        item_count = cache.get("ic_list_item_count")
        rr = cache.get("ic_list_sum_data")
        from_page_item(request,Result,item_count)
        tmp_name = cache.get("ic_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(rr)
        Result['datas'] =re
        return Result
    
#ID消费明细报表
def get_id_list_record(request,deptids,userids,dining,st,et,pos_model,operate,totalall=False):
    from mysite.personnel.models import Employee,Department
    from  get_reportsfields import get_ic_pos_list
    from mysite.utils import get_MultiSelect_objs
    import time
    ids=[]
    deptIDS = []
    datas=[]#储存统计记录   储存的是每行记录
    tag="" #部门是否有人员
    a= time.time()
    ids = get_MultiSelect_objs(Employee,request)
    ot=['PIN','DeptID']
    if len(ids)==0:
       tag="NoEmp"
    else:
       userids=','.join([str(i) for i in ids])
    Result={}#返回结果 字典
#    sql_add="select user_id,card,money,blance,sn_name,cardserial,serialnum,discount,type_id,dining_id,checktime,create_operator from pos_carcashsz where hide_column in (6,8,9,10,12) and checktime>='%s' and checktime <'%s'" %(st,et)
#    if operate!="9999":
#        sql_add +="and create_operator='%s' "%operate
##    if pos_model!="0":#消费模式
##        sql_add +=" and pos_model='%s' "%pos_model
#    if dining!="0":#餐厅
#        sql_add +=" and dining_id='%s' "%dining
#    if len(ids)==0:#没有选择人 
#        if tag=="NoEmp":
#            sql_add += "and user_id ='0' "
#    else:
#         sql_add += "and user_id in (%s)  order by  checktime desc "%userids
    sql_add = get_id_list_record_sql(st,et,tag,operate,pos_model,dining,ids,userids)
    r_base,FieldNames,FieldCaption=get_ic_pos_list()
    Result['fieldnames']=FieldNames
    Result['fieldcaptions']=FieldCaption
    if not totalall:
#        rows = customSql(sql_add,False).fetchall()
        rows = p_query(sql_add)
        b= time.time()
        print "sql_tim==================",b-a
        item_count=len(rows)
        sum_pos_money = 0
        back_money = 0
        sum_back_money = 0
        sum_total_money = 0
        sum_total_back_money = 0
        try:
            from_page_item(request,Result,item_count)
            all_department = dict_dept_obj()
            all_cash_type = dict_cash_type_obj()
            all_dining = dict_dining_obj()
            if userids:
                all_emp = dict_all_emp_obj()
            #开始进行统计
            c= time.time()
            for row in rows:
                r = r_base.copy()   
                pos_money = row[2]
#                for emp in all_emp:
#                    if row[0] == emp.pk:
                r['user_pin'] = all_emp[row[0]].split("_")[0]
                r['user_name'] = all_emp[row[0]].split("_")[1]
                r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                r['card'] = row[1]
                r['money'] = '￥'+ str(pos_money)
                r['balance'] = '￥'+ str(row[3])
                r['discount'] = row[7]
                r['type_name'] = all_cash_type[row[8]]
                
                if row[8] == 9:#纠错
                    back_money = pos_money
                    sum_back_money += pos_money
                    pos_money = 0
                if row[8] == 10:#计次消费
                    total_money = pos_money
                    sum_total_money += total_money
                    pos_money = 0
                if row[8] == 12:#计次纠错
                    total_back_money = pos_money
                    sum_total_back_money += total_back_money
                    pos_money = 0
                r['dining'] = all_dining[row[9]]
                r['dev_sn'] = row[4]
                r['dev_serial_num'] = row[6]
                r['card_serial_num'] = row[5]
                r['create_operator'] = row[11]
                r['pos_time'] = row[10].strftime("%Y-%m-%d %H:%M:%S")
                datas.append(r)
#                if pos_model == '9':#纠错
#                    sum_pos_money += back_money
#                else:
                sum_pos_money += pos_money
            d= time.time()
            print "date_______time=============",d-c
            try:
                offset = int(request.REQUEST.get('p', 1))
            except:
                offset=1
            limit= int(request.POST.get('l', settings.PAGE_LIMIT))
            re=datas[((offset-1)*limit):(offset*limit)]
            all_export_data = Result.copy()
            rr = r_base.copy()
            rr['user_pin'] = _(u"合计：")
            rr['card'] = _(u"纠错：")+'￥'+ str(sum_back_money)
            rr['money'] = _(u"消费：")+'￥'+ str(sum_pos_money - sum_back_money)
            rr['pos_time'] = _(u"计次成本：")+'￥'+ str(sum_total_money)
            rr['dev_sn'] = _(u"计次纠错：")+'￥'+ str(sum_total_back_money)
            cache.set("id_list_item_count",item_count,3600)
            cache.set("id_list_sum_data",rr,3600)
            re.append(rr)
            datas.append(rr)
            Result['datas'] =re
            all_export_data['datas'] = datas
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("id_list_tmp_name",tmp_name,3600)
            return Result
        except:
            import traceback;traceback.print_exc()
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
#        datas = cache.get("all_data")
        tmp_name = cache.get("id_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("id_list_item_count")
        rr = cache.get("id_list_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(rr)
        Result['datas'] =re
        return Result

        
RECHARGE_TYPE={
            1:_(u'充值'),
            13:_(u'充值优惠'),
                  }

#充值明细报表
def get_recharge_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids):
     from mysite.personnel.models.model_emp import Employee
     from mysite.personnel.models.model_dept import Department
     if get_option("POS_IC"):
        sql=get_ic_recharge_report_sql(d1,d2)
     else:
        sql=get_id_recharge_report_sql(type_id,d1,d2)
     sql+=sql_add
     datas=[]#储存统计记录   储存的是每行记录
     if not totalall :#不分页
#         rows = customSql(sql,False).fetchall()
         rows = p_query(sql)
         item_count=len(rows)
         sum_recharge_money = 0
         sum_yh_money = 0
         sum_test_card_money = 0
         sum_test_yh_money = 0
         try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             #开始进行统计
             if userids:
                all_emp = dict_all_emp_obj()
             for row in rows:
                 r = r_base.copy()
                 recharge_money = row[3]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                 r['card'] = row[1]
                 r['card_serial'] = row[2]
                 r['money'] = '￥'+ str(recharge_money)
                 r['card_blance'] = '￥'+ str(row[4])
                 r['check_time'] = row[5].strftime("%Y-%m-%d %H:%M:%S")
                 r['create_operator'] = str(row[6])
                 if get_option("POS_IC"):
                    r['recharge_type'] = RECHARGE_TYPE[int(row[11])]
                    r['dev_serial_num'] = row[12]
                    r['sys_card_no'] = row[8]
                    if row[11] == 13:
                        yh_money = row[3]
                        sum_yh_money += yh_money
                    if row[7]:
                        r['convey_time'] = row[7].strftime("%Y-%m-%d %H:%M:%S")
                    r['dev_sn'] = row[9]
                    r['log_flag'] = LOGFLAG[int(row[10])]
                    if int(row[10]) == 5:#发卡日期大于充值时间的充值（主要体现在设备的测试记录）
                        sum_test_card_money+=recharge_money
                    if int(row[10]) == 5 and row[11] == 13:#发卡日期大于充值时间的充值优惠（主要体现在设备的测试记录）
                        sum_test_yh_money+=yh_money
                    
                 datas.append(r)
                 sum_recharge_money += recharge_money
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             if get_option("POS_IC"):
                 rr['user_pin'] = _(u"合计：")
                 rr['money'] = _(u"充值合计：")+'￥'+ str(sum_recharge_money - sum_yh_money)
                 rr['recharge_type'] = _(u"优惠合计：")+'￥'+ str(sum_yh_money)
#                 rr['card_blance'] = _(u"测试卡充值：")+'￥'+ str(sum_test_card_money - sum_test_yh_money)
#                 rr['check_time'] = _(u"测试卡优惠：")+'￥'+ str(sum_test_yh_money)
             else:
                 rr['user_pin'] = _(u"合计：")
                 rr['money'] = '￥'+ str(sum_recharge_money)
             cache.set("recharge_list_item_count",item_count,3600)
             cache.set("recharge_list_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
         except:
             import traceback;traceback.print_exc()
     else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("recharge_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("recharge_list_item_count")
        rr = cache.get("recharge_list_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(rr)
        return [re,datas]
    
        
#退款明细报表
def get_reimburese_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    if get_option("POS_IC"):
        sql = get_ic_reimburese_report_sql(type_id,d1,d2)
    else:
        sql = get_id_reimburese_report_sql(type_id,d1,d2)
    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
    if not totalall:
#        rows = customSql(sql,False).fetchall()
        rows = p_query(sql)
        item_count=len(rows)
        sum_recharge_money = 0
        back_money = 0
        try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             if userids:
                all_emp = dict_all_emp_obj()
             #开始进行统计
             for row in rows:
                 r = r_base.copy()
                 recharge_money = row[3]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                        
                 r['card'] = row[1]
                 r['card_serial'] = row[2]
                 r['money'] = '￥'+ str(recharge_money)
                 r['card_blance'] = '￥'+ str(row[4])
                 r['check_time'] = row[5].strftime("%Y-%m-%d %H:%M:%S")
                 r['create_operator'] = str(row[6])
                 if get_option("POS_IC"):
                    r['dev_serial_num'] = row[11]
                    r['sys_card_no'] = row[8]
                    if row[7]:
                        r['convey_time'] = row[7].strftime("%Y-%m-%d %H:%M:%S")
                    r['dev_sn'] = row[9]
                    r['log_flag'] = LOGFLAG[int(row[10])]
                 datas.append(r)
                 sum_recharge_money += recharge_money
              
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             rr['user_pin'] = _(u"合计：")
             rr['money'] = '￥'+ str(sum_recharge_money)
             cache.set("reimburese_item_count",item_count,3600)
             cache.set("reimburese_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
        except:
             import traceback;traceback.print_exc()
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("reimburese_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("reimburese_item_count")
        cache_rr = cache.get("reimburese_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]
        


AllOW_TYPE={
            0:_(u'累加补贴'),
            1:_(u'清零补贴'),
                  }

#卡补贴明细报表
def get_allow_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    if get_option("POS_IC"):
        sql = get_ic_allow_report_sql(type_id,d1,d2)
    else:
        sql = get_id_allow_report_sql(type_id,d1,d2)
    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
    if not totalall:
#        rows = customSql(sql,False).fetchall()
        rows = p_query(sql)
        item_count=len(rows)
        sum_allow_money = 0
        sum_clear_money = 0
        try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             #开始进行统计
             if userids:
                all_emp = dict_all_emp_obj()
             for row in rows:
                 r = r_base.copy()
                 allow_money = row[3]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                 r['card'] = row[1]
                 r['card_serial'] = row[2]
                 r['money'] = '￥'+ str(allow_money)
                 r['card_blance'] = '￥'+ str(row[4])
                 r['check_time'] = row[5].strftime("%Y-%m-%d %H:%M:%S")
                 r['create_operator'] = row[6]
                 if get_option("POS_IC"):
                    r['sys_card_no'] = row[8]
                    r['dev_serial_num'] = row[12]
                    if row[11] == 1:
                        clear_money = row[3]
                        sum_clear_money += clear_money
                    r['allow_type'] = AllOW_TYPE[int(row[11])]
                    if row[7]:
                        r['convey_time'] = row[7].strftime("%Y-%m-%d %H:%M:%S")
                    r['dev_sn'] = row[9]
                    r['log_flag'] = LOGFLAG[int(row[10])]
                 datas.append(r)
                 sum_allow_money += allow_money
              
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             if get_option("POS_IC"):
                 rr['user_pin'] = _(u"合计：")
                 rr['money'] = _(u"补贴合计：") + '￥'+ str(sum_allow_money - sum_clear_money)
                 rr['card_blance'] = _(u"清零合计：") + '￥'+ str(sum_clear_money)
             else:
                 rr['user_pin'] = _(u"合计：")
                 rr['money'] = _(u"补贴合计：") + '￥'+ str(sum_allow_money)
             cache.set("allow_item_count",item_count,3600)
             cache.set("allow_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
        except:
             import traceback;traceback.print_exc()
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("allow_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("allow_item_count")
        cache_rr = cache.get("allow_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]
        


#退卡明细报表
def get_return_card_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    if get_option("POS_IC"):
        sql = get_ic_return_card_report(type_id,d1,d2)
    else:
        sql = get_id_return_card_report(type_id,d1,d2)
    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
    if not totalall:
#         rows = customSql(sql,False).fetchall()
         rows = p_query(sql)
         item_count=len(rows)
         sum_return_money = 0
         try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             if userids:
                all_emp = dict_all_emp_obj()
             #开始进行统计
             for row in rows:
                 r = r_base.copy()
                 return_money = row[5]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                 r['card'] = row[1]
                 r['card_serial'] = row[2]
                 r['check_time'] = row[3].strftime("%Y-%m-%d %H:%M:%S")
                 r['create_operator'] = str(row[4])
                 r['money'] = '￥'+ str(return_money)
                 if get_option("POS_IC"):
                    r['sys_card_no'] = row[6]
                 sum_return_money += return_money
                 datas.append(r)
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             rr['user_pin'] = _(u"合计：")
             rr['user_name'] = item_count
             rr['money'] = '￥'+ str(sum_return_money)
             cache.set("return_card_item_count",item_count,3600)
             cache.set("return_card_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
         except:
             import traceback;traceback.print_exc()
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("return_card_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("return_card_item_count")
        cache_rr = cache.get("return_card_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]
        
        
        
#卡成本报表
def get_cost_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids):
     from mysite.personnel.models.model_emp import Employee
     from mysite.personnel.models.model_dept import Department
     if get_option("POS_IC"):
        sql = get_ic_cost_report_sql(type_id,d1,d2)
     else:
        sql = get_id_cost_report_sql(type_id,d1,d2)
     sql+=sql_add
     datas=[]#储存统计记录   储存的是每行记录
     if not totalall:
#         rows = customSql(sql,False).fetchall()
         rows = p_query(sql)
         sum_cost_money = 0
         item_count=len(rows)
         try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             if userids:
                all_emp = dict_all_emp_obj()
             #开始进行统计
             for row in rows:
                 r = r_base.copy()
                 cost_money = row[5]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                 r['card'] = row[1]
#                 r['card_serial'] = row[2]
                 r['check_time'] = row[3].strftime("%Y-%m-%d %H:%M:%S")
                 r['create_operator'] = str(row[4])
                 r['money'] = '￥'+ str(cost_money)
                 if get_option("POS_IC"):
                    r['sys_card_no'] = row[6]
                 sum_cost_money += cost_money
                 datas.append(r)
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             rr['user_pin'] = _(u"合计：")
             rr['money'] = '￥'+ str(sum_cost_money)
             cache.set("cost_item_count",item_count,3600)
             cache.set("cost_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
         except:
             import traceback;traceback.print_exc()
     else:
        try:
            offset = int(request.REQUEST.get('p', 1))
        except:
            offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("cost_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("cost_item_count")
        cache_rr = cache.get("cost_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]
        


#发卡表
def get_issuecard_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids):
     from mysite.personnel.models.model_emp import Employee
     from mysite.personnel.models.model_dept import Department
     from mysite.personnel.models.model_iccard import ICcard
     if get_option("POS_IC"):
        sql = get_ic_issuecard_report_sql(type_id,d1,d2)
     else:
        sql = get_id_issuecard_report_sql(type_id,d1,d2)
     sql+=sql_add
     datas=[]#储存统计记录   储存的是每行记录
     if not totalall:
#         rows = customSql(sql,False).fetchall()
         rows = p_query(sql)
         item_count=len(rows)
         try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             #开始进行合计
             if userids:
                all_emp = dict_all_emp_obj()
             for row in rows:
                 r = r_base.copy()
                 recharge_money = row[3]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                 r['card'] = row[1]
#                 r['card_privage'] = _(u'普通卡')
#                 r['card_type'] = str(ICcard.objects.get(id = row[3]))
                 r['issue_date'] = row[2].strftime("%Y-%m-%d")
    #             r['valid_date'] = row[4].strftime("%Y-%m-%d %H:%M:%S")
                 r['create_operator'] = str(row[3])
                 if get_option("POS_IC"):
                    r['sys_card_no'] = row[4]
                 datas.append(r)
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             rr['user_pin'] = _(u"合计：")
             rr['user_name'] = str(item_count)
             cache.set("issuecard_item_count",item_count,3600)
             cache.set("issuecard_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
         except:
             import traceback;traceback.print_exc()
     else:
        try:
            offset = int(request.REQUEST.get('p', 1))
        except:
            offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("issuecard_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("issuecard_item_count")
        cache_rr = cache.get("issuecard_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]
        
        
        
#卡余额表
def get_card_blance_report(request,Result,r_base,type_id,d1,d2,sql_add,totalall,userids,ids,operate,tag,card_type = None):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    from mysite.personnel.models.model_iccard import ICcard
    if get_option("POS_IC"):
        sql = get_ic_card_blance_report(userids,ids,operate,tag,d1,d2,card_type)
    else:
        sql = get_id_card_blance_report(userids,ids,operate,tag)
#    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
    if not totalall:
#         rows = customSql(sql,False).fetchall()
         rows = p_query(sql)
         item_count=len(rows)
         sum_blance_money = 0
         try:
             from_page_item(request,Result,item_count)
             all_department = dict_dept_obj()
             all_card_type = dict_card_type_obj()
             all_emp = dict_all_emp_obj()
             #开始进行统计
             for row in rows:
                 r = r_base.copy()
                 blance_money = row[3]
                 r['user_pin'] = all_emp[row[0]].split("_")[0]
                 r['user_name'] = all_emp[row[0]].split("_")[1]
                 r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
                        
                 r['card'] = row[1]
                 if row[2]:
                    r['card_type'] = all_card_type[row[2]]
                 r['money'] = '￥'+ str(blance_money)
#                 r['create_operator'] = str(row[4])
                 if get_option("POS_IC"):
                    r['sys_card_no'] = row[5]
                 sum_blance_money += blance_money
                 datas.append(r)
             try:
                 offset = int(request.REQUEST.get('p', 1))
             except:
                 offset=1
             limit= int(request.POST.get('l', settings.PAGE_LIMIT))
             re=datas[((offset-1)*limit):(offset*limit)]
             rr = r_base.copy()
             rr['user_pin'] = _(u"合计：")
             rr['money'] = '￥'+ str(sum_blance_money)
             cache.set("card_blance_item_count",item_count,3600)
             cache.set("card_blance_sum_data",rr,3600)
             re.append(rr)
             datas.append(rr)
             return [re,datas]
         except:
             import traceback;traceback.print_exc()
    else:
        try:
            offset = int(request.REQUEST.get('p', 1))
        except:
            offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("card_blance_list_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("card_blance_item_count")
        cache_rr = cache.get("card_blance_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]
        





#批量充值
def get_batchrecharge_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取批量充值的数据  有金额 与次数'''
#    print ids,'emplist'
    day_money=0
    day_count=0
    sql_add=""
    if operate!="0":#充值与操作员有关 ，所以需要加进去
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 
            if tag=="NoEmp":
               sql_add += "and user_id ='0' "
            get_day_money,get_day_count=get_sql_data(3,d1,d3,sql_add)
            day_money+=get_day_money
            day_count += get_day_count
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(3,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
            day_count += get_day_count
#    print day_money,'cccc'
    return [day_money,day_count]

#卡成本
def get_cardCost_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取卡成本的数据  有金额 与次数'''
#    print ids,'emplist'
    day_money=0
    day_count=0
    sql_add=""
    if operate!="0":#充值与操作员有关 ，所以需要加进去
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(7,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(7,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
            day_count += get_day_count
#    print day_money,'cccc'
    return [day_money,day_count]

#卡管理费
def get_cardboard_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取卡成本的数据  有金额 与次数'''
#    print ids,'emplist'
    day_money=0
    sql_add=""
    if operate!="0":#
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
               sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(11,d1,d3,sql_add)
        day_money+=get_day_money
        
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(11,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
    return day_money


#支出卡成本
def get_exCardCost_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取支出卡成本的数据  有金额 与次数'''
#    print ids,'emplist'
    day_money=0
    day_count=0
    sql_add=""
    if operate!="0":#与操作员有关 ，所以需要加进去
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
               sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(4,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(4,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
            day_count += get_day_count
    return [day_money,day_count]


#手工补消费
def get_handConsume_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取手工补消费的数据  有金额 与次数'''
#    print ids,'emplist'
    day_money=0
    day_count=0
    sql_add=""
    if dining!="0":#判断选没选择餐厅
            sql_add+="and dining='%s' "%dining
    if meal!="0":#有餐别就获取 餐别的的打卡时间
           starttime,endtime=Meal.objects.filter(id=meal).values_list('starttime','endtime')[0]
           s1=d1.strftime("%Y-%m-%d")+' '+starttime.strftime("%H:%M:%S")
           s2=d1.strftime("%Y-%m-%d")+' '+endtime.strftime("%H:%M:%S")
           d1=datetime.datetime.strptime(s1,'%Y-%m-%d %H:%M:%S')
           d3=datetime.datetime.strptime(s2,'%Y-%m-%d %H:%M:%S')
           if d1>d3:
               d3=d3+datetime.timedelta(days=1)
    sql_add_bak=sql_add
    
    if operate!="0":#与操作员有关 ，所以需要加进去
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(8,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(8,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
            day_count += get_day_count
#    print day_money,'cccc'
    return [day_money,day_count]


#消费回滚
def get_reback_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取回滚的数据  有金额 与次数'''
    day_money=0
    day_count=0
    sql_add=""
    if dining!="0":#判断选没选择餐厅
            sql_add+="and dining='%s' "%dining
    sql_add_bak=sql_add
    if meal!="0":#有餐别就获取 餐别的的打卡时间
           starttime,endtime=Meal.objects.filter(id=meal).values_list('starttime','endtime')[0]
           s1=d1.strftime("%Y-%m-%d")+' '+starttime.strftime("%H:%M:%S")
           s2=d1.strftime("%Y-%m-%d")+' '+endtime.strftime("%H:%M:%S")
           d1=datetime.datetime.strptime(s1,'%Y-%m-%d %H:%M:%S')
           d3=datetime.datetime.strptime(s2,'%Y-%m-%d %H:%M:%S')
           if d1>d3:
               d3=d3+datetime.timedelta(days=1)
    sql_add_bak=sql_add
    
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(9,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(9,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
            day_count += get_day_count
    return [day_money,day_count]

#计次回滚
def get_count_reback_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取回滚的数据  有金额 与次数'''
    day_money=0
    day_count=0
    sql_add=""
    if dining!="0":#判断选没选择餐厅
            sql_add+="and dining='%s' "%dining
    sql_add_bak=sql_add
    if meal!="0":#有餐别就获取 餐别的的打卡时间
           starttime,endtime=Meal.objects.filter(id=meal).values_list('starttime','endtime')[0]
           s1=d1.strftime("%Y-%m-%d")+' '+starttime.strftime("%H:%M:%S")
           s2=d1.strftime("%Y-%m-%d")+' '+endtime.strftime("%H:%M:%S")
           d1=datetime.datetime.strptime(s1,'%Y-%m-%d %H:%M:%S')
           d3=datetime.datetime.strptime(s2,'%Y-%m-%d %H:%M:%S')
           if d1>d3:
               d3=d3+datetime.timedelta(days=1)
    sql_add_bak=sql_add
    
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(12,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(12,d1,d3,sql_add)
            sql_add=sql_add_bak
            day_money += get_day_money
            day_count += get_day_count
    return [day_money,day_count]





#消费
def get_consume_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取每日消费的数据  有金额 与次数'''
    day_money=0
    day_count=0
    day_back_money=0
    day_back_count=0
    money=0
    sql_add=""
    if dining!="0":#判断选没选择餐厅
        sql_add+="and dining='%s' "%dining
    
    if meal!="0":#有餐别就获取 餐别的的打卡时间
        starttime,endtime=Meal.objects.filter(id=meal).values_list('starttime','endtime')[0]
        s1=d1.strftime("%Y-%m-%d")+' '+starttime.strftime("%H:%M:%S")
        s2=d1.strftime("%Y-%m-%d")+' '+endtime.strftime("%H:%M:%S")
        d1=datetime.datetime.strptime(s1,'%Y-%m-%d %H:%M:%S')
        d3=datetime.datetime.strptime(s2,'%Y-%m-%d %H:%M:%S')
        if d1>d3:
            d3=d3+datetime.timedelta(days=1)
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 及部门的时候  pos_type=6
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(6,d1,d3,sql_add)
        get_dayback_money,get_dayback_count=get_sql_data(9,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
        day_back_money+=get_dayback_money
        day_back_count += get_dayback_count
        money= day_money-day_back_money
    else:
        for emp in ids:
            sql_add += "and user_id='%s' "%emp
            get_day_money,get_day_count=get_sql_data(6,d1,d3,sql_add)
            get_dayback_money,get_dayback_count=get_sql_data(9,d1,d3,sql_add)
            sql_add=sql_add_bak#还原开始的sql 语句
            day_money += get_day_money
            day_count += get_day_count
            day_back_money+=get_dayback_money
            day_back_count += get_dayback_count
            money= day_money-day_back_money
    return [day_money,day_count,day_back_money,day_back_count,money]


#补贴
def get_allowance_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取每日补贴的数据  有金额 与次数'''
    day_money=0
    day_count=0
    sql_add=""
    if operate!="0":#与操作员有关 ，所以需要加进去  补贴=2
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak=sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(2,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
        
    else:
        for emp in ids:
            sql_add += "and user_id='%s' "%emp
            get_day_money,get_day_count = get_sql_data(2,d1,d3,sql_add)
            sql_add=sql_add_bak#还原开始的sql 语句
            day_money += get_day_money
            day_count += get_day_count
    return [day_money,day_count]


#退款
def get_refund_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取每日退款的数据  有金额 与次数  postype_id=5'''
    day_money=0
    day_count=0
    sql_add=""
    if operate!="0":#操作员有关 ，所以需要加进去 
        sql_add +="and create_operator='%s' "%operate
    sql_add_bak = sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(5,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
        
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(5,d1,d3,sql_add)
            sql_add=sql_add_bak#还原开始的sql 语句
            day_money += get_day_money
            day_count += get_day_count
    
    return [day_money,day_count]

#计次汇总
def get_count_data(ids,dining,meal,operate,d1,d3,tag):
    '''获取每日退款的数据  有金额 与次数  postype_id=5'''
    day_money=0
    day_count=0
    day_back_money=0
    day_back_count=0
    money=0
    sql_add=""
    if dining!="0":#判断选没选择餐厅
            sql_add+="and dining='%s' "%dining
    if meal!="0":#有餐别就获取 餐别的的打卡时间
           starttime,endtime=Meal.objects.filter(id=meal).values_list('starttime','endtime')[0]
           s1=d1.strftime("%Y-%m-%d")+' '+starttime.strftime("%H:%M:%S")
           s2=d1.strftime("%Y-%m-%d")+' '+endtime.strftime("%H:%M:%S")
           d1=datetime.datetime.strptime(s1,'%Y-%m-%d %H:%M:%S')
           d3=datetime.datetime.strptime(s2,'%Y-%m-%d %H:%M:%S')
           if d1>d3:
               d3=d3+datetime.timedelta(days=1)
    sql_add_bak = sql_add
    if len(ids)==0:#没有选择人 
        if tag=="NoEmp":
           sql_add += "and user_id ='0' "
        get_day_money,get_day_count=get_sql_data(10,d1,d3,sql_add)
        get_dayback_money,get_dayback_count=get_sql_data(12,d1,d3,sql_add)
        day_money+=get_day_money
        day_count += get_day_count
        day_back_money+=get_dayback_money
        day_back_count += get_dayback_count
        money= day_money-day_back_money
        
        
    else:
        for emp in ids:
            sql_add += "and user_id ='%s' "%emp
            get_day_money,get_day_count = get_sql_data(10,d1,d3,sql_add)
            get_dayback_money,get_dayback_count=get_sql_data(12,d1,d3,sql_add)
            sql_add=sql_add_bak#还原开始的sql 语句
            day_money += get_day_money
            day_count += get_day_count
            day_back_money+=get_dayback_money
            day_back_count += get_dayback_count
            money= day_money-day_back_money
            
    return [day_money,day_count,day_back_money,day_back_count,money]



#得到每天的统计数据
def get_days_data(typeid,ids,dining,meal,operate,d1,d3,tag):
    '''传递的值: typeid 消费报表类型,ids 人员元组、dining 餐厅  id号 ，meal 餐别 id号 operate 操作员 username'''
    day_pos_count =0
    day_pos_money=0
    day_posback_money=0
    day_posback_count=0
    money=0
    if typeid=="1":#充值
        day_pos_money,day_pos_count=get_recharge_data(ids,dining,meal,operate,d1,d3,tag)
    
    elif typeid =="2":#消费
        day_pos_money,day_pos_count,day_posback_money,day_posback_count,money=get_consume_data(ids,dining,meal,operate,d1,d3,tag)
    elif typeid =="3":#补贴
        day_pos_money,day_pos_count=get_allowance_data(ids,dining,meal,operate,d1,d3,tag)
  
    elif typeid =="4":#退款
        day_pos_money,day_pos_count=get_refund_data(ids,dining,meal,operate,d1,d3,tag)
        
    elif typeid =="10":#计次
        day_pos_money,day_pos_count,day_posback_money,day_posback_count,money=get_count_data(ids,dining,meal,operate,d1,d3,tag)
    return [day_pos_money,day_pos_count,day_posback_money,day_posback_count,money]
            
#日实收现金表
def balance_data(ids,dining,meal,operate,d1,d3,tag):
    '''
    支入结算报表， typeid=5
    post_carcashsz  type_id=1充值 2补贴 5"退款,6消费
    
    '''
    day_count_1 = 0
    day_money_1 = 0#充值
    day_count_2 = 0
    day_money_2 = 0#消费 批量充值
    day_count_3 = 0
    day_money_3 = 0#补贴 
    day_count_4 = 0
    day_money_4 = 0#发卡 卡成本
    day_count_5 = 0
    day_money_5 = 0#计次  回滚
    day_count_6 = 0
    day_money_6 = 0#消费  回滚
    
    board_money = 0 #卡管理费
    
    day_pos_count = 0
    day_pos_money= 0
    day_money_1, day_count_1 = get_recharge_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_2, day_count_2 = get_batchrecharge_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_3, day_count_3 = get_allowance_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_4, day_count_4 = get_cardCost_data(ids,dining,meal,operate,d1,d3,tag)
#    day_money_5, day_count_5 = get_count_reback_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_6, day_count_6 = get_reback_data(ids,dining,meal,operate,d1,d3,tag)
    board_money = get_cardboard_data(ids,dining,meal,operate,d1,d3,tag)
    day_pos_money = day_money_1 + day_money_2+day_money_3+day_money_4+day_money_6+board_money
    
    return [day_count_1,day_money_1,day_count_2,day_money_2,day_count_3,day_money_3, day_count_4,day_money_4,day_count_6,day_money_6, board_money,day_pos_money]

#日实收现金表
def day_include_data(ids,dining,meal,operate,d1,d3,tag):
    '''
    支入结算报表， typeid=5
    post_carcashsz  type_id=1充值 2补贴 5"退款,6消费
    
    '''
    day_count_1 = 0
    day_money_1 = 0#充值
    day_count_2 = 0
    day_money_2 = 0#消费 批量充值
#    day_count_3 = 0
#    day_money_3 = 0#补贴 
    day_count_4 = 0
    day_money_4 = 0#发卡 卡成本
#    day_count_5 = 0
#    day_money_5 = 0#计次  回滚
    money5 = 0 #卡管理费
    
    day_pos_count = 0
    day_pos_money= 0
    day_money_1, day_count_1 = get_recharge_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_2, day_count_2 = get_batchrecharge_data(ids,dining,meal,operate,d1,d3,tag)
#    day_money_3, day_count_3 = get_allowance_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_4, day_count_4 = get_cardCost_data(ids,dining,meal,operate,d1,d3,tag)
#    day_money_5, day_count_5 = get_reback_data(ids,dining,meal,operate,d1,d3,tag)
    money5 = get_cardboard_data(ids,dining,meal,operate,d1,d3,tag)
    day_pos_money = day_money_1 + day_money_2+day_money_4+money5
    
    return [day_count_1,day_money_1,day_count_2,day_money_2,day_count_4,day_money_4,money5,day_pos_money]

#支出结算
def expend_data(ids,dining,meal,operate,d1,d3,tag):
    '''
    支出结算报表， typeid=5
    post_carcashsz  type_id=1充值 2补贴 5"退款,6消费
    
    '''
    day_count_1 = 0
    day_money_1 = 0#金额消费
    day_count_2 = 0
    day_money_2 = 0#计次消费
    day_count_3 = 0
    day_money_3 = 0#手工补消费 
    day_count_4 = 0
    day_money_4 = 0#退款
    day_count_5 = 0
    day_money_5 = 0#支出卡成本
    day_back_count_1=0
    day_back_money_1=0
    day_pos_count = 0
    day_pos_money= 0
    day_money_1, day_count_1,day_back_count_1,day_pos_money,money = get_consume_data(ids,dining,meal,operate,d1,d3,tag)
    #day_money_2, day_count_2,day_back_count_1,day_pos_money,money = get_count_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_3, day_count_3 = get_handConsume_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_4, day_count_4 = get_refund_data(ids,dining,meal,operate,d1,d3,tag)
    day_money_5, day_count_5 = get_exCardCost_data(ids,dining,meal,operate,d1,d3,tag)
    day_pos_money = day_money_1+day_money_3 +day_money_4+day_money_5
    
    return [day_count_1,day_money_1,day_count_3,day_money_3,day_count_4,day_money_4,day_count_5,day_money_5,day_pos_money]


def get_sql_month_data(postype_id,flag,month,s_type,sql_add):
    mon_money=0
    mon_count=0
    year = datetime.datetime.now().year
    if db_select==MYSQL:
        if flag=="M":
            sql="select sum(money)as total ,Month(checktime) as mon  from   pos_carcashsz  where  Month(checktime)='%s' and type_id=%s and year(checktime)='%s' group by Month(checktime)" %(month,postype_id,year)
        else:
            if s_type=="B":#补卡表
                sql="select count(*) as result from   pos_replenishcard  where  Month(time)='%s' and year(time)='%s'" %(month,year) 
            elif s_type=="C":#挂失
                sql="select count(*) as result from   pos_loseunitecard  where Month(time)='%s' and cardstatus='1' and year(time)='%s'"%(month,year) 
            elif s_type=="D":#解挂
                sql="select count(*) as result from   pos_loseunitecard  where  Month(time)='%s' and cardstatus='2' and year(time)='%s'"  %(month,year) 
            else:
                sql="select count(*) as result from   pos_carcashsz  where  Month(checktime)='%s' and type_id=%s and year(checktime)='%s'" %(month,postype_id,year) 
    elif db_select==SQLSERVER:
#select   sum(total)as   total,convert(varchar(7),ldate,120)   as   month    
#  from   total   group   by   convert(varchar(7),ldate,120) 

        if flag=="M":
            sql="select sum(money)as total ,Month(checktime) as mon  from   pos_carcashsz  where  Month(checktime)='%s' and type_id=%s and year(checktime)='%s' group by Month(checktime)" %(month,postype_id,year)
        else:
            if s_type=="B":#补卡表
                sql="select count(*) as result from   pos_replenishcard  where  Month(time)='%s' and year(time)='%s'" %(month,year) 
            elif s_type=="C":#挂失
                sql="select count(*) as result from   pos_loseunitecard  where Month(time)='%s' and cardstatus='1' and year(time)='%s'"%(month,year) 
            elif s_type=="D":#解挂
                sql="select count(*) as result from   pos_loseunitecard  where  Month(time)='%s' and cardstatus='2' and year(time)='%s'"  %(month,year) 
            else:
                sql="select count(*) as result from   pos_carcashsz  where  Month(checktime)='%s' and type_id=%s and year(checktime)='%s'" %(month,postype_id,year) 
        
    else:
        sql=""
    sql+=sql_add
    cs=customSql(sql,False)
    desc=cs.description
    fldNames={}
    i=0
    for c in desc:#            
       fldNames[c[0].lower()]=i
       i=i+1
    rows=cs.fetchall()
    if db_select==MYSQL:
        if rows<>tuple():
            for t in rows:
                if flag=="M":
                    if t[fldNames['total']]:
                        mon_money+=t[fldNames['total']]
                    return mon_money
                else:  
                    mon_count+=t[fldNames['result']]
                    return mon_count
        else:
            return mon_money
    elif db_select==SQLSERVER:
         if len(rows)<>0:
            for t in rows:
                if flag=="M":
                    if t[fldNames['total']]:
                        mon_money+=t[fldNames['total']]
                    return mon_money
                else:  
                    mon_count+=t[fldNames['result']]
                    return mon_count
         else:
            return mon_money
    else:
        return mon_money

   
#餐厅或者部门消费汇总
def dining_or_dept_report(request,Result,r_base,d1,d2,dbname,pos_model):
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.personnel.models.model_dept import Department
    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
    dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
#    sum_breakfast_money = 0
#    sum_lunch_money = 0
#    sum_dinner_money = 0
#    sum_supper_money = 0 
    sum_back_money = 0
    sum_summary_money = 0
    sum_meal_money = 0
    sum_back_count = 0
    sum_pos_count = 0
    sum_summary_count = 0
    summary_total_time = 0
    summary_total_money = 0
    sum_single_money = 0
    sum_dev_money = 0
#    model = ','.join(pos_model+'9')
    datas=[]
    if dbname == 'Dininghall':
        ids=Dininghall.objects.all().order_by('id').values_list('id','name')
    elif dbname == 'Device':
        ids = Device.objects.all().filter(device_type = DEVICE_POS_SERVER).order_by('id').values_list('id','alias','sn')
    elif dbname == 'Department':
        ids=Department.all_objects.all().order_by('id').values_list('id','name')
    from_page_item(request,Result,len(ids))
    for id in ids:
        r=r_base.copy()
        if dbname == 'Dininghall':
            if get_option("POS_IC"):
                sql_db = ic_dining_or_dept_or_device_report_sql(dbname,id[0],d1,d2)
            else:
                sql_db = id_dining_or_dept_or_device_report_sql(dbname,id[0],d1,d2)
        elif dbname == 'Device':
            if get_option("POS_IC"):
                sql_db = ic_dining_or_dept_or_device_report_sql(dbname,id[2],d1,d2)
            else:
                sql_db = id_dining_or_dept_or_device_report_sql(dbname,id[2],d1,d2)
        elif dbname == 'Department':
            if get_option("POS_IC"):
                sql_db = ic_dining_or_dept_or_device_report_sql(dbname,id[0],d1,d2)
            else:
                sql_db = id_dining_or_dept_or_device_report_sql(dbname,id[0],d1,d2)
#        if dbname == 'Dininghall':
#            if get_option("POS_IC"):
#                sql_db = sql%({'where':" from pos_icconsumerlist where  dining_id = %s and pos_time>='%s' and pos_time <'%s'"%(id[0],d1,d2)})
#            else:
#                sql_db = sql%({'where':" from pos_carcashsz where  dining_id = %s and checktime>='%s' and checktime <'%s'"%(id[0],d1,d2)})
#        elif dbname == 'Device':
#            if get_option("POS_IC"):
#                sql_db = sql%({'where':" from pos_icconsumerlist where  dev_sn = '%s' and pos_time>='%s' and pos_time <'%s'"%(id[2],d1,d2)})
#            else:
#                sql_db = sql%({'where':" from pos_carcashsz where  sn_name = '%s' and checktime>='%s' and checktime <'%s'"%(id[2],d1,d2)})
#        elif dbname == 'Department':
#            if get_option("POS_IC"):
#                sql_db = sql%({'where':" from pos_icconsumerlist where  dept_id = %s and pos_time>='%s' and pos_time <'%s'"%(id[0],d1,d2)})
#            else:
#                sql_db = sql%({'where':" from pos_carcashsz where  dept_id = %s and checktime>='%s' and checktime <'%s'"%(id[0],d1,d2)})
#        print "sql================",sql_db
#        row = customSql(sql_db,False).fetchall()
        row = p_query(sql_db)
        if row:
#            breakfast_money = row[0][0] or 0
#            lunch_money = row[0][1] or 0
#            dinner_money = row[0][2] or 0
#            supper_money = row[0][3] or 0
            back_money = row[0][0] or 0
            back_count = row[0][1] or 0
            pos_count = row[0][2] or 0
            all_money = row[0][3] or 0
            total_count = row[0][4] or 0
            single_money = row[0][5] or 0 #手工补单
            summary_count = pos_count-back_count  
            summary_money = all_money - back_money #设备消费结算金额
            summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
            if get_option("POS_ID"):
                total_money = row[0][6] or 0
                total_back_count = row[0][7] or 0
                total_back_money = row[0][8] or 0
                summary_total_count = total_count - total_back_count
                all_total_money = total_money - total_back_money
                r['summary_total_time']=str(summary_total_count)#id消费计次合计
                r['summary_total_money']= '￥'+ str(all_total_money)#id消费计次金额
                summary_total_time +=summary_total_count
                summary_total_money +=all_total_money
            else:
                r['summary_total_time']=str(total_count)
                summary_total_time +=total_count
            r['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
            if dbname == 'Dininghall':
                r['dining_name']=id[1]
            elif dbname == 'Device':
                r['device_name']=id[1]
                r['device_sn']=id[2]
            else:
                r['dept_name']=id[1]
#            r['breakfast_money']=str(breakfast_money)
#            r['lunch_money']=str(lunch_money)
#            r['dinner_money']=str(dinner_money)
#            r['supper_money']=str(supper_money)
            r['meal_money']='￥'+ str(all_money)
            r['back_money']='￥'+ str(back_money)
            r['summary_money']='￥'+ str(summary_money)
            r['back_count']=str(back_count)
            r['pos_count']=str(pos_count)
            r['summary_count']=str(summary_count)
            if dbname in ['Dininghall','Device']:
                r['summary_dev_money']='￥'+ str(summary_dev_money)
                r['add_single_money']='￥'+ str(single_money)
#            sum_breakfast_money +=breakfast_money
#            sum_lunch_money +=lunch_money
#            sum_dinner_money +=dinner_money
#            sum_supper_money +=supper_money
            sum_meal_money +=all_money
            sum_back_money +=back_money
            sum_back_count +=back_count
            sum_pos_count +=pos_count
            sum_summary_count +=summary_count
            sum_summary_money +=summary_money
            sum_single_money +=single_money
            sum_dev_money +=summary_dev_money
            datas.append(r)
    try:
        offset = int(request.REQUEST.get('p', 1))
    except:
        offset=1
    limit= int(request.POST.get('l', settings.PAGE_LIMIT))
    re=datas[((offset-1)*limit):(offset*limit)] #数据分页
    
    rr = r_base.copy()
    if dbname == 'Dininghall':
        rr['dining_name']=_(u"汇总：")
    elif dbname == 'Device':
        rr['device_name']=_(u"汇总：")
    else:
        rr['dept_name']=_(u"汇总：")
    rr['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
#    rr['breakfast_money']=str(sum_breakfast_money)
#    rr['lunch_money']=str(sum_lunch_money)
#    rr['dinner_money']=str(sum_dinner_money)
#    rr['supper_money']=str(sum_supper_money)
    rr['meal_money']='￥'+ str(sum_meal_money)
    rr['back_money']='￥'+ str(sum_back_money)
    rr['summary_money']='￥'+ str(sum_summary_money)
    rr['back_count']=str(sum_back_count)
    rr['pos_count']=str(sum_pos_count)
    rr['summary_count']=str(sum_summary_count)
    if dbname in ['Dininghall','Device']:
        rr['add_single_money']='￥'+ str(sum_single_money)
        rr['summary_dev_money']='￥'+ str(sum_dev_money)
    if get_option("POS_ID"):
        rr['summary_total_time']=str(summary_total_time)
        rr['summary_total_money']='￥'+ str(summary_total_money)
    else:
        rr['summary_total_time']=str(summary_total_time)
    datas.append(rr)
    re.append(rr)
    return [re,datas]

#个人消费汇总
def emp_summary_report(request,Result,r_base,d1,d2,ids,pos_model,totalall):
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    sum_back_money = 0
    sum_summary_money = 0
    sum_meal_money = 0
    sum_back_count = 0
    sum_pos_count = 0
    sum_summary_count = 0
    summary_total_time = 0
    summary_total_money = 0
    sum_single_money = 0
    sum_dev_money = 0
    datas=[]
    userids=','.join([str(i) for i in ids])
    if not totalall:
        if get_option("POS_IC"):
            if db_select == POSTGRESSQL:
                id_list = userids.split(',')
                user_list = ','.join(("'%s'"%str(i) for i in id_list))
                db_sql = ic_emp_summary_report_sql(user_list,d1,d2)
            else:
                db_sql = ic_emp_summary_report_sql(userids,d1,d2)
        else:
            db_sql = id_emp_summary_report_sql(userids,d1,d2)
        if userids:
#            rows = customSql(db_sql,False).fetchall()
             rows = p_query(db_sql)
        else:
            rows = []
        from_page_item(request,Result,len(rows))
        all_department = dict_dept_obj()
        item_count = len(rows)
        if userids:
            all_emp = dict_all_emp_obj()
        if rows:
            for row in rows:
                r=r_base.copy()
                back_money = row[0] or 0
                back_count = row[1] or 0
                pos_count = row[2] or 0
                all_money = row[3] or 0
                total_count = row[4] or 0
                summary_count = pos_count-back_count
                summary_money = all_money - back_money #包含补单金额结算
                if get_option("POS_ID"):
                    total_money = row[5] or 0
                    total_back_count = row[6] or 0
                    total_back_money = row[7] or 0
                    single_money = row[8] or 0  #手工补消费
                    summary_total_count = total_count - total_back_count
                    all_total_money = total_money - total_back_money
                    r['summary_total_time']=str(summary_total_count)#id消费计次合计
                    r['summary_total_money']='￥'+ str(all_total_money)#id消费计次金额
                    summary_total_time +=summary_total_count
                    summary_total_money +=all_total_money
                    r['user_pin'] = all_emp[int(row[9])].split("_")[0]
                    r['user_name'] = all_emp[int(row[9])].split("_")[1]
                    r['dept_name'] = all_department[int(all_emp[int(row[9])].split("_")[2])]
                            
                else:
                    r['user_pin'] = all_emp[int(row[6])].split("_")[0]
                    r['user_name'] = all_emp[int(row[6])].split("_")[1]
                    r['dept_name'] = all_department[int(all_emp[int(row[6])].split("_")[2])]
                    r['summary_total_time']=str(total_count)
                    single_money = row[5] or 0 #手工补消费
                    summary_total_time +=total_count
                summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
                r['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
                r['meal_money']='￥'+ str(all_money)
                r['back_money']='￥'+ str(back_money)
                r['summary_money']='￥'+ str(summary_money)
                r['back_count']=str(back_count)
                r['pos_count']=str(pos_count)
                r['summary_count']=str(summary_count)
                r['summary_dev_money']='￥'+ str(summary_dev_money)
                r['add_single_money']='￥'+ str(single_money)
                sum_meal_money +=all_money 
                sum_back_money +=back_money
                sum_back_count +=back_count
                sum_pos_count +=pos_count
                sum_summary_count +=summary_count
                sum_summary_money +=summary_money
                sum_single_money +=single_money
                sum_dev_money +=summary_dev_money
                datas.append(r)
        try:
            offset = int(request.REQUEST.get('p', 1))
        except:
            offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        re=datas[((offset-1)*limit):(offset*limit)] #数据分页
        rr = r_base.copy()
        rr['user_pin']=_(u"汇总：")
        rr['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
        rr['meal_money']='￥'+ str(sum_meal_money)
        rr['back_money']='￥'+ str(sum_back_money)
        rr['summary_money']='￥'+ str(sum_summary_money)
        rr['back_count']=str(sum_back_count)
        rr['pos_count']=str(sum_pos_count)
        rr['summary_count']=str(sum_summary_count)
        rr['add_single_money']='￥'+ str(sum_single_money)
        rr['summary_dev_money']='￥'+ str(sum_dev_money)
        
        if get_option("POS_ID"):
            rr['summary_total_time']=str(summary_total_time)
            rr['summary_total_money']='￥'+ str(summary_total_money)
        else:
            rr['summary_total_time']=str(summary_total_time)
        cache.set("emp_summary_sum_data",rr,3600)
        cache.set("emp_summary_item_count",item_count,3600)
        datas.append(rr)
        re.append(rr)
        return [re,datas]
    else:
        try:
             offset = int(request.REQUEST.get('p', 1))
        except:
             offset=1
        limit= int(request.POST.get('l', settings.PAGE_LIMIT))
        tmp_name = cache.get("emp_summary_tmp_name")
        attrs, admin_attrs, data=pos_load_tmp_file(tmp_name)
        datas = data[0:-1]
        item_count = cache.get("emp_summary_item_count")
        cache_rr = cache.get("emp_summary_sum_data")
        from_page_item(request,Result,item_count)
        re=datas[((offset-1)*limit):(offset*limit)]
        re.append(cache_rr)
        return [re,datas]



#收支汇总报表
def SZ_summary_report(request,Result,r_base,d1,d2,check_opreate):
    from django.contrib.auth.models import User
    from mysite.pos.models.model_cardmanage import CardManage
    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
    dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
    sum_recharge_money = 0
    sum_recharge_count = 0
    sum_refund_money = 0
    sum_refund_count = 0
    sum_cost_money = 0
    sum_manage_money = 0
    sum_hairpin_count = 0
    sum_back_card_count = 0
    sum_back_card_money = 0
    sum_sz_money = 0
    datas=[]
    operate_list = []
    if get_option("POS_IC"):
        sql_db = ic_SZ_summary_report(d1,d2,check_opreate)
    else:
        sql_db = id_SZ_summary_report(d1,d2,check_opreate)
#    print "sql================",sql_db
#    row_data = customSql(sql_db,False).fetchall()
    row_data = p_query(sql_db)
    from_page_item(request,Result,len(row_data))
    for row in row_data:
        r=r_base.copy()
        if row:
            recharge_money = row[0] or 0
            recharge_count = row[1] or 0
            refund_money = row[2] or 0
            refund_count = row[3] or 0
            cost_money = row[4] or 0
            manage_money = row[5] or 0 
            hairpin_count = row[6] or 0
            back_card_count = row[7] or 0 
            back_card_money = row[8] or 0 
            sz_money = recharge_money - refund_money + cost_money + manage_money - back_card_money
            r['summary_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
            r['recharge_money']='￥'+ str(recharge_money)
            r['recharge_count']=str(recharge_count)
            r['refund_money']='￥'+ str(refund_money)
            r['refund_count']=str(refund_count)
            r['cost_money']='￥'+ str(cost_money)
            r['manage_money']='￥'+ str(manage_money)
            r['hairpin_count']=str(hairpin_count)
            r['back_card_count']=str(back_card_count)
            r['back_card_money']='￥'+ str(back_card_money)
            r['sz_money']='￥'+ str(sz_money)
            if check_opreate == 'checked':
                r['operate']=str(row[9])
            else:
                r['operate']=_(u'全部')
            sum_recharge_money +=recharge_money
            sum_recharge_count +=recharge_count
            sum_refund_money +=refund_money
            sum_refund_count +=refund_count
            sum_cost_money +=cost_money
            sum_manage_money +=manage_money
            sum_hairpin_count +=hairpin_count
            sum_back_card_count +=back_card_count
            sum_back_card_money +=back_card_money
            sum_sz_money +=sz_money
            if check_opreate == 'checked':
                if row[9]:
                    r['operate']=str(row[9])
                    datas.append(r)
            else:
               r['operate']=_(u'全部')
               datas.append(r)
            
    try:
        offset = int(request.REQUEST.get('p', 1))
    except:
        offset=1
    limit= int(request.POST.get('l', settings.PAGE_LIMIT))
    re=datas[((offset-1)*limit):(offset*limit)] #数据分页
    
    rr = r_base.copy()
    
    rr['operate']=_(u"汇总：")
    rr['summary_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
    rr['recharge_money']='￥'+ str(sum_recharge_money)
    rr['recharge_count']=str(sum_recharge_count)
    rr['refund_money']='￥'+ str(sum_refund_money)
    rr['refund_count']=str(sum_refund_count)
    rr['cost_money']='￥'+ str(sum_cost_money)
    rr['manage_money']='￥'+ str(sum_manage_money)
    rr['hairpin_count']=str(sum_hairpin_count)
    rr['back_card_count']=str(sum_back_card_count)
    rr['back_card_money']='￥'+ str(sum_back_card_money)
    rr['sz_money']='￥'+ str(sum_sz_money)
    datas.append(rr)
    re.append(rr)
    return [re,datas]

def monthReports(r_base):
    datas=[]
    total_count_1=0#开户数
    total_count_2=0#退卡数
    total_count_3=0
    total_count_4=0
    total_count_5=0
    total_money_1=0
    total_money_2=0
    total_money_3=0
    total_money_4=0
    total_money_5=0
    total_money_6=0
    
    year = datetime.datetime.now().year
    sql_add=""
#    if len(ids)==0:#没有选择人 
    for i in range(1,13) :
        count1 = get_sql_month_data(7,"C",i,"A",sql_add)#开户数
        count2 = get_sql_month_data(4,"C",i,"A",sql_add)#退卡数
        count3 = get_sql_month_data(7,"C",i,"B",sql_add)#补卡数
        count4 = get_sql_month_data(7,"C",i,"C",sql_add)#挂失数
        count5 = get_sql_month_data(7,"C",i,"D",sql_add)#解挂数
        money1 = get_sql_month_data(6,"M",i,"F",sql_add)#消费
        money2 = get_sql_month_data(1,"M",i,"F",sql_add)#充值
        money3 = get_sql_month_data(5,"M",i,"F",sql_add)#退款
        money4 = get_sql_month_data(2,"M",i,"F",sql_add)#补贴
        money5 = get_sql_month_data(9,"M",i,"F",sql_add)#纠错
        money6 = get_sql_month_data(8,"M",i,"F",sql_add)#补消费
        r=r_base.copy()
        r["month"]=str(year)+"-"+str(i)
        r["count1"]=count1#开户数
        r["count2"]=count2#退卡数
        r["count3"]=count3#补卡数
        r["count4"]=count4#挂失数
        r["count5"]=count5#解挂数
        r["money1"]=str(money1)#消费
        r["money2"]=str(money2)#充值
        r["money3"]=str(money3)#退款
        r["money4"]=str(money4)#补贴
        r["money5"]=str(money5)#纠错
        r["money6"]=str(money6)#补消费
        
        total_count_1+=count1
        total_count_2+=count2
        total_count_3+=count3
        total_count_4+=count4
        total_count_5+=count5
        total_money_1+=money1
        total_money_2+=money2
        total_money_3+=money3
        total_money_4+=money4
        total_money_5+=money5
        total_money_6+=money6
        datas.append(r)
    rr = r.copy()
    rr["month"]=_(u"总计")
    rr["count1"]=total_count_1#开户数
    rr["count2"]=total_count_2#退卡数
    rr["count3"]=total_count_3#补卡数
    rr["count4"]=total_count_4#挂失数
    rr["count5"]=total_count_5#解挂数
    rr["money1"]=str(total_money_1)#消费
    rr["money2"]=str(total_money_2)#充值
    rr["money3"]=str(total_money_3)#退款
    rr["money4"]=str(total_money_4)#补贴
    rr["money5"]=str(total_money_5)#纠错
    rr["money6"]=str(total_money_6)#补消费
    datas.append(rr)
#    datas.insert(0,rr)
#    else:
#        for emp in ids:
#            sql_add += "and user_id ='%s' "%emp
#            get_day_money,get_day_count = get_sql_month_data(5,d1,d3,sql_add)
#            sql_add=sql_add_bak#还原开始的sql 语句
#            day_money += get_day_money
#            day_count += get_day_count
    return datas
    
#消费汇总报表入口
def posStatisticalReports(request,deptids,userids,d1,d2,dining,meal,typeid,operate,pos_model,check_opreate,totalall=False):
    '''
    参数的意义：deptids 部门数组 ，userids 人员组， d1 开始时间 d2 结束时间，。
    dining,餐厅的 的pk，meal 餐别的 pk
    typeid=1 是充值，
    typeid=2 是消费
    typeid=3
    '''
    from mysite.personnel.models import Employee,Department
    from mysite.utils import get_MultiSelect_objs
    ids=[]
    tag="" #部门是否有人员
    ot=['PIN','DeptID']
    ids = get_MultiSelect_objs(Employee,request)
    if len(ids)==0:
        tag="NoEmp"

    Result={}#返回结果 字典
#    item_count=len(ids)
    from mysite.pos.models import HandConsume
    try:
        total_days=int((d2-d1).days)+1#总天数
        if typeid =="7":
            item_count=12
        else:
            item_count=total_days
        
#        limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #每页显示 多少数据
#        if item_count % item_count==0:#page_count获取总页数
#            page_count =item_count/item_count
#        else:
#            page_count =int(item_count/limit)+1   
#        try:
#            offset = int(request.REQUEST.get('p', 1))
#        except:
#            offset=1
#        if offset>page_count and page_count:
#            offset=page_count
#        #定义一些显 总数
#        Result['item_count']=item_count
#        Result['page']=offset
#        Result['limit']=limit
#        Result['from']=(offset-1)*limit+1
#        Result['page_count']=page_count
        total_count=0
        total_money=0
        total_back_count=0
        total_back_money=0
        summoney=0
        #充值
        total_count_1=0
        total_money_1=0
        #消费  批量充值
        total_count_2=0
        total_money_2=0
        #补贴  
        total_count_3=0
        total_money_3=0
        #退款 卡成本
        total_count_4=0
        total_money_4=0
        
        #计次 回滚
        total_count_5=0
        total_money_5=0
        
        #消费 回滚
        total_count_11=0
        total_money_11=0
        
        
        #金额消费
        total_count_6=0
        total_money_6=0


        #计次消费
        total_count_7=0
        total_money_7=0


        #手工补消费
        total_count_8=0
        total_money_8=0


        #退款
        total_count_9=0
        total_money_9=0
        
        #支出卡成本
        total_count_10=0
        total_money_10=0
        board_money = 0 #卡管理费
        exceed_money=0
        include_money=0
        
        datas=[]#储存统计记录   储存的是每行记录
        r_base,FieldNames,FieldCaption=get_posreprots_fields(typeid)
        Result['fieldnames']=FieldNames
        Result['fieldcaptions']=FieldCaption
        if typeid =="7":#月结汇总
            datas=monthReports(r_base)
            Result['datas']=datas
            return Result
        elif typeid=="110":#餐厅汇总
            datas,all_data=dining_or_dept_report(request,Result,r_base,d1,d2,'Dininghall',pos_model)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
            Result['datas']=datas
            return Result
        elif typeid=="120":#部门汇总
            datas,all_data=dining_or_dept_report(request,Result,r_base,d1,d2,'Department',pos_model)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
            Result['datas']=datas
            return Result
        elif typeid=="130":# 个人汇总
            datas,all_data=emp_summary_report(request,Result,r_base,d1,d2,ids,pos_model,totalall)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("emp_summary_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="140":#设备汇总
            datas,all_data=dining_or_dept_report(request,Result,r_base,d1,d2,'Device',pos_model)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
            Result['datas']=datas
            return Result
        elif typeid=="150":#收支汇总
            datas,all_data=SZ_summary_report(request,Result,r_base,d1,d2,check_opreate)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
            Result['datas']=datas
            return Result
        else: 
            for i in  range(total_days-1):
                r=r_base.copy()
                d3=d1+datetime.timedelta(days=1)
                if typeid=="5":#支入
    #                per_count_1,per_money_1,per_count_2,per_money_2,per_count_3,per_money_3,per_count_4,per_money_4,per_count_5,per_money_5,day_money = balance_data(ids,dining,meal,operate,d1,d3,tag)
                    per_count_1,per_money_1,per_count_2,per_money_2,per_count_4,per_money_4,money_board,day_money = day_include_data(ids,dining,meal,operate,d1,d3,tag)
                    r["date"] = d1.strftime("%Y-%m-%d")
                    r["count1"] = str(per_count_1)
                    r["money1"] = str(per_money_1)
    #                    r["count2"] = str(per_count_2)
    #                    r["money2"] = str(per_money_2)
    #                r["count3"] = str(per_count_3)
    #                r["money3"] = str(per_money_3)
                    r["count4"] = str(per_count_4)
                    r["money4"] = str(per_money_4)
    #                r["count5"] = str(per_count_5)
    #                r["money5"] = str(per_money_5)
                    r["money6"] = str(money_board)
                    r["money"]  = str(day_money)
                    
                    datas.append(r)
                    total_count_1 += per_count_1
                    total_money_1 += per_money_1
                    #消费 批量充值
    #                    total_count_2 += per_count_2
    #                    total_money_2 += per_money_2
                    #补贴
    #                total_count_3 += per_count_3
    #                total_money_3 += per_money_3
                    #退款 卡成本
                    total_count_4 += per_count_4
                    total_money_4 += per_money_4
                    #回滚
    #                total_count_5 += per_count_5
    #                total_money_5 += per_money_5
                    board_money += money_board
                    total_money += day_money
                elif typeid=="6":#营业报表
                    per_count_6,per_money_6,per_count_7,per_money_7,per_count_8,per_money_8,per_count_9,per_money_9,per_count_10,per_money_10,b_money,in_money = balance_data(ids,dining,meal,operate,d1,d3,tag)
                    per_count_1,per_money_1,per_count_3,per_money_3,per_count_4,per_money_4,per_count_5,per_money_5,out_money = expend_data(ids,dining,meal,operate,d1,d3,tag)
                    r["date"] = d1.strftime("%Y-%m-%d")
                    r["count1"] = str(per_count_1)
                    r["money1"] = str(per_money_1)
    #                    r["count2"] = str(per_count_2)#计次消费
    #                    r["money2"] = str(per_money_2)
                    r["count3"] = str(per_count_3)
                    r["money3"] = str(per_money_3)
                    r["count4"] = str(per_count_4)
                    r["money4"] = str(per_money_4)
                    r["count5"] = str(per_count_5)
                    r["money5"] = str(per_money_5)
                    
                    r["count6"] = str(per_count_6)
                    r["money6"] = str(per_money_6)
    #                    r["count7"] = str(per_count_7)
    #                    r["money7"] = str(per_money_7)
                    r["count8"] = str(per_count_8)
                    r["money8"] = str(per_money_8)
                    r["count9"] = str(per_count_9)
                    r["money9"] = str(per_money_9)
                    r["count10"] = str(per_count_10)#消费回滚
                    r["money10"] = str(per_money_10)
    #                    r["count11"] = str(per_count_11)#计次回滚
    #                    r["money11"] = str(per_money_11)
                    r["board_money"] = str(b_money)
                    r["in_money"] = str(in_money)
                    r["out_money"] = str(out_money)
                    
                    
                    m_total = in_money-out_money
                    if m_total>0:
                        r["money"] = u"%s:" %_(u"支入")+str(m_total)
                    elif m_total<0:
                        r["money"] = u"%s:" %_(u"支出")+str(-m_total)
                    else:
                        r["money"] = str(m_total)
                    
    #                    r["money"]  = str(in_money-out_money)
                    datas.append(r)
                    total_count_1 += per_count_6
                    total_money_1 += per_money_6
                    #消费 批量充值
    #                    total_count_2 += per_count_7
    #                    total_money_2 += per_money_7
                    #补贴
                    total_count_3 += per_count_8
                    total_money_3 += per_money_8
                    #退款 卡成本
                    total_count_4 += per_count_9
                    total_money_4 += per_money_9
                    #计次回滚
    #                    total_count_5 += per_count_11
    #                    total_money_5 += per_money_11
                    #消费回滚
                    total_count_11 += per_count_10
                    total_money_11+= per_money_10
                    
                    
                    #金额消费
                    total_count_6 += per_count_1
                    total_money_6 += per_money_1
                    #计次消费
    #                    total_count_7 += per_count_2
    #                    total_money_7 += per_money_2
                    #手工补消费
                    total_count_8 += per_count_3
                    total_money_8 += per_money_3
                    #退款
                    total_count_9 += per_count_4
                    total_money_9 += per_money_4
                    #支出卡成本
                    total_count_10 += per_count_5
                    total_money_10 += per_money_5
                    
                    total_money += (in_money-out_money)
                    
                    board_money +=b_money
                    include_money+=in_money
                    exceed_money+=out_money
                                
            
                    
                else:
                    if typeid == '10' or typeid =='2':
                        day_money,day_pos_count,day_back_money,day_back_count,smoney=get_days_data(typeid,ids,dining,meal,operate,d1,d3,tag)
                        r["date"]=d1.strftime("%Y-%m-%d")
                        r["money"]=str(day_money)
                        r["money1"]=str(day_back_money)
                        r["money2"]=str(smoney)
                        if  "count" in r.keys():
                            r["count"]=str(day_pos_count)
                        if  "count1" in r.keys():
                            r["count1"]=str(day_back_count)
                        datas.append(r)
                        total_money+=day_money
                        total_count+=day_pos_count
                        total_back_money+=day_back_money
                        total_back_count+=day_back_count
                        summoney += smoney
                        d1=d3
                        
                    else:
                        day_money,day_pos_count,day_back_money,day_back_count,money=get_days_data(typeid,ids,dining,meal,operate,d1,d3,tag)
                        r["date"]=d1.strftime("%Y-%m-%d")
                        r["money"]=str(day_money)
                        if  "count" in r.keys():
                            r["count"]=str(day_pos_count)
                        datas.append(r)
                        total_money+=day_money
                        total_count+=day_pos_count
                d1=d3
            rr=r_base.copy()
            if typeid=="5":
                rr["date"] = _("总计")
                rr["count1"] = str(total_count_1)
                rr["money1"] = str(total_money_1)
#                rr["count2"] = str(total_count_2)
#                rr["money2"] = str(total_money_2)
    #            rr["count3"] = str(total_count_3)
    #            rr["money3"] = str(total_money_3)
                rr["count4"] = str(total_count_4)
                rr["money4"] = str(total_money_4)
    #            rr["count5"] = str(total_count_5)
    #            rr["money5"] = str(total_money_5)
                rr["money6"] = str(board_money)
                rr["money"] = str(total_money)
                
            elif typeid=="6":
                rr["date"] = _("总计")
                rr["count1"] = str(total_count_6)
                rr["money1"] = str(total_money_6)
#                rr["count2"] = str(total_count_7)#计次
#                rr["money2"] = str(total_money_7)
                rr["count3"] = str(total_count_8)
                rr["money3"] = str(total_money_8)
                rr["count4"] = str(total_count_9)
                rr["money4"] = str(total_money_9)
                rr["count5"] = str(total_count_10)
                rr["money5"] = str(total_money_10)
                
                rr["count6"] = str(total_count_1)
                rr["money6"] = str(total_money_1)
#                rr["count7"] = str(total_count_2)
#                rr["money7"] = str(total_money_2)
                rr["count8"] = str(total_count_3)
                rr["money8"] = str(total_money_3)
                rr["count9"] = str(total_count_4)
                rr["money9"] = str(total_money_4)
                rr["count10"] = str(total_count_11)#消费回滚
                rr["money10"] = str(total_money_11)
#                rr["count11"] = str(total_count_5)#计次回滚
#                rr["money11"] = str(total_money_5)
                rr["in_money"] = str(include_money)
                rr["out_money"] = str(exceed_money)
                rr["board_money"] = str(board_money)
                
#                rr["money"] = str(total_money)
               
                if total_money>0:
                    rr["money"] = u"%s:" %_(u"支入")+str(total_money)
                elif total_money<0:
                    rr["money"] = u"%s:" %_(u"支出")+str(-total_money)
                else:
                    rr["money"] = str(total_money)
                
               
                
            else:
                if typeid == '10' or typeid =='2':
                    rr["date"]=_("总计")
                    if  "count" in rr.keys():
                        rr["count"]=str(total_count)
                    rr["money"]=str(total_money)
                    if  "count1" in rr.keys():
                      rr["count1"]=str(total_back_count)
                    rr["money1"]=str(total_back_money)
                    rr["money2"]=str(total_money-total_back_money)
                    
                else:
                    rr["date"]=_("总计")
                    if  "count" in rr.keys():
                        rr["count"]=str(total_count)
                    rr["money"]=str(total_money)
            
            
            datas.append(rr)
            Result['datas']=datas
            
            return Result
                
            
    
    except:
          import traceback;traceback.print_exc()
    
    
  
#消费报表点
def pos_list_Reports(request,deptids,userids,d1,d2,dining,meal,typeid,operate,pos_model,check_opreate,totalall=False):
    '''
    参数的意义：deptids 部门数组 ，userids 人员组， d1 开始时间 d2 结束时间，。
    dining,餐厅的 的pk，meal 餐别的 pk
    typeid=1 是充值，
    typeid=2 是消费
    typeid=3
    '''
    from mysite.personnel.models import Employee,Department
    from mysite.utils import get_MultiSelect_objs
    ids=[]
    tag="" #部门是否有人员
    ot=['PIN','DeptID']
    ids = get_MultiSelect_objs(Employee,request)
    if len(ids)==0:
        tag="NoEmp"
    else:
        userids=','.join([str(i) for i in ids])
    sql_add = ""
    if operate!="9999":
        sql_add +=" and create_operator='%s' "%operate
    if typeid in ['12']:
        if len(ids)==0:#没有选择人 
            if tag=="NoEmp":
                sql_add += " and UserID_id ='0' "
        else:
             sql_add += " and UserID_id in (%s) "%userids
    else:
        if len(ids)==0:#没有选择人 
            if tag=="NoEmp":
                sql_add += " and user_id ='0' "
        else:
             sql_add += " and user_id in (%s) "%userids
        
    Result={}#返回结果 字典
#    item_count=len(ids)
    try:
        datas=[]#储存统计记录   储存的是每行记录
        if typeid != '14':
            r_base,FieldNames,FieldCaption=get_posreprots_fields(typeid)
            Result['fieldnames']=FieldNames
            Result['fieldcaptions']=FieldCaption
        if typeid=="1":#充值表
            sql_add += "order by checktime desc"
            datas,all_data=get_recharge_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("recharge_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="13":#发卡表
            sql_add += "order by checktime desc"
            datas,all_data=get_issuecard_report(request,Result,r_base,7,d1,d2,sql_add,totalall,userids)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("issuecard_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="12":# 卡余额表
            card_type = request.GET.get('card_type',"")
            if card_type :#无卡退卡表
                datas,all_data=get_card_blance_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids,ids,operate,tag,card_type)
            else:
                datas,all_data=get_card_blance_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids,ids,operate,tag)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("card_blance_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="7":#卡成本
            sql_add += "order by checktime desc"
            datas,all_data=get_cost_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("cost_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="4":#退卡
            sql_add += "order by checktime desc"
            datas,all_data=get_return_card_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("return_card_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="5":#退款
            sql_add += "order by checktime desc"
            datas,all_data=get_reimburese_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("reimburese_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="2":#补贴表
            sql_add += "order by checktime desc"
            datas,all_data=get_allow_report(request,Result,r_base,typeid,d1,d2,sql_add,totalall,userids)
            all_export_data = Result.copy()
            all_export_data['datas'] = all_data
            if not totalall:
                tmp_name = save_pos_tmp_datalist(all_export_data)#保存所有数据临时文件，导出使用
                Result['tmp_name'] = tmp_name
                cache.set("allow_list_tmp_name",tmp_name,3600)
            Result['datas']=datas
            return Result
        elif typeid=="14":
            return get_ic_error_list_record(request,d1,d2,totalall=False)
    except:
          import traceback;traceback.print_exc()
