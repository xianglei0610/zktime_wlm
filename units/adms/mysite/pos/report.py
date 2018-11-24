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
from getfields import get_base_fields,get_pos_fields_pos,get_pos_fields_add,get_pos_fields_subsidies
from dbapp.datalist import save_datalist
from  datetime   import datetime,date,time,timedelta
from mysite.personnel.models import Employee,Department
#from mysite.pos.models import CarCashSZ

from mysite.personnel.models.model_meal import Meal

#sql语句生产报表的时候，需要引入的：
from django.conf import settings
from mysite.att.models.modelproc import customSql,customSqlEx
from django.db import  connection
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



def get_dining_room(request):
    '''
    得到所有的餐厅 并在前台显示
    '''
    select_dininghall= request.REQUEST.get("dininghall", "")
    from mysite.pos.models import Dininghall,Meal
    print 'select_dininghall',select_dininghall
    #select_meeting="abcdef"
    if select_dininghall:
       pass
    else:
        halls= Dininghall.objects.all().order_by('id').values_list('id','code','name')
        meals=Meal.objects.all().order_by('id').values_list('id','code','name')
        return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all', 'meals':[meal for meal in meals],'halls': [hall for hall in halls]})))
 
 

def pos_dingding_summary(request,deptids,userids,d1,d2,totalall=False):
    '''
    餐厅统计
    '''
    from mysite.iclock.models.model_dininghall import Dininghall
    from  get_ic_reports_fields import get_dining_report
    ids=Dininghall.objects.all().order_by('id').values_list('id')
    Result={}#返回结果
    item_count=len(ids)
    try:
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
        print ids
        uids=ids
        if not totalall:#如果 不得到全部数据，就进行下面分片操作
            uids=uids[((offset-1)*limit):(offset*limit)]#分页过滤条件（就是 使用列表中的分片原理）
            
        datas=[]#储存统计记录
        r,FieldNames,FieldCaption=get_dining_report()
        Result['fieldnames']=FieldNames
        Result['fieldcaptions']=FieldCaption
        Result['datas']=r
        if db_select==SQLSERVER or db_select == MYSQL:
            sql = '''
                select
                sum(case when  meal_id='1' then money else 0 end) as breakfast_money, 
                sum(case when  meal_id='2' then money else 0 end) as lunch_money, 
                sum(case when  meal_id='3' then money else 0 end) as dinner_money, 
                sum(case when  meal_id='4' then money else 0 end) as supper_money,
                sum(money) as aa,dining  from pos_icconsumerlist where dining='%s'
            '''
        for id in uids:
            sql_add = sql%id
            rows = customSql(sql_add,False).fetchall()
            if rows:
                r['pos_date']=d1.strftime("%Y-%m-%d")+"---"+d2.strftime("%Y-%m-%d")
                r['dining_name']=row[fldNames['dining']]
                r['breakfast_money']=row[fldNames['breakfast_money']]
                r['lunch_money']=row[fldNames['lunch_money']]
                r['dinner_money']=row[fldNames['dinner_money']]
                r['supper_money']=row[fldNames['supper_money']]
                r['summary_money']=row[fldNames['summary_money']]
            datas.append(r)    
        Result['datas']=datas
        return Result
        
    except:
        import traceback;traceback.print_exc()
    

    
def get_pos_record(request,deptids,userids,d1,d2,totalall=False):
    '''
    统计 消费 原始记录信息
    '''
    from mysite.pos.models import CarCashSZ
    import decimal
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
#        deptids=deptIDS[0]
        ot=['PIN','DeptID']
        ids=Employee.objects.filter(DeptID__in=deptIDS,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)

    Result={}#返回结果
    item_count=len(ids)
    try:
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
        print ids
        uids=ids
        if not totalall:#如果 不得到全部数据，就进行下面分片操作
            uids=uids[((offset-1)*limit):(offset*limit)]#分页过滤条件（就是 使用列表中的分片原理）        
        datas=[]#储存统计记录    
        rrr,FieldNames,FieldCaption=get_pos_fields_pos()       
        Result['fieldnames']=FieldNames
        Result['fieldcaptions']=FieldCaption
        Result['datas']=rrr
        total_money_all=0
       
        for emp in uids:
            total_money=0
            r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
            'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
            if db_select==1:
#                em=CarCashSZ.objects.filter(user__id=int(emp),checktime__gte=d1,checktime__lte=d2,type__id=6).order_by("checktime")
#             values_list("user__PIN","user__EName","user__card","user__Gender","user__DeptID__code","user__DeptID__name")
                sql='''
                    select u.badgenumber as pin,u.name as name,u.card as card,d.code as deptcode,d.DeptName as department,
                    pd.code as diningcode,pd.name as diningname,p.checktime as checktime,p.money as money from userinfo u,Departments d,
                    pos_carcashsz p,pos_dininghall as pd  where u.userid=p.user_id and d.deptID=u.defaultdeptid and  p.dining_id =pd.id and
                    '''
                sql += '''p.checktime>='%s' and p.checktime<='%s' and'''%(d1,d2)
                sql +=""" p.user_id = %s order by u.badgenumber,u.defaultdeptid"""%(emp)
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
                    print  t[fldNames['name']] 
            if rows:
                for row in rows:
                    r['badgenumber']=row[fldNames['pin']]
                    r['username']=row[fldNames['name']]
                    r['card']=row[fldNames['card']]
                    r['gender']=''
                    r['deptcode']=row[fldNames['deptcode']]
                    r['deptname']=row[fldNames['department']]
                    r['diningcode']=row[fldNames['diningcode']]
                    r['diningname']=row[fldNames['diningname']]
                    r['checktime']=row[fldNames['checktime']].strftime("%Y-%m-%d %H:%M:%S")
                    r['money']="-"+ str(row[fldNames['money']])
#                    total_money +=decimal.Decimal(row[fldNames['money']])
                    total_money +=row[fldNames['money']]
                    
                    datas.append(r)
                   
                total_money_all+=total_money
                
                           
                           

        r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
            'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
                    
        
        r['badgenumber']=_("总计")
        r['username']=""
        r['card']=""
        r['gender']=""
        r['deptcode']=""
        r['deptname']=""
        r['diningcode']=""
        r['diningname']=""
        r['checktime']=""
        
        r["money"]="-"+str(total_money_all)
     
            
        datas.append(r)
        
        
        Result['datas']=datas
        return Result
        
    except:
        import traceback;traceback.print_exc()
    
    
    
def get_add_record(request,deptids,userids,d1,d2,totalall=False):
    '''
    充值原始明细表
    '''
    from mysite.pos.models import CarCashSZ
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
#        deptids=deptIDS[0]
        ot=['PIN','DeptID']
        ids=Employee.objects.filter(DeptID__in=deptIDS,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)

    Result={}#返回结果
    item_count=len(ids)
    try:
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
        print ids
        uids=ids
        if not totalall:#如果 不得到全部数据，就进行下面分片操作
            uids=uids[((offset-1)*limit):(offset*limit)]#分页过滤条件（就是 使用列表中的分片原理）
        
        
            
        datas=[]#储存统计记录

        
        r,FieldNames,FieldCaption=get_pos_fields_add()
        Result['fieldnames']=FieldNames
        Result['fieldcaptions']=FieldCaption
        Result['datas']=r
        total_money_all=0
        for emp in uids:
            total_money=0
#            r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
#            'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
           
            em=CarCashSZ.objects.filter(user__id=int(emp),checktime__gte=d1,checktime__lte=d2,type__id=1).order_by("checktime")
#             values_list("user__PIN","user__EName","user__card","user__Gender","user__DeptID__code","user__DeptID__name")
            if em:
                for e  in em:
                    r={'admin':'','badgenumber':'','username':'','card':'','gender':'','deptcode':'',
                    'deptname':'','checktime':'','money':''}
                    r['admin']=e.create_operator
                    r['badgenumber']=e.user.PIN
                    r['username']=e.user.EName
                    r['card']=e.user.Card
                    r['Gender']=e.user.Gender
                    r['deptcode']=e.user.DeptID.code
                    r['deptname']=e.user.DeptID.name
                    r['checktime']=e.checktime.strftime("%Y-%m-%d %H:%M:%S")
                    r['money']=str(e.money)
                    total_money +=float(e.money)
                   
                    datas.append(r)
            
            total_money_all+=total_money
            
        r={'admin':'','badgenumber':'','username':'','card':'','gender':'','deptcode':'',
            'deptname':'','checktime':'','money':''}
                    
        r['admin']=_(u"总计")
        r['badgenumber']=""
        
        r['username']=""
        r['card']=""
        r['Gender']=""
        r['deptcode']=""
        r['deptname']=""
        r['diningcode']=""
        r['diningname']=""
        r['checktime']=""
        
        r["money"]=str(total_money_all)
     
            
        datas.append(r)
       
        
        Result['datas']=datas
        return Result
        
    except:
        import traceback;traceback.print_exc()


def get_subsidies_record(request,deptids,userids,d1,d2,totalall=False):
    '''
    消费 补贴原始记录信息
    '''
    from mysite.pos.models import CarCashSZ
    if len(userids)>0 and userids!='null':   
        ids=userids.split(',')
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
    #        deptids=deptIDS[0]
        ot=['PIN','DeptID']
        ids=Employee.objects.filter(DeptID__in=deptIDS,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)

    Result={}#返回结果
    item_count=len(ids)
    try:
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
        print ids
        uids=ids
        if not totalall:#如果 不得到全部数据，就进行下面分片操作
            uids=uids[((offset-1)*limit):(offset*limit)]#分页过滤条件（就是 使用列表中的分片原理）
        datas=[]#储存统计记录
        r,FieldNames,FieldCaption=get_pos_fields_subsidies()
        Result['fieldnames']=FieldNames
        Result['fieldcaptions']=FieldCaption
        Result['datas']=r
        total_money_all=0
        for emp in uids:
            total_money=0
    #            r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
    #            'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
           
            em=CarCashSZ.objects.filter(user__id=int(emp),checktime__gte=d1,checktime__lte=d2,type__id=2).order_by("checktime")
    #             values_list("user__PIN","user__EName","user__card","user__Gender","user__DeptID__code","user__DeptID__name")
            if em:
                for e  in em:
                    r={'admin':'','badgenumber':'','username':'','card':'','gender':'','deptcode':'',
                    'deptname':'','checktime':'','money':''}
                    r['admin']=e.create_operator
                    r['badgenumber']=e.user.PIN
                    r['username']=e.user.EName
                    r['card']=e.user.Card
                    r['Gender']=e.user.Gender
                    r['deptcode']=e.user.DeptID.code
                    r['deptname']=e.user.DeptID.name
                    r['checktime']=e.checktime.strftime("%Y-%m-%d %H:%M:%S")
                    r['money']=str(e.money)
                    total_money +=e.money
                   
                    datas.append(r)
            
            total_money_all+=total_money
            
        r={'admin':'','badgenumber':'','username':'','card':'','gender':'','deptcode':'',
            'deptname':'','checktime':'','money':''}
                    
        r['admin']=_(u"总计")
        r['badgenumber']=""
        
        r['username']=""
        r['card']=""
        r['Gender']=""
        r['deptcode']=""
        r['deptname']=""
        r['diningcode']=""
        r['diningname']=""
        r['checktime']=""
        
        r["money"]=str(total_money_all)
     
            
        datas.append(r)
       
        
        Result['datas']=datas
        return Result
        
    except:
        import traceback;traceback.print_exc()



def get_diningcalculate_record(request,deptids,userids,d1,d2,dining,totalall=False):
    '''
    统计 餐厅消费 详细记录
    '''
    from mysite.pos.models import CarCashSZ
    if len(userids)>0 and userids!='null':
        ids=userids.split(',')
    elif len(deptids)>0:
        deptIDS=deptids.split(',')
    #        deptids=deptIDS[0]
        ot=['PIN','DeptID']
        ids=Employee.objects.filter(DeptID__in=deptIDS,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)

    Result={}#返回结果
    item_count=len(ids)
    try:
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
    
        uids=ids
        if not totalall:#如果 不得到全部数据，就进行下面分片操作
            uids=uids[((offset-1)*limit):(offset*limit)]#分页过滤条件（就是 使用列表中的分片原理）        
        datas=[]#储存统计记录    
        
        
        r,FieldNames,FieldCaption=get_pos_fields_pos()       
        Result['fieldnames']=FieldNames
        Result['fieldcaptions']=FieldCaption
        Result['datas']=r
        total_money_all=0
        for emp in uids:
            total_money=0
            #            r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
            #            'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
            if dining=='0':
                em=CarCashSZ.objects.filter(user__id=int(emp),checktime__gte=d1,checktime__lte=d2,type__id=6).order_by("checktime")
            else:
                em=CarCashSZ.objects.filter(dining__id=int(dining),user__id=int(emp),checktime__gte=d1,checktime__lte=d2,type__id=6).order_by("checktime")
            
        #             values_list("user__PIN","user__EName","user__card","user__Gender","user__DeptID__code","user__DeptID__name")
            if em:
                for e  in em:
                    r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
                    'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
                    r['badgenumber']=e.user.PIN
                    r['username']=e.user.EName
                    r['card']=e.user.Card
                    r['Gender']=e.user.Gender
                    r['deptcode']=e.user.DeptID.code
                    r['deptname']=e.user.DeptID.name
                    if e.dining:
                        r['diningcode']=e.dining.code
                        r['diningname']=e.dining.name
                    r['checktime']=e.checktime.strftime("%Y-%m-%d %H:%M:%S")
                    r['money']="-"+str(e.money)
                    total_money +=e.money
                    datas.append(r)
              
            total_money_all+=total_money
              
        r={'badgenumber':'','username':'','card':'','gender':'','deptcode':'',
          'deptname':'','diningcode':'','diningname':'','checktime':'','money':''}
                  
        r['badgenumber']=_("总计")
        r['username']=""
        r['card']=""
        r['Gender']=""
        r['deptcode']=""
        r['deptname']=""
        r['diningcode']=""
        r['diningname']=""
        r['checktime']=""
        r["money"]="-"+str(total_money_all)
        datas.append(r)
        Result['datas']=datas
        return Result

    except:
        import traceback;traceback.print_exc()

def funPosReport(request):
    '''
    消费各类统计报表
    '''
    pass