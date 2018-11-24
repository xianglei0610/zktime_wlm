# -*- coding: utf-8 -*-

from ooredis import *

from mosys.custom_model import AppPage

class RedisRedirect(AppPage):
    verbose_name=u'Redis中设备报告'
    menu_grup = 'att_monitor'
    icon_class = "menu_pathing"
    template = 'redis_redirect.html'
    pass
    
    def context(self):
        from apps.zkeco_conf import cfg
        m_client = get_client()
        keys = m_client.keys("device:*:data")
        ret = []
        for e in keys:
            data =  Dict(e)
            sn = e.split(':')[1]
            m_tar = [sn, data["ipaddress"],data["area"]]
            oo_cmd = SortedSet("device:%s:update"%sn)
            m_tar.append(len(oo_cmd))
            ret.append(m_tar)
        return {'table_data':ret,'web_port':cfg['Options']['Port']}