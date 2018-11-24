# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg
from mysite.pos.models.report_models.report_utils import posreport,get_grid_arg
class GetDeptSummaryReport(GridModel):
    verbose_name=_(u'部门汇总表')
    app_menu ="pos"
    menu_index=3
    visible = False
    template = 'grid_data.html'
    report_typeid = '120'
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
        from get_head import get_posreprots_fields
        self.head,FieldNames,FieldCaption = get_posreprots_fields(self.report_typeid)
        super(GetDeptSummaryReport, self) .__init__()
        #设置 colum_trans 属性
        def f_datetime(r, val):
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%Y-%m-%d %H:%M:%S')
        for i in FieldNames:
            self.grid.fields[i]["width"]=100
        self.grid.fields["pos_date"]["width"]=180
    def MakeData(self,request,**arg):
#        userids= get_grid_arg(request)
##        self.Paging(arg['offset'],item_count=len(userids))
##        userids = userids[self.grid._begin:self.grid._end]
#        print "len============userids===========",len(userids)
#        if userids :
        userids = []
        posreport(self,request,userids,self.report_typeid,**arg)
#        else:
#            self.SetBlank()
       
