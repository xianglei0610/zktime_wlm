# coding=utf-8
from django.db import connections, IntegrityError,DatabaseError
from constant import SYNC_MODEL
conn = connections['default']

def cdata_post_userinfo(device, raw_data,Op, head=None):
    '''
    与用户有关的命令解析
    oplog_stamp 时间戳时
    '''
    if SYNC_MODEL:
        from sync_conv_emp import line_to_emp
    else:
        from conv_emp import line_to_emp
    import time
    if SYNC_MODEL:
        cursor = None
    else:
        cursor = conn.cursor()
    c = 0;
    ec = 0;
    user = False
    for line in raw_data.splitlines():  #--- 原始数据分行解析
        try:
            if line:
                user = line_to_emp(cursor, device, line,Op)
                if SYNC_MODEL:
                    if user:
                        c = c + 1
                    else:
                        ec = ec + 1
                else:
                    c = c + 1
        except Exception, e:
            import traceback;traceback.print_exc()
            ec = ec + 1
            if not SYNC_MODEL:
                if isinstance(e, DatabaseError):
                    conn.close()
                    cursor = conn.cursor()
        time.sleep(0.1)
    if not SYNC_MODEL:
        conn._commit()
    dlogObj = "TMP"
    try:
        dlogObj = u"%s" % user
    except: pass
    return (c, ec, dlogObj)
