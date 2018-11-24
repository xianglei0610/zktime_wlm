#coding:utf-8
from django.conf import settings
import datetime
from mysite.att.models import attCalcLog
from mysite.att.models.num_run_deil import  NUM_RUN_DEIL
from mysite import sql_utils
from mysite.iclock.models.model_trans import Transaction

def CalcReportItem_sql(d1,d2,uid):
    params={"d1":d1,"d2":d2,"uid":uid}
    id_part={}
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
        id_part["where"]="oracleengine"
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
        id_part["where"]="pgengine"
    else:
        id_part["where"]="otherengine"
    sql=sql_utils.get_sql('sql',sqlid='CalcReportItem_sql',app='iclock',params=params,id_part=id_part)
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql="""select s.userid as userid,u.badgenumber as pin,u.name as name,u."SSN" as ssn,s."SchId" as schid,s."AttDate" as attdate,d."DeptName" as deptname,s."ClockInTime" as clockintime,s."ClockOutTime" as clockouttime,
#                s."StartTime" as starttime,s."EndTime" as endtime,s."WorkDay" as workday,s."RealWorkDay" as realworkday,s."NoIn" as noin,s."NoOut" as noout,
#                s."Early" as early,s."Late" as late,s."Absent" as absent,s."AbsentR" as absentr,s."OverTime" as overtime,s."ExceptionID" as exceptionid,s."MustIn" as mustin,s."MustOut" as mustout,  
#                s."WorkTime" as worktime,s."AttTime" as atttime,s."WorkMins" as workmins,s."SSpeDayNormal" as SSpeDayNormal,s."SSpeDayWeekend" as SSpeDayWeekend,s."SSpeDayHoliday" as SSpeDayHoliday ,s."Symbol" as symbol,
#                s."SSpeDayNormalOT" as SSpeDayNormalOT,s."SSpeDayWeekendOT" as SSpeDayWeekendOT,s."SSpeDayHolidayOT" as SSpeDayHolidayOT
#                from attshifts s,userinfo u,Departments d where u.userid=s.userid and d."DeptID"=u.defaultdeptid and  """
#    else:
#        sql="""select s.userid as userid,u.badgenumber as pin,u.name as name,u.ssn as ssn,s.schid as schid,s.attdate as attdate,d.deptname as deptname,s.clockInTime as clockintime,s.clockouttime as clockouttime,
#                s.starttime as starttime,s.endtime as endtime,s.workday as workday,s.realworkday as realworkday,s.noin as noin,s.noout as noout,
#                s.early as early,s.late as late,s.absent as absent,s.absentr as absentr,s.overtime as overtime,s.exceptionid as exceptionid,s.mustin as mustin,s.mustout as mustout,  
#                s.worktime as worktime,s.atttime as atttime,s.workmins as workmins,s.SSpeDayNormal as SSpeDayNormal,s.SSpeDayWeekend as SSpeDayWeekend,s.SSpeDayHoliday as SSpeDayHoliday ,s.symbol as symbol,
#                s.SSpeDayNormalOT as SSpeDayNormalOT,s.SSpeDayWeekendOT as SSpeDayWeekendOT,s.SSpeDayHolidayOT as SSpeDayHolidayOT
#                from attshifts s,userinfo u,Departments d where u.userid=s.userid and d.deptID=u.defaultdeptid and  """
#        
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
#        sql=sql+""" s.attdate>=to_date('%s','YYYY-MM-DD HH24:MI:SS') and s.attdate<=to_date('%s','YYYY-MM-DD HH24:MI:SS') and"""%(d1,d2)
#    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql=sql+""" s."AttDate">='%s' and s."AttDate"<='%s' and"""%(d1,d2)
#    else:
#        sql=sql+""" s.attdate>='%s' and s.attdate<='%s' and"""%(d1,d2)
#    sql=sql+""" s.userid = %s order by u.badgenumber,u.defaultdeptid"""%(uid)
#    return sql

def PrepareCalcDate_sql(StartDate,EndDate,nt,u,itype):
    params={"attc":attCalcLog._meta.db_table,"u":u,"StartDate":StartDate,"ed1":EndDate-datetime.timedelta(1),"EndDate":EndDate,"nti":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"itype":itype}
    id_part={}
    if StartDate<EndDate and EndDate==nt:
        id_part["where"]="timedel"
#        sql="""insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)
#        """%(attCalcLog._meta.db_table, u,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
    elif StartDate<=EndDate and EndDate!=nt:
        id_part["where"]="timenow"
#        sql="""insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)
#        """%(attCalcLog._meta.db_table, u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
#    sql="insert into %s(userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s',%s)"%(attCalcLog._meta.db_table, u,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
    sql=sql_utils.get_sql('sql',sqlid='PrepareCalcDate_sql',app='iclock',params=params,id_part=id_part)
    return sql

def PrepareCalcDateByDept_sql(deptid,StartDate,EndDate,nt,itype):
    params={"attc":attCalcLog._meta.db_table,"deptid":deptid,"StartDate":StartDate,"ed1":EndDate-datetime.timedelta(1),"EndDate":EndDate,"nti":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"itype":itype}
    id_part={}
    if StartDate<EndDate and EndDate==nt:
        id_part["where"]="timedel"
    elif StartDate<=EndDate and EndDate!=nt:
        id_part["where"]="timenow"
    sql=sql_utils.get_sql('sql',sqlid='PrepareCalcDateByDept_sql',app='iclock',params=params,id_part=id_part)
    return sql
#    if StartDate<EndDate and EndDate==nt:
#        sql="""insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)
#        """%(attCalcLog._meta.db_table, deptid,0,StartDate,EndDate-datetime.timedelta(1),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
#    elif StartDate<=EndDate and EndDate!=nt:
#        sql="""insert into %s(deptid,userid,startdate,enddate,opertime,type) values('%s','%s','%s','%s','%s',%s)
#        """%(attCalcLog._meta.db_table, deptid,0,StartDate,EndDate,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),itype)
#    return sql

def SaveLeaveClass_sql(dbTable, s,t):
#    sql="update %s set %s where LeaveId=%s"%(dbTable, s,t)
    params={"dbTable":dbTable,"s":s,"t":t}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='SaveLeaveClass_sql',app='iclock',params=params,id_part=id_part)
    return sql

def ClearTableData_sql(Condition,TableName):
    params={"Condition":Condition,"TableName":TableName}
    id_part={}
    if Condition!='':
        id_part["where"]="hascon"
#        sql='delete from %s where (%s)'%(TableName,Condition)
    else:
        id_part["where"]="nocon"
#        sql='delete from %s'%(TableName)
    sql=sql_utils.get_sql('sql',sqlid='ClearTableData_sql',app='iclock',params=params,id_part=id_part)
    return sql

def MainCalc_sql1(db_table,u,StartDate,EndDate):
    params={"db_table":db_table,"u":u,"StartDate":StartDate.strftime('%Y-%m-%d %H:%M:%S'),"EndDate":EndDate.strftime('%Y-%m-%d %H:%M:%S')}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='MainCalc_sql1',app='iclock',params=params,id_part=id_part)
    return sql
#    sql="""delete from %s where userid=%s and attdate>='%s' and attdate<='%s'
#    """%(db_table,u,StartDate.strftime('%Y-%m-%d %H:%M:%S'),EndDate.strftime('%Y-%m-%d %H:%M:%S'))
#    return sql

def MainCalc_sql2(db_table,u,StartDate,EndDate):
    params={"db_table":db_table,"u":u,"StartDate":StartDate.strftime('%Y-%m-%d %H:%M:%S'),"EndDate":EndDate.strftime('%Y-%m-%d %H:%M:%S')}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='MainCalc_sql2',app='iclock',params=params,id_part=id_part)
    return sql

def MainCalc_sql3(db_table,u,StartDate,EndDate):
    params={"db_table":db_table,"u":u,"StartDate":StartDate.strftime('%Y-%m-%d %H:%M:%S'),"EndDate":EndDate.strftime('%Y-%m-%d %H:%M:%S')}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='MainCalc_sql3',app='iclock',params=params,id_part=id_part)
    return sql

def deleteShiftTime_sql(sd,ed,st,et,shift_id):
    params={"db_table":NUM_RUN_DEIL._meta.db_table,"sd":sd,"ed":ed,"st":st,"et":et,"shift_id":shift_id}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='deleteShiftTime_sql',app='iclock',params=params,id_part=id_part)
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
#        sql="""delete from %s where sdays=%s and edays=%s and to_char(starttime, 'HH24:Mi:SS')>='%s' and 
#        to_char(endtime, 'HH24:Mi:SS')<='%s' and num_runid=%s
#        """%(NUM_RUN_DEIL._meta.db_table,sd,ed,st,et,shift_id)
#    else:
#        sql="""delete from %s where sdays=%s and edays=%s and starttime>='%s' and endtime<='%s' and num_runid=%s
#        """%(NUM_RUN_DEIL._meta.db_table,sd,ed,st,et,shift_id)
#    return sql

def deleteShiftDetail_sql(SchID):
    params={"db_table":NUM_RUN_DEIL._meta.db_table,"SchID":SchID}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='deleteShiftDetail_sql',app='iclock',params=params,id_part=id_part)
    return sql
#    sql='delete from %s where Num_runID=%s'%(NUM_RUN_DEIL._meta.db_table,SchID)
#    return sql

def SaveTempSch_sql(userid,st,et):
    from mysite.att.models.user_temp_sch import USER_TEMP_SCH
    params={"db_table":USER_TEMP_SCH._meta.db_table,"userid":userid,"st":st,"et":et+datetime.timedelta(days=1)}
    sql=sql_utils.get_sql('sql',sqlid='SaveTempSch_sql',app='iclock',params=params,id_part=id_part)
    return sql
#    sql="""delete from %s where userid=%s and leavetime>='%s' and cometime<'%s' and cometime>='%s'
#    """%(USER_TEMP_SCH._meta.db_table,userid,st,et+datetime.timedelta(days=1),st)
#    return sql

def SaveSchPlan_sql1(userid):
    from mysite.att.models.userusedsclasses import UserUsedSClasses
    params={"db_table":UserUsedSClasses._meta.db_tabl,"userid":userid}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='SaveSchPlan_sql1',app='iclock',params=params,id_part=id_part)
    return sql
#    sql="delete from %s where userid=%s"%(UserUsedSClasses._meta.db_table,userid)
#    return sql

def SaveSchPlan_sql2(userid,st,et):
    from mysite.att.models.user_of_run import USER_OF_RUN
    params={"db_table":USER_OF_RUN._meta.db_table,"userid":userid,"st":st.strftime("%Y-%m-%d"),"et":et.strftime("%Y-%m-%d")}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='SaveSchPlan_sql2',app='iclock',params=params,id_part=id_part)
    return sql
#    sql="""delete from %s where userid=%s and StartDate='%s' and EndDate='%s'
#    """%(USER_OF_RUN._meta.db_table,userid,st.strftime("%Y-%m-%d"),et.strftime("%Y-%m-%d"))
#    return sql

def commit_log_sql():
    from mysite.iclock.models.model_trans import Transaction
    params={"db_table":Transaction._meta.db_table}
    id_part={}
    sql_exc=sql_utils.get_sql('sql',sqlid='commit_log_sql',app='iclock',params=params,id_part=id_part)
    return sql_exc
#    log_statement="""insert into %s (userid, checktime, checktype, verifycode, SN, WorkCode, Reserved,sn_name) \
#    values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#    log_statement_postgresql="""insert into %s (userid, checktime, checktype, verifycode, "SN", "WorkCode", "Reserved",sn_name) \
#    values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql_exc=log_statement_postgresql
#    else:
#        sql_exc=log_statement
#    return sql_exc

def OpUploadAttLog_sql():
#    MYSQL_INSERT = u'''INSERT INTO checkinout(userid,checktime,checktype,verifycode,workcode)
#    VALUES %(batch_rows)s'''
#    SQLSERVER_INSERT = u'''INSERT INTO checkinout(userid,checktime,checktype,verifycode,workcode)
#    VALUES('%(uid)s','%(time)s','%(type)s','%(vf)s','%(wc)s')'''
    params={}
    id_part={}
    sql_insert=sql_utils.get_sql('sql',sqlid='OpUploadAttLog_sql',app='iclock',params=params,id_part=id_part)
    return sql_insert


def cache_utils_insert_sql(record_dict):
    params={"sn_id":record_dict["sn_id"],"cmdoperate_id":record_dict["cmdoperate_id"],"cmdcontent":record_dict["cmdcontent"],"cmdcommittime":record_dict["cmdcommittime"],
            "cmdtranstime":record_dict["cmdtranstime"],"cmdovertime":record_dict["cmdovertime"],"cmdreturn":record_dict["cmdreturn"],
            "cmdreturncontent":record_dict["cmdreturncontent"],"cmdimmediately":record_dict["cmdimmediately"]}
    id_part={}
    INSERT_SQL=sql_utils.get_sql('sql',sqlid='cache_utils_insert_sql',app='iclock',params=params,id_part=id_part)
    return INSERT_SQL
 

def cache_utils_delete_sql(ids):
    params={"ids":ids}
    id_part={}
    DELETE_SQL=sql_utils.get_sql('sql',sqlid='cache_utils_delete_sql',app='iclock',params=params,id_part=id_part)
    return DELETE_SQL
#    DELETE_SQL=u'''
#        DELETE FROM devcmds WHERE id in 
#        (%s)
#    '''
#    return DELETE_SQL

def cache_utils_update_sql(record_dict):
    params={"id":record_dict["id"],"sn_id":record_dict["sn_id"],"cmdoperate_id":record_dict["cmdoperate_id"],"cmdcontent":record_dict["cmdcontent"],"cmdcommittime":record_dict["cmdcommittime"],
            "cmdtranstime":record_dict["cmdtranstime"],"cmdovertime":record_dict["cmdovertime"],"cmdreturn":record_dict["cmdreturn"],
            "cmdreturncontent":record_dict["cmdreturncontent"],"cmdimmediately":record_dict["cmdimmediately"]}
    id_part={}
    UPDATE_SQL=sql_utils.get_sql('sql',sqlid='cache_utils_update_sql',app='iclock',params=params,id_part=id_part)
#    UPDATE_SQL=u'%s'%(sql_utils.get_sql('sql',sqlid='cache_utils_update_sql',app='iclock',params=params,id_part=id_part))
    return UPDATE_SQL
#    UPDATE_SQL = u'''
#        UPDATE  devcmds SET SN_id =%(sn_id)s ,CmdOperate_id =%(cmdoperate_id)s ,CmdContent = %(cmdcontent)s ,
#            CmdCommitTime =%(cmdcommittime)s ,CmdTransTime =%(cmdtranstime)s ,CmdOverTime = %(cmdovertime)s,
#            CmdReturn = %(cmdreturn)s,CmdReturnContent = %(cmdreturncontent)s,CmdImmediately = %(cmdimmediately)s,
#            status ='0' 
#        WHERE id = %(id)s
#    '''
#    POSTGRE_UPDATE_SQL=u'''
#    UPDATE  devcmds SET "SN_id" =%(sn_id)s ,"CmdOperate_id" =%(cmdoperate_id)s ,"CmdContent" = %(cmdcontent)s ,
#    "CmdCommitTime" =%(cmdcommittime)s ,"CmdTransTime" =%(cmdtranstime)s ,"CmdOverTime" = %(cmdovertime)s,
#    "CmdReturn" = %(cmdreturn)s,"CmdReturnContent" = %(cmdreturncontent)s,"CmdImmediately" = %(cmdimmediately)s,
#    status ='0' 
#    WHERE id = %(id)s
#'''

def devview_log_sql():
    
    params={"db_table":Transaction._meta.db_table}
    id_part={}
    log_statement=sql_utils.get_sql('sql',sqlid='devview_log_sql',app='iclock',params=params,id_part=id_part)  
    return log_statement
#    log_statement="""insert into %s (userid, checktime, checktype, verifycode, SN, WorkCode, Reserved,sn_name) \
#    values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#    
#    log_statement_postgresql="""insert into %s (userid, checktime, checktype, verifycode, "SN", "WorkCode", "Reserved",sn_name) \
#    values(%%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s)""" % Transaction._meta.db_table
#    return log_statement,log_statement_postgresql

def update_device_sql_sql(sql,sn):
    params={"sql":sql,"sn":sn}
    id_part={}
    tsql=sql_utils.get_sql('sql',sqlid='update_device_sql_sql',app='iclock',params=params,id_part=id_part)
#    tsql="update iclock set %s where sn='%s'"%(sql,sn)
    return tsql



