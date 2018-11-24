#coding=utf-8
from mysite.iclock.models import *
from django.utils.encoding import smart_str
from dbapp.datautils import *
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from dbapp.utils import getJSResponse
from mysite.personnel.models import Employee, EmpForeignKey
from constant import REALTIME_EVENT, MAX_TRANS_IN_QUEQE

def getCopyInfo(request, ModelName):
    copyInfo = request.GET.get("key", "")
    model=models.get_model("iclock", ModelName)
    toResponse = "{"
    objs = model.objects.all()
    if objs.count():
        copyFields = objs[0].GetCopyFields()
        if model == Employee:
            info = model.objects.filter(PIN=copyInfo).values(*copyFields)[0]
        elif model == iclock:
            info = model.objects.filter(SN=copyInfo).values(*copyFields)[0]
        else:
            info = model.objects.values(*copyFields)[0]        # For Exception
        for field in copyFields:
            if field == "Gender":
                toResponse += field + ":'" + ((info[field] == u'M') and _(u"男") or _(u"女")) + "',"
            else:
                f_value = info[field]
                toResponse += field + ":'" + unicode(f_value) + "',"
        toResponse = toResponse[:-1]
    toResponse += "}"
    return getJSResponse(toResponse)

def sendnew(request, ModelName):
    # 发送新的考勤记录到MS-SQL
    #from data2mssql import copyTransation
    from data2txt import copyTransation
    copyTransation()
    return getJSResponse("""'OK'""")

MAX_REALTIME_COUNT=100

@login_required
def newTransLog(request): #考勤记录实时监控
    from devview import del_len
    from redis_self.server import queqe_server
    result={}
    lastid=int(request.REQUEST.get("lastid","-1"));
    if lastid==-1:
        return render_to_response("logcheck.html",{},RequestContext(request, {}))
    q=queqe_server()
    l=q.llen(REALTIME_EVENT)
    if lastid>l and lastid>=MAX_TRANS_IN_QUEQE/2:
        ll=lastid		
        while lastid>l:
           if lastid>=MAX_TRANS_IN_QUEQE/2:
               lastid-=MAX_TRANS_IN_QUEQE/2
           else:
               break
        print "Queqe Len: ", l, ", lastid: %s->%s"%(ll, lastid)
    if l>lastid:
        event_list=q.lrange(REALTIME_EVENT, 0, -lastid)
        lastid+=len(event_list)
        event_list=event_list[:MAX_REALTIME_COUNT]  #id=%s\tPIN=%s\tEName=%s\tTTime=%s\tState=%s\tVerify=%s\tDevice=%s
    else:
        event_list=[]

    result['msg']='OK'
    result['data']=[dict([item.split("=") for item in line.split("\t")]) for line in event_list]
    result['lastId']=lastid
    result['ret']=len(event_list)
    return getJSResponse(smart_str(simplejson.dumps(result)))

"""
    logs=Transaction.objects.filter(id__gt=lastid).order_by("-id")[:MAX_REALTIME_COUNT]
    if len(logs)>0: lastid=logs[0].id
    lines=[]
    for l in logs:
        line={}
        line['id']=l.id
        line['PIN']=l.UserID.PIN
        line['EName']=l.UserID.EName
        line['TTime']=l.TTime.strftime(settings.SHORT_DATETIME_FMT)
        line['State']=l.get_State_display()
        line['Verify']=l.get_Verify_display()
        line['Device']=smart_str(l.SN)
        lines.append(line.copy())
    result['msg']='OK'
    result['data']=lines
    result['lastId']=lastid
    result['ret']=len(logs)
    return getJSResponse(smart_str(simplejson.dumps(result)))
"""

@login_required        
def newDevLog(request): #考勤记录实时监控
    device=get_device(request.REQUEST.get('SN', ""))
    result={}
    lasttid=int(request.REQUEST.get("lasttid","-1"));
    lastdid=int(request.REQUEST.get("lastdid","-1"));
    if lasttid==-1:
        return render_to_response("dlogcheck.html",{},RequestContext(request, {}))
#        if lasttid==0:
#                logs=Transaction.objects.filter(id__gt=lasttid).order_by("-id")[:1]
#        else:
    logs=Transaction.objects.filter(id__gt=lasttid).order_by("-id")
    if device: logs.filter(SN=device)
    logs=logs[:MAX_REALTIME_COUNT]
    if len(logs)>0: lasttid=logs[0].id
#        if lasttid==0:
#                logs=[]
    lines=[]
    for l in logs:
        line={}
        line['id']=l.id
        line['PIN']="%s"%l.employee()
        line['TTime']=l.TTime.strftime(settings.SHORT_DATETIME_FMT)
        line['State']=l.get_State_display()
        line['Verify']=l.get_Verify_display()
        line['SC']=l.State
        line['VC']=l.Verify
        line['Device']=smart_str(l.Device())
        line['WorkCode']=l.WorkCode=="0" and " " or l.WorkCode or ""
        line['Reserved']=l.Reserved=="0" and " " or l.Reserved or ""
        line['T']=1
        line['time']=l.TTime
        lines.append(line.copy())

    logs=oplog.objects.filter(id__gt=lastdid).order_by("-id")
    if device: logs.filter(SN=device)
    if len(logs)>0: lastdid=logs[0].id
    logs=logs[:MAX_REALTIME_COUNT]
    for l in logs:
        line={}
        line['id']=l.id
        line['PIN']=l.admin or ""
        line['TTime']=l.OPTime.strftime(settings.SHORT_DATETIME_FMT)
        line['State']=u"%s"%l.ObjName() or ""
        line['Verify']=u"%s"%l.OpName()
        line['SC']=u"%s"%l.Object
        line['VC']=u"%s"%l.OP
        line['Device']=smart_str(l.Device())
        line['WorkCode']=l.Param1 or ""
        line['Reserved']=l.Param2 or ""
        line['time']=l.OPTime
        lines.append(line.copy())
    lines.sort(lambda x,y: x['time']<y['time'] and 1 or -1)
    for i in lines: i.pop("time")
    lines=lines[:MAX_REALTIME_COUNT]
    result['msg']='OK'
    result['data']=lines
    result['lasttId']=lasttid
    result['lastDId']=lastdid
    result['ret']=len(lines)
    return getJSResponse(smart_str(simplejson.dumps(result)))

@login_required        
def uploadFile(request, path): #上传文件
    if request.method=='GET':
        return render_to_response("uploadfile.html",{"title": "Only for upload file test"})
    if "EMP_PIN" not in request.REQUEST:
        return getJSResponse("result=-1; message='Not specified a target';")
    f=device_pin(request.REQUEST["EMP_PIN"])+".jpg"
    size=saveUploadImage(request, "fileUpload", fname=get_stored_file_name("photo", None, f))
    return getJSResponse("result=%s; message='%s';"%(size,get_stored_file_url("photo",None,f)))

MAX_PHOTO_WIDTH=400

def saveUploadImage(request, requestName, fname):
    import StringIO
    import os
    try:
        os.makedirs(os.path.split(fname)[0])
    except: pass
    output = StringIO.StringIO()
    f=request.FILES[requestName]
    for chunk in f.chunks():
        output.write(chunk)
    try:
        import PIL.Image as Image
    except Execption, e:
        return None
    try:
        output.seek(0)
        im = Image.open(output)
    except IOError, e:
        return getJSResponse("result=-1; message='Not a valid image file';")
    #print f.name
    size=f.size
    if im.size[0]>MAX_PHOTO_WIDTH:
        width=MAX_PHOTO_WIDTH
        height=int(im.size[1]*MAX_PHOTO_WIDTH/im.size[0])
        im=im.resize((width, height), Image.ANTIALIAS)
    try:
        im.save(fname);
    except IOError:
        im.convert('RGB').save(fname)
    return size        

