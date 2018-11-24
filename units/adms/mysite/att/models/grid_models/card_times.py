# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg

class CardTimes(GridModel):
    verbose_name=_(u'统计结果详情表')
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_data.html'
    head = (('userid',u'用户ID'),('DeptName',u'部门名称'),('badgenumber',u'人员编号'),('name',u'姓名'),('card_date',u'日期'),('times',u'打卡次数'),('card_times',u'打卡时间'))
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
        super(CardTimes, self) .__init__()
        self.SetHide("userid")
        self.grid.fields["DeptName"]["width"]=120
        self.grid.fields["badgenumber"]["width"]=120
        self.grid.fields["name"]["width"]=120
        self.grid.fields["times"]["width"]=120
        self.grid.fields["card_date"]["width"]=180
        self.grid.fields["card_times"]["width"]=380
    def MakeData(self,request,**arg):
        userids,d1,d2 = parse_grid_arg(request)
        if userids and d1 and d1:
            params={"userids": ','.join(userids),"st":d1,"et":d2}
            self.grid.sql = sql_utils.get_sql('sql',sqlid='cardtimes',app='att',params=params)
        else:
            self.SetBlank()
