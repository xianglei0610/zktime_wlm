# -*- coding: utf-8 -*-
from django.template import Context, Template, loader, TemplateDoesNotExist
from traceback import print_exc
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

def dfind(dlist, dobj):
        for d in dlist:
                dl = dlist[d]
                if d == dobj: return dl
                if dl:
                        l = dfind(dl, dobj)
                        if l: return l
def format_a_ul(obj, children):
    if children:
        return u"<li id=%s><p class=t>%s</p>%s</li>" % (obj.pk, obj,
            "<ul>%s</ul>" % ("".join([format_a_ul(key, value) \
                for key, value in (lambda c: c.sort(lambda x, y: unicode(x[0]) > unicode(y[0])) or c)(children.items())])))
    else:
        return u"<li id=%s><p>%s</p></li>" % (obj.pk, obj)

def format_a_ul_cb(obj, children, data=[]):
        return u"<li id=%s><p%s>%s</p></li>" % (obj.pk, (obj.pk in data) and " class=s" or "", obj)

class TimeSliceTree:
    def update(self, depts):
        #print "depts:%s" % depts
        self.depts = list(depts)
        depts_dict = {}
        self.max_level = 0
        for d in self.depts:
#            if d.parent_id==d.id: #错误的父部门，尝试解除
#                d.parent_id=None 
#                try:
#                    d.save()
#                except: pass
            depts_dict[d['code']] = d
        self.depts_dict = depts_dict
    def __init__(self, depts):
        self.update(depts)
   
   

    def html_tree(self):
            tmp = u"""
<ul class="dtree">
{% for d in tree %}
<li>{% for i in d.0 %}<div class="{{ i }}"></div>{% endfor %}<div>{{ d.1 }}</div></li>{% endfor %}
</ul>
"""
            t = Template(tmp)
            c = Context({'tree':[(d[4], u"%s" % d[0]) for d in self.tree]})
            return t.render(c)
    def html(self, data=[],
            format="<li class='level_%(level)s %(folder_class)s%(selected_class)s' id='%(id)s'>%(repr)s</li>",
            folder_class='folder', leaf_class='leaf', selected_class='selected'):
            l = self.tree
            lines = []
            llen = len(l)
            for i in range(llen):
                    d = l[i]
                    level = len(d[1]) - 1
                    is_folder = (i < llen - 1) and (len(l[i + 1][1]) > level)
                    obj = d[0]
                    lines.append(format % {\
                            'level':level,
                            'folder_class':is_folder and folder_class or leaf_class,
                            'id': obj.pk,
                            'repr': obj,
                            'selected_class': (obj.pk in data) and (' ' + selected_class) or ""})
            return "\n".join(lines)

   
    def html_ul_li(self,depts):
        lines = []
        for d in self.depts:
            htm=u"<li id=%s><p>%s</p></li>" % (d['code'], d['name'])
            lines.append(htm)
        return "".join(lines)

import time

def exe_time(func):  
    def new_func(*args, **args2):
        t0 = time.time()  
        print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)  
        back = func(*args, **args2)  
        print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)  
        print "@%.3fs taken for {%s}" % (time.time() - t0, func.__name__)  
        return back  
    return new_func

@exe_time
def test_dtree():
    from mysite.pos.models.model_timeslice import TimeSlice
    return TimeSliceTree(TimeSlice.objects.all()[4989:])

from django import forms
from django.forms.util import flatatt


 
class ZtimeSliceChoiceWidget(forms.Select):
    flat = False
    def __init__(self, attrs={}, choices=()):
        super(ZtimeSliceChoiceWidget, self).__init__(attrs=attrs, choices=choices)
    def render(self, name, data, attrs=None):
        #from mysite.personnel.views import get_dept_tree_data
        from django.core.urlresolvers import reverse
      
        #print "ZDeptChoiceWidget_render data", data
       
        if data is not None:
            try:
                data = int(data)
            except:
                pass            
            if type(data) in (int, long):
                data = self.choices.queryset.model.objects.get(pk=data)
        if attrs: self.attrs.update(attrs)
        if 'id' not in self.attrs: self.attrs['id'] = 'id_' + name
        self.attrs['class'] = self.attrs['class'] + ' filetree r'
        self.attrs = self.build_attrs(self.attrs, name=name)
        required = ""
        if hasattr(self.choices.field, "required") and self.choices.field.required:
            required = "class='wZBaseCharField required input_showDeptTree'"
        try:
            from mysite.pos.models.model_batchtime import BatchTime
            from django.db.models import Count            
            dd = BatchTime.objects.filter(isvalid=1).query.group_by=['code']
            vdata = filterdata_by_user(BatchTime.objects.values('code','name').annotate(dcount=Count('code')).filter(isvalid=1),threadlocals.get_current_user())
           # vdata = filterdata_by_user(dd,threadlocals.get_current_user())
#            for ii in vdata:
#                if ii.parent_id is not None:
#                    l=[e for e in vdata if  e.id==ii.parent_id]
#                    if not l:ii.parent_id=None 
#<li id=24><p>晚餐</p></li><li id=25><p>夜宵</p></li><li id=22><p>早餐</p></li><li id=23><p>中餐</p></li>
            html = u"<div id='999' class='div_box1' style='padding-left: 30px;'>"\
                    "<p style='margin-right: 40px;'>%s&nbsp; %s &nbsp; &nbsp;</p></div>" % (_(u'开始时间'), _(u'结束时间'))
            html+=TimeSliceTree(vdata).html_ul_li(vdata)
            html_el = {"disp": data or "",
                "name": name,
                "value": data and data.pk or "",
                "attr": flatatt(self.attrs),
                "required":required, 
                "id": self.attrs['id'],
                "uid":"%s" % id(self),
                "none": _(u"撤销选择").capitalize(),
                "items": html,
                "ok":_(u"确定")}
            if self.flat == False:#平铺
                return ('<input %(required)s class="wZBaseCharField input_showq" type="text" readonly="readonly" value="%(disp)s"><input type=hidden name="%(name)s" value="%(value)s">' + \
                                u'<span class="btn_showDeptTree"><img onclick="render_dept_dropdown(this, false)" src="/media/img/sug_down_on.gif" id="id_drop_dept"><div  id="show_deptment" style="display: none;"><div class="title"><span class="span_selectNone Link_blue1" onclick="dept_tree_none(this)"><a href="javascript: void(0)">%(none)s</a>&nbsp;&nbsp;</span><span onclick="javascript:$(this).parent().parent().hide();" class="close btn">%(ok)s</span></div><div id="id_dept"><ul %(attr)s>%(items)s</ul></div></div></span>') % html_el            
            else:
                return u'<input type=hidden><input value="%(disp)s" type=hidden>%(value)s<div id="show_deptment"><div id=%(uid)s><ul %(attr)s>%(items)s</ul></div><script>render_dept_($("#%(uid)s"),false,true)</script></div>' % html_el
        except:
            print_exc()

class ZtimeSliceChoiceFlatWidget(ZtimeSliceChoiceWidget):
    flat=True

class ZTimeSliceMultiChoiceWidget(forms.SelectMultiple):
    flat=False
    def __init__(self, attrs={}, choices=()):
        super(ZTimeSliceMultiChoiceWidget, self).__init__(attrs=attrs, choices=choices)

    def render(self, name, data, attrs=None, choices=()):
        import time
        if data is not None:
            model=self.choices.queryset.model
            try:
                datapk = data
                data=[model.objects.get(pk=int(d)) for d in datapk]
            except:
                print_exc()
        if attrs: self.attrs.update(attrs)
        if 'id' not in self.attrs: self.attrs['id']='id_'+name
        self.attrs['class']=self.attrs['class']+' filetree'
        self.attrs = self.build_attrs(self.attrs, name=name)
        try:
            
            vdata =filterdata_by_user(self.choices.queryset.all().filter(isvalid=1),threadlocals.get_current_user())
#            for ii in vdata:
#                if ii.parent_id is not None:
#                    l=[e for e in vdata if  e.id==ii.parent_id]
#                    if not l:ii.parent_id=None
            html = u"<div id='999' class='div_box1' style='padding-left: 30px;'>"\
                    "<p style='margin-right: 40px;'>%s&nbsp; %s &nbsp; &nbsp;</p></div>" % (_(u'开始时间'), _(u'结束时间'))
            html+=TimeSliceTree(vdata).html_ul_li(data=data and datapk or [])
            html_el={\
                "disp": data and ",".join([u"%s"%d for d in data]) or "", 
                "name": name, 
                "value": data and "".join(['<input type=hidden name="%s" value="%s">'%(name, d.pk) for d in data]) or "",
                "attr": flatatt(self.attrs),
                "id": self.attrs['id'],
                'uid': "%s"%id(self),
                "items": html,
                "ok":_(u"确定"),
                "selectchildren":_(u"包含下级")}
            if self.flat: #平铺型
                return u'<input value="%(disp)s" type=hidspan_selectchildrenspan_selectchildrenden>%(value)s<div id="show_deptment"><div id="id_dept"><span id=%(uid)s></span><ul %(attr)s>%(items)s</ul></div><script>render_dept_tree("%(uid)s")</script></div>'%html_el
            else: #下拉框型
                return ('<input  id="dropTime" type="text" class="wZBaseCharField input_showDeptTree" readonly="readonly" value="%(disp)s">%(value)s'+\
                u'<span class="btn_showDeptTree" style="width:200px;"><img onclick="render_dept_dropdown(this, true)"  src="/media/img/sug_down_on.gif" id="id_drop_dept"><div id="show_deptment" style="display: none;""><div class="title"><span class="span_selectchildren displayN"></span><span onclick="javascript:$(this).parent().parent().hide();" class="close btn">%(ok)s</span></div><div id="id_dept"><ul %(attr)s>%(items)s</ul></div></div></span>')%html_el
        except:
            print_exc()

class ZDeptMultiChoiceDropDownWidget(ZTimeSliceMultiChoiceWidget):
    flat=False

