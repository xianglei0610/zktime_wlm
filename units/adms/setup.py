# -*- coding: utf-8 -*-
from distutils.core import setup  
import py2exe  
import shutil
import os

includes = ["encodings", "encodings.*"]
options = {"py2exe":   
        {"compressed": 1, 
         "optimize": 2,   
         "ascii": 1,   
         "includes":includes,   
         "bundle_files": 1 }
}  

def process_files():
    #删除文件
    current_path=os.getcwd()
    for e in ["library.zip","zkecomng.exe","w9xpopen.exe"]:
        try:
            os.remove(current_path+"\\"+e)
        except:
            pass
    #复制文件
    
    src_files=os.listdir(current_path+"\\dist")
    for e  in src_files:
        src_file=current_path+"\\dist\\"+e
        try:
            shutil.move(src_file,current_path)
        except:
            pass
    #shutil.rmtree("dist")
       
setup(  
    options = options,
    version = "0.5.0",  
    description = "zkeco console",  
    name = "py2exe samples",    
    windows = [{'script':'gui.py','dest_base':'zkecomng','uac_info':'requireAdministrator', "icon_resources": [(1, r"zkeco.ico")]}] 
)  

#移动文件
try:
    process_files()
except:
    import traceback;traceback.print_exc();

