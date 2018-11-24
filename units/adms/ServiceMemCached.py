# -*- coding: utf-8 -*-
from service_utils import main, CmdService
import os
import sys
import redis_self
from subprocess import Popen

path=os.path.split(__file__)[0]

class ZKECOMemCachedService(CmdService):
    _svc_name_ = "ZKECOMemCachedService"
    _svc_display_name_ = "ZKECO MemCached Service"
    path = path
    cmd_and_args=["memcached.exe",  "-p 11211 -l 127.0.0.1 -m 128"]
    
if __name__=='__main__':
    main(ZKECOMemCachedService)
    
