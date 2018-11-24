# coding=utf-8

from django.conf import settings
from mysite.utils import get_option

#设备可能的各种时间戳映射字典
STAMPS={'Stamp':'log_stamp', 'OpStamp': 'oplog_stamp', 'FPImage':'FPImage', 'PhotoStamp':'photo_stamp'}
STAMPS_KEY = ['Stamp','OpStamp','FPImage','PhotoStamp']

#消费机类型
POSDEVICE='30'

def device_pin(pin):
        if not settings.PIN_WIDTH: return pin
        if (settings.PIN_SUPPORT_LETTERS and get_option("ONLY_ATT")) or not pin.isdigit(): return pin
        i = 0
        for c in pin[0:-1]:
                if c == "0":
                        i += 1
                else:
                        break
        return pin[i:]

def face_prot(face):
    line = "PIN=%s\tFID=%d\tSIZE=%d\tValid=%d\tTMP=%s\n"%(device_pin(face.user.PIN), face.faceid,len(face.facetemp),face.valid, face.facetemp)
    CMD="DATA UPDATE FACE %s"%(line)
    return CMD

def auth_prot(info):
    ret="AUTH=Success\tPIN=%s\tName=%s\tPri=%s\tGrp=%s\tTZ=%s"%(info["PIN"], info["Name"], info["Pri"], info["Grp"], info["TZ"])
    return ret

def userpic_prot(photo):
    rstr = ""
    if photo:
        import base64
        f = open(photo.file.name,'rb')
        base64_photo=base64.b64encode(f.read())
        f.close()
        len_photo = len(base64_photo)
        if len_photo<=16*1024/0.75:
            rstr += '\tPhotoSize=%s\tPhoto=%s'%(str(len_photo),base64_photo)
            rstr +='\n'
    return rstr.encode("gb18030")

def pos_return():
    resp="Ret=NO\nretnumber=-1\nerrmsg=%s"%u"设备为ID消费机"
    resp = resp.encode("GB18030")
    return resp

#post_urlPara_dic = {}
#
#class post_urlPara_handler(object):
#    def __init__(self,name,action=None,if_break=False):
#        self.name = name
#        self.value = ''
#        self.action = action
#        self.if_break = if_break
#    def do_action(self,request, device):
#        self.value = request.REQUEST.get(self.name, None)
#        if self.action:
#            self.action(request, device,self.value)