# -*- coding: utf-8 -*-
"""
Views and functions for serving static files. 
支持合并多个静态 js / css 文件的用法
"""

import mimetypes
import os
import posixpath
import re
import stat
import urllib
from django.http import Http404, HttpResponse 
from django.utils.http import http_date
from django.views.static import serve as django_serve
import datetime

def serve_combined_files(file_name, document_root):
    """
    合并多个静态 js / css 文件, 要和并的文件需在同一目录下，然后用加号连接文件名
    例如 /media/css/css.css+corner.css+tabs.css
    """
    files=file_name.split("+")
    print files
    contents=''
    file_path=''
    for path in files:
        if not file_path:
            path = posixpath.normpath(urllib.unquote(path))
            path = path.lstrip('/')
            newpath = ''
            for part in path.split('/'):
                if not part:
                    # Strip empty path components.
                    continue
                drive, part = os.path.splitdrive(part)
                head, part = os.path.split(part)
                if part in (os.curdir, os.pardir):
                    # Strip '.' and '..' in path.
                    continue
                newpath = os.path.join(newpath, part).replace('\\', '/')
            if newpath and path != newpath:
                raise Http404('"%s" does not exist' % newpath)
            fullpath = os.path.join(document_root, newpath)
            file_path = os.path.split(fullpath)[0]
        else:
            fullpath = os.path.join(file_path, path)
        if not os.path.exists(fullpath):
            raise Http404('"%s" does not exist' % fullpath)
        contents += open(fullpath, 'rb').read()
        contents += " \n\n"     #/*----%s-------*/\n"%path.decode("utf-8")
    
    fullpath = os.path.join(document_root, file_name)
    f=file(fullpath, "w+")
    f.write(contents)
    f.close()
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    response = HttpResponse(contents, mimetype=mimetype)
    response["Content-Length"] = len(contents)
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    return response

def serve(request, path, document_root=None, show_indexes=False):
    try:
        response=django_serve(request, path, document_root, show_indexes)
    except Http404, e:
        if "+" in path:
            try:
                response=serve_combined_files(path, document_root)
            except:
                import traceback; traceback.print_exc()
                raise
        else:
            raise

    return response