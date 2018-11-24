#!/usr/bin/env python
#coding=utf-8
from mysite.personnel.models import Employee, EmpForeignKey,Department,Area
from mysite.iclock.models import *
from mysite.iclock.tools import *
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
#from django.http import HttpResponse
from django.shortcuts import render_to_response
import datetime
from mysite.utils import *
from django.contrib.auth.decorators import permission_required, login_required
from mysite.iclock.dataprocaction import *
#from django.contrib.auth.models import User, Permission
from mysite.iclock.iutils import *
from mysite.iclock.reb        import *
#REBOOT_CHECKTIME, PAGE_LIMIT, ENABLED_MOD, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT
from mysite.iclock.cab import *
#from mysite.iclock.datv import *
from django.utils.translation import ugettext as _
#from django.contrib.auth.models import User
#from django.contrib.sessions.models import Session
from mysite.iclock.datas import *
#from django.utils import simplejson
#from mysite.iclock.datasproc import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from mysite.iclock.datasproc import deleteCalcLog
from dbapp.utils import getJSResponse
from dbapp.datalist import save_datalist
@login_required
def shift_detail(request):
    from datetime import datetime
    if request.method=="POST":
            id=int(request.POST.get("Shift_id","0"))
            unit=int(request.POST.get("unit","1"))
            weekStart=int(request.POST.get("weekStartDay","0"))
            #print "id:%s"%id
            N=NUM_RUN.objects.filter(pk=id).values_list('pk','Name','StartDate','EndDate','Cycle','Units')
            p=[]
            for f in N:
                if type(f)==datetime.date:
                    p.append(f.strftime("%Y-%m-%d"))
                else:
                    p.append(f)
            
            objNRD=NUM_RUN_DEIL.objects.filter(Num_runID=id).order_by('Num_runID', 'Sdays', 'StartTime')
            l=[]
            dic={}
            li=[]
            n=0
            d={}
            #print objNRD
            if objNRD.count()==0:
                    d['StartTime']=0
                    d['EndTime']=0
                    d['Color']=16715535
                    d['SchName']=''
                    l.append(d.copy())
                    qs=l
            else:
                    sch=GetSchClasses()
                    for t in objNRD:
                        try:
                            j=FindSchClassByID(t.SchclassID_id)
                            #print sch[j]
                            x=sch[j]['TimeZone']

                            st=(float(x['StartTime'].hour)+float(x['StartTime'].minute)/60)/24
                            et=(float(x['EndTime'].hour)+float(x['EndTime'].minute)/60)/24
                            sd=t.Sdays
                            ed=t.Edays
                            
                            clr=sch[j]['Color']
#                            if unit==1:
#                                    sd=sd-weekStart
#                                    ed=ed-weekStart
#                                    if ed<0:
#                                            sd=sd+7
#                                            ed=ed+7
                            d['StartTime']=st+sd
                            d['EndTime']=et+ed
                            if clr==None:
                                    d['Color']=16715535
                            else:
                                    d['Color']=clr
                            d['SchName']=t.SchclassID.SchName
                            l.append(d.copy())
                        except:
                            import traceback;traceback.print_exc()
            j={'data':l,'N':p}
                    
    return getJSResponse(smart_str(dumps(j)))

@login_required
def assignedShifts(request):
        if request.method=="POST":
                id=request.POST.get("emp","")
                deptids=request.POST.get("deptIDs","")
                if id=="":
                        deptIDs=deptids.split(',')
                        UserIDs = Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                        len(UserIDs)
                        id=UserIDs[0]
                schPlan=LoadSchPlan(int(id),True,True,True)
                return getJSResponse(smart_str(dumps(schPlan)))

@login_required
def worktimezone(request):
        tzs=[]
        if request.method=="POST":
                id=request.POST.get("UserID"," ")
                d1=request.POST.get("ComeTime"," ")
                d2=request.POST.get("EndDate"," ")
                d1=datetime.datetime.strptime(d1,'%Y-%m-%d')
                d2=datetime.datetime.strptime(d2,'%Y-%m-%d')
                userplan=LoadSchPlanEx(id,True,True)
                l=GetUserScheduler(int(id), d1, d2, userplan['HasHoliday'])
                for t in l:
                        
                        if t['TimeZone']['StartTime']>=d1 and t['TimeZone']['EndTime']<d2+datetime.timedelta(days=2):
                                li=[]
                                k={}
                                if t['TimeZone']['EndTime']>d2+datetime.timedelta(days=1):
                                        k['dis']=t['TimeZone']['StartTime']-d1
                                        k['die']=d2+datetime.timedelta(days=1)-d1
                                        li.append(k.copy())
                                        k['dis']=d2+datetime.timedelta(days=1)-d1
                                        k['die']=t['TimeZone']['EndTime']-d1
                                        
                                        li.append(k.copy())
                                else:
                                        k['dis']=t['TimeZone']['StartTime']-d1
                                        k['die']=t['TimeZone']['EndTime']-d1
                                        li.append(k.copy())
                                for v in li:
                                        d={}
                                        dd1=v['dis'].days
                                        dd2=v['die'].days
                                        dt1=float(v['dis'].seconds)/60/60/24
                                        dt2=float(v['die'].seconds)/60/60/24
                                        ds=dd1+dt1
                                        de=dd2+dt2
                                        d['StartTime']=ds
                                        d['EndTime']=de
                                        d['SchClassID']=t['schClassID']
                                        if 'Color' in t:
                                                d['Color']=t['Color']
                                        else:
                                                d['Color']=16715535
                                        tzs.append(d.copy())
        return getJSResponse(smart_str(dumps(tzs)))

@login_required
def attrule(request):
        l=[]
        InitData()
        attrule=LoadAttRule()
        l.append(attrule)
        return getJSResponse(smart_str(dumps(l)))



@permission_required("iclock.browse_employee")  #指纹采集器登记指纹渲染页面
def registerFinger(request):
        request.user.iclock_url_rel='../..'
        request.model = employee
        return render_to_response('RegisterFP_list.html',
                                                        RequestContext(request, {
                                                        'from': 1,
                                                        'page': 1,
                                                        'limit': 10,
                                                        'item_count': 4,
                                                        'page_count': 1,
                                                        'iclock_url_rel': request.user.iclock_url_rel,
                                                        }))

@permission_required("iclock.browse_employee")
def savePhoto(request):    #上传人员照片
        request.user.iclock_url_rel='../..'
        request.model = employee
        if not request.method == 'POST':
                return render_to_response('employeePhoto_list.html',
                                                                                RequestContext(request, {
                                                                                'from': 1,
                                                                                'page': 1,
                                                                                'limit': 10,
                                                                                'item_count': 4,
                                                                                'page_count': 1,
                                                                                'iclock_url_rel': request.user.iclock_url_rel,
                                }))
                        
        else:
                f=request.FILES["fileToUpload"]
                from mysite.iclock.datamisc import saveUploadImage
                fname="%s%s/%s"%(settings.MEDIA_ROOT,'img/employee', f)
                saveUploadImage(request, "fileToUpload", fname)
                return HttpResponse("result=0");


@login_required
def saveFingerprint(request):    #保存指纹采集器登记的指纹模板
        userid=int(request.POST['UserIDs'])
        fid=request.POST.get('fingerid',0)
        tmp=request.POST.get('templates','')
        tmps=tmp.split(',')
        fids=fid.split(',')
        for i in range(len(fids)):
                try:
                        
                        f=fptemp.objects.filter(UserID=userid, FingerID=int(fids[i])-1)
                        if f.count():
                                sql="update template set template = '%s', utime='%s' where userid='%s' and fingerid=%s" % (tmps[i], str(datetime.datetime.now())[:19], userid, int(fids[i])-1)
                        else:
                                sql="insert into template(template, userid, fingerid,  utime, valid, DelTag) values('%s', '%s', %s, '%s', 1, '0')" % (tmps[i], userid, int(fids[i])-1, str(datetime.datetime.now())[:19])
                        customSql(sql)
                except:
                        return getJSResponse("result=1")
        return getJSResponse("result=0")



@permission_required("iclock.Forget_transaction")
def forget(request):
        from mysite.iclock.models import Transaction
        from dbapp.urls import dbapp_url
        from base import get_all_app_and_models
        from mysite.settings import MEDIA_ROOT
        request.dbapp_url=dbapp_url
        apps=get_all_app_and_models()
        
        request.user.iclock_url_rel='../..'
        request.model = Transaction
        dict=checkForget()
       
        return render_to_response('ForgetAtt_list.html',
                                                        RequestContext(request, {'ForgetAtt_list': dumps(dict),
                                                        'from': 1,
                                                        'page': 1,
                                                        'limit': 10,
                                                        'item_count': 4,
                                                        'page_count': 1,
                                                        'iclock_url_rel': request.user.iclock_url_rel,
                                                        'dbapp_url': dbapp_url,
                                                        'MEDIA_URL':MEDIA_ROOT,
                                                        "current_app":'att', 
                                                        'apps':apps,
        												"myapp": [a for a in apps if a[0]=="att"][0][1],
                                                        }))
                                                        
@permission_required("iclock.browse_user_of_run")
def searchShifts(request):
        request.user.iclock_url_rel='../..'
        request.model = Transaction
        return render_to_response('search_shifts.html',
                                                        RequestContext(request, {
                                                        'from': 1,
                                                        'page': 1,
                                                        'limit': 10,
                                                        'item_count': 4,
                                                        'page_count': 1,
                                                        'iclock_url_rel': request.user.iclock_url_rel,
                                                        }))

@login_required
def        searchComposite():                        #综合排班列表
        pass

@permission_required("iclock.add_user_of_run")
def deleteTmpShifts(request):
        request.user.iclock_url_rel='../..'
        request.model = Transaction
        return render_to_response('delete_tmpshifts.html',
                                                        RequestContext(request, {
                                                        'from': 1,
                                                        'page': 1,
                                                        'limit': 10,
                                                        'item_count': 4,
                                                        'page_count': 1,
                                                        'iclock_url_rel': request.user.iclock_url_rel,
                                                        }))


@login_required
def        clearUserDefinedRep():                        #清除所有自定义报表
        pass


@login_required
def saveCheckForget(request):
        from mysite.iclock.models.model_trans import Transaction
        from mysite.att.models.checkexact_model import CheckExact
        
        l=[]
        userids=request.POST.get('UserIDs')
        deptids=request.POST.get('deptIDs')
        sdate=request.POST.get('checkdate')+' '+request.POST.get('checktime')
        st=datetime.datetime.strptime(sdate,'%Y-%m-%d %H:%M:%S')
        nt=st.strftime('%Y-%m-%d %H:%M:%S')
        ct=ATTSTATES[int(request.POST.get('checktype'))][0]
        reson=request.POST.get('reson')
        first_name=request.user.first_name
        #if not allowAction(st,3):
        #        return getJSResponse("result=1;message=%s"%(_('Save Fail,account has been locked!')))
        
        if len(userids)>0 and userids!='null':
                uids=userids.split(',')
        elif len(deptids)>0:
                deptIDS=deptids.split(',')
                uids=Employee.objects.filter(DeptID__in=deptIDS ).values_list('id', flat=True).order_by('id')
                
        if not first_name:
                first_name=request.user
        time=datetime.datetime.now()
        time=datetime.datetime.strftime(time,'%Y-%m-%d %H:%M:%S')
        try:
           
            for i in uids:
                    if settings.DATABASE_ENGINE == 'oracle':
                        sql_log="""insert into %s (UserID, CHECKTIME, CHECKTYPE, YUYIN,MODIFYBY,"DATE") values('%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', '%s', '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'))""" % (CheckExact._meta.db_table, int(i), nt,ct, reson, first_name,time)
                        sql="""insert into %s (userid, checktime, checktype,verifycode) values('%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s',5)""" % (Transaction._meta.db_table, int(i), nt, ct)
    #                        print sql_log,sql
                    else:
                        sql_log="""insert into %s (UserID, CHECKTIME, CHECKTYPE, YUYIN,MODIFYBY,DATE) values('%s', '%s', '%s', '%s', '%s', '%s')""" % (CheckExact._meta.db_table, int(i), nt,ct, reson, first_name,time)
                        sql="""insert into %s (userid, checktime, checktype,verifycode) values('%s', '%s', '%s',5)""" % (Transaction._meta.db_table, int(i), nt, ct)
                    
                    ret=customSql(sql)
                    if ret!=None:
                            deleteCalcLog(UserID=i)
                            ret=customSql(sql_log)
                    else:
                            break
                
            #adminLog(time=datetime.datetime.now(),User=request.user, model=u"%s"%Transaction._meta.verbose_name,action=_("Add"),object=request.META["REMOTE_ADDR"]).save()
            
            if ret!=None:
                    return HttpResponse("result=0")
            else:
                    return HttpResponse("result=1;message=%s"%(_(u'保存失败，考勤记录可能重复了')))
        except:
            import traceback;traceback.print_exc()        
@login_required
def saveFields(request):
        u=request.user
        f=request.POST.get('Fields','')
        tblName=request.POST.get('tblName','')
        item=ItemDefine(Author=u,ItemName=tblName,ItemType='report_fields_define')
        if f!="":
                #item=ItemDefine(Author=u,ItemName=tblName,ItemType='report_fields_define',ItemValue=f)
                item.ItemValue=f
                item.save()
        else:
                item.delete()
        return getJSResponse("result=0")

@login_required
def calcLeaveReport(request):
        deptIDs=request.POST.get('DeptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('ComeTime','')
        et=request.POST.get('EndTime','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')

        r=CalcLeaveReportItem(request,deptIDs,userIDs,st,et)
        
        loadall=request.REQUEST.get('pa','')
        p_datas=r['datas']
        if not loadall:
            objdata={}
            allr=CalcLeaveReportItem(request,deptIDs,userIDs,st,et,0,True)
            
            objdata['data']=allr['datas']
            objdata['fields']=allr['fieldnames']
            heads={}
            for i  in  range(len(allr['fieldnames'])):
                heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
            objdata['heads']=heads
            tmp_name=save_datalist(objdata)
            r['tmp_name']=tmp_name
        r['datas']=p_datas
        return getJSResponse(smart_str(dumps(r)))

@login_required
def calcAttShiftsReport(request):
        deptIDs=request.POST.get('DeptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('ComeTime','')
        et=request.POST.get('EndTime','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        r=CalcAttShiftsReportItem(request,deptIDs,userIDs,st,et)
        return getJSResponse(smart_str(dumps(r)))





@login_required
def calcReport(request):
        deptIDs=request.POST.get('DeptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('ComeTime','')
        et=request.POST.get('EndTime','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        r=CalcReportItem(request,deptIDs,userIDs,st,et)
        loadall=request.REQUEST.get('pa','')
        if not loadall:
            objdata={}
            allr=CalcReportItem(request,deptIDs,userIDs,st,et,0,True)
            objdata['data']=allr['datas']
            objdata['fields']=allr['fieldnames']
            heads={}
            for i  in  range(len(allr['fieldnames'])):
                heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
            objdata['heads']=heads
    
            tmp_name=save_datalist(objdata)
            r['tmp_name']=tmp_name
        return getJSResponse(smart_str(dumps(r)))

@login_required
def calcPriReport(request):
        if request.method=="POST":
                deptIDs=request.POST.get('DeptIDs',"")
                userIDs=request.POST.get('UserIDs',"")
                st=request.POST.get('ComeTime','')
                et=request.POST.get('EndTime','')
                isforce=request.POST.get('IsForce','1')
                st=datetime.datetime.strptime(st,'%Y-%m-%d')
                et=datetime.datetime.strptime(et,'%Y-%m-%d')
                deptids=[]
                userids=[]
                if userIDs == "":
                        deptids=deptIDs.split(',')
                else:
                        userids=userIDs.split(',')


                if userids or deptids:        
                        t1=datetime.datetime.now()
                        re=PriReportCalc(userids,deptids,st,et,int(isforce))
                        t2=datetime.datetime.now()-t1
                        if re==-3:
                                r=getJSResponse("result=-3")
                        elif re==-4:
                                r=getJSResponse("result=0;message=%s"%(_(u"账户已经被锁定！")))
                        else:
                                r=getJSResponse("result=0;message=%s%s%d sec"%(_(u'计算成功'),_(u'总时间'),t2.seconds))
                else:
                        r=getJSResponse("result=1")
                return r

@login_required
def dailycalcReport(request):
        deptIDs=request.POST.get('DeptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('ComeTime','')
        et=request.POST.get('EndTime','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        #修改  郭学文   2010-05-17
#        et=et+datetime.timedelta(days=-1)
#        print "-------------------",st,et,deptIDs,userIDs
#        st=datetime.datetime(2008,5,1)
#        et=datetime.datetime(2008,5,30)
        r=CalcReportItem(request,deptIDs,userIDs,st,et,1)
#        print "11111111111111111111111"
        loadall=request.REQUEST.get('pa','')
        if not loadall:
            
            allr=CalcReportItem(request,deptIDs,userIDs,st,et,1,True)
            objdata={}
            objdata['data']=allr['datas']
            objdata['fields']=allr['fieldnames']
            heads={}
            for i  in  range(len(allr['fieldnames'])):
                heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
            objdata['heads']=heads
            
            tmp_name=save_datalist(objdata)
            r['tmp_name']=tmp_name
#            print "allr['fieldnames']:%s"%r['fieldnames']
        return getJSResponse(smart_str(dumps(r)))

@permission_required("iclock.reCalcaluteReport_itemdefine")
def reCaluate(request):
        request.user.iclock_url_rel='../..'
        request.model = Transaction
        return render_to_response('CalcReports.html',
                                                RequestContext(request, {
                                                'from': 1,
                                                'page': 1,
                                                'limit': 10,
                                                'item_count': 4,
                                                'page_count': 1,
                                                'iclock_url_rel': request.user.iclock_url_rel,
                                                }))
@login_required                                                
def reCaluateAction(request):
   
        if request.method=="POST":
                deptIDs=request.POST.get('DeptIDs',"")
                userIDs=request.POST.get('UserIDs',"")
                st=request.POST.get('ComeTime','')
                et=request.POST.get('EndTime','')
                isforce=request.POST.get('isForce','0')
                st=datetime.datetime.strptime(st,'%Y-%m-%d')
                et=datetime.datetime.strptime(et,'%Y-%m-%d')
                deptids=[]
                userids=[]
                if userIDs == "":
                        deptids=deptIDs.split(',')
                        userids=Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                else:
                        userids=userIDs.split(',')
                
                
                if userids or deptids:        
#                        print "OK"
                        t1=datetime.datetime.now()
#                        re=MainCalc(userids,deptids,st,et,int(isforce))# lehman 2010-06-01 屏蔽 
                        try:
                           from mysite.iclock.attcalc import MainCalc_new                            
                           re = MainCalc_new(userids,deptids,st,et,int(isforce)) # lehman 2010-06-01 加入
                        except:
                            import traceback;
                            traceback.print_exc()                            
                        t2=datetime.datetime.now()-t1
                        if re==-3:
                                r=getJSResponse("result=-3")
                        elif re==-4:
                                r=getJSResponse("result=0;message=%s"%(_(u"账户已经被锁定！")))
                        else:
                                r=getJSResponse("result=0;message=%s%s%d sec"%(_(u'计算成功'),_(u'总时间'),t2.seconds))
                else:
                        r=getJSResponse("result=1")
                #if userIDs == "":
                        #try:
                                #deptIDs=deptIDs.split(',')
                                #userlist = Employee.objects.filter(DeptID__in=deptIDs ).values_list('id', flat=True).order_by('id')
                        #except:
                                #pass
                        #userIDs=",".join(["%s" % int(i) for i in userlist])
                #t1=datetime.datetime.now()
                #if len(userIDs)>0:        
                        #re=MainCalc(userIDs,st,et,1)
                        #t2=datetime.datetime.now()-t1
                        #if re==-3:
                                #r=getJSResponse("result=-3")
                        #else:
                                #r=getJSResponse("result=0;message=%d sec"%(t2.seconds))
                #else:
                        #r=getJSResponse("result=1")
                return r

@login_required
def savespecialday(request):
        if request.method=="POST":
                id=request.POST.get('id','')
                userids=request.POST.get('UserID','')
                if id=="_new_":
                        userids=userids.split(',')
                st=request.POST.get('StartSpecDay','')
                et=request.POST.get('EndSpecDay','')
                at=request.POST.get('ApplyDate','')
                reson=request.POST.get('YUANYING','')
                dateid=request.POST.get('DateID','')
                clearance=request.POST.get('clearance','')
                st=datetime.datetime.strptime(st,"%Y-%m-%d %H:%M:%S")
                et=datetime.datetime.strptime(et,"%Y-%m-%d %H:%M:%S")
                if not allowAction(st,2,et):
                        return getJSResponse("result=1;message=%s"%(_(u'账户已经被锁定！')))
                try:
                
                        if id=="_new_":
                                for i in userids:
                                        if settings.DATABASE_ENGINE == 'oracle':
                                                sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,"DATE",DateID,clearance,State) values('%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'),'%s','%s','0')""" % (USER_SPEDAY._meta.db_table, int(i),st,et,reson, at,dateid,clearance)
                                        else:
                                                sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,Date,DateID,clearance,State) values('%s', '%s', '%s', '%s','%s','%s','%s','0')""" % (USER_SPEDAY._meta.db_table, int(i), st, et,reson, at,dateid,clearance)
                                        customSql(sql)
                                        deleteCalcLog(UserID=i)
                        else:
                                if settings.DATABASE_ENGINE == 'oracle':
                                        sql="""update %s set StartSpecDay=to_date('%s','YYYY-MM-DD HH24:MI:SS'),EndSpecDay=to_date('%s','YYYY-MM-DD HH24:MI:SS'),YUANYING='%s',"DATE"=to_date('%s','YYYY-MM-DD HH24:MI:SS'),DateID='%s',clearance='%s' where id=%s"""%(USER_SPEDAY._meta.db_table,st,et,reson,at,dateid,clearance,id)
                                else:
                                        sql="update %s set StartSpecDay='%s',EndSpecDay='%s',YUANYING='%s',Date='%s',DateID='%s',clearance='%s' where id=%s"%(USER_SPEDAY._meta.db_table,st,et,reson,at,dateid,clearance,id)
                                customSql(sql)
                                deleteCalcLog(UserID=id)
                except:
                        return getJSResponse(u"result=1;message=%s"%(_(u'非法异常')))
                return getJSResponse("result=0")

@login_required
def applySpecialday(request):
        if request.method=="POST":
                id=request.POST.get('id','')
                st=request.POST.get('StartSpecDay','')
                et=request.POST.get('EndSpecDay','')
                at=request.POST.get('ApplyDate','')
                reson=request.POST.get('YUANYING','')
                dateid=request.POST.get('DateID','')
                st=datetime.datetime.strptime(st,"%Y-%m-%d %H:%M:%S")
                et=datetime.datetime.strptime(et,"%Y-%m-%d %H:%M:%S")
                if id=='':
                        return getJSResponse("result=1")
                try:
                        if settings.DATABASE_ENGINE == 'oracle':
                                sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,"DATE",DateID,State) values('%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'),'%s','0')""" % (USER_SPEDAY._meta.db_table, int(id),st,et,reson, at,dateid)
#                                print 111,sql
                        else:
                                sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,Date,DateID,State) values('%s', '%s', '%s', '%s','%s','%s','0')""" % (USER_SPEDAY._meta.db_table, int(id), st, et,reson, at,dateid)
                        customSql(sql)
#                        deleteCalcLog(UserID=int(id))
                        #adminLog(time=datetime.datetime.now(),User=request.user, model=u"%s"%USER_SPEDAY._meta.verbose_name,action=_("Add"),object=request.META["REMOTE_ADDR"]).save()
                except:
                        return getJSResponse("result=1")
                return getJSResponse("result=0")
        
@login_required
def auditedTrans(request):
        try:        
                id=int(request.POST['id'])
                rk=request.POST['remarks']
                sql="update %s set Reserved2='%s' where id=%s "%(Transaction._meta.db_table,rk,id)
                customSql(sql)
                return getJSResponse("result=0")
        except:
                return getJSResponse("result=1")
                
def deleteLeaveClass(request):
        id=request.GET.get('LeaveId','')
        sql="delete from %s where LeaveId=%s"%(LeaveClass._meta.db_table, id)
        customSql(sql)
        return getJSResponse("result=0")

def submitLeaveClass(request):
        if request.method=="POST":
                s=request.POST['LeaveClass']
                l=loads(s)
                SaveLeaveClass(l,1)  #保存假类表
                InitData()
                #adminLog(time=datetime.datetime.now(),User=request.user, model='LeaveClass').save()
                return getJSResponse("result=0")

def submitAttParam(request):
    try:
        from mysite.personnel.models import Department
        if request.method=="POST":
                #dept=request.POST.get('CompanyLogo','Our Company')
                d=Department.objects.get(pk=1)
                #d.name=dept
                d.save()
                s=request.POST['LeaveClass']
                l=loads(s)
                try:
                    SaveAttRule(request.POST)
                except:
                    return getJSResponse(_(u'填写不完整或者不合法!'))
                SaveLeaveClass(l)
                InitData()
                #adminLog(time=datetime.datetime.now(),User=request.user, model='AttParam').save()
                return getJSResponse("result=0")
    except:
        import traceback;traceback.print_exc()

def getLeaveClass(request):
        ls=GetLeaveClasses(1)
        return getJSResponse(smart_str(dumps(ls)))

@login_required
def deleteEmpFromDevice(request):
        userids=request.POST.get("userids","")
        deptIDs=request.POST.get("deptIDs","")
        sns=request.POST.getlist("K")
        flag=int(request.POST.get("flag"))        #flag=1为从所有设备删除人员
        if userids=='':
                deptidlist=[int(i) for i in deptIDs.split(',')]
                deptids=[]
                for d in deptidlist:#支持选择多部门
                        deptids+=getAllAuthChildDept(d,request)
                userids=Employee.objects.filter(DeptID__in=deptids)  
        else:
                emplist=userids.split(',')
                userids=Employee.objects.filter(id__in=emplist)  
        len(userids)
        if flag==1:
                o_devs=iclock.objects.all()
        else:
                o_devs=iclock.objects.filter(SN__in=sns)
        for dev in o_devs:
                d=getDevice(dev.SN)
                for userPin in userids:
                        append_dev_cmd(d, "DATA DEL_USER PIN=%s"%userPin.PIN)
                sendRecCMD(d)
        return getJSResponse("result=0")
        
        

@login_required
def getData(request):
        funid = request.REQUEST.get("func", "")
        if funid == 'init_database':
                ClearDataAll()
                #adminLog(time=datetime.datetime.now(), User=request.user, action="InitSystem", object=request.META["REMOTE_ADDR"]).save()
        elif funid == 'clearObsoleteData':
                attEndTime = request.REQUEST.get("attEndTime", "")
                attEndTime1 = request.REQUEST.get("attEndTime1", "")
                attEndTime2 = request.REQUEST.get("attEndTime2", "")
                if attEndTime!= "":
                        attEndTime = attEndTime + " 23:59:59"
                        Condition = "checktime <= '%s'" % attEndTime
                        ClearTableData("checkinout", Condition)
                        #adminLog(time=datetime.datetime.now(), User=request.user, action="Clear Obsolete Transaction Data", object=request.META["REMOTE_ADDR"]).save()
                #if attEndTime1!= "":
                        #清除照片功能,未完
                        #adminLog(time=datetime.datetime.now(), User=request.user, action="Clear Obsolete Transaction picture Data", object=request.META["REMOTE_ADDR"]).save()
                if attEndTime2!= "":
                        attEndTime = attEndTime2 + " 23:59:59"
                        Condition = "checktime <= '%s'" % attEndTime2
                        ClearTableData(attRecAbnormite._meta.db_table, Condition)

                        Condition = "attdate <= '%s'" % attEndTime2
                        ClearTableData(attShifts._meta.db_table, Condition)

                        ClearTableData(AttException._meta.db_table, Condition)
                        #adminLog(time=datetime.datetime.now(), User=request.user, action="Clear Obsolete cacluate Data", object=request.META["REMOTE_ADDR"]).save()
                        return getJSResponse('result=0')
        elif funid == 'schClass':
                schclasses = GetSchClasses()
                re = []
                ss = {}
                for t in schclasses:
                        ss['SchclassID'] = t['schClassID']
                        ss['SchName'] = t['SchName']
                        ss['StartTime'] = t['TimeZone']['StartTime'].time()
                        ss['EndTime'] = t['TimeZone']['EndTime'].time()
                        t = ss.copy()
                        re.append(t)
                return getJSResponse(smart_str(dumps(re)))
        elif funid == 'shifts':
                nrun = NUM_RUN.objects.all().order_by('Num_runID')
                len(nrun)
                re = []
                ss = {}
                for t in nrun:
                        ss['shift_id'] = t.Num_runID
                        ss['shift_name'] = t.Name
                        t = ss.copy()
                        re.append(t)
                return getJSResponse(smart_str(dumps(re)))
        elif funid == 'employee':
#                deptIDs = request.REQUEST.get("deptIDs").split(',')
                pin=request.REQUEST.get("pin")
                if pin:
                        emps = Employee.objects.filter(PIN__exact=pin)
                        len(emps)
#                else:
#                        emps = Employee.objects.filter(DeptID__in=deptIDs).order_by('id')
                emp = []
                e = {}
                for i in emps:
                        e['id'] = i.id
                        e['PIN'] = i.PIN
                        e['EName'] = i.EName
                        e['DeptName'] = i.Dept().DeptName
                        t = e.copy()
                        emp.append(t)
                return getJSResponse(smart_str(dumps(emp)))
        elif funid == 'leaveClass':
                qs = GetLeaveClasses(1)
                return getJSResponse(smart_str(dumps(qs)))
        elif funid == 'attParam':
                InitData()
                la = LoadAttRule()
                lc = LoadCalcItems()
                qs = la.copy()
                qs['LeaveClass'] = lc
                return getJSResponse(smart_str(dumps(qs)))
        elif funid == 'department':
                if not request.user.is_superuser:                        
                        dept_list=userDeptList(request.user)
                        dd=[]
                        for i in dept_list:
                                dd.append(int(i.id))
                        objs=Department.objects.filter(id__in=dd).order_by('id').values_list("id", "name","parent")
                else:
                        objs = Department.objects.all().order_by('id').values_list("id", "name","parent")
                
#                orderStr=['id']
#                objs=objs.order_by(*orderStr)
#                deptObj = []
#                d = {}
#                len(objs)
#                for i in objs:
#                        d['DeptID'] = int(i['id'])
#                        d['DeptName'] = i['name']
#                        d['parent'] = i['parent']
#                        t = d.copy()
#                        deptObj.append(objs)
                xdata=[]
                for o in  objs:xdata.append(list(o))
                return getJSResponse(smart_str(dumps(xdata)))
        elif funid=="area":
            
                if not request.user.is_superuser:
                        area_list = userAreaList(request.user)
                        dd=[]
                        for i in area_list:
                                dd.append(int(i.id))
                        objs=Area.objects.filter(id__in=dd).order_by('id').values_list("id", "areaname","parent")
                else:
                        objs =Area.objects.all().order_by('id').values_list("id", "areaname","parent")
                xdata=[]
                for o in  objs:xdata.append(list(o))
                return getJSResponse(smart_str(dumps(xdata)))
        elif funid=="areadevice":
                if not request.user.is_superuser:
                        area_list = userAreaList(request.user)
                        dd=[]
                        for i in area_list:
                                dd.append(int(i.id))
                        objs=Area.objects.filter(id__in=dd).order_by('id').values_list("id", "areaname","parent")
                else:
                        objs =Area.objects.all().order_by('id').values_list("id", "areaname","parent")
                
                xdata=[]
                for o in  objs:xdata.append(list(o))
                try:
                    maxid= xdata[len(xdata)-1][0]
                    objsd = Device.objects.filter(device_type__exact='1').values_list("sn","alias","area")
                    for o in  objsd:
                        maxid = maxid+1
                        i = list(o)
                        i[0] =maxid
                        xdata.append(i)
                except:
                    import traceback; traceback.print_exc()
                return getJSResponse(smart_str(dumps(xdata)))
                
        elif funid=='attTotal':
                t,rFieldNames,rCaption=ConstructFields()
                dis=FetchDisabledFields(request.user,funid)
                d={}
                d['FieldNames']=rFieldNames
                d['FieldCaptions']=rCaption
                d['disableCols']=dis
                return getJSResponse(smart_str(dumps(d)))
        elif funid=='attDailyTotal':
                st=request.POST.get('startDate','')
                et=request.POST.get('endDate','')
                if (st=='') or (et==''):
                        st=datetime.datetime.now()
                        et=datetime.datetime.now()
                d1=datetime.datetime.strptime(st,'%Y-%m-%d')
                d2=datetime.datetime.strptime(et,'%Y-%m-%d')

                t,rFieldNames,rCaption=ConstructFields1(d1,d2)
                #rCaption=ConstructFields1(st,et)[2]
                #item=ItemDefine.objects.filter(Author=request.user,ItemName=funid,ItemType='report_fields_define')
                dis=FetchDisabledFields(request.user,funid)
                d={}
                d['FieldNames']=rFieldNames
                d['FieldCaptions']=rCaption
                d['disableCols']=dis
                return getJSResponse(smart_str(dumps(d)))
        elif funid=='attShifts':
                #rFieldNames=FetchModelFields('attShifts')
                #rCaption=FetchModelFieldsCaption('attShifts')
                """for New attshifts detail"""
                rFieldNames,rCaption,r=ConstructAttshiftsFields1()
                rFieldNames.remove('userid')
                rCaption.remove('UserID')
                
                
                dis=FetchDisabledFields(request.user,funid)
                d={}
                d['FieldNames']=rFieldNames
                d['FieldCaptions']=rCaption
                d['disableCols']=dis
                return getJSResponse(smart_str(dumps(d)))

        return getJSResponse('result=0')

def ClearDataAll():
        #EXCNOTES.objects.all().delete()
        holidays.objects.all().delete()
        NUM_RUN.objects.all().delete()
        SchClass.objects.all().delete()
        SECURITYDETAILS.objects.all().delete()
#        LeaveClass.objects.all().delete()
#        LeaveClass1.objects.all().delete()
#        AttParam.objects.all().delete()
        UserUsedSClasses.objects.all().delete()
        attCalcLog.objects.all().delete()
        attRecAbnormite.objects.all().delete()
        AttException.objects.all().delete()
#        adminLog.objects.all().delete()
#        sql='''delete from auth_user where (username<>'%s') and  (is_superuser<>1)'''%('employee')
#        customSql(sql)
#        initDB()
        clearData()
        InitData()
#        print "Init Success"
@permission_required("iclock.browse_employee")
def NoFingerCount(request):#, qs, offset, limit, cl, state):
        request.user.iclock_url_rel='../..'
        request.model = employee
        count=0
        curCount=0
        try:
                offset = int(request.GET.get('p', 1))
                deptid=request.GET.get('DeptID__DeptID__in')
                deptid=deptid.split(',')
        except:
                offset=1
        limit= int(request.GET.get('l', settings.PAGE_LIMIT))
        state = int(request.GET.get('s', -1))

        qs=Employee.objects.filter(DeptID__DeptID__in=deptid).extra(where=['UserID NOT IN (%s)'%('select userid from template')])
        paginator = Paginator(qs, limit)
        item_count = paginator.count
        if offset>paginator.num_pages: offset=paginator.num_pages
        if offset<1: offset=1
        pgList = paginator.page(offset)
        cc={'latest_item_list': pgList.object_list,
                'from': (offset-1)*limit+1,
                'item_count': item_count,
                'page': offset,
                'limit': limit,
                'page_count': paginator.num_pages,
                'dataOpt': Employee._meta,
                'iclock_url_rel': request.user.iclock_url_rel,
                }

        tmpFile='empsInDept_noFP.html'
        return render_to_response(tmpFile, cc,RequestContext(request, {}))
#----------------------------------------------------------------------
@login_required
def  searchComposite(request):
        deptIDs=request.POST.get('deptIDs',"")
        userIDs=request.POST.get('UserIDs',"")
        st=request.POST.get('startDate','')
        et=request.POST.get('endDate','')
        st=datetime.datetime.strptime(st,'%Y-%m-%d')
        et=datetime.datetime.strptime(et,'%Y-%m-%d')
        if len(userIDs)>0 and userIDs!='null':
                ids=userIDs.split(',')
        elif len(deptIDs)>0:
                deptids=deptIDs.split(',')
#                deptids=[]
#                for d in deptidS:#支持选择多部门
#                        deptids+=getAllAuthChildDept(d,request)
                ot=['DeptID','PIN']
                ids=Employee.objects.filter(DeptID__in=deptids,OffDuty__lt=1).values_list('id', flat=True).order_by(*ot)
        try:
                offset = int(request.GET.get('p', 1))
        except:
                offset=1
                
        Fields,Capt=ConstructScheduleFields()
        re=[]
        Result={}
        Result['fieldnames']=Fields
        Result['fieldcaptions']=Capt
        Result['datas']=re

        for id in ids:
                userplan=LoadSchPlanEx(id,True,True)
                l=GetUserScheduler(int(id), st, et, userplan['HasHoliday'])
                d={}
                for t in l:
                        d['userid']=id
                        d['deptid']=userplan['DeptName']
                        d['badgenumber']=userplan['BadgeNumber']
                        d['username']=userplan['UserName']
                        d['starttime']=t['TimeZone']['StartTime']
                        d['endtime']=t['TimeZone']['EndTime']
                        d['schname']=t['SchName']
                        re.append(d.copy())
        limit= int(request.GET.get('l', 500))
        page_count =len(re)/limit+1
        if offset>page_count:offet=page_count
        item_count =len(re)
        res=re[(offset-1)*limit:offset*limit]
        Result['item_count']=item_count
        Result['page']=offset
        Result['limit']=limit
        Result['from']=(offset-1)*limit+1
        Result['page_count']=page_count
        Result['datas']=res
        return getJSResponse(smart_str(dumps(Result)))


