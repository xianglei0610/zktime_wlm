# -*- coding: utf-8 -*-
import datetime
from mysite.personnel.models.model_emp import format_pin
from mysite.sql_utils import p_execute ,p_mutiexec
from mysite.iclock.models.model_trans import normal_state ,normal_verify
import xlrd

def response_write(msg):
    from django.http import HttpResponse
    response = HttpResponse(mimetype='text/plain')
    response["Content-Type"]="text/html; charset=utf-8"
    response.write(u"%s"%msg)
    return response
def batch_insert(sql_list):
    if sql_list:
        flag,res = p_mutiexec(sql_list)
        if not flag:
           for elem in sql_list:
               p_execute(elem)

def val_datetime(val):
    dt = None
    if not val:
        dt = None
    elif isinstance(val,float):
        dt_tuple =  xlrd.xldate_as_tuple(val, 0)
        dt = datetime.datetime(*dt_tuple)
    elif isinstance(val,unicode):
        try:
            dt =  datetime.datetime.strptime(val,"%Y-%m-%d %H:%M:%S")
        except:
            dt =  None
    return dt

def move_file(sn,datalist):
    from base.sync_api import save_att_file
    save_att_file(sn,("\r\n").join(datalist))
               
def import_u_data_action(request):
    f=request.FILES.get('upload_attlog', None)
    sn = request.POST.get("dev_select",None)
    ret_res = ""
    ret =[]
    if not f:
        ret_res = u"请选择文件!" 
    elif not sn:
        ret_res = u"请选择设备!" 
    else:
        try:
            f_format=str(f).split('.')
            format_list=['dat']
            ret = []
            if str(f_format[-1]) not in format_list:
                return response_write(u"考勤文件格式无效！")
            try:
                file_data = f.read()
                file_data = file_data.strip()
            except Exception,e:
                return response_write (u"解析文件出错!")
            finally:
                f.close() 
            data_list=[]   
            log_list = file_data.split("\r\n")
            for i in range(0,len(log_list)):
                row = log_list[i]
                elems = row.split("\t")
                if len(elems) != 6:
                    ret.append(u"第%(r)s行:%(info)s"%{"r":i+1,"info":u"数据格式不正确;"})
                    continue
                pin = format_pin(elems[0].strip()) #用户PIN号
                ttime = elems[1].strip() #考勤时间
                sdevice_id = elems[2].strip() #设备号
                state  = elems[3].strip() #考勤状态
                verify = elems[4].strip() # 验证方式
                workcode = elems[5].strip() # 工作代码
                
                try:
                    ttime = datetime.datetime.strptime(ttime,"%Y-%m-%d %H:%M:%S")
                except:
                    ret.append(u"%(r)s:%(info)s"%{"r":row,"info":u"时间格式不正确;"})
                    continue
                data_list.append(u"%s\t%s\t%s\t%s"%(pin,ttime,state,verify))
            move_file(sn,data_list)
            ret.append(u"文件已经上传,后台正在处理!")         
        except Exception,e:
            ret.append(u"%s"%e)           
        if ret:
            ret_res = u"%s"%("\n".join(ret))
    ret_res = u"%s"%(len(ret_res)>30 and ret_res[:31]+"..." or ret_res)
    return  response_write(ret_res)


def import_self_data_action(request): 
    import time
    import datetime
    ret = [] # 导入过程中的错误信息
    ret_res = ""
    file = None #导入的文件对象            
    book = None 
    excel_head = []
    need_head = [u"人员编号",u"考勤时间",u"考勤状态"]
    file=request.FILES.get('import_data', None)
    a = time.time()
    if file:
        try:
            f_format=str(file).split('.')
            format_list=["xls",]
            if str(f_format[-1]) not in format_list:
                return response_write (u"导入文件格式无效，只支持 xls 文件导入！")
            try:
                book  = xlrd.open_workbook(file_contents=file.read())
            except Exception,e:
                return response_write (u"解析文件出错")
            finally:
                file.close()
            if book.nsheets !=1:
                return response_write(u"工作表(sheet)必须为一张")                
            sheet = book.sheet_by_index(0)
            n_rows =sheet.nrows
            n_cols = sheet.ncols
            if n_rows<2:
                return response_write(u"数据不能少于两条(标题和数据)") 
            excel_head = [i.strip() for i in sheet.row_values(0)]
            if len(excel_head)<3  or need_head <> excel_head[:3]:
                return response_write(u"请按照指定列格式导入文件!")  
            
            row_sql =[]
            SQLSERVER_INSERT = """
                if not exists(select id from checkinout where pin = '%(pin)s' and checktime= '%(time)s') 
                INSERT INTO checkinout(pin,checktime,checktype,verifycode)
                    VALUES('%(pin)s','%(time)s','%(type)s',%(vf)s)
            """
            for i in range(1,n_rows):
                b = time.time()
                row  =  sheet.row_values(i)
                pin = format_pin(row[0])
                atttime = val_datetime(row[1])
                state = row[2]
                verify = 5
                if not pin:
                    ret.append(u"第%d行 人员编号 有问题,不能导入"%(i+2))
                    continue
                if not atttime:
                    ret.append(u"第%d行 考勤时间 有问题,不能导入"%(i+2))
                    continue
                if not state:
                    ret.append(u"第%d行  考勤状态  有问题,不能导入"%(i+2))
                    continue
                row_sql.append(
                    SQLSERVER_INSERT%{
                        "pin":pin,
                        "time":atttime,
                        "type":state,
                        "vf":verify
                    }
                )
                if len(row_sql)>100:
                    batch_insert(row_sql)
                    sql = []
            if row_sql:
                batch_insert(row_sql)
                sql = []
        except Exception,e:
            import traceback; traceback.print_exc();
            ret.append(u"%s"%e) 
        if ret:
            ret_res = u"导入完成,导入结果:%s"%("\n".join(ret))
        else:
            ret_res = u"导入完成!"  
    else:
        ret_res = u"请选择要导入的文件"
    ret_res = "%s"%(len(ret_res)>30 and ret_res[:31]+"..." or ret_res)
    return  response_write(ret_res)