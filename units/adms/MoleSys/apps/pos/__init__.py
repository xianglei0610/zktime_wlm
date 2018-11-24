# -*- coding: utf-8 -*-

menus = (
         ('pos_simulate',u'模拟操作', 'grup_alarm'),
         )

####### 自定义视图 #########


import routes

from mole.const import TEMPLATE_PATH
TEMPLATE_PATH.append('./apps/pos/templates/')