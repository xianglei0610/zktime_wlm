# coding=utf-8

from mole import route, run, static_file, error,get, post, put, delete, Mole   # 均来自Mole类
from mole.template import template, Jinja2Template
from mole import request
from mole import response
from mole import redirect

from config import  media_prefix,site_root

@route('%s/%s/:file#.*#'%(site_root,media_prefix))
def media(file):
    return static_file(file, root='./lib/serverM/static')

@route('%s/'%site_root)
def index():
    print '123'
    redirect('%s/%s/index.html'%(site_root, media_prefix))

@route('/login', method='POST')
def login():
    print '456'
    return {"msg": u"登录成功", "code": 1}

@route('/authstatus', method='POST')
def authstatus():
    return {"authed": "yes"}

@route('/xsrf')
def xsrf():
    return ''

import view_file
import view_query


if __name__  == "__main__":
    run(host='localhost', port=8086, reloader=True)