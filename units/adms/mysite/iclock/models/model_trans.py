#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from mysite.personnel.models import Department
from mysite.personnel.models.model_emp import Employee, EmpForeignKey,EmpPoPForeignKey
from model_device import Device, DeviceForeignKey
from base.operation import OperationBase, Operation, ModelOperation
from mysite.utils import get_option
from django.db import connections, IntegrityError, DatabaseError
#from base.models import CachingModel

def get_stored_file_name(sn, id, fname):
        fname="%s%s/%s"%(settings.ADDITION_FILE_ROOT, sn, fname)
        if id:
                fname, ext=os.path.splitext(fname)
                fname="%s_%s%s"%(fname,id,ext)
        fname.replace("\\\\","/")
        return fname

def get_upload_file_name(sn, id, fname):
        return get_stored_file_name('upload/'+sn, id, fname)

def get_stored_file_url(sn, id, fname):
        fname=settings.UNIT_URL+"iclock/file/%s/%s"%(sn, fname)
        if id:
                fname, ext=os.path.splitext(fname)
                fname="%s_%s%s"%(fname,id,ext)
        return fname


def get_upload_file_url(sn, id, fname):
        return get_stored_file_url('upload/'+sn, id, fname)



VERIFYS=(
#(3, _("Card")),
(0, _(u"密码")),
(1, _(u"指纹")),
(2, _(u"卡")),
(5, _(u"增加")),

(9, _(u"其他")),
)

ATTSTATES=(
("I",_(u"上班签到")),
("O",_(u"下班签退")),

("8",_(u"就餐开始")),
("9",_(u"就餐结束")),
#("i",_("Break in")),
#("o",_("Break out")),
#("0",_("Check in")),
#("1",_("Check out")),
("2",_(u"外出")),
("3",_(u"外出返回")),
("4",_(u"加班签到")),
("5",_(u"加班签退")),
("255",_(u"未设置状态")),
#("160",_("Test Data")),
)


IS_MYSQL_DB = 1
IS_SQLSERVER_DB = 2
IS_ORACLE_DB = 3
IS_POSTGRESQL_DB = 4

#根据不同的数据库 执行对应的sql语句
db_select = IS_MYSQL_DB
if 'mysql' in connection.__module__:#mysql 数据库
    db_select = IS_MYSQL_DB
elif 'sqlserver_ado' in connection.__module__:#sqlserver 2005 数据库 
    db_select = IS_SQLSERVER_DB
elif 'oracle' in connection.__module__: #oracle 数据库 
    db_select = IS_ORACLE_DB
elif 'postgresql_psycopg2' in connection.__module__: # postgresql 数据库
    db_select = IS_POSTGRESQL_DB


def normal_state(state):
    if state == '0': return 'I'
    if state == '1': return 'O'
    try:
        d = int(state)
        if d >= 32 and d < 127:
            return chr(d)
    except: pass
    return state

def normal_verify(state):
    try:
        d = int(state)
        if d >= 32 and d < 127:
            return chr(d)
    except: pass
    return state


class Transaction(models.Model,OperationBase):
        UserID = models.CharField(db_column='userid', verbose_name=_(u"人员"),max_length=20, null=True, blank=True)
        PIN = models.CharField(db_column='pin', verbose_name=u"人员编号", max_length=20)
        TTime = models.DateTimeField(_(u'考勤时间'), db_column='checktime')
        State = models.CharField(_(u'考勤状态'), db_column='checktype', max_length=5, default='I', choices=ATTSTATES)
        Verify = models.IntegerField(_(u'验证方式'), db_column='verifycode', default=0, choices=VERIFYS)
        SN = models.CharField(db_column='SN', verbose_name=_(u'设备'), null=True, blank=True,max_length=20)
        sensorid = models.CharField(db_column='sensorid', verbose_name=u'Sensor ID', null=True, blank=True, max_length=5, editable=False)
        WorkCode = models.CharField(_(u'工作号码'), max_length=20, null=True, blank=True)
        Reserved = models.CharField(_(u'保留'), max_length=20, null=True, blank=True)
        sn_name = models.CharField(_(u'序列号'), max_length=40, null=True, blank=True)
        def limit_transaction_to(self,query_set,user): 
#            from mysite.iclock.iutils import userDeptList,userAreaList
#            deptids = userDeptList(user)
#            if not deptids:
#                return query_set
#            #deptids = [ dept.pk for dept in deptids ]
#            return query_set.filter(UserID__DeptID__in=deptids)
            if not user.is_superuser:
                query_set=query_set.extra(where=['checkinout.PIN in (select userid from userinfo where defaultdeptid in (select dept_id from deptadmin where user_id='+ str(user.pk) +'))'])
            return query_set

        def employee(self): #cached employee
                try:
                        return Employee.objByID(self.UserID_id)
                except:
                        return None
        def Time(self):
                if self.TTime.microsecond>500000:
                        self.TTime=self.TTime+datetime.timedelta(0,0,1000000-self.TTime.microsecond)
                return self.TTime
        def StrTime(self):
                return self.Time().strftime('%Y/%m%d/%H%M%S')
        @staticmethod        
        def delOld(): return ("TTime", 365)
        def Device(self):
                return get_device(self.sn_name)
        def get_img_url(self, default=None):
                device=self.Device()
                emp=self.employee()
                if device and emp:
                        try:
                                pin=int(emp.PIN)
                        except:
                                pin=emp.PIN
                        fname="%s.jpg"%(self.StrTime())
                        imgUrl=getUploadFileName(device.SN, pin, fname)
                        if os.path.exists(imgUrl):
                                return getUploadFileURL(device.SN, pin, fname)
                return default
            
        def get_thumbnail_url(self, default=None):
                device=self.Device()
                emp=self.employee()
                if device and emp:
                        try:
                                pin=int(emp.PIN)
                        except:
                                pin=emp.PIN
                        fname="%s.jpg"%(self.StrTime())
                        imgUrl=getUploadFileName("thumbnail/"+device.SN, pin, fname)
                        #print imgUrl
                        if not os.path.exists(imgUrl):
                                imgUrlOrg=getUploadFileName(device.SN, pin, fname)
                                if not os.path.exists(imgUrlOrg):
                                        #print imgUrlOrg, "is not exists"
                                        return default
                                if not createThumbnail(imgUrlOrg, imgUrl):
                                        #print imgUrl, "create fail."
                                        return default
                        return getUploadFileURL("thumbnail/"+device.SN, pin, fname)
                #print "device, emp", device, emp
                return default
            
        def __unicode__(self):
                emp_obj="" 
                try:
                    emp_obj=Employee.objects.get(id=self.UserID_id)
                except:
                    pass
                return u"%s, %s"%(emp_obj,self.TTime.strftime("%y-%m-%d %H:%M:%S"))
#                return self.UserID.__unicode__()+', '+self.TTime.strftime("%y-%m-%d %H:%M:%S")
                
        @staticmethod
        def myData(user):
                if user.username=='employee': #employee user
                        return Transaction.objects.filter(UserID=request.employee)
                return Transaction.objects.filter(UserID__DeptID__in=userDeptList(user))
        
        def get_attpic(self):            
            from dbapp.additionfile import get_model_filename
            from mysite.personnel.models.model_emp import getuserinfo
            dt=self.TTime.strftime("%Y%m%d%H%M%S")
            pin=""
            user_pin = getuserinfo(self.UserID_id,"PIN")
            #pin= int(self.UserID.PIN)
            pin= int(user_pin)
            sn=self.sn_name

            t=get_model_filename(Transaction,            
            "%s/%s/%s" % (sn, dt[:4], dt[4:8])+"/"+ str(pin)+"_"+ dt[8:] + ".jpg",
            "picture")[1]
            return t
        
        def get_emppic(self):
            return self.UserID.photo 
        
        class dataexport(Operation):
                help_text=_(u"数据导出") #导出
                verbose_name=_(u"导出")
                visible=False
                def action(self):
                        pass
                    
        class OpUploadAttLog(ModelOperation):
            u"导入u盘记录"
            help_text = _(u'''导入u盘考勤记录''')
            verbose_name = _(u"导入u盘考勤记录")
            params = (
                    ('upload_attlog', models.FileField(verbose_name=_(u'选择考勤记录文件'), blank=True, null=True)),
            )
            def action(self,upload_attlog):
                from django.db import connection
                import datetime
                from mysite.personnel.models.model_emp import format_pin, Employee
                
                cursor = connection.cursor()
                if self.request.FILES:
                    f=self.request.FILES['upload_attlog']
                    f_format=str(f).split('.')
                    format_list=['dat']
                    ret = []
                    try:
                       format_list.index(str(f_format[1]))
                    except:
                       raise Exception (_(u"考勤文件格式无效！"))
                
                    try:
                        file_data = f.read()
                        file_data = file_data.strip()
                        log_list = file_data.split("\r\n")
                        sql = []
                        MYSQL_INSERT = u'''INSERT INTO checkinout(userid,checktime,checktype,verifycode,workcode)
                            VALUES %(batch_rows)s
                            '''
        
                        SQLSERVER_INSERT = u'''INSERT INTO checkinout(userid,checktime,checktype,verifycode,workcode)
                            VALUES('%(uid)s','%(time)s','%(type)s','%(vf)s','%(wc)s')
                            '''
                        for row in log_list:
                            try:
                                elems = row.split("\t")
                                if len(elems) != 6:
                                    ret.append(u"%(r)s:%(info)s"%{"r":row,"info":_(u"数据格式不正确")})
                                    continue
                                pin = elems[0].strip() #用户PIN号
                                ttime = elems[1].strip() #考勤时间
                                sdevice_id = elems[2].strip() #设备号
                                state  = elems[3].strip() #考勤状态
                                verify = elems[4].strip() # 验证方式
                                workcode = elems[5].strip() # 工作代码
                                
                                try:
                                    ttime = datetime.datetime.strptime(ttime,"%Y-%m-%d %H:%M:%S")
                                except:
                                    ret.append(u"%(r)s:%(info)s"%{"r":row,"info":_(u"时间格式不正确")})
                                    continue
                                obj_emp = None
                                try:
                                    obj_emp = Employee.objects.get(PIN = format_pin(pin))
                                except:
                                    #创建用户
                                    obj_emp  = Employee()
                                    obj_emp.PIN = pin
                                    obj_emp.DeptID_id = 1
                                    obj_emp.save()
                                    obj_emp.attarea = [1,]
                                
                                if db_select == IS_SQLSERVER_DB:
                                    sql.append(
                                        SQLSERVER_INSERT%{
                                            "uid":obj_emp.pk,
                                            "time":ttime,
                                            "type":normal_state(state),
                                            "vf":normal_verify(verify),
                                            "wc":workcode
                                        }
                                    )
                                elif db_select == IS_MYSQL_DB:
                                    sql.append(
                                        u'''('%(uid)s','%(time)s','%(type)s','%(vf)s','%(wc)s')'''%{
                                            "uid":obj_emp.pk,
                                            "time":ttime,
                                            "type":normal_state(state),
                                            "vf":normal_verify(verify),
                                            "wc":workcode
                                        }
                                    )
                                if len(sql)>200:
                                    if db_select == IS_SQLSERVER_DB:
                                        cursor.execute(";".join(sql))
                                    elif db_select == IS_MYSQL_DB:
                                        cursor.execute(
                                            MYSQL_INSERT%({"batch_rows":",".join(sql)})
                                        )
                                    sql = []
                            except IntegrityError:
                                    if sql:        
                                        for elem in sql:
                                            try:
                                                if db_select == IS_SQLSERVER_DB:
                                                    cursor.execute(elem)
                                                elif db_select == IS_MYSQL_DB:
                                                    cursor.execute(
                                                        MYSQL_INSERT%({"batch_rows":elem})
                                                    )
                                            except:
                                                pass
                                        sql = []
                            except Exception,e:
                                ret.append(u"%s"%e)
                        if sql:        
                            if db_select == IS_SQLSERVER_DB:
                                cursor.execute(";".join(sql))
                            elif db_select == IS_MYSQL_DB:
                                cursor.execute(
                                    MYSQL_INSERT%({"batch_rows":",".join(sql)})
                                )
                    except IntegrityError:
                        if sql:        
                            for elem in sql:
                                try:
                                    if db_select == IS_SQLSERVER_DB:
                                        cursor.execute(elem)
                                    elif db_select == IS_MYSQL_DB:
                                        cursor.execute(
                                            MYSQL_INSERT%({"batch_rows":elem})
                                        )
                                except:
                                    pass
                    except Exception,e:
                        ret.append(u"%s"%e)
                    finally:
                        try:
                            connection._commit()
                        except:
                            pass
                        
                        f.close()
                        
                    if ret:
                        raise Exception(u"%s"%("\n".join(ret)))
        
        class dataimport(ModelOperation):
                help_text = _(u"自定义导入记录") #导入
                verbose_name = _(u"自定义导入记录")
                def action(self):
                    from django.db import connection
                    from mysite.iclock.trans_import import ImportTransData
                    obj_import = ImportTransData(req = self.request,input_name = "import_data")
                    obj_import.exe_import_data()
                    ret_error = obj_import.error_info
                    if ret_error:
                        import traceback
                        traceback.extract_stack()
                        raise Exception(_(u'导入出错，请检查数据合法性'))
#                        raise Exception(u"%(ret)s"%{
#                                    "ret":";".join(ret_error)
#                              })
        
        def get_emp_name(self):
            u'''从缓存中得到人员name'''
            emp_name=""
            try:
                Employee.can_restore=True
                emp_obj=Employee.objects.get(id=self.UserID_id)
                Employee.can_restore=False
                emp_name=emp_obj.EName
            except:
                pass
            return emp_name
        
        def get_emp_pin(self):
            u'''从缓存中得到人员PIN号'''
            emp_pin=""
            try:
                Employee.can_restore=True
                emp_obj=Employee.objects.get(id=self.UserID_id)
                Employee.can_restore=False
                emp_pin=emp_obj.PIN
            except:
                pass
            return emp_pin
        
        def get_dept_name(self):
            u'''从缓存中得到部门的Name'''
            from mysite.personnel.models.model_emp  import get_dept
            dept_name=""
            try:
                dept_obj=get_dept(self.UserID_id)
                dept_name=dept_obj.name
            except:
                pass
            return dept_name
        
        def get_dept_code(self):
            u'''从缓存中得到部门的code'''
            from mysite.personnel.models.model_emp  import get_dept
            dept_code=""
            try:
                dept_obj=get_dept(self.UserID_id)
                dept_code=dept_obj.code
            except:
                pass
            return dept_code
        def get_device_name(self):
            u'''获取设备名称'''
            from mysite.iclock.models import Device
            if self.sn_name:
                dev=Device.objects.get(sn=self.sn_name)
                if dev:
                    return dev.alias                
            else:
                return ""
        class Meta:
                app_label='iclock'
                verbose_name = _(u"原始记录表")
                verbose_name_plural = verbose_name
                db_table = 'checkinout'
                unique_together = (("PIN", "TTime"),)
                permissions = (
                                ('clearObsoleteData_transaction','Clear Obsolete Data'),
                                )
        class Admin:
                default_give_perms=["contenttypes.can_AttCalculate"]
                sort_fields=["-TTime","UserID.PIN","UserID.DeptID.code",]
                app_menu="att"
                menu_group = 'att'
                visible = get_option("ATT")#暂只有考勤使用
                visible = False#暂只有考勤使用
                read_only=True
                api_fields=('UserID.PIN','UserID.EName','TTime','State','sn_name')
                list_display=('UserID_id','UserID.PIN','UserID.EName','UserID.DeptID.code','UserID.DeptID.name','TTime','WorkCode','State','get_device_name','sn_name','get_attpic','get_emppic')
                newadded_column={
                    "UserID.PIN":"get_emp_pin",
                    "UserID.EName":"get_emp_name",
                    "UserID.DeptID.name":"get_dept_name",
                    "UserID.DeptID.code":"get_dept_code",
                    
                }
                
                photo_path_tran="get_attpic"
                photo_path="get_emppic"
                                
                hide_fields=('UserID_id','get_attpic','get_emppic')
                
                list_filter = ('UserID','TTime','State','Verify','SN')
                query_fields=['UserID__PIN','UserID__EName','sn_name','TTime']
                search_fields=('TTime',)
                tstart_end_search={
                    "TTime":[_(u"起始考勤时间"),_(u"结束考勤时间")]
                }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
                
                menu_index=8
                disabled_perms=["add_transaction",'change_transaction','delete_transaction','clearObsoleteData_transaction']
                layout_types=["table","photo"]