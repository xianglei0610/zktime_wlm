# -*- coding: utf-8 -*-
from mosys.custom_model import AppPage,GridModel

class DeviceReq_ID(AppPage):
    verbose_name=u'ID消费 PUSH 模拟'
    menu_grup = 'pos_simulate'
    template = 'pos_id_info.html'
    pass

class DeviceReq_IC(AppPage):
    verbose_name=u'IC消费 PUSH 模拟'
    menu_grup = 'pos_simulate'
    template = 'pos_ic_info.html'
    pass