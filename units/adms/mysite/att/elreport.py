#! /usr/bin/env python
#coding=utf-8
from django.utils.translation import ugettext_lazy as _
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps 
from dbapp.modelutils import GetModel
from mysite.settings import MEDIA_ROOT
from django.db.models import Q
from dbapp.datalist import save_datalist
from mysite.personnel.models import Employee
from mysite.iclock.models import Transaction
from basefield import get_base_fields,get_card_times_fields,get_yc_fields
import datetime
from django.db.models import connection as conn
def le_reprot_calculate(request,deptids,userids,st,et,totalall=False):
    '''
    根据传递过来的参数 来返回 考勤汇总
    '''
       
    if len(userids)>0 and userids!='null':#获取人
        ids=userids.split(',')
    elif len(deptids)>0:
        deptids=deptids.split(',')
        deptids=deptids
        ot=['PIN','DeptID']
        ids=Employee.all_objects.filter(DeptID__in=deptids,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)

    total_days=int((et-st).days)+1#总天数
    
    Result={}#定义返回的字典，也就是 传递到前台
    re=[]#储存每条记录数
    try:
        #分页        
        try:
            offset = int(request.REQUEST.get('p', 1))#获取分页信息
        except:
            offset=1
            #print "offset:%s"%offset
        uids=[]#储存人员信息
        k=0
        limit= int(request.POST.get('l', settings.PAGE_LIMIT)) 
        if not totalall:
#            limit= int(request.POST.get('l', settings.PAGE_LIMIT))  #导出时使用
            item_count =len(ids)*total_days #获取记录总数
            
            if item_count % limit==0:
                page_count =item_count/limit
            else:
                page_count =int(item_count/limit)+1            
                
            if offset>page_count and page_count:offset=page_count
             
#            ids=ids[(offset-1)*limit:offset*limit]#分页操作
            
            Result['item_count']=item_count#记录总数
            Result['page']=offset          #第几页
            Result['limit']=limit           #每页显示数
            Result['from']=(offset-1)*limit+1 #
            Result['page_count']=page_count  #总页数
        for u in ids:
            uids.append(u)
       
        r,Fields,Capt=get_base_fields()
        
        #print "Result['fieldnames']=",Fields
        Result['fieldnames']=Fields
        Result['fieldcaptions']=Capt
        Result['datas']=r
        try:
            days = et.date() - st.date()#结束时间 - 开始时间
            for emp in uids:
                userid =int (emp)
                emp_pin = Employee.all_objects.get(pk=userid)#.values_list("PIN","EName","DeptID__code","DeptID__name")
                check = Transaction.objects.filter(UserID=userid,TTime__range=(st,et)).values_list("UserID__PIN","UserID__EName","UserID__DeptID__code","UserID__DeptID__name","TTime").order_by("TTime")
                pos=0
                for d  in range(days.days+1):
                    r={'username': '', 'deptid': '', 'firstchecktime': '', 'userid': -1, 'badgenumber': '', 'latechecktime': ' ','date':'','deptname':''}
                    cur=st.date()+datetime.timedelta(d)
                    some_day=[]
                    first=True
                    while pos<len(check) and check[pos][4].date()==cur:
                        if first:   
                            some_day.append(check[pos][4])#当天第一条
                            first=False
                        pos+=1
                    if not first and some_day[len(some_day)-1]!=check[pos-1][4]:
                        some_day.append(check[pos-1][4])#当天最晚一条
                    r["badgenumber"]=emp_pin.PIN
                    r["username"]=emp_pin.EName
                    r["deptid"]=emp_pin.DeptID.code
                    r["deptname"]=emp_pin.DeptID.name
                    if some_day:
                        if len(some_day)==1:
                            r["firstchecktime"]=str(some_day[0])
                            r["latechecktime"]=""
                        if len(check)>=2:
                            r["firstchecktime"]=str(some_day[0])
                            r["latechecktime"]=str(some_day[-1])
                    else:
                        r["firstchecktime"]=""
                        r["latechecktime"]=""
#                        r["date"] = u"%s"%ce.date()
                    r["date"] = u"%s"%cur
                    re.append(r)
        except:
            import traceback;traceback.print_exc()
        
        #分页数据
        
        if not totalall:
           re=re[((offset-1)*limit):(offset*limit)]
        
        Result['datas']=re
        return Result
    except:
        import traceback;traceback.print_exc()
    
@login_required
def le_reprot(request):
    '''
    汇总最早与最晚计算报表
    '''
    deptids=request.POST.get('DeptIDs','')
    userids=request.POST.get('UserIDs','')
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')+" 23:59:59"
    st=datetime.datetime.strptime(st,'%Y-%m-%d')
    et=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
    r=le_reprot_calculate(request,deptids,userids,st,et)
    loadall=request.REQUEST.get('pa','')
    if not loadall:
       objdata={}
       allr=le_reprot_calculate(request,deptids,userids,st,et,True)
    
       objdata['data']=allr['datas']
       objdata['fields']=allr['fieldnames']
       heads={}
       for i  in  range(len(allr['fieldnames'])):
           heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
       objdata['heads']=heads
       tmp_name=save_datalist(objdata)
       r['tmp_name']=tmp_name#用于导出  没有这个字段导出报错。
       
    return getJSResponse(smart_str(dumps(r)))
    
@login_required    
def yc_report(request):
    '''
    考勤异常明细表
    '''
    deptids=request.POST.get('DeptIDs','')
    userids=request.POST.get('UserIDs','')
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')
    st=datetime.datetime.strptime(st,'%Y-%m-%d')
    st=st-datetime.timedelta(seconds=1)
    et=datetime.datetime.strptime(et,'%Y-%m-%d')
    r=yc_calculate(request,deptids,userids,st,et)
    loadall=request.REQUEST.get('pa','')
    if not loadall:
       objdata={}
       allr=yc_calculate(request,deptids,userids,st,et,True)
       objdata['data']=allr['datas']
       objdata['fields']=allr['fieldnames']
       heads={}
       for i  in  range(len(allr['fieldnames'])):
           heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
       objdata['heads']=heads
       tmp_name=save_datalist(objdata)
       r['tmp_name']=tmp_name#用于导出  没有这个字段导出报错。
       
    return getJSResponse(smart_str(dumps(r)))


def yc_calculate(request,deptids,userids,st,et,totalall=False):
    '''
    计算出考勤异常明细表结果
    '''
       
    from mysite.att.sql import yc_calculate_sql1,yc_calculate_sql2
    total_days=int((et-st).days)+1#总天数
    
    Result={}#定义返回的字典，也就是 传递到前台
    re=[]#储存每条记录数
    try:
        #分页        
        try:
            offset = int(request.REQUEST.get('p', 1))#获取分页信息
        except:
            offset=1
            #print "offset:%s"%offset
        uids=[]#储存人员信息
        k=0
        limit= int(request.POST.get('l', settings.PAGE_LIMIT)) 
        if not totalall:
            sql=yc_calculate_sql1(deptids,st,et,userids)                       
            count_data=((0,),)
            try:
                cur=conn.cursor()
                cur.execute(sql)
                count_data=cur.fetchall()
                conn._commit()
            except:
#                print sql
                import traceback;traceback.print_exc()
            
            item_count =count_data[0][0] #获取记录总数
            
            if item_count % limit==0:
                page_count =item_count/limit
            else:
                page_count =int(item_count/limit)+1            
                
            if offset>page_count and page_count:offset=page_count
             
#            ids=ids[(offset-1)*limit:offset*limit]#分页操作
            
            Result['item_count']=item_count#记录总数
            Result['page']=offset          #第几页
            Result['limit']=limit           #每页显示数
            Result['from']=(offset-1)*limit+1 #
            Result['page_count']=page_count  #总页数
#        for u in ids:
#            uids.append(u)
       
        r,Fields,Capt=get_yc_fields()
        
        #print "Result['fieldnames']=",Fields
        Result['fieldnames']=Fields
        Result['fieldcaptions']=Capt
        Result['datas']=r
        date =st.date()
        sql=yc_calculate_sql2(totalall,Result['from'],deptids,st,et,userids,offset,limit)   
            
        ret_data=[]
        try:
            cur=conn.cursor()
#            print sql            
            cur.execute(sql)
            ret_data=cur.fetchall()
            conn._commit()
        except:
#            print sql
            import traceback;traceback.print_exc()
            
        for d in ret_data:
            r={'username': '', 'deptname': '', 'worktime': '', 'userid': -1, 'badgenumber': '', 'card_times': ' ','date':'','late':'','early':'','absent':'','late_times':'','early_times':'','absent_times':'','super_dept':''}
            r["userid"]=d[1]
            r["super_dept"]=d[2] or " "
            r["deptname"]=d[3] or " "
            r["badgenumber"]=d[4]
            r["username"]=d[5] or " "
            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
                r["date"]=d[6].strftime("%Y-%m-%d")
            else:
                r["date"]=d[6]
            r["late"]=d[7] or " "
            r["early"]=d[8] or " "
            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
                r["absent"]=str(d[9]) or " "
            else:
                r["absent"]=d[9]
            r["late_times"]=d[10] or " "
            r["early_times"]=d[11] or " "
            r["absent_times"]=d[12] or " "
            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":            
                r["worktime"]=str(d[13])
            else:
                r["worktime"]=d[13]
            r["card_times"]=d[14] or " "
            re.append(r)

        
        Result['datas']=re
        return Result
    except:
        import traceback;traceback.print_exc()
    

@login_required    
def cardtimes_report(request):
    '''
    打卡详情表
    '''
    deptids=request.POST.get('DeptIDs','')
    userids=request.POST.get('UserIDs','')
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')
    st=datetime.datetime.strptime(st,'%Y-%m-%d')
    et=datetime.datetime.strptime(et,'%Y-%m-%d')
    et=et+datetime.timedelta(seconds=86399)
    r=cardtime_calculate(request,deptids,userids,st,et)
    loadall=request.REQUEST.get('pa','')
    
    if not loadall:
       objdata={}
       allr=cardtime_calculate(request,deptids,userids,st,et,True)
       objdata['data']=allr['datas']
       objdata['fields']=allr['fieldnames']
       heads={}
       for i  in  range(len(allr['fieldnames'])):
           heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
       objdata['heads']=heads
       tmp_name=save_datalist(objdata)
       r['tmp_name']=tmp_name#用于导出  没有这个字段导出报错。
    
    return getJSResponse(smart_str(dumps(r)))


def cardtime_calculate(request,deptids,userids,st,et,totalall=False):
    '''
    计算出打卡详情表
    '''
       
    from mysite.att.sql import cardtime_calculate_sql1,cardtime_calculate_sql2
    total_days=int((et-st).days)+1#总天数
    
    Result={}#定义返回的字典，也就是 传递到前台
    re=[]#储存每条记录数
    try:
        #分页        
        try:
            offset = int(request.REQUEST.get('p', 1))#获取分页信息
        except:
            offset=1
            #print "offset:%s"%offset
        uids=[]#储存人员信息
        k=0
        limit= int(request.POST.get('l', settings.PAGE_LIMIT)) 
        if not totalall:
            sql=cardtime_calculate_sql1(deptids,st,et,userids)  
            count_data=((0,),)
            try:
                cur=conn.cursor()
                cur.execute(sql)
                count_data=cur.fetchall()
                conn._commit()
            except:
                print sql
                import traceback;traceback.print_exc()
            
            item_count =count_data[0][0] #获取记录总数
            
            if item_count % limit==0:
                page_count =item_count/limit
            else:
                page_count =int(item_count/limit)+1            
                
            if offset>page_count and page_count:offset=page_count
             
#            ids=ids[(offset-1)*limit:offset*limit]#分页操作
            
            Result['item_count']=item_count#记录总数
            Result['page']=offset          #第几页
            Result['limit']=limit           #每页显示数
            Result['from']=(offset-1)*limit+1 #
            Result['page_count']=page_count  #总页数
#        for u in ids:
#            uids.append(u)
       
        r,Fields,Capt=get_card_times_fields()
        #print "Result['fieldnames']=",Fields
        Result['fieldnames']=Fields
        Result['fieldcaptions']=Capt
        Result['datas']=r
        date =st.date()
        sql=cardtime_calculate_sql2(totalall,Result['from'],deptids,st,et,userids,offset,limit)    
#        print sql
        
        ret_data=[]
        try:
            cur=conn.cursor()
            cur.execute(sql)
            ret_data=cur.fetchall()
            conn._commit()
        except:
            print sql
            import traceback;traceback.print_exc()
            
        for d in ret_data:
            r={'username': '', 'deptname': '', 'userid': -1, 'badgenumber': '', 'card_times': ' ','date':'','super_dept':''}
            r["userid"]=d[1]
            r["super_dept"]=d[2] or " "
            r["deptname"]=d[3] or " "
            r["badgenumber"]=d[4]
            r["username"]=d[5] or " "
            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql" :
                r["date"]=d[6].strftime("%Y-%m-%d")
            else:
                r["date"]=d[6]
            r["times"]=d[7]
            r["card_times"]=d[8] or " "
            re.append(r)

        
        Result['datas']=re
        return Result
    except:
        import traceback;traceback.print_exc()
