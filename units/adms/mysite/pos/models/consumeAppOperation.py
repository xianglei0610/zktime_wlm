#coding=utf-8

from mysite.settings import MEDIA_ROOT
from base import get_all_app_and_models
from django.shortcuts import render_to_response
from django.template import Context, RequestContext

from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from mysite.utils import get_option
from mysite.pos.pos_constant import OLD_CONSUMER_REPORT,OLD_CONSUMER_SUMMARY_REPORT
from mysite.pos.views import consumeReport

class consumeAppReport(AppOperation):
    from mysite.pos.models.model_cardmanage import CardManage
    from mysite.pos.models.model_loseunitecard import LoseUniteCard
    from mysite.pos.models.model_replenishcard import ReplenishCard
    verbose_name = _(u'消费报表')
    view = consumeReport
    _menu_index = 6
    visible = OLD_CONSUMER_REPORT
    _app_menu = 'pos'
    _menu_group = 'pos'
    add_model_permission=[CardManage,LoseUniteCard,ReplenishCard]
    _disabled_perms=['change_cardmanage','browse_cardmanage','add_cardmanage','dataexport_cardmanage','delete_cardmanage',
                     'change_loseunitecard','browse_loseunitecard','add_loseunitecard','dataexport_loseunitecard','delete_loseunitecard',
                     'change_replenishcard','browse_replenishcard','add_replenishcard','dataexport_replenishcard','delete_replenishcard',
    ]
    _select_related_perms={
            "can_consumeAppReport":"browse_replenishcard.dataexport_replenishcard.browse_loseunitecard.dataexport_loseunitecard.browse_cardmanage.dataexport_cardmanage.browse_issuecard.dataexport_issuecard.browse_carcashsz.dataexport.carcashsz",
   }

    

class PosReport(AppOperation):
    from mysite.pos.views import fun_posreport
    verbose_name = _(u'统计报表')
    view = fun_posreport
    visible = OLD_CONSUMER_SUMMARY_REPORT
    _menu_index = 7
    _app_menu = 'pos'
    _menu_group = 'pos'
    


        
class pos_guide(AppOperation):
        from mysite.pos.views import funPosGuide
        verbose_name = _(u'导航')
        view = funPosGuide
        _menu_index = 0
        _app_menu = 'pos'
        _menu_group = 'pos'

    
    
class PosDeviceDataManage(AppOperation):
        from mysite.pos.views import funPosDeviceDataManage 
        u'''消费设备管理'''
        verbose_name=_(u'消费设备管理')
        view=funPosDeviceDataManage
        visible=get_option("POS")
        _app_menu ='pos'
        _menu_group = 'pos'
        _menu_index=9
        
#class PosCarManage(AppOperation):
#        from mysite.pos.views import funPosCarManage 
#        u'''消费卡管理'''
#        verbose_name=_(u'消费卡管理')
#        view=funPosCarManage
#        visible=False
#        _app_menu ='pos'
#        _menu_group = 'pos'
#        _menu_index=4
        
#class SettingOp(AppOperation):
#    from mysite.pos.views import renderLeftOp 
#    verbose_name = _(u'补贴设置')
#    view = renderLeftOp
#    #_menu_index = 100041
#    _app_menu = 'pos'
#    _menu_group = 'pos'
#    
#    _template = "Allowance_SettingOp.html"
#    _position = _(u'pos -> 补贴设置')
    
    

