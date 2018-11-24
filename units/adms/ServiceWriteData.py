from service_utils import main, DjangoService
import os
import sys


path=os.path.split(__file__)[0]

class WriteDataService(DjangoService):
    _svc_name_ = "ZKECOWriteDataService"
    _svc_display_name_ = "ZKECO Write Data Service"
    _svc_deps_ = []
    path = path
    cmd_and_args=["writedata"]
    
if __name__=='__main__':
    main(WriteDataService)
    