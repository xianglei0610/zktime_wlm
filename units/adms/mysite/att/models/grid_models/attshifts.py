# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.att.report_utils import parse_grid_arg

class AttShiftsBase(GridModel):
    verbose_name=_(u'考勤明细表')
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_data_attshifts.html'
    head =(('id',u'编号'),('code',u'部门编号'),('DeptName',u'部门名称'),('badgenumber',u'人员编号'),('name',u'姓名'),
           ('AttDate',u'日期'),('SchName',u'时段名称'), ('ClockInTime',u'上班时间'),('ClockOutTime',u'下班时间'),
           ('StartTime',u'签到时间'),('EndTime',u'签退时间'),('WorkDay',u'应到'),('RealWorkDay',u'实到'),
           ('MustIn',u'应签到'),('MustOut',u'应签退'),('NoIn',u'未签到'),('NoOut',u'未签退'),('Late',u'迟到'),
           ('Early',u'早退'),('AbsentR',u'旷工'),('WorkTime',u'出勤时长'),('Exception',u'例外情况'),
           ('OverTime_des',u'加班时间'),('AttTime',u'时段时间'),('SSpeDayNormalOT',u'平日加班'),
           ('SSpeDayWeekendOT',u'休息日加班'),('SSpeDayHolidayOT',u'节假日加班'))
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
        super(AttShiftsBase, self) .__init__()
        #设置sql
    
        #设置 colum_trans 属性
        def f_date(r,val):
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%Y-%m-%d')
            
        def f_datetime(r,val):
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%m-%d %H:%M')
        def f_exception(r,val):
            if val=="" or val=="None" :
                return ""
            else:
                return '<font color=red>有</font> <a href="javascript:showDetail(\'%s\');" title="">查看明细</a>'%val
        self.grid.colum_trans["AttDate"] = f_date
        self.grid.colum_trans["ClockInTime"] = f_datetime
        self.grid.colum_trans["ClockOutTime"] = f_datetime
        self.grid.colum_trans["StartTime"] = f_datetime
        self.grid.colum_trans["EndTime"] = f_datetime
        self.grid.colum_trans["Exception"] = f_exception
            
        #设置 colum 属性
        self.grid.fields["code"]["width"]=60
        self.grid.fields["DeptName"]["width"]=70
        self.grid.fields["badgenumber"]["width"]=70
        self.grid.fields["name"]["width"]=70
        self.grid.fields["SchName"]["width"]=70
        self.grid.fields["AttDate"]["width"]=70
        self.grid.fields["ClockInTime"]["width"]=70
        self.grid.fields["ClockOutTime"]["width"]=70
        self.grid.fields["StartTime"]["width"]=70
        self.grid.fields["EndTime"]["width"]=70
        self.grid.fields["Exception"]["width"]=70
        self.SetHide("id")
        
    def MakeData(self,request,**arg):
        userids,d1,d2 = parse_grid_arg(request)
        if userids and d1 and d1:
            params={"userids": ','.join(userids),"st":d1,"et":d2}
            self.grid.sql = sql_utils.get_sql('sql',sqlid='attShifts_report_sql',app='att',params=params)
        else:
            self.SetBlank()