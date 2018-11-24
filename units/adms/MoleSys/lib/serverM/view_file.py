# coding=utf-8
import os

from mole import route,static_file
from mole import request,response
from mole.sessions import valid_user

import mate.file as file
from mosys.utils import utf8 as _u

from mate.config import Config
config = Config('./lib/serverM/config.ini')

def ret_str(content):
    return content

@route('/operation/file', method='POST')
@valid_user()
def view_file():
    payload = eval(_u(request.body.read()).replace('false','False').replace('true','True'))
    action = payload.get('action','')
    if action == 'last':
        lastdir = config.get('file', 'lastdir')
        lastfile = config.get('file', 'lastfile')
        return ret_str({'code': 0, 'msg': '', 'data': {'lastdir': lastdir, 'lastfile': lastfile}})
        
    elif action == 'listdir':
        path = payload.get('path', '')
        showhidden = payload.get('showhidden', 'off')
        remember = payload.get('remember', 'on')
        onlydir = payload.get('onlydir', 'off')
        items = file.listdir(_u(path), showhidden=='on', onlydir=='on')
        if items == False:
            return ret_str({'code': -1, 'msg': u'目录 %s 不存在！' % path})
        else:
            if remember == 'on': config.set('file', 'lastdir', path)
            return ret_str({'code': 0, 'msg': u'成功获取文件列表！', 'data': items})
        
    elif action == 'getitem':
        path = payload.get('path', '')
        item = file.getitem(_u(path))
        if item == False:
            return ret_str({'code': -1, 'msg': u'%s 不存在！' % path})
        else:
            return ret_str({'code': 0, 'msg': u'成功获取 %s 的信息！' % path, 'data': item})

    elif action == 'fread':
        path = payload.get('path', '')
        remember = payload.get('remember', 'on')
        size = file.fsize(_u(path))
        if size == None:
            return ret_str({'code': -1, 'msg': u'文件 %s 不存在！' % path})
        elif size > 1024*1024: # support 1MB of file at max
            return ret_str({'code': -1, 'msg': u'读取 %s 失败！不允许在线编辑超过1MB的文件！' % path})
        elif not file.istext(_u(path)):
            return ret_str({'code': -1, 'msg': u'读取 %s 失败！无法识别文件类型！' % path})
        else:
            if remember == 'on': config.set('file', 'lastfile', path)
            with open(path) as f: content = f.read()
            data = {
                'filename': os.path.basename(path),
                'filepath': path,
                'mimetype': file.mimetype(_u(path)),
                'content': content,
            }
            return ret_str({'code': 0, 'msg': u'成功读取文件内容！', 'data': data})

    elif action == 'fclose':
        config.set('file', 'lastfile', '')
        return ret_str({'code': 0, 'msg': ''})

    elif action == 'fwrite':
        path = payload.get('path', '')
        content = payload.get('content', '')

        if file.fsave(_u(path), content):
            return ret_str({'code': 0, 'msg': u'文件保存成功！'})
        else:
            return ret_str({'code': -1, 'msg': u'文件保存失败！'})

    elif action == 'createfolder':
        path = payload.get('path', '')
        name = payload.get('name', '').decode('utf8')

        if file.dadd(_u(path), _u(name)):
            return ret_str({'code': 0, 'msg': u'文件夹创建成功！'})
        else:
            return ret_str({'code': -1, 'msg': u'文件夹创建失败！'})

    elif action == 'createfile':
        path = payload.get('path', '')
        name = payload.get('name', '')
        if file.fadd(_u(path), _u(name)):
            return ret_str({'code': 0, 'msg': u'文件创建成功！'})
        else:
            return ret_str({'code': -1, 'msg': u'文件创建失败！'})

    elif action == 'rename':
        path = payload.get('path', '')
        name = payload.get('name', '').decode('utf8')

        if file.rename(_u(path), _u(name)):
            return ret_str({'code': 0, 'msg': u'重命名成功！'})
        else:
            return ret_str({'code': -1, 'msg': u'重命名失败！'})

    elif action == 'exist':
        path = payload.get('path', '')
        name = payload.get('name', '')
        return ret_str({'code': 0, 'msg': '', 'data': os.path.exists(os.path.join(path, name))})

    elif action == 'link':
        srcpath = payload.get('srcpath', '')
        despath = payload.get('despath', '')

        if file.link(_u(srcpath), _u(despath)):
            return ret_str({'code': 0, 'msg': u'链接 %s 创建成功！' % despath})
        else:
            return ret_str({'code': -1, 'msg': u'链接 %s 创建失败！' % despath})
    
    elif action == 'delete':
        paths = payload.get('paths', '')
        paths = paths.split(',')

        if len(paths) == 1:
            path = paths[0]
            if file.delete(_u(path)):
                return ret_str({'code': 0, 'msg': u'已将 %s 删除！' % path})
            else:
                return ret_str({'code': -1, 'msg': u'将 %s 删除失败！' % path})
        else:
            for path in paths:
                if not file.delete(_u(path)):
                    return ret_str({'code': -1, 'msg': u'将 %s 删除失败！' % path})
                    return
            return ret_str({'code': 0, 'msg': u'批量删除成功！'})

    elif action == 'tlist':
        return ret_str({'code': 0, 'msg': '', 'data': file.tlist()})

    elif action == 'trashs':
        return ret_str({'code': 0, 'msg': '', 'data': file.trashs()})

    elif action == 'titem':
        mount = payload.get('mount', '')
        uuid = payload.get('uuid', '')
        info = file.titem(_u(mount), _u(uuid))
        if info:
            return ret_str({'code': 0, 'msg': '', 'data': info})
        else:
            return ret_str({'code': -1, 'msg': '获取项目信息失败！'})

    elif action == 'trestore':
        mount = payload.get('mount', '')
        uuid = payload.get('uuid', '')
        info = file.titem(_u(mount), _u(uuid))
        if info and file.trestore(_u(mount), _u(uuid)):
            return ret_str({'code': 0, 'msg': u'已还原 %s 到 %s！' % \
                (tornado.escape.to_unicode(info['name']), tornado.escape.to_unicode(info['path']))})
        else:
            return ret_str({'code': -1, 'msg': u'还原失败！'})

    elif action == 'tdelete':
        mount = payload.get('mount', '')
        uuid = payload.get('uuid', '')
        info = file.titem(_u(mount), _u(uuid))
        if info and file.tdelete(_u(mount), _u(uuid)):
            return ret_str({'code': 0, 'msg': u'已删除 %s！' % tornado.escape.to_unicode(info['name'])})
        else:
            return ret_str({'code': -1, 'msg': u'删除失败！'})
        
        
@route('/fileupload', method='POST')
@valid_user()        
def FileUploadPost():
    #self.authed()
    path = lastdir = config.get('file', 'lastdir')#self.get_argument('path', '/')

    yield u'<body style="font-size:14px;overflow:hidden;margin:0;padding:0;">'
    if 'ufile' not in request.files:
        yield u'请选择要上传的文件！'
    else:
        yield u'正在上传...<br>'
        for file in [request.files['ufile']]:
            with open(os.path.join(path, file.filename), 'wb') as f:
                f.write(file.file.read())
            yield u'%s 上传成功！<br>' % file.filename

    yield '</body>'


@route('/file./:path#.*#',method='GET')
@valid_user()
def FileDownloadGet(path='World'):
#    self.authed()
    path = './%s'%path
    response.headers['Content-disposition'] = 'attachment; filename=%s' % os.path.basename(path)
    response.headers['Content-Transfer-Encoding'] = 'binary'
    return static_file(path, root='')


@route('/backend/copy', method='POST')
@valid_user()
def copy():
    """Copy a directory or file to a new path.
    """
    payload = eval(request.body.read().replace('false','False').replace('true','True'))
    srcpath = payload.get('srcpath','')
    despath = payload.get('despath','')
    yield u'正在复制 %s 到 %s...' % (srcpath, despath)
    try:
        import shutil
        if os.path.isdir(srcpath):
            shutil.copytree(srcpath, despath)
        else:
            shutil.copyfile(srcpath, despath)
        yield u'复制 %s 到 %s 完成！' % (srcpath, despath)
    except e:
        import traceback; traceback.print_exc()
        yield u'复制 %s 到 %s 失败！<p style="margin:10px">%s</p>' % (srcpath, despath, e)
    
@route('/backend/move', method='POST')
@valid_user()
def move():
    """Move a directory or file recursively to a new path.
    """
    payload = eval(request.body.read().replace('false','False').replace('true','True'))
    srcpath = payload.get('srcpath','')
    despath = payload.get('despath','')
    yield u'正在移动 %s 到 %s...' % (srcpath, despath)
    try:
        import shutil
        shutil.move(srcpath, despath) 
        yield u'移动 %s 到 %s 完成！' % (srcpath, despath)
    except e:
        import traceback; traceback.print_exc()
        yield u'移动 %s 到 %s 失败！<p style="margin:10px">%s</p>' % (srcpath, despath, e)
        
        
@route('/backend/copy_:m#.*#',method='GET')
def CopyStatu(m):
    return {"status": "finish", "msg": u"成功", "code": 0}

@route('/backend/move_:m#.*#',method='GET')
def MoveStatu(m):
    return {"status": "finish", "msg": u"成功", "code": 0}