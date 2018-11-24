# -*- coding: utf-8 -*-
class _const:
    u"常量类"
    class ConstError(TypeError):pass
    def __setattr__(self, name, value):
#        if self.__dict__.has_key(name):
#            raise self.ConstError, "Can't rebind const (%s)" % name
        self.__dict__[name] = value
import sys
sys.modules[__name__] = _const()    # 将const类注册到sys.modules
