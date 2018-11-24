# -*- coding: utf-8 -*-

import win32api, win32gui
import win32con, winerror
import sys, os
import dict4ini
import socket
import wx
import wx.lib.buttons
import wx.lib.stattext
import wx.lib.filebrowsebutton
from  pyDes import *
from wx.lib.anchors import LayoutAnchors
import time

def is_service_stoped():
    s=os.popen("sc.exe query ZkecoControlCenterService").read()
    if ": 1  STOPPED" in s:
        return True
    return False

def get_attsite_file():
    #current_path=os.path.split(__file__)[0]
    #if not current_path:
    if hasattr(sys, "frozen"):
        current_path=os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    else:
        current_path=os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

    if not current_path:
        current_path=os.getcwd()
    attsite=dict4ini.DictIni(current_path+"/attsite.ini")
    return attsite

def is_datacenter_stoped():
    s=os.popen("sc.exe query ZkecoControlCenterService").read()
    if ": 1  STOPPED" in s:
        return True
    return False

def get_i18_dict():
    d_language={
        "en":"en_inno.ini",
        "zh-cn":"cns_inno.ini"
    }
    if hasattr(sys, "frozen"):
        current_path=os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    else:
        current_path=os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
    if not current_path:
        current_path=os.getcwd()
    appconf=dict4ini.DictIni(current_path+"/appconfig.ini")
    language=u"%s"%appconf["language"]["language"]
    res_dict=dict4ini.DictIni(current_path+"/"+d_language[language])
    return res_dict["trans"]

def gettext(str_source):
    res_dict=get_i18_dict()
    if res_dict[str_source]:
        return u"%s"%res_dict[str_source]
    else:
        return u"%s"%str_source

#直接杀死服务进程，防止服务停掉之后有些服务进程还在(仅门禁)
def kill_services():
    from redis_self.server import queqe_server
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
    #os.system("taskkill /f /im PythonService.exe")
    q_server = queqe_server()
    main_pid = q_server.get_from_file("CENTER_MAIN_PID")
    if main_pid:
        os.system("taskkill /PID %s /F /T" % main_pid)
    processes = []
    for n in range(8):
        processes.append("Net%s"%n)
    for c in range(1, 30):
        processes.append("COM_%s"%c)
    if processes:
        for process in processes:#强制杀子进程
            chilren_pid = q_server.get_from_file("PROCESS_%s_PID"%process)
            if chilren_pid:
                os.system("taskkill /PID %s /F /T" % chilren_pid)
    #d_server.delete_dict("CENTER_RUNING")

def control_services(YesNoClose, local_db=True):
    from mysite import settings, utils
    #from redis.server import start_dict_server
    #utils.printf(settings.INSTALLED_APPS, True)
    #utils.printf("mysite.iaccess" in settings.INSTALLED_APPS, True)
    if YesNoClose:
        os.system("net stop ZkecoControlCenterService")
    else:
        os.system("net start ZkecoControlCenterService")

def check_port(txt_port,lbl_status):
    ret=False
    try:
        port=int(txt_port.Value)
        if port < 1 or port > 65535:
            lbl_status.Label=gettext(u'port_range_error')
            return False
            
    except Exception:
        lbl_status.Label=gettext(u'port_need_number')
        return False
    
    sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        sk.bind(('127.0.0.1',port))
        ret= True
    except Exception:
        ret= False
    finally:
        sk.close()
    if ret:
        lbl_status.Label=gettext(u'port_enable')
    else:
        lbl_status.Label=gettext(u'port_use') 
    return ret

def check_process_exist(process_name):#检测zkecomng进程
    import win32com.client
    WMI=win32com.client.GetObject('winmgmts:')
    processCodeCov=WMI.ExecQuery('select * from Win32_Process where Name="%s"'%process_name)
    if len(processCodeCov)>1:
        #print "%s is exists" %process_name
        return True
    else:
       # print "%s is not exist" %process_name
        return False
def save_dbinfo(dbframe):
    import subprocess
    db_dict=get_attsite_file()
    db_engine={
        "sqlserver2005":"sqlserver_ado",
        "mysql":"mysql",
        "oracle10g":"oracle",
    }

    port=None
    try:
        port=int(dbframe.txt_port.Value)
        dbframe.lbl_result.Label=gettext(u'dbinfo_save_success_restart')
    except Exception:
        dbframe.lbl_result.Label=gettext(u'port_need_number')
        return False

    if dbframe.txt_dbname.Value == '':
        dbframe.lbl_result.Label=gettext(u'db_name_null')
        return False
    txt_value=dbframe.txt_dbtype.Value.strip()
    db_dict["DATABASE"]["ENGINE"]=(txt_value in db_engine.keys()) and  db_engine[txt_value] or txt_value
    db_dict["DATABASE"]["NAME"]=dbframe.txt_dbname.Value.strip()
    db_dict["DATABASE"]["USER"]=dbframe.txt_user.Value.strip()
    db_dict["DATABASE"]["PASSWORD"]=dbframe.txt_pwd.Value.strip()
    db_dict["DATABASE"]["HOST"]=dbframe.txt_ip.Value.strip()
    db_dict["DATABASE"]["PORT"]=dbframe.txt_port.Value.strip()
    db_dict.save()
    #control_services(True)
    #control_services(False)

def save_mid_dbinfo(dbframe):
    import subprocess
    db_dict=get_attsite_file()
    db_engine={
        "sqlserver2005":"sqlserver_ado",
        "mysql":"mysql",
        "oracle10g":"oracle",
    }
    port=None
    try:
        port=int(dbframe.txt_port.Value)
        dbframe.lbl_result.Label=gettext(u'dbinfo_save_success_restart')
    except Exception:
        dbframe.lbl_result.Label=gettext(u'port_need_number')
        return False
    txt_value=dbframe.txt_dbtype.Value.strip()
    db_dict["MID_DATABASE"]["ENGINE"]=(txt_value in db_engine.keys()) and  db_engine[txt_value] or txt_value
    db_dict["MID_DATABASE"]["NAME"]=dbframe.txt_dbname.Value.strip()
    db_dict["MID_DATABASE"]["USER"]=dbframe.txt_user.Value.strip()
    db_dict["MID_DATABASE"]["PASSWORD"]=dbframe.txt_pwd.Value.strip()
    db_dict["MID_DATABASE"]["HOST"]=dbframe.txt_ip.Value.strip()
    db_dict["MID_DATABASE"]["PORT"]=dbframe.txt_port.Value.strip()
    db_dict.save()

def revert(dbframe):
    #取得原始数据库信息
     db_dict_get=get_attsite_file()["MID_DATABASE"]

    #初始化 页面显示信息 从 attsite中读取信息
     dbengine=db_dict_get["ENGINE"]
     dbname=db_dict_get["NAME"]
     dbuser=db_dict_get["USER"]
     dbpassword=db_dict_get["PASSWORD"]
     dbhost=db_dict_get["HOST"]
     dbport=db_dict_get["PORT"]

     import subprocess
     db_dict=get_attsite_file()

    #把原始数据配置信息写入到attsite文件中去
     db_dict["DATABASE"]["ENGINE"]=dbengine
     db_dict["DATABASE"]["NAME"]=dbname
     db_dict["DATABASE"]["USER"]=dbuser
     db_dict["DATABASE"]["PASSWORD"]=dbpassword
     db_dict["DATABASE"]["HOST"]=dbhost
     db_dict["DATABASE"]["PORT"]=dbport
     db_dict.save()

#验证端口有效后，保存到配置文件---darcy20110317
def save_webserver_port(txt_port,lbl_status):
    from mysite import settings
    db_dict=get_attsite_file()
    port=None
    try:
        port=int(txt_port.Value)
#        lbl_status.Label=gettext(u'portinfo_save_success')
    except Exception:
        lbl_status.Label=gettext(u'port_need_number')
        return False
    db_dict["Options"]["Port"]=port
    db_dict.save()
    #if "mysite.iaccess" in settings.INSTALLED_APPS:
    os.system("net stop ZkecoControlCenterService")
    kill_services()
    #if "mysite.iaccess" in settings.INSTALLED_APPS:
    os.system("net start ZkecoControlCenterService")
    lbl_status.Label=gettext(u'portinfo_save_success')
    
[wxID_DIALOG1, wxID_DIALOG1BTN_CLOSE, wxID_DIALOG1BTN_TEST, wxID_DIALOG1BTN_SAVE,
 wxID_DIALOG1LBL_DBINFO, wxID_DIALOG1LBL_DBNAME, wxID_DIALOG1LBL_DBTYPE,
 wxID_DIALOG1LBL_IP, wxID_DIALOG1LBL_PORT, wxID_DIALOG1LBL_PWD,
 wxID_DIALOG1LBL_RESULT, wxID_DIALOG1LBL_USER, wxID_DIALOG1STATICTEXT1,
 wxID_DIALOG1TXT_DBNAME, wxID_DIALOG1TXT_DBTYPE, wxID_DIALOG1TXT_IP,
 wxID_DIALOG1TXT_PORT, wxID_DIALOG1TXT_PWD, wxID_DIALOG1TXT_USER,
] = [wx.NewId() for _init_ctrls in range(19)]

class DialogDb(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(539, 130), size=wx.Size(535, 388),
              style=wx.DEFAULT_DIALOG_STYLE, title=gettext(u'db_connect_settings'))
        self.SetClientSize(wx.Size(527, 354))

        self.lbl_dbinfo = wx.StaticBox(id=wxID_DIALOG1LBL_DBINFO,
              label=gettext(u"db_connect_settings"),
              name=u'lbl_dbinfo', parent=self, pos=wx.Point(35, 20),
              size=wx.Size(456, 272), style=0)

        self.lbl_dbType = wx.StaticText(id=wxID_DIALOG1LBL_DBTYPE,
              label=gettext(u"db_type"), name=u'lbl_dbType',
              parent=self, pos=wx.Point(69, 57), size=wx.Size(128, 14),
              style=wx.ALIGN_RIGHT)

        self.lbl_user = wx.StaticText(id=wxID_DIALOG1LBL_USER,
              label=gettext(u"usrname"), name=u'lbl_user', parent=self,
              pos=wx.Point(70, 125), size=wx.Size(127, 14),
              style=wx.ALIGN_RIGHT)

        self.lbl_dbName = wx.StaticText(id=wxID_DIALOG1LBL_DBNAME,
              label=gettext(u"db_name"), name=u'lbl_dbName',
              parent=self, pos=wx.Point(70, 92), size=wx.Size(127, 14),
              style=wx.ALIGN_RIGHT)

        self.lbl_pwd = wx.StaticText(id=wxID_DIALOG1LBL_PWD,
              label=gettext(u"pwd"), name=u'lbl_pwd', parent=self,
              pos=wx.Point(78, 161), size=wx.Size(119, 14),
              style=wx.ALIGN_RIGHT)

        self.lbl_ip = wx.StaticText(id=wxID_DIALOG1LBL_IP,
              label=gettext(u"host_address"), name=u'lbl_ip', parent=self,
              pos=wx.Point(78, 194), size=wx.Size(119, 14),
              style=wx.ALIGN_RIGHT)

        self.lbl_port = wx.StaticText(id=wxID_DIALOG1LBL_PORT,
              label=gettext(u"port"), name=u'lbl_port', parent=self,
              pos=wx.Point(80, 230), size=wx.Size(118, 14),
              style=wx.ALIGN_RIGHT)

        self.lbl_result = wx.StaticText(id=wxID_DIALOG1LBL_RESULT,
              label=u'', name=u'lbl_result', parent=self, pos=wx.Point(89,
              264), size=wx.Size(351, 24), style=0)

        self.txt_dbtype = wx.ComboBox(choices=['mysql','oracle10g','sqlserver2005'],id=wxID_DIALOG1TXT_DBTYPE,
              name=u'txt_dbtype', parent=self, pos=wx.Point(203, 53),
              size=wx.Size(160, 22), style=wx.CB_READONLY, value=u'')

        #self.comboBox1.Bind(wx.EVT_KILL_FOCUS, self.OnComboBox1KillFocus)
       # self.txt_dbtype.Bind(wx.EVT_KILL_FOCUS, self.Ontxt_dbtypeKillFocus)        
        self.txt_dbtype.Bind(wx.EVT_COMBOBOX, self.Ontxt_dbtypeKillFocus)
        
        self.txt_dbname = wx.TextCtrl(id=wxID_DIALOG1TXT_DBNAME,
              name=u'txt_dbname', parent=self, pos=wx.Point(203, 88),
              size=wx.Size(160, 22), style=0, value=u'')
        self.txt_dbname.SetMaxLength(20)
        self.txt_user = wx.TextCtrl(id=wxID_DIALOG1TXT_USER, name=u'txt_user',
                    parent=self, pos=wx.Point(203, 121), size=wx.Size(160, 22),
                    style=0, value=u'')
        self.txt_user.SetMaxLength(20)
        
        self.txt_pwd = wx.TextCtrl(id=wxID_DIALOG1TXT_PWD, name=u'txt_pwd',
              parent=self, pos=wx.Point(204, 156), size=wx.Size(160, 22),
              style=wx.TE_PASSWORD, value=u'')
        self.txt_pwd.SetMaxLength(20)

        self.txt_ip = wx.TextCtrl(id=wxID_DIALOG1TXT_IP, name=u'txt_ip',
              parent=self, pos=wx.Point(204, 191), size=wx.Size(160, 22),
              style=0, value=u'')
        self.txt_ip.SetMaxLength(30)

        self.txt_port = wx.TextCtrl(id=wxID_DIALOG1TXT_PORT, name=u'txt_port',
              parent=self, pos=wx.Point(204, 228), size=wx.Size(160, 22),
              style=0, value=u'')
        self.txt_port.SetMaxLength(5)

        self.btn_test = wx.lib.buttons.GenButton(id=wxID_DIALOG1BTN_TEST,
              label=gettext(u"test"), name=u'btn_test', parent=self,
              pos=wx.Point(90, 307), size=wx.Size(100, 26), style=0)
        self.btn_test.Bind(wx.EVT_BUTTON, self.OnBtn_testButton,
              id=wxID_DIALOG1BTN_TEST)
        
        self.btn_save = wx.lib.buttons.GenButton(id=wxID_DIALOG1BTN_SAVE,
              label=gettext(u"save"), name=u'btn_save', parent=self,
              pos=wx.Point(220, 307), size=wx.Size(100, 26), style=0)
        self.btn_save.Bind(wx.EVT_BUTTON, self.OnBtn_saveButton,
              id=wxID_DIALOG1BTN_SAVE)      
        
        self.btn_close = wx.lib.buttons.GenButton(id=wxID_DIALOG1BTN_CLOSE,
              label=gettext(u"close"), name=u'btn_close', parent=self,
              pos=wx.Point(350, 307), size=wx.Size(100, 26), style=0)
        self.btn_close.Bind(wx.EVT_BUTTON, self.OnBtn_closeButton,
              id=wxID_DIALOG1BTN_CLOSE)

        # label=u'mysql,oracle10g,sqlserver2005'
        self.staticText1 = wx.StaticText(id=wxID_DIALOG1STATICTEXT1,
              label=u' ', name='staticText1',
              parent=self, pos=wx.Point(370, 56), size=wx.Size(30, 14),
              style=0)
    def Ontxt_dbtypeKillFocus(self, event):
        if self.txt_dbtype.Value=="sqlserver2005":
            self.txt_port.Value="1433"
#            self.txt_port.Enable(False)
            
        else:
            self.txt_port.Enable(True)
            if self.txt_dbtype.Value=="mysql":
                self.txt_port.Value="3306"
            elif self.txt_dbtype.Value=="oracle10g":
                self.txt_port.Value="1521"
        self.txt_dbname.Value=""
        self.txt_user.Value=""
        self.txt_pwd.Value=""
        self.txt_ip.Value=""

        event.Skip()

    def __init__(self, parent):
        self._init_ctrls(parent)
        db_dict=get_attsite_file()["DATABASE"]
        db_engine={
                "mysql":"mysql",
                "oracle":"oracle10g",
                "sqlserver_ado":"sqlserver2005",
            }
        #初始化 页面显示信息 从 attsite中读取信息
        self.txt_dbtype.Value=(u"%s"%db_dict["ENGINE"] in db_engine.keys()) and db_engine[u"%s"%db_dict["ENGINE"]] or  u"%s"%db_dict["ENGINE"]
        self.txt_dbname.Value=u"%s"%db_dict["NAME"]
        self.txt_user.Value=u"%s"%db_dict["USER"]
        self.txt_pwd.Value=u"%s"%db_dict["PASSWORD"]
        self.txt_ip.Value=u"%s"%db_dict["HOST"]
        self.txt_port.Value=u"%s"%db_dict["PORT"]
        #if self.txt_dbtype.Value=="sqlserver2005":
             #self.txt_port.Enable(False)
        save_mid_dbinfo(self)
        self.btn_save.Enable(False)
        self.lbl_result.Label=gettext(u' ')

    def OnBtn_saveButton(self, event):
        save_succ=save_dbinfo(self)
        save_mid_dbinfo(self)
        if save_succ!=False:
            dial = wx.MessageDialog(None, gettext(u'Whether_the_synchronization_database'), gettext(u'message'),
                                          wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            result = dial.ShowModal()
            try:
                if result == wx.ID_YES:
                    self.lbl_result.Label=gettext("Initializing_database")
                    control_services(True)
                    os.system("python manage.pyc syncdb --noinput")
                    os.system("python manage.pyc reset_data")
                    self.lbl_result.Label=gettext("init_success")
                    self.Refresh()
                else:
                    print "Cancel"
            finally:
                dial.Destroy()
        self.btn_save.Enable(False)
        event.Skip()

    def OnBtn_testButton(self,event):
        save_suc=save_dbinfo(self)
        import subprocess
        if save_suc==False:
            self.lbl_result.Label=gettext(u'test_fail')
        else:
            try:
                self.lbl_result.Label=gettext("testing")
                flag=False
                p = subprocess.Popen("python manage.pyc test_conn", shell=False,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=win32con.CREATE_NO_WINDOW)
                t_beginning = time.time()
                seconds_passed = 0
                timeout=30
                while True:
                    if p.poll() is not None:
                        break
                    seconds_passed = time.time() - t_beginning
                    if timeout and seconds_passed > timeout:
                        p.terminate()
                        self.lbl_result.Label=gettext("test_connecton_fail")
                        break
                    time.sleep(0.1)
                stderrdata = p.communicate()
                #print 'error--------',stderrdata,'p.returncode',p.returncode
                if stderrdata[1]!='' or p.returncode!=0:
                    flag=False
                    self.btn_save.Enable(False)
                    self.lbl_result.Label=gettext("test_connecton_fail")
                else:
                    flag=True
                    self.btn_save.Enable(True)
                    self.lbl_result.Label=gettext("test_connecton_success")
            except:
                self.lbl_result.Label=gettext("test_connecton_fail")
            revert(self)
            self.Refresh()

    def OnBtn_closeButton(self, event):
        self.Close()
        event.Skip()

[wxID_WEBPORTSET, wxID_WEBPORTSETBTN_CLOSE, wxID_WEBPORTSETBTN_SAVE,
 wxID_WEBPORTSETBTN_TEST_PORT, wxID_WEBPORTSETLBL_PORT,
 wxID_WEBPORTSETLBL_TEST_RESULT, wxID_WEBPORTSETSTATICBOX1,
 wxID_WEBPORTSETTXT_PORT,wxID_FRAME1CHECKBOX1,
] = [wx.NewId() for _init_ctrls in range(9)]

class WebPortSet(wx.Dialog):
#    global int_port1
#    db_dict=get_attsite_file()["Options"]
#    int_port1=u"%s"%db_dict["Port"]
    #print type(int_port1)
   # global str_port1
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WEBPORTSET, name=u'WebPortSet',
              parent=prnt, pos=wx.Point(462, 263), size=wx.Size(444, 259),
              style=wx.DEFAULT_DIALOG_STYLE, title=gettext(u"settings"))
        self.SetClientSize(wx.Size(436, 200))
        self.Show(True)
        #self.SetToolTipString(u'WebPortdialog')

        self.staticBox1 = wx.StaticBox(id=wxID_WEBPORTSETSTATICBOX1,
              label=gettext(u"port_settings"), name='staticBox1', parent=self,
              pos=wx.Point(35, 20), size=wx.Size(368, 128),
              style=wx.RAISED_BORDER)

        self.btn_save = wx.lib.buttons.GenButton(id=wxID_WEBPORTSETBTN_SAVE,
              label=gettext(u"save"), name=u'btn_save', parent=self,
              pos=wx.Point(96, 160), size=wx.Size(79, 26), style=0)
        self.btn_save.Bind(wx.EVT_BUTTON, self.OnBtn_saveButton,
              id=wxID_WEBPORTSETBTN_SAVE)

        self.btn_close = wx.lib.buttons.GenButton(id=wxID_WEBPORTSETBTN_CLOSE,
              label=gettext(u"close"), name=u'btn_close', parent=self,
              pos=wx.Point(270, 160), size=wx.Size(79, 26), style=0)
        self.btn_close.Bind(wx.EVT_BUTTON, self.OnBtn_closeButton,
              id=wxID_WEBPORTSETBTN_CLOSE)

        self.lbl_port = wx.StaticText(id=wxID_WEBPORTSETLBL_PORT,
              label=gettext(u"port"), name=u'lbl_port', parent=self,
              pos=wx.Point(100, 66), size=wx.Size(40, 22), style=wx.ALIGN_LEFT)

        self.txt_port = wx.TextCtrl(id=wxID_WEBPORTSETTXT_PORT,
              name=u'txt_port', parent=self, pos=wx.Point(141, 64),
              size=wx.Size(100, 22), style=wx.ALIGN_LEFT, value=u'')
        self.txt_port.SetMaxLength(5)

        self.btn_test_port = wx.lib.buttons.GenButton(id=wxID_WEBPORTSETBTN_TEST_PORT,
              label=gettext(u"test_port"), name=u'btn_test_port',
              parent=self, pos=wx.Point(260, 64), size=wx.Size(79, 22),
              style=0)
        self.btn_test_port.Bind(wx.EVT_BUTTON, self.OnBtn_test_portButton,
              id=wxID_WEBPORTSETBTN_TEST_PORT)

        self.lbl_test_result = wx.StaticText(id=wxID_WEBPORTSETLBL_TEST_RESULT,
              label=u'', name=u'lbl_test_result', parent=self, pos=wx.Point(100,
              110), size=wx.Size(150, 22), style=wx.ALIGN_LEFT)
        self.port_checkBox = wx.CheckBox(id=wxID_FRAME1CHECKBOX1,
              label=gettext(u"add_port_exception"), name='port_checkBox',
              parent=self, pos=wx.Point(100, 90), size=wx.Size(220, 14),
              style=0)
       # self.port_checkBox.SetForegroundColour(wx.Colour(230, 40, 6))
        
        self.txt_port.Bind( wx.EVT_TEXT, self.port_change_event)
        
        
    def __init__(self, parent):
       
        self._init_ctrls(parent)
        db_dict=get_attsite_file()["Options"]
        self.txt_port.Value=u"%s"%db_dict["Port"]
        self.btn_save.Enable(True)
        self.port_checkBox.SetValue(True)
        global str_port1
        str_port1=self.txt_port.Value
      
       
        
        
    def OnBtn_saveButton(self, event):
        db_dict=get_attsite_file()["Options"]
        if self.port_checkBox.IsChecked() == True :
            old_port=db_dict["Port"]
            delete_port="netsh firewall  delete portopening protocol = TCP port = "+str(old_port) ;
            
            os.system(delete_port)
      
        save_webserver_port(self.txt_port,self.lbl_test_result)
        #当保存后 关闭开始 打开的例外端口 ，另外打开新的
        
        if self.port_checkBox.IsChecked() == True :
            new_port=self.txt_port.Value
            open_port="netsh firewall add portopening protocol = TCP port = "+ str(new_port)+" name = ECOPort";
            os.system(open_port) 
        event.Skip()


    def OnBtn_closeButton(self, event):
        self.Close()
        event.Skip()
    
    def port_change_event(self,event):
      
        #print 'change',str_port1
        global str_port1
        
        str_port2=self.txt_port.Value
        if str_port2!=str_port1:
            self.btn_save.Enable(False)
        else:
            self.btn_save.Enable(True)
        event.Skip()
        
    def OnBtn_test_portButton(self, event):
        if check_port(self.txt_port,self.lbl_test_result)==True:
            global str_port1
            str_port1=self.txt_port.Value
            self.btn_save.Enable(True)
        else:
           
            self.btn_save.Enable(False) 
        
        event.Skip()




def create(parent):
    return RestoreDB(parent)

[wxID_DIALOG1, wxID_DIALOG1BUTTON1, wxID_DIALOG1BUTTON2,
 wxID_DIALOG1FILEBROWSEBUTTON1, wxID_DIALOG1GENSTATICTEXT1,
 wxID_DIALOG1GENSTATICTEXT2,
] = [wx.NewId() for _init_ctrls in range(6)]

class RestoreDB(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(462, 263), size=wx.Size(420, 250),
              style=wx.DEFAULT_DIALOG_STYLE, title=gettext(u'restore_db'))
        #self.SetClientSize(wx.Size(350, 200))
        self.Show(True)

        self.lbl_restore_db = wx.StaticBox(id=wxID_DIALOG1LBL_DBINFO,
              label=gettext(u"restore_db"),
              name=u'lbl_restore_db', parent=self,
              pos=wx.Point(25, 20), size=wx.Size(370, 150), style=0)

        self.lbl_submit = wx.lib.buttons.GenButton(id=wxID_DIALOG1BUTTON1, label=gettext(u'submit'),
              name='lbl_submit', parent=self, pos=wx.Point(100, 175),
              size=wx.Size(75, 24), style=0)
        self.lbl_submit.Bind(wx.EVT_BUTTON, self.Onlbl_submitButton,
              id=wxID_DIALOG1BUTTON1)

        self.lbl_cancel = wx.lib.buttons.GenButton(id=wxID_DIALOG1BUTTON2, label=gettext(u'close'),
              name='lbl_cancel', parent=self, pos=wx.Point(258, 175),
              size=wx.Size(75, 24), style=0)
        self.lbl_cancel.Bind(wx.EVT_BUTTON, self.Onlbl_cancelButton,
                      id=wxID_DIALOG1BUTTON2)

        self.lbl_browse = wx.lib.filebrowsebutton.FileBrowseButton(buttonText=gettext(u'browse'),
              dialogTitle=u'Choose a file', fileMask='*.*',
              id=wxID_DIALOG1FILEBROWSEBUTTON1, initialValue='', labelText=u'',
              parent=self, pos=wx.Point(38, 70), size=wx.Size(340, 56),
              startDirectory='.', style=wx.TAB_TRAVERSAL,
              toolTip=gettext(u't_select_file'))
        self.lbl_browse.SetAutoLayout(False)
        self.lbl_browse.SetLabel(u'')
        self.lbl_browse.SetValue(u'')
        db_dict=get_attsite_file()
        database_engine = db_dict["DATABASE"]["ENGINE"]
        start_path = db_dict["Options"]["BACKUP_PATH"]
        self.lbl_browse.startDirectory = start_path
        if database_engine == 'mysql':
            self.lbl_browse.fileMask = '*.sql'
        elif database_engine == 'sqlserver_ado':
            self.lbl_browse.fileMask = '*.bak'
        elif database_engine == 'oracle':
            self.lbl_browse.fileMask = '*.dmp'
        self.lbl_select_file = wx.lib.stattext.GenStaticText(ID=wxID_DIALOG1GENSTATICTEXT1,
            label=gettext(u'select_file'), name='lbl_select_file', parent=self,
            pos=wx.Point(40, 50), size=wx.Size(230, 24), style=0)
        self.lbl_info = wx.StaticText(id=wxID_DIALOG1GENSTATICTEXT2,
            label=u'', name='lbl_info', parent=self,
            pos=wx.Point(40, 125), size=wx.Size(240, 24), style=wx.ALIGN_LEFT)
        #self.genStaticText2.BestSize(360,24)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def Onlbl_submitButton(self, event):
        #print dir(self.fileBrowseButton1)
        check_and_restore_db(self.lbl_browse,self.lbl_info)
        event.Skip()
    def Onlbl_cancelButton(self, event):
           self.Close()
           event.Skip()

def check_and_restore_db(fileBrowse,lbl_info):
    path = fileBrowse.GetValue()
    db_dict=get_attsite_file()["DATABASE"]
    database_engine = db_dict["ENGINE"]
    database_user = db_dict["USER"]
    database_password = db_dict["PASSWORD"]
    database_host = db_dict["HOST"]
    database_name = db_dict["NAME"]
    database_port = db_dict["PORT"]
    #print database_engine
    if path == "" or path == None:
        #print 'please select a file'
        #print gettext(u'restore_ok_start_service')
        #print gettext(u'none_file')
        lbl_info.Label= gettext(u'none_file')
    else:
        s = path.split(".")[1]
        if s=='sql' and database_engine == 'mysql':
            lbl_info.Label = gettext(u'stop_service')
            control_services(True, False)
            lbl_info.size = wx.Size(460, 24)
            lbl_info.Label = gettext(u'restoring')
            if database_password != "":
                cmd = 'mysql -u%s -p%s -h %s --port %s --database %s <%s'%(database_user,database_password,database_host,database_port, database_name,path)
            else:
                cmd = 'mysql -u%s -h %s --port %s --database %s <%s'%(database_user,database_host, database_port, database_name,path)
            #print cmd
            try:
                res = os.system(cmd.encode('gbk'))
                if res == 1:
                    lbl_info.Label=gettext(u'restore_failed')
                    control_services(False, False)
                    return
                lbl_info.Label=gettext(u'restore_ok_start_service')
                control_services(False, False)
                lbl_info.Label=gettext(u'complate')
            except:
                lbl_info.Label=gettext(u'restore_failed')
                import traceback;traceback.print_exc();
        elif s == 'bak' and database_engine == 'sqlserver_ado':
            lbl_info.Label= gettext(u'stop_service')
            control_services(True, False)
            lbl_info.Label = gettext(u'restoring')
            try:
                int(database_name)
                database_name='[%s]'%database_name
            except:
                pass
            
            cmd  = '''sqlcmd -U %s -P %s -S %s -Q "restore database %s from disk='%s' with replace"'''%(database_user,database_password,database_host,database_name,path)
            #print cmd
            try:
                res = os.system(cmd.encode('gbk'))
                if res == 1:
                    lbl_info.Label=gettext(u'restore_failed')
                    control_services(False, False)
                    return

                lbl_info.Label = gettext(u'restore_ok_start_service')
                control_services(False, False)
                lbl_info.Label=gettext(u'complate')

            except:
                lbl_info.Label=gettext(u'restore_failed')
                import traceback;traceback.print_exc();
        elif s == 'dmp' and database_engine == 'oracle':
            lbl_info.Label= gettext(u'stop_service')
            control_services(True, False)
            lbl_info.Label = gettext(u'restoring')
            cmd = 'imp %s/%s@%s file=%s full=y'%(database_user,database_password,database_name,path)
            #print cmd
            try:
                res = os.system(cmd.encode('gbk'))
                if res == 1:
                    lbl_info.Label=gettext(u'restore_failed')
                    control_services(False, False)
                    return

                lbl_info.Label=gettext(u'restore_ok_start_service')
                control_services(False, False)
                lbl_info.Label=gettext(u'complate')

            except:
                lbl_info.Label=gettext(u'restore_failed')
                import traceback;traceback.print_exc();
        elif s == 'bak' and database_engine == 'postgresql_psycopg2':
            lbl_info.Label= gettext(u'stop_service')
            control_services(True, False)
            lbl_info.Label = gettext(u'restoring')
            cmd = 'psql -h %s -p %s -U %s -d %s <%s'%(database_host,database_port,database_user,database_name,path)
            try:
                res = os.system(cmd.encode('gbk'))
                if res == 1:
                    lbl_info.Label=gettext(u'restore_failed')
                    control_services(False, False)
                    return

                lbl_info.Label=gettext(u'restore_ok_start_service')
                control_services(False, False)
                lbl_info.Label=gettext(u'complate')

            except:
                lbl_info.Label=gettext(u'restore_failed')
                import traceback;traceback.print_exc();

        else:
            lbl_info.Label=gettext(u'invalid_file')

def create(parent):
    return Dialog1(parent)

[wxID_DIALOG1, wxID_DIALOG1DIRBROWSEBUTTON1, wxID_DIALOG1GENBUTTON1,
 wxID_DIALOG1GENBUTTON2, wxID_DIALOG1STATICTEXT1,
] = [wx.NewId() for _init_ctrls in range(5)]

class UpdateDB(wx.Dialog):
    def _init_ctrls(self, prnt):
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(462, 263), size=wx.Size(420, 265),
              style=wx.DEFAULT_DIALOG_STYLE, title=gettext(u'setup_backup_path'))
    def __init__(self, parent):
        self._init_ctrls(parent)
#        db_dict=get_attsite_file()
#        self.select_backup_path.SetValue(u'%s'%db_dict["Options"]["BACKUP_PATH"])
    def OnsubmitButton(self, event):
#        setup_backup_path(self.select_backup_path,self.success_info)
        event.Skip()
    def OncloseButton(self, event):
        self.Close()
#        event.Skip()

class SetupBackupPath(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(462, 263), size=wx.Size(420, 265),
              style=wx.DEFAULT_DIALOG_STYLE, title=gettext(u'setup_backup_path'))
        #self.SetClientSize(wx.Size(348, 184))

        self.setup_path_box = wx.StaticBox(id=wxID_DIALOG1LBL_DBINFO,
              label=gettext(u'setup_backup_path'),
              name=u'lbl_restore_db', parent=self,
              pos=wx.Point(25, 20), size=wx.Size(370, 175), style=0)

        self.setup_backup_path = wx.StaticText(id=wxID_DIALOG1STATICTEXT1,
              label=gettext(u'select_backup_file'), name='setup_backup_path', parent=self,
              pos=wx.Point(40, 50), size=wx.Size(280, 30), style=0)

        self.select_backup_path = wx.lib.filebrowsebutton.DirBrowseButton(buttonText=gettext(u'browse'),
              dialogTitle='', id=wxID_DIALOG1DIRBROWSEBUTTON1,
              labelText='', newDirectory=False, parent=self,
              pos=wx.Point(38, 70), size=wx.Size(340, 48), startDirectory='.',
              style=wx.TAB_TRAVERSAL,
              toolTip=gettext(u't_select_directory'))
        self.success_info = wx.StaticText(id=8,
              label='', name='lbl_info', parent=self,
              pos=wx.Point(40, 110), size=wx.Size(240, 24), style=wx.ALIGN_LEFT)

        self.star = wx.StaticText(id=9,
              label=u"**", name=u'lbl_note', parent=self,
              pos=wx.Point(30, 130), size=wx.Size(20, 30), style=wx.ALIGN_LEFT)
        self.star.SetForegroundColour(wx.Colour(255, 0, 0))
        self.note = wx.StaticText(id=9,
              label=gettext(u'path_note'), name=u'lbl_note', parent=self,
              pos=wx.Point(45, 130), size=wx.Size(345, 57), style=wx.ALIGN_LEFT)

        self.submit = wx.lib.buttons.GenButton(id=wxID_DIALOG1GENBUTTON1,
              label=gettext(u'save'), name='submit', parent=self,
              pos=wx.Point(100, 200), size=wx.Size(79, 26), style=0)
        self.submit.Bind(wx.EVT_BUTTON, self.OnsubmitButton,
              id=wxID_DIALOG1GENBUTTON1)

        self.close = wx.lib.buttons.GenButton(id=wxID_DIALOG1GENBUTTON2,
              label=gettext(u'close'), name='close', parent=self,
              pos=wx.Point(258, 200), size=wx.Size(79, 26), style=0)
        self.close.Bind(wx.EVT_BUTTON, self.OncloseButton,
              id=wxID_DIALOG1GENBUTTON2)

    def __init__(self, parent):
        self._init_ctrls(parent)
        db_dict=get_attsite_file()
        self.select_backup_path.SetValue(u'%s'%db_dict["Options"]["BACKUP_PATH"])
    def OnsubmitButton(self, event):
        setup_backup_path(self.select_backup_path,self.success_info)
        event.Skip()
    def OncloseButton(self, event):
        self.Close()
        event.Skip()

class RegisterLicence(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(462, 263), size=wx.Size(470, 390),
              style=wx.DEFAULT_DIALOG_STYLE, title=gettext(u"authorization"))
        #self.SetClientSize(wx.Size(348, 184))

        self.frame_customer = wx.StaticBox(id=wxID_DIALOG1LBL_DBINFO,
              label=gettext(u"customer_info"),
              name=u'lbl_restore_db', parent=self,
              pos=wx.Point(25, 18), size=wx.Size(420, 305), style=wx.RAISED_BORDER)

        self.customer = wx.StaticText(id=12,
                     label=gettext(u"customer_code"), name='setup_backup_path', parent=self,
                     pos=wx.Point(40, 52), size=wx.Size(109, 30), style=0)

        self.macaddress = wx.StaticText(id=13,
              label=gettext(u"machine_number"), name='setup_backup_path', parent=self,
              pos=wx.Point(40, 82), size=wx.Size(109, 30), style=0)

        self.licence = wx.StaticText(id=14,
              label=gettext(u"authorization_code"), name='lbl_info', parent=self,
              pos=wx.Point(40, 112), size=wx.Size(109, 24), style=wx.ALIGN_LEFT)
            
            
        self.frame_licence = wx.StaticBox(id=20,
                      label=u"授权结果",
                      name=u'lbl_restore_dbdd', parent=self,
                      pos=wx.Point(45, 200), size=wx.Size(375, 105), style=wx.RAISED_BORDER)
        self.licence_value= wx.StaticText(id=21,
                       label="", name='licence_value', parent=self,
                       pos=wx.Point(50, 220), size=wx.Size(360, 60), style=0)
        
        self.txt_customer = wx.TextCtrl(id=15, name=u'txt_customer',
            parent=self, pos=wx.Point(150, 50), size=wx.Size(140, 22),
            style=0, value=u'')

        self.txt_mac = wx.TextCtrl(id=16, name=u'txt_mac',
            parent=self, pos=wx.Point(150, 80), size=wx.Size(270, 22),
            style=0, value=u'')
        self.txt_licence1 = wx.TextCtrl(id=17, name=u'txt_licence1',
                     parent=self, pos=wx.Point(150, 110), size=wx.Size(270, 85),
                     style=wx.TE_MULTILINE, value=u'')
        self.submit = wx.lib.buttons.GenButton(id=wxID_DIALOG1GENBUTTON1,
              label=gettext(u'register'), name='submit', parent=self,
              pos=wx.Point(100, 328), size=wx.Size(79, 26), style=0)
        self.submit.Bind(wx.EVT_BUTTON, self.OnsubmitButton,
              id=wxID_DIALOG1GENBUTTON1)

        self.close = wx.lib.buttons.GenButton(id=wxID_DIALOG1GENBUTTON2,
              label=gettext(u'close'), name='close', parent=self,
              pos=wx.Point(258, 328), size=wx.Size(79, 26), style=0)
        self.close.Bind(wx.EVT_BUTTON, self.OncloseButton,
              id=wxID_DIALOG1GENBUTTON2)

    def __init__(self, parent):
        from mysite import authorize_fun
        self._init_ctrls(parent)
        db_dict=get_attsite_file()
        cust=db_dict["SYS"]["CUSTOMER_CODE"]
        if cust:
            self.txt_customer.SetValue(cust)
        sn=db_dict["SYS"]["SN"]
        if sn:
            self.txt_licence1.SetValue(sn)
        #mac=self.get_mac()
        mac = authorize_fun.encrypt(authorize_fun.get_mac())
        #tt=self.d_encrypt(mac,2)

        self.txt_mac.SetValue(mac)
    def get_device_limit(self,sn,mac,customer_code):
        u'''得到序列号中的数据'''
        CUSTOMER_CODE=None
        ATT_DEVICE_LIMIT=None
        MAX_ACPANEL_COUNT=None
        ZKECO_DEVICE_LIMIT=None
        if sn and customer_code:    
            key="softbyzk"
            k=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
               
            ret=k.decrypt(sn.decode("base64"))
            if len(ret)>=41:
                #customer_code+att+acc+mac+zkeco
                customer=ret[:14]  
                dmac=k.decrypt(mac.decode("base64"))  
                retmac=ret[24:41]
                #zkeco=ret[41:46]
                findpos=0
                for i in range(14):
                    if(customer[i:i+1]!="0"):
                        findpos=i
                        break
                if customer_code and customer_code==customer[findpos:] and dmac==retmac:
                    CUSTOMER_CODE=customer[findpos:]            
                    ATT_DEVICE_LIMIT=int(ret[14:19])
                    MAX_ACPANEL_COUNT=int(ret[19:24])
                    if len(ret)>=46:
                        ZKECO_DEVICE_LIMIT=int(ret[41:46])
                return ZKECO_DEVICE_LIMIT,ATT_DEVICE_LIMIT,MAX_ACPANEL_COUNT
        return False
    def OnsubmitButton(self, event):
        from mysite import authorize_fun
        licence=str(self.txt_licence1.Value).strip().replace("\n","")
        customer_code=str(self.txt_customer.Value).strip()
        continueflag=True

        if not customer_code:
            wx.MessageDialog(parent=None,
                message=u"%s"%gettext(u"input_customer_code"),
                caption=u"%s"%gettext(u"note"),
                style=wx.OK).ShowModal()
            continueflag=False
        
        if continueflag and not licence:
            wx.MessageDialog(parent=None,
                message=u"%s"%gettext(u"input_authorization_code"),
                caption=u"%s"%gettext(u"note"),
                style=wx.OK).ShowModal()
            continueflag=False
        ret=""
        try:
            au=authorize_fun.AuthClass()
            au.parse_string(licence)
            #print au.check_mac()
            #print au.customer_code
            if au.check_mac() and au.customer_code==customer_code:#MAC、客户编号验证通过
                message=u"部门:%s    人员数:%s    登录用户数:%s    \n\n 后台比对指纹数:%s     后台比对面部数:%s     \n\nzkeco:%s   zktime:%s   zkaccess:%s   zkpos:%s"%(
                            int(au.dept_count),int(au.employee_count),int(au.login_user_count),int(au.finger_count),int(au.face_count),
                            int(au.zkeco_limit),int(au.att_limit),int(au.acc_limit),int(au.pos_limit))
                #self.licence_value.SetValue(message)
                self.licence_value.Label=message
                try:
#                    if authorize_fun.Ini()==0:#文件许可不读写加密狗
#                        if authorize_fun.CheckKey()==1:
#                            authorize_fun.write_value(authorize_fun.NEW_ADDRESS,licence)
#                        else:
#                            wx.MessageDialog(parent=None,
#                                message=u"%s"%gettext(u"insert_right_dog"),
#                                caption=u"%s"%gettext(u"note"),
#                                style=wx.OK).ShowModal()
#                            return False
                    
                    db_dict=get_attsite_file()
                    db_dict["SYS"]["CUSTOMER_CODE"]=customer_code.strip()
                    mac =authorize_fun.encrypt(authorize_fun.get_mac())
                    db_dict["SYS"]["MAC"]=mac.strip()
                    db_dict["SYS"]["SN"]=licence.strip().replace("\n","")
                    db_dict.save()
                        

                except :
                    import traceback;traceback.print_exc()
                    wx.MessageDialog(parent=None,
                        message=u"%s"%gettext(u"authorization_error"),
                        caption=u"%s"%gettext(u"note"),
                        style=wx.OK).ShowModal()
                    
                    return False
                wx.MessageDialog(parent=None,
                    message=u"%s"%gettext(u"authorization_success"),
                    caption=u"%s"%gettext(u"note"),
                    style=wx.OK
                ).ShowModal()
            else:
                wx.MessageDialog(parent=None,
                    message=u"%s"%gettext(u"authorization_error"),
                    caption=u"%s"%gettext(u"note"),
                    style=wx.OK).ShowModal()
                               
                    
            #ret=self.d_encrypt(licence)
        except:
            import traceback;traceback.print_exc()
            wx.MessageDialog(parent=None,
                            message=u"%s"%gettext(u"authorization_error"),
                            caption=u"%s"%gettext(u"note"),
                            style=wx.OK).ShowModal()

        event.Skip()
    def OncloseButton(self, event):
        self.Close()
        event.Skip()
    def d_encrypt(self,data,type=1):
        key="softbyzk"
        k=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
        if type==1:
            ret=k.decrypt(data.decode("base64"))
        else:
            ret=k.encrypt(data)
            ret=ret.encode("base64")
            if ret[-1:]=="\n":
                ret=ret[:-1]
        return ret
    
    def get_mac(self):
        sd=os.popen("ipconfig/all").read()
        lans= sd.split("\r\n\r\n")
        lns=[]
        for i in lans:
            ln=[str(s).strip() for s in i.split("\r\n")]
            lns.append(ln)
        dip=socket.gethostbyname(socket.gethostname())#获取主机IP地址
        import re
        mac="";
        for i in lns:#获取MAC地址
            for j in i:
                if j.strip().find(dip)!=-1:
                    for m in i:
                        L = re.findall('([0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2}-[0-9,A-F]{2})', m)
                        if L:
                            mac=L[0]
        return mac
    

#    def get_mac(self):
#        sd=os.popen("ipconfig/all").read()
#        lans=sd.split("Ethernet adapter")
#        lns=[]
#        for l in lans:
#            ln=[str(s).strip() for s in l.split("\r\n")]
#            lns.append(ln)
#        dip=socket.gethostbyname(socket.gethostname())#获取主机IP地址
#        ret=""
#        findlns=[]
#        for i in lns:
#            mac=""
#            find=False
#            for p in i:
#                p=p.split(":")
#                if p[0].strip().find("Physical Address")!=-1:
#                    mac=p[1].strip()
#                    #print mac
#                if p[0].strip().find("IP Address")!=-1 and p[1].strip()==dip:#根据网卡列表查找真实的mac地址
#                    ret=mac
#                    find=True
#                    break
#            if find:
#                break
#        return ret


def setup_backup_path(select_backup_path,success_info):
    #print select_backup_path.GetValue()
    db_dict=get_attsite_file()
    path = select_backup_path.GetValue().strip()
    try:
        if path.split("\\")[1]=="":
            success_info.Label=gettext(u"error_path")
        elif len(path.split())>1:
            success_info.Label=gettext(u"error_path")
        else:
            if os.path.exists(path) == False:
                os.mkdir(path)
            db_dict["Options"]["BACKUP_PATH"] = path
            db_dict.save()
            success_info.Label = gettext(u'save_success')
    except:
        from traceback import print_exc
        print_exc()
        success_info.Label=gettext(u"error_path")

app=wx.App()
app.MainLoop()
str_port1='80'
class MainWindow:
    def __init__(self):
        self.root=None
        msg_TaskbarRestart = win32gui.RegisterWindowMessage("TaskbarCreated");
        message_map = {
                msg_TaskbarRestart: self.OnRestart,
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                win32con.WM_USER+20 : self.OnTaskbarNotify,
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "iClockTaskbar"
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        wc.hCursor = win32api.LoadCursor( 0, win32con.IDC_ARROW )
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map # could also specify a wndproc.

        # Don't blow up if class already registered to make testing easier
        try:
            classAtom = win32gui.RegisterClass(wc)
        except win32gui.error, err_info:
            if err_info.winerror!=winerror.ERROR_CLASS_ALREADY_EXISTS:
                raise

        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow( wc.lpszClassName, "Taskbar iClock", style,
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        self._DoCreateIcons()
    def _DoCreateIcons(self):
        # Try and find a custom icon
        hinst =  win32api.GetModuleHandle(None)
        if hasattr(sys, "frozen"):
            current_path=os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
        else:
            current_path=os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
        if not current_path:
            current_path=os.getcwd()

        iconPathName = current_path+"/mysite/favicon.ico"
        if os.path.isfile(iconPathName):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        else:
            #print "Can't find a Python icon file - using default"
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, gettext(u"service_control"))
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        except win32gui.error:
            # This is common when windows is starting, and this code is hit
            # before the taskbar has been created.
            #print "Failed to add the taskbar icon - is explorer running?"
            # but keep running anyway - when explorer starts, we get the
            # TaskbarCreated message.
            pass

    def OnRestart(self, hwnd, msg, wparam, lparam):
        #print "-----restart event"
        self._DoCreateIcons()

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        #print "-----OnDestroy event"
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # Terminate the app.

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONUP:
            #print u"单击了一下"
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1023, gettext(u"config_server_port"))
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, gettext(u"config_db"))
#            win32gui.AppendMenu(menu, win32con.MF_STRING, 1028, gettext(u"setup_backup_path"))
#            win32gui.AppendMenu(menu, win32con.MF_STRING, 1027, gettext(u"restore_db"))
                        
            if is_service_stoped() or is_datacenter_stoped():
                    win32gui.AppendMenu( menu, win32con.MF_STRING, 1025, gettext(u"service_start"))
            else:
                    win32gui.AppendMenu( menu, win32con.MF_STRING, 1025, gettext(u"service_stop"))
            
            win32gui.AppendMenu( menu, win32con.MF_STRING, 1029, gettext(u"authorization"))
            win32gui.AppendMenu( menu, win32con.MF_STRING, 1026, gettext(u"exit_server_control" ))
            
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
            
            #pass
        elif lparam==win32con.WM_LBUTTONDBLCLK:
            #print u"双击了一下"
            #win32gui.DestroyWindow(self.hwnd)
            pass
        elif lparam==win32con.WM_RBUTTONUP:
            #print u"右击了一下"
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1023, gettext(u"config_server_port"))
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, gettext(u"config_db"))
#            win32gui.AppendMenu(menu, win32con.MF_STRING, 1028, gettext(u"setup_backup_path"))
#            win32gui.AppendMenu(menu, win32con.MF_STRING, 1027, gettext(u"restore_db"))
#            win32gui.AppendMenu(menu, win32con.MF_STRING, 1030, "aaa")
            
            if is_service_stoped() or is_datacenter_stoped():
                win32gui.AppendMenu( menu, win32con.MF_STRING, 1025, gettext(u"service_start"))
            else:
                win32gui.AppendMenu( menu, win32con.MF_STRING, 1025, gettext(u"service_stop"))

            win32gui.AppendMenu( menu, win32con.MF_STRING, 1029, gettext(u"authorization"))
            win32gui.AppendMenu( menu, win32con.MF_STRING, 1026, gettext(u"exit_server_control" ))

            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1


    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = win32api.LOWORD(wparam)
        if id==1023:
            if self.root:
               self.root.Close()
            frame1=WebPortSet(None)
            self.root=frame1
            frame1.ShowModal()

        elif id == 1024:  #open dialog
            if self.root:
                self.root.Close()
            frame2=DialogDb(None)
            self.root=frame2
            frame2.ShowModal()
        elif id==1029:
            if self.root:
                self.root.Close()
            frame2=RegisterLicence(None)
            self.root=frame2
            frame2.ShowModal()

        elif id == 1025: #Start services
            #print "start services"
            try:
                 if is_datacenter_stoped():
                     control_services(False)
                 else:
                     control_services(True)
            except Exception,e:
                 import traceback;traceback.print_exc();
        elif id == 1026: #
            #print "Goodbye"
            if self.root:
                self.root.Close()
            win32gui.DestroyWindow(self.hwnd)

        elif id == 1027:
            #print "restore db"
            if self.root:
                self.root.Close()
            frame3 = RestoreDB(None)
            self.root = frame3
            frame3.ShowModal()
        elif id == 1028:
            if self.root:
                self.root.Close()
            frame4 = SetupBackupPath(None)
            self.root = frame4
            frame4.ShowModal()
        elif id == 1030:    #升级数据库
            if self.root:
                self.root.Close()
            frame5 = UpdateDB(None)
            self.root = frame5
            frame5.ShowModal()

def main():
   
    w=MainWindow()
    win32gui.PumpMessages()

if __name__=='__main__':
    #print"-------gui test begin"
    exist_pro=check_process_exist('zkecomng.exe')
    #print exist_pro
    if exist_pro==True:
        #dial = wx.MessageDialog(None, gettext(u'存在'), gettext(u'message'),
        #                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        #dial.ShowModal()
#        os.system('taskkill /F /IM zkecomng.exe')
        pass
    else:
        main()
