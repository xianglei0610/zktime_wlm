# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from mysite.iclock.models.model_device import Device
@login_required
def get_acc_dev(request):
    from mysite.iclock.models.model_device import DEVICE_ACCESS_CONTROL_PANEL
    from django.utils.encoding import smart_str
    from django.utils.simplejson  import dumps
    devs = Device.objects.filter(device_type=DEVICE_ACCESS_CONTROL_PANEL,enabled=True)
    list = []
    if devs:
        for dev in devs:
            l = [dev.id,dev.alias]
            list.append(l)
    return HttpResponse(smart_str(dumps(list)))

#验证输入的旧的通讯密码是否正确
@login_required
def check_old_commpwd(request):
    from base.crypt import encryption
    old_commpwd = request.POST.get("old_commpwd")
    device = request.POST.get("device")
    iclock = Device.objects.filter(id=device)
    if encryption(old_commpwd) == iclock[0].comm_pwd or old_commpwd == iclock[0].comm_pwd:
        return HttpResponse("ok")
    else:return HttpResponse("error")
    
#获取每个设备的控制器类型
@login_required
def get_dev_use_type(request):  
    dev_id = request.GET.get("dev_id")
    #dev_id = int(dev_id)
    dev_idstr = str(dev_id)
    #print "........type of= ",dev_id
    dev = Device.objects.filter(pk=dev_idstr)
    if dev is not None:
        acp_use = dev[0].is_elevator
    #print "//////////ggacptype=",acptype
    #if acptype is null:
        #acptype = "error"
    from dbapp.utils import getJSResponse
    from django.utils.encoding import smart_str
    from django.utils.simplejson  import dumps 
    
    return HttpResponse(smart_str(dumps(acp_use)))
