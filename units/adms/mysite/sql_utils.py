# -*- coding: utf-8 -*-
import os
import traceback
from lxml import etree
from django.core.cache import cache
import settings
#from django.db import connection as conn
from dbutils_pool import getConn,reConn
from dbutils_pool import OperationalError, InternalError, ProgrammingError

from base.backup import get_attsite_file


TIMEOUT = 7*24*3600 #7天

develop_model = False 
if get_attsite_file()["Options"]["SQL_PRINT"].lower()=="true":
    develop_model = True

def get_curr_db_engine_name():
    u"""
                获取当前使用的数据库类型
    """
    db_name = ""
    if settings.DATABASES["default"]["ENGINE"] == "sqlserver_ado":
        db_name = "sqlserver"
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
        db_name = "mysql"
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
        db_name = "sqlite"
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
        db_name = "postgresql"
    elif settings.DATABASES["default"]["ENGINE"] == "django.db.backends.oracle":
        db_name = "oracle"
    else:
        db_name = settings.DATABASES["default"]["ENGINE"].split(".")[-1]
    return db_name
curr_db_engine_name = get_curr_db_engine_name()

def test_conn():
    """
            测试连接池连接是否正常
        return:
        res: True:正常,False:不正常
        msg: 如果不正常,为异常信息
    """
    test_sql = """
        select 1
    """
    conn = None
    cur = None
    res = False
    msg = ""    
    try:
        conn = getConn()
        cur = conn.cursor()            
        cur.execute(test_sql)
        res = cur.fetchall() 
        res = True
    except Exception,e:
        traceback.print_exc()
        msg = e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        return res,msg

def call_reConn():
    """
        重新创建连接池
    """
    reConn()

def p_query(sql):
    """
        dbutils 数据连接池
                    只能 执行 数据查询 sql 语句, 否则会抛错 
        
        @parm: 要执行的sql 语句
        @return:
            []: 查询结果为空
            None: sql 语句执行失败,出现异常
                        二维list: 正常结果
    """
    if develop_model:
        print u"p_query()=============>sql: %s"%sql
    conn = None
    cur = None
    res = None    
    try:
        conn = getConn()
        cur = conn.cursor()            
        cur.execute(sql)
        res = cur.fetchall() 
    except (OperationalError, InternalError):
        call_reConn()
        traceback.print_exc()
    except:
        traceback.print_exc()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        return res
    
    
def p_query_one(sql):
    """
        dbutils 数据连接池
                    只能 执行 数据查询 sql 语句, 否则会抛错 
        
                执行sql查询语句,获取第一条记录
        @parm: 要执行的sql 语句
        @return:
            []: 查询结果为空
            None: sql 语句执行失败,出现异常
            list: 正常结果
    """
    if develop_model:
        print u"p_query_one()=============>sql: %s"%sql
    conn = None
    cur = None
    res = None    
    try:
        conn = getConn()
        cur = conn.cursor()            
        cur.execute(sql)
        res = cur.fetchone()
    except (OperationalError, InternalError):
        call_reConn()
    except:
        traceback.print_exc()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        return res
    
def p_execute(sql):
    """
        dbutils 数据连接池
                    执行 数据操作语句, 包括  update,insert,delete    
                        
        @parm: 要执行的sql 语句
        @return:
            None: sql 语句执行失败,出现异常
            number: 影响记录条数
            -2: 数据库连接失败导致执行失败
    """
    if develop_model:
        print u"p_execute()=============>sql: %s"%sql
    conn = None
    cur = None
    res = None 
    try:
        conn =  getConn()
        cur = conn.cursor()            
        cur.execute(sql)
        res = cur._cursor.rowcount
        conn.commit()
    except Exception ,e:
        if conn:
            conn.rollback()
        traceback.print_exc()
    finally:
        if res == -1: # 可能是数据库断开连接
            ret,msg =test_conn()
            if not ret:
                call_reConn()
                res = -2
        if cur:
            cur.close()
        if conn:
            conn.close()
        return res
    
def p_mutiexec(sql_list):
    """
        dbutils 数据连接池
                    执行多条 数据操作语句,可以用于多条sql语句的事务性操作 包括  update,insert,delete    
                        
        @parm: 要执行的sql 语句 []
        @return:
            (flag,res):
            flag<True or False>:批次是否全部执行成功
            res<list> : 每条sql 语句执行影响的行数,如果执行失败,由此可以判断第几条sql语句执行失败
                                            如果遇到 数据库断开的情况,返回[-2,]
    """
    conn = None
    cur = None
    res = []
    flag = True
    if develop_model:
        print u"p_mutiexec()=============>sql: %s"%sql_list
    try:
        conn = getConn()
        cur = conn.cursor()
        for sql in  sql_list:           
            cur.execute(sql)
            num = cur._cursor.rowcount
            res.append(num)
        conn.commit()
    except Exception ,e:
        flag = False
        if conn:
            conn.rollback()
        traceback.print_exc()
    finally:
        if -1 in res:
            ret,msg =test_conn()
            if not ret:
                call_reConn()
                flag = False
                res = [-2,]
        if cur:
            cur.close()
        if conn:
            conn.close()
        return flag,res
        
#def exe_sql(sql,params = None,action = True):
#    """
#            使用django 的常连接方式
#    """
#    if params:
#        sql = sql%params
#    if develop_model:
#        print u"=============>sql: %s"%sql
#    try:
#        cur = conn.cursor()            
#        cur.execute(sql)
#        if action:
#            conn._commit()
#        return cur,conn
#    except:
#        conn._rollback()
#        traceback.print_exc()
#        return None,None
#
#def get_sql_exe_result(sql,params=None):
#    """
#          使用django 的常连接方式
#    """
#    result = None
#    if sql:
#        try:
#            cur,conn = exe_sql(sql,params,False)
#            result = cur.fetchall()
#            conn._commit()
#        except:
#            traceback.print_exc()
#    return result

def get_sql_exe_result(sql,params=None):
    if params:
        sql = sql%params
    return p_query(sql)

def get_empIdList_by_user(request):
    u"""
        根据当前用户得到该用户所能操作的人员 id 列表
    """
    user = request.user
    if  user.is_superuser:
        return None
    sql = """select userid from userinfo
                left join deptadmin on userinfo.defaultdeptid = deptadmin.dept_id
                left join userinfo_attarea on userinfo.userid = userinfo_attarea.employee_id
                left join areaadmin on userinfo_attarea.area_id = areaadmin.area_id
            where areaadmin.user_id = %d or deptadmin.user_id = %d
        """%(user.pk,user.pk)
    
    ids = p_query(sql)
    return [id[0] for id in ids]

def get_sql_config_file():
    u"""
            @desc: 获取 settings 文件中  SQL_CONFIG_FILE 的配置,从而得到sqlconfig 文件
            @parms: 
            @return: 系统的 全局sql配置文件
    """
    if not settings.NEED_SQL:
        sqlconfig =  None
        if develop_model:
            print  u"get_sql_config_file()========> 无法获取sqlconfig.xml文件配置信息,因为settings文件中参数  NEED_SQL 设置为了 False!" 
    else:
        sqlconfig = settings.APP_HOME+'/'+settings.SQL_CONFIG_FILE
    return sqlconfig

def get_sql_file_dir(config_file,app = None):
    u"""
            @desc:根据 sqlconfig.xml 中 dir 的配置 ,获取 存放存放 sql语句的 xml文件的路径
            @parms:
                config_file: type<str(url)> 系统的 全局sql配置文件
                app: type<str> ,指定的app名称,参考 sqlconfig中的配置
            @return : type<list> sql 的 xml文件 所在目录列表
    """
    file_dir_list = []
    xpath_exp = "dirs/dir/@path"
    if app:
        xpath_exp = "dirs/dir[@app='%s']/@path"%app
    if os.path.exists(config_file):
        e =  etree.parse(config_file)
        file_dir_list = [a.replace(".","/") for a in e.xpath(xpath_exp)]           
    return file_dir_list
    
def get_sql_file(dir_list,sqlfile):
    u"""
            @desc:在dir_list 目录下的所有名为 sqlfile的文件
            @params:
                dir_list: type<list> sql 的 xml文件 所在目录列表
                sqlfile: type<str> sql语句指定的文件名
            @return: type<list> xml 文件完整路径列表
    """
    sql_xml_files=[]
    for file in dir_list:
        if os.path.exists(settings.APP_HOME+"/"+file+"/"+sqlfile+".xml"):
            sql_xml_files.append(settings.APP_HOME+"/"+file+"/"+sqlfile+".xml")
    if develop_model and not sql_xml_files:
        print u"get_sql_file()========> 无法得到指定的存放 sql语句的xml文件!" 
    return sql_xml_files
def get_sql_by_dict(ele_dict,params={},id_part={},only_content=False):
    u"""
            @desc:根据节点 以及相关的参数,获取sql语句
            @params:
                ele_dict: type<dict> sql 的内容和part 组成的字典
                params: type<dict>,  key 为  sql语句主体 和part主体 中要格式化的内容,value 为要替换的值
                id_part: type<dict>  key 为 sql 语句主体中需要 格式化 的内容,value 为 要格式化的part标签中的 id值 ,like {"aa":"bb"} or {"aa":["bb","cc",]}
                only_content : 如果设置为True,则直接返回 xml中的content 内容,不会进行参数匹配
            @return: type<str> 完整的sql语句
    """
    part= {}
    part_dict = ele_dict["part"]
    sql_text = ele_dict["sql_text"]
    if only_content:
        sql = sql_text
    else:
        for k,v in id_part.items():
            part[k] = ""
            if not isinstance(v,list):
                v = [v,]
            for val in v:
                if  part_dict.has_key(val):
                    part_ele = part_dict[val]
                    try:
                        part[k]+=(part_ele.strip()+" ")%params
                    except KeyError, e:
                        except_str = u"get_sql_by_dict()========>参数错误:\n\t id 为 %(val)s 的<part>标签缺少参数[%(msg)s] "%{"val":val,"msg":e}
                        raise Exception(except_str)
                    except:
                        traceback.print_exc()
        params.update(part)
        try:
            sql = sql_text%params
        except KeyError, e:
            except_str = u"get_sql_by_dict()========>参数错误:\n\t <content>缺少参数 [%(msg)s] "%{"msg":e}
            raise Exception(except_str)
        except:
            traceback.print_exc()
    return sql

def  get_sql_ele_content(sqlfiles,engine_name=curr_db_engine_name,sqlid=None):
    u"""
            @desc: 获取xml 文件中指定sql节点
                                    规则:
                    1.若根据 sqlfilename 以及其他相关的条件搜索出多条 匹配的 sql节点,则默认返回sqlconfig中配置的第一个 匹配的dir的path路径下的sql 
                    2.若根据当前数据库引擎没有搜索到对应的sql语句,则会搜索出 engine="default" 属性下的sql节点
            @params:
                sqlfiles: type<list>, sql 所在的xml文件的搜索路径列表
                engine_name: type<str> , 数据库类型
                sqlid: type(str), sql语句的sql标签 id
            @return: type<Ele> sql语句节点
    """
    sql_ele = None
    for f in sqlfiles:
        if os.path.exists(f):
            e =  etree.parse(f)
            if sqlid:
                content_exp = "/sqlgroup/sql[@id='%s']/content[@engine='%s']"%(sqlid,engine_name)
            else:
                content_exp = "/sqlgroup/sql/content[@engine='%s']"%engine_name
            sql_ele =  e.xpath(content_exp) 
            if sql_ele:
                sql_ele = sql_ele[0]
                break;
            else: 
                if sqlid:
                    content_exp = "/sqlgroup/sql[@id='%s']/content[@engine='%s']"%(sqlid,"default")
                else:
                    content_exp = "/sqlgroup/sql/content[@engine='%s']"%"default"
                sql_ele =  e.xpath(content_exp) 
                if sql_ele:
                    sql_ele = sql_ele[0]
                    break;
    return sql_ele

def get_sql_ele(sqlfilename,sqlid,app):
    """
        获取sql语句所在的xml文件节点
    """
    engine_name = curr_db_engine_name
    sql_config_file = get_sql_config_file()
    config_dir = get_sql_file_dir(sql_config_file,app)
    sql_file = get_sql_file(config_dir,sqlfilename)
    sql_ele = get_sql_ele_content(sql_file,engine_name,sqlid)
    return sql_ele
def update_ele_to_dict(sql_ele):
    """
                    将一个sql语句的xml 节点转化为一个字典 易于存储
        格式:
        {
            "sql_text": content,
            "part":{ 
                   "id1":part_content1, 
                   "id2":part_content2
            }
        }
    """
    part = {}
    sql_text = sql_ele.text.strip().replace("\n\t","  ").replace("\n","  ")
    part_ele = sql_ele.xpath("part")
    for p in part_ele:
        part[p.attrib["id"].strip()] = p.text.strip()
    return {"sql_text":sql_text,"part":part}
  
def get_sql(sqlfilename,sqlid=None,app = None,params={},id_part={},only_content=False):
    u"""
        @desc:获取sql语句内容
        @params:
            sqlfilename: type<str>指定存放sql语句的 xml文件名
            sqlid:type<str> xml文件中 sql 语句指定 sql标签的id
            app:type<str>  sql 语句所指定的app
            params: type<dict>,  key 为  sql语句主体 和part主体 中要格式化的内容,value 为要替换的值
            id_part: type<dict>  key 为 sql 语句主体中需要 格式化 的内容,value 为 要格式化的part标签中的 id值 ,like {"aa":"bb"} or {"aa":["bb","cc"]}
            only_content: 如果设置为True,则直接返回 xml中的content 内容,不会进行参数匹配
        @return: 根据条件筛选出来的 sql 语句
    """
    if develop_model:
        print u"""get_sql()===========> The params you given is:
            sqlfilename:%s
            sqlid:%s
            app:%s
            params:%s
            id_part:%s
            only_content:%s
        """%(str(sqlfilename),str(sqlid),str(app),str(params),str(id_part),str(only_content))
    sql = " "
    try: 
        key = "%s_%s_%s"%(sqlfilename,sqlid,app)
        sql_dict = cache.get(key)
        if  not sql_dict: 
            sql_ele = get_sql_ele(sqlfilename,sqlid,app)
            sql_dict = update_ele_to_dict(sql_ele)
            cache.set(key,sql_dict,TIMEOUT)
        else:
            if develop_model:
                print "get_sql()===========>The sql is come from cache."
        sql = get_sql_by_dict(sql_dict,params,id_part,only_content)
    except:
        traceback.print_exc()    
    if develop_model:
         print u"get_sql()============> sql_result:\n\t%s"%sql
    return sql
    
    
    