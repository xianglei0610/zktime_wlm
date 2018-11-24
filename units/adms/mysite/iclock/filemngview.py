#!/usr/bin/env python
#coding=utf-8
from models import *
from django.template import loader, Context, RequestContext, Library
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
import string,os
import datetime
import time
from dbapp.utils import *
from django.db import models
from django.db.models import Q
from django.contrib.auth.decorators import login_required,permission_required
from django import forms
from django.db.models.query import QuerySet, Q
import operator
from dbapp.filterspecs import FilterSpec
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import User, Permission
from django.template import Template, Context
from django.conf import settings
from dbapp.utils import getJSResponse
from desfiles import *

def showFList(con, dir):
        showList=[]
        fList=con.split("\n");
        for f in fList:
                if f and (f[0]=="d" or f.find(".dat")>=0):
                        fname=f[56:]
                        if dir: fname=dir+"/"+fname
                        fun="getFile"
                        if f[0]=="d": # is dir
                                fun="getDir"
                        showList.append("""<li><a href='javascript: %s("%s")' class='cls_%s'> %s </a>"""%(fun, fname, fun, f)+"</li>")
        return "<ol class='pre-context' start='1' style='display: block;'>\n"+"\n".join(showList)+"\n</ol>\n"

def device_cmd_check(device, id):
        try:
                cmd=devcmds.objects.get(id=id)
        except ObjectDoesNotExist:
                return getJSResponse("_ERROR_ID_")
        if cmd.CmdReturn==None:
                if cmd.CmdTransTime:
                        return getJSResponse("_PROCESSING_")
                else:
                        return getJSResponse("_WAITTING_")
        else:
                try:
                        if cmd.CmdContent.find("Shell ls -l ")==0:
                                data=file(getUploadFileName(device.SN, id, "shellout.txt")).read()
                                data=showFList(data, cmd.CmdContent[12:])                                                                                                                                                                   
                        else:
                                fname=cmd.CmdContent[8:]
                                fname=getUploadFileURL(device.SN, id, fname)
                                data="URL:"+fname #file(fname).read()
                except:
                        data="_NONE_"
                        errorLog()
                return getJSResponse(data)

def device_file_ls(device, dir):
        id=appendDevCmdOld(device, "Shell ls -l "+dir)
        return getJSResponse("%s"%id)

def device_file_get(device, fileName):
        id=appendDevCmdOld(device, "GetFile "+fileName)
        return getJSResponse("%s"%id)

def device_file_desc(device, fileName):
        try:
                data=file("%supload/%s"%(settings.ADDITION_FILE_ROOT, fileName), "rb").read()
                if fileName.find("ssruser")>=0:
                        data=desSSRUser(data)
                elif fileName.find("ssrattlog")>=0:
                        data=desSSRAttLog(data)
                elif fileName.find("oplog")>=0:
                        data=desOpLog(data)
                else: 
                        data=data.decode("GB18030")
        except:
                errorLog()
                data="ERROR"
        resp=HttpResponse(data, mimetype="text/plain")
        resp["Content-Type"]="text/plain; charset=utf-8"
        return resp

def Device(sn):
        try:
                device=get_device(sn)
                if device.DelTag:
                        return None
                if device.State==DEV_STATUS_PAUSE:
                        return None
        except ObjectDoesNotExist:
                return None
        return device

@login_required
def index(request, pageName):
        pages=(pageName+"/////").split("/");
        sn=pages[0]
        device=Device(sn)
#        print pages, device
        if device:                
                cmd=pages[1]
                if cmd=="":
                        request.user.iclock_url_rel='../..'
                        return render_to_response("filemng.html", {
                                                "device": ("%s"%device), 'iclock_url_rel': '../..',},
                                                RequestContext(request,{}));
                if cmd=="ls":
                        dirName=pageName[4+len(sn):]
                        if not dirName: dirName="/mnt"
                        return device_file_ls(device, dirName)
                if cmd=="_check_":
                        return device_cmd_check(device, pages[2])
                if cmd=="get":
                        return device_file_get(device, pageName[5+len(sn):])
                if cmd=="desc":
                        return device_file_desc(device, pageName[6+len(sn):])
        return render_to_response("404.html",{"url":request.path},RequestContext(request, {}),);

