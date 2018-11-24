# coding=utf-8

def network_monitor(request):
    from constant import DEVELOP_MODEL
    if DEVELOP_MODEL:
        print '##################### network_monitor ##########################'
        print 'url-----------------',request.path
        print 'method-----------',request.method
        print 'raw_post_data----',request.raw_post_data
        print 'post --------------',request.POST
        print 'get ---------------',request.GET
        print '#############################################################'
        return 0

def simple_response(content):
    response["Content-Length"] = len(content)
    response.write(content)    #---返回服务器对设备的验证结果
    return response