# -*- coding: utf-8 -*-
import os

nginx_load_conf="""
upstream adms_device {
%(adms_device)s
}
upstream adms_mng {
%(adms_mng)s
}
"""

nginx_site_conf="""
    listen %(PORT)s;
    server_name adms;
    location /iclock/cdata {
        #proxy_pass http://adms_device;
        #include    proxy.conf;
        fastcgi_pass adms_device;
        include        fastcgi.conf;
                
    }
    location /iclock/getrequest {
        #proxy_pass http://adms_device;
        #include    proxy.conf;        
        fastcgi_pass adms_device;
        include        fastcgi.conf;
        
    }
    location /iclock/devicecmd {
        #proxy_pass http://adms_device;
        #include    proxy.conf;        
        fastcgi_pass adms_device;
        include        fastcgi.conf;
        
    }
    location /iclock/fdata {
#        proxy_pass http://adms_device;
#        include    proxy.conf;        
        fastcgi_pass adms_device;
        include        fastcgi.conf;

    }
    
    location /rpc/ { 
        fastcgi_pass adms_device;
        include        fastcgi.conf;
    }
    
    location /rpc_static/ { 
        fastcgi_pass adms_device;
        include        fastcgi.conf;
    }
    
    location /{
        fastcgi_pass adms_mng;
        include        fastcgi.conf;

    }

"""

def make_conf(port,fcgiPort,WebPort):
    portcount = 1
    webportcount = 1
    os.chdir("%s/../../python-support/nginx"%os.getcwd())
    bl=[]
    for p in range(int(portcount)):
        bl.append("     server 127.0.0.1:"+str(int(fcgiPort)+p)+";")
    webbl=[]
    for p in range(int(webportcount)):
        webbl.append("      server 127.0.0.1:"+str(int(WebPort)+p)+";")
    
    fname="conf/load_balance.conf"    
    f=file(fname, "w+")
    confStr=nginx_load_conf%{"adms_device":"\n".join(bl),"adms_mng":"\n".join(webbl)}
    f.write(confStr)
    f.close()
    
    fname="conf/site.conf"
    f=file(fname, "w+")
    confStr=nginx_site_conf%{"PORT":port}
    f.write(confStr)
    f.close()