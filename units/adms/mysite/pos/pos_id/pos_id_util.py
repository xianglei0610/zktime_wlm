# -*- coding: utf-8 -*-
from django.core.cache import cache
from mysite.pos.pos_constant import TIMEOUT
from mysite.utils import get_option
def set_pos_info_record():
    if get_option("POS_ID"):
        from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
        device_list = Device.objects.filter(device_type=DEVICE_POS_SERVER)
        for obj in device_list:
            key = str(obj.sn).strip()+"_update_db"
            cache.set(key,1,TIMEOUT)
   