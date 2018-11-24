# -*- coding: utf-8 -*-

from base.custom_model import AppPage,GridModel

class AttReport(AppPage):
    verbose_name=u'考勤报表'
    app_menu ="att"
    menu_index= 10
    visible = True
    template = 'app_page_attreport.html'
    
    def context(self):
        from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
        from mysite.utils import GetFormField
        m_field = EmpPoPMultForeignKey(verbose_name=u'选择人员',blank=True,null=True)
        emp = GetFormField("emp",m_field)
        return {"empfield" :emp}