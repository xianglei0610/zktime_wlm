from service_utils import main, DjangoService
import os
import sys


path=os.path.split(__file__)[0]

class AutoCalculateService(DjangoService):
    _svc_name_ = "ZKECOAutoCalculateService"
    _svc_display_name_ = "ZKECO Automatic Calculate Service"
    _svc_deps_ = []
    path = path
    cmd_and_args=["autocalculate"]
    
if __name__=='__main__':
    main(AutoCalculateService)
    