#coding=utf-8
from mysite.iclock.models import *
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response
import datetime
from django.contrib.auth.decorators import login_required,permission_required
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.models import Employee, Department

def getDBSetting():
        from django.conf import settings
        return {'DATABASE_ENGINE': settings.DATABASE_ENGINE,
                'DATABASE_NAME': settings.DATABASE_NAME,
                'DATABASE_USER': settings.DATABASE_USER,
                'DATABASE_PASSWORD': settings.DATABASE_PASSWORD,
                'DATABASE_HOST': settings.DATABASE_HOST,
                'DATABASE_PORT': settings.DATABASE_PORT}

def changeDBSetting(opt):
        from django.conf import settings
        settings.DATABASE_ENGINE=opt['DATABASE_ENGINE']
        settings.DATABASE_NAME=        opt['DATABASE_NAME']        
        settings.DATABASE_USER=        opt['DATABASE_USER']         
        settings.DATABASE_PASSWORD=        opt['DATABASE_PASSWORD']
        settings.DATABASE_HOST=        opt['DATABASE_HOST']         
        settings.DATABASE_PORT=        opt['DATABASE_PORT']         
                
def getNewCursor(opt):
        try:
                _import_path = 'django.db.backends.'
                backend = __import__('%s%s.base' % (_import_path, opt['DATABASE_ENGINE']), {}, {}, [''],0)
        except ImportError, e:
                backend = __import__('%s.base' % opt['DATABASE_ENGINE'], {}, {}, [''],0)
        #print backend, dir(backend)
        old=getDBSetting()
        changeDBSetting(opt)
        #print getDBSetting()
        try:
                connection=backend.DatabaseWrapper()
                cursor = connection.cursor()
                return connection, cursor
        finally:
                changeDBSetting(old)

def appendTimeFields(fields, prefix, time):
        fields[prefix+'YEAR']=time.year
        fields[prefix+'MONTH']=time.month
        fields[prefix+'DAY']=time.day
        fields[prefix+'HOUR']=time.hour
        fields[prefix+'MINUTE']=time.minute
        fields[prefix+'SECOND']=time.second
        fields[prefix+'TIME']=time.strftime("%H%M%S")

def mergeDict(d1,d2):
        for k in d2: d1[k]=d2[k]

def appendDevFields(row, snName, has_alias):        
        sn=row[snName]
        row['Device_SN']=sn
        if has_alias: 
                dev=get_device(sn)
                row['Device_Alias']=dev and dev.Alias or None
        
def doEmpExportData(opts, emps, fn):
        tail=opts['dexp_e_tail']
        head=opts['dexp_e_head']
        row_tail='\r\n'
        if opts['dexp_rowsp']=='rowsp13': 
                row_tail='\n'
        elif opts['dexp_rowsp']=='rowsp10': 
                row_tail='\r'
        row_fmt=opts['dexp_e_row']
        has_alia=("%(Device_Alias)" in row_fmt) 
        f=file(fn, "a+b")
        if head: f.write(head+row_tail)
        for r in emps:
                appendDevFields(r, 'SN', has_alia)
                for c in r: 
                        if r[c]==None: r[c]=""
                s=(row_fmt%r)+row_tail
                f.write(s.encode('utf-8'))
        if tail: f.write(tail+row_tail)
        f.close()

def getTransState(prefix, opts):
        prefix_len=len(prefix)
        trans={}
        for key in opts:
                if key[:prefix_len]==prefix:
                        value=opts[key]
                        key=key[prefix_len:]
                        if value:
                                trans[key]=value
                        else:
                                trans[key]=''
#        print prefix, trans
        return trans

def getTransWC(prefix, opts):
        prefix_len=len(prefix)
        trans={}
        for key in opts:
                value=opts[key]
                if value and (key[:prefix_len]==prefix):
                        key=key[prefix_len:]
                        key2=prefix+"t_"+key
                        if (key2 in opts) and (opts[key2]):
                                trans[value]=opts[key2]
        print prefix, trans
        return trans

def transKey(r, k, has_state):        
        key=r[k]
        if key and has_state:
                try:
                        r[k]=has_state[key]
                except:
                        has_state[key]=r[k]
        
def doTransExportData(opts, emps, fn):
        tail=opts['dexp_t_tail']
        head=opts['dexp_t_head']
        row_tail='\r\n'
        if opts['dexp_rowsp']=='rowsp13': 
                row_tail='\n'
        elif opts['dexp_rowsp']=='rowsp10': 
                row_tail='\r'
        row_fmt=opts['dexp_t_row']
        has_alia=("%(Device_Alias)" in row_fmt) 
        has_state=("%(State)" in row_fmt)
        has_verify=("%(Verify)" in row_fmt)
        has_workcode=("%(WorkCode)" in row_fmt)
        has_reserved=("%(Reserved)" in row_fmt)
        if has_state: has_state=getTransState("c_state_", opts)
        if has_verify: has_verify=getTransState("c_verify_", opts)
        if has_workcode: has_workcode=getTransWC("c_wc_", opts)
        if has_reserved: has_reserved=getTransWC("c_rs_", opts)
        f=file(fn, "a+b")
        try:
                if head: f.write(head+row_tail)
                for r in emps:
                        appendDevFields(r,'SN_id',has_alia)
                        appendTimeFields(r, "TTime_", r['TTime'])
                        e=Employee.objByID(r['UserID_id'])
                        r['PIN']=e.PIN
                        r['Employee_Name']=e.EName
                        r['TTime']=("%s"%r['TTime'])[:19]
                        transKey(r, 'State', has_state)
                        transKey(r, 'Verify', has_verify)
                        transKey(r, 'WorkCode', has_workcode)
                        transKey(r, 'Reserved', has_reserved)
                        for c in r: 
                                if r[c]==None: r[c]=""
                        s=(row_fmt%r)+row_tail
                        f.write(s.encode('utf-8'))
                if tail: f.write(tail+row_tail)
        finally:
                f.close()

def doEmpExport(opts, maxRow=10000, **filter):
        fn=opts['dexp_e_fn']
        if filter:
                rows=Employee.objects.filter(filter)
        else:
                rows=Employee.objects.all()
        if "%(Device_" in fn: #文件名中包括设备
                devices=rows.values("SN").distinct()
                for sn in devices:
                        dev=get_device(sn['SN'])
                        fnFields={'Device_SN': sn['SN'], 'Device_Alias': dev and dev.Alias or None}
                        appendTimeFields(fnFields, '', datetime.datetime.now())
                        fnsn=opts['dexp_path']+(fn%fnFields)
                        data=rows.filter(SN=dev)[:maxRow].values('EName','PIN','AccGroup','Card','Password', 'SN')
                        if len(data)>0:
                                doEmpExportData(opts, data, fnsn)
                        else:
                                print "No data for", dev
        else:
                fnFields={}
                appendTimeFields(fnFields, '', datetime.datetime.now())
                fnsn=opts['dexp_path']+(fn%fnFields)
                rows=rows[:maxRow].values('EName','PIN','AccGroup','Card','Password', 'SN')
                if len(rows)>0:
                        doEmpExportData(opts, rows, fnsn)

def doTransExport(opts, maxRow=10000, **filter):        
        fn=opts['dexp_t_fn']
        if filter:
                rows=Transaction.objects.filter(filter)
        else:
                rows=Transaction.objects.all()[:10]
        if "%(Device_" in fn: #文件名中包括设备
                devices=rows.values("SN").distinct()
                for sn in devices:
                        dev=get_device(sn['SN'])
                        fnFields={'Device_SN': sn['SN'], 'Device_Alias': dev and dev.Alias or None}
                        appendTimeFields(fnFields, '', datetime.datetime.now())
                        fnsn=opts['dexp_path']+(fn%fnFields)
                        data=rows.filter(SN=dev)[:maxRow].values()
                        if len(data)>0:
                                doTransExportData(opts, data, fnsn)
                        else:
                                print "No data for", dev
        else:
                fnFields={}
                appendTimeFields(fnFields, '', datetime.datetime.now())
                fnsn=opts['dexp_path']+(fn%fnFields)
                rows=rows[:maxRow].values()
                if len(rows)>0:
                        doTransExportData(opts, rows, fnsn)

def try_sql(cursor, sqls):
        try:
                cursor.execute('\n'.jion(sqls))
        except:
                print "run sql single line"
                for s in sqls[1:-1]:
                        try:
                                cursor.execute(s)
                        except Exception, e:
                                print "ERROR SQL:", s, e
        return
                        
def doEmpDB(cursor, opts, maxRow=10000, **filter):
        sqls=[]
        if filter:
                rows=Employee.objects.filter(filter)
        else:
                rows=Employee.objects.all()
        rows=rows[:maxRow].values('EName','PIN','AccGroup','Card','Password', 'SN')
        if len(rows)<=0: return
        tail=opts['dexp_db_sql_tail']
        head=opts['dexp_db_sql_head']
        row_tail='\n'
        row_fmt=opts['dexp_db_sql_user']
        has_alia=("%(Device_Alias)" in row_fmt) 
        sqls.append(head)
        for r in rows:
                appendDevFields(r, 'SN', has_alia)
                for c in r: 
                        if r[c]==None: r[c]=""
                s=(row_fmt%r)
                sqls.append(s)
        sqls.append(tail)
        try_sql(cursor, sqls)

def searchUserID(cursor, pin, cache, emp_search_sql):
        if pin in cache: return cache[pin]
        cursor.execute(emp_search_sql, [pin])
        try:
                r=cursor.fetchone()
                id=r[0]
                cache[pin]=id
                return id
        except Exception, e:
                print e
                return 0
        
def doTransDB(cursor, opts, maxRow=10000, **filter):
        sqls=[]
        if filter:
                rows=Transaction.objects.filter(filter)
        else:
                rows=Transaction.objects.all()[:10]
        rows=rows[:maxRow].values()
        if len(rows)<=0: return
        tail=opts['dexp_db_sql_tail']
        head=opts['dexp_db_sql_head']
        row_tail='\n'
        row_fmt=opts['dexp_db_sql_trans']
        has_alia=("%(Device_Alias)" in row_fmt) 
        has_alia=("%(Device_Alias)" in row_fmt) 
        has_state=("%(State)" in row_fmt)
        has_verify=("%(Verify)" in row_fmt)
        has_workcode=("%(WorkCode)" in row_fmt)
        has_reserved=("%(Reserved)" in row_fmt)
        has_userid=("%(Employee_ID)" in row_fmt)
        if has_userid:
                userid_cache={}
                emp_search_sql=opts['emp_search_sql']
        if has_state: has_state=getTransState("c_state_", opts)
        if has_verify: has_verify=getTransState("c_verify_", opts)
        if has_workcode: has_workcode=getTransWC("c_wc_", opts)
        if has_reserved: has_reserved=getTransWC("c_rs_", opts)
        sqls.append(head)
        for r in rows:
                appendDevFields(r,'SN_id',has_alia)
                appendTimeFields(r, "TTime_", r['TTime'])
                e=Employee.objByID(r['UserID_id'])
                r['PIN']=e.PIN
                r['Employee_Name']=e.EName
                r['TTime']=("%s"%r['TTime'])[:19]
                transKey(r, 'State', has_state)
                transKey(r, 'Verify', has_verify)
                transKey(r, 'WorkCode', has_workcode)
                transKey(r, 'Reserved', has_reserved)
                if has_userid:
                        r['Employee_ID']=searchUserID(cursor, r['PIN'], userid_cache, emp_search_sql)
                for c in r: 
                        if r[c]==None: r[c]=""
                s=(row_fmt%r)
                sqls.append(s)
        sqls.append(tail)
        try_sql(cursor, sqls)
                        
def data_exp_def(request):
        if request.method=="POST":
#                conn, cursor=getNewCursor(request.POST)
#        doEmpDB(cursor, request.POST, 10000)
#                doTransDB(cursor, request.POST, 10000)
#                conn.close()
#                print request.POST
                import os
                try:
                        os.makedirs(request.POST['dexp_path'])
                except: pass
                doEmpExport(request.POST, 10000)
                doTransExport(request.POST, 10000)
                        
        return render_to_response("data_exp_def.html", RequestContext(request,{
                "title": _(u"自动导出数据格式定义"),
                "attstates": ATTSTATES,
                "verifies": VERIFYS,
                "workcode_count": 20*[1],
                "reserved_count": 20*[1],
                }))

@login_required
def index(request, pageName):
        if(pageName=="data_exp_def"): return data_exp_def(request)
