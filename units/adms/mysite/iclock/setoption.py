#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
import os
import string
from django.contrib import auth
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context, RequestContext
import dict4ini
from django.conf import settings

ENGINE_CHOICES = (
        'mysql',
        'sqlite3',
        'oracle',
        'ado_mssql'
)

YN_CHOICES = (
        (1, _(u'是')),
          (0, _(u'否')),
)

def index(request):
        if request.META['REMOTE_ADDR']!='127.0.0.1':
                return render_to_response("404.html", {'content':_(u'你必须从你的站点修改配置！')}, RequestContext(request, {}))
        if request.method == "GET":
                x = dict4ini.DictIni('attsite.ini')
                WebPort        = x.Options.Port 
                return render_to_response("setoption.html", {"WebPort":WebPort,"DbEngine":settings.DATABASE_ENGINE,"DatabaseName":settings.DATABASE_NAME,"DatabaseUser":settings.DATABASE_USER,"DatabasePassword":settings.DATABASE_PASSWORD,"DatabasePort":settings.DATABASE_PORT,"DatabaseHost":settings.DATABASE_HOST,"PIN_WIDTH":settings.PIN_WIDTH,"ENCRYPT":settings.ENCRYPT,"PAGE_LIMIT":settings.PAGE_LIMIT,"REALTIME":settings.TRANS_REALTIME,"AUTO_REG":settings.ICLOCK_AUTO_REG, "DBEC": ENGINE_CHOICES,"YN":YN_CHOICES }, RequestContext(request, {}))
        elif request.method == "POST":
                x = dict4ini.DictIni('attsite.ini')
                x.Options.Port = int(request.REQUEST['WebPort'])
                x.DATABASE.ENGINE = request.REQUEST['DbEngine'].encode('ASCII')
                x.DATABASE.NAME = request.REQUEST['DatabaseName'].encode('ASCII')
                x.DATABASE.USER = request.REQUEST['DatabaseUser'].encode('ASCII')
                x.DATABASE.PASSWORD = request.REQUEST['DatabasePassword'].encode('ASCII')
                x.DATABASE.PORT = int(request.REQUEST['DatabasePort'])
                x.DATABASE.HOST = request.REQUEST['DatabaseHost'].encode('ASCII')
                x.SYS.PIN_WIDTH = int(request.REQUEST['PIN_WIDTH'])
                x.SYS.ENCRYPT = int(request.REQUEST['ENCRYPT'])
                x.SYS.PAGE_LIMIT = int(request.REQUEST['PAGE_LIMIT'])
                x.SYS.REALTIME = int(request.REQUEST['REALTIME'])
                x.SYS.AUTO_REG = int(request.REQUEST['AUTO_REG'])
                x.save()
                return render_to_response("info.html", {'content':_(u'设置成功')}, RequestContext(request, {}))

