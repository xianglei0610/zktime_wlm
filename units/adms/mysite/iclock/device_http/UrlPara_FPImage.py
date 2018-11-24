# -*- coding: utf-8 -*-
import os
from dbapp.additionfile import save_model_file

def cdata_post_fpimage(device, raw_data, head):
    '''
    FPImage 时间戳时
    '''
    pin, fid, image_file=(head['PIN'], head['FID'], head['FPImage'])
    fName = os.path.split(image_file)[1]
    fName = os.path.splitext(fName)
    save_model_file(Template, 
        "%s/%s/%s-%s%s" % (pin, fid, device.id, fName[0].split("_")[-1], fName[1]), 
        raw_data, "fpimage") 
    return "FP"