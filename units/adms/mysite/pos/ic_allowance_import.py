# -*- coding: utf-8 -*-
from dbapp.import_data import ImportData
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.db.models.fields import AutoField
import xlrd
import types
from mysite.personnel.models.model_emp import format_pin
from mysite.pos.models.model_allowance import Allowance
from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
import datetime
from decimal import Decimal
from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE,ONLINE_ALLOWANCE
allow_data_list = []
class ICImportAllowData(ImportData):
    u"补贴记录导入类"
    def __init__(self,req,input_name = "import_data"):
        super(ICImportAllowData, self).__init__(req,input_name)
        self.must_fields = [
            u"%s"%_(u"人员编号"),
            u"%s"%_(u"补贴金额"),
            u"%s"%_(u"补贴有效日期"),
        ]#必填字段
        self.calculate_fields_verbose = [u"%s"%_(u"人员编号")]
        self.import_error_info = []
    def records_analysis(self, record_dict):
        u"分析哪些是应该插入的数据，哪些应该是更新的数据"
        from mysite.personnel.models import Employee
        from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
        records = record_dict["sql_list"]
        insert_records = []
        count = 0 
        temp_records = []
        card_dict = []
        global allow_data_list
        for record in records:#格式：[{},{}]
#            if not self.error_info:
                now = datetime.datetime.now().date()
                valid_date = datetime.datetime.strptime(record["valid_date"],"%Y-%m-%d").date()
#                sys_card_no = record["sys_card_no"]
                user_id = record["user_id"]
                money = Decimal(record["money"])
                emp_pin = record["user_pin"]
                del(record["user_pin"])
                now_time = datetime.datetime.now()
                if ONLINE_ALLOWANCE:#在线补贴模式
                    batch = ((now_time.year-2000)*12+now_time.month)*31+now_time.day
                else:
                    batch = now_time.strftime("%Y%m")[2:]
                try:
                    obj_emp = Employee.objects.get(id = int(user_id))
                except:
                    obj_emp = None
                    self.import_error_info.append(_(u"人员编号为：%s的员工编号在人事表中不存在，导入失败！")%emp_pin)
                try:
                    if obj_emp:
                        objcard = IssueCard.objects.get(UserID=user_id,cardstatus__in=[CARD_VALID,CARD_OVERDUE],sys_card_no__isnull=False)
    #                    objcard = IssueCard.objects.get(UserID=user_id,sys_card_no=sys_card_no,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                        sys_card_no = objcard.sys_card_no
                        record["sys_card_no"] = sys_card_no
                        temp_records.append( record )
                        if obj_emp and sys_card_no not in card_dict:
                            newblan = objcard.blance+money
                            from mysite.personnel.models.model_iccard import ICcard
                            iccardobj= ICcard.objects.get(pk=objcard.type_id)
                            lessmoney = iccardobj.less_money#卡类最小余额
                            maxmoney = iccardobj.max_money#卡类最大余额
                            if lessmoney>newblan and lessmoney>0:
                                objcard = None
                                self.import_error_info.append(_(u"人员编号为：%s的员工超出卡类最小余额，导入失败！")%emp_pin)
                            if newblan>maxmoney and maxmoney>0:
                                objcard = None
                                self.import_error_info.append(_(u"人员编号为：%s的员工超出卡类最大余额，导入失败！")%emp_pin)
                            if maxmoney==0 and newblan > 10000 :
                                objcard = None
                                self.import_error_info.append(_(u"人员编号为：%s的员工超出系统允许最大余额，导入失败！")%emp_pin)
                        if valid_date >= now: #验证有效日期是否大于当前日期
                            count = count + 1
                        else:
                            count = 0
                            self.import_error_info.append(_(u"人员编号为：%s的员工有效日期必须大于当前日期，导入失败！")%emp_pin)
                except:
#                    import traceback; traceback.print_exc();
                    objcard = None
                    count = 0
                    self.import_error_info.append(_(u"人员编号为：%s的员工没有注册卡账号，或者已经挂失，导入失败！")%emp_pin)
                if count > 0:
                    allow_data = Allowance.objects.filter(sys_card_no=sys_card_no,batch = batch)
                    if not allow_data and sys_card_no not in card_dict :
                        card_dict.append(sys_card_no)
                        for elem in temp_records:
                            insert_records.append(elem)
                            allow_data_list.append(elem)
                    else:
                        self.import_error_info.append(_(u"人员编号为：%s的员工当月补贴重复，导入失败！")%emp_pin)
                temp_records = []
                count =0
#            else:
#                insert_records = []
#                allow_data_list = []
#        if self.error_info:
#            insert_records = []
        record_dict["insert_records"] = insert_records
        insert_records = []
        

    def before_insert(self):
        from mysite.personnel.models import Employee
        from mysite.personnel.models.model_emp import format_pin
        from base.middleware import threadlocals
        from mysite.personnel.models.model_iccard import ICcard
        from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
        from mysite.pos.models.model_allowance import Allowance
        calculate_dict = {}
        count_head = len(self.head) 
        u = datetime.datetime.now()
        for row in self.records:
            for index in range(count_head):
                for k,v in self.calculate_fields_index.items():
                    if v == index:
                        calculate_dict[ k ] = row[index]
            key = u"%s"%_(u"人员编号")
            emp_pin = u"%s"%calculate_dict[key]
            emp_pin = format_pin(emp_pin)
            try:
                obj_emp = Employee.objects.get(PIN = emp_pin)
                user_id= obj_emp.pk #初始化人员
            except:
                user_id = '0000'
            try:
                now_time = datetime.datetime.now()
                if ONLINE_ALLOWANCE:#在线补贴模式
                    batch = ((now_time.year-2000)*12+now_time.month)*31+now_time.day
                else:
                    batch = now_time.strftime("%Y%m")[2:]
                objcard = IssueCard.objects.get(UserID=user_id,cardstatus__in=[CARD_VALID,CARD_OVERDUE],sys_card_no__isnull=False)
                sys_card_no = objcard.sys_card_no
                allow_data = Allowance.objects.get(sys_card_no=sys_card_no,batch = batch)
            except:
                pass
                    
    def after_insert(self):
        global allow_data_list
        if ONLINE_ALLOWANCE:#在线补贴模式
            allow_data_list = []
            self.error_info = self.import_error_info
            pass
        else:
            devlist=Device.objects.filter(device_type=DEVICE_POS_SERVER,device_use_type = 2)#查找补贴机
            from mysite.iclock.models.dev_comm_operate import update_pos_device_info,save_operate_cmd
            for dev in devlist:
                for elem in allow_data_list:
                    table_name = "SUBSIDYLOG"
                    Op=save_operate_cmd("DATA UPDATE %s"%table_name)
                    valid_date = datetime.datetime.strptime(elem["valid_date"],"%Y-%m-%d")
                    allowdata = ((valid_date.year-2000)*12+valid_date.month)*31+valid_date.day
                    line=("SysID=%s\tCardNo=%s\tBatch=%s\tMoney=%s\tallowDate=%s"%(elem["sys_card_no"],elem["sys_card_no"],elem["batch"],int(elem["money"])*100,allowdata))
                    CMD="UPDATE %s %s"%(table_name,line)
                    dev.appendcmd(CMD,Op)
            self.error_info = self.import_error_info
            allow_data_list = []
            
    def process_row(self,row_data,calculate_dict):
        from mysite.personnel.models import Employee
        from mysite.personnel.models.model_emp import format_pin
        from base.middleware import threadlocals
        op=threadlocals.get_current_user()
        key = u"%s"%_(u"人员编号")
        emp_pin = u"%s"%calculate_dict[key]
        emp_pin = format_pin(emp_pin)
        try:
            obj_emp = Employee.objects.get(PIN = emp_pin)
            row_data["user_id"] = obj_emp.pk #初始化人员
        except:
            row_data["user_id"] = '0000'
        now_time = datetime.datetime.now()
        if ONLINE_ALLOWANCE:#在线补贴模式
            row_data["batch"] = ((now_time.year-2000)*12+now_time.month)*31+now_time.day
        else:
            row_data["batch"] = now_time.strftime("%Y%m")[2:]
        row_data["date"] = datetime.datetime.now()
        row_data["is_pass"] = 1
        row_data["pass_name"] = op.username
        row_data["user_pin"] = emp_pin
        return row_data

    
    
 
