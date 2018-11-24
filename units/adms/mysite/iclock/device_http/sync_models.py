# -*- coding: utf-8 -*-
from ooredis import *
import time

FETCH_CMDBAT_SIZE = 10
SERVER_UPDATE_BAT_SIZE = 20

MIN_REQ_DELAY = 5 #正常联网时联接服务器的间隔时间（秒）
MIN_REQ_ERROR_DELAY = 5 #联网失败后重新联接服务器的间隔时间（秒）
MIN_TRANSINTERVAL=0.5 #检查并传送新数据间隔时间（分钟）
TRANSTIMES ='00:00;14:05' # 定时检查并传送新数据时间 （时:分，24小时格式），多个时间用分号分开，最多支持10个时间 
TRANS_REALTIME=1        #设备是否实时上传记录
ENCRYPT=0
TRANSFLAG = 1111101011 #数据更新标志 (控制设备可以将哪些数据上传上来)
PUSHSTATUS = 0000000000 #数据下发标志(控制可以将哪些数据下发到机器)

PIN_WIDTH = 9
DEVICE_CREATEUSER_FLAG = True
DEVICE_CREATEBIO_FLAG = True

SORT = 0.00000

def TouchSync(SortSet,key):
    '''
    向update有序集合中添加元素
    返回成功添加的行数
    '''
    global SORT
    SORT += 0.00001
    c = SortSet.add(key, SORT)
#    if c==0:
#        '''成员已经存在则将其排到最前面去'''
#        try:
#            m_min = SortSet[0]["score"]
#            SortSet[key] = m_min-1
#        except:
#            ''' 已经是第一个了 '''
#            pass
    return c
        
def GetDateKey(pin):
    '''人员下发相关命令标识key'''
    return {'info': 'info%s'%pin,
                'fp': 'fp%s'%pin,
                'face': 'face%s'%pin,
                'pic': 'pic%s'%pin}
    
def GetDelCmd(pin):
    '''人员删除相关命令标识key'''
    return {"info": "%s|info"%(pin),
                "fp": "%s|fp"%(pin),
                "face": "%s|face"%(pin),
                "pic": "%s|pic"%(pin)
                }
    
class ObjectDoesNotExist(Exception):
    "The requested object does not exist"
    silent_variable_failure = True
    
class SyncObject(object):
    '''
    redis同步模型基类
    '''
    def __init__(self,oo,_isnew):
        self.__isnew = True
        self.isdel = False
        self.__oo = oo

    def __setattr__(self,name,value):
            self.__dict__[name] = value
              
    def get(self,field=None):
        '''
        从redis中获取该key的所有属性或者某个字段属性
        '''
        if field:
            return self.__oo[field]
        else:
            dev_r = self.__oo.getall()
            if dev_r:
                self.__isnew = False
                for e in dev_r.keys():
                    setattr(self,e,dev_r[e])
                return self
            else:
                raise ObjectDoesNotExist
            
    def isnew(self):
        return self.__isnew
    
    def delete(self):
        self.__oo.delete()
        
    def clean(self):
        '''计数器控制的对象的数据清空操作'''
        for e in self.__oo.keys():
            if e!='counter':
                del self.__oo[e]
                
    def init_counter(self):
        self.__oo.incrby("counter",0)
        
    def pipecli(self):
        _client = self.__oo._client.pipeline()
        return _client
    #pipecli = property(_pipecli)
    
    def setcli(self,client):
        '''获取模型当前使用的redis客户端对象'''
        self.__oo._client = client
        
    def getoo(self):
        '''获取当前模型对应的ooredis对象'''
        return self.__oo
    
class Device(SyncObject):
    '''
    设备模型 
    存储格式:
        设备
            device:[sn]:data        [data_dict]
            device:[sn]:update    [update_list]
        考勤区域:
            area:[id]:devices              [sn_list]
            employee:[pin]:devices    [pin_list]
    '''
    def __init__(self,sn):
        self.sn = sn
        self.__oo = Dict("device:%s:data"%sn)
        self.__isnew = True
        super(Device, self).__init__(self.__oo,self.__isnew)
               
    def __getattr__(self,name):
        '''当没有该时返回None'''
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            return None

    def set(self,field=None):
        '''设置设备相关属性 set()时触发服务器更新设备信息'''
        if field:
            self.__oo[field] = getattr(self,field)
        else:
            m_dic = {}
            for e in dir(self):
                if not e.startswith('__') and not e.startswith('_SyncObject__') and e!='isdel' and not e.startswith('_Device') and e!='sn' and not callable(getattr(self,e)):
                    m_dic[e] = getattr(self,e)
            self.__oo.sets(m_dic)
            if self.isnew():
                self.add_cmd("INFO")
            ''' 通知服务器 设备信息有更新 '''
            oo_server = SortedSet("server:update")
            m_key = 'device%s'%self.sn
            TouchSync(oo_server,m_key)
            
    def sets(self,m_dic):
        self.__oo.sets(m_dic)
    
    def delete(self):
        try:
            super(Device, self).delete()
        except:
            pass
        
    def total(self):
        '''得到已注册的设备总数'''
        all_device_key = self.__oo._client.keys("device:*:data")
        return len(all_device_key)
                
    def set_area(self,id):
        '''
        设置设备的考勤区域
        id 区域ID
        '''
        id = str(id)
        try:
            #新设置区域
            if not hasattr(self,'area') or (hasattr(self,'area') and self.area in [None,'']):
                '''要求原子操作开始'''
                Set("area:%s:devices"%id).add(self.sn)
                oo_area_emps = Set("area:%s:employees"%id)
                for pin in oo_area_emps:
                    oo_emp_devs = Set("employee:%s:devices"%pin)
                    oo_emp_devs.add(self.sn)
                self.area = id
                self.set('area')
                '''要求原子操作结束'''
            #调整区域
            else:
                old_id = self.area
                if str(old_id)!=id:
                    '''要求原子操作开始'''
                    Set("area:%s:devices"%old_id).remove(self.sn)
                    oo_old_area_emps = Set("area:%s:employees"%old_id)
                    for pin in oo_old_area_emps:
                        Set("employee:%s:devices"%pin).remove(self.sn)
                    self.fetch_cmds(all=True)
                    if id:    
                        self.add_cmd("CLEAR DATA")
                        Set("area:%s:devices"%id).add(self.sn)
                        oo_new_area_emps = Set("area:%s:employees"%id)
                        for pin in oo_new_area_emps:
                            Set("employee:%s:devices"%pin).add(self.sn)
                        self.area = id
                        self.set('area')
                    '''要求原子操作结束'''
        except:
            print 'sync error.'
            import traceback;traceback.print_exc()
            
    def add_cmd(self,cmd):
        '''
        给指定设备添加一条指令
        命令格式:
            cmd|content
        '''
        oo_cmd = SortedSet("device:%s:update"%self.sn)
        m_key = 'cmd|%s'%cmd
        TouchSync(oo_cmd,m_key)
        
    def count_cmd(self):
        '''
        获取命令数
        '''
        oo_cmd = SortedSet("device:%s:update"%self.sn)
        return len(oo_cmd)
    
    def en_fp(self):
        '''是否支持指纹'''
        try:
            _status = self.get("push_status")
        except:return False
        if _status[0]=='1' and _status[1]=='1':
            return True
        return False
    
    def en_face(self):
        '''是否支持人脸'''
        try:
            _status = self.get("push_status")
        except:return False
        if _status[0]=='1' and _status[2]=='1':
            return True
        return False
    
    def en_pic(self):
        '''是否支持人员照片'''
        try:
            _status = self.get("push_status")
        except:return False
        if _status[0]=='1' and _status[3]=='1':
            return True
        return False
        
    def pop_update(self,pin):
        '''
        当下发del时需要pop掉的之前产生的命令标识
        '''
        m_keys = GetDateKey(pin).values()
        oo_update = SortedSet("device:%s:update"%self.sn)
        for e in m_keys:
            oo_update.remove(e)#如果不存在则不会做任何动作
        
    def add_unit(self,pin):
        '''同步该人员到到设备(服务器触发)'''
        ep = Employee(pin)
        ep.call_sync(dev=False, just=self.sn)
        if self.en_fp():
            try:
                _Fpversion = self.get('Fpversion')
            except KeyError:
                _Fpversion = None
            if _Fpversion:
                try:
                    fp = FingerPrint(pin, _Fpversion).get()
                    fp.prep_data()
                    fp.call_sync(dev=False, just=self.sn)
                except ObjectDoesNotExist:
                    pass
        if self.en_face():
            try:
                _face_ver = self.get('face_ver')
            except KeyError:
                _face_ver = None
            if _face_ver:
                try:
                    face = Face(pin,  _face_ver).get()
                    face.prep_data()
                    face.call_sync(dev=False, just=self.sn)
                except ObjectDoesNotExist:
                    pass
        if self.en_pic():
            try:
                pic = EmployeePic(pin).get()
                pic.prep_data()
                pic.call_sync(dev=False, just=self.sn)
            except ObjectDoesNotExist:
                pass
    
    def del_unit(self,pin):
        '''删除设备上的该人员(服务器触发)'''
        m_keys = GetDelCmd(pin)
        oo_update = SortedSet("device:%s:update"%self.sn )
        #self.pop_update(pin)
        TouchSync(oo_update,'del|%s'%m_keys["info"])
        if self.en_fp():
            try:
                _Fpversion = self.get('Fpversion')
            except KeyError:
                _Fpversion = None
            if _Fpversion and FingerPrint(pin, _Fpversion).getoo().exists:
                TouchSync(oo_update,'del|%s'%m_keys["fp"])
        if self.en_face():
            try:
                _face_ver = self.get('face_ver')
            except KeyError:
                _face_ver = None
            if _face_ver and Face(pin,  _face_ver).getoo().exists:
                TouchSync(oo_update,'del|%s'%m_keys["face"])
        if self.en_pic():
            TouchSync(oo_update,'del|%s'%m_keys["pic"])
            
    def spread(self):
        '''用于重新下发人员到设备(服务器触发)'''
        oo_old_area_emps = Set("area:%s:employees"%self.area)
        for pin in oo_old_area_emps:
            self.add_unit(pin)
            
    def clean_cache(self):
        '''
        当设备长期不在线时清除其占用的缓存资源(包括指纹, 面部, 人员照片)
        '''
        oo_cmd = SortedSet("device:%s:update"%self.sn)
        for e in oo_cmd:
            if e:
                mb = e['value']
                try:
                    if mb.startswith('fp'):
                        pin = mb.replace('fp','')
                        m_fp = FingerPrint(pin,self.Fpversion)
                        m_fp.clean()
                    elif mb.startswith('face'):
                        pin = mb.replace('face','')
                        m_face = Face(pin,self.face_ver)
                        m_face.clean()
                    elif mb.startswith('pic'):
                        pin = mb.replace('pic','')
                        m_pic = EmployeePic(pin)
                        m_pic.clean()
                except:
                    import traceback;traceback.print_exc()
    
    def clean_update(self):
        oo_cmd = SortedSet("device:%s:update"%self.sn)
        if oo_cmd.exists:
            oo_cmd.delete()
                
    def get_option(self):
        '''
        设备获取redis中自己的参数信息
        '''
        resp = "GET OPTION FROM: %s\n" % self.sn
        resp += "Stamp=%s\n" % (self.log_stamp or 0)
        resp += "OpStamp=%s\n" % (self.oplog_stamp or 0)
        resp += "PhotoStamp=%s\n" % (self.photo_stamp or 0)
        resp += "ErrorDelay=%d\n" % max(30, MIN_REQ_ERROR_DELAY)
        resp += "Delay=%s\n" %(self.delay or MIN_REQ_DELAY)
        resp += "TransTimes=%s\n" %(self.trans_times or TRANSTIMES)
        resp += "TransInterval=%s\n" %(self.trans_interval or MIN_TRANSINTERVAL)
        resp += "TransFlag=%s\n" % (self.update_db or TRANSFLAG)
        if self.tz_adj is not None:
            resp += "TimeZone=%s\n" %(self.tz_adj or 'Etc/GMT+8')
        resp += "Realtime=%s\n" % (self.realtime or TRANS_REALTIME)
        resp += "Encrypt=%s\n\n" % (ENCRYPT or self.encrypt)
        return resp
            
    def fetch_cmds(self,all=False):
        '''
        设备获取redis中属于自己的命令
        '''
        oo_cmd = SortedSet("device:%s:update"%self.sn)
        ''' 要求原子'''
        if not all:
            cmds = oo_cmd[:FETCH_CMDBAT_SIZE]
        else:
            cmds = oo_cmd[:]
        m_cmds = [e for e in cmds if e]
        c = oo_cmd.rems(0,len(m_cmds)-1)
        ''' 要求原子'''
        resp = ''
        for e in m_cmds:
            if e:
                mb = e['value']
                if mb.startswith('info'):
                    pin = mb.replace('info','')
                    try:
                        m_emp = Employee(pin).get()
                        cc=m_emp.get_info()
                        try:
                            cc=cc.encode("gb18030")
                        except:
                            try:
                                cc=cc.decode("utf-8").encode("gb18030")
                            except:
                                import traceback;traceback.print_exc()
                                pass
                        resp+="C:%s:%s\n"%(mb,str(cc))
                    except ObjectDoesNotExist:
                        m_cmd = "DATA DEL_USER PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)

                elif mb.startswith('fp'):
                    pin = mb.replace('fp','')
                    try:
                        m_fp = FingerPrint(pin,self.Fpversion).get()
                        #业务处理
                        fps = m_fp.get_fp()
                        if len(fps)==0:
                            m_fp.prep_data()
                            m_fp.get()
                            fps = m_fp.get_fp()
                        cnt = m_fp.descount('counter')#没每取一次计数器减1
                        for e in fps:
                            resp+="C:%s:%s\n"%(mb,str(e))
                    except ObjectDoesNotExist:
                        import traceback; traceback.print_exc()
                        m_cmd = "DATA DEL_FP PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                        
                elif mb.startswith('del'):
                    pin,type = mb.replace('del|','').split('|')
                    if type=='info':
                        m_cmd = "DATA DEL_USER PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                    if type =='fp':
                        m_cmd = "DATA DEL_FP PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                    if type=='face':
                        m_cmd = "DATA DELETE FACE PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                    if type =='pic':
                        m_cmd = "DATA DELETE USERPIC PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                        
                elif mb.startswith('cmd'):
                    cmd = mb.replace('cmd|','')
                    if cmd.find('SMS')!=-1:
                        try:
                            cmd=cmd.encode("gb18030")
                        except:
                            try:
                                cmd=cmd.decode("utf-8").encode("gb18030")
                            except:
                                import traceback;traceback.print_exc()
                                pass
                        resp+="C:%s:%s\n"%('1',cmd)
                    else:
                        resp+="C:%s:%s\n"%(mb,cmd)
                          
                elif mb.startswith('face'):
                    pin = mb.replace('face','')
                    try:
                        m_face = Face(pin,self.face_ver).get()
                        fcs = m_face.get_face()
                        if len(fcs)==0:
                            m_face.prep_data()
                            m_face.get()
                            fcs = m_face.get_face()
                        cnt = m_face.descount('counter')
                        for e in fcs:
                            resp+="C:%s:%s\n"%(mb,str(e))
                    except ObjectDoesNotExist:
                        import traceback; traceback.print_exc()
                        m_cmd = "DATA DELETE FACE PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                        
                elif mb.startswith('pic'):
                    pin = mb.replace('pic','')
                    try:
                        m_pic = EmployeePic(pin).get()
                        fcs = m_pic.get_pic()
                        if len(fcs)==0:
                            m_pic.prep_data()
                            m_pic.get()
                            fcs = m_pic.get_pic()
                        cnt = m_pic.descount('counter')
                        if fcs:
                            resp+="C:%s:%s\n"%(mb,str(fcs))
                    except ObjectDoesNotExist:
                        import traceback; traceback.print_exc()
                        m_cmd = "DATA DELETE USERPIC PIN=%s"%(pin)
                        resp+="C:%s:%s\n"%(mb,m_cmd)
                        
                c -=1
        if c!=0:
            print 'sync error 101'
        if resp:
            return resp
        else:
            return 'OK\n'

class Employee(SyncObject):
    '''
    存储格式:
        人员:
            employee:[id]:info        [info_dict]
            employee:[id]:devices   [sn_list]
            employee:[id]:areas      [id_list]
    '''
    def __init__(self,pin):
        self.PIN = pin
        self.__oo = Dict("employee:%s:info"%pin)
        self.__isnew = True
        self.sync = True
        super(Employee, self).__init__(self.__oo,self.__isnew)
        
    def __getattr__(self,name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            return None

    def set(self,field=None):
        if field:
            self.__oo[field] = getattr(self,field)
        else:
            m_dic = {}
            for e in dir(self):
                if not e.startswith('__') and not e.startswith('_SyncObject__') and e!='isdel' and not e.startswith('_Employee') and e!='PIN' and not callable(getattr(self,e)):
                    m_dic[e] = getattr(self,e)
            self.__oo.sets(m_dic)
            
    def sets(self,m_dic):
        self.__oo.sets(m_dic)
    
    def call_sync(self,dev=True,just=False):
        '''触发同步各终端
        参数
            dev 发起的设备
            just 只触发同步的设备
        几种调用方式:
            call_sync(dev=False) 服务器触发(除webserver外的所有终端的同步)
            call_sync(dev=device.sn) 设备触发(其他所有终端包括webserver的同步)
            call_sync(dev=device.sn,just=device.sn) 只下发给webserver(一般是由于已经有调整区域的动作,所以只需下发到webserver)
        '''
        key = 'info%s'%self.PIN
        pin = self.PIN
        ''' 通知设备信息有更新 '''
        if just:
            oo_devices = [just]
        else:
            oo_devices = Set("employee:%s:devices"%pin)
        for sn in oo_devices:
            if dev and str(sn) == str(dev):
                continue
            oo_cmd = SortedSet("device:%s:update"%sn)
            TouchSync(oo_cmd,key)
        if dev:
            ''' 通知服务器 信息有更新 '''
            oo_server = SortedSet("server:update")
            TouchSync(oo_server,key)
            
    def delete(self):
        '''
        删除人员(redis和设备里的人员)
        '''
        '''要求原子操作开始'''
        ids_old = Set("employee:%s:areas"%self.PIN)
        for id in ids_old:
            Set("area:%s:employees"%id).remove(self.PIN)
        self.call_sync(dev=False)#触发设备删除人员
        super(Employee, self).delete()
        Set("employee:%s:devices"%self.PIN).delete()
        Set("employee:%s:areas"%self.PIN).delete()
        '''要求原子操作结束'''
    
    def get_area(self):
        '''获取人员所在区域 返回set集合'''
        m_set = Set("employee:%s:areas"%self.PIN)
        return set(m_set)
            
    def set_area(self,id,dev=None):
        '''
        增加人员的区域
        dev 用于指定不下发的设备
        '''
        id = str(id)
        print 'setting area...',id
        '''要求原子操作开始'''
        Set("employee:%s:areas"%self.PIN).add(id)
        Set("area:%s:employees"%id).add(self.PIN)
        
        oo_area_devs = Set("area:%s:devices"%id)
        oo_emp_devs = Set("employee:%s:devices"%self.PIN)
        for sn in oo_area_devs:
            oo_emp_devs.add(sn)
            if dev and str(sn) == str(dev):
                continue
            if self.sync:Device(sn).add_unit(self.PIN)
        '''要求原子操作结束'''
        
    def del_area(self,id):
        '''去除人员的区域'''
        id = str(id)
        print 'deleting area...',id
        key = 'info%s'%self.PIN
        '''要求原子操作开始'''
        Set("employee:%s:areas"%self.PIN).remove(id)
        Set("area:%s:employees"%id).remove(self.PIN)
        
        oo_area_devs = Set("area:%s:devices"%id)
        oo_emp_devs = Set("employee:%s:devices"%self.PIN)
        for sn in oo_area_devs:
            oo_emp_devs.remove(sn)
            if self.sync:Device(sn).del_unit(self.PIN)
        '''要求原子操作结束'''
        
    def set_areas(self,id_list):
        '''调整人员区域(一般由服务器触发,会引起各个设备的同步)'''
        ids_old_init = Set("employee:%s:areas"%self.PIN)
        ids_old = [e for e in ids_old_init]
        ids_old = set(ids_old)
        ids_new = set(id_list)
        ids_mid = ids_old & ids_new
        ids_del = ids_old - ids_mid
        ids_add = ids_new - ids_mid
        for x in ids_add:
            self.set_area(x)
        for y in ids_del:
            self.del_area(y)

    def get_info(self):
        '''获取人员信息'''
        from base.crypt import encryption,decryption
        from commen_utils import get_normal_card
        cc = u"DATA USER PIN=%s\tName=%s\tPasswd=%s\tGrp=%s\tCard=%s\tTZ=%s\tPri=%s" % (self.PIN, self.EName or "", self.Password or "", self.AccGroup or 1, get_normal_card(self.Card), self.TimeZones or "", self.Privilege or 0)
        return cc
    
    def getc_fp(self):
        all_key = self.__oo._client.keys("fingerprint:%s|*"%self.PIN)
        return [e.replace("fingerprint:%s|"%self.PIN,"") for e in all_key]
    
    def getc_face(self):
        all_key = self.__oo._client.keys("face:%s|*"%self.PIN)
        return [e.replace("face:%s|"%self.PIN,"") for e in all_key]
    
class FingerPrint(SyncObject):
    '''
    存储格式:
            fingerprint:[pin]|[version]     [fid_dict]    (key: fg[FID])
    '''
    def __init__(self,pin,Fpversion):
        self.key = '%s|%s'%(pin,Fpversion)
        self.__oo = Dict("fingerprint:%s"%self.key)
        self.__isnew = True
        super(FingerPrint, self).__init__(self.__oo,self.__isnew)
        
    def set(self,field=None,force=False):
        '''当set(FID_key)时触发保存到数据库'''
        if field:
            from sync_store import save_finnger
            self.__oo[field] = getattr(self,field)
            if field.startswith('fp'):
                save_finnger(self.key, field.replace('fp',''), getattr(self,field),force)
        else:
            m_dic = {}
            for e in dir(self):
                if not e.startswith('__') and not e.startswith('_SyncObject__') and e!='isdel'  and not e.startswith('_FingerPrint') and e!='key' and not callable(getattr(self,e)):
                    m_dic[e] = getattr(self,e)
            self.__oo.sets(m_dic)
                
    def call_sync(self,dev=True,just=False):
        '''
        触发同步
        '''
        pin = self.key.split('|')[0]
        Fpversion = self.key.split('|')[1]
        key = 'fp%s'%pin
        try:
            e=self.get()
        except ObjectDoesNotExist:
            return
        if just:
            oo_devices = [just]
        else:
            oo_devices = Set("employee:%s:devices"%pin)
        for sn in oo_devices:
            if dev and dev == str(sn):
                continue
            dev_obj = Device(sn)
            if not dev_obj.en_fp():
                continue
            dev_Fpversion = None
            if not just:
                try:
                    dev_Fpversion = dev_obj.get("Fpversion")
                except:
                    continue
            '''just说明是device调用的, device在调用时已经做了版本的处理所以无需在这里再做判断'''
            if just or str(dev_Fpversion) == Fpversion:
                oo_cmd = SortedSet("device:%s:update"%sn)
                c = TouchSync(oo_cmd,key)
                '''被标记为删除或已经有的命令标识的均不做处理'''
                if not self.isdel and c:
                    self.__oo.incrby("counter",1)
        if self.__oo.incrby("counter",0)==0:
            self.clean()  
            
    def delete(self):
        self.isdel = True
        self.call_sync(dev=False)
        super(FingerPrint, self).delete()
        
    @staticmethod    
    def deletes(oo,pin):
        all_key = oo._client.keys("fingerprint:%s|*"%pin)
        for e in all_key:
            try:
                pin, ver = e.replace('fingerprint:','').split('|')
                fp=FingerPrint(pin, ver)
                fp.delete()
            except:
                import traceback; traceback.print_exc()
        from sync_store import delete_finnger
        delete_finnger(pin)
        
    def prep_data(self):
        '''预备数据: 从永久存储中load数据到redis的相应key'''
        _len = len(self.__oo.keys())
        if _len==0 or (_len==1 and self.__oo.keys()[0]=='counter'):
            from sync_store import load_emp_fg
            m_fp_dict = load_emp_fg(self.key)
            if m_fp_dict:
                self.__oo.sets(m_fp_dict)
             
    def descount(self,field):
        '''计数器递减操作当为零时触发redis数据清理'''
        cnt = self.__oo.incrby(field,-1)
        if cnt==0:
            self.clean()
        if cnt<0:
            print 'sync error 102'
        return cnt
    
    def get_fp(self):
        cc = []
        for e in self.__dict__.keys():
            if  e.startswith('fp'):
                pin = self.key.split('|')[0]
                id = e.replace('fp','')
                data = getattr(self,e)
                cc.append(u"DATA UPDATE FINGERTMP PIN=%s\tValid=1\tSize=%s\tFID=%s\tTMP=%s" % (pin,len(data) , id, data) )
        return cc
    
class Face(SyncObject):
    def __init__(self,pin,face_ver):
        self.key = '%s|%s'%(pin,face_ver)
        self.__oo = Dict("face:%s"%self.key)
        self.__isnew = True
        super(Face, self).__init__(self.__oo,self.__isnew)
        
    def set(self,field=None):
        if field:
            from sync_store import save_face
            self.__oo[field] = getattr(self,field)
            if field.startswith('face'):
                save_face(self.key, field.replace('face',''), getattr(self,field))
        else:
            m_dic = {}
            for e in dir(self):
                if not e.startswith('__') and not e.startswith('_SyncObject__') and e!='isdel'  and not e.startswith('_Face') and e!='key' and not callable(getattr(self,e)):
                    m_dic[e] = getattr(self,e)
            self.__oo.sets(m_dic)
            
    def call_sync(self,dev=True,just=False):
        pin = self.key.split('|')[0]
        face_ver = self.key.split('|')[1]
        key = 'face%s'%pin
        try:
            e=self.get()
        except ObjectDoesNotExist:
            return
        if just:
            oo_devices = [just]
        else:
            oo_devices = Set("employee:%s:devices"%pin)
        for sn in oo_devices:
            if dev and dev == str(sn):
                continue
            dev_obj = Device(sn)
            if not dev_obj.en_face():
                continue
            dev_face_ver =None
            if not just:
                try:
                    dev_face_ver = dev_obj.get("face_ver")
                except:
                    continue
            if just or str(dev_face_ver) == face_ver:
                oo_cmd = SortedSet("device:%s:update"%sn)
                c = TouchSync(oo_cmd,key)
                if not self.isdel and c:
                    self.__oo.incrby("counter",1)
        if self.__oo.incrby("counter",0)==0:
            self.clean() 
                
    def delete(self):
        self.isdel = True
        self.call_sync(dev=False)
        super(Face, self).delete()
        
    @staticmethod    
    def deletes(oo,pin):
        all_key = oo._client.keys("face:%s|*"%pin)
        for e in all_key:
            try:
                pin, ver = e.replace('face:','').split('|')
                fp=Face(pin, ver)
                fp.delete()
            except:
                import traceback; traceback.print_exc()
        from sync_store import delete_face
        delete_face(pin)
        
    def prep_data(self):
        _len = len(self.__oo.keys())
        if _len==0 or (_len==1 and self.__oo.keys()[0]=='counter'):
            from sync_store import load_emp_face
            m_face_dict = load_emp_face(self.key)
            if m_face_dict:
                self.__oo.sets(m_face_dict)
              
    def descount(self,field):
        cnt = self.__oo.incrby(field,-1)
        if cnt==0:
            self.clean()
        if cnt<0:
            print 'sync error 103'
        return cnt
    
    def get_face(self):
        cc = []
        for e in self.__dict__.keys():
            if  e.startswith('face'):
                pin = self.key.split('|')[0]
                id = e.replace('face','')
                data = getattr(self,e)
                cc.append(u"DATA UPDATE FACE PIN=%s\tValid=1\tSIZE=%s\tFID=%s\tTMP=%s" % (pin,len(data) , id, data) )
        return cc
    
class EmployeePic(SyncObject):
    def __init__(self,pin):
        self.key = '%s'%pin
        self.__oo = Dict("employeepic:%s"%self.key)
        self.__isnew = True
        super(EmployeePic, self).__init__(self.__oo,self.__isnew)
          
    def set(self,field=None):
        if field:
            from sync_store import save_EmployeePic
            self.__oo[field] = getattr(self,field)
            if field.startswith('data'):
                save_EmployeePic(self.key,getattr(self,field))
        else:
            m_dic = {}
            for e in dir(self):
                if not e.startswith('__') and not e.startswith('_SyncObject__')  and e!='isdel'  and not e.startswith('_EmployeePic') and e!='key' and not callable(getattr(self,e)):
                    m_dic[e] = getattr(self,e)
            self.__oo.sets(m_dic)
            
    def call_sync(self,dev=True,just=False):
        pin = self.key
        key = 'pic%s'%pin
        try:
            e=self.get()
        except ObjectDoesNotExist:
            return
        if just:
            oo_devices = [just]
        else:
            oo_devices = Set("employee:%s:devices"%pin)
        for sn in oo_devices:
            if dev and dev == str(sn):
                continue
            dev_obj = Device(sn)
            if not dev_obj.en_pic():
                continue
            oo_cmd = SortedSet("device:%s:update"%sn)
            c = TouchSync(oo_cmd,key)
            if not self.isdel and c:
                self.__oo.incrby("counter",1)
        if self.__oo.incrby("counter",0)==0:
            self.clean() 
                
    def delete(self):
        self.isdel = True
        self.call_sync(dev=False)
        super(EmployeePic, self).delete()
        
    def prep_data(self):
        _len = len(self.__oo.keys())
        if _len==0 or (_len==1 and self.__oo.keys()[0]=='counter'):
            from sync_store import load_emp_pic
            m_pic_dict = load_emp_pic(self.key)
            if m_pic_dict:
                self.__oo.sets(m_pic_dict)
             
    def descount(self,field):
        cnt = self.__oo.incrby(field,-1)
        if cnt==0:
            self.clean()
        if cnt<0:
            print 'sync error 104'
        return cnt
    
    def get_pic(self):
        cc = u''
        if 'data' in self.__dict__.keys():
            import base64
            pin = self.key
            base64_photo=base64.b64encode(getattr(self, 'data'))
            cc += u"DATA UPDATE USERPIC PIN=%s\tSize=%s\tContent=%s\n" % (pin, str(len(base64_photo)), base64_photo)
        return cc
    
def server_update():
    '''
    获取web server需要更新的数据
    '''
    oo_cmd = SortedSet("server:update")
    ''' 要求原子'''
    cmds = oo_cmd[:SERVER_UPDATE_BAT_SIZE]
    m_cmds = [e for e in cmds if e]
    c = oo_cmd.rems(0,len(m_cmds)-1)
    ''' 要求原子'''
    resp = {'employee':[],'device':[]}
    for e in m_cmds:
        if e:
            mb = e['value']
            if mb.startswith('info'):
                pin = mb.replace('info','')
                try:
                    m_emp = Employee(pin).get().getoo()
                    m_dict = dict(m_emp).copy()
                    m_dict['PIN'] = pin
                    resp['employee'].append(m_dict)
                except ObjectDoesNotExist:
                    pass
            if mb.startswith('device'):
                sn = mb.replace('device','')
                try:
                    m_dev = Device(sn).get().getoo()
                    m_dict = dict(m_dev).copy()
                    m_dict['sn'] = sn
                    resp['device'].append(m_dict)
                except ObjectDoesNotExist:
                    pass
            c -=1
    if c!=0:
        print 'sync error 105'
    return resp