from service_utils import main, DjangoService
import os
import sys

path=os.path.split(__file__)[0]

class ServiceBackupDB(DjangoService):
    _svc_name_ = "ZKECOBackupDB"
    _svc_display_name_ = "ZKECO Backup Database"
    _svc_deps_ = [""]
    path = path
    cmd_and_args=["dbadmin"]
    
if __name__=='__main__':
    main(ServiceBackupDB)
