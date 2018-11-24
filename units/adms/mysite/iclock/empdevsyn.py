#coding=utf-8

from mysite.iclock.models import *
from mysite.iclock.dataprocaction import append_dev_cmd


def dispatchEmpToAll(emp):
        for dev in Device.objects.all():
                if (dev.State<>DEV_STATUS_PAUSE) and not dev.DelTag:
                        s=getEmpCmdStr(emp)
                        append_dev_cmd(dev, s)

def deleteEmpFromAll(pin):
        for dev in Device.objects.all():
                append_dev_cmd(dev, "DATA DEL_USER PIN=%s"%pin)
