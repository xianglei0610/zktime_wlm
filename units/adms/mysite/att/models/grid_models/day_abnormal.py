# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg

class DayAbnormal(GridModel):
    verbose_name=_(u'考勤异常日报')
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_data.html'
    head = (('userid',u'用户ID'),('DeptName',u'部门名称'),('badgenumber',u'人员编号'),('name',u'姓名'),('att_date',u'日期'),('late',u'迟到分钟'),('early',u'早退分钟'),('absent',u'旷工时间'),('late_times',u'迟到次数'),('early_times',u'早退次数'),('absent_times',u'旷工次数'),('worktime',u'上班时间'))
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
        super(DayAbnormal, self) .__init__()
        self.grid.fields["badgenumber"]["width"]=70
        self.grid.fields["att_date"]["width"]=70
        self.grid.fields["late"]["width"]=75
        self.grid.fields["early"]["width"]=75
        self.grid.fields["absent"]["width"]=75
        self.grid.fields["late_times"]["width"]=75
        self.grid.fields["early_times"]["width"]=75
        self.grid.fields["absent_times"]["width"]=75
        self.grid.fields["worktime"]["width"]=75
        self.SetHide("userid")
    def MakeData(self,request,**arg):
        userids,d1,d2 = parse_grid_arg(request)
        if userids and d1 and d1:
            params={"userids": ','.join(userids),"st":d1,"et":d2}
            self.grid.sql = sql_utils.get_sql('sql',sqlid='day_abnormal',app='att',params=params)
        else:
            self.SetBlank()
