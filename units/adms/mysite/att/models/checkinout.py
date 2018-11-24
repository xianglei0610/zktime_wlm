# -*- coding: utf-8 -*-

from base.custom_model import AppPage,GridModel

class CheckInOut(AppPage):
    verbose_name=u'原始记录表'
    app_menu ="att"
    menu_index= 8
    visible = True
    template = 'app_page_checkinout.html'
    
#    def context(self):
#        from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
#        from mysite.utils import GetFormField
#        m_field = EmpPoPMultForeignKey(verbose_name=u'选择人员',blank=True,null=True)
#        emp = GetFormField("emp",m_field)
#        return {"empfield" :emp}
#        {% autoescape off %}
#        <td><div class="lineH22">{{ empfield|field_as_label_tag }}</div></td><td>{{empfield.as_widget}}</td>
#        {% endautoescape %}
