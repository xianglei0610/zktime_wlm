# coding=utf-8

from django.conf import settings

def pre_proccess(raw_Data):
    if settings.ENCRYPT:
        import lzo
        rawData = lzo.bufferDecrypt(raw_Data, device.sn)#---解密POST数据
    else:
        rawData = raw_Data
    return rawData