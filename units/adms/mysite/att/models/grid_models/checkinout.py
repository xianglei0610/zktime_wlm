# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from mysite import sql_utils
from mysite.utils import GetAuthoIDs

class CheckInOutGrid(GridModel):
    verbose_name=u'原始记录数据'
    app_menu ="att"
    menu_index=3
    visible = False
    template = 'grid_checkinout.html'
    head = [('id',u'编号'),('badgenumber',u'人员编号'),('name',u'姓名'),('DeptName',u'部门'),('checktime',u'考勤时间'),('checktype',u'考勤状态'),('sn_name',u'设备序列号')]
    option = {
            "usepager": True,
            "useRp": True,
            "rp": 20,
            "height":350,
            "width":900 ,
            'checkbox' : False,
            "showTableToggleBtn":True,
            "onSuccess":'$band_show_photo$',
            "buttons":[{"name": '导出xls', "bclass": 'export_xls', "onpress" : '$do_export$'},
                            {"name": '导出pdf', "bclass": 'export_pdf', "onpress" : '$do_export$'},
                            {"name": '导出csv', "bclass": 'export_csv', "onpress" : '$do_export$'}
                       ],
              }
    def __init__(self,request):
        super(CheckInOutGrid, self) .__init__()
        #设置sql
        self.grid.sql = sql_utils.get_sql('sql',sqlid='checkinout',app='att')
        #设置 colum 属性
        self.SetHide("id")
        self.grid.fields["name"]["width"]=100
        self.grid.fields["badgenumber"]["width"]=100
        self.grid.fields["name"]["width"]=100
        self.grid.fields["DeptName"]["width"]=100
        self.grid.fields["checktime"]["width"]=150
        self.grid.fields["checktype"]["width"]=100
        self.grid.fields["sn_name"]["width"]=120
   
    def MakeData(self,request,**arg):
        pin = request.REQUEST.get("pin", '')
        userid = request.REQUEST.get("userid", '')
        if pin:
            self.grid.sql += " and badgenumber like '%%%s%%'"%pin
        if userid:
            self.grid.sql += " and u.userid=%s"%userid
        deptcode = request.REQUEST.get("deptcode", '')
        if deptcode:
            self.grid.sql += " and d.code='%s'"%deptcode
        
        start = request.REQUEST.get("start", '')
        if start:
            self.grid.sql += " and checktime>='%s'"%start
        end = request.REQUEST.get("end", '')
        if end:
            self.grid.sql += " and checktime<='%s'"%end
            
        deptids = GetAuthoIDs(request.user,1)
        if deptids:
            self.grid.sql += " and d.DeptID in (%s)"%deptids