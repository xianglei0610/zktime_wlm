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

EMPID = {'currentID':None,'id':None}

def render_emp_widget(name, data, multiple, popup, filter):
    from mysite.personnel.models import Employee
    from mysite.meeting.models.meeting_emp import MeetingEmp
    from mysite.meeting.models.meeting_exact import MeetingExact
    from mysite.meeting.models.meeting_leave import Leave
    from dbapp.urls import dbapp_url
    from mysite.urls import surl
    
    js_attrs={}
    
    try:
        
        if type(data) == list:
            data = ','.join(d for d in [str(i) for i in data])
#        print '====name===data======',name,data,multiple,popup,filter
#        if data and (name == "employee" or name == "user"):
#            try:
#                meetingEmp = MeetingEmp.objects.get(id=data)
#                data = meetingEmp.user.id
#                print 'data===',data
#            except:
#                pass
#                e = Employee.objects.get(id=data)
#                print '=====pin',e.PIN
#                meetingEmp = MeetingEmp.objects.get(user=e)
#                data = meetingEmp.id

        url=data and ("/%s%s/select_meeting_emp_data/?id__exact=%s"%(surl,Employee._meta.app_label,data)) or ("/%s%s/select_meeting_emp_data/?%s"%(surl, Employee._meta.app_label, filter))
        date_now=datetime.datetime.now()
        str_now=str(date_now.strftime('%Y%m%d%H%M%S'))+str(date_now.microsecond)
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
                            +"<script> $.zk._select_emp(%s);</script>"%(json_attrs) \
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

class ZMulEmpChoiceWidget(forms.SelectMultiple):
    popup=False
    def __init__(self, attrs={}, choices=()):
            super(ZMulEmpChoiceWidget, self).__init__(attrs=attrs, choices=choices)
    def value_from_datadict(self, data, files, name):
#        from django.utils.datastructures import MultiValueDict, MergeDict
#        if isinstance(data, (MultiValueDict, MergeDict)):
#            dept_all = data.getlist("dept_all")#'on'或者''
#                
#            if dept_all:#选择部门下所有人员
#                dept_id = data.getlist("deptIDs")
#                #print '------dept_id=',dept_id
#                from mysite.personnel.models import Employee
#                return [e.pk for e in MeetingEmp.objects.filter(DeptID__in = dept_id)]
#            else:
#                return data.getlist(name)
#        else:
#            return data.get(name, None)
        from django.utils.datastructures import MultiValueDict, MergeDict
        from mysite.personnel.models import Employee
        from mysite.personnel.models.empwidget import filter_for_select_emp
        from mysite.iclock.iutils import get_dept_from_all,get_max_in

        if isinstance(data, (MultiValueDict, MergeDict)):
            dept_all = data.getlist(u"%s_dept_all"%name)#'on'或者''
            if dept_all:#选择部门下所有人员
                dept_id = data.getlist("deptIDs")
                deptIDschecked_child = data.get("deptIDschecked_child")
                if deptIDschecked_child == "on":
                    request=get_current_request()
                    dept_id = get_dept_from_all(dept_id,request)
                UserID = get_max_in(filter_for_select_meetingemp(data),dept_id,"DeptID__in")
                print "data",data
                print "data.meetingid",data.getlist("meetingID")
                print"------------" ,int(data.getlist("meetingID")[0])
                
                print "UserID",UserID
                u=[e.pk for e in UserID]

                return u
            else:
                return data.getlist(name)
        else:
            return data.get(name, None)
    
    def render(self, name, data, attrs=None, filter=None):
            if attrs: self.attrs.update(attrs)
            if 'id' not in self.attrs: self.attrs['id']='id_'+name
            self.attrs = self.build_attrs(self.attrs, name=name)
            return render_emp_widget(name, data, True, self.popup, filter)
def filter_for_select_meetingemp(data):
    from mysite.meeting.models.meeting_emp import MeetingEmp
    from mysite.personnel.models.model_emp import Employee
    ids=MeetingEmp.objects.filter(meetingID=int(data.getlist("meetingID")[0])).values_list('user')
    print "ids",ids
    qs = Employee.objects.all().filter(id__in=ids)
    return qs
class ZMulPopEmpChoiceWidget(ZMulEmpChoiceWidget):
    popup=True
class ZPopEmpChoiceWidget(ZEmpChoiceWidget):
    popup=True
    
#multiple=F&popup=F
def get_widget_for_select_emp(request,multiple=False,popup=False):
        from dbapp.widgets import form_field
        from mysite.personnel.models.model_emp import  EmpForeignKey
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
