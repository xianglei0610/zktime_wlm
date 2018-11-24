# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg

class RecAbnormite(GridModel):
    verbose_name=_(u'统计结果详情表')
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_data.html'
    head = (('badgenumber',u'人员编号'),('name',u'姓名'),('checktime',u'考勤时间'),('CheckType',u'考勤状态'), ('NewType',u'更正状态'))
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
        super(RecAbnormite, self) .__init__()
        #设置 colum_trans 属性
        def f_datetime(r, val):
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%Y-%m-%d %H:%M:%S')
        ATTSTATES=(("I",u"上班签到"),("O",u"下班签退"),("0", u"上班签到"),("1", u"下班签退"),("8",u"就餐开始"),("9",u"就餐结束"),("2",u"外出"),("3",u"外出返回"),("4",u"加班签到"),("5",u"加班签退"),("255",u"未设置状态"))
        m_dic = {}
        m_dic.update(ATTSTATES)
        def f_attstatu(r,val):
            try:
                return m_dic[str(val)]
            except:return u"未知"
        
        self.grid.colum_trans["checktime"] = f_datetime
        self.grid.colum_trans["CheckType"] = f_attstatu
        self.grid.colum_trans["NewType"] = f_attstatu
        #设置 colum 属性
        self.grid.fields["badgenumber"]["width"]=100
        self.grid.fields["name"]["width"]=100
        self.grid.fields["checktime"]["width"]=180
        self.grid.fields["CheckType"]["width"]=100
        self.grid.fields["NewType"]["width"]=100
    def MakeData(self,request,**arg):
        userids,d1,d2 = parse_grid_arg(request)
        if userids and d1 and d1:
            params={"userids": ','.join(userids),"st":d1,"et":d2}
            self.grid.sql = sql_utils.get_sql('sql',sqlid='get_tjjgxq_report_sqla',app='att',params=params)
        else:
            self.SetBlank()
