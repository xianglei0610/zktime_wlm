# -*- coding: utf-8 -*-

from base.custom_model import GridModel
from django.utils.translation import ugettext as _
from mysite import sql_utils
from mysite.utils import get_option
from  datetime   import datetime,date,time,timedelta
class LostCardReport(GridModel):
    verbose_name=_(u'挂失解挂表')
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
        if get_option("POS_ID"):
            self.head = (('badgenumber',u'人员编号'),('name',u'姓名'),('card_no',u'卡号'),('card_type',u'卡类'), ('cardstatus',u'卡状态'),('time',u'操作时间'),('create_operator',u'创建者'))
        else:
            self.head = (('badgenumber',u'人员编号'),('name',u'姓名'),('card_no',u'卡号'),('sys_card_no',u'卡账号'),('card_type',u'卡类'), ('cardstatus',u'卡状态'),('time',u'操作时间'),('create_operator',u'创建者'))
        super(LostCardReport, self) .__init__()
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
        self.grid.colum_trans["cardstatus"] = f_status
        #设置 colum 属性
        self.grid.fields["badgenumber"]["width"]=150
        self.grid.fields["name"]["width"]=150
        self.grid.fields["card_no"]["width"]=150
        self.grid.fields["card_type"]["width"]=150
        self.grid.fields["cardstatus"]["width"]=150
        self.grid.fields["time"]["width"]=150
        self.grid.fields["create_operator"]["width"]=150
        if get_option("POS_IC"):
            self.grid.fields["sys_card_no"]["width"]=150
            
    def MakeData(self,request,**arg):
        sql_add = ""
        st=request.REQUEST.get('ComeTime','')
        et=request.REQUEST.get('EndTime','')
        st=datetime.strptime(st,'%Y-%m-%d')
        et=datetime.strptime(et,'%Y-%m-%d')
        et=et+timedelta(days=1)
        operate=request.REQUEST.get('operate','')
        if operate!="9999":
            sql_add +=" and l.create_operator='%s' "%operate
        
        et=et+timedelta(days=1)
        if st and et:
            params={"st":st,"et":et}
            if get_option("POS_ID"):
                sql = sql_utils.get_sql('id_report_sql',sqlid='get_id_lost_card_report_sql',app='pos',params=params)
                sql+= sql_add
            else:
                sql = sql_utils.get_sql('ic_report_sql',sqlid='get_ic_lost_card_report_sql',app='pos',params=params)
                sql+= sql_add
            self.grid.sql = sql
        else:
            self.SetBlank()
