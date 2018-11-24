# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.utils import get_option
from  datetime   import datetime,date,time,timedelta
class PosReplenishCard(GridModel):
    verbose_name=_(u'换卡表')
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
        self.head = (('badgenumber',u'人员编号'),('name',u'姓名'),('old_card_no',u'原卡号'),('new_card_no',u'现卡号'),('time',u'换卡时间'),('create_operator',u'创建者'))
        super(PosReplenishCard, self) .__init__()
        #设置 colum_trans 属性
        
        def f_datetime(r, val):
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%Y-%m-%d %H:%M:%S')
        
   
        CARDSTATUS = (
                ('1', _(u'解挂')),
                ('3', _(u'挂失')),
        )
        m_status_dic = {}
        m_status_dic.update(CARDSTATUS)
        def f_status(r,val):
            try:
                return m_status_dic[str(val)]
            except:return u"未知"
        
                
        self.grid.colum_trans["time"] = f_datetime
        #设置 colum 属性
        self.grid.fields["badgenumber"]["width"]=100
        self.grid.fields["name"]["width"]=100
        self.grid.fields["old_card_no"]["width"]=100
        self.grid.fields["new_card_no"]["width"]=100
        self.grid.fields["time"]["width"]=150
        self.grid.fields["create_operator"]["width"]=100
            
    def MakeData(self,request,**arg):
        sql_add = ""
        st=request.REQUEST.get('ComeTime','')
        et=request.REQUEST.get('EndTime','')
        st=datetime.strptime(st,'%Y-%m-%d')
        et=datetime.strptime(et,'%Y-%m-%d')
        et=et+timedelta(days=1)
        operate=request.REQUEST.get('operate','')
        if operate!="9999":
            sql_add +=" and r.create_operator='%s' "%operate
        
        et=et+timedelta(days=1)
        if st and et:
            params={"st":st,"et":et}
            sql = sql_utils.get_sql('id_report_sql',sqlid='get_id_replenish_card_report_sql',app='pos',params=params)
            sql+= sql_add
            self.grid.sql = sql
        else:
            self.SetBlank()
