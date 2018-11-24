#coding=utf-8

from constant import SYNC_MODEL

if SYNC_MODEL:
    from UrlPara_Stamp import sync_cdata_post_trans as cdata_post_trans
else:
    from UrlPara_Stamp import cdata_post_trans
    
from UrlPara_OpStamp import cdata_post_userinfo
from UrlPara_FPImage import cdata_post_fpimage

def get_request_list(request):
    '''
    得到当前请求的时间戳类型
    '''
    from protocol_content import STAMPS_KEY
    for e in STAMPS_KEY:
        val = request.REQUEST.get(e, None)
        if val:
            return (e,val)
    return None