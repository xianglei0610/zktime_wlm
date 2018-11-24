# -*- coding: utf-8 -*-
#/*******
#1.能对当前模型进行集合运算(aggregate)，最后一条记录用来汇总
#Book.objects.all().aggregate(Avg('price'))

#2.能对当前模型所关联的多对多字段进行结合运算(annotate)，作为其中的一列
#Store.objects.annotate(min_price=Min('books__price'), max_price=Max('books__price'))

#3.能对当前模型中的字段进行分组小计，每一个组后面一条小计记录，如Max,Min,
# Employee.objects.annotate(num_attarea=Count("attarea")).values("PIN","num_attarea").annotate(max_pin=Max("PIN"))

#******/

from django.db.models import get_model
from django.db import models
import json
from dbapp.utils import getJSResponse
from django.db.models.loading import get_app
from django.conf import settings
from django.http import HttpResponse
from django.db.models import get_model
import datetime
from django.utils.translation import ugettext_lazy as _


def get_all_datasources(request):
    u'''返回所有报表数据源的json格式'''
    json_data={}
    for application in settings.INSTALLED_APPS:
        if application in settings.INVISIBLE_APPS: continue
        app_label=application.split(".")[-1]
        
        def get_app_dict(app_label):
            app=get_app(app_label)
            dict_data={
                "verbose_name":u"%(name)s"%{
                    'name':hasattr(app, "verbose_name") and app.verbose_name or app_label
                },
                "models":[]
            }
            return app,dict_data
        
        app,json_data[app_label]=get_app_dict(app_label)
        
        for e in dir(app):
            try:
                model=app.__getattribute__(e)
                if issubclass(model, models.Model) \
                        and (model._meta.app_label==app_label) \
                        and hasattr(model.Admin,"report_fields"):
                    app_menu=None
                    if hasattr(model.Admin,"app_menu"):
                        app_menu=model.Admin.app_menu
                    else:
                        app_menu=app_label
                        
                    if not json_data.has_key(app_menu):
                        menu_app,json_data[app_menu]=get_app_dict(app_menu)
                    json_data[app_menu]["models"].append([u"%s"%model._meta.verbose_name,model.__name__,model._meta.app_label])
            except:
                pass
            
        if len(json_data[app_label]["models"])==0:
            del json_data[app_label]
    return getJSResponse(json.dumps(json_data))


#@params mc类名
#@recursive_level 最多关联多少级，默认为2
#@return 返回json数据(不包含多对多的字段),
#必须要在模型的Admin下配置report_fields参数指定哪些自动可以用于报表设计
#例如:
#{
#   "m_name":"Template",
#   "m_verbose_name",u"指纹模板",
#   "fields":{
#       "FingerID":{
#            "f_name":"FingerID","f_verbose_name":u"手指","field_type":"SmallIntegerField",
#        },
#      "UserID":{
#            "m_name":"Employee","m_verbose_name":u"人员","field_type":"ForeignKey","rel_field_name":"id","f_verbose_name":"人员","f_name":"UserID","fields":{}
#       }
#   }
#}
def get_model_attributes(mc,recursive_level=1):
    #正向查找本模型字段，以及外键，多对多字段类型
    from dbapp import widgets
    field_types={
        models.CharField : "CharField",
        models.AutoField : "AutoField",
        models.BigIntegerField : "BigIntegerField",
        models.BooleanField : "BooleanField",
        models.DateField : "DateField",
        models.DateTimeField : "DateTimeField",
        models.DecimalField : "DecimalField",
        models.EmailField : "EmailField",
        models.FilePathField : "FilePathField",
        models.FloatField : "FloatField",
        models.ForeignKey : "ForeignKey",
        models.ManyToManyField :"ManyToManyField",
        models.IntegerField : "IntegerField",
        models.IPAddressField : "IPAddressField",
        #models.PhoneNumberField : "PhoneNumberField",
        models.SmallIntegerField : "SmallIntegerField",
        models.TextField : "TextField",
        models.TimeField : "TimeField",
    }
    dict={}
    dict.update({
        "app_label":mc._meta.app_label,
        "m_name":mc.__name__,
        "m_verbose_name":u"%s"%mc._meta.verbose_name,
    });
    #字段
    fields={}
    
    #判断模型是否配置了报表字段（不同的系统模型字段可能不一样，例如Employee模型中门禁字段就不能在考勤系统中出现）
    if not hasattr(mc.Admin,"report_fields"):
        return {}
    for f_name in mc.Admin.report_fields:
        try:
            e=mc._meta.get_field(f_name)
        except:
            continue
        
        field_type=[v for k,v in field_types.items() if isinstance(e,k)]#是否在规定的字段中
        if field_type:
            field_name=e.name
            fields[field_name]={
                "f_name":field_name,
                "f_verbose_name":u"%s"%e.verbose_name,
                "field_type":field_type[0],
            }
            #下拉列表属性
            choices=[]
            try:
                for k,v in e.choices:
                    choices.append([k,u"%s"%v])
            except:pass
            fields[field_name]["choices"]=choices 
            
            #默认值
            default_value=""
            try:
               default_value=e.get_default() or ""
            except:pass
            fields[field_name]["default"]=default_value
            
            #长度
            max_length=0
            try:
                max_length=e.max_length
            except:pass
            fields[field_name]["max_length"]=max_length
            
            #widget html
            widget=None
            default_widgets={}
            if hasattr(mc.Admin, "default_widgets"):
                default_widgets=mc.Admin.default_widgets
                if callable(default_widgets): default_widgets(mc)
            
            if field_name in default_widgets: 
                widget=default_widgets[field_name]
            elif e.__class__ in default_widgets:
                widget=default_widgets[e.__class__]
              
            if widget:
                    formfield = widgets.form_field(e, initial="", widget=widget)
            else:
                    formfield = widgets.form_field(e, initial="")
            if isinstance(e,models.ForeignKey):
                fields[field_name]["widget"]=""
            else:
                fields[field_name]["widget"]=formfield.widget.render(field_name,"",{})   
            
#            if widget:
#                fields[field_name]["widget"]=widget.render("","")
#            else:
#                fields[field_name]["widget"]=e.formfield().widget.render("","")
            
            if isinstance(e,models.ForeignKey):
                if e.rel.to!=mc:#自连接表
                    fields[field_name]["rel_field_name"]=e.rel.field_name
                    if recursive_level!=0:
                        recursive_level=recursive_level-1
                        fields[field_name].update(get_model_attributes(e.rel.to,recursive_level))
                else:#自连接字段暂时删除
                    del fields[field_name]
    
    dict["fields"]=fields
    return dict

#def get_all_fk_model_attrubutes(model_class, recursive_level=3):
#    u'''得到所有的外键模型，最深递归为recursive_level,默认为3'''
#    m_classes=[model_class,]
#    recursive_level=recursive_level-1
#    if recursive_level==0:
#        return m_classes
#    
#    for f in model_class._meta.fields:
#        if isinstance(f,models.fields.related.ForeignKey):
#            m_classes=m_classes+get_all_relate_model(f.rel.to,recursive_level)
#    
#    return m_classes


#@request 请求
#@app_label 应用
#@model_name 模型名称
def response_model_attributes(request, app_label, model_name):
    u"返回该模型的所有信息"
    model_class=get_model(app_label,model_name)
    json_data=json.dumps(get_model_attributes(model_class))
    return getJSResponse(json_data)
    
def save_report(req,key=None):
    u"保存报表"
    from mysite.report.models import Report
    from base.middleware.threadlocals import get_current_user
    import json
    
    r=None;
    if key:
        try:
            r=Report.objects.get(pk=key)
        except Exception,e:
            return HttpResponse("%s"%_(u"没有找到该记录!"))
    else:
        r=Report()
    str_dict=req.POST.get("g_report")
    dict_report=json.loads(str_dict)
    #dict_report=eval(u"%s"%str_dict)
    print dict_report
    r.name=dict_report["report_name"]
    #print 'str_dict',str_dict,'\n'
    r.user=get_current_user()
    r.json_data=u"%s"%str_dict
    if dict_report["report_type"]:
        r.report_type_id=dict_report["report_type"]
    try:
        r.save()
    except Exception,e:
        import traceback;traceback.print_exc();
        raise e
    return HttpResponse("success");
    
#新增报表
def new_report(request):
    u"保存报表"
    return save_report(request)

#编辑报表
def edit_report(request,key):
    return save_report(request,key)


def browse_report(request):
    key=request.REQUEST.get("K")
    return HttpResponse("hee")


def render_data(request,lines):
    import xlwt
    from django.http import HttpResponse,HttpResponseRedirect
    from mysite.urls import tmpDir, tmp_url
#    rn=request.REQUEST.get("reportname",'')
    title="sdfdf"
    sheet_name=u"%s"%datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#    
#    if self.head=="":
#        #print self.data[0]
#        heads=[k for k in self.data[0].keys()]
#    else:
#        heads=self.head
#    
#    lines=[xls_format(a) for a in self.cells]
#    lines.insert(0, xls_format(self.head))
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
            try:
                ws.write(row_index,col_index,col,style)
                ws.col(col_index).width=0x0d00+2000
                col_index+=1
            except Exception,e:
                import traceback;traceback.print_exc()
                
        row_index+=1
    filename="%(d1)s_%(d2)s.xls"%{
        "d1":u"%s"%title,
        "d2":datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    }
    
    response = HttpResponse(mimetype=u"application/vnd.ms-excel; charset=utf-8")
    response["Content-Disposition"] = u"attachment;filename="+filename+""
    wb.save(response)
    return response
#    wb.save(u"%s/%s"%(tmpDir(), filename))
#    f="/"+tmp_url()+filename
#    return HttpResponseRedirect(f.encode("utf-8"))

def download_report(request):
    from mysite.report.models import Report
    from dbapp.datautils import QueryData
    import json
    key=request.REQUEST.get("K")
    json_data = Report.objects.get(pk=key).json_data
    json_dict=json.loads(json_data)
    app_label,model_name=json_dict["sel_datasource"].split("__")
    MClass=get_model(app_label,model_name)
    qs=MClass.objects.all()
    qs, cl=QueryData(request, MClass, qs=qs)
    #分页
    
    stack=[]
    line_display=[]
    fields_attributes = json_dict["fields_attributes"]
    fields=json_dict["fields"]
    
    #得到所有的现实头
    for e in fields:
        for k,v in fields_attributes.items():
            if e==k:
                try:
                    line_display.append(u"%s"%v["display"])
                except Exception,e:
                    import traceback;traceback.print_exc();
                    raise e
                break
    
    stack.append(line_display)    
    #得到所有的记录
    for r in qs:
        line=[]
        for f in fields:
            level_f=f.split("__")
            value=r
            for ee in level_f:
                if hasattr(value,"get_%s_display"%ee):
                    value=getattr(value,"get_%s_display"%ee)()
                else:
                    value =getattr(value,ee)
            line.append(value)
        stack.append(line)
    return render_data(request,stack)
    #print 'stack',stack,'\n'
#    response = HttpResponse(mimetype='application/json; charset=utf-8')
#    response['Content-Disposition'] = 'attachment; filename='+file_name.split("/")[-1].split("_",2)[-1].split(".")[0]+"_backup.json"
#    f=open(file_name,"r")
#    for line in f.readlines():
#        response.write(line)
#    f.close()
#    return response
    
    #return HttpResponse("hee")