# -*- coding: utf-8 -*-
from django.conf import settings
if settings.DATABASE_ENGINE=='pool':
    settings.DATABASE_ENGINE=settings.POOL_DATABASE_ENGINE

from django.core.management.base import BaseCommand, CommandError
import sys
import datetime
import time
import os
import shutil
from traceback import print_exc
from django.utils.simplejson import dumps
from mysite import settings

def sort_files(fns):
    sf=[]
    ln=len(fns)
    for i in range(ln-1):
        j=i+1
        while j<ln:
            if t_e(fns[i])>t_e(fns[j]):
                tmp=fns[i]
                fns[i]=fns[j]
                fns[j]=tmp
            j+=1
            
            
def t_e(d):
    x=d.split(".")[0]
    if len(x)>17:
        return int((str(d).split("_")[0]+"000000")[:17])
    else:
        return int((x+"000000")[:17])
        
        
def process_data():    
    from mysite.iclock.models.model_device import Device
    from mysite.iclock.device_http.device_view import write_data
    data=""
    devs=Device.objects.filter(device_type=1)
    path=settings.C_ADMS_PATH+"new/"
    tnow=datetime.datetime.now()
    #print tnow,"      device count",len(devs)
    for d in devs: 
        
        #print "current device: ",d.sn
        try:        
            
            objpath=path%d.sn
#            if not os.path.exists(objpath):
#                os.makedirs(objpath)
            
            if os.path.exists(objpath):
                files=[]
                add="000000"
                for f in os.listdir(objpath):                    
                    if os.path.isfile(objpath+f):
                        try:
                            #f=f.split(".")[0]
                            #if len(f)<=17:                                
                            #    fn=int((f+add)[:17])                        
                            files.append(f)
                        except:
                            pass
                if len(files)>1:                    
                    sort_files(files)
                #print files
                for f in files:
                    
                    if os.path.exists(objpath+f):
                        process_flag=True
                        try:        
                            #print "import data file '%s'"%(objpath+f)
                            fs=file(objpath+f,"r+")
                            data=fs.read();                    
                            fs.close()
                            write_data(data,d)
                                
                        except:
                            process_flag=False
                            print_exc()
                        finally:
                            try:
                                f_dir=f[:8]
                                #print "f_dir ",f_dir
                                cf_path=settings.C_ADMS_PATH+f_dir+"/"
                                cf_path=cf_path%d.sn
                                #print cf_path
                                if not os.path.exists(cf_path):
                                    os.makedirs(cf_path)
                                old=f
                                if not process_flag:
                                    f="error_"+f
                                shutil.copy(objpath+old,cf_path+f)
                                os.remove(objpath+old)
                            except:
                                print_exc()
                                pass
            else:
                pass
                #print "path not exists '%s' "%objpath
        except:
            import traceback;traceback.print_exc()
            pass
        time.sleep(0.1)
        
class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "Starts zksaas adms ."
    args = ''

    def handle(self, *args, **options):
        import time,os
        from base.sync_api import SYNC_MODEL, get_att_record_file
        if SYNC_MODEL:
            from base.backup import get_attsite_file
            from mysite.iclock.device_http.sync_conv_att import line_to_log
            batch_lens = 100 # 最多插入的批次，根据服务器的配置以及数据库的性能来配置条数的多少
            cnts = get_attsite_file()["SYS"]["SQL_BATCH_CNTS"]
            if cnts:
                batch_lens = int(cnts)
            while True:
                dev,lines,file = get_att_record_file()
                if lines:
                    lens = len(lines)
                    times = lens%batch_lens == 0 and lens/batch_lens or (lens/batch_lens + 1)
                    for i in range(times):
                        m_lines = lines[i*batch_lens:(i+1)*batch_lens]
                        succcess = True
                        while succcess:
                            ret = line_to_log(dev,m_lines,event="files") # ret =False <数据库断开了>
                            if not ret:
                                time.sleep(60*2)
                            else:
                                succcess = False
                        time.sleep(0.1)
                    if file:
                        os.remove(file) 
                time.sleep(0.1)
        else:
            from django.db import connection as conn
            import time	
            
            while True:
                start =time.time()
                while True:
                    try:
                        process_data()
                    except:
                        import traceback;traceback.print_exc()
                    time.sleep(5)
                    end=time.time()
                    if end-start>60*30:#半个小时重启一下连接
                    	break
                try:
                    #退出的时候防止是断网，不断开连接而不能处理数据，所以关闭该连接
                    cur=conn.cursor()
                    cur.close()
                    conn.close()
                except:
                    pass
            
        
