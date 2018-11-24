#coding:utf-8
from django.conf import settings
import datetime
from mysite import sql_utils

def get_temp_flex_id_sql(emp,d1,d2):
    '''
             得到临时班次数据中的弹性时段类型ID
    '''
#     sql = '''select t.id
#     from user_temp_sch as t,schclass as s
#     where t.UserID=%s and t.SchClassID = s.SchclassID and (t.LeaveTime>'%s' and t.ComeTime<'%s') and t.SchClassID=1 
#     order by t.ComeTime 
#     '''%(emp,start_date,end_date)
    params={}
    id_part={}
    params={'emp':emp,'start_date':d1,'end_date':d2}
    sql=sql_utils.get_sql('sql','get_temp_flex_id_sql','att',params=params,id_part=id_part)
    return sql
    
 
def get_emp_run_time_temp_sql(emp,d1,d2):
    '''
           返回时间段数据 ([上班时间，下班时间，ID，开始签到，结束签到，开始签退，结束签退, 覆盖类型])
    '''
#    sql = '''
#    select t.ComeTime,t.LeaveTime,t.Flag,t.SchClassID,s.CheckInTime1, s.CheckInTime2,s.CheckOutTime1,s.CheckOutTime2,t.WorkType,t.id
#    from user_temp_sch as t,schclass as s
#    where t.UserID=%s and t.SchClassID = s.SchclassID and (t.LeaveTime>'%s' and t.ComeTime<'%s') 
#    order by t.ComeTime 
#    '''%(emp,start_date,end_date)
    params={}
    id_part={}
    params={'emp':emp,'start_date':d1,'end_date':d2}
    sql=sql_utils.get_sql('sql','get_emp_run_time_temp_sql','att',params=params,id_part=id_part)
    return sql 

def get_emp_run_sql(emp,d1,d2):
    '''
          功能: 获取人员在某期间的排班
    '''
#    sql = '''
#    select UserID,StartDate,EndDate,NUM_OF_RUN_ID,id
#    from user_of_run 
#    where UserID=%s and (enddate>'%s' and startdate<'%s') 
#    order by user_of_run.StartDate 
#    '''%(emp,start_date,end_date)
    params={}
    id_part={}
    params={'emp':emp,'start_date':d1,'end_date':d2}
    sql=sql_utils.get_sql('sql','get_emp_run_sql','att',params=params,id_part=id_part)
    return sql

def get_emp_num_run_sql():
    '''
           获取所有班次
    '''
#    sql = '''
#    select Num_runID,Units,Cyle from num_run
#    '''
    params={}
    id_part={}
    sql=sql_utils.get_sql('sql','get_emp_num_run_sql','att',params=params,id_part=id_part)
    return sql

def get_run_detail_sql(num_run_ID):
    '''
          功能: 获取某个班次的班次详细
    '''
#    sql = '''
#    select d.StartTime,d.EndTime,d.Sdays,d.SchclassID,s.CheckInTime1, s.CheckInTime2,s.CheckOutTime1,s.CheckOutTime2
#    from num_run_deil as d,schclass as s
#    where num_runid = %s and d.SchclassID = s.SchclassID
#    order by d.Sdays,d.StartTime
#    '''%num_run_ID
    params={}
    id_part={}
    params={'num_run_ID':num_run_ID}
    sql=sql_utils.get_sql('sql','get_run_detail_sql','att',params=params,id_part=params)
    return sql

def get_holiday_sql():
    '''
          功能: 获取节假日
    '''
#    sql = '''
#    select HolidayID,StartTime,Duration from holidays
#    order by StartTime
#    '''
    params={}
    id_part={}
    sql=sql_utils.get_sql('sql','get_holiday_sql','att',params=params,id_part=id_part)
    return sql

def get_askleave_sql(emp,d1,d2):
    '''
          功能: 获取人员在某期间的审核通过的请假
    '''
#    sql = '''
#    select id,StartSpecDay,EndSpecDay from user_speday 
#    where State=1 and UserID=%s and (EndSpecDay>'%s' and StartSpecDay<'%s')
#    order by StartSpecDay
#    '''%(emp,start_date,end_date)
    params={}
    id_part={}
    params={'emp':emp,'start_date':d1,'end_date':d2}
    sql=sql_utils.get_sql('sql','get_askleave_sql','att',params=params,id_part=id_part)
    return sql

def get_setleave_sql(emp,d1,d2):
    '''
          功能: 获取人员在某期间的调休里的休息类型
          返回:  ((id, datetime.date(2011, 6, 1), datetime.date(2012, 10, 1), 22),)
    '''
#    sql = '''
#    select id,starttime,endtime from setuseratt
#    where UserID_id = %s and atttype=2 and (endtime>'%s' and starttime<'%s')
#    order by starttime
#    '''%(emp,start_date,end_date)
    params={}
    id_part={}
    params={'emp':emp,'start_date':d1,'end_date':d2}
    sql=sql_utils.get_sql('sql','get_setleave_sql','att',params=params,id_part=id_part)
    return sql

def get_initial_record_sql(emp,d1,d2):
    '''
          功能: 获取人员某期间的原始签卡记录
    '''
#    sql = '''
#    select id,userid, checktime, checktype, 0 as counter 
#    from checkinout 
#    where userid=%s and checktime>='%s' and checktime<='%s' 
#    order by checktime
#    '''%(emp,start_date,end_date)
    params={}
    id_part={}
    params={'emp':emp,'start_date':d1,'end_date':d2}
    sql=sql_utils.get_sql('sql','get_initial_record_sql','att',params=params,id_part=id_part)
    return sql

def savespecialday_sql(i,st,et,reson, at,dateid,clearance):
    if settings.DATABASE_ENGINE == 'oracle':
        sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,"DATE",DateID,clearance,State) 
        values('%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', 
        to_date('%s','YYYY-MM-DD HH24:MI:SS'),'%s','%s','0')
        """ % (USER_SPEDAY._meta.db_table, int(i),st,et,reson, at,dateid,clearance)
    else:
        sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,Date,DateID,clearance,State) 
        values('%s', '%s', '%s', '%s','%s','%s','%s','0')
        """ % (USER_SPEDAY._meta.db_table, int(i), st, et,reson, at,dateid,clearance)
    return sql

def savespecialday_sql2(st,et,reson,at,dateid,clearance,id):
    if settings.DATABASE_ENGINE == 'oracle':
        sql="""update %s set StartSpecDay=to_date('%s','YYYY-MM-DD HH24:MI:SS'),
        EndSpecDay=to_date('%s','YYYY-MM-DD HH24:MI:SS'),YUANYING='%s',
        "DATE"=to_date('%s','YYYY-MM-DD HH24:MI:SS'),DateID='%s',clearance='%s' where id=%s
        """%(USER_SPEDAY._meta.db_table,st,et,reson,at,dateid,clearance,id)
    else:
        sql="""update %s set StartSpecDay='%s',EndSpecDay='%s',YUANYING='%s',Date='%s',DateID='%s',clearance='%s' where id=%s
        """%(USER_SPEDAY._meta.db_table,st,et,reson,at,dateid,clearance,id)
    return sql

def applySpecialday_sql(id,st,et,reson, at,dateid):
    if settings.DATABASE_ENGINE == 'oracle':
        sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,"DATE",DateID,State) 
        values('%s',  to_date('%s','YYYY-MM-DD HH24:MI:SS'), 
        to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'),'%s','0')
        """ % (USER_SPEDAY._meta.db_table, int(id),st,et,reson, at,dateid)

    else:
        sql="""insert into %s (UserID, StartSpecDay, EndSpecDay, YUANYING,Date,DateID,State) 
        values('%s', '%s', '%s', '%s','%s','%s','0')
        """ % (USER_SPEDAY._meta.db_table, int(id), st, et,reson, at,dateid)
    return sql

def saveFingerprint_update_sql(tmps,userid,fids):    
    sql="""update template set template = '%s', utime='%s' where userid='%s' and fingerid=%s
    """ % (tmps, str(datetime.datetime.now())[:19], userid, int(fids)-1)
    return sql
    
def saveFingerprint_insert_sql(tmps,userid,fids):        
    sql="""insert into template(template, userid, fingerid,  utime, valid, DelTag) values('%s', '%s', %s, '%s', 1, '0')
    """ % (tmps, userid, int(fids)-1, str(datetime.datetime.now())[:19])
    return sql

def saveCheckForget_sql(i,nt,ct, reson, first_name,time):
    from mysite.iclock.models.model_trans import Transaction
    from mysite.att.models.checkexact_model import CheckExact
    if settings.DATABASE_ENGINE == 'oracle':
        sql_log="""insert into %s (UserID, CHECKTIME, CHECKTYPE, YUYIN,MODIFYBY,"DATE") 
        values('%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s', '%s', '%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'))
        """ % (CheckExact._meta.db_table, int(i), nt,ct, reson, first_name,time)
        sql="""insert into %s (userid, checktime, checktype,verifycode) values('%s', to_date('%s','YYYY-MM-DD HH24:MI:SS'), '%s',5)
        """ % (Transaction._meta.db_table, int(i), nt, ct)
    #                        print sql_log,sql
    else:
        sql_log="""insert into %s (UserID, CHECKTIME, CHECKTYPE, YUYIN,MODIFYBY,DATE) 
        values('%s', '%s', '%s', '%s', '%s', '%s')""" % (CheckExact._meta.db_table, int(i), nt,ct, reson, first_name,time)
        sql="""insert into %s (userid, checktime, checktype,verifycode) values('%s', '%s', '%s',5)
        """ % (Transaction._meta.db_table, int(i), nt, ct)
    return sql_log,sql

def auditedTrans_sql(rk,id):
    from mysite.iclock.models.model_trans import Transaction
    sql="update %s set Reserved2='%s' where id=%s "%(Transaction._meta.db_table,rk,id)
    return sql

def deleteLeaveClass_sql(id):
    sql="delete from %s where LeaveId=%s"%(LeaveClass._meta.db_table, id)
    return sql

def deleteCalcLog_sql(Type,deptid,userid):
    sql="""delete from attcalclog where """
    if Type==-1:
            sql=sql+"Type>%s"%(Type)
    else:
            sql=sql+"Type=%s"%(Type)
    if deptid>0:
            sql=sql+" and deptid=%s"%(deptid)
    if userid>0:
            sql=sql+" and userid=%s"%(userid)
    return sql

def SaveLeaveClass_sql(dbTable, s,t):
    sql="update %s set %s where LeaveId=%s"%(dbTable, s,t)
    return sql

def yc_calculate_sql1(deptids,st,et,userids):
    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":                        
        sql="""
            select count(*) from (
           select row_number() over( order by  a.attdate,u.defaultdeptid,a.userid ) as 'row',
           a.userid,
           (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
           (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
           u.badgenumber,u.[name],convert(nvarchar(10),a.attdate,120) as attdate,sum(a.worktime) as 'worktime'
           
            from attshifts a,userinfo u
           where a.userid=u.userid and (starttime is null or endtime is null or worktime<480) %(where)s 
           group by a.attdate,u.defaultdeptid,a.userid,u.badgenumber,u.[name]
           ) bb
         
        """
        if deptids:
            sql=sql%({'where':" and u.defaultdeptid in (%s)  and a.attdate between '%s' and '%s' "%(deptids,st,et)})
        else:
            sql=sql%({'where':" and a.userid in (%s)  and a.attdate between '%s' and '%s' "%(userids,st,et)}) 
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
        sql="""
            select count(*) from (
            select '',
            a.userid,
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
            (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
            u.badgenumber,
            u.name,date(attdate) as attdate,
            sum(a.worktime) as 'worktime'
            
            from attshifts a,userinfo u
            where a.userid=u.userid and ( a.late>0 or a.early>0 or a.absent>0) %(where)s
            group by a.attdate,u.defaultdeptid,a.userid,u.badgenumber,u.name
            ) bb
            
        """
        if deptids:
            sql=sql%({'where':" and u.defaultdeptid in (%s)  and a.attdate >= '%s' and a.attdate<='%s' "%(deptids,st,et)})
        else:
            sql=sql%({'where':" and a.userid in (%s)  and a.attdate >= '%s' and a.attdate<='%s' "%(userids,st,et)})
    else:
        sql="""
            select count(*) from(
            select row_number() over( order by  defaultdeptid,userid,att_date ) as row_no,
            userid, name, badgenumber,att_date, 
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=v.defaultdeptid)) as super_dept,
            (select deptname from departments where deptid=v.defaultdeptid ) as dept_name,
            sum(worktime) as work_time
            
            from 
            (select u.userid, defaultdeptid, name, badgenumber,attdate,worktime,to_char(attdate,'YYYY-MM-DD') as att_date from userinfo u, attshifts a where u.userid=a.userid and ( a.late>0 or a.early>0 or a.absent>0)%(where)s)v
            group by userid, att_date, defaultdeptid, name, badgenumber
            order by userid, att_date)
            
        """
        if deptids:
            sql=sql%({'where':" and u.defaultdeptid in (%s)  and to_char(attdate,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(deptids,st,et)})
        else:
            sql=sql%({'where':" and a.userid in (%s)  and to_char(attdate,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(userids,st,et)})    
    return sql

def yc_calculate_sql2(totalall,result,deptids,st,et,userids,offset,limit):
    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":        
        sql="""
            select * from (
           select row_number() over( order by  a.attdate,u.defaultdeptid,a.userid ) as 'row',
           a.userid,
           (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
           (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
           u.badgenumber,u.[name],convert(nvarchar(10),a.attdate,120) as attdate,
            sum(a.late) as late,
            sum(a.early) as early,
            sum(a.absent) as absent,
           (select count(*) from attshifts a2 where  late >0  and a2.attdate = a.attdate and a2.userid = a.userid)as late_times,
           (select count(*) from attshifts a3 where  early >0  and a3.attdate = a.attdate and a3.userid = a.userid) as early_times,
           (select count(*) from attshifts a4 where  absent>0 and a4.attdate = a.attdate and a4.userid = a.userid) as absent_times,                               
           
           sum(a.worktime) as 'worktime',
           (SELECT checktime 
                                       FROM ( 
                                           SELECT 
                                              right(convert(nvarchar(20),checktime,120),8) + ',' 
                                           FROM (
                                               SELECT  checktime 
                                               FROM attrecabnormite t
                                               where t.attdate=a.attdate and t.userid=a.userid
                                           ) AS SUM_COL 
                                           FOR XML PATH('') 
                                       )as card_times(checktime)
                                   ) as card_times
            from attshifts a,userinfo u
           where a.userid=u.userid and ( a.late>0 or a.early>0 or a.absent>0) %(where)s
           group by a.attdate,u.defaultdeptid,a.userid,u.badgenumber,u.[name]
           ) bb
         %(row)s
        """
        where={'row':'','where':''}
        if not totalall:
            where['row']=" where row between %s and %s"%(result,offset*limit)
        if deptids:
                 
            where['where']=" and u.defaultdeptid in (%s)  and a.attdate between '%s' and '%s' "%(deptids,st,et)
        else:
            where['where']=" and a.userid in (%s)  and a.attdate between '%s' and '%s' "%(userids,st,et)
        sql=sql%where
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
        sql="""
            select '',
            a.userid,
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
            (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
            u.badgenumber,
            u.name,
            date(a.attdate) as attdate,
            sum(a.late) as late,
            sum(a.early) as early,
            sum(a.absent) as absent,
           (select count(*) from attshifts a2 where  late >0  and a2.attdate = a.attdate and a2.userid = a.userid)as late_times,
           (select count(*) from attshifts a3 where  early >0  and a3.attdate = a.attdate and a3.userid = a.userid) as early_times,
           (select count(*) from attshifts a4 where  absent>0 and a4.attdate = a.attdate and a4.userid = a.userid) as absent_times,                               
            sum(a.worktime) as worktime,
            (select group_concat(time(checktime) order by checktime SEPARATOR ',')  from attrecabnormite t  where date(a.attdate)=t.AttDate and  t.userid=a.userid) as card_times
            
            from attshifts a,userinfo u
            where a.userid=u.userid and ( a.late>0 or a.early>0 or a.absent>0) %(where)s
            group by a.userid,date(a.attdate) 
            order by dept_name,a.userid,a.attdate
            %(row)s
            
        """
        where={'row':'','where':''}
        if deptids:
           where['where']=" and u.defaultdeptid in (%s)  and a.attdate >= '%s' and a.attdate<='%s' "%(deptids,st,et)
        else:
           where['where']=" and a.userid in (%s)  and a.attdate >= '%s' and a.attdate<='%s' "%(userids,st,et) 
        if not totalall:
            where['row']=" limit %s,%s"%((offset-1)*limit,offset*limit)
        sql=sql%where
    else:
        sql="""
            select * from(
            select row_number() over( order by  defaultdeptid,userid,att_date ) as row_no,
            userid,
             (select deptname from departments where deptid=(select supdeptid from departments where deptid=v.defaultdeptid)) as super_dept,
             (select deptname from departments where deptid=v.defaultdeptid ) as dept_name,
             badgenumber,
             name,
            att_date, 
            sum(late)as late_minutes,
            sum(early)as early_minutes,
            sum(absent) as absent_days,
            (select count(*) from attshifts a2 where late>0 and a2.attdate=v.attdate and a2.userid = v.userid) as late_times,
            (select count(*) from attshifts a3 where early>0 and a3.attdate=v.attdate and a3.userid = v.userid) as early_times,
            (select count(*) from attshifts a4 where absent>0 and a4.attdate=v.attdate and a4.userid = v.userid) as absent_times,
            sum(worktime) as work_time,
            (select wmsys.wm_concat(to_char(checktime,'HH24:Mi:SS')) from attrecabnormite t where t.attdate=v.attdate and t.userid=v.userid) as card_times
            
            from 
            (select u.userid, defaultdeptid, name, badgenumber,late,early,absent,attdate,worktime,to_char(attdate,'YYYY-MM-DD') as att_date from userinfo u, attshifts a where u.userid=a.userid and ( a.late>0 or a.early>0 or a.absent>0)%(where)s )v
            group by userid, att_date, defaultdeptid, name, badgenumber,attdate
            order by userid, att_date)
            %(row_no)s
            
        """
        where={'row_no':'','where':''}
        if deptids:
           where['where']=" and u.defaultdeptid in (%s)  and to_char(attdate,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(deptids,st,et)
        else:
           where['where']=" and a.userid in (%s)  and to_char(attdate,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(userids,st,et) 
        if not totalall:
            where['row_no']=" where row_no between %s and %s"%(result,offset*limit)
        sql=sql%where
    return sql 

def cardtime_calculate_sql1(deptids,st,et,userids):
    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":            
        sql="""
            select count(*) from (
            select row_number() over( order by  u.defaultdeptid,a.userid,convert(nvarchar(10),a.checktime,120) ) as 'row',
            a.userid,
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
            (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
            u.badgenumber,u.[name],convert(nvarchar(10),a.checktime,120) as date
            from userinfo u ,checkinout a
            where u.userid=a.userid  %(where)s
            group by u.defaultdeptid,a.userid,convert(nvarchar(10),a.checktime,120),u.badgenumber,u.[name]
            ) bb

         
        """
        if deptids:
            sql=sql%({'where':" and u.defaultdeptid in (%s)  and a.checktime between '%s' and '%s' "%(deptids,st,et)})
        else:
            sql=sql%({'where':" and a.userid in (%s)  and a.checktime between '%s' and '%s' "%(userids,st,et)})
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
        sql="""
            select count(*) from (
            select '',
            a.userid,
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
            (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
            u.badgenumber,u.name,date(checktime) as date
            from userinfo u ,checkinout a
            where u.userid=a.userid %(where)s
            group by u.defaultdeptid,a.userid,date(a.checktime),u.badgenumber,u.name
            ) bb
            
        """
        if deptids:
            sql=sql%({'where':" and u.defaultdeptid in (%s)  and a.checktime >= '%s' and a.checktime<='%s' "%(deptids,st,et)})
        else:
            sql=sql%({'where':" and a.userid in (%s)  and a.checktime >= '%s' and a.checktime<='%s' "%(userids,st,et)})
    else:
        sql="""
            select count(*) from(
            select row_number() over( order by  defaultdeptid,userid,check_date ) as row_no,
            userid, name, badgenumber,check_date, 
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=v.defaultdeptid)) as super_dept,
            (select deptname from departments where deptid=v.defaultdeptid ) as dept_name,
            count(checktime) as check_times,
            wmsys.wm_concat(to_char(checktime,'HH24:Mi:SS')) as card_times
            from 
            (select u.userid, defaultdeptid, name, badgenumber,checktime,to_char(checktime,'YYYY-MM-DD') as check_date from userinfo u, checkinout c where u.userid=c.userid  %(where)s) v
            group by userid, check_date, defaultdeptid, name, badgenumber
            order by userid, check_date)
            
        """
        if deptids:
            sql=sql%({'where':" and u.defaultdeptid in (%s)  and to_char(checktime,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(deptids,st,et)})
        else:
            sql=sql%({'where':" and c.userid in (%s)  and to_char(checktime,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(userids,st,et)})
    return sql

def cardtime_calculate_sql2(totalall,result,deptids,st,et,userids,offset,limit):
    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":
        sql="""
            select * from (
            select row_number() over( order by  u.defaultdeptid,a.userid,convert(nvarchar(10),a.checktime,120) ) as 'row',
            a.userid,
            (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
            (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
            u.badgenumber,u.[name],convert(nvarchar(10),a.checktime,120) as date,
            
            count(*) as times,
            (SELECT checktime 
                FROM ( 
                    SELECT 
                       right(convert(nvarchar(20),checktime,120),8) + ',' 
                    FROM (
                        SELECT  checktime 
                        FROM checkinout t
                        where convert(nvarchar(10),t.checktime,120)=convert(nvarchar(10),a.checktime,120) and t.userid=a.userid
                        
                    ) AS SUM_COL 
                    FOR XML PATH('') 
                )as card_times(checktime)
            ) as card_times

            from userinfo u ,checkinout a
            where u.userid=a.userid  %(where)s
            group by u.defaultdeptid,a.userid,convert(nvarchar(10),a.checktime,120),u.badgenumber,u.[name]
            ) bb
            
         %(row)s
        
        order by dept_name,userid,date
        """
        where={'row':'','where':''}
        if not totalall:
            where['row']=" where row between %s and %s"%(result,offset*limit)
        if deptids:
                 
            where['where']=" and u.defaultdeptid in (%s)  and a.checktime between '%s' and '%s' "%(deptids,st,et)
        else:
            where['where']=" and a.userid in (%s)  and a.checktime between '%s' and '%s' "%(userids,st,et)
        sql=sql%where
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
        sql="""
             select '',
             a.userid,
             (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
             (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
             u.badgenumber,
             u.name, 
             date(checktime) as date,             
             count(checktime) as times,
             group_concat(time(checktime) order by checktime SEPARATOR ',') as card_times
            
             from userinfo u ,checkinout a
             where u.userid=a.userid  %(where)s
             group by a.userid  ,date(a.checktime)         
             order by dept_name,a.userid,a.checktime
             %(row)s
             
        """
        where={'row':'','where':''}
        if deptids:
           where['where']=" and u.defaultdeptid in (%s)  and a.checktime >= '%s' and a.checktime<='%s' "%(deptids,st,et)
        else:
           where['where']=" and a.userid in (%s)  and a.checktime >= '%s' and a.checktime <= '%s' "%(userids,st,et) 
        if not totalall:
            where['row']=" limit %s,%s"%((offset-1)*limit,offset*limit)
        sql=sql%where
    else:
        sql="""
            select * from (
             select row_number() over( order by  defaultdeptid,userid,"date" ) as row_no,
             userid,
             (select deptname from departments where deptid=(select supdeptid from departments where deptid=v.defaultdeptid)) as super_dept,
             (select deptname from departments where deptid=v.defaultdeptid ) as deptname,
             badgenumber,                         
             name,
             "date", 
             count(checktime) as times,
             wmsys.wm_concat(to_char(checktime,'HH24:Mi:SS')) as card_times
             from 
             (select u.userid, defaultdeptid, name, badgenumber,checktime,to_char(checktime,'YYYY-MM-DD') as "date" from userinfo u, checkinout c where u.userid=c.userid %(where)s ) v
             group by userid, "date", defaultdeptid, name, badgenumber
             order by userid, "date" )
            %(row_no)s 
        """
        where={'row_no':'','where':''}
        if deptids:
           where['where']=" and u.defaultdeptid in (%s)  and to_char(checktime,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(deptids,st,et)
        else:
           where['where']=" and c.userid in (%s)  and to_char(checktime,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(userids,st,et) 
        if not totalall:
            where['row_no']=" where row_no between %s and %s"%(result,offset*limit)
        sql=sql%where
    return sql
                
    
    
    
    
    
    
    
    
    
    
    




 