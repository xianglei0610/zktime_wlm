# coding=utf-8
import datetime
import base64

from django.db import connections, IntegrityError
conn = connections['default']
from django.conf import settings
from constant import DEVELOP_MODEL
from constant import SYNC_MODEL,ATT_DEAL_BAT_SIZE
from sync_models import Device

if SYNC_MODEL:
    from sync_conv_att import line_to_log
else:
    from conv_att import line_to_log,commit_log

def sync_cdata_post_trans(device, raw_data, head=None,old_head=None):
    '''
    log_stamp ( 以 Stamp 结尾的请求)
    raw_data 请求的原始数据
    head 头信息字典
    old_head 包含Stamp name 的头数据
    '''
    log = None
    okc = 0;    #----成功的行数
    errerc = 0;    #----失败的行数
    retmsg = None   #---成功的首行信息
    if DEVELOP_MODEL or len(raw_data)<100:
        m_attrecord = []
        lines = raw_data.splitlines()
        m_tmp = [e for e in lines if e]
        lines_len = len(m_tmp)
        #print 'get batch data',lines_len
        for line in m_tmp:  #--- 原始数据分行解析
            if line:
                m_attrecord.append(line)
                flag = len(m_attrecord)>=ATT_DEAL_BAT_SIZE or len(m_attrecord)==lines_len
                try:
                    if head['Z']=='0':
                        if flag:
                            log = line_to_log(device, m_attrecord,False)
                            m_attrecord = []
                            lines_len -= ATT_DEAL_BAT_SIZE
                    else:
                        if flag:
                            log = line_to_log(device, m_attrecord)
                            m_attrecord = []
                            lines_len -= ATT_DEAL_BAT_SIZE
                except Exception, e:  #行数据解析错误
                    import traceback; traceback.print_exc();
                    log = None
                if log: #---解析成功
                    okc += 1
                    if not retmsg:
                        retmsg = log
                else:   #----解析失败
                    errerc +=1 
        return (okc, errerc, retmsg)  #---------返回 成功的行数,错误的行数,和成功首行输出信息
    else:
        from sync_store import save_att_file
        save_att_file(device.sn,raw_data)
        return (1,0,'')
    
def cdata_post_trans(device, raw_data, head=None,old_head=None):
    '''
    log_stamp ( 以 Stamp 结尾的请求)
    raw_data 请求的原始数据
    head 头信息字典
    old_head 包含Stamp name 的头数据
    '''
    cursor = conn.cursor()  #---数据库操作对象
    okc = 0;    #----成功的行数
    errorLines = [] #---发生保存错误的记录
    cacheLines = [] #---本次提交的行集合
    errorLogs = []  #---解析出错、不正确数据的行
    sqls = []
    commitLineCount = 700 #达到700行就提交一次
    if settings.DATABASE_ENGINE == "sqlserver_ado": commitLineCount = 50
    alog = None #---成功的首行信息
    for line in raw_data.splitlines():  #--- 原始数据分行解析
        if line:
            eMsg = ""
            try:
                if head['Z']=='0':
                    log = line_to_log(device, line,False)
                else:
                    log = line_to_log(device, line) #---解析考勤数据
            except Exception, e:  #行数据解析错误
                eMsg = u"%(mg)s" % {"mg":e.message}
                import traceback; traceback.print_exc();
                print eMsg
                log = None
            if log: #---解析成功
                sqls.append(log)
                cacheLines.append(line) #先记住还没有提交数据，commit不成功的话可以知道哪些数据没有提交成功
                if len(cacheLines) >= commitLineCount: #达到一定的行就提交一次
                    try:
                        commit_log(cursor, sqls, conn)  #---提交日志处理
                        okc += len(cacheLines)
                        if not alog:
                            alog = cacheLines[0]
                    except IntegrityError:
                        errorLines += cacheLines    #----错误的行
                    except Exception, e:
                        import traceback;traceback.print_exc()
                        conn.close()
                        cursor = conn.cursor()
                        errorLines += cacheLines
                    cacheLines = [] #----执行一次后恢复初始状态
                    sqls = []
            else:   #----解析失败
                if not head['Z']=='0':
                    errorLogs.append("%s\t--%s" % (line, eMsg and eMsg or "Invalid Data"))
    if cacheLines: #解析成功的数据  第二次
        try:
            commit_log(cursor, sqls, conn)
            okc += len(cacheLines)
            if not alog:
                alog = cacheLines[0]
        except IntegrityError:
            errorLines += cacheLines
        except Exception, e:
            import traceback;traceback.print_exc()
            print "try again"
            conn.close()
            cursor = conn.cursor()
            errorLines += cacheLines

    if errorLines: #(上两步)提交失败的数据
        cacheLines = errorLines
        errorLines = []
        for line in cacheLines: #---第三次提交数据
            if line not in errorLogs:
                try:
                    if head['Z']=='0':
                        log = line_to_log(device, line,False)
                    else:
                        log = line_to_log(device, line)
                    commit_log(cursor, log, conn)
                    if not alog: alog = cacheLines[0]
                    okc += 1
                except Exception, e:
                    pass
    errorLines += errorLogs #---解析失败的数据返成提交失败的数据
    
    dlogObj = ""
    try:
        if okc == 1:
            dlogObj = alog
        elif okc > 1:
            dlogObj = alog + ", ..."
    except:pass
#    print okc, len(raw_data.splitlines())
    
    return (okc, len(errorLines), dlogObj)  #---------返回 成功的行数,错误的行数,和成功首行输出信息