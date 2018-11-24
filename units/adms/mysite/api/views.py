#coding=utf-8
from piston.handler import BaseHandler
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication, NoAuthentication
from piston.doc import documentation_view
from piston.utils import rc
from django.db import models
from dbapp.datautils import QueryData, get_field_verbosename
import datetime
import sys
from mysite.urls import tmpDir, tmp_url
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context
import json
from django.conf import settings
auth = HttpBasicAuthentication(realm='ZK-ECO API')
from base.middleware import threadlocals
from base.models_logentry import LogEntry, EXPORT
from django.contrib.contenttypes.models import ContentType

#部门导出数据通过写SQL语句来实现
def get_eport_dict():
    u"为了能国际化，改为函数"
    try:
        t_sql=loader.get_template("export_sql_"+settings.DATABASE_ENGINE+".json")
        dict_export=json.loads(t_sql.render(Context({})).replace("\n","").replace("\t",""))
    except:
        dict_export={}
    return dict_export

def get_auth(request):
    if request.user.is_authenticated():
        return NoAuthentication()
    else:
        return auth

def get_data_use_sql(model,start_index,end_index,filter_params):
    u'''特殊处理模型特殊模型的导出，优化'''
    from django.db import connection as cnn
    from base.middleware.threadlocals import get_current_request
    from mysite.personnel.models.model_deptadmin import  DeptAdmin
    request=get_current_request()
    dict_export = get_eport_dict()
    sql_key=model._meta.app_label+"."+model.__name__
    if dict_export.has_key(sql_key):
        fields=dict_export[sql_key]["db_fields"]
        use_perms = dict_export[sql_key]["use_perms"]
        need_verbose_field=dict_export[sql_key]["verbose_fields"]
        cur=cnn.cursor()
        sql_add = ""
        #print dict_export[sql_key]["sql"]%(filter_params, start_index, end_index)
        dept_admin_ids =  DeptAdmin.objects.filter(user=request.user).values_list("dept_id",flat=True)
        try:
            if use_perms=="True":#使用按授权部门权限导出
                if not request.user.is_superuser :
                    if dept_admin_ids:#登录用户有按授权部门分配
                        sql_add = "and u.defaultdeptid in (select dept_id from deptadmin where user_id=%s)"%request.user.pk
                        sql=dict_export[sql_key]["sql"]%(sql_add,filter_params, start_index, end_index)
                    else:
                        sql=dict_export[sql_key]["sql"]%(sql_add,filter_params, start_index, end_index)
                    cur.execute(sql)
                else:
                    cur.execute(dict_export[sql_key]["admin_sql"]%(filter_params, start_index, end_index))
            else:
                cur.execute(dict_export[sql_key]["sql"]%(filter_params, start_index, end_index))
            records=cur.fetchall() or []
            cnn._commit()
        except:
            import traceback;traceback.print_exc()
            records=""
        ret=[]
        fields_len=len(fields)
        for elem in records:
            row={}
            for i in range(fields_len):
                e=elem[i]
                if need_verbose_field.has_key("%s"%i):
                    tmp_dict=dict(model._meta.get_field(need_verbose_field["%s"%i]).get_choices())
                    if tmp_dict.has_key(e):# and e:
                        row[fields[i]]=u"%s"%(tmp_dict[e])
                    else:
                        row[fields[i]]=e
                else:
                    row[fields[i]]=e
            ret.append(row)
        return ret
    else:
        return []

#根据查询条件用sql导出报表中，查询条件的解析，并转换为当前使用的数据库类型的查询条件表达式
def get_filterparams(request, dataModel):
    #获取该模型的所有字段
    from django.db.models.fields.related import ManyRelatedObjectsDescriptor as mrod, ReverseManyRelatedObjectsDescriptor as rmrod, ForeignRelatedObjectsDescriptor as frod
    model_fields=[f.name for  f in dataModel._meta.fields]
    for p,v in dataModel.__dict__.items() :
        if isinstance(v,mrod) or isinstance(v,frod) or isinstance(v,rmrod):
            if str(p).endswith("_set"):
                model_fields.append(str(p[:len(p)-4]))
            else:
                model_fields.append(p) 
 
    #剔除无效的查询字段及值
    params = dict(request.REQUEST.items())
    lookup_params = params.copy() 
    for k,v in lookup_params.items():#循环去掉不在当前模型中的字段(带":"的跳过)
        if k.__contains__(":"):#通过从表字段查询主表（当前表）-add by darcy 20100708
            kl = k.split(":")[1]
            lookup_params[kl] = v
            del lookup_params[k]
        else:#通过主表查询当前表（从表）
            if k.find("__")>0:
                ky = k.split("__")[0]
            else:
                ky = k 
            
            if ky not in model_fields:#如果该查询字段不在模型字段之列，则删除之
                del lookup_params[k]
#            else:    
#                ky_db_column = dataModel._meta.get_field(ky).db_column
#                if ky_db_column and ky != ky_db_column:#如果数据库表列名和模型字段名不一致，转换为数据库表列名
#                    ky_db_column = k.replace(ky,ky_db_column)
#                    lookup_params[ky_db_column] = lookup_params[k]
#                    del lookup_params[k]  
                

                   
    #把查询条件表达式，根据当前使用的数据库类型，转换成该数据库可识别的查询表达式         
    ret_filter_params = ''
    
    for k,v in lookup_params.items():
        filter_fileds = ''
        if not k.find("__")>0:
            ret_filter_params += " %s=%s and "%(k,v)
            continue
        else:
            
            kk=k.split("__")
            
            if len(kk)>2:
                try:
                    #print kk[1]
                    #print dataModel._meta.get_field(kk[0]).rel.to
#                    ret_filter_params += dataModel._meta.get_field(k.split("__")[0]).column + " in (" + loop_relate_sql(k.split("__"),dataModel,0,v) +")"
                    ret_filter_params += dataModel._meta.get_field(kk[0]).column + " in (" + loop_relate_sql(kk[1:],dataModel._meta.get_field(kk[0]).rel.to,0,v) +") and "
                except:
                    import traceback;traceback.print_exc()
            else:
                
                ret_filter_params += dataModel._meta.get_field(kk[0]).column
                if k.find("__exact") > 0:
                    ret_filter_params += " =%s and "%v
                    continue
                if k.find("__contains") > 0 or k.find("__icontains") > 0:
                    ret_filter_params += " LIKE '%%"+v+"%%' and "
                    continue
                if k.find("__gte") > 0:
                    ret_filter_params += " >= '%s' and "%v
                    continue
                if k.find("__gt") > 0:
                    ret_filter_params += " > '%s' and "%v
                    continue
                if k.find("__lt") > 0:
                    ret_filter_params += " < '%s' and "%v
                    continue
                if k.find("__lte") > 0:
                    ret_filter_params += " <= '%s' and "%v
                    continue
                if k.find("__ne") > 0:
                    ret_filter_params += " <> %s and "%v
                    continue
                if k.find("__in") > 0:
                    ret_filter_params += " in (%s) and "%(str(v)[1:-1])
                    continue
                if k.find("__isnull") > 0:
                    if v:
                        ret_filter_params += " is null and "
                    else:    
                        ret_filter_params += " is not null and "
                    continue        
    
    if ret_filter_params:#ret_filter_params必须判空，否则下面截取字符串会报错，另外where后为空，sql语法错误
        ret_filter_params = "where %s"%(ret_filter_params[:-4])
    return ret_filter_params
    
def loop_relate_sql(k,model,level,v):
    #print "k",k
    #print "model",model
    #print "level",level
    col=model._meta.get_field(k[level]).column
    table=model._meta.db_table
    id=model
    if level==len(k)-2:           
        ret_filter_params =col
        
        if str(k[level+1])=="exact":
            ret_filter_params += " ='%s'     "%v            
        if str(k[level+1])=="contains" or str(k[level+1])=="icontains":
            ret_filter_params += " LIKE '%%"+v+"%%'    "            
        if str(k[level+1])=="gte":
            ret_filter_params += " >= '%s'   "%v            
        if str(k[level+1])=="gt":
            ret_filter_params += " > '%s'    "%v            
        if str(k[level+1])=="lt":
            ret_filter_params += " < '%s'    "%v            
        if str(k[level+1])=="lte":
            ret_filter_params += " <= '%s'    "%v            
        if str(k[level+1])=="ne":
            ret_filter_params += " <> %s    "%v            
        if str(k[level+1])=="in":
            ret_filter_params += " in (%s)   "%(str(v)[1:-1])            
        if str(k[level+1])=="isnull":
            if v:
                ret_filter_params += " is null    "
            else:    
                ret_filter_params += " is not null    "
        return " select "+ model._meta.pk.column +" from "+ table +" where " + ret_filter_params
    else:
        return " select " + model._meta.pk.column +" from  "+ table + " where " + col + " in (" + loop_relate_sql(k,model._meta.get_field(k[level]).rel.to,level+1,v) + ")"
    

class APIHandler(BaseHandler):
    def read(self, request, data_key):
        if data_key is None:
            if hasattr(self,'qs') and self.qs!=None:return self.qs
            recordtype=int(request.GET.get('t', '1'))
            filter_params = get_filterparams(request, self.model)
            if recordtype==1:
                ret=get_data_use_sql(self.model,0,10000,filter_params)
                if ret:
#                    print "----use sql"
                    return ret
                qs, cl=QueryData(request, self.model)
                if qs.count()>10000:  
                    return qs[:10000]
                return qs[:]
            elif recordtype==2:
                l=int(request.GET.get('l', '15'))
                p1=int(request.GET.get('p1', '1'))
                p2=int(request.GET.get('p2', '1'))
                if p1<=0:
                    p1=1
                if p2<=0:
                    p2=1
                ret=get_data_use_sql(self.model,(p1-1)*l,p2*l,filter_params)
                if ret:
                    return ret
                qs, cl=QueryData(request, self.model)
                return qs[(p1-1)*l:p2*l]
            else:
                s1=int(request.GET.get('s1', '1'))
                s2=int(request.GET.get('s2', '1'))          
                if s1<=0:
                    s1=1
                if s2<=0:
                    s2=1      
                ret=get_data_use_sql(self.model,s1-1,s1+s2-1,filter_params)
                if ret:
                    return ret
                qs, cl=QueryData(request, self.model)
                return qs[s1-1:s1+s2-1]
        return self.model.objects.get(pk=data_key)
    
    def delete(self, request, data_key=None):
        if data_key is None:
            qs, cl=QueryData(request, self.model)
            qs.delete()
        else:
            obj = self.model.objects.get(kp=data_key)
            obj.delete()
            
    def update(self, request, data_key=None):
        if data_key is None:
            qs, cl=QueryData(request, self.model)
            qs.update(**dict(request.POST))
        else:
            obj = self.model.objects.get(kp=data_key)
            for p in request.POST: 
                setattr(obj, p, request.POST[p])
            obj.save()

def api(request, app_label, model_name, data_key=None):
    model=models.get_model(app_label,model_name)
    return api_for_model(request,model,data_key)
    
def api_for_model(request, model, data_key=None,query_set=None):
    from dbapp.modelutils import default_fields
    try:
        fields=request.GET.get("fields", "")
        if fields:
            fields=fields.split(",")
        if len(fields)==0:
            fields=None
            if hasattr(model,'Admin'):                
                if model.Admin:
                    
                    if hasattr(model.Admin,'api_fields'): 
                        fields=model.Admin.api_fields
                    elif hasattr(model.Admin, "list_display"):
                        fields=model.Admin.list_display
            if not fields:
                #fields=[isinstance(f, models.ForeignKey) and f.name+"_id" or f.name for f in model._meta.fields]
                fields=[isinstance(f, models.ForeignKey) and f.name+"_id" or f.name for f in model._meta.fields if f.name not in default_fields]
        else:
            of=fields
            if hasattr(model.Admin,'api_fields'): 
                of=model.Admin.api_fields            
            f=[i for i in fields if i.split("|")[0] in of]
            fields=f
#        print "export fields:%s"%fields
        #fields=[f.replace(".","__") for f in fields]
        
        dict_data={
            'model':model,
            'fields': fields,
            'qs':query_set,
        }
        
        try:
            dict_export = get_eport_dict()
            sql_key=model._meta.app_label+"."+model.__name__
            if dict_export.has_key(sql_key):
                dict_data["fields"]=dict_export[sql_key]["db_fields"]
                request.special_head=dict_export[sql_key]["head"]
        except:
            pass
        

        handler=type(str("_%s_%s_APIHandler"%(id(model.Admin), model.__name__)), (APIHandler, ), dict_data
        )
        #print "----",str("_%s_%s_APIHandler"%(id(model.Admin), model.__name__))
        #导出日志
        try:
             
            op = threadlocals.get_current_user()
            LogEntry.objects.log_action(
                    user_id=op and op.pk or None,
                    content_type_id=ContentType.objects.get_for_model(model).pk,
                    object_id="",
                    object_repr="",
                    action_flag=EXPORT
                )
        except :
            pass#解决在非管理员不能导出报表。重复插入日志报错
        return Resource(handler=handler, authentication=get_auth(request))(request, data_key)
    except UnicodeError:
        from django.http import HttpResponse  
        import traceback;traceback.print_exc();      
        return HttpResponse(u"%s"%_(u'导出的内容与选择的编码不符'))
    
def api_list(request,tmp_name):   
    from dbapp.utils import load_tmp_file
    from dbapp.models import create_model
    from dbapp.datalist import QSList 
    try:
        attrs, admin_attrs, data=load_tmp_file(tmp_name)
    except:
        raise Exception(u"%s"%_(u'导出超时，临时数据已经不存在!'))
    
    #print "attrs:%s"%attrs
    #print "admin_attrs:%s"%admin_attrs
    meta_attrs={}
    rn=request.REQUEST.get('reporttitle','')
    if rn:
        meta_attrs['verbose_name']=rn
    if len(data)>60001:  
        data =  data[:60001]
    model=create_model(tmp_name.encode("utf-8"),meta_attrs=meta_attrs, base_model=models.Model, attrs=attrs, admin_attrs=admin_attrs)
    return api_for_model(request,model,data_key=None,query_set=QSList(model,data))
    
class APIListHandler(BaseHandler):
    allowed_methods = ('GET', )
    def read(self, request,data):        
        return data
    
class APICountHandler(BaseHandler):
    allowed_methods = ('GET', )
    def read(self, request):
        qs, cl=QueryData(request, self.model)
        return {'count': len(qs)}

def api_count(request, app_label, model_name):
    model=models.get_model(app_label,model_name)
    handler=type(str("_%s_%s_APICounter"%(app_label, model_name)), (APICountHandler, ), { 'model':  model })
    return Resource(handler=handler, authentication=get_auth(request))(request)


from piston.emitters import HttpStatusCode, Mimer, Emitter

class ColumnEmitter(Emitter):
    head=False
    def render(self, request):
        from django.db.models.query import QuerySet
        seria = self.construct()
        title="table"
        heads="" 

        if isinstance(self.data, QuerySet):

            model = self.data.model
            fields=[('|' in f) and f.split("|")[0] or f for f in self.fields]
            heads=[get_field_verbosename(model, f, ".") for f in fields]
            title=model._meta.verbose_name
            self.cells = []
            for a in seria:
                cells_list = []
                for f in fields:
                    if f in a:
                        f_check = '.' in f and f.split('.')[0] or f
                        field=""
                        try:                            
                            field = model._meta.get_field(f_check)
                        except :
                            pass
                        if field:                                
                            if isinstance(field, models.fields.related.ManyToManyField):
                                m2m_field_display = hasattr(model,'Admin') and model.Admin.api_m2m_display[f] or ""#m2m要显示字段,多对多字段要导出必须在api_fields中配置要显示的字段（一个或多个，多个时用“ ”隔开显示）
                                m2m_field_verbose = []
                                for record in a[f]:
                                    d_list = []
                                    for d in m2m_field_display.split('.'):
                                        d_list.append(record[d])
                                    m2m_field_verbose.append(' '.join(d_list))
                                cells_list.append(','.join(m2m_field_verbose))
                            elif type(a[f])==dict and isinstance(field,models.fields.related.ForeignKey):
                                if u"%s"%a[f]['id']=='None':
                                    cells_list.append('')
                                else:
                                    if hasattr(field.rel.to,"export_unicode"):
                                        instance=field.rel.to.objects.get(id=a[f]['id'])
                                        if instance:
                                            cells_list.append(instance.export_unicode())
                                    else:
                                        cells_list.append(a[f])
                            else:                                
                                if a[f]==None:
                                    cells_list.append('')
                                else:
                                    if type(a[f])==dict and  u"%s"%(a[f]['verbose'])=='None':
                                        cells_list.append('')
                                    else:
                                        cells_list.append(a[f])
                                
                        else:
                            if a[f]==None :
                                cells_list.append('')
                            else:
                               if type(a[f])==dict and  u"%s"%(a[f]['verbose'])=='None':
                                  cells_list.append('')
                               else:
                                  cells_list.append(a[f])

                            
                    
                self.cells.append(tuple(cells_list))
            
        else:
            try:
                from django.db.models.loading import AppCache 
                http_app=request.META["HTTP_REFERER"].split("/")[-3]
                http_model=request.META["HTTP_REFERER"].split("/")[-2]
                modelname = AppCache().app_models.get(http_app).get(http_model.lower())
                title = modelname._meta.verbose_name
            except:
                title="table"
            
            fields=self.fields or (self.data and self.data[0].keys() or [])
            self.cells=[tuple([a[f] or '' for f in fields if f in a]) for a in seria]
        
        self.head=heads
        if hasattr(request,"special_head"):
            self.head=request.special_head
        rn=request.REQUEST.get("reportname",'')                
        title=rn and rn or title  
        #print "---rn=%s---title=%s"%(rn,title)     
        self.title=title
        self.file_name="%s_%s"%(title, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        return self.render_data(request)

def csv_format(a):
    l=[]
    for item in a:
        t = type(item)
        if t==type(0): l.append("%s"%item)
        elif t == datetime.datetime: l.append("%s"%(item.strftime("%Y-%m-%d %H:%M:%S")))
        elif t == type({}): l.append("%s"%item['verbose'])
        elif t == str or t==unicode:item = l.append(u"%s"%item.replace(",",";")) 
        else:l.append(u"%s"%item)
    return u", ".join(l)

class CSVEmitter(ColumnEmitter):
    """
    CSV emitter, understands timestamps.
    """
    def render_data(self, request):
        filecode='gb18030'#request.REQUEST.get('filecode','gb18030')
        Emitter.register('csv', CSVEmitter, 'applicatioin/download; charset=%s'%filecode)
        lines=[csv_format(a) for a in self.cells]
        lines.insert(0, csv_format(self.head))
        return u"\r\n".join(lines).encode(filecode)
    
Emitter.register('csv', CSVEmitter)

def txt_format(a):
    l=[]
    for item in a:
        t = type(item)
        if t == type({}): 
            l.append(item['verbose'])
        else:
            if t == datetime.datetime: 
                p="%s"%(item.strftime("%Y-%m-%dT%H:%M:%S"))
            elif item is not None: 
                p=u"%s"%item
                p=p.replace("\t","\\t").replace("\r", "\\r").replace("\n","\\n")
            else:
                p=""
            l.append(p)
    return u"\t".join(l)

class TXTEmitter(ColumnEmitter):
    """
    TXT emitter
    """
    def render_data(self, request):
        filecode=request.REQUEST.get('filecode','gb18030')
        Emitter.register('txt', TXTEmitter, 'text/plain; charset=%s'%filecode)
        lines=[txt_format(a) for a in self.cells]
        #print "self.head:%s"%self.head
        #print "META", request.META
        lines.insert(0, txt_format(self.head))
        
        return u"\r\n".join(lines).encode(filecode)
    
Emitter.register('txt', TXTEmitter)

def cell_format(a):
    l=[]
    for item in a:
        t = type(item)
        if t == datetime.datetime: 
            l.append(u"%s"%(item.strftime("%Y-%m-%d %H:%M:%S")))
        elif t == type({}): 
            l.append(u"%s"%item["verbose"])
        else: 
            l.append(u"%s"%(item or ""))
    return tuple(l)

def get_page_size(c):
    #(最大字符数，纸张尺寸名称，是否横向打印，每页行数)
    default_page_sizes=((130, 'A4', False, 41), 
        (200, "A4", True, 25),
        (300, "A3", True, 41),
    ) 
    for s in default_page_sizes:
        if s[0]>c: return s
    return default_page_sizes[-1] 
   
class PDFEmitter(ColumnEmitter):
    """
    TXT emitter
    """
    def render_data(self, request):
        from report import Report, Paragraph, Spacer, Table
        from django.http import HttpResponseRedirect
        from mysite.urls import tmpDir, tmp_url
        import os
        cells=[cell_format(a) for a in self.cells]
        rn=request.REQUEST.get("reportname",'')
        
        file_path = tmpDir() + "/report_file"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        title=rn and rn or self.title
        if self.head=="":
            #print self.data[0]
            heads=[k for k in self.data[0].keys()]
        else:
            heads=self.head
        file_name=u"%s_%s.pdf"%(title, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        filecode=request.REQUEST.get("fielcode",'gb18030')
        
        whs=colwidths = [len(i.encode(filecode)) for i in heads]
        wcells=[[len(item.encode("gb18030")) for item in line] for line in cells[:40]]
        wcells.insert(0, whs)
        wcs=map(max, zip(*wcells)) #计算每列的最大值
        chars_cnt=sum(wcs)
        page_size=get_page_size(chars_cnt)

        p=Report()
        p.set_page_size(page_size[1], page_size[2])
        allws=min(6, max(3.7, 2.85*(p.width-23)/chars_cnt)) #计算每个字符的最大可能宽度
        page_head=(Paragraph(title, p.style_title), )
        grid_head=[Paragraph(col_text, p.style_grid_head) for col_text in heads]
        p.colwidths=[(allws*item or 20) for item in wcs]
        p.grid_head_height=20
        p.row_height=15
        p.print_report(cells, page_size[3], grid_head, page_head, file_name=u"%s/%s"%(file_path, file_name))
        f="/"+tmp_url()+"report_file/"+file_name
        return HttpResponseRedirect(f.encode("utf-8"))
       


 
try:
    import report
    Emitter.register('pdf', PDFEmitter, 'application/pdf; charset=utf-8')
except:
    import traceback; traceback.print_exc()

        
def xls_format(a):
    l=[]
    for item in a:
        t = type(item)
        if t==type(0): l.append("%s"%item)
        elif t == datetime.datetime: l.append("%s"%(item.strftime("%Y-%m-%d %H:%M:%S")))
        elif t == type({}): l.append("%s"%item['verbose'])
        else: l.append(u"%s"%(item or ""))
    return l

class EXCELEmitter(ColumnEmitter):
    """
    Excel emitter
    """
    def render_data(self, request):
        import xlwt
        from django.http import HttpResponse,HttpResponseRedirect
        from mysite.urls import tmpDir, tmp_url
        import os
        rn=request.REQUEST.get("reportname",'')
        title=rn and rn or self.title
        sheet_name=u"%s_%s"%('Sheet', datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        
        file_path = tmpDir() + "/report_file"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        if self.head=="":
            #print self.data[0]
            heads=[k for k in self.data[0].keys()]
        else:
            heads=self.head
        
        lines=[xls_format(a) for a in self.cells]
        lines.insert(0, xls_format(self.head))
        filecode=request.REQUEST.get('filecode','gb18030')#编码
        
        wb = xlwt.Workbook(encoding=u"%s"%filecode)
        ws = wb.add_sheet(sheet_name)
        
        fnt = xlwt.Font()
        fnt.name = 'Arial'
        #fnt.colour_index = 4
        #fnt.bold = True
        
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        
        align = xlwt.Alignment()
        align.horz = xlwt.Alignment.HORZ_CENTER
        align.vert = xlwt.Alignment.VERT_CENTER
        
        style = xlwt.XFStyle()
        style.font = fnt
        style.borders = borders
        style.alignment = align
        
        row_index=0
        for row in lines:
            col_index=0
            for col in row:
                ws.write(row_index,col_index,col,style)
                ws.col(col_index).width=0x0d00+2000
                col_index+=1
            row_index+=1
        filename="%(d1)s_%(d2)s.xls"%{
            "d1":u"%s"%title,
            "d2":datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        }
        
#        response = HttpResponse(mimetype=u"application/vnd.ms-excel; charset=utf-8")
#        response["Content-Disposition"] = u"attachment;"
#         filename=%(d1)s_%(d2)s.xls"%{
#            "d1":title,
#            "d2":datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#        }
#       wb.save(response)
#       return response
        wb.save(u"%s/%s"%(file_path, filename))
        f="/"+tmp_url()+"report_file/"+filename
        return HttpResponseRedirect(f.encode("utf-8"))

Emitter.register('xls', EXCELEmitter,"application/vnd.ms-excel; charset=utf-8")
