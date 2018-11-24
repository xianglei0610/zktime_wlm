# -*- coding: utf-8 -*-
import os.path
import sys, time
from pyDes import *
# Django settings for mysite project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

#mysql ****连接池参数开始*****
DBPOOL_WAIT_TIMEOUT = 28800
DBPOOL_SIZE = 60
DBPOOL_MAX = 100 
DBPOOL_INTERNAL_CONN_TIMEOUT = 10
NEED_SQL = True  # 是否需要sql语句
SQL_CONFIG_FILE = "sqlconfig.xml" # sql 语句的配置文件名
#mysql ****连接池参数结束*****

NUMBERS_FOR_CMDS_LOAD=200 #一个设备一次性加载多少条命令到缓存 memcache 最大1M
COMMAND_TIMEOUT=7 #缓存中的命令多久超时,单位天
MAX_SIZE_PER_DEVICE_CMDS = 960 #缓存中一个设备最大存储命令容量，单位K,不能操作1024
MAX_SIZE_PER_CMD = 4 #一条命令最大容量，单位K
DELETE_PROCESSED_CMD = True #删除执行完的命令
GETREQ_THREE_TIMES = True #为了兼容固件bug问题，有时候下发的命令不确认，所以设置下发三次

TREE_ASYNC_LOAD=0#树形控件到1000个之后就采用异步加载的方式，如果这个参数为0表示不启用异步加载

OEM = False#True代表软件为OEM（白标），默认为False，zk标  ---废弃
#ZKECO_AS_ZKACCESS = True#将zkeco作为zkaccess---需要保证同时放开att和acc方可
ZKACCESS_ATT = True#该配置变量值为True时，表示带考勤功能的门禁管理系统---废弃
ZKACCESS_5TO4 = True #用5.0代码打4.1包，主要是功能差异。值为False代表当前为5.0软件。---废弃
SINGLE_ELEVATOR = False #单梯控时该变量为true,未完成  --暂未使用

DEVICE_CREATEUSER_FLAG=True  #自动从设备上新增人员到数据库标志
DEVICE_CREATEBIO_FLAG=True  #自动从设备上人员的指纹到数据库标志

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
#WORK_PATH=os.path.split(__file__.decode(sys.getfilesystemencoding()))[0]
WORK_PATH=os.getcwdu()+os.sep+'mysite'
APP_HOME=os.path.split(WORK_PATH)[0]

CACHE_BACKEND = 'file://%s/tmp/django_cache?&max_entries=40000'%APP_HOME
MANAGERS = ADMINS
C_ADMS_PATH=APP_HOME+"/files/upload/%s/"
DATABASE_ENGINE='sqlite3'
DATABASE_NAME=APP_HOME+'/icdat.db'
DEVICE_SN_LIST=APP_HOME+'/tmp/device_sn_list.sn'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Etc/GMT%+-d'%(time.timezone/3600)

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes

SITE_ID = 1

#db backup step time
DB_DBCKUP_STEPTIME=1
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = APP_HOME+'/media/'
if not os.path.exists(MEDIA_ROOT):
        MEDIA_ROOT = WORK_PATH+'/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media'
ADDITION_FILE_ROOT = APP_HOME+'/files/'
if not os.path.exists(ADDITION_FILE_ROOT):
        ADDITION_FILE_ROOT = WORK_PATH+'/files/'
ADDITION_FILE_URL="/file"
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't10g+$^b29eonku&fr+l50efir4&o==k*9)%#*zi5@osf6)q@x'+APP_HOME

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
#    'johnny.middleware.LocalStoreClearMiddleware',
#    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',  #for Django 1.2
    'mysite.middleware.iclocklocale.AuthenticationMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'base.middleware.threadlocals.ThreadLocals',
    'mysite.middleware.iclocklocale.LocaleMiddleware',

#    'django.middleware.locale.LocaleMiddleware',
#    'django.middleware.cache.CacheMiddleware',
#    'django.middleware.doc.XViewMiddleware',
    #'django.middleware.csrf.CsrfResponseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

CACHE_MIDDLEWARE_SECONDS=25

LANGUAGE_CODE = 'zh-cn'
LANGUAGES=(
  #('en', 'English'),
  ('zh-cn', 'Simplified Chinese'),
  #('es', 'Spanish'),
  #('zh-tw', 'Tranditional Chinese'),
)

ROOT_URLCONF = 'mysite.urls'

template_path=APP_HOME+'/templates'
if not os.path.exists(template_path):
        template_path=WORK_PATH+'/templates'
try:
        import debug_toolbar
        dtb=debug_toolbar.__path__[0]+'/templates'
except:
        dtb=''
TEMPLATE_DIRS = (
    template_path,
    dtb
)

#if 'mysite.iclocklocale.myContextProc' not in TEMPLATE_CONTEXT_PROCESSORS:
TEMPLATE_CONTEXT_PROCESSORS = (
        #"django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        'mysite.middleware.iclocklocale.auth',
        'mysite.middleware.iclocklocale.myContextProc',)

INSTALLED_APPS_list =[
'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
#    'django.contrib.admin',
#    'johnny',
    'django_extensions',
    'base',
    'dbapp',
    'mysite.iclock',
#    'mysite.att',
#    'mysite.pos',#消费系统app
    #'mysite.testapp',
#    'mysite.iaccess',
    #'mysite.elevator',
    #'mysite.video',
    #'mysite.visitor',
    'rosetta',
    'mysite.personnel',
    'mysite.worktable',
    'mysite.selfservice',
    #'mysite.meeting',
    #'mysite.report',
#        'south',
#    'debug_toolbar',
#        'test_utils',


]


INVISIBLE_APPS = (
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
        'debug_toolbar',
        'test_utils',
        'south',
        'rosetta',
        'mysite.testapp',
        'mysite.selfservice',
)

AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'mysite.authurls.EmployeeBackend',
        )

INTERNAL_IPS = ('127.0.0.1','192.168/16')

DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
	"INTERCEPT_REDIRECTS":False,
}

import dict4ini
APP_CONFIG = dict4ini.DictIni(os.getcwd()+"/appconfig.ini") 

#发件人信息
EMAIL_ADDR = APP_CONFIG.iaccess.email_addr
EMAIL_HOST = APP_CONFIG.iaccess.email_host
EMAIL_PORT = APP_CONFIG.iaccess.email_port
EMAIL_HOST_USER = APP_CONFIG.iaccess.email_host_user
EMAIL_HOST_PASSWORD = APP_CONFIG.iaccess.email_host_password
EMAIL_USE_TLS = APP_CONFIG.iaccess.email_use_tls

VERSION="Ver 2152(Build: 20081111)"
ALL_TAG="ALL"

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE=int(60 * 60 * 24 * 7)#7天
SESSION_SAVE_EVERY_REQUEST=True
MAX_UPDATE_COUNT=50
UPDATE_COUNT=0
MCOUNT=0
APPEND_SLASH=False
LOGIN_REDIRECT_URL="/data/index/"
SELFSERVICE_LOGIN_REDIRECT_URL="/selfservice/index/"
LOGIN_URL="/accounts/login/"
ICLOCK_AUTO_REG=1
PIN_WIDTH=9
PIN_SUPPORT_LETTERS=False   #工号是否支持字母,主流固件不支持,此参数打开需要固件定制支持,并且只有单考勤的时候才生效
transaction_absolute_path = ""
REBOOT_CHECKTIME=0  #
NOCMD_DEVICES=[]
ENCRYPT=0
PAGE_LIMIT=20
UPGRADE_FWVERSION="Ver 6.39 Jan  1 2009"
MIN_TRANSINTERVAL=2 #最小传输数据间隔时间(分钟）
MIN_REQ_DELAY=60
POS_MIN_REQ_DELAY=10   #最小检查服务器命令间隔时间(秒）
POS_SYNC_TIME = 10 #同步时间间隔时间，（单位：秒）缺省0表示不自动同步时间
DISABLED_PINS=["0"]        #不允许的考勤号码
TRANS_REALTIME=1        #设备是否实时上传记录
NATIVE_ENCODE='GB18030'
MAX_EXPORT_COUNT=20000


try:
        TMP_DIR=os.environ['TMP']
except:
        TMP_DIR="/tmp"

#if not os.path.exists(TMP_DIR+"/"):
#        TMP_DIR=os.path.split(os.tempnam())[0]

UNIT=""

LOG_DIR=APP_HOME+"/tmp"
LOG_LEVEL=0

if "USER_COMPANY" in os.environ:
        UNIT=os.environ['USER_COMPANY']
else:
        u=os.path.split(APP_HOME)
        if u[0][-6:] in ('/units', '\\units'):
                UNIT=u[1]

POOL_CONNECTION=0    #数据库连接池使用的连接数，0 表示不使用连接池
WRITEDATA_CONNECTION=1  #后台写数据库进程使用的连接数，0 表示不使用后台写方式

if UNIT:
        #UNIT_URL="/u/"+UNIT+'/'    #用于Hosting业务不同企业使用
        UNIT_URL='/'
        p_path=APP_HOME+'/attsite.ini'
        LOGIN_REDIRECT_URL=UNIT_URL+"data/index/"
        LOGIN_URL=UNIT_URL+"accounts/login/"
#        SESSION_COOKIE_PATH=UNIT_URL
        LOGOUT_URL=UNIT_URL+"accounts/logout/"
        SESSION_COOKIE_NAME='sessionid'+UNIT.encode("ascii")
        ADDITION_FILE_URL=UNIT_URL+"file"
elif len(sys.argv)>1 and not ("manage." in sys.argv[0]):
        UNIT_URL="/"
        p_path=APP_HOME+'/'+sys.argv[1]
else:
        UNIT_URL="/"
        p_path=APP_HOME+'/attsite.ini'

#-------------------------------app根据安装包选择自适应搭配-----------------------begin
import dict4ini
att_file = dict4ini.DictIni(p_path)
VISIBLE_POS = att_file["Options"]["APP_POS"]
VISIBLE_ATT = att_file["Options"]["APP_ATT"]
VISIBLE_IACCESS = att_file["Options"]["APP_IACCESS"]

if VISIBLE_POS.lower()=="true":
    INSTALLED_APPS_list.append('mysite.pos')
if VISIBLE_ATT.lower()=="true":
    INSTALLED_APPS_list.append('mysite.att')
if VISIBLE_IACCESS.lower()=="true":
    INSTALLED_APPS_list.append('mysite.iaccess')

INSTALLED_APPS = tuple(INSTALLED_APPS_list)
#-------------------------------app根据安装包选择自适应搭配-----------------------end

cfg=None
if os.path.exists(p_path+'.dev'):
        p_path=p_path+'.dev'
if os.path.exists(p_path):
        import dict4ini
        cfg=dict4ini.DictIni(p_path, 
                values={
                'DATABASE': DATABASES['default'].copy(),
                'SYS':{
                        'PIN_WIDTH':PIN_WIDTH, 
                        'PIN_SUPPORT_LETTERS':PIN_SUPPORT_LETTERS,
                        'ENCRYPT':ENCRYPT,
                        'PAGE_LIMIT':PAGE_LIMIT, 
                        'REALTIME':TRANS_REALTIME, 
                        'AUTO_REG':ICLOCK_AUTO_REG,
                        'NATIVE_ENCODE': NATIVE_ENCODE,
                        'MAX_EXPORT_COUNT': MAX_EXPORT_COUNT,
                        'TIME_ZONE': TIME_ZONE,
                        'memcached': 'locmem://', 
                        },
                'LOG':{
                        'DIR':LOG_DIR,
                        'FILE':"",
                        'LEVEL':LOG_LEVEL,
                        }
                })
        TIME_ZONE = cfg.SYS.TIME_ZONE
        DATABASES['default'] = dict(cfg.DATABASE).copy()
        DATABASE_ENGINE=DATABASES['default']['ENGINE']
        DATABASE_NAME=cfg.DATABASE.NAME
        if "{unit}" in DATABASE_NAME:
                DATABASE_NAME=DATABASE_NAME.replace("{unit}",UNIT)
        elif DATABASE_NAME.startswith('{tmp_file}'):
                source=DATABASE_NAME[10:]
                target=TMP_DIR+"/"+source
                source=file(WORK_PATH+"/"+source,"rb").read()
                if not os.path.exists(target):
                        f=file(target,"w+b")
                        f.write(source)
                        f.close()
                DATABASE_NAME=target
        DATABASES['default']['NAME'] = DATABASE_NAME
        POOL_CONNECTION=DATABASES['default'].get('POOL', 0) #数据库连接池
        WRITEDATA_CONNECTION=DATABASES['default'].get('WRITEDATA', 0) #后台写数据库进程
       	WRITEDATA_LIVE_MINUTES=DATABASES['default'].get("WRITEDATA_LIVE_MINUTES", 10) 
        PIN_WIDTH=cfg.SYS.PIN_WIDTH
        PIN_SUPPORT_LETTERS = cfg.SYS.PIN_SUPPORT_LETTERS=="True"  and True  or False 
        ENCRYPT=cfg.SYS.ENCRYPT
        PAGE_LIMIT=cfg.SYS.PAGE_LIMIT
        TRANS_REALTIME=cfg.SYS.REALTIME 
        ICLOCK_AUTO_REG=cfg.SYS.AUTO_REG 
        NATIVE_ENCODE=cfg.SYS.NATIVE_ENCODE
        MAX_EXPORT_COUNT=cfg.SYS.MAX_EXPORT_COUNT
        if cfg.SYS.memcached:
                if "://" in cfg.SYS.memcached:
                        CACHE_BACKEND = cfg.SYS.memcached
                else:
                        CACHE_BACKEND="memcached://%s/?&max_entries=40000"%cfg.SYS.memcached
        if cfg.LOG.DIR=="{tmp_file}":
                LOG_DIR=TMP_DIR
                ADDITION_FILE_ROOT = TMP_DIR+'/files/'
        else:
                LOG_DIR=cfg.LOG.DIR
        if cfg.LOG.FILE: LOG_FILE=cfg.LOG.FILE
        LOG_LEVEL=cfg.LOG.LEVEL

        if cfg.Options["MIN_TRANSINTERVAL"]:
            MIN_TRANSINTERVAL=cfg.Options["MIN_TRANSINTERVAL"]
            
        if cfg.Options["MIN_REQ_DELAY"]:
            MIN_TRANSINTERVAL=cfg.Options["MIN_REQ_DELAY"]
            
        if cfg.Options["DEVICE_CREATEUSER_FLAG"]=="False":
            DEVICE_CREATEUSER_FLAG=False
            
        if cfg.Options["DEVICE_CREATEBIO_FLAG"]=="False":
            DEVICE_CREATEBIO_FLAG=False
        
        if cfg.Options["MAX_SIZE_PER_DEVICE_CMDS"]:
            MAX_SIZE_PER_DEVICE_CMDS=cfg.Options["MAX_SIZE_PER_DEVICE_CMDS"]
            
        if cfg.Options["DELETE_PROCESSED_CMD"]=="True":
            DELETE_PROCESSED_CMD=True
        elif cfg.Options["DELETE_PROCESSED_CMD"]=="False":
            DELETE_PROCESSED_CMD=False
        
            
        if cfg.Options["GETREQ_THREE_TIMES"]=="True":
            GETREQ_THREE_TIMES=True
        elif cfg.Options["GETREQ_THREE_TIMES"]=="False":
            GETREQ_THREE_TIMES=False
        
        if  cfg.Options["DEBUG"] == "True":
            DEBUG = True
        elif cfg.Options["DEBUG"] == "False":
            DEBUG = False
            
if sys.argv.count('-d')>0:
    DEBUG = True
    TEMPLATE_DEBUG = True
                
        
if POOL_CONNECTION: #启用数据库连接池
    if "django.db.backends." in DATABASES['default']['ENGINE']:
        DATABASES['default']['POOL_ENGINE']=DATABASES['default']['ENGINE']
    else:
        DATABASES['default']['POOL_ENGINE']="django.db.backends."+DATABASES['default']['ENGINE']
        DATABASES['default']['ENGINE']='pool'

#print "DATABASE:", DATABASES
#print "CACHE_BACKEND:", CACHE_BACKEND
MAX_DEVICES=100
VALID_DAYS=100	#100天内的考勤记录才会保存到数据库中，之前的考勤记录被忽略
CHECK_DUPLICATE_LOG=False	#保存考勤记录到数据库时检查是否该记录已经存在
SYNC_DEVICE_CACHE=60		#同步缓存中的设备对象和数据库的时间（秒）

ZKECO_TEST=0    #测试版本

ATT_DEVICE_LIMIT=0           #限制考勤机台数,根据登记的先后顺序来确定是否达到限制
MAX_ACPANEL_COUNT = 50     #最大支持50台门禁控制器
ZKECO_DEVICE_LIMIT=0
POS_ID_DEVICE_LIMIT=10 #系统默认ID消费机台数
POS_IC_DEVICE_LIMIT = 10#系统默认IC消费机台数

AUTHORIZE_MAGIC_KEY='magic'
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_myproj'
import dict4ini
APP_CONFIG=dict4ini.DictIni(APP_HOME+"/appconfig.ini")

if APP_CONFIG.language.language:
    LANGUAGE_CODE=APP_CONFIG.language.language
#template_dir
ldirs=list(TEMPLATE_DIRS)
for e in INSTALLED_APPS:
    tdir=WORK_PATH+os.sep+e.split(".")[-1]+os.sep+"templates"
    if os.path.exists(tdir):
        ldirs.append(tdir)
TEMPLATE_DIRS=tuple(ldirs)
CUSTOMER_CODE=""

HAS_DOG=False


def has_serialize():
    u"判断是否有授权许可"
    try:
        sn=cfg["SYS"]["SN"]
        mac=cfg["SYS"]["MAC"]
        customer_code=cfg["SYS"]["CUSTOMER_CODE"]
        if sn and mac and customer_code:
            return True
    except Exception,e:
        pass
    return False
def get_licence_string():
    u"判断是否有授权许可"
    try:
        sn=cfg["SYS"]["SN"]
        return sn
    except Exception,e:
        return ""
    
import authorize_fun
def get_customer():
    customer_code = ""
    try:
            if authorize_fun.Ini()==0 and authorize_fun.CheckKey()==1:#有插加密狗
                value=authorize_fun.read_value(authorize_fun.NEW_ADDRESS,authorize_fun.NEW_ADDRESS_LENGTH)
                au=authorize_fun.AuthClass()
                au.parse_string(value.strip())
                customer_code = au.customer_code
            else:
                customer_code=cfg["SYS"]["CUSTOMER_CODE"]
    except Exception,e:
        import traceback;traceback.print_exc()
        customer_code=""
    return customer_code    
CUSTOMER_CODE=get_customer()


#def ungen_licence(pcode,mac):
#    uv=[]
#    mac=mac.zfill(12).upper()
#    pmac=mac[-6:]+mac[:6]
#    pcode=str(pcode).zfill(48)
#    for i in range(24):
#        uv.append(str(int(pcode[i*2:i*2+2],16)).zfill(4))
#    
#    uv="".join(uv)
#    #print "uv:",uv
#    uvp1=uv[:48]
#    uvp2=uv[-48:]
#    up1=[]
#    up2=[]
#    for i in range(12):
#        up1.append(chr(int(uvp1[i*4:i*4+4])^ord(pmac[i:i+1])))
#        up2.append(chr(int(uvp2[i*4:i*4+4])^ord(pmac[i:i+1])))
#    up1="".join(up1)
#    up2="".join(up2)
#    #print "up1:",up1
#    #print "up2:",up2
#    ret=up1[:7]+up2[:7]+up1[-5:]+up2[-5:]
#    

#def has_serialize():
#    u"判断是否有序列号"
#    try:
#        sn=cfg["SYS"]["SN"]
#        mac=cfg["SYS"]["MAC"]
#        customer_code=cfg["SYS"]["CUSTOMER_CODE"]
#        if sn and mac and customer_code:
#            return True
#    except Exception,e:
#        pass
#    return False
#
#def get_device_limit():
#    u"得到序列号中的"
#    ATT_DEVICE_LIMIT=0
#    MAX_ACPANEL_COUNT=50
#    ZKECO_DEVICE_LIMIT=0
#    sn=cfg["SYS"]["SN"]
#    mac=cfg["SYS"]["MAC"]
#    customer_code=cfg["SYS"]["CUSTOMER_CODE"]  
#    if sn and customer_code:    
#        key="softbyzk"
#        k=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
#           
#        ret=k.decrypt(sn.decode("base64"))
#        if len(ret)>=41:
#            #customer_code+att+acc+mac+zkeco
#            customer=ret[:14]  
#            #dmac=k.decrypt(mac.decode("base64"))  
#            from mysite.authorize_fun import get_mac
#            dmac=get_mac()
#            
#            retmac=ret[24:41]
#            #zkeco=ret[41:46]
#            findpos=0
#            for i in range(14):
#                if(customer[i:i+1]!="0"):
#                    findpos=i
#                    break
#            if customer_code and customer_code==customer[findpos:] and dmac==retmac:                
#                CUSTOMER_CODE=customer[findpos:]            
#                ATT_DEVICE_LIMIT=int(ret[14:19])
#                MAX_ACPANEL_COUNT=int(ret[19:24])
#                if len(ret)>=46:
#                    ZKECO_DEVICE_LIMIT=int(ret[41:46])
#    return ZKECO_DEVICE_LIMIT,ATT_DEVICE_LIMIT,MAX_ACPANEL_COUNT


##读软件狗中设备的数量
#import authorize_fun
#from threading import Event, Semaphore
#sem = Semaphore()
#sem.acquire()
#
#if authorize_fun.Ini()==0:
#    if authorize_fun.CheckKey()==1 and authorize_fun.check_mac():
#        HAS_DOG=True
#        ZKECO_DEVICE_LIMIT=authorize_fun.read_zkeco()
#        ATT_DEVICE_LIMIT=authorize_fun.read_zktime()
#        MAX_ACPANEL_COUNT=authorize_fun.read_zkaccess()
#        #print 'mac:',authorize_fun.read_mac(),'\n'
#elif has_serialize():
#    #读配置文件狗数量
#    ZKECO_DEVICE_LIMIT,ATT_DEVICE_LIMIT,MAX_ACPANEL_COUNT=get_device_limit()
#elif not authorize_fun.is_test_expired(os.path.join(APP_HOME,"author_test.pyc")):
#    #测试版
#    ZKECO_DEVICE_LIMIT,ATT_DEVICE_LIMIT,MAX_ACPANEL_COUNT = authorize_fun.get_test_info(os.path.join(APP_HOME,"author_test.pyc"))
#
#sem.release()   
#print 'zkeco:',ZKECO_DEVICE_LIMIT,'\n'
#print 'att:',ATT_DEVICE_LIMIT,'\n'
#print 'acc:',MAX_ACPANEL_COUNT,'\n'

