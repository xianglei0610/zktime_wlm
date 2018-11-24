# -*- coding: utf-8 -*-

from base.custom_model import AppPage,GridModel
from mysite.pos.pos_constant import NEW_CONSUMER_SUMMARY_REPORT
class ConsumerSummaryReport(AppPage):
    verbose_name=u'统计报表'
    app_menu ="pos"
    menu_index= 7
    visible = NEW_CONSUMER_SUMMARY_REPORT
    template = 'app_page_summary_report.html'
    
    def context(self):
        from mysite.personnel.models.model_emp import EmpPoPMultForeignKey
        from mysite.utils import GetFormField
        m_field = EmpPoPMultForeignKey(verbose_name=u'选择人员',blank=True,null=True)
        emp = GetFormField("emp",m_field)
        return {"empfield" :emp}
