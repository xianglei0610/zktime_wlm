#coding:utf-8
from django.conf import settings
from mysite.iclock.iutils import userDeptList
from mysite import sql_utils

def get_default_PIN_sql():
#    sql = "select badgenumber from userinfo order by userid desc"
    params={}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='get_default_PIN_sql',app='personnel',params=params,id_part=id_part)
    return sql

def search_by_filter_sql(level_type,level_id):
#    if level_type == "openlevel_id": #门禁权限组
#        sql = "select userid from userinfo where userid not in (select u.userid from userinfo u,acc_levelset_emp a where u.userid = a.employee_id and a.acclevelset_id = '%s')"%level_id
#        return sql
#    elif level_type == "firstopen_level_id": #首卡开门权限组
#        sql = "select userid from userinfo where userid not in (select u.userid from userinfo u,acc_firstopen_emp a where u.userid = a.employee_id and a.accfirstopen_id = '%s')"%level_id
#    return sql
    params={}
    id_part={}
    params={"level_id":level_id}
    if level_type == "openlevel_id": #门禁权限组
        id_part["where"]="levelset"
    elif level_type == "firstopen_level_id": #首卡开门权限组
        id_part["where"]="firstopen"
    sql=sql_utils.get_sql('sql',sqlid='search_by_filter_sql',app='personnel',params=params,id_part=id_part)
    return sql

def search_accdev_byuser_sql(id):
#    sql = "select distinct device_id from acc_door where  id in (select accdoor_id from acc_levelset_door_group where acclevelset_id in (select acclevelset_id from acc_levelset_emp where employee_id = %s))" % id
    params={"id":id}
    id_part={}
    sql=sql_utils.get_sql('sql',sqlid='search_accdev_byuser_sql',app='personnel',params=params,id_part=id_part)
    return sql

def GenerateEmpFlow_sql(request,deptids,d1,d2):
    params={"deptids":deptids,"d1":d1,"d2":d2}
    id_part={}
    if deptids:
        id_part["where"]="hasdeptids"
    else:
        depts = userDeptList(request.user)
        if depts:
            params["depts"]=",".join([str(i.id) for i in depts])
            id_part["where"]="nodeptids"
    sql=sql_utils.get_sql('sql',sqlid='GenerateEmpFlow_sql',app='personnel',params=params,id_part=id_part)
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql='''select  a."DeptName",
#                              (select count(1) from userinfo where userinfo."Hiredday">='%s' and userinfo."Hiredday"<='%s'
#                               and userinfo.defaultdeptid = a."DeptID") newin,
#                              (select count(1) from personnel_empchange cc
#                                   where cc.changepostion =1 and cc.isvalid=True  and cc.newvalue = to_char(a."DeptID",'999999999999999')
#                                     and cc.changedate>='%s' and cc.changedate<='%s') transferin,
#                              (select count(1) from personnel_empchange dd
#                                   where dd.changepostion =1 and dd.isvalid=True  and dd.oldvalue = to_char(a."DeptID",'999999999999999')
#                                     and dd.changedate>='%s' and dd.changedate<='%s') transferout,
#                              ( select  count(1) from personnel_leavelog ea left join userinfo eb on ea."UserID_id" = eb.userid
#                                   where ea.leavetype =1 and eb.defaultdeptid = a."DeptID"
#                                     and ea.leavedate >='%s' and ea.leavedate<= '%s') selfleave ,
#                              ( select  count(1) from personnel_leavelog ea left join userinfo eb on ea."UserID_id" = eb.userid
#                                   where ea.leavetype =2 and eb.defaultdeptid = a."DeptID"
#                                     and ea.leavedate >='%s' and ea.leavedate<= '%s') passiveleave ,
#                              ( select  count(1) from personnel_leavelog ea left join userinfo eb on ea."UserID_id" = eb.userid
#                                   where ea.leavetype =3 and eb.defaultdeptid = a."DeptID"
#                                     and ea.leavedate >='%s' and ea.leavedate<= '%s') normalleave
#                     from departments a  where status=0 '''%(d1,d2,d1,d2,d1,d2,d1,d2,d1,d2,d1,d2)
#        
#    else:
#        sql='''select  a.DeptName,
#                      (select count(1) from userinfo where to_char(userinfo.Hiredday,'YYYY-MM-DD')>='%s' and to_char(userinfo.Hiredday,'YYYY-MM-DD')<='%s'
#                       and userinfo.defaultdeptid = a.DeptID) newin,
#                      (select count(1) from personnel_empchange cc
#                           where cc.changepostion ='1' and cc.isvalid='1'  and to_char(cc.newvalue) = a.DeptID
#                             and to_char(cc.changedate,'YYYY-MM-DD')>='%s' and to_char(cc.changedate,'YYYY-MM-DD')<='%s') transferin,
#                      (select count(1) from personnel_empchange dd
#                           where dd.changepostion ='1' and dd.isvalid='1'  and to_char(dd.oldvalue) = a.DeptID
#                             and to_char(dd.changedate,'YYYY-MM-DD')>='%s' and to_char(dd.changedate,'YYYY-MM-DD')<='%s') transferout,
#                      ( select  count(1) from personnel_leavelog ea left join userinfo eb on ea.UserID_id = eb.userid
#                           where ea.leavetype ='1' and eb.defaultdeptid = a.DeptID
#                             and to_char(ea.leavedate,'YYYY-MM-DD') >='%s' and to_char(ea.leavedate,'YYYY-MM-DD')<= '%s') selfleave ,
#                      ( select  count(1) from personnel_leavelog ea left join userinfo eb on ea.UserID_id = eb.userid
#                           where ea.leavetype ='2' and eb.defaultdeptid = a.DeptID
#                             and to_char(ea.leavedate,'YYYY-MM-DD') >='%s' and to_char(ea.leavedate,'YYYY-MM-DD')<= '%s') passiveleave ,
#                      ( select  count(1) from personnel_leavelog ea left join userinfo eb on ea.UserID_id = eb.userid
#                           where ea.leavetype ='3' and eb.defaultdeptid = a.DeptID
#                             and to_char(ea.leavedate,'YYYY-MM-DD') >='%s' and to_char(ea.leavedate,'YYYY-MM-DD')<= '%s') normalleave
#             from departments a  where status=0 '''%(d1,d2,d1,d2,d1,d2,d1,d2,d1,d2,d1,d2)
#    if deptids:
#        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#            sql = sql + """ and  a."DeptID" in (%s)"""%deptids
#        else:
#            sql = sql + " and  a.DeptID in (%s)"%deptids
#    else:
#        depts = userDeptList(request.user)
#        if depts:
#            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#                sql = sql + """ and a."DeptID" in (%s)"""%",".join([str(i.id) for i in depts ])
#            else:
#                sql = sql + " and a.DeptID in (%s)"%",".join([str(i.id) for i in depts ])
    

def GenerateDeptRoster_sql(request,deptids):
    params={"deptids":deptids}
    id_part={}
    if deptids:
        id_part["where"]="hasdeptids"
    else:
        depts = userDeptList(request.user)    
        if depts:
            params["depts"]=",".join([str(i.id) for i in depts])
            id_part["where"]="nodeptids"
    sql=sql_utils.get_sql('sql',sqlid='GenerateDeptRoster_sql',app='personnel',params=params,id_part=id_part)
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql ="""
#           select a.badgenumber,a.name,c."DeptName",( select b.name from personnel_positions b where a.position_id =b.id )position,a.pager,a."Birthday",
#           a.birthplace,
#          (select b.name from personnel_education b where a.education_id =b.id )  education
#           from userinfo a left join departments c on a.defaultdeptid=c."DeptID" where a.status=0
#        """
#    else:
#        sql ="""
#           select a.badgenumber,a.name,c.DeptName,( select b.name from personnel_positions b where a.position_id =b.id )position,a.pager,a.Birthday,
#           a.birthplace,
#          ( select b.name from personnel_education b where a.education_id =b.id )  education
#           from userinfo a left join departments c on a.defaultdeptid=c.DeptID where a.status=0
#        """
#    if deptids:
#        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#            sql = sql + " and a.defaultdeptid in (%s)"%deptids 
#        else:
#            sql = sql + " and a.defaultdeptid in (%s)"%deptids 
#    else:
#         depts = userDeptList(request.user)
#         if depts:
#            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#                sql = sql + " and  a.defaultdeptid in (%s)"%",".join([str(i.id) for i in depts ])
#            else:
#                sql = sql + " and  a.defaultdeptid in (%s)"%",".join([str(i.id) for i in depts ])
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql = sql +"  order by a.defaultdeptid,a.badgenumber "
#    else:
#        sql = sql +"  order by a.defaultdeptid,a.badgenumber "
#    return sql
    
    

def GenerateEmpEducation_sql(request,deptids):
    params={"deptids":deptids}
    id_part={}
    if deptids:
        id_part["where"]="hasdeptids"
    else:
        depts = userDeptList(request.user)    
        if depts:
            params["depts"]=",".join([str(i.id) for i in depts])
            id_part["where"]="nodeptids"
    sql=sql_utils.get_sql('sql',sqlid='GenerateEmpEducation_sql',app='personnel',params=params,id_part=id_part)
    return sql
#    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#        sql ='''
#        select a."DeptName" ,
#                       (select count(1)  from userinfo where "education_id" =1 and userinfo.defaultdeptid = a."DeptID" ) pupil,
#                       (select count(1)  from userinfo where "education_id" =2 and userinfo.defaultdeptid = a."DeptID" ) middle_studemt,
#                       (select count(1)  from userinfo where "education_id" =3 and userinfo.defaultdeptid = a."DeptID" ) high_studemt,
#                       (select count(1)  from userinfo where "education_id" =8 and userinfo.defaultdeptid = a."DeptID" ) university_studemt,
#                       (select count(1)  from userinfo where "education_id" =9 and userinfo.defaultdeptid = a."DeptID" ) graduate_studemt,
#                       (select count(1)  from userinfo where "education_id" =10 and userinfo.defaultdeptid = a."DeptID" ) doctor
#         from departments a where status=0 
#        '''
#    else:
#        sql ='''
#        select a.DeptName ,
#                       (select count(1)  from userinfo where education_id =1 and userinfo.defaultdeptid = a.DeptID ) pupil,
#                       (select count(1)  from userinfo where education_id =2 and userinfo.defaultdeptid = a.DeptID ) middle_studemt,
#                       (select count(1)  from userinfo where education_id =3 and userinfo.defaultdeptid = a.DeptID ) high_studemt,
#                       (select count(1)  from userinfo where education_id =8 and userinfo.defaultdeptid = a.DeptID ) university_studemt,
#                       (select count(1)  from userinfo where education_id =9 and userinfo.defaultdeptid = a.DeptID ) graduate_studemt,
#                       (select count(1)  from userinfo where education_id =10 and userinfo.defaultdeptid = a.DeptID ) doctor
#         from departments a where status=0 
#        '''
#        
#    if deptids:
#        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#            sql = sql + """ and a."DeptID" in (%s)"""%deptids 
#        else:
#            sql = sql + " and a.DeptID in (%s)"%deptids 
#    else:
#        depts = userDeptList(request.user)
#        if depts:
#            if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
#                sql = sql + """ and a."DeptID" in (%s)"""%",".join([str(i.id) for i in depts ])
#            else:
#                sql = sql + " and a.DeptID in (%s)"%",".join([str(i.id) for i in depts ])
#    return sql
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    