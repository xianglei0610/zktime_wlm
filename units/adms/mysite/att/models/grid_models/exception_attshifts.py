# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg
from mysite.att.report_utils import NormalAttValue

class ExceptionAttshifts(GridModel):
    verbose_name=_(u'时段异常情况')
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_data.html'
    head = (('LeaveName',u'请假类别'),('scope',u'时长'),('id', u'请假ID'), ('StartSpecDay',u'请假开始'),('EndSpecDay',u'请假结束'),('YUANYING',u'请假原因'))
    option = {
            "usepager": False,
            "useRp": True,
            "rp": 20,
            "height":160,
            "width":617,
            "checkbox" : False,
            "showToggleBtn":True,
            "resizable" : False
              }
    def __init__(self,request):
        super(ExceptionAttshifts, self) .__init__()
        def f_val(r,val):
            val = NormalAttValue(val, r[6], r[7], r[8], 1)
            return val
        self.grid.colum_trans["scope"] = f_val
        self.grid.fields["StartSpecDay"]["width"]=120
        self.grid.fields["EndSpecDay"]["width"]=120
        self.grid.fields["YUANYING"]["width"]=150
        
    def MakeData(self,request,**arg):
        from mysite.att.calculate.global_cache import C_ATT_RULE,C_LEAVE_CLASS
        C_ATT_RULE.action_init()
        C_LEAVE_CLASS.action_init()
        self.SetPageSize(0)
        ids = request.REQUEST.get('ids','')
        if ids:
            params={"ids": ids}
            self.grid.sql = sql_utils.get_sql('sql',sqlid='leave_exception_attshifts',app='att',params=params)
        else:
            self.SetBlank()
