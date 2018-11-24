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
import os
def get_auth(request):
    if request.user.is_authenticated():
        return NoAuthentication()
    else:
        return auth

    
class ExportGridHandler(BaseHandler):
    
    def read(self, request, data_key):
        return self.grid_data
    
def ExportGrid(request, grid_data, data_key=None):
    '''
    Grid导出
    '''
    format = request.REQUEST.get('format','.xls')
    if request.method=="GET" and format and (format not in ('.xls','.pdf','.csv')):
        resp = rc.BAD_REQUEST
        resp.write(u':不支持的输出格式')
        return resp
    from dbapp.modelutils import default_fields
    try:
        '''得到字段名集合'''
        #fields= grid.__fieldnames
        #exclude = ['id']
        allowed_methods = ('GET',)
        '''动态构造 Resource'''
        type_name = str("_%s_APIHandler"%(id(grid_data)))
        type_bases = (ExportGridHandler, )
        type_dict = {
            'allowed_methods':('GET',),
            #'fields': fields,
            #'exclude':exclude,
            'grid_data':grid_data[0:65000]
        }
        handler=type(type_name,type_bases,type_dict)
        return Resource(handler=handler)(request, data_key)
    except UnicodeError:
        from django.http import HttpResponse  
        import traceback;traceback.print_exc();      
        resp = rc.BAD_REQUEST
        resp.write(u':编码出错，请另作选择')
        return resp
    
    


from piston.emitters import HttpStatusCode, Mimer, Emitter

class ColumnEmitter(Emitter):
    head=False
    def render(self, request):
        seria = self.construct()
        title="table"
        heads="" 
        fields=self.data[0]#self.fields or (self.data and self.data[0].keys() or [])
        del self.data[0]
        del seria[0]
        self.cells=[tuple([a[f] or '' for f in fields if f in a.keys()]) for a in seria]
        
        self.head=heads
        report_name=request.REQUEST.get("reportname",'')                
        title=report_name and report_name or title  
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
        else: l.append(u"%s"%item)
    return u", ".join(l)

class CSVEmitter(ColumnEmitter):
    """
    CSV emitter, understands timestamps.
    """
    def render_data(self, request):
        filecode='gb18030'#request.REQUEST.get('filecode','gb18030')
        Emitter.register('.csv', CSVEmitter, 'applicatioin/download; charset=%s'%filecode)
        lines=[csv_format(a) for a in self.cells]
        return u"\r\n".join(lines).encode(filecode)
    
Emitter.register('.csv', CSVEmitter)

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
        Emitter.register('.txt', TXTEmitter, 'text/plain; charset=%s'%filecode)
        lines=[txt_format(a) for a in self.cells]
        return u"\r\n".join(lines).encode(filecode)
    
#Emitter.register('txt', TXTEmitter)

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
        
        wcells=[[len(item.encode("gb18030")) for item in line] for line in cells[:40]]
        wcs=map(max, zip(*wcells)) #计算每列的最大值
        chars_cnt=sum(wcs)
        page_size=get_page_size(chars_cnt)

        p=Report()
        p.set_page_size(page_size[1], page_size[2])
        allws=min(6, max(3.7, 2.85*(p.width-23)/chars_cnt)) #计算每个字符的最大可能宽度
        page_head=(Paragraph('', p.style_title), )
        grid_head=[Paragraph(col_text, p.style_grid_head) for col_text in heads]
        p.colwidths=[(allws*item or 20) for item in wcs]
        p.grid_head_height=20
        p.row_height=15
        p.print_report(cells, page_size[3], None, page_head, file_name=u"%s/%s"%(file_path, file_name))
        f="/"+tmp_url()+"report_file/"+file_name
        return HttpResponseRedirect(f.encode("utf-8"))
       


 
try:
    import report
    Emitter.register('.pdf', PDFEmitter, 'application/pdf; charset=utf-8')
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

Emitter.register('.xls', EXCELEmitter,"application/vnd.ms-excel; charset=utf-8")
