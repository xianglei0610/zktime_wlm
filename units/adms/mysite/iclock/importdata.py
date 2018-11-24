#!/usr/bin/env python
#coding=utf-8
from mysite.iclock.models import *
from mysite.iclock.tools import *
from django.template import loader, Context, RequestContext, Library, Template, Context
from django.conf import settings
from django.shortcuts import render_to_response
import time, datetime
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.models import Employee, Department

lineFmt=u"&nbsp;&nbsp;&nbsp;&nbsp;%s<br />"

def InfoErrorRec(title, errorRecs):
        if not errorRecs: return ""
        time.sleep(0.1)
        fname="import_%s.txt"%(datetime.datetime.now().isoformat().replace(":",""))
        tmpFile(fname, "\n".join(errorRecs))
        #return lineFmt%(_("<a href='"+settings.UNIT_URL+"iclock/tmp/%s'> %d record(s) is duplicated or invalid.") % (fname, len(errorRecs))) #u"<a href='/iclock/tmp/%s'> %d 条数据</a>为重复或无效记录。<br />"
        return ""
def reportError(title, i, i_insert, i_update, i_rep, errorRecs):
        info=[]
        if i_insert: info.append(_(u"成功插入了 %(object_num)d 条") % {'object_num':i_insert})
        if i_update: info.append(_(u"成功修改了%(object_num)d 条") % {'object_num':i_update})
        if i_rep: info.append(_(u"%(object_num)d条已存在数据库中")% {'object_num':i_rep})
        result = u"<b>%s</b>: <br />%s%s%s<br />" % (title,
                lineFmt%(_(u"数据文件中有%(object_num)d %(object_name)s")%{'object_num':i,'object_name': title}),
                info and lineFmt%(u", ".join(info)) or "",
                InfoErrorRec(title, errorRecs))
        return result

from mysite.iclock.validdata import checkRecData,checkALogData                                 

def checkAndRunSql(cursor, sqlList, sql=None):
        error=[]
        if sql:
                sqlList.append(sql)
        if cursor and sqlList:
                if (not sql) or (len(sqlList)>=100):
#                        print "Post:", len(sqlList)
                        try:
                                commit_log(cursor, '; '.join(sqlList))
                        except Exception, er:
#                                print er
                                for s in sqlList:
                                        try:
                                                cursor.execute(s)
                                        except Exception, e:
                                                emsg="SQL '%s' Failed: %s"%(s,e)
#                                                print emsg
                                                error.append(emsg)
                        for s in range(len(sqlList)): sqlList.pop()
        return error

def upload_data(request):        # 上传导出到U盘的数据
        emps=[]
        result = ""
        sqlList=[]
        from django.db import connection as conn
        cursor = conn.cursor()
        device=check_device(request, None)
        sn = request.POST.get("SN", None)
        if not device:
                return render_to_response("info.html", {"title": _(u"失败"), "content": _(u"<h1>数据上传失败</h1>,<br />请选择考勤机") });

        SNs=getUserIclocks(request.user)
        if SNs!=settings.ALL_TAG and (device.SN not in SNs):
                return render_to_response("info.html", {"title": _(u"失败"), "content": _(u"<h1>数据上传失败</h1>,<br />没有权限导入考勤机%(object_name)s上的数据")%{'object_name':sn} });

        fs = request.FILES
        pin_pin2 = {} # 根据用户信息得到 pin 到 pin2 的一一对映，用以保存指纹模版
        errorRecs=[]
        if fs.has_key("file_user"): # 用户信息
                try:                        
                        dept = get_default_dept()        # 默认部门
                        f = fs["file_user"]
                        data=""
                        for chunk in f.chunks(): data+=chunk
        #                typedef struct _User_{                //size:72
        #                        U16 PIN;                                //[:2]
        #                        U8 Privilege;                        //[2:3]                Privilege
        #                        char Password[8];                //[3:11]        Password
        #                        char Name[24];                        //[11:35]        EName
        #                        U8 Card[4];                                //[35:39]                                        //卡号码，用于存储对应的ID卡的号码
        #                        U8 Group;                                //[39:40]        AccGroup                //用户所属的分组
        #                        U16 TimeZones[4];                //[40:48]        TimeZones                //用户可用的时间段，位标志
        #                        char PIN2[24];                        //[48:]                PIN
        #                }GCC_PACKED TUser, *PUser;        
                        fsn,upload_user,sum=checkRecData(data, 72)
                        if not fsn: raise Exception("Error of format")
                        if fsn!=sn:
                                return render_to_response("info.html", {"title": _(u"失败"), "content": _(u"<h1>数据上传失败</h1><br />人员信息数据文件不是来自考勤机%(object_name)s")%{'object_name':sn} });
                        i, count = 0, len(upload_user) / 72        
                        if not (count>0 and count*72==len(upload_user)):
                                raise Exception()
                        i_insert, i_update, i_rep = 0, 0, 0
                        while i < count:
                                buf = upload_user[i*72:(i+1)*72]
                                pin= format_pin(getStr_c_decode(buf[48:]))
                                i += 1
                                pin_pin2[ord(buf[0])+ord(buf[1])*256] = pin
                                if pin not in settings.DISABLED_PINS :
                                        try:
                                                emp=Employee.objects.filter(PIN=pin)[0]
                                        except:
                                                sql = getSQL_insert("userinfo", BadgeNumber = pin, defaultdeptid = dept.DeptID, OffDuty=0, DelTag=0,
                                                        Name = getStr_c_decode(buf[11:35]), Password = getStr_c_decode(buf[3:11]),
                                                        AccGroup = ord(buf[39:40]), TimeZones = getStr_c_decode(buf[40:48]),
                                                        SN_id=sn)                                                                                
                                                checkAndRunSql(cursor, sqlList, sql)
                                                i_insert += 1
                                        else:
                                                ename=getStr_c_decode(buf[11:35]) 
                                                #Password = getStr_c_decode(buf[3:11]),
                                                #AccGroup = ord(buf[39:40]), TimeZones = getStr_c_decode(buf[40:48])
                                                if ename==emp.EName:
                                                        i_rep += 1
                                                else:
                                                        sql = getSQL_update("userinfo", whereBadgeNumber = pin, name = ename, SN_id=sn)
                                                        checkAndRunSql(cursor, sqlList, sql)
                                                        i_update += 1
                                        emps.append(pin)
                                else:
                                        errorRecs.append(u"PIN=%s"%pin)
                        checkAndRunSql(cursor, sqlList)
                        conn._commit()
                        result+=reportError(_(u"个人信息"), i, i_insert, i_update, i_rep, errorRecs)
                except:
                        errorLog(request)
                        return render_to_response("info.html", {"title": _(u"导入数据"), 
                                        "content": _(u"用户信息数据不匹配，请选择正确的用户信息数据文件") })
        
        if fs.has_key("file_fptemp"): # 指纹模版
                try:
                        errorRecs=[]
                        data = fs["file_fptemp"]["content"]
        #                typedef struct _Template_{                        //size:608
        #                        U16 Size;                                                //[:2]
        #                        U16 PIN;                                                //[2:4]        pin
        #                        BYTE FingerID;                                        //[4:5]        FingerID
        #                        BYTE Valid;                                                //[5:6]
        #                        BYTE Template[MAXTEMPLATESIZE]; //[6:]        Template        //maximize template length                                602
        #                }GCC_PACKED TTemplate, *PTemplate;                        
                        fsn,upload_fptemp,sum=checkRecData(data, 608)
                        if not fsn: raise Exception("Error of format")
                        if fsn!=sn:
                                return render_to_response("info.html", {"title": _(u"失败"), "content": _(u"<h1>数据上传失败</h1>,<br />人员指纹数据文件不是来自考勤机 %(object_name)s")%{'object_name':sn} });
                        i, count = 0, len(upload_fptemp) / 608
                        if not (count>0 and ord(upload_fptemp[6])==0xA1 and ord(upload_fptemp[7])==0xCA and count*608==len(upload_fptemp)):
                                raise Exception()        
                        if not pin_pin2:                                
                                return render_to_response("info.html", {"title": _(u"失败"), 
                                                "content": _(u"如果上传指纹模版，必须同时上传相关的用户信息文件") });
                        i_insert, i_update, i_rep = 0, 0, 0
                        while i < count:
                                buf = getFptemp_c(upload_fptemp[i*608:(i+1)*608])                                
                                i += 1
                                uid = pin_pin2[ord(buf[2])+ord(buf[3])*256]
                                if pin not in settings.DISABLED_PINS:
                                        try:
                                                fp=fptemp.objects.filter(UserID=uid, FingerID = ord(buf[4:5]))[0]
                                        except:
                                                sql = getSQL_insert("template", UserID=uid, Template = buf[6:].encode("base64"),
                                                        FingerID = ord(buf[4:5]), Valid = ord(buf[5:6]), SN = sn, DelTag=0)                                        
                                                checkAndRunSql(cursor, sqlList, sql)
                                                i_insert += 1
                                        else:
                                                fptmp=buf[6:]
                                                if fp.Template.decode("base64")==fptmp:
                                                        i_rep += 1
                                                else:
                                                        sql = getSQL_update("template", whereUserID=uid, Template = fptmp.encode("base64"),
                                                                whereFingerID = ord(buf[4:5]), Valid = ord(buf[5:6]), SN = sn, DelTag=0)                                        
                                                        checkAndRunSql(cursor, sqlList, sql)
                                                        i_update += 1
                                
                        checkAndRunSql(cursor, sqlList)
                        conn._commit()
                        result+=reportError(_(u"指纹模版"), i, i_insert, i_update, i_rep, errorRecs)
                except:
                        errorLog(request)
                        return render_to_response("info.html", {"title": _(u"导入数据"), 
                                        "content": _(u"<h1>数据上传成功</h1><br /><br />%(object_name)s<br /><h1>数据导入失败</h1><br /><br />指纹模版数据不匹配或者数据文件为空，请选择正确的<b>指纹模版</b>数据文件" )% {'object_name':result,}});
        
        if fs.has_key("file_transaction"): # 考勤记录
                try:
                        data = fs["file_transaction"]["content"]
                        fsn,upload_transaction,sum=checkALogData(data)
                        if not fsn: raise Exception("Error of format")
                        if fsn!=sn:
                                return render_to_response("info.html", {"title": _(u"失败"), "content": "<h1>"+_(u'上传数据失败')+"</h1>,<br />"+_(u'考勤记录数据文件不是来自考勤机')+u" %s"%(sn) });
                        arr = upload_transaction.split("\n")
                        count=len(arr)
                        i, i_insert = 0, 0
                        errorRecs=[]
                        maxtime=(datetime.datetime.now()+datetime.timedelta(1, 0, 0)).strftime("%Y-%m-%d %H:%M:%S")
                        for row in arr:
                                if row=="": continue
                                arr_row = row.split("\t")
                                i += 1
                                pin=arr_row[0].strip()
                                time=arr_row[1]
                                if (len(time) in [19,16]) and (maxtime>time) and (pin not in settings.DISABLED_PINS):
                                        pin=format_pin(pin)
                                        e=Employee.objByPIN(pin, device)
                                        sql = getSQL_insert("checkinout", userid=e.id, checktime=time, SN=sn,
                                                checktype=arr_row[3], verifycode =arr_row[2])
                                        checkAndRunSql(cursor, sqlList, sql)
                                        i_insert += 1
                                else:
                                        errorRecs.append(row)
                        checkAndRunSql(cursor, sqlList)
                        conn._commit()
                        result+=reportError(_(u"考勤记录"), i, i_insert, 0, 0, errorRecs)
                except:
                        errorLog(request)
                        return render_to_response("info.html", {"title": _(u"导入数据"), 
                                        "content": (u"<h1>%s"%_(u'数据导入结果'))+"</h1><br /><br />"+u"%s"%(result,)+(u"<br /><h1>%s"%_(u'数据导入失败'))+u"</h1><br /><br />%s"%_(u"选择正确的考勤记录数据文件")});
                                                
        return render_to_response("info.html", {"title": _(u"导入数据"), "content": u"<h1>%s</h1><br /><br />%s"%(_(u'数据导入结果'),result)});

def uploadData(request):
        if "udisk" not in settings.ENABLED_MOD:
                return render_to_response("info.html", {"title":  _(u"错误"), "content": _(u"该版本服务器程序没有安装U盘数据导入模块")});
        if request.method == "GET":
                return render_to_response("upload.html", {}, RequestContext(request, {}))
        elif request.method == "POST":
                adminLog(User=request.user, action="Import U-disk data files").save()
                return upload_data(request)
        
