# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg
from mysite.pos.models.report_models.report_utils import get_pos_list_record,get_grid_arg
from mysite.utils import get_option
from  datetime   import datetime,date,time,timedelta
class GetErrorPosListReport(GridModel):
    verbose_name=_(u'异常消费明细表')
    app_menu ="pos"
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
        from get_head import get_pos_list
        self.head,FieldNames,FieldCaption = get_pos_list()
        super(GetErrorPosListReport, self) .__init__()
        #设置 colum_trans 属性
        def f_datetime(r, val):
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%Y-%m-%d %H:%M:%S')
        for i in FieldNames:
            self.grid.fields[i]["width"]=60
        self.grid.fields["user_pin"]["width"]=80
        self.grid.fields["user_name"]["width"]=100
        self.grid.fields["pos_time"]["width"]=150
        self.grid.fields["dev_sn"]["width"]=100
        if get_option("POS_IC"):
            self.grid.fields["money"]["width"]=150 
            self.grid.fields["convey_time"]["width"]=150 
            self.grid.fields["meal_data"]["width"]=100
    def MakeData(self,request,**arg):
        from report_data import get_ic_error_list_record
        st=request.REQUEST.get('ComeTime','')
        et=request.REQUEST.get('EndTime','')
        st=datetime.strptime(st,'%Y-%m-%d')
        et=datetime.strptime(et,'%Y-%m-%d')
        et=et+timedelta(days=1)
        try:
            get_ic_error_list_record(self,request,st,et,**arg)
        except:
            import traceback;traceback.print_exc()
#       else:
#           self.SetBlank()
       
