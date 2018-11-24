from django.test.client import Client as DClient
from django.conf import settings

class Client(DClient):
        def __init__(self, **kargs):
                self.prefix=settings.UNIT_URL[:-1]
                DClient.__init__(self, **kargs)
        def request(self, **request):
                if 'PATH_INFO' in request:
                        path=self.prefix+request['PATH_INFO']
                else:
                        path=self.prefix
                request['PATH_INFO']=path
                print "\nclient PATH_INFO:", path
                return DClient.request(self, **request)
                
