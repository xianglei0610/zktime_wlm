#coding=utf-8

from django.conf import settings
from mysite import sql_utils

def attShifts_report_sql(uid,d1,d2):
    '''
    考勤明细表
    '''
    params={"uid":uid,"d1":d1,"d2":d2}
    id_part={}
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
#        sql=sql+""" a.AttDate>=to_date('%s','YYYY-MM-DD HH24:MI:SS') and a.AttDate<=to_date('%s','YYYY-MM-DD HH24:MI:SS') and"""%(d1,d2)
        id_part["sqlengine"]="oracleengine"
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql=sql+""" a."AttDate">='%s' and a."AttDate"<='%s' and"""%(d1,d2)
        id_part["sqlengine"]="pgengine"
    else:
#        sql=sql+""" a.AttDate>='%s' and a.AttDate<='%s' and"""%(d1,d2)
        id_part["sqlengine"]="otherengine"
#    sql=sql+""" a.userid in (%s) order by userinfo.badgenumber,userinfo.defaultdeptid"""%(uid)
    sql=sql_utils.get_sql('sql',sqlid='attShifts_report_sql',app='att',params=params,id_part=id_part)
    return sql
#    sql="""  select 
#                        departments.code,departments.DeptName,userinfo.badgenumber,userinfo.name,
#                        a.AttDate as AttDate,schclass.SchName,
#                        a.ClockInTime as ClockInTime,
#                        a.ClockOutTime as ClockOutTime,
#                        a.StartTime as StartTime,
#                        a.EndTime as EndTime,
#                        a.WorkDay,a.RealWorkDay,a.MustIn,a.MustOut,a.NoIn,a.NoOut,a.Late,a.Early,a.AbsentR,a.WorkTime,
#                        a.Exception,
#                        a.OverTime_des,a.WorkMins,a.SSpeDayNormal,a.SSpeDayWeekend,a.SSpeDayHoliday,a.AttTime,
#                        a.SSpeDayNormalOT,a.SSpeDayWeekendOT,a.SSpeDayHolidayOT,a.userid
#                     from attshifts as a
#                        left join userinfo  on userinfo.userid=a.userid 
#                        left join departments  on userinfo.defaultdeptid=departments.DeptID 
#                        left join schclass on schclass.SchclassID = a.SchId where 
#                    """
#    sql="""    select 
#                        departments.code,departments."DeptName",userinfo.badgenumber,userinfo.name,
#                        a."AttDate" as AttDate,schclass."SchName",
#                        a."ClockInTime" as ClockInTime,
#                        a."ClockOutTime" as ClockOutTime,
#                        a."StartTime" as StartTime,
#                        a."EndTime" as EndTime,
#                        a."WorkDay",a."RealWorkDay",a."MustIn",a."MustOut",a."NoIn",a."NoOut",a."Late",a."Early",a."AbsentR",a."WorkTime",
#                        a."Exception",
#                        a."OverTime_des",a."WorkMins",a."SSpeDayNormal",a."SSpeDayWeekend",a."SSpeDayHoliday",a."AttTime",
#                        a."SSpeDayNormalOT",a."SSpeDayWeekendOT",a."SSpeDayHolidayOT",a.userid
#                     from attshifts as a
#                        left join userinfo  on userinfo.userid=a.userid 
#                        left join departments  on userinfo.defaultdeptid=departments."DeptID" 
#                        left join schclass on schclass."SchclassID" = a."SchId"
#                     where
#    """    


def get_tjjgxq_report_sql(userids,d1,d2):
    '''
    统计结果详情表
    '''
    params={"userids":userids,"st":d1,"et":d2}
#    id_part={"where":["date","uids"]}
    sql=sql_utils.get_sql('sql',sqlid='get_tjjgxq_report_sqla',app='att',params=params)
    return sql  
#    sql="""SELECT
#                userinfo.badgenumber,
#                userinfo.name,
#                attrecabnormite.checktime,
#                attrecabnormite.CheckType,
#                attrecabnormite.NewType
#                FROM attrecabnormite ,userinfo
#                where attrecabnormite.userid = userinfo.userid  and """        
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
#        sql=sql+""" attrecabnormite.AttDate>=to_date('%s','YYYY-MM-DD HH24:MI:SS') and attrecabnormite.AttDate<=to_date('%s','YYYY-MM-DD HH24:MI:SS') and"""%(d1,d2)
#    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql=sql+""" attrecabnormite."AttDate">='%s' and attrecabnormite."AttDate"<='%s' and"""%(d1,d2)
#    else:
#        sql=sql+""" attrecabnormite.AttDate>='%s' and attrecabnormite.AttDate<='%s' and"""%(d1,d2)
#    sql=sql+""" attrecabnormite.userid in (%s) order by userinfo.badgenumber,userinfo.defaultdeptid"""%(uid)
  

def get_yc_report_sql(userids,deptids,st,et):
    '''
    考勤异常明细表sql
    '''
    id_part={}
    params={"userids":userids,"deptids":deptids,"st":st,"et":et,"row_no":''}
    if deptids:
        id_part["where"]="hasdeptids"
    else:
        id_part["where"]="nodeptids"
    sql=sql_utils.get_sql('sql',sqlid='get_yc_report_sql',app='att',params=params,id_part=id_part)
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":        
#        sql="""
#            select * from (
#           select row_number() over( order by  a.attdate,u.defaultdeptid,a.userid ) as 'row',
#           a.userid,
#           (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
#           (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
#           u.badgenumber,u.[name],convert(nvarchar(10),a.attdate,120) as attdate,
#            sum(a.late) as late,
#            sum(a.early) as early,
#            sum(a.absent) as absent,
#           (select count(*) from attshifts a2 where  late >0  and a2.attdate = a.attdate and a2.userid = a.userid)as late_times,
#           (select count(*) from attshifts a3 where  early >0  and a3.attdate = a.attdate and a3.userid = a.userid) as early_times,
#           (select count(*) from attshifts a4 where  absent>0 and a4.attdate = a.attdate and a4.userid = a.userid) as absent_times,                               
#           
#           sum(a.worktime) as 'worktime',
#           (SELECT checktime 
#                                       FROM ( 
#                                           SELECT 
#                                              right(convert(nvarchar(20),checktime,120),8) + ',' 
#                                           FROM (
#                                               SELECT  checktime 
#                                               FROM attrecabnormite t
#                                               where t.attdate=a.attdate and t.userid=a.userid
#                                           ) AS SUM_COL 
#                                           FOR XML PATH('') 
#                                       )as card_times(checktime)
#                                   ) as card_times
#            from attshifts a,userinfo u
#           where a.userid=u.userid and ( a.late>0 or a.early>0 or a.absent>0) %(where)s
#           group by a.attdate,u.defaultdeptid,a.userid,u.badgenumber,u.[name]
#           ) bb
#         %(row)s
#        """
#        where={'row':'','where':''}
#        if deptids:
#            where['where']=" and u.defaultdeptid in (%s)  and a.attdate between '%s' and '%s' "%(deptids,st,et)
#        else:
#            where['where']=" and a.userid in (%s)  and a.attdate between '%s' and '%s' "%(userids,st,et)
#        sql=sql%where
#    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
#        sql="""
#            select '',
#            a.userid,
#            (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
#            (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
#            u.badgenumber,
#            u.name,
#            date(a.attdate) as attdate,
#            sum(a.late) as late,
#            sum(a.early) as early,
#            sum(a.absent) as absent,
#           (select count(*) from attshifts a2 where  late >0  and a2.attdate = a.attdate and a2.userid = a.userid)as late_times,
#           (select count(*) from attshifts a3 where  early >0  and a3.attdate = a.attdate and a3.userid = a.userid) as early_times,
#           (select count(*) from attshifts a4 where  absent>0 and a4.attdate = a.attdate and a4.userid = a.userid) as absent_times,                               
#            sum(a.worktime) as worktime,
#            (select group_concat(time(checktime) order by checktime SEPARATOR ',')  from attrecabnormite t  where date(a.attdate)=t.AttDate and  t.userid=a.userid) as card_times
#            
#            from attshifts a,userinfo u
#            where a.userid=u.userid and ( a.late>0 or a.early>0 or a.absent>0) %(where)s
#            group by a.userid,date(a.attdate) 
#            order by dept_name,a.userid,a.attdate
#            %(row)s
#            
#        """
#        where={'row':'','where':''}
#        if deptids:
#           where['where']=" and u.defaultdeptid in (%s)  and a.attdate >= '%s' and a.attdate<='%s' "%(deptids,st,et)
#        else:
#           where['where']=" and a.userid in (%s)  and a.attdate >= '%s' and a.attdate<='%s' "%(userids,st,et) 
#        sql=sql%where
#    else:
#        sql="""
#            select * from(
#            select row_number() over( order by  defaultdeptid,userid,att_date ) as row_no,
#            userid,
#             (select deptname from departments where deptid=(select supdeptid from departments where deptid=v.defaultdeptid)) as super_dept,
#             (select deptname from departments where deptid=v.defaultdeptid ) as dept_name,
#             badgenumber,
#             name,
#            att_date, 
#            sum(late)as late_minutes,
#            sum(early)as early_minutes,
#            sum(absent) as absent_days,
#            (select count(*) from attshifts a2 where late>0 and a2.attdate=v.attdate and a2.userid = v.userid) as late_times,
#            (select count(*) from attshifts a3 where early>0 and a3.attdate=v.attdate and a3.userid = v.userid) as early_times,
#            (select count(*) from attshifts a4 where absent>0 and a4.attdate=v.attdate and a4.userid = v.userid) as absent_times,
#            sum(worktime) as work_time,
#            (select wmsys.wm_concat(to_char(checktime,'HH24:Mi:SS')) from attrecabnormite t where t.attdate=v.attdate and t.userid=v.userid) as card_times
#            
#            from 
#            (select u.userid, defaultdeptid, name, badgenumber,late,early,absent,attdate,worktime,to_char(attdate,'YYYY-MM-DD') as att_date 
#            from userinfo u, attshifts a where u.userid=a.userid and ( a.late>0 or a.early>0 or a.absent>0)%(where)s )v
#            group by userid, att_date, defaultdeptid, name, badgenumber,attdate
#            order by userid, att_date)
#            %(row_no)s
#            
#        """
#        where={'row_no':'','where':''}
#        if deptids:
#           where['where']=" and u.defaultdeptid in (%s)  and to_char(attdate,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(deptids,st,et)
#        else:
#           where['where']=" and a.userid in (%s)  and to_char(attdate,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(userids,st,et) 
#        sql=sql%where
    

def get_cardtimes_report_sql(userids,deptids,st,et):
    '''
    打卡详情表sql
    '''
    params={"userids":userids,"deptids":deptids,"st":st,"et":et,"row_no":''}
    id_part={}
    if deptids:
        id_part["where"]="hasdeptids"
    else:
        id_part["where"]="nodeptids"
    sql=sql_utils.get_sql('sql',sqlid='get_cardtimes_report_sql',app='att',params=params,id_part=id_part)   
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":
#                sql="""
#                    select * from (
#                    select row_number() over( order by  u.defaultdeptid,a.userid,convert(nvarchar(10),a.checktime,120) ) as 'row',
#                    a.userid,
#                    (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
#                    (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
#                    u.badgenumber,u.[name],convert(nvarchar(10),a.checktime,120) as date,
#                    
#                    count(*) as times,
#                    (SELECT checktime 
#                        FROM ( 
#                            SELECT 
#                               right(convert(nvarchar(20),checktime,120),8) + ',' 
#                            FROM (
#                                SELECT  checktime 
#                                FROM checkinout t
#                                where convert(nvarchar(10),t.checktime,120)=convert(nvarchar(10),a.checktime,120) and t.userid=a.userid
#                                
#                            ) AS SUM_COL 
#                            FOR XML PATH('') 
#                        )as card_times(checktime)
#                    ) as card_times
#    
#                    from userinfo u ,checkinout a
#                    where u.userid=a.userid  %(where)s
#                    group by u.defaultdeptid,a.userid,convert(nvarchar(10),a.checktime,120),u.badgenumber,u.[name]
#                    ) bb
#                    
#                 %(row)s
#                
#                order by dept_name,userid,date
#                """
#                where={'row':'','where':''}
#                if deptids:
#                    where['where']=" and u.defaultdeptid in (%s)  and a.checktime between '%s' and '%s' "%(deptids,st,et)
#                else:
#                    where['where']=" and a.userid in (%s)  and a.checktime between '%s' and '%s' "%(userids,st,et)
#                sql=sql%where
#    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
#                sql="""
#                     select '',
#                     a.userid,
#                     (select deptname from departments where deptid=(select supdeptid from departments where deptid=u.defaultdeptid)) as 'super_dept',
#                     (select deptname from departments where deptid=u.defaultdeptid )as 'dept_name',
#                     u.badgenumber,
#                     u.name, 
#                     date(checktime) as date,             
#                     count(checktime) as times,
#                     group_concat(time(checktime) order by checktime SEPARATOR ',') as card_times
#                    
#                     from userinfo u ,checkinout a
#                     where u.userid=a.userid  %(where)s
#                     group by a.userid  ,date(a.checktime)         
#                     order by dept_name,a.userid,a.checktime
#                     %(row)s
#                     
#                """
#                where={'row':'','where':''}
#                if deptids:
#                   where['where']=" and u.defaultdeptid in (%s)  and a.checktime >= '%s' and a.checktime<='%s' "%(deptids,st,et)
#                else:
#                   where['where']=" and a.userid in (%s)  and a.checktime >= '%s' and a.checktime <= '%s' "%(userids,st,et) 
#                sql=sql%where
#    else:
#                sql="""
#                    select * from (
#                     select row_number() over( order by  defaultdeptid,userid,"date" ) as row_no,
#                     userid,
#                     (select deptname from departments where deptid=(select supdeptid from departments where deptid=v.defaultdeptid)) as super_dept,
#                     (select deptname from departments where deptid=v.defaultdeptid ) as deptname,
#                     badgenumber,                         
#                     name,
#                     "date", 
#                     count(checktime) as times,
#                     wmsys.wm_concat(to_char(checktime,'HH24:Mi:SS')) as card_times
#                     from 
#                     (select u.userid, defaultdeptid, name, badgenumber,checktime,to_char(checktime,'YYYY-MM-DD') as "date" from userinfo u, checkinout c where u.userid=c.userid %(where)s ) v
#                     group by userid, "date", defaultdeptid, name, badgenumber
#                     order by userid, "date" )
#                    %(row_no)s 
#                """
#                where={'row_no':'','where':''}
#                if deptids:
#                   where['where']=" and u.defaultdeptid in (%s)  and to_char(checktime,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(deptids,st,et)
#                else:
#                   where['where']=" and c.userid in (%s)  and to_char(checktime,'YYYY-MM-DD HH24-Mi-SS') between '%s' and '%s' "%(userids,st,et) 
#                sql=sql%where
    

def get_calc_report_sql(userids,d1,d2):
    '''
    考勤汇总表/每日考勤统计表 sql
    '''
    params={"userids":userids,"st":d1,"et":d2}
#    id_part={"where":["date","uids"]}
    sql=sql_utils.get_sql('sql',sqlid='get_calc_report_sqla',app='att',params=params)
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
     