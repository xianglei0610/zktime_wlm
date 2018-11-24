# coding=utf-8
from django.conf import settings
import datetime
from django.db import  IntegrityError
from mysite.iclock.models.model_trans import Transaction

from commen_utils import server_time_delta, normal_state, normal_verify

def line_to_log(device, line, event=True):
    '''
    解析 Stamp 的行数据
    '''
    flds = line.split("\t") + ["", "", "", "", "", "", "",""]

    #检查员工号码的合法性
    pin = flds[0]   #---第一个元素为人员编号
    try:
        if pin in settings.DISABLED_PINS:  return None
    except:
        return None
    if flds[5] == '255' and flds[3] == '3' and flds[0] == flds[4]:
        print u"Swiped a invalid card: \n", line
        return None
    from db_utils import get_employee 
    emp = get_employee(pin, device)
    if not emp:
        return None
    if emp.IsNewEmp:
        emp.DeptID_id=1
        emp.attarea=(device.area,)  #---更新考勤区域
        emp.save()
    pin = emp.id

    try:
        logtime = datetime.datetime.strptime(flds[1], "%Y-%m-%d %H:%M:%S")  #---第二个元素为打卡时间
    except:
        return None
    now=datetime.datetime.now()
    
    #---检查考勤记录时间的合法性
    if event:
        if (now + datetime.timedelta(1, 0, 0)) < logtime: 
            print u"时间比当前时间还要多一天"
            return None
        if logtime<now-datetime.timedelta(days=settings.VALID_DAYS): 
            print u"时间比当前要早...天", settings.VALID_DAYS
            return None

    if settings.CHECK_DUPLICATE_LOG or (not event): #检查重复记录
        try:
            if Transaction.objects.filter(TTime=logtime, UserID=emp): 
                print u"该记录已经存在"
                return None
        except: pass
 
    #根据考勤机的时区矫正考勤记录的时区，使之同服务器的时区保持一致
    if device.tz_adj <> None:
        count_minutes = None
        if abs(device.tz_adj)<=13:
            count_minutes = device.tz_adj*3600
        else:
            count_minutes = device.tz_adj*60
        logtime = logtime - datetime.timedelta(0, count_minutes) + server_time_delta() #UTC TIM
                
    sql = (pin, logtime, normal_state(flds[2]), normal_verify(flds[3]), None, flds[4], flds[5],device.sn)
    return sql


def commit_log_(cursor, sql, cnn):
     #----------打开记录插入语句  
    from mysite.iclock.sql import commit_log_sql
    sql_exc=commit_log_sql() 
#    log_statement="""insert into %s (userid, checktime, checktype, verifycode, SN, WorkCode, Reserved,sn_name) \
#    values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#    log_statement_postgresql="""insert into %s (userid, checktime, checktype, verifycode, "SN", "WorkCode", "Reserved",sn_name) \
#    values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#    sql_exc=""
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql_exc=log_statement_postgresql
#    else:
#        sql_exc=log_statement
    
    if type(sql)==type([]):
        """sqls="; ".join([log_statement%data for data in sql])
        try:
            cursor.execute("begin; "+sqls+"; end")
        except:
            print_exc()"""
        
        for data in sql: #sqlite3 数据库需要单次执行以减少 “Database is locked 错误”
            try:
                cursor.execute(sql_exc, data)
                cnn._commit()
            except IntegrityError:
                raise IntegrityError
                pass
            except:
                import traceback;traceback.print_exc()

    elif type(sql)==type((0,)):
        cursor.execute(sql_exc, sql)
    else:
        cursor.execute(sql)
    if cnn: cnn._commit()


def commit_log(cursor, sql, cnn):
    try:
        commit_log_(cursor, sql, cnn)
    except IntegrityError:
        raise IntegrityError
    except:
        import traceback;traceback.print_exc()
        print "try again"
        cnn._rollback()
        cnn.close()
        cursor=cnn.cursor()
        commit_log(cursor, sql, cnn)
    return cursor