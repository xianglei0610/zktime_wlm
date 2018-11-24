#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime, time
import threading

ONE_SECOND=datetime.timedelta(seconds=1)

def device_request(url, body=""):
    import urllib2
    if body:
        req=urllib2.Request(url, body)
    else:
        req=urllib2.Request(url)
    req.headers["Content-type"]="text/plain"
    print url
    #print req.headers, req.get_data()
    try:
        f=urllib2.urlopen(req)
        reply_body=(200, 'OK', f.read())
    except urllib2.HTTPError, e:
        if e.fp:
            reply_body=(e.code, e.msg, e.fp.read())
        else:
            reply_body=(e.code, e.msg, None)
    except Exception, e:
        reply_body=(-99999, u"%s"%e, None)
    return reply_body

DEF_TMP=("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",
)

class DeviceEmulate:
    def __init__(self, iclock_url="http://127.0.0.1:8000/iclock/", sn='100001', start_uid=19000, user_count=1000, template_count=2000):
        self.iclock_url=iclock_url
        self.sn=sn
        self.start_uid=start_uid
        
        users={}         #用户表
        for i in range(user_count):
            users[str(i+start_uid)]={'NAME': 'NAME_%s'%(start_uid+i)}
        self.user=users

        templates={}     #指纹模板表
        fc=0
        findex=0
        for fi in range(10):
            for uid, u in self.user.items():
                templates[(uid, fi)]=DEF_TMP[findex]
                fc+=1
                if fc>=template_count: break;
                findex+=1
                if findex>=len(DEF_TMP): findex=0
            if fc>=template_count: break;
        self.template=templates
        self.tc_user=0
        self.tc_trans=0
        self.stop=False
        self.FW_VERSION="Ver 3.60 Feb 20 2010"
    def stop_device(self):
        self.stop=True
    def request(self, path, query="", post=""):
        import urllib
        if type(query)==type({}):
            query=urllib.urlencode(query)
        return device_request("%s%s?SN=%s&%s"%(self.iclock_url, path, self.sn, query), post)
    def getrequest(self):
        return self.request("getrequest", {"INFO":"%s,%d,%d,%d,%s"%(self.FW_VERSION, len(self.user), len(self.template), self.tc_trans, "192.168.1.119")})
    def postcmd(self, id, cmd, ret):
        return self.request("devicecmd",post="ID=%s&Return=%s&CMD=%s"%(id, ret, cmd))
    def cdata(self):
        return self.request('cdata',"options=ALL")
    def process_cmd(self, cmd, process=None):
        #C:289:PutFile file/fw/X938/main.tgz    main.tgz.tmp
        print cmd
        try:
            cmd=cmd.split(":",2)
            cmds=cmd[2].split(' ',1)+['']
            if process:
                ret=process(cmds[0], cmds[1])
            else:
                ret="0"
            self.postcmd(cmd[1], cmds[0], ret)
        except:
            pass
    def req_and_process(self, process=None):
        res=self.getrequest()
        if res[0]==200:
            cmds=res[2].split("\n")
            for cmd in cmds:
                if cmd:
                    if cmd=="OK": break
                    self.process_cmd(cmd, process)
    def append_user(self, uid=None, name=""):
        if uid is None:
            id=len(self.user)+self.start_uid
            uid=str(id)
            while True:
                if uid not in self.user: break;
                id+=1
        else:
            if uid in self.user: return 0
        self.user[uid]={'NAME': name or ("NAME_%s"%uid)}
        return uid
    def append_template(self, uid, fid, template):
        self.template[(uid, fid)]=template
    def process_data(self, data_fun):
        i=0
        if data_fun:
            data=data_fun(self)
            if type(data)==type(()):
                stamp=data[0]
                data=data[1]
            else:
                stamp="Stamp=111222"
            if type(data) in types.StringTypes:
                data=[data,]
            for d in data:
                res=self.request('cdata', stamp, d)
                if res[0]==200:
                    i+=1
                else:
                    print "process_data error", stamp, d, res
                    break;
        return i
        
    def post_data(self, stamp, data):
        i=0
        res=self.request('cdata', stamp, "\n".join(data))
        if res[0]==200 and res[2][:3]=="OK:":
            i=len(data)
            print "\n".join(data)
        else:
            print res
        return i
        for d in data:
            res=self.request('cdata', stamp, d)
            if res[0]==200:
                i+=1
            else:
                print "process_data error", stamp, d, res
                break;
        return i
        
    def run(self, process_fun=None, transaction_per_hour=60*60, user_per_hour=60): 
        while not self.stop:
            try:
                response=self.cdata()
                if response[0]==200:
                    break
                else:
                    print response
            except:
                import traceback; traceback.print_exc()
            time.sleep(5)
        if self.stop: return
        self.param=dict([s.split("=") for s in response[2].splitlines() if "=" in s])
        delay=int(self.param["Delay"]) #间隔getrequest的时间
        realtime=self.param["Realtime"]=='1'
        interval=int(self.param['TransInterval'])
        print "delay=%s(seconds), realtime=%s, interval=%s(minutes)"%(delay, realtime, interval)
        interval=id(self)%30 #*=60

        transaction_delay=60*60/transaction_per_hour
        if transaction_delay<1: transaction_delay=1
        user_delay=60*60/user_per_hour
        if realtime: 
            min_sleep=min(user_delay, transaction_delay, delay, interval)
        else:
            min_sleep=min(interval, delay)

        d_delay=delay
        d_interval=interval
        pending_trans=[]
        pending_user=[]
        all_trans=0
        trans_user=0
        all_user=0
        seconds=0
        uids=self.user.keys()
        last_t=datetime.datetime.now()
        while not self.stop:
            #按照指定的频率生成新用户和考勤记录
            while all_user*60*60<user_per_hour*seconds:
                uid=self.append_user()
                uname=self.user[uid]["NAME"]
                #USER PIN=982 Name=Richard Passwd=9822 Card=[09E4812202] Grp=1 TZ=
                #FP PIN=982 FID=1 Valid=1 TMP=ocoRgZPRN8EwJNQxQTY......
                pending_user.append("USER PIN=%s\tName=%s\tPasswd=\tCard=\tGrp=1\tTZ="%(uid, uname))
                pending_user.append("FP PIN=%s\tFID=%s\tValid=1\tTMP=%s"%(uid, 0, DEF_TMP[all_user%len(DEF_TMP)]))
                all_user+=1    
            t=datetime.datetime.now()
            old_user=trans_user
            while all_trans*60*60<transaction_per_hour*seconds:
                uid=uids[trans_user]
                trans_user+=1
                if trans_user>=len(uids): trans_user=0
                if trans_user==old_user:
                    last_t+=ONE_SECOND
                elif last_t<t:
                    last_t+=ONE_SECOND
                pending_trans.append("%s\t%s\t0\t1"%(uid, last_t.strftime("%Y-%m-%d %H:%M:%S")))
                all_trans+=1
            if last_t<t: last_t

            #获取并处理服务器上下发的命令
            d_delay=d_delay-min_sleep
            if d_delay<=0:
                self.req_and_process(process_fun)
                d_delay=delay
            
            post_data=realtime

            #处理上传数据的间隔时间
            d_interval=d_interval-min_sleep
            if d_interval<=0:
                d_interval=interval
                post_data=True
            
            if post_data: #需要检查并上传新数据
                stamp=int(time.mktime(time.gmtime()))
                if pending_user:
                    i=self.post_data("OpStamp=%s"%stamp, pending_user)
                    pending_user=pending_user[i:]
                    self.tc_user+=i
                if pending_trans:
                    j=self.post_data("Stamp=%s"%stamp, pending_trans)
                    pending_trans=pending_trans[j:]
                    self.tc_trans+=j
            time.sleep(min_sleep)
            seconds+=min_sleep

DEFAULT_EMP_COUNT=100

def create_many_trans(t):
    users=['%s'%(i+20) for i in range(DEFAULT_EMP_COUNT)]
    return "\n".join(["%s\t%s\t0\t1"%(u, t) for u in users])

def post_many_trans(device, c):
    d=datetime.datetime.now()-datetime.timedelta(365)
    dt=datetime.timedelta(seconds=1)
    for i in range(c):
        trans=create_many_trans(d.strftime("%Y-%m-%d %H:%M:%S"))
        d+=dt
        print device.request('cdata', 'Stamp=111222', trans)
    
def p_proc(cmd, args):
    if 'PutFile'==cmd:
        if 'main.tgz' in args:  return 335063
        if 'libzkfp.so.3.5.1' in args:  return 171148
        if 'libfpsensor.so' in args:  return 38224
        if 'LANGUAGE.S' in args:  return 9911
        if 'auto.sh' in args:  return 1227
    return "0"


class DeviceThread(threading.Thread):
    def __init__(self, sn, iclock_url="http://192.168.1.117:8010/iclock/", start_uid=19000):
        threading.Thread.__init__(self)
        self.device=DeviceEmulate(iclock_url, sn, start_uid=start_uid)
        print "create a device %s OK"%sn
    def run(self):
        self.device.run()
    def stop_device(self):
        self.device.stop_device()
    def tc(self):
        return self.device.tc_trans

def test_run(c, url):
    devices=[]
    for i in range(c):
        device=DeviceThread('00801181%05d'%i, url, start_uid=19000+i*1000)
        devices.append(device)
        device.start()
        if i%10==1: time.sleep(1)
    return devices

if __name__=="__main__":
    import sys
    try:
        url=sys.argv[1]
        c=int(sys.argv[2])
        total=int(sys.argv[3])
    except:
        print "Usage: %s iclock_url device_count total_trans\n"%sys.argv[0]
        sys.exit(1)
    devices=test_run(c, url)
    while True:
        time.sleep(10)
        c=sum([device.tc() for device in devices])
        print "--------------------------------"
        print u"pushed transaction:", c
        print "--------------------------------"
        print 
        if c>total:
            for d in devices: d.stop_device()     #设置线程结束标志
            for d in devices: d.join()             #等待线程结束
            c=sum([device.tc() for device in devices])
            print "--------------------------------"
            print u"pushed transaction:", c
            print "--------------------------------"
            print u"Finished, press Ctrl+C to exit."    
            time.sleep(100000)
            break;
        
    
