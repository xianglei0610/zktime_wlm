from service_utils import main, CmdService
import os
import sys
import redis_self
from subprocess import Popen

path=os.path.split(__file__)[0]

def start_q_server(stdout=None):
    exe_name=redis_self.__path__[0]+"/redis-server"
    if not os.name=='posix': exe_name+=".exe"
    return Popen(exe_name, stdout=stdout)

class QueqeService(CmdService):
    _svc_name_ = "iClockQueqeService"
    _svc_display_name_ = "iClock Queqe Service"
    path = path
    def cmd_and_args(self):
        q=redis_self.Redis(host='localhost', port=6379, db=0)
        try:
            q.ping()
        except redis_self.exceptions.ConnectionError: 
            return start_q_server(self.logger.handlers[0].stream)
        except redis_self.exceptions.InvalidResponse:
            pass
    def stop_fun(self, process):
        if not process: return
        q=redis_self.Redis(host='localhost', port=6379, db=0)
        q.save()
    
if __name__=='__main__':
    main(QueqeService)
    