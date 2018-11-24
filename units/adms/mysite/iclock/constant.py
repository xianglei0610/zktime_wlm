from django.conf import settings

import re
IP4_RE = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')

REALTIME_EVENT="RT_EVENT_%s"%settings.UNIT
MAX_TRANS_IN_QUEQE=10000
DEVICE_POST_DATA="DEVICE_POST_DATA"

