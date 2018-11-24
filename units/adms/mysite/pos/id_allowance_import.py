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
allow_data_list = []
class IDImportAllowData(ImportData):
    u"补贴记录导入类"
    def __init__(self,req,input_name = "import_data"):
        super(IDImportAllowData, self).__init__(req,input_name)
        self.must_fields = [
            u"%s"%_(u"人员编号"),
            u"%s"%_(u"补贴金额"),
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
#                valid_date = datetime.datetime.strptime(record["valid_date"],"%Y-%m-%d").date()
#                sys_card_no = record["sys_card_no"]
                user_id = record["user_id"] #由于已经构造好了为"'%s'"
                money = Decimal(record["money"])
                emp_pin = record["user_pin"]
                del(record["user_pin"])
                now_time = datetime.datetime.now()
                batch = now_time.strftime("%Y%m")[2:]
                try:
                    obj_emp = Employee.objects.get(id = int(user_id))
                except:
                    obj_emp = None
                    self.import_error_info.append(_(u"人员编号为：%s的员工编号在人事表中不存在，导入失败！")%emp_pin)
                try:
                    if obj_emp:
                        objcard = IssueCard.objects.get(UserID=user_id,cardstatus__in=[CARD_VALID,CARD_OVERDUE])
    #                    objcard = IssueCard.objects.get(UserID=user_id,sys_card_no=sys_card_no,cardstatus__in = [CARD_OVERDUE,CARD_VALID])
                        card_no = objcard.cardno
#                        record["cardno"] = card_no
                        temp_records.append( record )
                        if obj_emp and card_no not in card_dict:
                            newblan = objcard.blance+money
                            flag = True
                            from mysite.personnel.models.model_iccard import ICcard
                            iccardobj= ICcard.objects.get(pk=objcard.type_id)
                            lessmoney = iccardobj.less_money#卡类最小余额
                            maxmoney = iccardobj.max_money#卡类最大余额
                            if lessmoney>newblan and lessmoney>0:
                                objcard = None
                                flag = False
                                self.import_error_info.append(_(u"人员编号为：%s的员工超出卡类最小余额，导入失败！")%emp_pin)
                            if newblan>maxmoney and maxmoney>0:
                                objcard = None
                                flag = False
                                self.import_error_info.append(_(u"人员编号为：%s的员工超出卡类最大余额，导入失败！")%emp_pin)
                            if maxmoney==0 and newblan > 10000 :
                                objcard = None
                                flag = False
                                self.import_error_info.append(_(u"人员编号为：%s的员工超出系统允许最大余额，导入失败！")%emp_pin)
                        if flag:
                            count = count + 1
                        else:
                            count = 0
                except:
#                    import traceback; traceback.print_exc();
                    objcard = None
                    count = 0
                    self.import_error_info.append(_(u"人员编号为：%s的员工没有发卡，或者已经挂失，导入失败！")%emp_pin)
                if count > 0:
                    try:
                        if card_no not in card_dict :
                            card_dict.append(card_no)
                            for elem in temp_records:
                                insert_records.append(elem)
                                new_elem = elem.copy()
                                new_elem['newblance'] = newblan
                                new_elem['cardno'] = card_no
                                allow_data_list.append(new_elem)
                        else:
                            self.import_error_info.append(_(u"当前导入文件中，人员编号为：%s的员工存在重复记录，请核查数据！")%emp_pin)
                    except:
                        pass
#                        import traceback; traceback.print_exc();
                temp_records = []
                count =0
#            else:
#                insert_records = []
#                allow_data_list = []
#        if self.error_info:
#            insert_records = []
        record_dict["insert_records"] = insert_records
        insert_records = []
        

                    
    def after_insert(self):
        global allow_data_list
        from mysite.pos.models.model_carcashsz import CarCashSZ
        from mysite.pos.models.model_carcashtype import CarCashType
        for elem in allow_data_list:
            from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_OVERDUE
            try:
                objcard = IssueCard.objects.get(UserID=elem['user_id'],cardstatus__in=[CARD_VALID,CARD_OVERDUE])
                CarCashSZ(user_id=elem['user_id'],
                        card = elem['cardno'],
                        checktime = datetime.datetime.now(),
                        type = CarCashType.objects.get(id=2),#消费类型
                        money = elem['money'],
                        hide_column = 2,
                        blance = elem['newblance'],
                        ).save()
                objcard.blance = elem['newblance']
                objcard.save()
            except:
                import traceback; traceback.print_exc();
                pass
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
        row_data["batch"] = datetime.datetime.now().strftime("%Y%m")[2:]
        row_data["date"] = datetime.datetime.now()
        row_data["is_pass"] = 1
        row_data["pass_name"] = op.username
        row_data["user_pin"] = emp_pin
        return row_data

    
    
 
