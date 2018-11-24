# -*- coding: utf-8 -*-
import datetime
import glob
from traceback import print_exc
from django.utils.translation import ugettext_lazy as _
from mysite.settings import *
from os import makedirs, remove
import os

WRITE_LOG = True#用户后台的调试，该变量与debug无关，即：可用于debug为False时的调试

def fwVerStd(ver): # Ver 6.18 Oct 29 2007 ---> Ver 6.18 20071029
        ml=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov','Dec']
        if ver and len(ver)>=20:
                tl=ver[9:].split(" ")
                try:
                        tl.remove("")
                except: pass
                try:
                        return ver[:9]+"%s%02d%02d"%(tl[2], 1+ml.index(tl[0]), int(tl[1]))
                except:
                        return ""
        else:
                return ""

def printf(str, primary=False):
    if DEBUG or primary:
        try:
            dt=datetime.datetime.now()
            mfile='tmp/center_%s.txt'%datetime.datetime.now().strftime("%Y%m%d")
            f=open(mfile,'a')
            wstr='%s-%d-%s\n'%(datetime.datetime.now().strftime("%H:%M:%S"), os.getpid(), str)
            f.write(wstr)
            f.close()
        except:
            print_exc()
            pass

def write_log(str, primary=False):#primary暂时不使用
    if WRITE_LOG:
        try:
            dt=datetime.datetime.now()
            mfile='tmp/center_%s.txt'%datetime.datetime.now().strftime("%Y%m%d")
            f=open(mfile,'a')
            wstr='-%s-%d-%s\n'%(datetime.datetime.now().strftime("%H:%M:%S"), os.getpid(), str)
            print wstr#手动启动时，显示到命令行，服务时打印到后台服务日志中
            f.write(wstr)
            f.close()
        except:
            print_exc()
            pass


def delete_log():
	dt = datetime.datetime.now() + datetime.timedelta(days = -30)
 	it=int(dt.strftime("%Y%m%d"))
	filelist=glob.glob('tmp/center_*.txt')
	for flist in filelist:
		ftime=int(flist.split('_')[1].split('.')[0])
		if ftime < it:
			remove(flist)
