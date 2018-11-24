from service_utils import main, DjangoService
import os

path=os.path.split(__file__)[0]

class iClockDBPoolService(DjangoService):
    _svc_name_ = "iClockDBPoolService"
    _svc_display_name_ = "iClock DB Pool Service"
    _svc_deps_ = ["iClockQueqeService"]
    path = path
    cmd_and_args=["writedata"]

if __name__=='__main__':
    main(iClockDBPoolService)
    
