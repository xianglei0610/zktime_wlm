# -*- coding: utf-8 -*-
from dbapp.import_data import ImportData
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.db.models.fields import AutoField
import xlrd
import types
from mysite.personnel.models.model_emp import format_pin

class ImportTransData(ImportData):
    u"考勤记录导入类"
    def __init__(self,req,input_name = "import_data"):
        super(ImportTransData, self).__init__(req,input_name)
        self.must_fields = [
            u"%s"%_(u"人员编号"),
            u"%s"%_(u"考勤时间"),
        ]#必填字段
        self.calculate_fields_verbose = [u"%s"%_(u"人员编号")]

    def process_row(self,row_data,calculate_dict):
         u'''
             特殊情况给开发人员提供的接口
             row_data 这一行的数据
             calculate_dict 文档附加的列，如人员编号，
             记录表是没有人员编号的，人员编号是用来初始化员工字段UserID的
         '''
         from mysite.personnel.models import Employee
         #print "calculate_dict:",calculate_dict,"\n"
         key = u"%s"%_(u"人员编号")
         emp_pin = u"%s"%calculate_dict[key]
         emp_pin = format_pin(emp_pin)
         try:
             obj_emp = Employee.all_objects.get(PIN = emp_pin)
         except:
             #判断是使用默认还是创建新的人员
             obj_emp = Employee()
             obj_emp.PIN = emp_pin
             obj_emp.DeptID_id= 1
             obj_emp.save()
         
         row_data["userid"] = u"%s"%obj_emp.pk #初始化人员
         return row_data
 