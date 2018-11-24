from service_utils import main, DjangoService
import os
import sys


path=os.path.split(__file__)[0]

class ZkposAdmsService(DjangoService):
    _svc_name_ = "ZKECOZkposAdmsService"
    _svc_display_name_ = "ZKECO Zkpos ADMS Service"
    _svc_deps_ = []
    path = path
    cmd_and_args=["zkpos_adms"]
    
if __name__=='__main__':
    main(ZkposAdmsService)
    
