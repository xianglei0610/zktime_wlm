from service_utils import main, DjangoService
import os
import sys

path=os.path.split(__file__)[0]

class ServiceInstantMsg(DjangoService):
    _svc_name_ = "ZKECOInstantMessage"
    _svc_display_name_ = "ZKECO Worktable Instant Message"
    _svc_deps_ = [""]
    path = path
    cmd_and_args=["instantmsg"]
    
if __name__=='__main__':
    main(ServiceInstantMsg)
    
