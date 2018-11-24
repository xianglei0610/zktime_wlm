# -*- coding: utf-8 -*-
import datetime
from django.db import models
from base.models import CachingModel, Operation, ModelOperation
from mysite import sql_utils

import os,socket
from ftplib import FTP
from mysite.settings import cfg


YESORNO = (
        (1, u'是'),
        (0, u'否'),
)

def ftp_up(username,pwd,filename,targUrl,serverIP,port="21"):
    u"""
        ftp 上传文件
       @param:
           username : ftp 用户名
           pwd：ftp 密码
           filename ：文件名
           serverIP ： ftp 服务器IP
            port : 端口号
           targUrl : ftp  存放路径
    """
    ftp = None
    file_handler = None
    try:
        ftp=FTP() 
        ftp.connect(serverIP,port)
        ftp.login(username,pwd)
        print "111111111111111111",os.getcwd()
        
        bufsize = 1024
        file_handler = open(filename,'rb')
        print "targUrl-000000000-",targUrl
        ftp.cwd(targUrl)
        print "222222222222222", os.getcwd()
        ftp.storbinary('STOR %s' % os.path.basename("\\".join([targUrl,filename])),file_handler,bufsize)
        print "%s   The file  %s upload success! "%(datetime.datetime. now(),filename)
    except:
         import traceback;
         traceback.print_exc()
    finally:
        if file_handler:
            file_handler.close() 
        if ftp:
            ftp.quit() 

def use_ftp(filename,targUrl=""):
    ftp_cfg =  cfg["FTP"]
    
    username = ftp_cfg["USER"]
    pwd  = ftp_cfg["PASSWORD"]
   
    serverIP  = ftp_cfg["HOST"]
    port = ftp_cfg["PORT"]
    
    targUrl  = targUrl and targUrl or ftp_cfg["PATH"]
    ftp_up(username,pwd,filename,targUrl,serverIP,port="21")
    
def ftp_down(username,pwd,filename,targUrl,serverIP,port="21"):
    u"""
        ftp 下载文件
       @param:
           username : ftp 用户名
           pwd：ftp 密码
           filename ：本地文件名
           serverIP ： ftp 服务器IP
            port : 端口号
           targUrl : 目标存放路径
    """
    ftp = None
    file_handler = None
    try:
        ftp=FTP() 
        ftp.connect(serverIP,port)
        ftp.login(username,pwd) 
        bufsize = 1024 
        file_handler = open(("%s\%s")%(targUrl,filename),'w')
        ftp.retrbinary('RETR %s' % os.path.basename(filename),file_handler,bufsize) 
    except:
         import traceback;
         traceback.print_exc()
    finally:
        if file_handler:
            file_handler.close() 
        if ftp:
            ftp.quit() 

def load_data(starttime,endtime):
    from django.db import connection
    print "1111111111111",starttime,endtime,type(starttime)
    starttime=starttime.strftime('%Y-%m-%d %H:%M:%S')
    endtime=endtime.strftime('%Y-%m-%d %H:%M:%S')
    file_cfg=cfg["Options"] #获取存放目录
    file_path=file_cfg["FILE_PATH"]
    os.chdir(file_path) #切换到存放目录
    os.getcwd()
    filename='%s%s.txt'%(socket.getfqdn(socket.gethostname()),datetime.datetime.now().strftime("%Y%m%d%H%M"))
    filename1 = open(filename,'a')      #以追加模式打开文件，如果文件不存在则创建
    print "file_path--------",file_path
    
    
    #通过sql语句查到所有满足条件的数据
    params={}
    id_part={}
    params={'startdate':starttime,'end_date':endtime}
    sql=sql_utils.get_sql('sql','get_syncftp_sql','att',params=params,id_part=id_part)
    cs = connection.cursor()
    cs.execute(sql)
    print "sql00000000000000000000000000000000",sql
    data = cs.fetchall()
    print "data---------------",data,type(data)
    datas=[]
    for row in data:
        datas.append(list(row))
    print "datas-------------",datas    
    for row in datas:
            i = row 
            for j in i:        #写入文件中
                filename1.write(str(j))
            filename1.write('\n')   
    print 'filename--------------',filename
    return filename

class SyncSet(CachingModel):
    name = models.CharField(u'名称', null=False, blank=False,max_length=20)
    syncTime= models.TimeField(u'同步时间', null=False,  blank=False, editable=True)
    times= models.IntegerField(u'前置分钟数', null=False, blank=False, editable=True)
    isValid=models.BooleanField(verbose_name=u'是否生效',choices=YESORNO, null=False,default=0, editable=True)
    
  
    
    class OpAddManyOvertime(ModelOperation):
        help_text=u'''FTP同步'''
        verbose_name=u"FTP同步"
        params=(
            ('starttime', models.DateTimeField(u'开始时间' , null=False,  blank=False)),
            ('endtime', models.DateTimeField(u'结束时间', null=False, blank=False)),
        )
        def action(self, **args):
            if args['starttime']>=args['endtime']:
                raise Exception(u'结束时间不能小于等于开始时间')
            filename=load_data(args['starttime'],args['endtime'])
            use_ftp(filename)
            raise Exception((u"FTP传递成功，文件名%s")%filename)
        
        
    class Admin(CachingModel.Admin):
            app_menu="att"
            menu_index=25
            @staticmethod
            def initial_data():
                if SyncSet.objects.all().count()==0:
                    SyncSet(name='7:30',syncTime="07:30:00",times=360,isValid=1).save()
                    SyncSet(name='15:30',syncTime="15:30:00",times=480,isValid=1).save()
                    SyncSet(name='1:30',syncTime="01:30:00",times=600,isValid=1).save()


    class Meta:
                app_label = 'att'
                db_table = 'sync_set'
                verbose_name = u" 同步设置"
                verbose_name_plural = verbose_name
