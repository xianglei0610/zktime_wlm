# -*- coding: utf-8 -*-
from django.db import models, connection
import datetime
from base.models import CachingModel, Operation
from mysite.personnel.models.model_dept import DeptForeignKey, DEPT_NAME, DeptManyToManyField, Department
from mysite.personnel.models.model_area import Area
from dbapp.utils import *
from django.shortcuts import render_to_response
from django.template import Context, RequestContext, Template, TemplateDoesNotExist
from mysite.settings import MEDIA_ROOT
def funTestTree(request):
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    request.dbapp_url =dbapp_url
    apps=get_all_app_and_models()
    return render_to_response('testTree.html',
            RequestContext(request,{
                    'dbapp_url': dbapp_url,
                    'MEDIA_URL':MEDIA_ROOT,
                    "current_app":'iclock', 
                    'apps':apps
                    })
            
            )
            
            
def ouputtreejsondemo(request):
    #"expanded": false
    sjson = '[ { "text": "1. Pre Lunch (120 min)", "classes": "important", "children": [ { "text": "1.1 The State of the Powerdome (30 min)" }, { "text": "1.2 The Future of jQuery (30 min)" }, { "text": "1.2 jQuery UI - A step to richnessy (60 min)" } ] }, { "text": "2. Lunch (60 min)" }, { "text": "3. After Lunch (120+ min)", "children": [ { "text": "3.1 jQuery Calendar Success Story (20 min)" }, { "text": "3.2 jQuery and Ruby Web Frameworks (20 min)" }, { "text": "3.3 Hey, I Can Do That! (20 min)" }, { "text": "3.4 Taconite and Form (20 min)" }, { "text": "3.5 Server-side JavaScript with jQuery and AOLserver (20 min)" }, { "text": "3.6 The Onion: How to add features without adding features (20 min)", "id": "36", "hasChildren": true }, { "text": "3.7 Visualizations with JavaScript and Canvas (20 min)" }, { "text": "3.8 ActiveDOM (20 min)" }, { "text": "3.8 Growing jQuery (20 min)" } ] } ]'
    return getJSResponse(sjson)


def GetChild(pn,qs,sjson):
    if not pn:
        childnodes = filter(lambda dept: dept.parent is None, qs)
    else:
        childnodes = filter(lambda dept: dept.parent_id==pn.id, qs)
    i=0
    j= len(childnodes)
    while i<j:
        if i>0 and i<j:
            sjson+=","
#        sjson+="{"
#        sjson+='"id":"'+ str(childnodes[i].id) + '",'
#        sjson+='"text:"' + childnodes[i].name  + '",'
        sjson.append("{")
        sjson.append('"id":"'+ str(childnodes[i].id) + '",')
        sjson.append('"text":"' + childnodes[i].name  + '",')
        ch=filter(lambda dept: dept.parent_id==childnodes[i].id, qs)
        if ch:
            #sjson+='children:['
            sjson.append('children:[')
            GetChild(childnodes[i],qs,sjson)
        else:
            sjson[-1]=sjson[-1][:-1]
            sjson.append("}")
            #sjson+='}'
        i+=1
    sjson+=']}'

def generateJsonTree():
    
    dept_qs=list(Department.objects.all())  #这里要根据权限过滤,所以一些节点要重新设置父节点
    dept_ids=[dept.pk for dept in dept_qs]
    for dept in dept_qs:
        if dept.parent_id not in dept_ids:
            dept.parent=None
    
    firstLevelNodes=filter(lambda a: a.parent is None, dept_qs)
    sjson=[]
    sjson.append("[")
    GetChild(None, dept_qs, sjson)
    return  "".join([i for i in sjson])[:-1]
    
def ouputtreejson(request):
    return getJSResponse(generateJsonTree())

