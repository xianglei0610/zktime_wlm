# -*- coding: utf-8 -*-
from django.db import models, connection
import datetime
import os
import string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from model_dept import DeptForeignKey, DEPT_NAME, Department
from model_country import CountryForeignKey, COUNTRY_NAME, Country
from model_state import StateForeignKey, STATE_NAME, State
from model_city import CityForeignKey, CITY_NAME, City
from model_position import PositionForeignKey, POSITION_NAME, Position
from model_education import EducationForeignKey, EDUCATION_NAME, Education
from model_national import  NationalForeignKey, NATIONAL_NAME, National
from model_morecardempgroup import AccMoreCardEmpGroup

from base.models import CachingModel, Operation, ModelOperation
from dbapp.models import BOOLEANS
from base.cached_model import STATUS_PAUSED, STATUS_OK, STATUS_LEAVE
#from mysite.iclock.dataprocaction import *
#from mysite.iclock.models.dev_comm_operate import sync_set_user, sync_set_userinfo, sync_set_user_privilege, sync_set_user_privilege, sync_set_user_fingerprint, sync_delete_user, sync_delete_user_privilege, sync_delete_user_finger,sync_set_acc_user,sync_set_acc_user_fingerprint
from django import forms
from base.base_code import BaseCode, base_code_by
from model_area import Area, AreaManyToManyField
from dbapp import data_edit
from base.crypt import encryption
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from mysite.utils import get_option
#from model_iccard import ICcard,ICcardForeignKey
photo_storage = FileSystemStorage(
    location=settings.ADDITION_FILE_ROOT,
    #base_url=settings.APP_HOME+"/file"
)

emp_update_list = []
emp_insert_list=[]

GENDER_CHOICES = (
        ('M', _(u'男')),
        ('F', _(u'女')),
)

PRIV_CHOICES = (
        (0, _(u'普通员工')),
        (2, _(u'登记员')),
        (6, _(u'系统管理员维护')),
        (14, _(u'超级管理员')),
)

EMPTYPE = (
        (1, _(u'正式员工')),
        (2, _(u'试用员工')),
)

NORMAL_FINGER = 1      # 普通指纹
DURESS_FINGER = 3      # 胁迫指纹

init_settings = []
if settings.APP_CONFIG["remove_permision"]:
    init_settings = [ k.split(".")[1] for k, v in settings.APP_CONFIG["remove_permision"].items() if v == "False" and k.split(".")[0] == "Employee"]
    
def format_pin(pin):
    if type(pin) == int or type(pin)==float:
        pin = str(int(pin))
    if not settings.PIN_WIDTH: return pin
    if (settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT")) or not pin.isdigit():return pin             
    return string.zfill(device_pin(pin.strip()), settings.PIN_WIDTH)

def device_pin(pin):
    if not settings.PIN_WIDTH: return pin
    if (settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT")) or not pin.isdigit(): return pin
    i = 0
    for c in pin[0:-1]:
            if c == "0":
                    i += 1
            else:
                    break
    return pin[i:]
def get_pk(obj):
    if obj:
        return obj.pk
    else:
        return None

if settings.PIN_WIDTH == 5: MAX_PIN_INT = 65534
elif settings.PIN_WIDTH == 10: MAX_PIN_INT = 4294967294L
elif settings.PIN_WIDTH <= 1: MAX_PIN_INT = 999999999999999999999999L
else: MAX_PIN_INT = int("999999999999999999999999"[:settings.PIN_WIDTH])

CHECK_CLOCK_IN = (
        (0, _(u'依据相应时间段')),
        (1, _(u'上班必须签到')),
        (2, _(u'上班不用签到')),
)

CHECK_CLOCK_OUT = (
        (0, _(u'依据相应时间段')),
        (1, _(u'上班必须签到')),
        (2, _(u'上班不用签到')),
)

def get_default_dept():
        """ 获取默认部门；没，则创建
                """
        try:
                dept = Department.objects.get(DeptID=1)
        except:
                try:
                        dept = Department(id=1, name=_(u"总公司"))
                        dept.save()
                except:
                        dept = Department.objects.all()[0]
        return dept

def get_default_PIN():
        from mysite.personnel.sql import get_default_PIN_sql
        sqlstr = get_default_PIN_sql()
        cur = connection.cursor()
        cur.execute(sqlstr)
        res = cur.fetchall()
        if res:
            data = res[0][0]
        else:
            data = None

        if data:
                pin = data
        else:
                pin = ""
        char = ""
        num = ""
        for i in range(len(pin)):
                if pin[i:].isdigit():
                        char = pin[:i]
                        num = pin[i:]
                        break
        if num:
                diglen = len(num)
                return char + (str(int(num) + 1).zfill(diglen))
        else:
                return ""

YESORNO = (
        (1, _(u'是')),
        (0, _(u'否')),
)

SUPER_AUTH = (
        (0, _(u'否')),
        (15, _(u'是')),
)



HIRETYPE = (
        (1, _(u'合同内')),
        (2, _(u'合同外')),

)
LEAVETYPE = (
        (1, _(u'自离')),
        (2, _(u'辞退')),
        (3, _(u'辞职')),
        (4, _(u'调离')),
        (5, _(u'停薪留职')),
)
def show_visible():
    if settings.APP_CONFIG.language.language!='zh-cn':
        return False
    else:
        if get_option("ATT"):
            return True
        else:
            return False
def en_query_hide():
    education=[]
    if settings.APP_CONFIG.language.language!='zh-cn':
        education=[]           
    else:
        education=['education'] 
    if not get_option("ATT"):
        education=education+["level_count",]
    return education
Education=[]
#job_transfer=[]
if show_visible():
    Education=['Education',]
#if not show_visible():
#    job_transfer=["oppositionchange_employee",]
#处理英文版安装下  角色 人事中的删除与职务调动操作
def is_att_only():
    job_transfer=[]
    if not show_visible():
        job_transfer=["oppositionchange_employee",]
    
    from mysite import settings
    installed_apps = settings.INSTALLED_APPS
    if not get_option("IACCESS"):
        job_transfer =job_transfer+["delete_employee"]
    
    return job_transfer
class Employee(CachingModel):
        id = models.AutoField(db_column="userid", primary_key=True, null=False, editable=False)
        PIN = models.CharField(_(u'人员编号'), db_column="badgenumber", null=False, max_length=20)
        DeptID = DeptForeignKey(db_column="defaultdeptid", verbose_name=DEPT_NAME, editable=True, null=True)
        country = CountryForeignKey( verbose_name=COUNTRY_NAME, editable=True, null=True, blank=True)
        state = StateForeignKey(verbose_name=STATE_NAME, editable=True, null=True, blank=True)
        city = CityForeignKey(verbose_name=CITY_NAME, editable=True, null=True, blank=True)
        position = PositionForeignKey( verbose_name=POSITION_NAME, editable=True, null=True, blank=True)        
        education = EducationForeignKey(verbose_name=EDUCATION_NAME, editable=True,null=True, blank=True)
        national = NationalForeignKey( verbose_name=NATIONAL_NAME, editable=True, null=True, blank=True)
#        nativeplace = CityForeignKey(_(u'籍贯'), max_length=20, null=True, blank=True, editable=True,)
        EName = models.CharField(_(u'姓名'), db_column="name", null=True, max_length=24, blank=True, default="")
        lastname = models.CharField(_(u'姓氏'), max_length=20, null=True, blank=True, editable=True)
        #Password = models.CharField(_(u'密码'), max_length=8, null=True, blank=True, editable=True) #Password
        Password = models.CharField(_(u'密码'), max_length=16, null=True, blank=True, editable=True)#加密 增加长度
#        Card = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default='')
        Privilege = models.IntegerField(_(u'人员设备权限'), null=True, default=0,blank=True, choices=PRIV_CHOICES)
        AccGroup = models.IntegerField(_(u'门禁组'), null=True, blank=True, editable=True)
        TimeZones = models.CharField(_(u'门禁时间段'), max_length=20, null=True, blank=True, editable=True)
        Gender = models.CharField(_(u'性别'), max_length=2, choices=GENDER_CHOICES, null=True, blank=True)
        Birthday = models.DateField(_(u'生日'), max_length=8, null=True, blank=True)
        Address = models.CharField(_(u'办公地址'), db_column="street", max_length=100, null=True, blank=True)
        PostCode = models.CharField(_(u'邮编'), db_column="zip", max_length=6, null=True, blank=True)
        Tele = models.CharField(_(u'办公电话'), db_column="ophone", max_length=20, null=True, blank=True, default='')
        FPHONE = models.CharField(_(u'家庭电话'), max_length=20, null=True, blank=True)
        Mobile = models.CharField(_(u'手机'), db_column="pager", max_length=20, null=True, blank=True)
#        National = models.CharField(_(u'民族'), db_column="minzu", max_length=20, null=True, blank=True, choices=base_code_by('CN_NATION'), editable=True)
#        Title = models.CharField(_(u'职务'), db_column="title", max_length=50, null=True, blank=True, choices=base_code_by('TITLE'))
        #SN = DeviceForeignKey(db_column='SN', verbose_name=_(u'登记设备'), null=True, blank=True, editable=True)
        SSN = models.CharField(_(u'社保号'), max_length=20, null=True, blank=True)
        identitycard = models.CharField(_(u'身份证号码'), max_length=20, null=True, blank=True, default='')
        UTime = models.DateTimeField(_(u'更新时间'), null=True, blank=True, editable=False)
        Hiredday = models.DateField(_(u'聘用日期'), max_length=8, null=True, blank=True, default=datetime.datetime.now().strftime("%Y-%m-%d"))
        VERIFICATIONMETHOD = models.SmallIntegerField(_(u'验证方法'), null=True, blank=True, editable=False)
#        State = models.CharField(_(u'省份'), max_length=50, null=True, blank=True, editable=True, choices=base_code_by('IDENTITY'))
#        City = models.CharField(_(u'城市'), max_length=50, null=True, blank=True, editable=True, choices=base_code_by('CN_PROVINCE'))
#        Education = models.CharField(_(u'学历'), max_length=50, null=True, blank=True, editable=True, choices=base_code_by('EDUCATION'))
        SECURITYFLAGS = models.SmallIntegerField(_(u'动作标志'), null=True, blank=True, editable=False)
        ATT = models.BooleanField(_(u'有效考勤记录'), null=False, default=True, blank=True, editable=True)
        OverTime = models.BooleanField(_(u'是否加班'), null=False, default=True, blank=True, editable=True, choices=YESORNO)
        Holiday = models.BooleanField(_(u'节假日休息'), null=False, default=True, blank=True, editable=True, choices=YESORNO)
        INLATE = models.SmallIntegerField(_(u'上班签到'), null=True, default=0, choices=CHECK_CLOCK_IN, blank=True, editable=True)
        OutEarly = models.SmallIntegerField(_(u'下班签退'), null=True, default=0, choices=CHECK_CLOCK_OUT, blank=True, editable=True)
        Lunchduration = models.SmallIntegerField(_(u'荷兰语'), null=True, default=1, blank=True, editable=False)
        MVerifyPass = models.CharField(_(u'人员密码'), max_length=6, null=True, blank=True, editable=True)
        ##=models.ImageField(_(u'照片'),blank=True,null=True,editable=False,upload_to=MEDIA_ROOT)
        photo = models.ImageField(verbose_name=_(u'图片'),storage=photo_storage, upload_to='photo',max_length=200)
        #photo = models.CharField(_(u'个人照片'), max_length=200, null=True, blank=True, editable=True)
        SEP = models.SmallIntegerField(null=True, default=1, editable=False)
        OffDuty = models.SmallIntegerField(_(u"离职标记"), null=False, default=0, editable=False, choices=BOOLEANS)
        DelTag = models.SmallIntegerField(null=False, default=0, editable=False)
#        Image = models.ForeignKey(Photo, verbose_name=u'照片', null=True, blank=True)
        AutoSchPlan = models.SmallIntegerField(_(u'是否自动排班'), null=True, blank=True, default=1, editable=True, choices=YESORNO)
        MinAutoSchInterval = models.IntegerField(null=True, default=24, editable=False)
        RegisterOT = models.IntegerField(null=True, default=1, editable=False)
        #门禁区
        morecard_group = models.ForeignKey(AccMoreCardEmpGroup, verbose_name=_(u'多卡开门人员组'), blank=True, editable=True, null=True)
        set_valid_time = models.BooleanField(_(u'设置有效时间'), default=False, null=False, blank=True)
        acc_startdate = models.DateField(_(u'开始日期'), null=True, blank=True)
        acc_enddate = models.DateField(_(u'结束日期'), null=True, blank=True)
        acc_super_auth = models.SmallIntegerField(_(u'超级用户'), default=0, null=True, blank=True, editable=False, choices=SUPER_AUTH)

        #新加字段
        birthplace = models.CharField(_(u'籍贯'), max_length=20, null=True, blank=True, editable=True,)
        Political = models.CharField(_(u'政治面貌'), max_length=20, null=True, blank=True, editable=True)
#        contry = models.CharField(_(u'国家'), max_length=20, default="", null=True, blank=True, editable=True, choices=base_code_by('REGION'))
        hiretype = models.IntegerField(_(u'雇佣类型'), null=True, blank=True, editable=True, choices=HIRETYPE)
        email = models.EmailField(_(u'邮箱'), max_length=50, null=True, blank=True, editable=True)
        firedate = models.DateField(_(u'解雇日期'), null=True, blank=True, editable=True)
        attarea = AreaManyToManyField(Area, verbose_name=_(u'考勤区域'), null=True, blank=True, editable=True, default=(1,))
        isatt = models.BooleanField(verbose_name=_(u'是否考勤'), editable=True, null=False, blank=True, choices=YESORNO, default=1)
        homeaddress = models.CharField(_(u'家庭地址'), max_length=100, null=True, blank=True, editable=True)
        emptype = models.IntegerField(_(u'员工类型'), null=True, blank=True, editable=True, choices=EMPTYPE)
        bankcode1 = models.CharField(_(u'银行帐号1'), max_length=50, null=True, blank=True, editable=True)
        bankcode2 = models.CharField(_(u'银行帐号2'), max_length=50, null=True, blank=True, editable=True)
        isblacklist = models.IntegerField(_(u'是否黑名单'), null=True, blank=True, editable=True, choices=YESORNO)
        Iuser1 = models.IntegerField(_(u'保留字段1'), null=True, blank=True, editable=True)
        Iuser2 = models.IntegerField(_(u'保留字段2'), null=True, blank=True, editable=True)
        Iuser3 = models.IntegerField(_(u'保留字段3'), null=True, blank=True, editable=True)
        Iuser4 = models.IntegerField(_(u'保留字段4'), null=True, blank=True, editable=True)
        Iuser5 = models.IntegerField(_(u'保留字段5'), null=True, blank=True, editable=True)
        Cuser1 = models.CharField(_(u'保留字段1'), max_length=100, null=True, blank=True, editable=True)
        Cuser2 = models.CharField(_(u'保留字段2'), max_length=100, null=True, blank=True, editable=True)
        Cuser3 = models.CharField(_(u'保留字段3'), max_length=20, null=True, blank=True, editable=True)
        Cuser4 = models.CharField(_(u'保留字段4'), max_length=20, null=True, blank=True, editable=True)
        Cuser5 = models.CharField(_(u'保留字段5'), max_length=20, null=True, blank=True, editable=True)
        Duser1 = models.DateField(_(u'保留字段1'), null=True, blank=True, editable=True)
        Duser2 = models.DateField(_(u'保留字段2'), null=True, blank=True, editable=True)
        Duser3 = models.DateField(_(u'保留字段3'), null=True, blank=True, editable=True)
        Duser4 = models.DateField(_(u'保留字段4'), null=True, blank=True, editable=True)
        Duser5 = models.DateField(_(u'保留字段5'), null=True, blank=True, editable=True)
#        using_card = models.CharField(_(u'正在使用的有效卡号'),default="", max_length=20, null=True, blank=True, editable=True)
        
        selfpassword=models.CharField(_(u'登录密码'),max_length=20,default='123456', null=True,blank=True,editable=True)
        is_visitor = models.BooleanField(_(u'是否访客'), editable=True, null=False, blank=True, choices=YESORNO, default=0)
       
        
        all_objects = models.Manager()

        @staticmethod
        def objByID(id):
            try:
                u = Employee.objects.get(id=id)
            except:
                connection.close()
                u = Employee.objects.get(id=id)
            u.IsNewEmp = False

            return u
        
        @staticmethod
        def search_by_filter(qs_filter):  #xiaoxiaojun 2012.02.16 人员过滤 
            u'''查询出不在当前权限组中的人员
                return： (dbfield,where)
            '''
            
            from mysite.personnel.sql import search_by_filter_sql
            level_type = (str(qs_filter)).split("=")[0]
            level_id = (str(qs_filter)).split("=")[1]
            sql=search_by_filter_sql(level_type,level_id)
            return "userid",sql
            
        def _getEmpCard(self):
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
            try:
                objcard = IssueCard.objects.filter(UserID=self,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                if len(objcard)>0:
                    return objcard[0].cardno
            except:
                pass
            
            return ''
        
        Card = property(_getEmpCard) 
           
        def delete_cache_template_count(self):
            u'''删除模板数量缓存'''
            from mysite.personnel.cache import PERSONNEL_EMP_T_COUNT,TIMEOUT
            cache_key=PERSONNEL_EMP_T_COUNT+str(self.id)
            cache.delete(cache_key)
            
        def delete_cache_face_count(self):
            u'''删除人脸数量缓存'''
            from mysite.personnel.cache import PERSONNEL_FACE_COUNT,TIMEOUT
            cache_key=PERSONNEL_FACE_COUNT+str(self.id)
            cache.delete(cache_key)
            
        def cache_area(self,str_area):
            u"缓存区域"
            from mysite.personnel.cache import EMP_AREA,TIMEOUT
            cache_key=EMP_AREA%self.id
            
            cache.set(cache_key,str_area,TIMEOUT)
            
        def get_cache_area(self):
            u"获取员工区域"
#            from mysite.personnel.cache import EMP_AREA,TIMEOUT
#            cache_key=EMP_AREA%self.id
#            ret = cache.get(cache_key)
#            if ret == None:
#                str_area = u",".join([a.areaname for a in self.attarea.all()])
#                self.cache_area(str_area)
#                ret = str_area
            ret = u",".join([a.areaname for a in self.attarea.all()])  # 获取区域时取消缓存,无法即时更新区域信息
            return ret
            
        def delete_cache_area(self):
            u"删除区域缓存"
            from mysite.personnel.cache import EMP_AREA
            key = EMP_AREA%self.pk
            cache.delete(key)
            
        def delete(self, Init_db=False):
            from mysite import settings
            from mysite.iclock.models.model_device import Device, DEVICE_TIME_RECORDER,DEVICE_POS_SERVER
            from mysite.iclock.models.dev_comm_operate import sync_delete_user
            import os
            installed_apps = settings.INSTALLED_APPS
            if get_option("POS") and not Init_db:
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID
                nowtime = datetime.datetime.now().date()
                if type(self.Hiredday) == datetime.datetime:
                    day_count = (nowtime-self.Hiredday.date()).days
                else:
                    day_count = (nowtime-self.Hiredday).days
                if get_option("POS_ID"):
                    iscard = IssueCard.objects.filter(UserID=self)
                else:
                    iscard = IssueCard.objects.filter(UserID=self,sys_card_no__isnull=False)
                if iscard:
                    raise Exception(_(u'编号%s当前有在使用的消费卡，请先办理退款,退卡手续')%self)
#                if iscard and day_count < 365:
#                    raise Exception(_(u'为了保证消费系统数据安全性，该员工资料请在入职日期满一年后删除')%self)
                    
            filepath = settings.ADDITION_FILE_ROOT + "photo/" + self.PIN + ".jpg"
            if os.path.exists(filepath):
                os.remove(filepath)
            if get_option("ATT"):#zkeco+zktime
                if not Init_db:
                    from base.sync_api import SYNC_MODEL
                    if not SYNC_MODEL:
                        dev=Device.objects.filter(area__in=self.attarea.all()).filter(device_type=DEVICE_TIME_RECORDER)
                        sync_delete_user(dev, [self])
                        #from mysite.iclock.models.model_cmmdata import del_user_cmmdata
                        #del_user_cmmdata(self)
            
            self.delete_cache_template_count()#删除模板数目缓存
            self.delete_cache_face_count()#删除面部模板数目缓存
            self.delete_cache_area()
                
            if get_option("VISITOR"):
                from mysite.visitor.models.model_visitor import VisitorManage
                VisitorManage.objects.filter(visitor_pin=self.PIN).delete()
            
            if get_option("IACCESS"):
                from redis_self.server import start_dict_server
                accdev=self.search_accdev_byuser()
                sync_delete_user(accdev, [self])
                
                d_server = start_dict_server()
                d_server.set_key("EMP_CHANGED", 1)#通知实时监控重新获取人员-darcy20111027
                d_server.close()            
            
            if "mysite.meeting" in settings.INSTALLED_APPS:
                from mysite.meeting.models.meeting_emp import MeetingEmp
                MeetingEmp.objects.filter(user__PIN = self.PIN).delete()

            if get_option("POS") and not Init_db:#带消费的情况下防止删除人员的时候做级联删除，导致消费记录丢失，消费记录出现人员编号跟部门为空的现象
                from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
                self.status = STATUS_INVALID
                super(Employee, self).save()
            else:
                super(Employee, self).delete()
            #print"####end delete emp"
        @staticmethod
        def clear():
            import time
            Employee.can_restore=True
            try:
                for e in Employee.all_objects.all():
                    e.delete(Init_db=True)
                    time.sleep(0.1)
            finally:
                Employee.can_restore=False

        def data_valid(self, sendtype):
            is_new = False#是否新增
            if self.pk == None:
               is_new = True
               
            import re
            p_text = r'^[0-9]+$'
            if settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT"): 
                p_text = r'^[0-9a-zA-Z]+$'
            p =  re.compile(p_text)
            if not p.match(self.PIN):
                if settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT"):
                    raise Exception(_(u'人员编号只能为数字或字母  '))
                else:
                    raise Exception(_(u'人员编号只能为数字'))
            if re.compile(r"^0+$").match(self.PIN):
                raise Exception(_(u'人员编号不能为0'))
            
            if len(self.PIN) > settings.PIN_WIDTH:
                raise Exception(_(u'%(f)s 人员编号长度不能超过%(ff)s位') % {"f":self.PIN, "ff":settings.PIN_WIDTH})
            self.PIN = format_pin(self.PIN)

            tmp = Employee.all_objects.filter(PIN__exact=self.PIN)
            if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                raise Exception(_(u'人员编号: %s 已存在') % self.PIN)
            
            if self.identitycard:
                self.__class__.can_restore=True
                emp_obj = Employee.objects.filter(identitycard__exact=self.identitycard)
                tmpid = emp_obj.filter(isblacklist__exact=1)
                self.__class__.can_restore=False
                if len(tmpid) > 0 :
                    raise Exception(_(u'%s 已存在黑名单中！') % self.identitycard)
                if len(emp_obj) > 0 and emp_obj[0].id != self.id :   #编辑状态
                    raise Exception(_(u'%s 身份证号码已被登记！') % self.identitycard)
                

            if self.set_valid_time == True:
                if not self.acc_startdate or not self.acc_enddate:
                    raise Exception(_(u'您已选择设置门禁有效时间,请填写开始日期和结束日期'))
                if self.acc_startdate > self.acc_enddate:
                    raise Exception(_(u'门禁有效时间的开始日期不能大于结束日期'))
#            else:
#                if self.acc_startdate or self.acc_enddate:
#                    raise Exception(_(u'您已填写开始日期或结束日期,请勾选设置门禁有效时间'))

            if self.Password:
                if get_option("IACCESS"):
                    from mysite.iaccess.models import AccDoor
                    doors = AccDoor.objects.all()#系统里所有的，不需要权限过滤
                    force_pwd_existed = [d.force_pwd for d in doors]#[int(d.force_pwd) for d in doors if d.force_pwd]
                    from base.crypt import encryption
                    #由于胁迫密码已经加密，须将人员密码加密后再进行比较
                    if self.Password in force_pwd_existed or encryption(self.Password) in force_pwd_existed:#不含‘’
                        raise Exception(_(u"人员密码不能与任意门禁胁迫密码相同"))
                p = re.compile(r'^[0-9]+$')
                if not self.pk:#新增时
                    if not p.match(self.Password):
                        raise Exception(_(u"人员密码必须为整数"))
                else:
                    emp = Employee.objects.filter(pk=self.pk)
                    if emp[0].Password == self.Password and not emp[0].Password.isdigit():
                        pass    
                    elif not p.match(self.Password):
                        raise Exception(_(u"人员密码必须为整数"))
        
            if self.Birthday and self.Birthday>datetime.datetime.now().date():
                raise Exception(_(u"生日日期错误"))
            tmpre = re.compile('^[0-9]+$')
            email = re.compile('^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$')
            if self.email and not email.search(self.email):
                raise Exception(_(u'邮箱格式不正确'))
            if self.Mobile and not tmpre.search(self.Mobile):
                raise Exception(_(u'手机号码格式不正确'))

        def save(self, **args):
            try:
#                try:
#                   self.PIN = str(int(self.PIN))
#                except:
#                   raise Exception(_(u'人员编号只能为数字'))
#                if int(self.PIN) == 0:
#                    raise Exception(_(u'人员编号不能为0'))


                import re
                p_text = r'^[0-9]+$'
                if settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT"): 
                    p_text = r'^[0-9a-zA-Z]+$'
                p =  re.compile(p_text)
                if not p.match(self.PIN):
                    if settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT"):
                        raise Exception(_(u'人员编号只能为数字或字母  '))
                    else:
                        raise Exception(_(u'人员编号只能为数字'))
                if re.compile(r"^0+$").match(self.PIN):
                    raise Exception(_(u'人员编号不能为0'))
#                import re
#                tmpre = re.compile('^[0-9]+$')
#                orgcard = self.using_card
#                if self.using_card and not tmpre.search(orgcard):
#                    raise Exception(_(u'卡号不正确'))
#                if self.using_card:
#                    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP
#                    try:
#                        tmpcard = IssueCard.objects.get(cardno=self.using_card)
#                    except:
#                        tmpcard = None
#                    if tmpcard and tmpcard.UserID!= self:#用于前端表单验证
#                        raise Exception(_(u'卡号已使用，如果确认将重新发卡，请卡原持卡人 %s 进行退卡操作') % tmpcard)
                    
                self.PIN = format_pin(self.PIN)
                
                tmp = Employee.all_objects.filter(PIN__exact=self.PIN)
                
                if len(tmp) > 0 and tmp[0].id != self.id:   #编辑状态
                    raise Exception(_(u'人员编号: %s 已存在') % self.PIN)
                #对密码进行加密
                if self.Password!="" or None:
                    if len(tmp) !=0:
                        if tmp[0].Password == self.Password:
                            pass
                        else:
                            self.Password = encryption(self.Password)
                    else:
                        self.Password = encryption(self.Password)
                installed_apps = settings.INSTALLED_APPS
                super(Employee, self).save(**args)
                from base.sync_api import SYNC_MODEL
                if not SYNC_MODEL:
                    if get_option("ATT") and (len(tmp)==0 or (tmp and tmp[0].Card!=self.Card)):#zkeco+zktime
                        from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                        adj_user_cmmdata(self, [], self.attarea.all())
                        #sync_set_user(self.search_device_byuser(), [self])
                
            except Exception, e:
                    import traceback; traceback.print_exc();
                    raise e
            str_area = u",".join([a.areaname for a in self.attarea.all()])
            self.cache_area(str_area)

        def pin(self):
                return device_pin(self.PIN)

        def get_level_count(self):
            if get_option("IACCESS"):#仅适用于门禁，其他子系统pass且前端不显示
                return self.acclevelset_set.count()
            else:
                pass

        def fp_count(self):
                return models.get_model("iclock", "fptemp").objects.filter(UserID=self).count()

        def __unicode__(self):
                return u"%s %s"%(self.PIN ,self.EName  or "")
                
        class dataimport(ModelOperation):
            help_text = _(u"导入数据") #导入
            verbose_name = _(u"导入")
            def action(self):
                from django.db import connection
                from dbapp.import_data import ImportData
                if 'postgresql_psycopg2' in connection.__module__:
                    badgenumber_key = '"'+"badgenumber"+'"'
                    defaultdeptid_key = '"'+"defaultdeptid"+'"'
                else:
                    badgenumber_key = "badgenumber"
                    defaultdeptid_key = "defaultdeptid"
                class ImportEmpData(ImportData):
                    def __init__(self,req,input_name = "import_data"):
                        super(ImportEmpData, self).__init__(req,input_name)
                        self.calculate_fields_verbose = [u"%s"%_(u"部门编号"),u"%s"%_(u"卡号")]
                        self.must_fields = [
                            u"%s"%_(u"部门编号"),
                            u"%s"%_(u"人员编号"),
                            u"%s"%_(u"姓名"),
                        ]
                        self.card_head = [ u"%s"%_(u"人员编号"),u"%s"%_(u"卡号"),"user_pk" ]#卡管理导入头,user_pk用来初始化的
                        self.card_records = [ ]#卡记录
                    
                    def records_analysis(self, record_dict):
                        u"分析哪些是应该插入的数据，哪些应该是更新的数据"
                        records = record_dict["sql_list"]
                        UPDATE_SQL = record_dict["UPDATE_SQL"]
                        model_table = record_dict["model_table"]
                        update_old_record = record_dict["update_old_record"]
                        #print '------update_old_record=', update_old_record
                        update_records = []
                        insert_records = []
                        update_multi_params = []
                        update_params = []
                        pins = []
                        count = 0 
                        temp_records = []
                        global emp_update_list
                        global emp_insert_list
                        for record in records:#格式：[{},{}]
                            pins.append(record[badgenumber_key]) #由于已经构造好了为"'%s'"
                            temp_records.append( record )
                            count = count + 1
                            if count > 100:
                                if get_option("POS"):
                                    exists_pins = list(Employee.all_objects.filter(PIN__in=pins).values_list("PIN",flat=True))
                                else:
                                    exists_pins = list(Employee.objects.filter(PIN__in=pins).values_list("PIN",flat=True))
                                for elem in temp_records:
                                    badgenumber = elem[badgenumber_key]
                                    if  badgenumber not in exists_pins:
                                        insert_records.append(elem)
                                        emp_insert_list.append(elem[badgenumber_key])   
                                    elif update_old_record:
                                        #print '---------update--old---'
                                        set_key = [k+'=%s' for k in elem.keys()]
                                        update_sql = UPDATE_SQL%{
                                            "table":model_table,
                                            "fields_value":",".join(set_key),
                                            "condition":"badgenumber=%s"
                                        }
                                        #print '-------1------update_sql==', update_sql
                                        update_records.append(update_sql)
                                        param = [v for v in elem.values()]
                                        param.append(elem[badgenumber_key])
                                        update_params += param
                                        update_multi_params.append(param)
                                        emp_update_list.append(elem[badgenumber_key])   
#                                            #---------------------#
#                                            set_kvs = [ u"%(k)s=%(v)s"%{"k":k,"v":v} for k,v in elem.items() ]
#                                            update_records.append(UPDATE_SQL%{
#                                                "table":model_table,
#                                                "fields_value":",".join(set_kvs),
#                                                "condition":"badgenumber = %s"%elem["badgenumber"]
#                                            })
                                temp_records = []
                                pins = []
                                count =0
                        if pins:
                            if get_option("POS"):
                                exists_pins = list(Employee.all_objects.filter(PIN__in=pins).values_list("PIN",flat=True))
                            else:
                                exists_pins = list(Employee.objects.filter(PIN__in=pins).values_list("PIN",flat=True))
                            for elem in temp_records:
                                badgenumber = elem[badgenumber_key]
                                if  badgenumber not in exists_pins:
                                    insert_records.append(elem)
                                    emp_insert_list.append(elem[badgenumber_key])  
                                elif update_old_record:
                                    #print '--------update---old----'
                                    set_key = [k+'=%s' for k in elem.keys()]
                                    update_sql = UPDATE_SQL%{
                                        "table":model_table,
                                        "fields_value":",".join(set_key),
                                        "condition":"badgenumber=%s"
                                    }
                                    #print '-------------update_sql==', update_sql
                                    update_records.append(update_sql)
                                    param = [v for v in elem.values()]
                                    param.append(elem[badgenumber_key])
                                    update_params += param
                                    update_multi_params.append(param)
                                    emp_update_list.append(elem[badgenumber_key])  
#                                        set_kvs = [ u"%(k)s=%(v)s"%{"k":k,"v":v} for k,v in elem.items() ]
#                                        update_records.append(UPDATE_SQL%{
#                                           "table":model_table,
#                                           "fields_value":",".join(set_kvs),
#                                           "condition":"badgenumber = %s"%elem["badgenumber"] 
#                                        })
                               
                        record_dict["insert_records"] = insert_records
                        record_dict["update_records"] = [update_records, update_params, update_multi_params]
                        #print "---------update_records==", record_dict["update_records"]
                        #print "---------insert_records==", record_dict["insert_records"] 
                        update_records = []
                        insert_records = []
                        update_multi_params = []
                        update_params = []
                        pins = []

                        
                    def after_insert(self):
                        u"插入后,提供给特殊处理,导入人员卡号"
                        if self.card_records:
                            from mysite.personnel.card_import  import ImportCardData
                            obj_import = ImportCardData()
                            obj_import.head = self.card_head
                            obj_import.records = self.card_records
                            obj_import.mapping_model()
                            obj_import.exe_import_data()
                            ret_error = obj_import.error_info
                            self.error_info = ret_error
                            
                        global emp_update_list
                        global emp_insert_list
 #                        将人员保存到redis中,并管理缓存
                        from base.sync_api import update_emp
                        from base.cached_model import cache_key
                        if emp_update_list:
                            cnt = 900
                            lens = len(emp_update_list)
                            times = lens%cnt ==0 and lens/cnt or (lens/cnt +1)
                            for i in range(times):
                                eul = emp_update_list[i*cnt:(i+1)*cnt]
                                emps = Employee.objects.filter(PIN__in=eul)
                                for emp in emps:
                                    key = cache_key(emp,emp.pk)
                                    cache.delete(key)
                                    update_emp(emp)
                        if emp_insert_list:
                            cnt = 900
                            lens = len(emp_insert_list)
                            times = lens%cnt ==0 and lens/cnt or (lens/cnt +1)
                            for i in range(times):
                                eul = emp_insert_list[i*cnt:(i+1)*cnt]
                                emps = Employee.objects.filter(PIN__in=eul)
                                for emp in emps:
                                    update_emp(emp)
                        emp_update_list = []
                        emp_insert_list = []
                        return True
                            
                        
                    def process_row(self,row_data,calculate_dict):
                        u'''
                            特殊情况给开发人员提供的接口
                            row_data 这一行的数据
                            calculate_dict 文档附加的列，如部门编号，
                            员工表是没有部门编号的，部门编号是用来初始化员工字段DeptID的
                        '''
                        from mysite.personnel.models import Department
                        #print "calculate_dict:",calculate_dict,"\n"
                        key = u"%s"%_(u"部门编号")
                        dept_code = u"%s"%calculate_dict[key]
                        
                        try:
                            obj_dept = Department.objects.get(code = dept_code.strip())
                        except:
                            #判断是使用默认还是创建新的部门
                            obj_dept = Department()
                            obj_dept.code = u"%s"%dept_code
                            obj_dept.name = u"%s"%dept_code
                            obj_dept.parent_id = 1
                            obj_dept.save()
                        
                        emp_pin = format_pin(row_data[badgenumber_key])
                        row_data[defaultdeptid_key] = u'%s'%obj_dept.pk #初始化部门
                        row_data[badgenumber_key] =u'%s'%emp_pin#格式化PIN
                        
                        card_key = u"%s"%_(u"卡号")
                        if calculate_dict.has_key(card_key):
                            card_value = calculate_dict[ card_key ]
                            #第一列为员工工号，第二列为卡号，第三列为员工记录PK(在卡号插入前初始化)
                            card_record = [ emp_pin,card_value,'' ] 
                            if card_value:
                                self.card_records.append( card_record ) #卡记录
                        #print row_data
                        return row_data

                obj_import = ImportEmpData(req = self.request,input_name = "import_data")
                obj_import.exe_import_data()
                ret_error = obj_import.error_info
                if ret_error:
                    import traceback
                    traceback.extract_stack()
                    raise Exception(u"%(ret)s"%{
                                "ret":";".join(ret_error)
                          })


        class OpLeave(Operation): #定义一个操作，必须继承 base.operation.Operation
                help_text = _(u"""对员工进行离职操作""")
                verbose_name = _(u'离职')                               #在页面上显示该操作的名称
                params = [
                ('leavedate', models.DateField(verbose_name=_(u'离职日期'))),
                ('leavetype', models.IntegerField(verbose_name=_(u'离职类型'), choices=LEAVETYPE)),
                ('reason', models.CharField(verbose_name=_(u'离职原因'),null=True,blank=True)),
                ('isReturnTools', models.BooleanField(verbose_name=_(u'是否归还工具'), choices=YESORNO)),
                ('isReturnClothes', models.BooleanField(verbose_name=_(u'是否归还工衣'), choices=YESORNO)),
#                ('isReturnCard', models.BooleanField(verbose_name=_(u'是否归还卡'), choices=YESORNO)),
                ('isblacklist', models.BooleanField(verbose_name=_(u'是否黑名单'), choices=YESORNO, default=0)),
                ]
                def __init__(self,obj):
                    super(Employee.OpLeave, self).__init__(obj)
                    installed_apps = settings.INSTALLED_APPS
                    if not get_option("POS"):#zkeco
                        self.params.append(('isReturnCard', models.BooleanField(verbose_name=_(u'是否归还卡'), choices=YESORNO)))
                    if get_option("ATT"):
                        self.params.append(('closeAtt', models.BooleanField(verbose_name=_(u'立即关闭考勤'), default=True)))
                    if get_option("IACCESS"):#zkeco+iaccess
                        self.params.append(('closeAcc', models.BooleanField(verbose_name=_(u'立即关闭门禁'), default=True)))
                    if get_option("POS"):#zkeco+POS
                        self.params.append(('is_close_pos', models.BooleanField(verbose_name=_(u'立即关闭消费'), default=True)))
                    
                def action(self, leavedate, leavetype,
                    reason, isReturnTools, isReturnClothes,isblacklist,closeAtt=False, is_close_pos=False,closeAcc=False,isReturnCard = 0 ):                                #定义实际进行操作的函数
                    #from mysite.personnel.models.model_leave import Leave
                    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_OVERDUE
                    iscard = IssueCard.objects.filter(UserID=self.object,cardstatus__in = [CARD_VALID,CARD_OVERDUE])
                    self.object.isblacklist = isblacklist
                    self.object.status = STATUS_LEAVE
                    if not get_option("POS"):
                        if  isReturnCard==1 and iscard:
                            for e in iscard:e.delete()
                    self.object.save()
                    Leave = self.object.__class__.leavelog_set.related.model
                    t = Leave()
                    t.UserID = self.object
                    t.leavedate = leavedate
                    t.leavetype = leavetype
                    t.reason = reason
                    t.isReturnTools = isReturnTools
                    t.isReturnClothes = isReturnClothes
                    if not get_option("POS"):
                        t.isReturnCard = isReturnCard
                    t.save()
                    if closeAtt:
                            t.OpCloseAtt(t).action()
                    if closeAcc:
                            t.OpCloseAccess(t).action()
                    if is_close_pos:
                            t.OpClosePos(t).action()
                    
                def can_action(self):                                         #定义一个对象是否能够进行该操作
                        return self.object.status in (STATUS_OK, STATUS_PAUSED)
#        class _clear(ModelOperation):
#                visible=False
#                help_text=_(u"清空人员") #删除选定的记录
#                verbose_name=u"清空人员"
#                def action(self):
#                    pass
        class OpSyncToDevice(Operation):
            u"同步人员到其所在区域的设备中"
            help_text = _(u"同步人员到其所在区域的设备中")
            verbose_name = _(u"重新同步到设备")
            visible = True
            def action(self):
                from base.sync_api import SYNC_MODEL
                if SYNC_MODEL:
                    from base.sync_api import spread_emp
                    spread_emp(self.object)
                else:
                    from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                    adj_user_cmmdata(self.object, [], self.object.attarea.all())

        class OpAdjustDept(Operation): #调整部门
                help_text = _(u'''调整部门''')
                verbose_name = _(u"调整部门")
                params = (
                        ('department', DeptForeignKey(verbose_name=_(u'调整到的部门'))),
#                        ('position', PositionForeignKey(verbose_name=_(u'调整后的职位'))),
                        ('changereason',models.CharField(max_length=200,verbose_name=_(u'调动原因'),null=True,blank=True,editable=True)),
                        ('remark',models.CharField(verbose_name=_(u'备注'),editable=True,null=True,blank=True,max_length=200)),
                )
                def action(self, department,changereason,remark):
                        empchange = self.object.__class__.empchange_set.related.model()
                        empchange.UserID = self.object
                        empchange.changepostion = 1
                        empchange.changereason=changereason#部门调整 加入原因 by ycm 2011-06-11
                        empchange.remark=remark
                        empchange.oldvalue = get_pk(self.object.DeptID)
                        empchange.newvalue = get_pk(department)
                        empchange.save()
#                        self.object.DeptID=department
#                        self.object.save()

        class OpDelLevelFromEmp(Operation):
           verbose_name = _(u"删除所属权限组")
           def action(self):
                pass

        class OpAddLevelToEmp(Operation):
            verbose_name = _(u"添加所属权限组")
            help_text = _(u'''添加人员所属权限组，一个人可以属于多个权限组。''')
            def action(self):
                from mysite.iclock.models.dev_comm_operate import sync_set_user, sync_set_user_privilege,sync_delete_user_privilege,sync_delete_user_finger,sync_set_acc_user
                from mysite.iaccess.models import AccLevelSet
                emp_obj = self.object#当前要操作的对象（人）
                levels = self.request.POST.getlist("level")#新增的权限组（跟旧权限组肯定不重复）
                devset = []
#                print '----levels=',levels
                for level in levels:#以权限组为中心，循环权限组--当前新增权限组要处理的设备，其他的设备并不需要处理，所以共用一个dev即可。
                    obj = AccLevelSet.objects.get(pk=int(level))
                    obj.emp.add(emp_obj.id)
                    for door in obj.door_group.all():
                        devset.append(door.device)
                dev = set(devset) #新权限中的所有设备
#                print '---OpAddLevelToEmp--sync_delete_user_privilege before=',dev
                sync_delete_user_privilege(dev, [emp_obj])
#                print '---OpAddLevelToEmp--sync_set_user before=',dev
                sync_set_user(dev, [emp_obj])
                sync_set_user_privilege(dev, [emp_obj])
        
        class OpCardPrinting(Operation):
            verbose_name = _(u"制卡")
            help_text = _(u'''制卡，将通过卡打印机制卡。''')
            visible = False
            def action(self):
                raise Exception(_(u"制卡成功！"))

        class OpAdjustArea(Operation):
                verbose_name = _(u"调整区域")
                help_text = _(u"调整区域:将会把该人员所属原区域内的设备清除掉该人员，并自动下发到新区域内的所有设备中")
                params = (
                        ('area', AreaManyToManyField(Area, verbose_name=_(u'调整到的区域'))),
                        ('changereason',models.CharField(max_length=200,verbose_name=_(u'调动原因'),null=True,blank=True,editable=True)),
                        ('remark',models.CharField(verbose_name=_(u'备注'),editable=True,null=True,blank=True,max_length=200)),
                )
                def action(self, area,changereason):
                        #print "UserID :%s " % self.object
                        oldObj = self.object
                       
                        #devs=oldObj.search_device_byuser()
                        #sync_delete_user(devs, oldObj)
                        #sync_delete_user_fingerprint(devs, oldObj)
                        import copy
                        oldarea = copy.deepcopy(oldObj.attarea.all())
                        empchange = self.object.__class__.empchange_set.related.model()
                        empchange.UserID = self.object
                        empchange.changepostion = 4
#                        print empchange
#                        print 'changereason',changereason
                        empchange.changereason=changereason #区域调整 加入原因 这里添加无效
                        empchange.oldvalue = ",".join(["%s" % i.pk for i in  self.object.attarea.all()])
                        #print "empchange.oldvalue:%s" % empchange.oldvalue
                        empchange.newvalue = ",".join(["%s" % i.pk for i in  area])
                        empchange.changedate = datetime.datetime.now()
                        empchange.save(log_msg=False, force_insert=True)

                        self.object.attarea = area
                        self.object.save(log_msg=False)
                        #新增下载人员信息
                        newObj = self.object
                        #sync_set_user(newObj.search_device_byuser(), newObj)
                        #sync_set_user_fingerprint(newObj.search_device_byuser(), [newObj])
                        from base.sync_api import SYNC_MODEL
                        if not SYNC_MODEL:
                            from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                            adj_user_cmmdata(self.object, Area.objects.filter(pk__in=oldarea), area)

                def action_batch(self, area,changereason,remark):
                        #print "UserID :%s " % self.object
                        from mysite.iclock.models.model_device import Device
                        from mysite.iclock.models.model_device import DEVICE_TIME_RECORDER
                        from base.sync_api import SYNC_MODEL
                        if not SYNC_MODEL:
                            from mysite.iclock.models.model_cmmdata import adj_user_cmmdata, save_userarea_together
                        datalist = []
                        for oldObj in self.object:
                            empchange = oldObj.__class__.empchange_set.related.model()
                            empchange.changepostion = 4
                            empchange.changereason=changereason #加入调整区域加入原因 by ycm 2011-06-10
                            empchange.remark=remark
                            empchange.newvalue = ",".join(["%s" % i.pk for i in  area])
                            empchange.newids = [i.pk for i in area]
                            empchange.changedate = datetime.datetime.now()
                            new_devs = None
                            import copy

                            old_attarea = copy.deepcopy(oldObj.attarea.select_related())
                            devs = set(list(Device.objects.filter(area__in=old_attarea).filter(device_type=DEVICE_TIME_RECORDER)))    #只管理考勤
                            empchange.oldvalue = ",".join(["%s" % i.pk for i in old_attarea])
                            #print "empchange.oldvalue:%s" % empchange.oldvalue
                            empchange.UserID = oldObj
                            empchange.changeno = None
                            empchange.save()
                            oldObj.attarea = area
                            oldObj.save(log_msg=False)
                            if not SYNC_MODEL:
                                if new_devs is None:
                                    new_devs = set(list(oldObj.search_device_byuser()))
                                #新增下载人员信息
    
                                #sync_delete_user(list(devs-new_devs), [oldObj])
                                #sync_set_user(list(new_devs-devs), [oldObj])
                                #print "old_attarea:%s" % old_attarea
                                #print "area:%s" % area
                                datalist.append(adj_user_cmmdata([oldObj], old_attarea, area, True))
                        if not SYNC_MODEL:
                            save_userarea_together(self.object, area, datalist)
        class OpUploadPhoto(Operation):
                help_text = _(u'''设置用户照片''')
                verbose_name = _(u"设置用户照片")
                only_one_object = True
                params = (
                        ('fileUpload', models.ImageField(verbose_name=_(u'选择个人照片'), blank=True, null=True)),
                )
                def action(self, fileUpload):
                    #from   mysite import settings
                    #photopath = settings.ADDITION_FILE_ROOT + "photo/"

                    #fname = self.object.PIN + ".jpg"
                    #saveUploadImage(self.request, fname)
                    #self.object.photo = "/file/photo/" + fname
                    import datetime
                    if self.request.FILES:
                        f=self.request.FILES['fileUpload']
                        f_format=str(f).split('.')
                        format_list=['jpg','gif','png','bmp']
                        try:
                           format_list.index(str(f_format[1].lower()))
                        except:
                           raise Exception (_(u"图片格式无效！"))
                        data = f.read()
                        size = len(data)
                        print size
                        if size>16*1024:
                            raise Exception(_(u"人员照片大小不能超过16Kb"))
                        from base.sync_api import SYNC_MODEL,update_emp_pic,EN_EMP_PIC
                        if SYNC_MODEL and EN_EMP_PIC:
                            update_emp_pic(self.object.PIN, data)
                        else:
                            self.object.photo.save(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")+".jpg",f)
                    else:
                        raise Exception(_(u"请选择文件!"))

        class OpIssueCard(Operation):
                verbose_name = _(u"人员发卡")
                help_text = _(u"目前支持手动输入卡号以及使用发卡器发卡！")
                only_one_object = True
                visible = False
                params = (
                        ('card', models.CharField(verbose_name=_(u'人员发卡'))),
                )
                def action(self, card):
                    from mysite.iclock.models.dev_comm_operate import sync_set_acc_user
                    if card != "":

                        import re
                        tmp = re.compile('^[0-9]+$')
                        if not tmp.search(card):
                            raise Exception(_(u'卡号不正确'))
                        card=int(card)
                        tmpcard = Employee.objects.filter(Card=card)
                        if tmpcard:
                            #raise Exception(_(u'卡号已存在，如果确认将重新发卡，请先清除该卡原持卡人 %s' % tmpcard[0]))
                            raise Exception(_(u'卡号已存在，如果确认将重新发卡，请先清除该卡原持卡人 %s') % tmpcard[0])

                        self.object.Card = card
                        self.object.save()
#                        issuecard=self.object.__class__.issuecard_set.related.model()
#                        issuecard.UserID=self.object
#                        issuecard.cardno=card
#                        issuecard.issuedate=datetime.datetime.now().strftime("%Y-%m-%d")
#                        issuecard.save()
                        if "mysite.iaccess" in settings.INSTALLED_APPS:
                            sync_set_acc_user(self.object.search_accdev_byuser(), [self.object])

#
        class OpRegisterFinger(Operation):
               verbose_name = _(u"登记指纹")
               help_text = _(u"指纹登记需要指纹仪驱动，如果您未安装驱动，请先下载驱动程序！")
               only_one_object = True

               params = (
                   ('tfcount', models.CharField(verbose_name=_(u'模版数量'), max_length=10, blank=True, null=True)),
                   ('tfids', models.CharField(verbose_name=_(u'手指编号'), max_length=20, blank=True, null=True)),
                   ('tfcount10', models.CharField(verbose_name=_(u'模版数量'), max_length=10, blank=True, null=True)),
                   ('tfids10', models.CharField(verbose_name=_(u'手指编号'), max_length=20, blank=True, null=True)),
                   ('fpcode', models.CharField(verbose_name=_(u'手指类型'), max_length=20, blank=True, null=True)),
                   ('tlng', models.CharField(verbose_name=_(u'当前语言'), max_length=10, blank=True, null=True)),

               )
               def __init__(self, obj):
                   from mysite.iclock.models.model_bio import Template
                   super(Employee.OpRegisterFinger, self).__init__(obj)
                   t9 = Template.objects.filter(UserID=obj.PIN, Fpversion=9)
                   t10 = Template.objects.filter(UserID=obj.PIN, Fpversion=10)
                   tcount = 0#当前人员的指纹模板数量
                   tfingerid = ""
                   #if len(t) > 0:
                   if len(t10)>0 and len(t10)>=len(t9):
                       tcount = len(t10)
                       tfingerid = ",".join(["%s" % i.FingerID for i  in t10])
                       fptypecode = ",".join(["%s" % i.Valid for i in t10])    # 指纹类型代码
                   else:
                       tcount = len(t9)
                       tfingerid = ",".join(["%s" % i.FingerID for i  in t9])  
                       fptypecode = ",".join(["%s" % i.Valid for i in t9])    # 指纹类型代码

                   params = dict(self.params)

                   tfcount = params['tfcount']
                   tfcount.label = _(u'模版数量')
                   tfcount.default = tcount
                   params['tfcount'] = tfcount

                   tfids = params['tfids']
                   tfids.label = _(u'手指编号')
                   tfids.default = tfingerid
                   params['tfids'] = tfids
                   
                   fpcode = params['fpcode']
                   fpcode.label = _(u'手指类型')
                   fpcode.default = fptypecode
                   params['fpcode'] = fpcode

                   from base.models import options
                   from mysite import settings
                   lng = options['base.language']
                  
                   tlng = params['tlng']
                   tlng.label = _(u'当前语言')
                   tlng.default = lng
                   params['tlng'] = tlng
                   #t = Template.objects.filter(UserID=obj, Fpversion=10)
                   #tcount10 = 0
                   #tfingerid10 = ""
                   #if len(t) > 0:
                   #    tcount10 = len(t)
                   #    tfingerid10 = ",".join(["%s" % i.FingerID for i  in t])

                   #tfcount = params['tfcount10']
                   #tfcount.label = _(u'模版数量')
                   #tfcount.default = tcount10
                   #params['tfcount10'] = tfcount

                   #tfids = params['tfids10']
                   #tfids.label = _(u'手指编号')
                   #tfids.default = tfingerid10
                   #params['tfids10'] = tfids


                   self.params = tuple(params.items())

               #def action(self, tfcount, tfids, tfcount10, tfids10):
               def action(self, tfcount, tfids, tfcount10, tfids10, fpcode, tlng):
                   from mysite.iclock.models.dev_comm_operate import  sync_set_user_fingerprint,sync_set_acc_user_fingerprint
                   if self.request:
                       save_finnger(self.request, self.object)
                       from base.sync_api import SYNC_MODEL
                       if not SYNC_MODEL:
                           att_devs = self.object.search_device_byuser()
                           if att_devs:
                               sync_set_user_fingerprint(att_devs, [self.object])
                       try:
                           acc_devs = self.object.search_accdev_byuser()
                       except:
                           acc_devs = None
                       if acc_devs:
                           sync_set_acc_user_fingerprint(acc_devs, [self.object])
                       del_finnger(self.request, self.object)


        class OpPositionChange(Operation):
                help_text = _(u'''职位调动''')
                verbose_name = _(u"职位调动")
                params = (
                        ('department', DeptForeignKey(verbose_name=_(u'职位所属部门'))),                        
                        ('position', PositionForeignKey(verbose_name=_(u'调整后的职位'))),
                        ('changereason',models.CharField(max_length=200,verbose_name=_(u'调动原因'),null=True,blank=True,editable=True)),
                        ('remark',models.CharField(verbose_name=_(u'备注'),editable=True,null=True,blank=True,max_length=200)), 
                                )
                def action(self, department,position,changereason,remark):
                    if position:
                        empchange = self.object.__class__.empchange_set.related.model()
                        empchange.UserID = self.object

                        empchange.changepostion = 2
                        empchange.changereason=changereason  #by 2011-0611 ycm 
                        empchange.remark=remark
                        empchange.oldvalue = get_pk(self.object.position)
                        empchange.newvalue = get_pk(position)
                        empchange.save()

#                        self.object.Position = position
#                        self.object.DeptID = position.DeptID
#                        self.object.save()
        class OpEmpType(Operation):
                help_text = _(u'''员工转正''')
                verbose_name = _(u"员工转正")
                params = (
                        ('emptype', models.IntegerField(verbose_name=_(u'员工转正'), choices=EMPTYPE)),
                        ('changereason',models.CharField(max_length=200,verbose_name=_(u'调动原因'),null=True,blank=True,editable=True)),
                        ('remark',models.CharField(verbose_name=_(u'备注'),editable=True,null=True,blank=True,max_length=200)), 
                                )
                def action(self, emptype,changereason,remark):
                        if emptype:
                                empchange = self.object.__class__.empchange_set.related.model()
                                empchange.UserID = self.object
                                empchange.changepostion = 3
                                empchange.changereason=changereason# by20110611 ycm
                                empchange.remark=remark
                                empchange.oldvalue = self.object.emptype
                                empchange.newvalue = emptype
                                empchange.save()
#                                self.object.hiretype = 1     #转正后的雇佣类型不做修改  zyg 2011-12-02
                                self.object.emptype = emptype
                                self.object.save()

        #数据中心处理接口
        def check_accprivilege(self):
            from mysite.iaccess.models import AccLevelSet
            try:
                if self.acclevelset_set.all():
                    return True
                else:
                    return False
            except:
                return False
        def search_device_byuser(self): #考勤用
            from mysite.iclock.models import Device
            from mysite.iclock.models.model_device import DEVICE_TIME_RECORDER
            return Device.objects.filter(area__in=self.attarea.select_related()).filter(device_type=DEVICE_TIME_RECORDER)

        def search_accdev_byuser(self, acd=False):#默认获取门禁控制器，acd为True时获取一体机
            from mysite.iclock.models.model_device import Device, DEVICE_ACCESS_CONTROL_PANEL
            from mysite.personnel.sql import search_accdev_byuser_sql
            sql =search_accdev_byuser_sql(self.id)
            #print "search_accdev_byuser sql=", sql
            fet = []
            try:
                cursor = connection.cursor()
                cursor.execute(sql)
                fet = set(cursor.fetchall())
            except:
                pass
            dev = []
            ss = [dev.append(int(f[0])) for f in fet]
            #print dev
            devs_obj = Device.objects.filter(id__in=dev).filter(device_type=DEVICE_ACCESS_CONTROL_PANEL)
            acds_obj = []
            if acd:
               for d in devs_obj:
                   if d.accdevice and d.accdevice.machine_type==12:
                       acds_obj.append(d)
               return acds_obj
            return devs_obj
        

        def get_attarea(self):
            return self.get_cache_area()
            #return u",".join([a.areaname for a in self.attarea.all()])

        def get_template(self):
            verbose_name = _(u"指纹模板")
            from base.sync_api import SYNC_MODEL
            from base.sync_api import get_emp_fp_count
            if SYNC_MODEL:
                m_list = get_emp_fp_count(self.PIN)
                strl = [ u'%s.0:有'%e for e in m_list]
                if strl:
                    return ';'.join(strl)
                else:
                   return u"无"
            else:
                from mysite.iclock.models import Template
                from mysite.personnel.cache import PERSONNEL_EMP_T_COUNT,TIMEOUT
                cache_key=PERSONNEL_EMP_T_COUNT+str(self.pk)
                cache_t=cache.get(cache_key)
                if cache_t:
                    return _(u"9.0指纹数:%(f)s ; 10.0指纹数:%(f1)s") % {'f':cache_t["9"], 'f1':cache_t["10"]}
                
                t9 = Template.objects.filter(UserID=self, Fpversion="9").count()
                t10 = Template.objects.filter(UserID=self, Fpversion="10").count()
                cache.set(cache_key,{"9":t9,"10":t10},TIMEOUT)
                return _(u"9.0指纹数:%(f)s ; 10.0指纹数:%(f1)s") % {'f':t9, 'f1':t10}
            
        def get_dept_name(self):
            u'''从缓存中得到部门的Name'''
            from mysite.personnel.models import Department
            dept_name=""
            try:
                dept_obj=Department.objects.get(id=self.DeptID_id)
                dept_name=dept_obj.name
            except:
                pass
            return dept_name
        def get_dept_code(self):
            u'''从缓存中得到部门的code'''
            from mysite.personnel.models import Department
            dept_code=""
            try:
                dept_obj=Department.objects.get(id=self.DeptID_id)
                dept_code=dept_obj.code
            except:
                pass
            return dept_code
        
        def get_face(self):
#            u'''获取人脸数'''
            verbose_name = _(u"面部模板")
            from base.sync_api import SYNC_MODEL
            from base.sync_api import get_emp_face_count
            if SYNC_MODEL:
                m_list = get_emp_face_count(self.PIN)
                strl = [ u'%s.0:有'%e for e in m_list]
                if strl:
                    return ';'.join(strl)
                else:
                   return u"无"
            else:
                from mysite.iclock.models import FaceTemplate
                face=FaceTemplate.objects.filter(user=self)
                d = {}
                for e in face:
                    face_ver = e.face_ver
                    if face_ver:
                        try:
                            d[face_ver] +=1
                        except:
                            d[face_ver] = 1
                    else:
                        continue
                strl = [ u'%s.0人脸数:%s'%(e,d[e]>=12 and 1 or 0) for e in d.keys()]
                if strl:
                    return ';'.join(strl)
                else:
                   return u"人脸数:0"
        class Admin(CachingModel.Admin):
                from depttree import ZDeptChoiceWidget,ZDeptMultiChoiceWidget
                #把人员浏览权限赋予其他需要此权限的任何地方,来达到一个权限多用的目的
                default_give_perms = ["personnel.browse_issuecard", "att.browse_setuseratt", "att.opaddmanycheckexact_checkexact", "personnel.browse_leavelog", "contenttypes.can_AttDeviceUserManage", "att.browse_empspecday", "personnel.browse_empchange", "contenttypes.can_AttUserOfRun", "contenttypes.can_AttCalculate", "contenttypes.can_EmpLevelSetPage", \
                                    "opaddleveltoemp_employee", "opdellevelfromemp_employee", "personnel.browse_accmorecardempgroup", "iaccess.browse_accfirstopen", "contenttypes.can_EmpLevelSetPage", "iaccess.get_logs"]
                layout_types = ["table", "photo"]
                sort_fields = ["PIN","DeptID.code"]
                photo_path = "photo"#指定图片的路径，如果带了".jpg",就用这个图片，没有带的话就找这个字符串所对应的字段的值
                app_menu = "personnel"
                #api_fields=('PIN','EName','DeptID.code','DeptID.name','Gender','Title','Tele','Mobile')
                list_display = ['PIN', 'EName','Card','DeptID.code', 'DeptID.name', 'position.name', 'Gender','Privilege', 'attarea', 'get_template', 'identitycard','Tele', 'Mobile', 'photo','get_face',]+en_query_hide()
                adv_fields = ['PIN', 'EName', 'DeptID.code', 'DeptID.name', 'position.name', 'country.name',  'state.name',  'city.name', 'Gender',  'identitycard',  'Tele', 'Mobile', 'attarea']+en_query_hide();
                newadded_column = {
                    'DeptID.code':'get_dept_code',
                    'DeptID.name':'get_dept_name',
#                    'CounID.code':'get_coun_code', 
#                    'CounID.name':'get_coun_name',                    
#                    'StateID.code':'get_state_code',
#                    'StateID.name':'get_state_name',
#                    'CityID.code':'get_city_code',
#                    'CityID.name':'get_city_name',
                    'attarea': 'get_attarea',
                    'template': 'get_template', 
                    'level_count': 'get_level_count' ,
                }
                hide_fields = get_option("EMPLOYEE_DISABLE_COLS")
                
                list_filter = ('DeptID', 'Gender',)
                search_fields = ['PIN', 'EName']
                query_fields = ['PIN','EName','DeptID__name']
                query_fields_iaccess = ['PIN', 'EName', 'DeptID__name']#,  'is_visitor'
                help_text = get_option("EMPLOYEE_HELP_TEXT")
                cache = 3600
                menu_index = 3
                import_fields = get_option("EMPLOYEE_IMPORT_FIELDS")
                disabled_perms = get_option("EMPLOYEE_DISABLED_PERMS")
                
                default_widgets = {
                    'MVerifyPass': forms.PasswordInput,
                    'Password': forms.PasswordInput,
                    'DeptID':ZDeptChoiceWidget(attrs={"async_model":"personnel__Department"}),
                    'attarea':ZDeptMultiChoiceWidget(attrs={"async_model":"personnel__Area"}),
                }
                #view_fields=['PIN', 'EName', 'DeptID', 'Gender', 'Card', 'identitycard', 'Mobile']
                api_m2m_display = { "attarea" : "areaname", }
                disabled_perms = ["clear_employee"] + init_settings
                if get_option("ONLY_POS"):
                    hide_perms = ["opaddleveltoemp_employee", "opdellevelfromemp_employee",]+is_att_only()+get_option("EMPLOYEE_HIDE_PERMS")
                else:
                    hide_perms = ["opaddleveltoemp_employee", "opdellevelfromemp_employee",]+is_att_only()
                #select_related_perms = {"browse_employee": "opaddleveltoemp_employee"}
                opt_perm_menu = { "opaddleveltoemp_employee": "iaccess.EmpLevelByEmpPage", "opdellevelfromemp_employee": "iaccess.EmpLevelByEmpPage" }#配置到其他目录下
                report_fields=['National','attarea','UTime','Hiredday','PIN', 'EName', 'DeptID', 'Gender','Privilege', 'attarea',  'identitycard','Tele', 'Mobile','AutoSchPlan']#报表可用字段
                disable_inherit_perms = ["OpCardPrinting","OpIssueCard"]
                #disable_inherit_perms=["View_detail",]去除继承过来的不必要的操作
#                tstart_end_search={
#                    "Hiredday":[_(u"起始聘用日期"),_(u"结束聘用日期")]
#                }#配置时间字段(TimeField,DatetimeField,DateField)可以有起始和结束查找
                #scroll_table=False#列表是否需要滚动
        class Meta:
                app_label = 'personnel'
                db_table = 'userinfo'
                verbose_name = _(u"人员")
                verbose_name_plural = verbose_name
                unique_together = (('PIN',),)

#installed_apps = settings.INSTALLED_APPS #配置完后把这些全部删掉
#if "mysite.iaccess" in installed_apps and "mysite.att" in installed_apps:
#    pass#默认
#elif "mysite.iaccess" in installed_apps:#门禁
#    Employee.Admin.help_text = _(u'人员信息是系统的基本信息，人员编号、部门为必填项<br>门禁控制器仅支持6位密码，超过规定长度后系统将自动截取！')
#elif "mysite.pos" in installed_apps:#消费
#    Employee.Admin.help_text = _(u'人员信息是系统的基本信息，人员编号、部门为必填项')
#    
#else:#考勤
#    Employee.Admin.help_text = _(u'人员信息是系统的基本信息，人员编号、部门为必填项<br>指纹登记需要指纹仪驱动，如果您未安装驱动，请先下载驱动程序！<br>黑白屏考勤机仅支持5位密码，彩屏考勤机支持8位密码，超过规定长度后系统将自动截取！')
#
class EmpForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(EmpForeignKey, self).__init__(Employee, to_field=to_field, **kwargs)
class EmpMultForeignKey(models.ManyToManyField):
        def __init__(self, *args, **kwargs):
                super(EmpMultForeignKey, self).__init__(Employee, *args, **kwargs)
class EmpPoPForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(EmpPoPForeignKey, self).__init__(Employee, to_field=to_field, **kwargs)
class EmpPoPMultForeignKey(models.ManyToManyField):
        def __init__(self, *args, **kwargs):
                super(EmpPoPMultForeignKey, self).__init__(Employee, *args, **kwargs)



def update_dept_widgets():
        from dbapp import widgets
        if EmpForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                from empwidget import ZEmpChoiceWidget, ZMulEmpChoiceWidget, ZMulPopEmpChoiceWidget, ZPopEmpChoiceWidget
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpForeignKey] = ZEmpChoiceWidget
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpMultForeignKey] = ZMulEmpChoiceWidget
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpPoPForeignKey] = ZPopEmpChoiceWidget
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[EmpPoPMultForeignKey] = ZMulPopEmpChoiceWidget

update_dept_widgets()
#from mysite.iclock.models.model_bio import Template

#处理指纹模版/个人照片
def save_finnger(request, newObj):
    from base.sync_api import SYNC_MODEL
    from base.sync_api import update_emp_fp
    try:
        if SYNC_MODEL:
            template = request.REQUEST.get("template", "")
            finger_type = request.REQUEST.get("fptype", "")
            if template:
                m_ver = "9"
                fingger = request.REQUEST.get("finnger", "")
                template = template.split(",")
                fingger = fingger.split(",")
                fin_len = len(fingger)
                if finger_type:
                    finger_type1 = finger_type.split(",")
                else:
                    finger_type = ["1" for i in range(fin_len)]
                for i in range(fin_len):
                    update_emp_fp(newObj.PIN, m_ver, fingger[i], template[i],force = finger_type1[i]=="3" and True or False)  
            template10 = request.REQUEST.get("template10", "")
            if template10:
                m_ver = "10"
                fingger10 = request.REQUEST.get("finnger10", "")
                template10 = template10.split(",")
                fingger10 = fingger10.split(",")
                fin10_len = len(fingger10)
                if finger_type:
                    finger_type = finger_type.split(",")
                else:
                    finger_type = ["1" for i in range(fin10_len)]
                for i in range(fin10_len):
#                    print 'go update_emp_fp10...'
                    update_emp_fp(newObj.PIN, m_ver, fingger10[i], template10[i],force = finger_type[i]=="3" and True or False)
        else:
            from mysite.iclock.models.model_bio import Template
            fingger = request.REQUEST.get("finnger", "")
            template = request.REQUEST.get("template", "")
            finger_type = request.REQUEST.get("fptype", "")
            if finger_type:
                finger_type = finger_type.split(",")
                
            if fingger and template:
                fingger = fingger.split(",")
                template = template.split(",")
                for i in range(len(fingger)):
                    t = Template.objects.filter(UserID=newObj.PIN, FingerID__exact=fingger[i], Fpversion="9")
                    if not t:
                        t = Template()
                    else:
                        t = t[0]
                    t.UserID = newObj.PIN
                    t.Template = template[i]
                    t.FingerID = fingger[i]
                    t.Valid = finger_type[i]
                    t.Fpversion = "9"
                    length=len(t.Template)
                    t.save()
        
            fingger = request.REQUEST.get("finnger10", "")
            template = request.REQUEST.get("template10", "")
            if fingger and template:
                fingger = fingger.split(",")
                template = template.split(",")
                for i in range(len(fingger)):
                    t = Template.objects.filter(UserID=newObj.PIN, FingerID__exact=fingger[i], Fpversion="10")
                    if not t:
                        t = Template()
                    else:
                        t = t[0]
                    t.UserID = newObj.PIN
                    t.Template = template[i]
                    t.FingerID = fingger[i]
                    t.Valid = finger_type[i]
                    t.Fpversion = "10"
                    length=len(t.Template)
                    t.save()
    except:
        import traceback;traceback.print_exc()
def del_fp(emp,o,mb=False):
    from mysite.iclock.models   import Template,Device
    if mb:
        tmp_all=Template.objects.filter(UserID=emp.PIN,FingerID__in=o)
    else:
        tmp_all=Template.objects.filter(UserID=emp.PIN,id__in=o)
    devs=Device.objects.filter(area__in=emp.attarea.all(),device_type=1)
    try:
        for dev in devs:
            for template in tmp_all:
                if dev.Fpversion != template.Fpversion:
                    continue
                if len(template.Template)>0:                            
                    line = "PIN=%s\tFID=%d"%(device_pin(emp.PIN), template.FingerID)
                    CMD="DATA DEL_FP %s"%(line)
                    dev.appendcmd(CMD, None)
    except:
        import traceback;traceback.print_exc()
    for t in tmp_all  :
        t.delete()
    emp.delete_cache_template_count()


def del_finnger(request, oldObj):
    from mysite.iclock.models.model_bio import Template
    from mysite import settings
    from mysite.iclock.models.dev_comm_operate import    sync_delete_user_finger,sync_set_acc_user
    #from mysite.iclock.models.model_device import Device, DEVICE_TIME_RECORDER
    installed_apps = settings.INSTALLED_APPS
    delfingger = request.REQUEST.get("delfinger", "")
    if delfingger:
        delfingger = delfingger.split(",")
        del_fp(oldObj,delfingger,True)
#        for i in range(len(delfingger)):
#            template = Template.objects.filter(UserID=oldObj, FingerID__exact=delfingger[i])
#            filter = "Pin=%s\tFingerID=%s"%(oldObj.PIN,delfingger[i])
#            if template:
#                if get_option("IACCESS"):
#                    acc_dev_list = oldObj.search_accdev_byuser()
#                    sync_delete_user_finger(acc_dev_list, "templatev10", filter)
#                    template.delete()
#                elif get_option("ATT"):
#                    pass
                    
#处理个人照片
def saveUploadImage(request, fname, path=None):
    from   mysite import settings
    import StringIO
    import os
    photopath = path or settings.ADDITION_FILE_ROOT + "photo/"
    fname = photopath + fname
    #print "fname:%s" % fname
    try:
        os.makedirs(os.path.split(fname)[0])
    except: pass
    output = StringIO.StringIO()
    f = request.FILES.get('fileUpload', None)
    if not f:
        return  None
    for chunk in f.chunks():
        output.write(chunk)
    try:
        import PIL.Image as Image
    except:
        return None
    try:
        output.seek(0)
        im = Image.open(output)
    except IOError, e:
        return None
    size = f.size
    try:
        im.save(fname);
    except IOError:
        im.convert('RGB').save(fname)
    return size

#在表单提前，加入自定义字段
def detail_resplonse(sender, **kargs):
        from dbapp.widgets import form_field, check_limit
        from model_iccard import ICcard,ICcardForeignKey
        from mysite.iclock.models import Template
        from mysite import settings
        import os
        if kargs['dataModel'] == Employee:
                form = sender['form']
                emp_card = ""
                blance = 0
                mng_cost = 0
                card_cost = 0
                obj_type = ICcard.objects.all()[0]
                isexits = False
                tcount = 0
                tfingerid = ""
                fptypecode = ""
                durtcount = 0
                durfpid = ""
                tcount10 = 0
                tfingerid10 = ""

                pin = ""
                lng = 'chs'
                hdate = None #雇佣日期
                photo_url=""
                if kargs['key'] != None:
                    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
                    try:
                        objcard = IssueCard.objects.get(UserID__exact=kargs['key'],cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                        if objcard:
                            blance = objcard.blance
                            mng_cost = objcard.mng_cost
                            card_cost = objcard.card_cost
                            emp_card = objcard.cardno
                            obj_type = objcard.type
                    except:
                        pass
                    pin = Employee.objects.get(pk=kargs['key']).PIN
                    t9 = Template.objects.filter(UserID__exact=pin, Fpversion='9')#9.0指纹模版
                    t10 = Template.objects.filter(UserID__exact=pin, Fpversion='10')#9.0指纹模版
                    if len(t10)>0 and len(t10)>=len(t9):
                        tcount = len(t10)
                        fptypecode = ",".join(["%s" % i.Valid for i in t10])     # 指纹类型代码
                        tfingerid = ",".join(["%s" % i.FingerID for i  in t10])
                    else:
                        tcount = len(t9)
                        fptypecode = ",".join(["%s" % i.Valid for i in t9])     # 指纹类型代码
                        tfingerid = ",".join(["%s" % i.FingerID for i  in t9])
                    emp = Employee.objects.filter(id__exact=kargs['key'])[0]
                    hdate=emp.Hiredday#获取人员的入职日期
                    if emp.photo:
                        photo_url = emp.photo.url

                    t = Template.objects.filter(UserID__exact=kargs['key'], Fpversion='9', Valid=DURESS_FINGER)   #胁迫指纹数量
                    if len(t) > 0:
                        durtcount = len(t)
                        durfpid = ",".join(["%s" % i.FingerID for i in t])
           
                    if len(t10) > 0:
                        tcount10 = len(t10)
                        tfingerid10 = ",".join(["%s" % i.FingerID for i  in t10])


                photopath = settings.ADDITION_FILE_ROOT + "photo/" + pin + ".jpg"
                if os.path.isfile(photopath):
                    isexits = True

                from base.models import options
                from mysite import settings
                
                lng = options['base.language']
                #print "lng:%s" % lng
                chkph = models.CharField(verbose_name=_(u'照片url'),max_length=50 ,default=photo_url, blank=True, null=True)
                tfcount = models.CharField(verbose_name=_(u'指纹模版数量'), max_length=10, default=tcount, blank=True, null=True)
                fpcode = models.CharField(verbose_name=_(u'手指类型'), max_length=20, default=fptypecode, blank=True, null=True)
                durtfcount = models.CharField(verbose_name=_(u'胁迫指纹模版数量'), max_length=10, default=durtcount, blank=True, null=True)
                durfingerid = models.CharField(verbose_name=_(u'胁迫指纹id'), max_length=10, default=durfpid, blank=True, null=True)
                tfids = models.CharField(verbose_name=_(u'手指编号'), max_length=20, default=tfingerid, blank=True, null=True)
                tlng = models.CharField(verbose_name=_(u'当前语言'), max_length=10, default=lng, blank=True, null=True)
                tfcount10 = models.CharField(verbose_name=_(u'模版数量'), max_length=10, default=tcount10, blank=True, null=True)
                tfids10 = models.CharField(verbose_name=_(u'手指编号'), max_length=20, default=tfingerid10, blank=True, null=True)
                pin_width = models.IntegerField(null=True, blank=True, default=settings.PIN_WIDTH)
                
                
                
                cardno = models.CharField(_(u'卡号'), max_length=20, null=False, blank=True, editable=True, default = emp_card)
                #消费字段
                if get_option("POS_ID"):
                    blance = models.DecimalField(verbose_name=_(u'卡上金额（元）'),max_digits=9,null=True, blank=True,default=blance,decimal_places=2,editable=True)
                    mng_cost = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"卡管理费（元）"),null=True, default = mng_cost,blank=True)
                    card_cost = models.DecimalField (max_digits=8,decimal_places=2, verbose_name=_(u"卡成本（元）"),null=True,default = card_cost, blank=True)
                    type=ICcardForeignKey(verbose_name=_(u'消费卡类'), editable=True,null=True,blank=True,default=obj_type.pk)
                
                
                
                #安装语言
                if hdate !=None:
                    hdate = hdate.strftime("%Y-%m-%d")
                else:
                    hdate =  datetime.datetime.now().strftime("%Y-%m-%d")
                Hiredday = models.DateField(_(u'聘用日期'), max_length=8, null=True, blank=True, default=hdate)
               # kargs["install_language"]=settings.APP_CONFIG.language.language
                install_language = models.CharField(verbose_name=_(u'安装语言'), max_length=20, default=settings.APP_CONFIG.language.language, blank=True, null=True)
                form.fields['install_language'] = form_field(install_language)
                                
                form.fields['Hiredday'] = form_field(Hiredday)#by 雇佣日期默认不是系统时间 不更新的问题
                form.fields['chkph'] = form_field(chkph)
                form.fields['tcount'] = form_field(tfcount)
                form.fields['tfids'] = form_field(tfids)
                form.fields['fpcode'] = form_field(fpcode)
                form.fields['durtcount'] = form_field(durtfcount)
                form.fields['durfpid'] = form_field(durfingerid)
                form.fields['lng'] = form_field(tlng)
                form.fields['tcount10'] = form_field(tfcount10)
                form.fields['tfids10'] = form_field(tfids10)
                form.fields['pin_width'] = form_field(pin_width)
                
                
                
                form.fields['cardno'] = form_field(cardno)
                if get_option("POS_ID"):
                    form.fields['blance'] = form_field(blance)
                    form.fields['mng_cost'] = form_field(mng_cost)
                    form.fields['card_cost'] = form_field(card_cost)
                    form.fields['type'] = form_field(type)
                

data_edit.pre_detail_response.connect(detail_resplonse)

def getuserinfo(user_pk,attr):
    u'''取得用户pk为user_pk的属性attr'''
    try:
        Employee.can_restore=True
        emp=Employee.objects.get(id=user_pk)
        Employee.can_restore=False
        if attr == "DeptID":
            dept=""
            try:
                dept=Department.objects.get(pk=emp.DeptID_id)
            except:
                return ""
            return u"%s"%dept
            
        
        if hasattr(emp,attr):
            return getattr(emp,attr)
    except:
        Employee.can_restore=False
        pass
    return ""


def get_dept(user_id):
    u"取得用户id为user_id所属部门"
    from mysite.personnel.models import Employee,Department
    emp=""
    try:
        Employee.can_restore = True
        emp=Employee.objects.get(pk = user_id)
        Employee.can_restore = False
    except:
        Employee.can_restore = False
        return emp
    
    dept = ""
    try:
        Department.can_restore = True
        dept = Department.objects.get(pk = emp.DeptID_id)
        Department.can_restore = False
    except:
        Department.can_restore = False
        return dept
    return dept


#在表单提交后，对自定义字段进行处理
def DataPostCheck(sender, **kwargs):
    from mysite.iclock.models.dev_comm_operate import sync_set_user, sync_set_user_privilege,sync_delete_user_privilege
    from django.db.models import Model
    from decimal import Decimal
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender           
    emp_card = request.REQUEST.get("cardno", "")
    type = request.REQUEST.get("type", "")
    blance = request.REQUEST.get("blance",0)
    card_cost = request.REQUEST.get("card_cost", 0)
    mng_cost = request.REQUEST.get("mng_cost", 0)
    if isinstance(newObj, Employee):
        installed_apps = settings.INSTALLED_APPS
#        if saveUploadImage(request, newObj.PIN + ".jpg"):
#            photopath = settings.ADDITION_FILE_ROOT + "photo/"
#            newObj.photo = "/file/photo/" + newObj.PIN + ".jpg"
#            newObj.save()
        #门禁考勤通用--保存、删除指纹
        
        save_finnger(request, newObj)  
        try:          #保存指纹
            del_finnger(request, oldObj)             #删除指纹
        except:
            import traceback;traceback.print_exc()
        from mysite.personnel.models.model_issuecard import IssueCard,POS_CARD,CARD_VALID,CARD_STOP,CARD_LOST,CARD_OVERDUE
        from mysite.personnel.models.model_iccard import ICcard
        tmp_issuecare = IssueCard.objects.filter(UserID=newObj,cardstatus = CARD_VALID )
        try:
            if tmp_issuecare:#编辑
#                for obj  in tmp_issuecare:
                if  tmp_issuecare[0].cardno <> emp_card and not tmp_issuecare[0].sys_card_no:
                    from mysite.pos.models import CarCashSZ, CarCashType
#                        card_blance = obj.blance
#                        card_cost = obj.card_cost
#                        mng_cost = obj.mng_cost
#                        type = obj.type
                    old_card = tmp_issuecare[0].cardno
                    tmp_issuecare[0].cardstatus = CARD_STOP  #停用旧卡号
                    tmp_issuecare[0].save(force_update=True)
                    if emp_card:
                        issuecard = IssueCard()
                        issuecard.UserID = newObj
                        issuecard.cardno = emp_card
                        issuecard.issuedate = datetime.datetime.now().strftime("%Y-%m-%d")
                        issuecard.save()
                
            elif emp_card:
                issuecard = IssueCard()
                issuecard.UserID = newObj
                issuecard.cardno = emp_card
                issuecard.type_id = type
                issuecard.blance = Decimal(str(blance))
                issuecard.card_cost = card_cost
                issuecard.mng_cost = mng_cost
                issuecard.issuedate = datetime.datetime.now().strftime("%Y-%m-%d")
                issuecard.save()
#            if not get_option("POS_IC"):
#                newObj.using_card = emp_card
            newObj.save()
        except Exception, e:
            import traceback;traceback.print_exc()
        if get_option("POS_IC") and oldObj!=None and oldObj.EName != newObj.EName:
            try:
                obj_list = IssueCard.objects.filter(UserID = newObj,card_privage = POS_CARD,sys_card_no__isnull=False)
                if obj_list:
                    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                    from mysite.iclock.models.dev_comm_operate import update_pos_device_info
                    dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                    update_pos_device_info(dev,obj_list,"USERINFO")#下发指令修改姓名
            except Exception, e:
                import traceback;traceback.print_exc()
            
        if get_option("ATT"):#zkeco+zktime
            #fingger=request.REQUEST.get("finnger","")
            #template=request.REQUEST.get("template","")
            from base.sync_api import SYNC_MODEL
            if not SYNC_MODEL:
                from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
            if oldObj is None:  #新增人员
                if len(newObj.attarea.all()) == 0:
                    newObj.attarea.add(Area.objects.get(pk=1))
                    newObj.save()
                if not SYNC_MODEL:
                    adj_user_cmmdata(newObj, [], newObj.attarea.all())
                str_area = u",".join([a.areaname for a in newObj.attarea.all()])
                newObj.cache_area(str_area)#oldObj.cache_area(str_area) ----is None

                 
                
                #sync_set_user(newObj.search_device_byuser(), [newObj])
            else:   #修改人员信息
                area = []
                if oldObj.attarea_set != newObj.attarea_set:
                    #devs=oldObj.search_device_byuser()
                    for attarea in oldObj.attarea_set:
                        area.append(attarea)
                    #print "area=", area
                    #devs=Device.objects.filter(area__in=area).filter(device_type=DEVICE_TIME_RECORDER)
                    #print "devs=", devs
                #    sync_delete_user(devs, [oldObj])
                #sync_set_user(newObj.search_device_byuser(), [newObj])
                if not SYNC_MODEL:
                    adj_user_cmmdata(newObj, area, newObj.attarea.all())
                str_area = u",".join([a.areaname for a in newObj.attarea.all()])
                oldObj.cache_area(str_area)
                
                #print "upload fingerprint"
        if get_option("IACCESS"):#zkeco+iaccess
            from mysite.iaccess.models import AccLevelSet
            from mysite.iclock.models.dev_comm_operate import sync_set_acc_user
            levels = request.POST.getlist("level")
            changed = request.POST.getlist("level_changed")
            if oldObj!=None and oldObj.EName!=newObj.EName:#姓名修改时，重新下命令（一体机）
                sync_set_acc_user(newObj.search_accdev_byuser(acd=True), [newObj])
            
            #print "changed=", changed
            if changed:
                #删除人的旧权限
                emp_obj = newObj#当前要操作的对象（人）
                emp_levels = emp_obj.acclevelset_set.all()#和人关联的所有权限组
                devset = []
                for emp_level in emp_levels:
                    for door in emp_level.door_group.all():
                        devset.append(door.device)
                    emp_level.emp.remove(emp_obj.id)
                dev = set(devset)
                sync_delete_user_privilege(dev, [emp_obj])
                #同步人的新权限
                devset = []
                #print "#####levels",levels
                for level in levels:#以权限组为中心，循环权限组
                    obj = AccLevelSet.objects.get(pk=level)
                    obj.emp.add(emp_obj.id)
                    for door in obj.door_group.all():
                        devset.append(door.device)
                dev = set(devset)
                #print "#####dev",dev
                sync_set_acc_user(dev, [emp_obj])
                sync_set_user_privilege(dev, [emp_obj])
            else:
                sync_set_acc_user(newObj.search_accdev_byuser(), [newObj])
data_edit.post_check.connect(DataPostCheck)

#验证卡号有效性
def valid_card(sender, **kwargs):
    import re
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_issuecard import IssueCard
    from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
    request = sender
    oldobj = kwargs['oldObj']
    model = kwargs['model']
    type = request.REQUEST.get("type", "")
    blance = request.REQUEST.get("blance",0)
    if model == Employee:
        if get_option("POS_ID"):
            from decimal import Decimal
            from mysite.personnel.models.model_iccard import ICcard 
            iccardobj= ICcard.objects.filter(pk=type)        
            lessmoney = iccardobj[0].less_money#卡类最小余额
            maxmoney = iccardobj[0].max_money#卡类最大余额
            newblance = Decimal(str(blance))
#            if lessmoney>0 and lessmoney>newblance:
#               raise Exception(_(u"超出卡最小余额"))
            if maxmoney>0 and newblance>maxmoney:
               raise Exception(_(u"超出卡最大余额"))
            if maxmoney==0 and newblance >9999 :
               raise Exception(_(u"超出系统允许最大余额"))
            
        card = request.POST.get("cardno", "")
        tmpre = re.compile('^[0-9]+$')
        if card and not tmpre.search(card):
            raise Exception(_(u'卡号不正确'))
        if card:#新增或编缉了卡号时
            if int(card) == 0:
                raise Exception(_(u'卡号不能为0'))
        if card:
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP
            try:
                tmpcard = IssueCard.objects.get(cardno=int(card))
            except MultipleObjectsReturned:
                raise Exception(_(u'同一有效卡号登记了多个人，请核对是否在考勤设备上存在同一卡号登记多个人的情况!'))
            except ObjectDoesNotExist:
                tmpcard = None
            if oldobj:#编辑不带消费的情况下才允许编辑卡号
                if tmpcard and tmpcard.cardstatus == CARD_STOP:#编辑的卡号为停用状态
                    raise Exception(_(u'卡号已使用，如果确认将重新发卡，请卡原持卡人 %s 进行退卡操作') % tmpcard)
                if tmpcard and tmpcard.UserID!= oldobj:#用于前端表单验证 #编辑的卡号正在被别人使用
                    raise Exception(_(u'卡号已使用，如果确认将重新发卡，请卡原持卡人 %s 进行退卡操作') % tmpcard)
            else:
                if tmpcard :#用于前端表单验证
                    raise Exception(_(u'卡号已使用，如果确认将重新发卡，请卡原持卡人 %s 进行退卡操作') % tmpcard)
            
data_edit.pre_check.connect(valid_card)#验证编辑卡号

#保存访客信息到人员表 --hjs20111110
def visitor_save(sender, **kwargs):
    from mysite.personnel.models.model_emp import Employee
    request = sender
    oldObj = kwargs['oldObj']
    model = kwargs['model'] 
    pin = request.POST.get("visitor_pin", "")
    if pin:
        try:
            name = request.POST.get("visitor_name", "")#访客姓名
            gender = request.POST.get("gender", "")
            card = request.POST.get("card", None)
            home_address = request.POST.get("home_address", "")
            levels = request.POST.get("visitor_level", "")
            certificate_photo = request.POST.get("certificate_photo", None)
            #print '----card===', card
            pin = format_pin(pin)
            
            try:
                visitor = Employee.objects.get(PIN=pin)#访客已存在，更新信息
                visitor.EName = name
                visitor.photo = certificate_photo
                visitor.Gender = gender
                visitor.homeaddress = home_address or None
                visitor.save()
                set_level_to_visitor(visitor, levels)
            except:
                #新增访客
                visitor = Employee()
                visitor.PIN = pin
                visitor.EName = name
                #visitor.Card = card
                visitor.photo = certificate_photo
                visitor.Gender = gender
                visitor.homeaddress = home_address or None
                visitor.is_visitor = 1
                visitor.is_att = 0
                
                visitor.save()
                set_level_to_visitor(visitor, levels)
            
            #print '------ddddd---',
            from mysite.personnel.models.model_issuecard import IssueCard, CARD_VALID, CARD_OVERDUE
            iss_card = IssueCard.objects.filter(UserID=visitor, cardstatus__in = [CARD_OVERDUE,CARD_VALID])
            if iss_card:
                iss_card[0].cardno = card
                iss_card[0].save()
            else:
                iss_card = IssueCard()
                iss_card.UserID = visitor
                iss_card.cardno = card
                iss_card.cardstatus = CARD_VALID
                iss_card.save()
        except Exception, e:
            print '---wwww---eee=', e
            
if get_option("VISITOR"):            
    data_edit.pre_check.connect(visitor_save)

#给访客授权 --hjs20111110
def set_level_to_visitor(visitor, levels):
    from mysite.iaccess.models import AccLevelSet
    from mysite.iclock.models.dev_comm_operate import sync_set_user, sync_set_user_privilege,sync_delete_user_privilege
    try:
        devset = []
        #print '----levels=',levels
        if levels != "":
            levels = levels.split(',')
            for level in levels:#以权限组为中心，循环权限组--当前新增权限组要处理的设备，其他的设备并不需要处理，所以共用一个dev即可。
                obj = AccLevelSet.objects.get(pk=int(level))
                obj.emp.add(visitor.id)
                for door in obj.door_group.all():
                    devset.append(door.device)
            dev = set(devset) 
            sync_delete_user_privilege(dev, [visitor])
            sync_set_user(dev, [visitor])
            sync_set_user_privilege(dev, [visitor])
    except Exception, e:
        print '-----set_level_to_visitor--error---', e
