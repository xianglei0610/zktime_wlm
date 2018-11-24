# -*- coding: utf-8 -*-

import re

from django.conf import settings

#IPv4 地址格式正则
IP4_RE = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')

REALTIME_EVENT="RT_EVENT_%s"%settings.UNIT
MAX_TRANS_IN_QUEQE=10000
DEVICE_POST_DATA="DEVICE_POST_DATA"

DEVELOP_MODEL = False
import dict4ini
att_file = dict4ini.DictIni("attsite.ini")
COMM_PRINT = att_file["Options"]["COMM_PRINT"]
if COMM_PRINT.lower()=="true":
    DEVELOP_MODEL = True

SYNC_MODEL = True
ENCRYPT = False

ATT_DEAL_BAT_SIZE = 50

DEVICE_CREATEUSER_FLAG = True #是否允许设备更新人员信息到服务器
DEVICE_CREATEBIO_FLAG = True    #是否允许设备更新指纹到服务器
DEVICE_CREATECARD_FLAG = False    #是否允许设备更新卡号到服务器

EN_EMP_PIC = True

PUSH_COMM_KEY_CHECK =False