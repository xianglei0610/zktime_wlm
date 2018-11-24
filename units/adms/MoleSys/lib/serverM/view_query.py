# coding=utf-8

from mole import route,static_file
from mole import request,response,redirect
from mosys.utils import utf8 as _u
import mate.si as si

"""Interface for quering server information.

Query one or more items, seperated by comma.
Examples:
/query/*
/query/server.*
/query/service.*
/query/server.datetime,server.diskinfo
/query/config.fstab(sda1)
"""
@route('/query/:items#.*#')   
def Query(items='*'):
#    self.authed()
    items = items.split(',')
    qdict = {'server': [], 'service': [], 'config': [], 'tool': []}
    for item in items:
        if item == '**':
            # query all items
            qdict = {'server': '**', 'service': '**'}
            break
        elif item == '*':
            # query all realtime update items
            qdict = {'server': '*', 'service': '*'}
            break
        elif item == 'server.**':
            qdict['server'] = '**'
        elif item == 'service.**':
            qdict['service'] = '**'
        else:
            item = _u(item)
            iteminfo = item.split('.', 1)
            if len(iteminfo) != 2: continue
            sec, q = iteminfo
            if sec not in ('server', 'service', 'config', 'tool'): continue
            if qdict[sec] == '**': continue
            qdict[sec].append(q)

    # item : realtime update
    server_items = {
        'hostname'     : False,
        'datetime'     : True,
#        'uptime'       : True,
        'loadavg'      : True,
        'cpustat'      : True,
        'meminfo'      : True,
        'mounts'       : True, 
        'netifaces'    : True,
        'nameservers'  : True,
        'distribution' : False,
        'uname'        : False, 
        'cpuinfo'      : False,
        'diskinfo'     : False,
        'virt'         : False,
    }
    service_items = {
        'Memmcached' : True,
        'Redis'        : True,
        'webserver'        : True,
        'InstantMsg'       : True,
        'AutoCalculate'        : True,
        'WriteData'       : True,
        'ZksaasAdms'       : True,
        'ZkposAdms'        : True,
        'DataCommCenter'       : True,
        'RedisSelf'       : True,
               
#        'vpsmate'      : False,
#        'nginx'        : False,
#        'httpd'        : False,
#        'vsftpd'       : False,
#        'mysqld'       : False,
#        'redis'        : False,
#        'memcached'    : False,
#        'mongod'       : False,
#        'php-fpm'      : False,
#        'sendmail'     : False,
#        'sshd'         : False,
#        'iptables'     : False,
#        'crond'        : False,
#        'ntpd'         : False,
    }
    config_items = {
        'fstab'        : False,
    }
    tool_items = {
        'supportfs'    : False,
    }
    import cPickle
    try:
        f = open('../loop_server.pid')
        process_dic = cPickle.load(f)
        f.close()
    except:
        process_dic = {}        
    result = {}
    for sec, qs in qdict.iteritems():
        if sec == 'server':
            if qs == '**':
                qs = server_items.keys()
            elif qs == '*':
                qs = [item for item, relup in server_items.iteritems() if relup==True]
            for q in qs:
                if not server_items.has_key(q): continue
                result['%s.%s' % (sec, q)] = getattr(si.Server, q)()
        elif sec == 'service':     
            autostart_services = si.Service.autostart_list()
            if qs == '**':
                qs = service_items.keys()
            elif qs == '*':
                qs = [item for item, relup in service_items.iteritems() if relup==True]
            for q in qs:
                if not service_items.has_key(q): continue
                m_pid = process_dic.get(q,None)
                if m_pid:
                    status = si.Service.status(m_pid)
                else:
                    status = si.Service.status(q)
                result['%s.%s' % (sec, q)] = status and {        'status': status,
                    'autostart': q in autostart_services,
                } or None
        elif sec == 'config':
            for q in qs:
                params = []
                if q.endswith(')'):
                    q = q.strip(')').split('(', 1)
                    if len(q) != 2: continue
                    q, params = q
                    params = params.split(',')
                if not config_items.has_key(q): continue
                result['%s.%s' % (sec, q)] = getattr(sc.Server, q)(*params)
        elif sec == 'tool':
            for q in qs:
                params = []
                if q.endswith(')'):
                    q = q.strip(')').split('(', 1)
                    if len(q) != 2: continue
                    q, params = q
                    params = params.split(',')
                if not tool_items.has_key(q): continue
                result['%s.%s' % (sec, q)] = getattr(si.Tool, q)(*params)
    return result

@route('/killpid')
def killpid():
    m_pid = request.params.get('pid','')
    try:
        import psutil
        p = psutil.Process(int(m_pid))
        p.terminate()
    except:
        pass
    redirect('/serverM/pyred_media/index.html#/main?s=service')
