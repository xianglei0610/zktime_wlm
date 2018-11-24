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
    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
    from mysite.pos.pos_ic.ic_pos_devview import write_data
    data=""
    devs=Device.objects.filter(device_type =DEVICE_POS_SERVER)
    path=settings.C_ADMS_PATH%"zkpos/%s"
    tnow=datetime.datetime.now()
#    print tnow,"      device count",len(devs)
    for d in devs: 
        #print "current device: ",d.sn
        try:            
            objpath=path%d.sn+"new/"
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
                            process_flag=False #解析数据是否出错标识
                            print_exc()
                        finally:
                            try:
                                f_dir=f[:8]
#                                print "f_dir ",f_dir
#                                cf_path=settings.C_ADMS_PATH%"zkpos/%s"+f_dir+"/"
                                cf_path=settings.WORK_PATH+"/files/zkpos/%s/"+f_dir+"/"
                                cf_path=cf_path%d.sn  #数据备份路径
#                                print "cf_path==",cf_path
#                                print "objpath===",objpath
                                if not os.path.exists(cf_path):
                                    os.makedirs(cf_path)
                                if process_flag:
                                    shutil.copy(objpath+f,cf_path)
                                os.remove(objpath+f)
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
    help = "Starts zkpos adms ."
    args = ''

    def handle(self, *args, **options):
        from django.db import connection as conn
        import time	
        from mysite.pos.pos_constant import POS_IC_ADMS_MODEL
        from mysite.pos.pos_ic.ic_sync_action import get_pos_record,init_pos_batch,pos_ic_write_data
        from mysite.pos.pos_ic.ic_pos_devview import write_data
        print self.help
        if POS_IC_ADMS_MODEL:
#            init_pos_batch()
            while True:
                try:
                    cur=conn.cursor()                       
                    if cur:
                        head_data,lines = get_pos_record()
                        if lines:
                            b_time = time.time()
                            pos_ic_write_data(head_data,lines)
                            end_time = time.time()
#                            print "--------time----------%s----------%s------------%s"%(end_time-b_time,len(lines),time.ctime())
                        time.sleep(0.1)
                except:
                    import traceback;traceback.print_exc()
        else:
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
            
        
