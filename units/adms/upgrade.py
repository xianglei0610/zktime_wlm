#!/usr/bin/python
# -*- coding: utf-8 -*-

#此文件用于同步数据库信息，主要包含在软件中修改的一些字段定义以及新增约束
#每次发布若数据库有变动或做升级包时需更新此文件
from base.backup import get_attsite_file
from base.options import AppOption
import os
from django.utils.translation import ugettext_lazy as _
from traceback import print_exc
from mysite import settings
import subprocess
import logging

#引进 django 环境
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
from django.db import connection,connections#引入数据库的2个操作函数
import dict4ini
import datetime
from base.crypt import decryption, encryption

def get_attsite_file():
    current_path = settings.APP_HOME
    attsite=dict4ini.DictIni(current_path+"/attsite.ini")
    return attsite

#更新数据库部分的代码在此方法中实现
def sync_db():
    try:
        backup_db()
    except:
        print_exc()
        pass
    os.system("python manage.pyc syncdb")
    conn = connections['default']
    cursor = conn.cursor()
    db_dict = get_attsite_file()["DATABASE"]
    database_engine = db_dict["ENGINE"]
    
    try:
        if database_engine == 'sqlserver_ado':
#            print 'sqlserver_ado'
            sql="alter table Departments alter COLUMN  code nvarchar(100)"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table Departments alter COLUMN DeptName nvarchar(100)"
            cursor.execute(sql)
            conn._commit()            
            
            sql="alter table personnel_empchange alter column newvalue nvarchar(MAX)"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table personnel_empchange alter column oldvalue nvarchar(MAX)"
            cursor.execute(sql)
            conn._commit()            
#            
            sql="alter table checkinout alter column checktype nvarchar(5)"
            cursor.execute(sql)
            conn._commit()

            sql="alter table userinfo alter column street  nvarchar(100)"
            cursor.execute(sql)
            conn._commit()

            sql="alter table userinfo alter column cuser1  nvarchar(100)"
            cursor.execute(sql)
            conn._commit()

            sql="alter table userinfo alter column cuser2  nvarchar(100)"
            cursor.execute(sql)
            conn._commit()
            
            sql = "select length from syscolumns where id=object_id('userinfo') and name='password';"
            cursor.execute(sql)
            qets = cursor.fetchall()
            if qets and qets[0][0] == 16:#判断password长度，如果是8则未加过密
                sql="alter table userinfo alter column Password nvarchar(16)"
                cursor.execute(sql)
                conn._commit()
                
                sql="alter table acc_door alter column force_pwd  nvarchar(18)"
                cursor.execute(sql)
                conn._commit()

                sql="alter table acc_door alter column supper_pwd  nvarchar(18)"
                cursor.execute(sql)
                conn._commit()

                sql="alter table iclock alter column comm_pwd  nvarchar(32)"
                cursor.execute(sql)
                conn._commit()   
                process_pwd()
            print 'sqlserver_ado'
            print 'create tmp table and copy data'
            sql='SELECT DISTINCT log_tag,time,pin,card_no,device_id,device_sn,device_name, door_id, door_name, in_address,out_address,verified,state,event_type,trigger_opt \
                 INTO acc_monitor_log_tmp1 FROM acc_monitor_log'
            cursor = connection.cursor()
            cursor.execute(sql)
            connection._commit()
            
            print 'TRUNCATE TABLE acc_monitor_log'
            sql='TRUNCATE TABLE acc_monitor_log'
            cursor.execute(sql)
            connection._commit()
            
            try:
                sql = 'update acc_monitor_log_tmp1 set out_address=-1 where out_address is null'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            try:
                print 'alter table acc_monitor_log add constraint tri_def default -1 for trigger_opt'
                sql='alter table acc_monitor_log add constraint tri_def default -1 for trigger_opt'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            try:
                print 'alter table acc_monitor_log add constraint in_address_def default -1 for in_address'
                sql='alter table acc_monitor_log add constraint in_address_def default -1 for in_address'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            try:
                print 'ALTER TABLE acc_monitor_log ADD CONSTRAINT time_pin UNIQUE (TIME, pin,card_no,device_id,door_id,in_address,out_address,verified,state,event_type,trigger_opt)'
                sql='ALTER TABLE acc_monitor_log ADD CONSTRAINT time_pin UNIQUE (TIME, pin,card_no,device_id,door_id,in_address,out_address,verified,state,event_type,trigger_opt)'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            try:
                print 'copy date from tmp'
                sql='INSERT INTO acc_monitor_log(change_time,  create_time , STATUS , log_tag,TIME , pin , card_no , device_id , device_sn, device_name, door_id, door_name,  in_address ,out_address, verified , state , event_type , trigger_opt ) \
                    SELECT getdate(), getdate(),0,  log_tag,TIME , pin , card_no , device_id , device_sn,device_name, door_id, door_name,  in_address ,out_address, verified , state , event_type , trigger_opt FROM acc_monitor_log_tmp1'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            print 'DROP table acc_monitor_log_tmp1'
            sql='DROP table acc_monitor_log_tmp1'
            cursor.execute(sql)
            connection._commit()
            
        elif database_engine=='mysql':
#            print "personnel empchange"
            sql="alter table personnel_empchange modify oldvalue longtext"
            cursor.execute(sql)
            conn._commit()
            sql="alter table personnel_empchange modify newvalue longtext"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table Departments modify DeptName nvarchar(100)"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table Departments modify code nvarchar(100)"
            cursor.execute(sql)
            conn._commit()       
#            
            sql="alter table checkinout modify checktype varchar(5)"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table userinfo modify street varchar(100)"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table userinfo modify cuser1 varchar(100)"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table userinfo modify cuser2 varchar(100)"
            cursor.execute(sql)
            conn._commit()
                    
            sql = 'desc userinfo'
            cursor.execute(sql)
            qets = cursor.fetchall()
            for q in qets:#判断password长度，如果是8则未加过密
                if q[0].lower() == 'password' and q[1] == 'varchar(8)':
                    sql="alter table userinfo modify Password varchar(16)"
                    cursor.execute(sql)
                    conn._commit()
                                
                    sql="alter table acc_door modify force_pwd varchar(18)"
                    cursor.execute(sql)
                    conn._commit()
                    
                    sql="alter table acc_door modify supper_pwd varchar(18)"
                    cursor.execute(sql)
                    conn._commit()
                    
                    sql="alter table iclock modify comm_pwd varchar(32)"
                    cursor.execute(sql)
                    conn._commit() 
                    process_pwd()
                    break
            print 'mysql'
            print 'create tmp table and copy data'
            sql='CREATE TABLE acc_monitor_log_tmp1 SELECT DISTINCT log_tag,TIME,pin,card_no,device_id,device_sn,device_name, door_id, door_name, in_address,out_address,verified,state,event_type,trigger_opt \
             FROM acc_monitor_log '
            cursor = connection.cursor()
            cursor.execute(sql)
            connection._commit()
        
            print 'TRUNCATE TABLE acc_monitor_log'
            sql='TRUNCATE TABLE acc_monitor_log'
            cursor.execute(sql)
            connection._commit()
            
            try:
                sql = 'update acc_monitor_log_tmp1 set out_address=-1 where out_address is null'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            try:
                print 'ALTER TABLE acc_monitor_log MODIFY trigger_opt INT(6) DEFAULT -1'
                sql='ALTER TABLE acc_monitor_log MODIFY trigger_opt INT(6) DEFAULT -1'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            try:
                print 'ALTER TABLE acc_monitor_log MODIFY in_address INT(6) DEFAULT -1'
                sql='ALTER TABLE acc_monitor_log MODIFY in_address INT(6) DEFAULT -1'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            try:
                print 'ALTER TABLE acc_monitor_log ADD CONSTRAINT time_pin UNIQUE'
                sql='ALTER TABLE acc_monitor_log ADD CONSTRAINT time_pin UNIQUE (TIME, pin,card_no,device_id,door_id,in_address,out_address,verified,state,event_type,trigger_opt)'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
        
            try:
                print 'copy date from tmp'
                sql='INSERT INTO acc_monitor_log(change_time,  create_time , STATUS , log_tag,TIME , pin , card_no , device_id ,device_sn, device_name, door_id, door_name,  in_address , out_address,verified , state , event_type , trigger_opt ) \
                    SELECT NOW(), NOW(),0,  log_tag,TIME , pin , card_no , device_id ,device_sn, device_name, door_id, door_name,  in_address , out_address,verified , state , event_type , trigger_opt FROM acc_monitor_log_tmp1'
                cursor.execute(sql)
                connection._commit()
            except:
                print_exc()
                pass
            
            print 'drop table acc_monitor_log_tmp1'
            sql='drop table acc_monitor_log_tmp1'
            cursor.execute(sql)
            connection._commit()
            

            
        elif database_engine=='oracle':
#            sql="alter table personnel_empchange modify oldvalue longtext"
#            cursor.execute(sql)
#            conn._commit()
#            
#            sql="alter table personnel_empchange modify newvalue longtext"
#            cursor.execute(sql)
#            conn._commit()
            
            sql="alter table Departments modify (DeptName nvarchar2(100))"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table Departments modify (code nvarchar2(100))"
            cursor.execute(sql)
            conn._commit()       
#            
            sql="alter table checkinout modify (checktype nvarchar2(5))"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table userinfo modify (street nvarchar2(100))"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table userinfo modify (cuser1 nvarchar2(100))"
            cursor.execute(sql)
            conn._commit()
            
            sql="alter table userinfo modify (cuser2 nvarchar2(100))"
            cursor.execute(sql)
            conn._commit()
                    
            sql="select DATA_LENGTH  from  user_tab_columns  where table_name='USERINFO' and column_name='PASSWORD'"
            cursor.execute(sql)
            qets = cursor.fetchall()
            if qets and qets[0][0] == '16':
                sql="alter table userinfo modify (Password nvarchar2(16))"
                cursor.execute(sql)
                conn._commit()
                            
                sql="alter table acc_door modify (force_pwd nvarchar2(18))"
                cursor.execute(sql)
                conn._commit()
                
                sql="alter table acc_door modify (SUPPER_PWD nvarchar2(18))"
                cursor.execute(sql)
                conn._commit()
                
                sql="alter table iclock modify (comm_pwd nvarchar2(32))"
                cursor.execute(sql)
                conn._commit() 
                process_pwd()
            try: 
                sql="alter table acc_monitor_log add constraint uq_id unique(time, pin,card_no,device_id,door_id,in_address,verified,state,event_type,trigger_opt)"
                cursor.execute(sql)
                conn._commit()
            except:
                pass
        cursor = connection.cursor()
        #sql = 'update userinfo set isatt=1'
        #cursor.execute(sql)
        #员工自助补签卡添加审核
        sql = "UPDATE checkexact SET audit_status =2  WHERE audit_status is NULL"
        cursor.execute(sql)
        connection._commit()

        #员工自助请假单添加审核
        sql = "UPDATE user_speday SET audit_status =2  WHERE audit_status is NULL"
        cursor.execute(sql)
        connection._commit()
        
    except:
        import traceback;traceback.print_exc()
        pass
#    print u'update database complie...'
    finally:
        connection.close()
#升级前先备份数据库
def backup_db():
    logger = logging.getLogger()
    database_user = settings.DATABASES["default"]["USER"]
    database_password = settings.DATABASES["default"]["PASSWORD"]
    database_engine = settings.DATABASES["default"]["ENGINE"]
    database_name = settings.DATABASES["default"]["NAME"]
    database_host = settings.DATABASES["default"]["HOST"]
    database_port = settings.DATABASES["default"]["PORT"]

    backup_file = ""
    dict = get_attsite_file()
    path = dict["Options"]["BACKUP_PATH"]#.encode('gbk')
    #print type(path)
    #print path
    if path == "":
        path = settings.APP_HOME+"/tmp"
    if not os.path.exists(path):
        os.mkdir(path)

    if database_engine == "django.db.backends.mysql":
        backup_file = path+"\\db_upgrade_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S") +".sql"
    #backup_file = "python manage.pyc dumpdata >\"%s\""%backup_file
        if database_password != "":
            backup_file = "mysqldump --hex-blob -l --opt -q -R --default-character-set=utf8 -h %s -u %s -p%s --port %s --database %s >%s"%(database_host, database_user, database_password, database_port, database_name, backup_file)
        else:
            backup_file = "mysqldump --hex-blob -l --opt -q -R --default-character-set=utf8 -h %s -u %s --port %s --database %s >%s"%(database_host, database_user, database_port, database_name, backup_file)
    elif database_engine == "sqlserver_ado":
        database_name='[%s]'%database_name
        backup_file = path+"\\db_upgrade_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")  +".bak"
        backup_file = '''sqlcmd -U %s -P %s -S %s -Q "backup database %s to disk='%s'"'''%(database_user,database_password,database_host,database_name,backup_file)
    elif database_engine == "django.db.backends.oracle":
        path = os.environ["path"]
        list = path.split(";")
        oracle_path = ""
        for i  in list:
            if "oraclexe" in i:
                oralce_path = i
        backup_file = path+"\\db_upgrade_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S") +".dmp"
        backup_file = "%s\\exp %s/%s@%s file='%s'"%(oracle_path,database_user,database_password,database_name,backup_file)
    p = subprocess.Popen(backup_file.encode('gbk'), shell=True, stderr=subprocess.PIPE)
    p.wait()
    stderrdata = p.communicate()
    if p.returncode != 0:
        logger.error(stderrdata)
    
    
#处理密码加密，视频密码暂不考虑.
def process_pwd():
    try: 
        cursor = connection.cursor()
        sql = "select badgenumber, Password from userinfo"
        cursor.execute(sql)
        qets = cursor.fetchall()
        for q in qets:
            try:
                password = q[1].strip()
            except:
                password = ''
            sql = u"update userinfo set Password='%s' where badgenumber=%s"%(encryption(password), q[0])
            #cursor = connection.cursor()
            cursor.execute(sql)
            connection._commit()
        
        sql = "select id, comm_pwd from iclock"
        cursor.execute(sql)
        qets = cursor.fetchall()
        for q in qets:
            try:
                comm_pwd = q[1].strip()
            except:
                comm_pwd = ''
            sql = u"update iclock set comm_pwd='%s' where id=%s"%(encryption(comm_pwd), q[0])
            #cursor = connection.cursor()
            cursor.execute(sql)
            connection._commit()

        sql = "select id, force_pwd, supper_pwd from acc_door"
        cursor.execute(sql)
        qets = cursor.fetchall()
        for q in qets:
            try:
                force_pwd = q[1].strip()
            except:
                force_pwd = ''
            try:
                supper_pwd = q[2].strip()
            except:
                supper_pwd = ''
            sql = u"update acc_door set force_pwd='%s', supper_pwd='%s' where id=%s"%(encryption(force_pwd), encryption(supper_pwd), q[0])
            #cursor = connection.cursor()
            cursor.execute(sql)
            connection._commit()
        connection._commit()
        connection.close()
    except:
        import traceback;traceback.print_exc()
        connection.close()
        pass
    
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
    dict = get_attsite_file()
    version = None
    version_file = str(dict["Options"]["Version"])
    version_db = version_file.split('.')[0] #attsite中的数据库版本号
    new_svn_version = version_file.split('.')[1] #attsite 中的svn 版本号
    app_option = AppOption.objects.filter(optname='dbversion')
    if app_option:
        version = app_option[0].value.split('.')[0] #数据库中的数据库版本号
        svn_version = app_option[0].value.split('.')[1] #数据库中的svn 的版本号
    if not version: 
        super(AppOption,AppOption(optname="dbversion", value=version_file, discribe=u"%s" % _(u'版本'))).save()
        sync_db()
    elif int(version_db) > int(version) or int(new_svn_version) >int(svn_version) :
        app_option[0].value = version_file
        super(AppOption,app_option[0]).save()
        sync_db()
except Exception, e:
    print e
    pass
