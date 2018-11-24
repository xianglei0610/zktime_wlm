# coding=utf-8
from django.http import HttpResponse
import logging
import datetime
        
def normal_state(state):
    '''
    打卡是签到还是签退    不能解析则返回原字符
    '''
    if state == '0': return 'I'
    if state == '1': return 'O'
    try:    #---其他字符
        d = int(state)
        if d >= 32 and d < 127:
            return chr(d)
    except: pass
    return state

def normal_verify(state):
    try:
        d = int(state)
        if d >= 32 and d < 127:
            return chr(d)
    except: pass
    return state

def card_to_num(card):
    if card and len(card) == 12 and card[0] == '[' and card[-3:] == '00]':
        card = "%s" % (int(card[1:3], 16) + int(card[3:5], 16) * 256 + int(card[5:7], 16) * 256 * 256 + int(card[7:9], 16) * 256 * 256 * 256)
    return card

def get_normal_card(card):
    if not card or not card.strip(): return "[0000000000]"        
    try:
            num=int(str(card))
            card="[%02X%02X%02X%02X%02X]"%(num & 0xff, (num >> 8) & 0xff, (num >> 16) & 0xff, (num >> 24) & 0xff, (num >> 32) & 0xff)
    except:
            pass
    return card

def excsql(sql):
    from django.db import connections, IntegrityError
    conn = connections['default']
    cursor=conn.cursor()
    count=cursor.execute(sql)   
    conn._commit()
    
#def try_sql(cursor, sql, param={}):
#    try:
#        cursor.execute(sql, param)
#        conn._commit();
#    except IntegrityError:
#        raise
#    except:
#        conn.close()
#        cursor=conn.cursor()
#        cursor.execute(sql, param)
#        conn._commit()


#def get_value_from(data, key):
#    for l in data:
#        if l.find(key + "=") == 0:
#            return l[len(key) + 1:]
#    return ""

#def response_str(response, str):
#    response["Content-Length"] = len(str)
#    response.write(str)
#    return response

def parse_a_post(data, split):
    '''
    单行命令字符处理
    '''
    p = {}
    ditems = data.split(split)
    for i in range(len(ditems)):
        if not ditems[i]: continue
        k = ditems[i].split("=", 1)
        if k[0] == 'Content':
            p['Content'] = k[1] + split + split.join(ditems[i + 1:])
            break;
        elif ditems[i].find("CMD=INFO") >= 0:
            p['CMD'] = "INFO"
            p['Content'] = split.join(ditems[i + 1:])
            break;
        elif len(k) == 2:
            p[k[0]] = k[1]
    return p

def parse_posts(data):
    '''
    多行命令字符处理
    '''
    posts = []
    lines = data.split("\n")    #---分行
    if len(lines) == 0: return posts
    firstline = lines[0].split("&") #---第一行在以"&"分隔
    if len(firstline) < 2: #just a posts
        return [parse_a_post(data, "\n")]
    if "CMD=INFO" in firstline:
        d = parse_a_post(lines[0], "&")
        d['CMD'] = "INFO"
        d['Content'] = "\n".join(lines[1:])
        return [d]
    for l in lines:
        if l:
            posts.append(parse_a_post(l, "&"))
    return posts

def get_logger(path):
    import os
    if path:
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.mkdir(dir)
    logger = logging.getLogger()
    hdlr = logging.FileHandler(path)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def server_time_delta():
    return datetime.datetime.now()-datetime.datetime.utcnow()

def create_logger(fname):
    import logging
    logger = logging.getLogger()
    hdlr = logging.FileHandler(fname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger