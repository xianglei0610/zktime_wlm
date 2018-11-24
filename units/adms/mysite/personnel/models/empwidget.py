# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import flatatt
from django.utils.translation import ugettext_lazy as _
import datetime
from django.http import HttpResponse
from django.utils import simplejson
from base.middleware import threadlocals
from base.middleware.threadlocals import  get_current_request
from mysite import settings

def render_emp_widget(name, data, multiple, popup, filter):
    #员工自助
    req=get_current_request()
    if req.session.has_key("employee"):
        emp = req.session["employee"]
        return u"<input type='hidden' value =%(v)s name =%(n)s /><span>%(d)s</span>"%{
            "v":emp.pk,
            "n":name,
            "d":emp,
        } 

    js_attrs={}
    try:
        from depttree import DeptTree
        from mysite.personnel.models import Employee, Department
        from dbapp.urls import dbapp_url
        from mysite.urls import surl
        if type(data) == list:
            data = ','.join(d for d in [str(i) for i in data])
        url=data and ("/%s%s/select_emp_data/?id__exact=%s"%(surl,Employee._meta.app_label,data)) or ("/%s%s/select_emp_data/?%s"%(surl, Employee._meta.app_label, filter))
        date_now=datetime.datetime.now()
        str_now=str(date_now.strftime('%Y%m%d%H%M%S'))+str(date_now.microsecond)+name
        js_attrs["multiple_select"]=multiple
        js_attrs["popup"]=popup
        js_attrs["select_record"]=data and data or False
        js_attrs["field_name"]=name
        js_attrs["grid_id"]="emp_select_%s"%(str_now)
        js_attrs["surl"]=surl
        js_attrs["model_url"]=url
        json_attrs=simplejson.dumps(js_attrs)
        html=""
        if multiple:
            html+=u"<input type='hidden' name='multipleFieldName' value='%s' />"%name
        html+=u"<table id='id_corner_tbl' class='corner_tbl' cellpadding='0' cellspacing='0' style='float:left;'><tr><td></td><td></td><td class='tboc1 h1'></td><td></td><td></td></tr>" \
            +u"<tr><td></td><td class='tboc1 w1 h1'>&nbsp;</td><td class='tbac1'></td>" \
            +u"<td class='tboc1 w1 h1'>&nbsp;</td><td></td></tr><tr><td class='tboc1 w1'>&nbsp;" \
            +u"</td><td class='tbac1 tbg'></td><td class='tbac1 tbg td_contant'><div class='div_contant'>" \
                    +u"<div class='zd_Emp div_box_emp'>" \
                            +u"<div id='%s'></div>"%(js_attrs["grid_id"]) \
                            +"<script> $(document).ready(function(){$.zk._select_emp(%s);}) </script>"%(json_attrs) \
                    +"</div>" \
            +u"<div class='clear'></div></div></td><td class='tbac1 tbg'>"\
            +u"</td><td class='tboc1 w1'>&nbsp;</td></tr>" \
            +u"<tr><td></td><td class='tboc1 w1 h1'>&nbsp;</td><td class='tbac1'></td><td class='tboc1 w1 h1'>&nbsp;</td>" \
            +u"<td></td></tr><tr><td></td><td></td><td class='tboc1 h1'></td><td></td><td></td></tr></table>"
        return html
        
    except:
        import traceback; traceback.print_exc()

class ZEmpChoiceWidget(forms.Select):
    popup=False
    def __init__(self, attrs={}, choices=()):
            super(ZEmpChoiceWidget, self).__init__(attrs=attrs, choices=choices)
    def render(self, name, data, attrs=None, filter=None):
            if attrs: self.attrs.update(attrs)
            if 'id' not in self.attrs: self.attrs['id']='id_'+name
            self.attrs = self.build_attrs(self.attrs, name=name)
            return render_emp_widget(name, data, False, self.popup, filter)

def filter_for_select_emp(data):
    from mysite.personnel.models.model_emp import Employee
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_LOST,CARD_OVERDUE,POS_CARD
    from mysite.iclock.iutils import get_dept_from_all
    from mysite.utils import get_option
    all_emp = data.get("id_all_emp")
    op_type = data.get("id_op_type")
    if all_emp == "all":
        qs = Employee.all_objects.all()
    elif all_emp == "filed_card":#获取没发卡人员
        if get_option("POS_IC"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).values_list('UserID')
        elif get_option("POS_ID"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD).values_list('UserID')
        else:
            ids=IssueCard.objects.filter(cardstatus=CARD_VALID).values_list('UserID')
        qs = Employee.objects.all().exclude(id__in=ids)
    elif all_emp == "filed_having_card":#获取已发卡人员
        if get_option("POS_IC"):
            if op_type == "allowance":#补贴特殊处理
                from mysite.pos.models.model_allowance import Allowance
                batch = datetime.datetime.now().strftime("%Y%m")[2:]
                allow_sys_card = Allowance.objects.filter(batch = batch).values_list('sys_card_no')#已领取补贴卡账号
                ids = IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).exclude(sys_card_no__in=allow_sys_card).values_list('UserID')#获取没领取补贴人员ID 
            else:
                ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD,sys_card_no__isnull=False).values_list('UserID')#获取已发卡人员ID
        elif get_option("POS_ID"):
            ids=IssueCard.objects.filter(cardstatus__in=[CARD_VALID,CARD_OVERDUE],card_privage=POS_CARD).values_list('UserID')#获取已发卡人员ID
        else:
            ids=IssueCard.objects.filter(cardstatus=CARD_VALID).values_list('UserID')#获取已发卡人员ID
        qs = Employee.objects.all().filter(id__in=ids)
    else:
        qs = Employee.objects.all()
    return qs
        
    
class ZMulEmpChoiceWidget(forms.SelectMultiple):
    popup=False
    def __init__(self, attrs={}, choices=()):
            super(ZMulEmpChoiceWidget, self).__init__(attrs=attrs, choices=choices)
    def value_from_datadict(self, data, files, name):
        from django.utils.datastructures import MultiValueDict, MergeDict
        from mysite.personnel.models import Employee
        from mysite.iclock.iutils import get_dept_from_all,get_max_in

        if isinstance(data, (MultiValueDict, MergeDict)):
            dept_all = data.getlist(u"%s_dept_all"%name)#'on'或者''
            if dept_all:#选择部门下所有人员
                dept_id = data.getlist("deptIDs")
                deptIDschecked_child = data.get("deptIDschecked_child")
                if deptIDschecked_child == "on":
                    request=get_current_request()
                    dept_id = get_dept_from_all(dept_id,request)
                UserID = get_max_in(filter_for_select_emp(data),dept_id,"DeptID__in")
                u=[e.pk for e in UserID]

                return u[:1001]
            else:
                return data.getlist(name)
        else:
            return data.get(name, None)
    
    def render(self, name, data, attrs=None, filter=None):
            if attrs: self.attrs.update(attrs)
            if 'id' not in self.attrs: self.attrs['id']='id_'+name
            self.attrs = self.build_attrs(self.attrs, name=name)
            return render_emp_widget(name, data, True, self.popup, filter)

class ZMulPopEmpChoiceWidget(ZMulEmpChoiceWidget):
    popup=True
class ZPopEmpChoiceWidget(ZEmpChoiceWidget):
    popup=True
    
#multiple=F&popup=F
def get_widget_for_select_emp(request,multiple=False,popup=False):
        from dbapp.widgets import form_field
        from model_emp import  EmpForeignKey
        choice_widget="";
        multiple=request.REQUEST.get("multiple",False)
        if multiple=="F" or multiple=="False":
            multiple=False
        elif multiple=="T" or multiple=="True":
            multiple=True
            choice_widget+="Mul"
        else:
            multiple=False
        popup=request.REQUEST.get("popup",False)
        if popup=="F":
            popup=False
        elif popup=="T":
            popup=True
            choice_widget+="Pop"
        else:
            popup=False
        
        filter = request.REQUEST.get("filter", '')
        
        choice_widget="Z"+choice_widget+"EmpChoiceWidget"
        name=request.REQUEST.get("name","emp")
        f=globals()[choice_widget]()
        f.multiple=multiple
        f.popup=popup
        html=f.render(name, "", None, filter)
        return HttpResponse(html)
