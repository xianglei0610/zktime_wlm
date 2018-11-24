# -*- coding: utf-8 -*-
import datetime
import glob
from traceback import print_exc
from django.utils.translation import ugettext_lazy as _
from mysite.settings import *
from os import makedirs, remove
import os


WRITE_LOG = False#用户后台的调试，该变量与debug无关，即：可用于debug为False时的调试

def fwVerStd(ver): # Ver 6.18 Oct 29 2007 ---> Ver 6.18 20071029
        ml=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov','Dec']
        if ver and len(ver)>=20:
                tl=ver[9:].split(" ")
                try:
                        tl.remove("")
                except: pass
                try:
                        return ver[:9]+"%s%02d%02d"%(tl[2], 1+ml.index(tl[0]), int(tl[1]))
                except:
                        return ""
        else:
                return ""

def printf(str, primary=False):
    if DEBUG or primary:
        try:
            dt=datetime.datetime.now()
            mfile='tmp/center_%s.txt'%datetime.datetime.now().strftime("%Y%m%d")
            f=open(mfile,'a')
            wstr='%s-%d-%s\n'%(datetime.datetime.now().strftime("%H:%M:%S"), os.getpid(), str)
            f.write(wstr)
            f.close()
        except:
            print_exc()
            pass

def write_log(str, primary=False):#primary暂时不使用
    if WRITE_LOG:
        try:
            dt=datetime.datetime.now()
            mfile='tmp/center_%s.txt'%datetime.datetime.now().strftime("%Y%m%d")
            f=open(mfile,'a')
            wstr='-%s-%d-%s\n'%(datetime.datetime.now().strftime("%H:%M:%S"), os.getpid(), str)
            print wstr#手动启动时，显示到命令行，服务时打印到后台服务日志中
            f.write(wstr)
            f.close()
        except:
            print_exc()
            pass

#def pos_write_log(str,sn,cardno):
#        try:
#            import settings
#            dt=datetime.datetime.now()
#            path=settings.APP_HOME.replace('\\','/')
#            
#            mfile=path+'/tmp/zkpos/poslog/poslog_%s_%s_%s.txt'%(datetime.datetime.now().strftime("%Y%m"),sn,cardno)
#            f=open(mfile,'a')
#            wstr='Request-%s-%s\r\n'%(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f"),str)           
#            f.write(wstr)
#            f.close()
#        except:
#            print_exc()
#            pass

def pos_write_log(str,sn,cardno):
        import codecs,os,sys
        import settings
        if settings.DEBUG:
            try:
                dt=datetime.datetime.now()
                path=settings.APP_HOME.replace('\\','/') + '/tmp/zkpos/poslog/%s/%s/'%(sn,datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(path):
                    os.makedirs(path)
                mfile=path+'poslog_%s_%s_%s.txt'%(datetime.datetime.now().strftime("%Y-%m-%d"),sn,cardno)
                f=codecs.open(mfile,'a')
                wstr='Request-%s-%s\r\n'%(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S %f"),str)
                f.write(wstr)
                f.close()
            except:
                print_exc()
                pass


def delete_log():
    dt = datetime.datetime.now() + datetime.timedelta(days = -30)
    it=int(dt.strftime("%Y%m%d"))
    filelist=glob.glob('tmp/center_*.txt')
    for flist in filelist:
        ftime = 0
        try:
            ftime = int(flist.split('_')[1].split('.')[0])
        except:
            pass
        if ftime < it:
            remove(flist)


def get_option(key):
    u"得到配置文件中某个键的值"
    from mysite import config
    ret =""
    if hasattr(config.const,key):
        ret = getattr(config.const,key)
        if u"%s"%type(ret)==u"<class 'django.utils.functional.__proxy__'>":
            ret  = u"%s"%ret
    
    return  ret


def loads(str):
    '''
    json字符转化为python对象
    '''
    from django.conf import settings
    from django.utils import simplejson as json
    return json.loads(str, encoding=settings.DEFAULT_CHARSET) 

def customSqlEx(sql,params=[],action=True):
    from django.conf import settings
    from django.db import  connection
    try:
        cursor = connection.cursor()
        if settings.DATABASE_ENGINE == 'ibm_db_django':
            if not params:params=()
        if params:
            cursor.execute(sql,params)
        else:
            cursor.execute(sql)
        
        if action:
            connection._commit()
        return cursor
    except:
        return None
    
def customSql(sql,action=True):
    from django.db import  connection
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        if action:
            connection._commit()
        return cursor
    except:
        return None

def get_MultiSelect_objs(model,request):
    '''
    用来返回报表查询中选人控件选中了包含下级时的人员列表
    model 选择的对象模型 例: Employee
    request 请求上下文
    
    return  返回所选择的对象列表
    '''
    from mysite.iclock.iutils import get_dept_from_all,get_max_in
    userids=request.REQUEST.getlist('UserIDs')
    deptids=request.REQUEST.get('DeptIDs',"")
    u = []
    if request:
        if userids[0]:
              u=userids
        elif len(deptids)>0:
            dept_id = request.REQUEST.getlist("deptIDs")
            checked_child=request.REQUEST.get('deptIDschecked_child',None)
            if checked_child == "on" and dept_id:#包含部门下级
                depts = get_dept_from_all(dept_id,request)
                user_list = get_max_in(model.all_objects.all(),depts,"DeptID__in")
                u=[e.pk for e in user_list]
            else:
                user_list = get_max_in(model.all_objects.all(),dept_id,"DeptID__in")
                u=[e.pk for e in user_list]
    return u


def GetFormField(key,ModelField,**kwargs):
    '''
    由模型字段构造表单字段,供前端灵活使用
    
    key                表单字段名称
    ModelField    定义的模型字段 如: EmpPoPMultForeignKey
    
    返回可直接供前端使用的表单字段 如: 选人控件
    '''
    from django import forms
    from dbapp.widgets import form_field
    form=forms.Form()
    m_formfield = form_field(ModelField,**kwargs)
    form.fields[key] = m_formfield
    return form[key]

def params2form(params):
    from django.forms import forms
    from dbapp import widgets
    from dbapp.widgets import form_field
    form=forms.Form()
    for e in params:
        field = e[1]
        form.fields[e[0]]=form_field(field)
    return form

def GetAuthoIDs(user,Type):
    '''
    Type:  1 授权组织 2 授权区域
    '''
    from mysite.personnel.models.model_deptadmin import  DeptAdmin
    from mysite.personnel.models.model_areaadmin import AreaAdmin
    if  user.is_superuser or user.is_anonymous :
        return None
    area_admin_ids = AreaAdmin.objects.filter(user=user).values_list("area_id",flat=True)
    if Type==1:
        ids =  DeptAdmin.objects.filter(user=user).values_list("dept_id",flat=True)
    if Type==2:
        ids = AreaAdmin.objects.filter(user=user).values_list("area_id",flat=True)
    if ids:
        return ','.join([str(i) for i in ids])
    else:
        return None