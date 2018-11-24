# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg

class ExceptionSum(GridModel):
    verbose_name=_(u'请假汇总表')
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_data.html'
    option = {
            "usepager": True,
            "useRp": True,
            "rp": 20,
            "height":300,
            "width":1286 ,
            'checkbox' : False,
            "showTableToggleBtn":True,
            "buttons":[{"name": '导出xls', "bclass": 'export_xls', "onpress" : '$do_export$'},
                            {"name": '导出pdf', "bclass": 'export_pdf', "onpress" : '$do_export$'},
                            {"name": '导出csv', "bclass": 'export_csv', "onpress" : '$do_export$'}
                       ],
              }
    def __init__(self,request):
        userids,d1,d2 = parse_grid_arg(request)
        from emp_total import GetHead
        self.head = GetHead(userids,d1,d2,reportType=2)
        super(ExceptionSum, self) .__init__()
        self.grid.fields["badgenumber"]["width"]=70
        self.SetHide("userid")
    def MakeData(self,request,**arg):
        userids,d1,d2 = parse_grid_arg(request)
        if userids and d1 and d1:
            params={"userids": ','.join(userids),"st":d1,"et":d2}
            userids_sql = sql_utils.get_sql('sql',sqlid='exception_emp_ids',app='att',params=params)
            rows = sql_utils.p_query(userids_sql)
            if rows:
                userids = [r[0] for r in rows]
            else:
                userids = []
            
            self.Paging(arg['offset'],item_count=len(userids))
            userids = userids[self.grid._begin:self.grid._end]
            
            from emp_total import ForMakeDataExcepSum
            ForMakeDataExcepSum(self,userids,d1,d2)
        else:
            self.SetBlank()
