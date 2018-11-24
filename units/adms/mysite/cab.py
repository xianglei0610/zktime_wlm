# -*- coding: utf-8 -*-
def set_lib_path():
    import sys
    import os
    _cur = os.getcwd()
    _cur = _cur.replace('units%sadms%smysite'%(os.sep,os.sep),'')
    lib_path = os.path.join(_cur,'python-support')
    sys.path.append(lib_path)
    os.environ["PYTHONPATH"]=lib_path
set_lib_path()

import os
import zipfile
import time
import fnmatch
import threading

def tmpDir():
	ret=os.path.split(__file__)[0]
	if ret: 
		ret=ret+"/release"
	else:
		ret=os.getcwd()+"/release"
	try:
		os.makedirs(ret)
	except: pass
	return ret


def famatch(fn, matches):
	for m in matches:
		if fnmatch.fnmatch(fn, m):
			return True
	return False

def zipDir(source_dir, target_file, match=['*'], exclude_dirs=[], exclude_files=[],other_py_file=[]):
	myZipFile = zipfile.ZipFile(target_file, 'w' )
	for root,dirs,files in os.walk(source_dir):
		for xdir in exclude_dirs:
			if xdir in dirs:
				dirs.remove(xdir)
		if files:
			other_files=filter(lambda f: famatch(f, other_py_file), files)
			src_files=filter(lambda f: famatch(f, match), files)
			files=filter(lambda f: not famatch(f, exclude_files), src_files)
			files=files+other_files
			if os.path.split(root)[1]=="commands" and os.path.split(os.path.split(root)[0])[1]=="management":
				files=files+src_files
				
			for vfileName in files:
				fileName = os.path.join(root,vfileName)
				myZipFile.write( fileName, fileName, zipfile.ZIP_DEFLATED )
	myZipFile.close()

def listFile(source_dir, match=['*'], exclude_dirs=[], exclude_files=[],other_py_file=[]):	
	fl=[]
	for root,dirs,files in os.walk(source_dir):
		for xdir in exclude_dirs:
			if xdir in dirs:
				dirs.remove(xdir)
		if files:
			other_files=filter(lambda f: famatch(f, other_py_file), files)
			src_files=filter(lambda f: famatch(f, match), files)
			files=filter(lambda f: not famatch(f, exclude_files), src_files)
			files=files+other_files
			
			if os.path.split(root)[1]=="commands" and os.path.split(os.path.split(root)[0])[1]=="management":
				files=files+src_files
			
			for vfileName in files:
				fl.append(os.path.join(root,vfileName))
	return fl

def unzipFile(source_file, target_dir):
	fl={}
	if not os.path.exists(target_dir):
		os.mkdir(target_dir)
	if target_dir[-1] not in ["/","\\"]:
		target_dir+="/"
	z=zipfile.ZipFile(source_file, 'r')
	for fn in z.namelist():
		bytes=z.read(fn)
		filename=target_dir+fn
		if (len(bytes)==0) and (fn[-1] in ["/","\\"]):
			try:
				os.makedirs(filename)
			except: pass
		else:
			try:
				os.makedirs("/".join(filename.split('/')[:-1]))
			except: pass
			file(filename,"wb+").write(bytes)
			fl[filename]=len(bytes)
	return fl

def restartSvr(svrName):
	os.system("cmd /C net stop %s & net start %s"%(svrName, svrName))

class restartThread(threading.Thread):
	def __init__(self, svrName):
		threading.Thread.__init__(self)
		self.svrName=svrName
	def run(self):
		time.sleep(2)
		restartSvr(self.svrName)

def exportMysite(original):
	import compileall
	old=os.getcwd()
	compileall.compile_dir(old)
	zipDir(old, tmpDir()+'/mysite.zip', ['*'], ['.hg','_svn','.svn','setup','photologue','lzo','upload'], ['.*','icdat.db','*.swp','*.py','*.orig','*.zip','options.txt','l.txt','*.sql', '*.7z', '*.doc', 'tftpgui.cfg', 'oracle9', 'author.pyc','authorization.pyc'],['library.zip'])#'*.log',*.txt'runpool.pyc', 'datacommcenter.pyc', '__init__.pyc'
	try:
		os.removedirs(tmpDir()+"/mysite")
	except: pass
	unzipFile(tmpDir()+'/mysite.zip', tmpDir()+"/mysite/")
	

if __name__=="__main__":
	from mysite import authorize_fun
	import datetime
	import shutil
	original = os.getcwd()
	os.chdir("../")
	
	#加入托盘程序执行文件
	try:
		#create_author_file()#创建权限文件
		#创建三个月试用版
		authorize_fun.create_trial_version(datetime.datetime.now() + datetime.timedelta(days=int(90)),att=3,acc=50,pos=3)
		os.system("python setup.py py2exe")
	except:
		import traceback;traceback.print_exc();
	os.chdir("../../")
	compile = os.getcwd()
	os.system("del *.pyc /s")

	os.chdir(original)
	shutil.copyfile(original+"/authorize_fun.dpy",original+"/authorize_fun.pyc")

	os.chdir(compile)
	exportMysite(compile)

