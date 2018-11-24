# -*- coding: utf-8 -*-

from mosys.custom_model import AppPage,GridModel
from mosys import forms
from ooredis import *

class EmployeeReport(GridModel):
    '''
    人员报告
    '''
    verbose_name=u'Redis中人员报告'
    app_menu ="personnel"
    menu_grup = 'att_monitor'
    icon_class = "menu_people"
    menu_index=15
    visible = True
    head = [('pin',u'工号'),('EName',u'姓名'),('Card',u'卡号'),('Password',u'密码'),('area',u'区域'),('device',u'设备'),('fingerprint',u'指纹'), ('face',u'面部'), ('employeepic',u'用户照片')]
    search_form = [
                   ('pin',forms.CharField(label=u'工号'))
                   ]
    option = {
            "usepager": True,
            "useRp": True,
            "rp": 20,
            "height":350,
            'checkbox' : False,
            "showTableToggleBtn":True,
            "buttons":[{"name": '导出xls', "bclass": 'export_xls', "onpress" : '$do_export$'}],
              }
    def __init__(self, request):
        super(EmployeeReport, self) .__init__()
        self.grid.fields["area"]["width"]=200
        self.grid.fields["device"]["width"]=350
    
    def MakeData(self,request,**arg):
        #添加数据
        from ooredis.client  import get_client
        m_client = get_client()
        m_pin = request.params.get('pin',None)
        if m_pin:
            keys = m_client.keys("employee:*%s*:info"%m_pin)
        else:
            keys = m_client.keys("employee:*:info")
        self.Paging(arg['offset'],item_count=len(keys))
        m_keys = keys[self.grid._begin:self.grid._end]
        self.grid.InitItems()
        for e in m_keys:
            r = self.grid.NewItem()
            emp = Dict(e)
            r["pin"] = e.split(':')[1]
            r["EName"] = emp["EName"]
            r["Card"] = emp["Card"]
            r["Password"] = emp["Password"]
            m_area = Set('employee:%s:areas'%r["pin"])
            if m_area:
                r["area"] = ', '.join(m_area)
            else:
                r["area"] = ''
            m_device = Set('employee:%s:devices'%r["pin"])
            if m_area:
                r["device"] = ', '.join(m_device)
            else:
                r["device"] = ''
            m_keys = m_client.keys("fingerprint:%s|*"%r["pin"])
            if len(m_keys)>0:
                r["fingerprint"] = '有'
            else:
                r["fingerprint"] = ''
            m_keys = m_client.keys("face:%s|*"%r["pin"])
            if len(m_keys)>0:
                r["face"] = '有'
            else:
                r["face"] = ''
            m_keys = m_client.keys("employeepic:%s"%r["pin"])
            if len(m_keys)>0:
                r["employeepic"] = '有'
            else:
                r["employeepic"] = ''
            self.grid.AddItem(r)