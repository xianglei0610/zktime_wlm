# -*- coding: utf-8 -*-
from dbapp.import_data import ImportData
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.db.models.fields import AutoField
import xlrd
import types
from base.backup import get_attsite_file

class ImportCardData(ImportData):
    def __init__(self,req=None,input_name = "import_data"):
        u"初始化基础类"
        self.input_name = "import_data" #前段上传文件控件的名称
        self.valid_format = ["xls","csv"] #导入的文件格式
        self.request=req #请求
        self.head = None #模型头
        self.records=[] #记录
        self.format = None #上传文件的格式
        self.upload_file = None #上传的文件
        self.app_label = None #应用名称
        self.model_name = None #模型名称
        self.model_cls = None #模型类
        self.error_info = [] #错误信息
        self.valid_head_indexs =[] #导入文件中合法字段的索引
        self.valid_model_fields = [] #导入文件中包含的模型字段
        self.other_fields = [] #其他需要没有在文档中的字段，使用默认值插入到数据
        self.calculate_fields_verbose = []# {u"%s"%_(u"部门编号"):""} 用来给其他列初始化的列，例如人员中的部门编号，就是为了初始化，人员中的部门字段
        self.calculate_fields_index = {}# 在文档头中的index
        self.must_fields=[] #必须要用户填的字段，如员工的PIN号。。。
        self.current_dbtype = "sqlserver_ado" #当前连接数据库的驱动名称
        self.input_name = input_name
        self.need_read_data = False #不需要验证
        self.need_update_old_record = True
        self.sql_batch_cnts = 80
        cnts = get_attsite_file()["SYS"]["SQL_BATCH_CNTS"]
        if cnts:
            self.sql_batch_cnts = int(cnts)
        app_label = "personnel"
        model_name = "IssueCard"
        self.model_cls = models.get_model(app_label, model_name)
        self.calculate_fields_verbose = [u"%s"%_(u"人员编号"),"user_pk"]
        self.must_fields = [
            u"%s"%_(u"人员编号"),
            u"%s"%_(u"卡号"),
        ]
    
    
    def before_insert(self):
        u"插入前批量剔除已经有的人员卡记录"
        from mysite.personnel.models.model_issuecard import IssueCard, CARD_VALID
        from mysite.personnel.models.model_emp import format_pin,Employee
        from mysite.utils import get_option
        tmp_pins = []
        exist_pks = []#存在卡的员工
        exist_emp = [] #存在的员工
        tem_card = [] #导入文件的卡号
        imported_card = [] #已经验证通过的卡号
        exist_card = [] #已经登记过的卡号
        count = 0
        for e in self.records:
#            imported_card.append(e[1])
            tem_card.append(e[1])
            tmp_pins.append( e[0] )#这里不需要格式化format_pin因为传进来的记录已经在员工导入里面格式化了
            count = count + 1
            if count>200:
                if get_option("POS"):
                    exist_emp = exist_emp +list(Employee.all_objects.filter(PIN__in=tmp_pins).values_list("id","PIN"))
                else:
                    exist_emp = exist_emp +list(Employee.objects.filter(PIN__in=tmp_pins).values_list("id","PIN"))
                exist_pks = exist_pks +list(IssueCard.objects.filter(UserID__PIN__in=tmp_pins,cardstatus = CARD_VALID).values_list("UserID__PIN",flat = True))
                exist_card = exist_card +list(IssueCard.objects.filter(cardno__in=tem_card).values_list("cardno",flat = True))
                tmp_pins = []
                tem_card = []
                count = 0 
        
        if tmp_pins:
            if get_option("POS"):
                exist_emp = exist_emp +list(Employee.all_objects.filter(PIN__in=tmp_pins).values_list("id","PIN"))
            else:
                exist_emp = exist_emp +list(Employee.objects.filter(PIN__in=tmp_pins).values_list("id","PIN"))
            exist_pks = exist_pks +list(IssueCard.objects.filter(UserID__PIN__in=tmp_pins,cardstatus = CARD_VALID).values_list("UserID__PIN",flat = True))
            exist_card = exist_card +list(IssueCard.objects.filter(cardno__in=tem_card).values_list("cardno",flat = True))
#        print "exist_card====",exist_card
        result_records = []
        for e in self.records:
            emp_pin = e[0]#第0个是员工工号
            emp_card = e[1]#导入文件每一行的卡号
#            print "emp_card======%s-------e[2]======%s"%(emp_card,imported_card)
            if emp_card not in imported_card and emp_card not in exist_card :#如果卡号不是重复 and 卡号没有登记过
                for elem in exist_emp:
                    if emp_pin == elem[1]:#存在这个员工
                        e[2] = elem[0]
                        break
                if emp_pin not in  exist_pks:
                    imported_card.append(e[1])
                    result_records.append( e )
        self.records = result_records
                
    def process_row(self,row_data,calculate_dict):
        u'''
            特殊情况给开发人员提供的接口
            row_data 这一行的数据
            calculate_dict 文档附加的列，如部门编号，
            员工表是没有部门编号的，部门编号是用来初始化员工字段DeptID的
        '''
        from mysite.personnel.models.model_issuecard import IssueCard, CARD_VALID
        from mysite.personnel.models import Employee
        key = u"%s"%_(u"人员编号")
        emp_pin = u"%s"%calculate_dict[key]
        
        emp_pk = calculate_dict["user_pk"]
        if 'postgresql_psycopg2' in connection.__module__:
            userid_key = '"'+"UserID_id"+'"'
            cardstatus_key = '"'+"cardstatus"+'"'
        else:
            userid_key = "UserID_id"
            cardstatus_key = "cardstatus"
        if emp_pk:
            row_data[userid_key] = u'%s'%emp_pk #初始化人员外键
        else:
            obj_emp = Employee()
            obj_emp.PIN = emp_pin
            obj_emp.DeptID_id = 1
            obj_emp.save()
            row_data[userid_key] = u'%s'%obj_emp.pk #初始化部门
        row_data[cardstatus_key] = u'%s'%CARD_VALID
        
        return row_data
    
