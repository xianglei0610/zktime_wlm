# -*- coding: utf-8 -*-
'''
此文件包含与通讯有关的文件
'''
import os
import datetime
import base64
from django.conf import settings


def load_pos_file(file_path=None):
    '''
    从文件中加载消费记录
    '''
    path=(settings.C_ADMS_PATH%u"zkpos")
    if file_path:
        try:
            fs=file(file_path,"r+")
            data=fs.read()
#            m_data = base64.decodestring(data).splitlines()
            head_data, raw_data=data.split("\n",1)
            m_data = raw_data.splitlines()
            fs.close()
            return None,head_data,m_data
        except:
#            import traceback;traceback.print_exc()
            return None,None,None
    files = os.listdir(path)
    m_fn = None
    m_data = []
    if len(files)>0:
        try:
            m_fn = files[0]
            fs=file(path+m_fn,"r+")
            data=fs.read()
#            m_data = base64.decodestring(data)  
            fs.close()
            head_data = None
            m_data = None
            if data:
                head_data, raw_data=data.split("\n",1)
                m_data = raw_data.splitlines()
#            print "m_data==============",m_data
            return path+m_fn, head_data, m_data
        except:
            import traceback;traceback.print_exc()
    else:
        return None,None,None

def save_pos_file(device,data,logtype = None):
    '''
    保存消费记录到文件
    '''
    import datetime
    tnow=datetime.datetime.now()
    m_f=("000"+str(tnow.microsecond/1000))[-3:]
    if logtype:
        filename=device.sn+'_'+tnow.strftime("%Y%m%d%H%M%S")+m_f+'_'+logtype+".txt"
    else:
        filename=device.sn+'_'+tnow.strftime("%Y%m%d%H%M%S")+m_f+".txt"
    path=settings.C_ADMS_PATH%u"zkpos"
    if not os.path.exists(path):
        os.makedirs(path)
    f= file(path+filename,"a+")
    f.write(data)
#    f.write(base64.encodestring(data))
    f.close()
