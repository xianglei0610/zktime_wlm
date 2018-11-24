# coding=utf-8

from django.http import HttpResponse

def device_response_write(msg=""):
    '''
    生成标准的设备通信响应头
    '''
    response = HttpResponse(mimetype='text/plain')  #文本格式
    response["Pragma"]="no-cache"                   #不要缓存，避免任何缓存，包括http proxy的缓存
    response["Cache-Control"]="no-store"            #不要缓存
    if msg:
        response["Content-Length"] = len(msg)
        #print 'ret>>>>>>>>>>>>>>>>:',msg,type(msg)
        response.write(msg)
    return response

def unknown_device_response():
    return device_response_write('UNKNOWN DEVICE')

def unknown_data_response(device):
    resp = ""
    resp += "UNKOWN DATA\n"
    resp += "POST from: " + device.sn + "\n"
    return device_response_write(resp)

def unknown_response():
    return device_response_write('UNKNOWN')

def ok_response():
    print '>>>>>>>>>>>>>>'
    return device_response_write('OK\n')

def none_response():
    '''
    如:人员不存在
    '''
    return device_response_write('NONE\n')

def erro_response(e):
    resp = u"ERROR: %s" % e
#    errorLog(request)
    return device_response_write(resp)

def device_response_decode_write(msg=""):
    resp = ""
    try:
        resp = msg.encode("gb18030")
    except:
        resp = msg.decode("utf-8").encode("gb18030")
    return device_response_write(resp)

def auth_failed():
    resp = u'AUTH=Failed\n'
    return device_response_write(resp)