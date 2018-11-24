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
from  mysite.pos.get_reportsfields  import get_posreprots_fields
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

#分页sql拼接
def report_paging_sql(sort_column,sql_add,_begin,_end):
    sql_data = 'select * from (select * ,row_number() over (order by %s desc) as r from (%s)  a ) t where t.r>%s and t.r<=%s'%(sort_column,sql_add,_begin,_end)
    return sql_data

        

#ic消费异常明细报表
def get_ic_error_list_record(hander,request,st,et,**arg):
    from mysite.personnel.models import Employee,Department
    from mysite.pos.models import IcErrorLog    
    from mysite.personnel.models.model_meal import Meal
    from mysite.iclock.models.model_dininghall import Dininghall
    import time
    sql_add="select user_pin,user_name,dept,card,sys_card_no,money,balance,pos_model,dining_id,meal_id,meal_data,dev_sn,dev_serial_num,card_serial_num,log_flag,create_operator,pos_time,convey_time from %s where pos_time>='%s' and pos_time <'%s' order by pos_time desc" %(IcErrorLog._meta.db_table,st,et)
    r_base = hander.grid.NewItem()
    rows = p_query(sql_add)
    item_count=len(rows)
    hander.Paging(arg['offset'],item_count=len(rows))
    b= time.time()
    sum_pos_money = 0
    back_money = 0
    sum_back_money = 0
    sum_test_card_money = 0
    sum_test_card_back_money = 0
    try:
        all_dining = dict_dining_obj()
        all_meal = dict_meal_obj()
        #开始进行统计
        hander.grid.InitItems()
        for i in range(len(rows)):
            row = rows[i]
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
            if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
            sum_pos_money += pos_money
        rr = r_base.copy()
        rr['user_pin'] = _(u"合计：")
        rr['money'] = _(u"实消费总额：") + '￥'+ str(sum_pos_money - sum_back_money)
        hander.grid.AddItem(rr)
    except:
        import traceback;traceback.print_exc()
    


#ic消费明细报表
def get_ic_list_record(hander,request,deptids,userids,dining,st,et,pos_model,operate,**arg):
    from mysite.personnel.models import Employee,Department
    from mysite.pos.models import ICConsumerList    
    from mysite.personnel.models.model_meal import Meal
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.utils import get_MultiSelect_objs
    from mysite.sql_utils import p_query,p_execute,p_query_one
    import time
    ids=[]
    deptIDS = []
    datas=[]#储存统计记录   储存的是每行记录
    tag="" #部门是否有人员
    ids = userids
    a = time.time()
    ot=['PIN','DeptID']
    if len(ids)==0:
       tag="NoEmp"
    else:
       userids=','.join([str(i) for i in ids])
    if db_select == POSTGRESSQL:
        id_list = userids.split(',')
        user_list = ','.join(("'%s'"%str(i) for i in id_list))
        if request.REQUEST.has_key("export"):
            top_count = "top(65000)" 
            sql_add = get_ic_list_record_sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,user_list,top_count)
        else:
            sql_add = get_ic_list_record_sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,user_list)
        settle_accounts_sql = get_ic_list_summary__sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,user_list)
    else:
        if request.REQUEST.has_key("export"):
            top_count = "top(65000)"  #最多导出65000条记录
            sql_add = get_ic_list_record_sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,userids,top_count)
        else:
            sql_add = get_ic_list_record_sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,userids)
        settle_accounts_sql = get_ic_list_summary__sql(ICConsumerList._meta.db_table,st,et,tag,operate,pos_model,dining,ids,userids)
    r_base = hander.grid.NewItem()
    
    settle_accounts_data = p_query_one(settle_accounts_sql)#消费明细汇总列查询

    item_count = int(settle_accounts_data[0] or 0) 
    hander.Paging(arg['offset'],item_count=item_count)
    sql_data = report_paging_sql('pos_time',sql_add,hander.grid._begin,hander.grid._end)
#    sql_data = 'select * from (select * ,row_number() over (order by pos_time desc) as r from (%s)  a ) t where t.r>%s and t.r<=%s'%(sql_add,hander.grid._begin,hander.grid._end)
    rows = p_query(sql_data) #分页获取数据
    
    
    b= time.time()
#    print "sql_tim==================",b-a
        
        
    sum_pos_money = settle_accounts_data[1] or 0
    back_money = 0
    sum_back_money = settle_accounts_data[2] or 0
    sum_test_card_money = settle_accounts_data[3] or 0
    sum_test_card_back_money = settle_accounts_data[4] or 0
    c= time.time()
    try:
        all_department = dict_dept_obj()
        all_dining = dict_dining_obj()
        all_meal = dict_meal_obj()
        #开始进行统计
        hander.grid.InitItems()
        for i in range(len(rows)):
            row = rows[i]
            r = r_base.copy()
            pos_money = row[5]
            r['user_pin'] = row[0]
            r['user_name'] = row[1]
            r['dept_name'] = all_department[row[2]]
            r['card'] = row[3]
            r['sys_card_no'] = row[4]
            r['money'] = '￥'+ str(pos_money)
            r['balance'] = '￥'+ str(row[6])
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
#            if i>=hander.grid._begin and i<hander.grid._end:
            hander.grid.AddItem(r)
        rr = r_base.copy()
        rr['user_pin'] = _(u"合计：")
        if pos_model == '9':#纠错
            rr['money'] = _(u"纠错总额：") + '￥'+ str(sum_back_money)
            rr['pos_model'] = _(u"消费日期异常：") + '￥'+ str(sum_test_card_back_money)
        else:
            rr['money'] = _(u"实消费总额：") + '￥'+ str(sum_pos_money - sum_back_money)
            rr['pos_model'] = _(u"消费日期异常：") + '￥'+ str(sum_test_card_money - sum_test_card_back_money)
        d= time.time()
#        print "date_______time=============",d-c
        
        hander.grid.AddItem(rr)
    except:
        import traceback;traceback.print_exc()
   
    
#ID消费明细报表
def get_id_list_record(hander,request,deptids,userids,dining,st,et,pos_model,operate,**arg):
    from mysite.personnel.models import Employee,Department
    from mysite.utils import get_MultiSelect_objs
    import time
    ids=[]
    deptIDS = []
    datas=[]#储存统计记录   储存的是每行记录
    tag="" #部门是否有人员
    a= time.time()
    ids = userids
    ot=['PIN','DeptID']
    if len(userids)==0:
       tag="NoEmp"
    else:
       userids=','.join([str(i) for i in userids])
    sql_add = get_id_list_record_sql(st,et,tag,operate,pos_model,dining,ids,userids)#报表内容sql
    settle_accounts_sql = get_id_summary_list_record_sql(st,et,tag,operate,pos_model,dining,ids,userids)#报表结算sql
    
    settle_accounts_data = p_query_one(settle_accounts_sql)#消费明细汇总列查询
    
    item_count = settle_accounts_data[0] or 0
    
    hander.Paging(arg['offset'],item_count=item_count)
    
    pageing_sql_data = report_paging_sql('checktime',sql_add,hander.grid._begin,hander.grid._end)#内容分页sql
    
    
    rows = p_query(pageing_sql_data)
    b= time.time()
#    print "sql_tim==================",b-a
    
    sum_pos_money = settle_accounts_data[1] or 0
    back_money = 0
    sum_back_money = settle_accounts_data[2] or 0
    sum_total_money = settle_accounts_data[3] or 0
    sum_total_back_money = settle_accounts_data[4] or 0
    
    try:
        all_department = dict_dept_obj()
        all_cash_type = dict_cash_type_obj()
        all_dining = dict_dining_obj()
        if userids:
            all_emp = dict_all_emp_obj()
        #开始进行统计
        c= time.time()
        r_base = hander.grid.NewItem()
        hander.grid.InitItems()
        for i in range(len(rows)):
            row = rows[i]
            r = r_base.copy()   
            pos_money = row[2]
            r['user_pin'] = all_emp[row[0]].split("_")[0]
            r['user_name'] = all_emp[row[0]].split("_")[1]
            r['dept_name'] = all_department[int(all_emp[row[0]].split("_")[2])]
            r['card'] = row[1]
            r['money'] = '￥'+ str(pos_money)
            r['balance'] = '￥'+ str(row[3])
            r['discount'] = row[7]
            r['type_name'] = all_cash_type[row[8]]
            
#            if row[8] == 9:#纠错
#                back_money = pos_money
#                sum_back_money += pos_money
#                pos_money = 0
#            if row[8] == 10:#计次消费
#                total_money = pos_money
#                sum_total_money += total_money
#                pos_money = 0
#            if row[8] == 12:#计次纠错
#                total_back_money = pos_money
#                sum_total_back_money += total_back_money
#                pos_money = 0
            r['dining'] = all_dining[row[9]]
            r['dev_sn'] = row[4]
            r['dev_serial_num'] = row[6]
            r['card_serial_num'] = row[5]
            r['create_operator'] = row[11]
            r['pos_time'] = row[10].strftime("%Y-%m-%d %H:%M:%S")
#            if i>=hander.grid._begin and i<hander.grid._end:
            hander.grid.AddItem(r)

        d= time.time()
#        print "date_______time=============",d-c
       
        rr = r_base.copy()
        rr['user_pin'] = _(u"合计：")
        rr['card'] = _(u"纠错：")+'￥'+ str(sum_back_money)
        rr['money'] = _(u"消费：")+'￥'+ str(sum_pos_money - sum_back_money)
        rr['pos_time'] = _(u"计次成本：")+'￥'+ str(sum_total_money)
        rr['dev_sn'] = _(u"计次纠错：")+'￥'+ str(sum_total_back_money)
        hander.grid.AddItem(rr)
    except:
        import traceback;traceback.print_exc()


        
RECHARGE_TYPE={
            1:_(u'充值'),
            13:_(u'充值优惠'),
                  }

#充值明细报表
def get_recharge_report(hander,request,Result,r_base,type_id,d1,d2,sql_add,userids,**arg):
     from mysite.personnel.models.model_emp import Employee
     from mysite.personnel.models.model_dept import Department
     if get_option("POS_IC"):
        sql=get_ic_recharge_report_sql(d1,d2)
     else:
        sql=get_id_recharge_report_sql(type_id,d1,d2)
     sql+=sql_add
     datas=[]#储存统计记录   储存的是每行记录
     rows = p_query(sql)
     hander.Paging(arg['offset'],item_count=len(rows))
     item_count=len(rows)
     sum_recharge_money = 0
     sum_yh_money = 0
     sum_test_card_money = 0
     sum_test_yh_money = 0
     try:
        all_department = dict_dept_obj()
        #开始进行统计
        if userids:
            all_emp = dict_all_emp_obj()
        hander.grid.InitItems()
        for i in range(len(rows)):
            row = rows[i]
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
            sum_recharge_money += recharge_money
            if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
        rr = r_base.copy()
        if get_option("POS_IC"):
            rr['user_pin'] = _(u"合计：")
            rr['money'] = _(u"充值合计（不包含优惠）：")+'￥'+ str(sum_recharge_money - sum_yh_money)
            rr['recharge_type'] = _(u"优惠合计：")+'￥'+ str(sum_yh_money)
#                 rr['card_blance'] = _(u"测试卡充值：")+'￥'+ str(sum_test_card_money - sum_test_yh_money)
#                 rr['check_time'] = _(u"测试卡优惠：")+'￥'+ str(sum_test_yh_money)
        else:
            rr['user_pin'] = _(u"合计：")
            rr['money'] = '￥'+ str(sum_recharge_money)
        hander.grid.AddItem(rr)
     except:
         import traceback;traceback.print_exc()
        
#退款明细报表
def get_reimburese_report(hander,request,Result,r_base,type_id,d1,d2,sql_add,userids,**arg):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    if get_option("POS_IC"):
        sql = get_ic_reimburese_report_sql(type_id,d1,d2)
    else:
        sql = get_id_reimburese_report_sql(type_id,d1,d2)
    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
#        rows = customSql(sql,False).fetchall()
    rows = p_query(sql)
    hander.Paging(arg['offset'],item_count=len(rows))
    hander.grid.InitItems()
    sum_recharge_money = 0
    back_money = 0
    try:
         all_department = dict_dept_obj()
         if userids:
            all_emp = dict_all_emp_obj()
         #开始进行统计
         for i in range(len(rows)):
             row = rows[i]
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
             if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
             sum_recharge_money += recharge_money
         rr = r_base.copy()
         rr['user_pin'] = _(u"合计：")
         rr['money'] = '￥'+ str(sum_recharge_money)
         hander.grid.AddItem(rr)
    except:
         import traceback;traceback.print_exc()
    
        


AllOW_TYPE={
            0:_(u'累加补贴'),
            1:_(u'清零补贴'),
                  }

#卡补贴明细报表
def get_allow_report(hander,request,Result,r_base,type_id,d1,d2,sql_add,userids,**arg):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    if get_option("POS_IC"):
        sql = get_ic_allow_report_sql(type_id,d1,d2)
    else:
        sql = get_id_allow_report_sql(type_id,d1,d2)
    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
#        rows = customSql(sql,False).fetchall()
    rows = p_query(sql)
    hander.Paging(arg['offset'],item_count=len(rows))
    hander.grid.InitItems()
#    print "sql========================",sql
    sum_allow_money = 0
    sum_clear_money = 0
    try:
         all_department = dict_dept_obj()
         #开始进行统计
         if userids:
            all_emp = dict_all_emp_obj()
         for i in range(len(rows)):
             row = rows[i]
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
             if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
             sum_allow_money += allow_money
         rr = r_base.copy()
         if get_option("POS_IC"):
             rr['user_pin'] = _(u"合计：")
             rr['money'] = _(u"补贴合计：") + '￥'+ str(sum_allow_money - sum_clear_money)
             rr['card_blance'] = _(u"清零合计：") + '￥'+ str(sum_clear_money)
         else:
             rr['user_pin'] = _(u"合计：")
             rr['money'] = _(u"补贴合计：") + '￥'+ str(sum_allow_money)
         hander.grid.AddItem(rr)
    except:
         import traceback;traceback.print_exc()
    
        


#退卡明细报表
def get_return_card_report(hander,request,Result,r_base,type_id,d1,d2,sql_add,userids,**arg):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    if get_option("POS_IC"):
        sql = get_ic_return_card_report(type_id,d1,d2)
    else:
        sql = get_id_return_card_report(type_id,d1,d2)
    sql+=sql_add
    datas=[]#储存统计记录   储存的是每行记录
#         rows = customSql(sql,False).fetchall()
    rows = p_query(sql)
    item_count = len(rows)
    hander.Paging(arg['offset'],item_count=len(rows))
    hander.grid.InitItems()
    sum_return_money = 0
    try:
        all_department = dict_dept_obj()
        if userids:
            all_emp = dict_all_emp_obj()
        #开始进行统计
        for i in range(len(rows)):
            row = rows[i]
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
            if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
        rr = r_base.copy()
        rr['user_pin'] = _(u"合计：")
        rr['user_name'] = item_count
        rr['money'] = '￥'+ str(sum_return_money)
        hander.grid.AddItem(rr)
    except:
        import traceback;traceback.print_exc()
    
        
        
        
#卡成本报表
def get_cost_report(hander,request,Result,r_base,type_id,d1,d2,sql_add,userids,**arg):
     from mysite.personnel.models.model_emp import Employee
     from mysite.personnel.models.model_dept import Department
     if get_option("POS_IC"):
        sql = get_ic_cost_report_sql(type_id,d1,d2)
     else:
        sql = get_id_cost_report_sql(type_id,d1,d2)
     sql+=sql_add
     datas=[]#储存统计记录   储存的是每行记录
#     print "sql=================",sql
     rows = p_query(sql)
     hander.Paging(arg['offset'],item_count=len(rows))
     hander.grid.InitItems()
     sum_cost_money = 0
     try:
         all_department = dict_dept_obj()
         if userids:
            all_emp = dict_all_emp_obj()
         #开始进行统计
         for i in range(len(rows)):
             row = rows[i]
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
             if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
         rr = r_base.copy()
         rr['user_pin'] = _(u"合计：")
         rr['money'] = '￥'+ str(sum_cost_money)
         hander.grid.AddItem(rr)
     except:
         import traceback;traceback.print_exc()
     
        


#发卡表
def get_issuecard_report(hander,request,Result,type_id,d1,d2,sql_add,userids,r_base,**arg):
     from mysite.personnel.models.model_emp import Employee
     from mysite.personnel.models.model_dept import Department
     from mysite.personnel.models.model_iccard import ICcard
     if get_option("POS_IC"):
        sql = get_ic_issuecard_report_sql(type_id,d1,d2)
     else:
        sql = get_id_issuecard_report_sql(type_id,d1,d2)
     sql+=sql_add
     datas=[]#储存统计记录   储存的是每行记录
#     print "sql=============",sql
     rows = p_query(sql)
     item_count = len(rows)
     hander.Paging(arg['offset'],item_count=len(rows))
     hander.grid.InitItems()
     try:
         all_department = dict_dept_obj()
         #开始进行合计
         all_emp = dict_all_emp_obj()
         for i in range(len(rows)):
             row = rows[i]
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
             if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
         rr = r_base.copy()
         rr['user_pin'] = _(u"合计：")
         rr['user_name'] = str(item_count)
         hander.grid.AddItem(rr)
     except:
         import traceback;traceback.print_exc()
        
#卡余额表
def get_card_blance_report(hander,request,Result,r_base,type_id,d1,d2,sql_add,userids,ids,operate,tag,card_type = None,**arg):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_dept import Department
    from mysite.personnel.models.model_iccard import ICcard
    if get_option("POS_IC"):
        sql = get_ic_card_blance_report(userids,ids,operate,tag,d1,d2,card_type)
    else:
        sql = get_id_card_blance_report(userids,ids,operate,tag)
#    sql+=sql_add
#    print "sql=============================",sql
    datas=[]#储存统计记录   储存的是每行记录
#    rows = p_query(sql)
#    hander.Paging(arg['offset'],item_count=len(rows))
#    sql_data = 'select  a.*,row_number() as r from (%s) as a where r>=%s and r<=%s '%(sql,hander.grid._begin,hander.grid._end)#
    sum_blance_money = 0
    rows = p_query(sql)
    hander.Paging(arg['offset'],item_count=len(rows))
    try:
        all_department = dict_dept_obj()
        all_card_type = dict_card_type_obj()
        all_emp = dict_all_emp_obj()
        hander.grid.InitItems()
        #开始进行统计
        for i in range(len(rows)):
            row = rows[i]
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
            if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
        rr = r_base.copy()
        rr['user_pin'] = _(u"合计：")
        rr['money'] = '￥'+ str(sum_blance_money)
        hander.grid.AddItem(rr)
    except:
        import traceback;traceback.print_exc()



#ID消费餐厅或者部门消费汇总
def id_dining_or_dept_report(hander,request,Result,r_base,d1,d2,dbname,pos_model,**arg):
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
    
    hander.Paging(arg['offset'],item_count=len(ids))
    hander.grid.InitItems()
    for i in range(len(ids)):
        id = ids[i]
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
#        print "sql======================",sql_db
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
            if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
    
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
    hander.grid.AddItem(rr)

#IC消费餐厅或者部门消费汇总
def ic_dining_or_dept_report(hander,request,Result,r_base,d1,d2,dbname,pos_model,**arg):
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
    
    sum_error_pos_money = 0
    sum_error_pos_count = 0
    sum_error_back_pos_money = 0
    sum_error_back_pos_count = 0
    sum_error_total_count  = 0
    sum_device_count = 0
    sum_pos_count = 0
#    model = ','.join(pos_model+'9')
    datas=[]
    if dbname == 'Dininghall':
        ids=Dininghall.objects.all().order_by('id').values_list('id','name')
    elif dbname == 'Device':
        ids = Device.objects.all().filter(device_type = DEVICE_POS_SERVER).order_by('id').values_list('id','alias','sn')
    elif dbname == 'Department':
        ids=Department.all_objects.all().order_by('id').values_list('id','name')
    
    hander.Paging(arg['offset'],item_count=len(ids))
    hander.grid.InitItems()
    for i in range(len(ids)):
        id = ids[i]
        r=r_base.copy()
        if dbname == 'Dininghall':
            sql_db = ic_dining_or_dept_or_device_report_sql(dbname,id[0],d1,d2)
            error_sql = ic_device_or_dining_error_log_sql(dbname,id[0],d1,d2)
            error_list = p_query(error_sql)
        elif dbname == 'Device':
            sql_db = ic_dining_or_dept_or_device_report_sql(dbname,id[2],d1,d2)
            error_sql = ic_device_or_dining_error_log_sql(dbname,id[2],d1,d2)
            error_list = p_query(error_sql)
        elif dbname == 'Department':
            sql_db = ic_dining_or_dept_or_device_report_sql(dbname,id[0],d1,d2)
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
            
            if dbname in ['Dininghall','Device']:
                error_back_count = error_list[0][0] or 0
                error_pos_count = error_list[0][1] or 0
                error_back_money = error_list[0][2] or 0
                error_pos_money = error_list[0][3] or 0
                error_total_count = error_list[0][4] or 0
                
                summary_error_count = error_pos_count - error_back_count -  error_total_count#异常实际消费次数结算
                summary_error_money = error_pos_money - error_back_money #异常实际消费金额结算
                
                sum_error_pos_count += summary_error_count
                sum_error_pos_money += summary_error_money
                sum_error_total_count +=error_total_count
                
                r['error_summary_count']=str(summary_error_count)
                r['error_summary_money']='￥'+str(summary_error_money)
                
                r['meal_money']='￥'+ str(all_money + error_pos_money - single_money) # 消费总金额不包含补单
                r['back_money']='￥'+ str(back_money + error_back_money)#纠错总金额
                r['back_count']=str(back_count + error_back_count)#纠错总次数
                summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
                r['summary_dev_money']='￥'+ str(summary_dev_money)#实消费金额结算（不含异常）
                r['add_single_money']='￥'+ str(single_money)
                summary_pos_count = pos_count + total_count + error_pos_count#消费总次数
                r['pos_count']=str(summary_pos_count)#消费总次数
                r['sum_device_count']=str(pos_count + total_count + error_pos_count + back_count + error_back_count )#设备记录总次数
                r['summary_total_time']=str(total_count + error_total_count)  #计次结算
                
                
                sum_error_back_pos_count +=error_back_count
                sum_error_back_pos_money +=error_back_money
                summary_count = pos_count - back_count   ##实际消费次数结算（不包含异常记录）
                summary_money = all_money - back_money ##实际消费金额结算（不包含异常记录）
                summary_device_count = pos_count + total_count + error_pos_count + back_count + error_back_count#设备记录总次数
                sum_device_count +=summary_device_count #设备记录总次数 汇总
                sum_pos_count += summary_pos_count #消费总次数汇总
                r['summary_money']='￥'+ str(summary_money)#系统金额结算（含补单）
                r['summary_count']=str(summary_count) #实消费次数结算 扣款消费次数结算（不含异常）
                
            else:
                r['meal_money']='￥'+ str(all_money)
                r['back_money']='￥'+ str(back_money)
                r['back_count']=str(back_count)
                r['pos_count']=str(pos_count + total_count)
                summary_count = pos_count - back_count   #实消费次数结算
                summary_money = all_money - back_money #系统消费结算金额
                summary_dev_money = all_money - back_money  - single_money#不包含补单金额结算
                r['summary_total_time']=str(total_count)  #计次结算
                r['summary_money']='￥'+ str(summary_money)#系统金额结算（含补单）
                r['summary_count']=str(summary_count) #实消费次数结算 扣款消费次数结算（不含异常）
                
                sum_pos_count +=pos_count
            summary_total_time +=total_count
            r['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
            if dbname == 'Dininghall':
                r['dining_name']=id[1]
            elif dbname == 'Device':
                r['device_name']=id[1]
                r['device_sn']=id[2]
            else:
                r['dept_name']=id[1]

            sum_meal_money +=all_money
            sum_back_money +=back_money
            sum_back_count +=back_count
            sum_summary_count +=summary_count
            sum_summary_money +=summary_money
            sum_single_money +=single_money
            sum_dev_money +=summary_dev_money
            
            if i>=hander.grid._begin and i<hander.grid._end:
                hander.grid.AddItem(r)
    
    rr = r_base.copy()
    if dbname == 'Dininghall':
        rr['dining_name']=_(u"汇总：")
    elif dbname == 'Device':
        rr['device_name']=_(u"汇总：")
    else:
        rr['dept_name']=_(u"汇总：")
#    rr['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
#    rr['breakfast_money']=str(sum_breakfast_money)
#    rr['lunch_money']=str(sum_lunch_money)
#    rr['dinner_money']=str(sum_dinner_money)
#    rr['supper_money']=str(sum_supper_money)
#    rr['summary_money']='￥'+ str(sum_summary_money)#系统金额结算（含补单）
#    rr['summary_count']=str(sum_summary_count)#扣款消费次数结算（不含异常）
        

    if dbname in ['Dininghall','Device']: 
        rr['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
        rr['summary_money']='￥'+ str(sum_summary_money)#系统金额结算（含补单）
        rr['summary_count']=str(sum_summary_count)#扣款消费次数结算（不含异常）
        
        rr['add_single_money']='￥'+ str(sum_single_money)#补单合计（汇总）
        rr['summary_dev_money']='￥'+ str(sum_dev_money) #实消费金额结算（不含异常）
        
        rr['error_summary_count'] = str(sum_error_pos_count)#异常消费次数汇总
        rr['error_summary_money'] = '￥'+str(sum_error_pos_money)#异常消费金额汇总
        rr['pos_count']=str(sum_pos_count)#消费总次数合计
        rr['sum_device_count']=str(sum_device_count)#设备记录总次数合计
        rr['meal_money']='￥'+ str(sum_meal_money + sum_error_pos_money  - sum_single_money + sum_error_back_pos_money)
        rr['back_money']='￥'+ str(sum_back_money + sum_error_back_pos_money)
        rr['back_count']=str(sum_back_count + sum_error_back_pos_count)
        rr['summary_total_time']=str(summary_total_time + sum_error_total_count )
    else:
        rr['pos_date']=d1.strftime("%Y-%m-%d")+"---"+(d2-timedelta(days=1)).strftime("%Y-%m-%d")
        rr['summary_money']='￥'+ str(sum_summary_money)#系统金额结算（含补单）
        rr['summary_count']=str(sum_summary_count)#扣款消费次数结算（不含异常）
        rr['pos_count']=str(sum_pos_count + summary_total_time)
        rr['meal_money']='￥'+ str(sum_meal_money)
        rr['back_money']='￥'+ str(sum_back_money)
        rr['back_count']=str(sum_back_count)
        rr['summary_total_time']=str(summary_total_time)
    hander.grid.AddItem(rr)

#个人消费汇总
def emp_summary_report(hander,request,Result,r_base,d1,d2,userids,pos_model,**arg):
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
    userids=','.join([str(i) for i in userids])
    if get_option("POS_IC"):
        if db_select == POSTGRESSQL:
            id_list = userids.split(',')
            user_list = ','.join(("'%s'"%str(i) for i in id_list))
            db_sql = ic_emp_summary_report_sql(user_list,d1,d2)
        else:
            db_sql = ic_emp_summary_report_sql(userids,d1,d2)
    else:
        db_sql = id_emp_summary_report_sql(userids,d1,d2)
        
#    print "sql==================",db_sql
    if userids:
         rows = p_query(db_sql)
    else:
        rows = []
    hander.Paging(arg['offset'],item_count=len(rows))
    all_department = dict_dept_obj()
    item_count = len(rows)
    if userids:
        all_emp = dict_all_emp_obj()
    hander.grid.InitItems()
    if rows:
        for i in range(len(rows)):
            row = rows[i]
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
            hander.grid.AddItem(r)
            
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
    hander.grid.AddItem(rr)
    


#收支汇总报表
def SZ_summary_report(hander,request,Result,r_base,d1,d2,check_opreate,**arg):
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
    row_data = p_query(sql_db)
    hander.Paging(arg['offset'],item_count=len(row_data))
    hander.grid.InitItems()
    for i in range(len(row_data)):
        r=r_base.copy()
        row = row_data[i]
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
                    if i>=hander.grid._begin and i<hander.grid._end:
                        hander.grid.AddItem(r)
                    
            else:
                r['operate']=_(u'全部')
                if i>=hander.grid._begin and i<hander.grid._end:
                    hander.grid.AddItem(r)
            
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
    hander.grid.AddItem(rr)


    
#消费汇总报表入口
def posStatisticalReports(hander,request,deptids,userids,d1,d2,dining,meal,typeid,operate,pos_model,check_opreate,**arg):
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
    ids = userids
    if len(ids)==0:
        tag="NoEmp"

    Result={}#返回结果 字典
#    item_count=len(ids)
    try:
        if typeid=="110":#餐厅汇总
            r_base = hander.grid.NewItem()
            if get_option("POS_ID"):
                id_dining_or_dept_report(hander,request,Result,r_base,d1,d2,'Dininghall',pos_model,**arg)
            else:
                ic_dining_or_dept_report(hander,request,Result,r_base,d1,d2,'Dininghall',pos_model,**arg)
        elif typeid=="120":#部门汇总
            r_base = hander.grid.NewItem()
            if get_option("POS_ID"):
                id_dining_or_dept_report(hander,request,Result,r_base,d1,d2,'Department',pos_model,**arg)
            else:
                ic_dining_or_dept_report(hander,request,Result,r_base,d1,d2,'Department',pos_model,**arg)
        elif typeid=="130":# 个人汇总
            r_base = hander.grid.NewItem()
            emp_summary_report(hander,request,Result,r_base,d1,d2,userids,pos_model,**arg)
            
        elif typeid=="140":#设备汇总
            r_base = hander.grid.NewItem()
            if get_option("POS_ID"):
                id_dining_or_dept_report(hander,request,Result,r_base,d1,d2,'Device',pos_model,**arg)
            else:
                ic_dining_or_dept_report(hander,request,Result,r_base,d1,d2,'Device',pos_model,**arg)
                
        elif typeid=="150":#收支汇总
            r_base = hander.grid.NewItem()
            SZ_summary_report(hander,request,Result,r_base,d1,d2,check_opreate,**arg)
    except:
          import traceback;traceback.print_exc()
    
    
  
#消费报表点
def pos_list_Reports(hander,request,deptids,userids,d1,d2,dining,meal,typeid,operate,pos_model,**arg):
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
    ids = userids
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
        if typeid=="1":#充值表
            sql_add += "order by checktime desc"
            r_base = hander.grid.NewItem()
            get_recharge_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,**arg)

        elif typeid=="13":#发卡表
            sql_add += "order by checktime desc"
            r_base = hander.grid.NewItem()
            get_issuecard_report(hander,request,Result,7,d1,d2,sql_add,userids,r_base,**arg)

        elif typeid=="12":# 卡余额表
            card_type = request.GET.get('card_type',"")
            r_base = hander.grid.NewItem()
            if card_type :#无卡退卡表
                get_card_blance_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,ids,operate,tag,card_type,**arg)
            else:
                get_card_blance_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,ids,operate,tag,**arg)

        elif typeid=="7":#卡成本
            r_base = hander.grid.NewItem()
            sql_add += "order by checktime desc"
            get_cost_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,**arg)

        elif typeid=="4":#退卡
            r_base = hander.grid.NewItem()
            sql_add += "order by checktime desc"
            get_return_card_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,**arg)

        elif typeid=="5":#退款
            r_base = hander.grid.NewItem()
            sql_add += "order by checktime desc"
            get_reimburese_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,**arg)
        
        elif typeid=="2":#补贴表
            r_base = hander.grid.NewItem()
            sql_add += "order by checktime desc"
            get_allow_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,**arg)
        
        elif typeid=="14":#无卡退卡余额表
            r_base = hander.grid.NewItem()
            get_card_blance_report(hander,request,Result,r_base,typeid,d1,d2,sql_add,userids,ids,operate,tag,card_type="no_card",**arg)
    except:
          import traceback;traceback.print_exc()
