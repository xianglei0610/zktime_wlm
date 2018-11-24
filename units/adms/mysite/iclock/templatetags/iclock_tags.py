#!/usr/bin/env python
#coding=utf-8
import datetime
from django.db import models, connection
from django import template
from mysite.settings import VERSION, ENABLED_MOD, STD_DATETIME_FORMAT
from cgi import escape
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from mysite.iclock.datautils import GetModel, hasPerm
from django.db import models
from django.utils.encoding import force_unicode, smart_str
from mysite.iclock.datas import GetLeaveClasses,GetSchClasses,FindSchClassByID,GetExceptionText
from mysite.iclock.models import transAttState,transAbnormiteName
from mysite.iclock.datasproc import *
from mysite.utils import *
register = template.Library()
LClass=[]
@register.inclusion_tag('filters.html')
def filters(cl):
    return {'cl': cl}

def filter(cl, spec):
    return {'title': spec.title(), 'choices' : list(spec.choices(cl))}
filter = register.inclusion_tag('admin/filter.html')(filter)


@register.simple_tag
def current_time(format_string):
    return str(datetime.datetime.now())

@register.filter
def HasPerm(user, operation): #判断一个登录用户是否有某个权限
	return user.has_perm(operation)
	
@register.filter
def menuItem(user, operation): #根据一项数据模型表操作产生菜单项
	if not isinstance(user, models.Model): user=user.user
	op, dm=operation.split('_')
	model=GetModel(dm)
	if model:
		try:
			iclock_url_rel=user.iclock_url_rel
		except:
			iclock_url_rel='..'
		if user.has_perm(operation):
			return u'<li><a href="%s/data/%s/">%s</a></li>'%(iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())
		else:
			return u'<li class="disablemenu">&nbsp;&nbsp;%s</li>'%model._meta.verbose_name.capitalize()
	return ""

@register.filter
def opMenuItem(user, operation): #根据一项操作产生操作菜单项!!!
	if user.has_perm(operation):
		return u'<li><a href="%s/data/%s/">%s</a></li>'%(iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())
	else:
		return u'<li class="disablemenu">&nbsp;&nbsp;'+model._meta.verbose_name+'</li>'
				
@register.filter
def reqHasPerm(request, operation): #判断一个当前请求的数据模型表是否有某个权限
	return hasPerm(request.user, request.model, operation)

@register.filter
def buttonItem(request, operation): #根据一项操作产生操作菜单项!!!
	if hasPerm(request.user, request.model, operation):
		return u'<li><a href="%s/data/%s/">%s</a></li>'%(iclock_url_rel, model.__name__, model._meta.verbose_name)
	else:
		return u'<li>'+model._meta.verbose_name+'</li>'
	

@register.simple_tag
def version():
    return VERSION+' by <a href="http://www.zkteco.com">ZKTeco Inc.</a>'

@register.filter
def cap(s):
	return (u"%s"%s).capitalize()

@register.filter
def enabled_udisk_mod(mod_name):
	return ("udisk" in ENABLED_MOD)
@register.filter
def enabled_weather_mod(mod_name):
	return ("weather" in ENABLED_MOD)
@register.filter
def enabled_msg_mod(mod_name):
	return ("msg" in ENABLED_MOD)
@register.filter
def enabled_att_mod(mod_name):
	return ("att" in ENABLED_MOD)

@register.filter
def enabled_fptemp_mod(mod_name):
	return ("fptemp" in ENABLED_MOD)
@register.filter
def enabled_uru_mod(mod_name):
	return ("uru" in ENABLED_MOD)

@register.filter
def enabled_mod(mod_name):
	return (mod_name in ENABLED_MOD)

@register.filter
def lescape(s):
    if not s: return ""
    s=escape(s)
    return escape(s).replace("\n","\\n").replace("\r","\\r").replace("'","&#39;").replace('"','&quot;')

@register.filter
def isoTime(value):
	if value:
		return str(value)[:19]
	if value==0:
		return "0"
	return ""

@register.filter
def transLogStamp(value):
	if value:
		return OldDecodeTime(value)
	return ""

@register.filter
def stdTime(value):
	if value:
		return value.strftime(STD_DATETIME_FORMAT)
	return ""
@register.filter
def schName(value):
    if value:
	if int(value)!=-1:
	    sches=GetSchClasses()
	    i=FindSchClassByID(int(value))
	    if i!=-1:
		return sches[i]['SchName']
	else:
	    return _(u'时段')
    return ""

@register.filter
def hourAndMinute(value):
    if value:
        h=str(int(value)/60)
        m=str(int(value)%60)
        if int(m)<10:
            m='0'+str(m)
        return h+':'+m
    return ""

@register.filter
def dept_related(value):
	r=""
	j=0
	if value:
		for t in value:
			if j>2:
				r+="...,"
				break
			r+=t.dept.DeptName+","
			j+=1
		return r[:-1]
	return r
@register.filter
def shortTime(value):
    if value:
        return value.strftime('%y-%m-%d %H:%M:%S')
    return ""

@register.filter
def vshortTime(value):
    if value:
        return value.strftime('%y%m%d%H%M')
    return ""

@register.filter
def shortDTime(value):
	return value.strftime('%m-%d %H:%M')
@register.filter
def onlyTime(value):
	if value:
		try:
			return value.strftime('%H:%M:%S')
		except:
			return (value+datetime.timedelta(100)).strftime('%H:%M:%S')
	elif str(value)=='00:00:00':
		return '00:00:00'
	else:
		return ""

@register.filter
def shortDate(value):
    if value:
        return value.strftime('%y-%m-%d')
    return ""
@register.filter
def shortDate4(value):
    if value:
        return value.strftime('%Y-%m-%d')
    return ""
@register.filter
def shortDate41(value):
    if value:
        if value.strftime('%Y-%m-%d')=='1900-01-01':
            return ''
        else:
            return value.strftime('%Y-%m-%d')
    return ""

Absent={
	"0":_(u"否"),
	"1":_(u"是"),
	}
@register.filter
def isYesNo(value):
	if value:
		return Absent['1']
	return Absent['0']

@register.filter
def isTrueOrFalse(value):
	if value:
		return Absent['0']
	return Absent['1']


GENDER_CHOICES = {
	'M': _(u'男'),
	'F': _(u'女'),
}

@register.filter
def getSex(value):
    try:
        return GENDER_CHOICES[value].title()
    except:
        return ''


@register.filter
def isOdd(value):
	if int(value)%2!=0:
		return 1
	else:
		return 0

def getStateStr(s):
    if s:
	return transAttState(s)
    return "" 

@register.filter
def StateName(value):
	if value:
		return getStateStr(value)
	return ""

@register.filter
def left(value, size):
	s=(u"%s"%value)
	if len(s)>size:
		return s[:size]+" ..."
	return s

@register.filter
def HasPerm(user, operation):
	return user.has_perm(operation)

@register.filter
def Leave(value):
    global LClass
    if LClass==[]:
	LClass=GetLeaveClasses(1)
    for s in  LClass:
	if value==s["LeaveId"]:
	    return s["LeaveName"]
    return ""
@register.filter
def ExceptionStr(value):
    if value:
        return GetExceptionText(value)
    return ""
@register.filter
def AbnormiteName(value):
    if value:
        return transAbnormiteName(value)
    return ""

@register.filter
def PackList(values, field):
	l=[]
	try:
		connection.close()
		for s in values:
			l.append(s[field])
		return ','.join(l)
	except:
		connection.close()
		for s in values:
			l.append(s[field])
		return ','.join(l)
		

def _(s): return s
	
CmdContentNames={
    'DATA USER PIN=':_(u'人员信息'),
	'DATA FP PIN=':_(u'指纹'),
	'DATA DEL_USER PIN=':_(u'删除人员'),
	'DATA DEL_FP PIN=':_(u'删除指纹'),
	'CHECK':_(u'检查服务器配置'),
	'INFO':_(u'更新服务器上的设备信息'),
	'CLEAR LOG':_(u'清除考勤记录'),
	'RESTART':_(u'重新启动设备'),
	'REBOOT':_(u'重新启动设备'),
	'LOG':_(u'检查并传送新数据'),
	'PutFile':_(u'发送文件到设备'),
	'GetFile':_(u'从设备传文件'),
	'Shell':_(u'执行内部命令'),
	'SET OPTION':_(u'修改配置'),
	'CLEAR DATA':_(u'清除设备上的所有数据'),
	'AC_UNLOCK':_(u'输出开门信号'),
	'AC_UNALARM':_(u'中断报警信号'),
	'ENROLL_FP':_(u'登记人员指纹'),
}

def getContStr(cmdData):
	for key in CmdContentNames:
		if key in cmdData:
			return CmdContentNames[key]
	return "" #_("Unknown command")

@register.filter
def cmdName(value):
	return getContStr(value)

DataContentNames={
	'TRANSACT':_(u'考勤记录'),
	'USERDATA':_(u'人员信息及其指纹')}

@register.filter
def dataShowStr(value):
	if value in DataContentNames:
		return value+" <span style='color:#ccc;'>"+DataContentNames[value]+"</span>"
	return value

@register.filter
def cmdShowStr(value):
	return left(value, 30)+" <span style='color:#ccc;'>"+getContStr(value)+"</span>"

@register.filter
def thumbnailUrl(obj):
    try:
        url=obj.getThumbnailUrl()
        if url:
            try:
                fullUrl=obj.getImgUrl()
            except: #only have thumbnail, no real picture
                return "<img src='%s' />"%url
            else:
                if not fullUrl:
                    return "<img src='%s' />"%url
            return "<a href='%s'><img src='%s' /></a>"%(fullUrl, url)
    except:
        pass
    return ""

@register.filter
def GetAnnualleaves(value):
    return GetAnnualleave(value)


@register.filter
def GetUsedAnnualleaves(value,dateid):
    global LClass
    if LClass==[]:
	LClass=GetLeaveClasses(1)
    LeaveID=0
    for t in LClass:
	    if t['LeaveId']==int(dateid) and t['LeaveType']==5:
		    LeaveID=t['LeaveId']
		    break
    if LeaveID==0:
	    return 0
    AttExcep=AttException.objects.filter(UserID=int(value),ExceptionID=LeaveID,InScopeTime__gt=0,AttDate__year=datetime.datetime.now().year)
    return len(AttExcep)
@register.filter
def GetempAnnualleaves(Annualleave,Hiredday):
	if Hiredday==None:
		return Annualleave
	elif str(type(Hiredday))!="<type 'datetime.date'>" and str(type(Hiredday))!="<type 'datetime.datetime'>":
		return 0
	else:
		nowyear=datetime.datetime.now().year
		hireyear=checkTime(Hiredday).year
		if hireyear<1960:
			return 0
		diff=nowyear-hireyear
		re=0
		if diff>=1 and diff<10:
			re=5
		elif diff>=10 and diff<20:
			re=10
		elif diff>=20:
			re=15
		if Annualleave!=None:
			if Annualleave<re:
				re=Annualleave
		return re


