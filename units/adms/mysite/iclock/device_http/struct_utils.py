# coding=utf-8

class post_urlPara_handlers(object):
    post_urlPara_dic = {}
    def __init__(self):
        pass
    
    @staticmethod
    def add(handler):
        post_urlPara_dic[handler.name] = handler
        
    @staticmethod
    def add_multy(handler):
        post_urlPara_dic[handler.name] = handler
    
    class handler(object):
        def __init__(self,name,action=None,if_break=True):
            self.name = name
            self.value = ''
            self.action = action
            self.if_break = if_break
            add(self)
        def do_action(self,request, device):
            self.value = request.REQUEST.get(self.name, None)
            if self.action and self.value:
                re = self.action(request, device,self.value)
                return re        
                
    @staticmethod
    def action(request, device):
        for e in post_urlPara_dic.iterkeys():
            handler_ = post_urlPara_dic[e]
            if handler_.if_break:
                re = handler_.do_action(request, device)
                return re
        return 'UNKNOWN'
            
    @staticmethod
    def action_late(request, device):
        for e in post_urlPara_dic.iterkeys():
            handler_ = post_urlPara_dic[e]
            if not handler_.if_break:
                re = handler_.do_action(request, device)
            
    @staticmethod        
    def get(key):
        if post_urlPara_dic.has_key(key):
            return post_urlPara_dic[key].value
        else:
            request.REQUEST.get(key, None)