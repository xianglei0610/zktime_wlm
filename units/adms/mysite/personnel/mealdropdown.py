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
    if children:
        return u"<li id=%s><p class='t%s'>%s</p>%s</li>" % (obj.pk, (obj.pk in data) and ' s' or '', obj,
            "<ul>%s</ul>" % ("".join([format_a_ul_cb(key, value, data) \
                for key, value in (lambda c: c.sort(lambda x, y: unicode(x[0]) > unicode(y[0])) or c)(children.items())])))
    else:
        return u"<li id=%s><p%s>%s</p></li>" % (obj.pk, (obj.pk in data) and " class=s" or "", obj)

class mealdropdown:
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
            depts_dict[d.pk] = d
        self.depts_dict = depts_dict
        self.tree = self.create_dtree2()
    def __init__(self, depts):
        self.update(depts)
    def search_did(self, did):
        return self.depts_dict[did]

    def parent(self, dobj):
        if dobj.parent_id:
            return self.depts_dict[dobj.parent_id]
    def get_parents(self, dobj):
        return dict(self.tree)[dobj]
    def index(self, dobj):
        i = 0
        for d in self.tree:
            if d[0] == dobj:
                return i
            i += 1
    def get_children(self, dobj, include_me=True):
            tree = self.tree
            i = self.index(dobj)
            if i == None:
                    level = 0
                    i = 0
            else:
                    level = tree[i][2]
            c = []
            if include_me:
                    c = [dobj]
            i += 1
            for j in range(len(tree) - i):
                    if tree[i][2] <= level: break
                    c.append(tree[i][0])
                    i += 1
            return c
    def get_children_folder(self, dobj, include_me=True):
            tree = self.tree
            i = self.index(dobj)
            if i == None:
                    level = 0
                    i = 0
            else:
                    level = tree[i][2]
            c = []
            if tree[i][3] and include_me:
                    c.append(tree[i][0])
            i += 1
            for j in range(len(tree) - i - 1):
                    if tree[i][2] <= level: break
                    if tree[i][3]:
                            c.append(tree[i][0])
                    i += 1
            return c
    def get_children_q(self, dobj):
            from django.db.models import Q
            c = self.get_children(dobj)
            if len(c) > 2000:
                    cf = self.get_children_folder(dobj)
                    #print "cf", cf
                    if len(cf) < 1000:
                            return Q(parent__in=cf) | Q(pk=dobj.pk)
            return Q(pk__in=[d.pk for d in c])

    def dappend(self, dlist, dobj):
        if dobj in dlist: 
            return dlist[dobj]
        if dobj.parent_id:
            if dobj.parent_id in self.depts_dict:
                p = self.depts_dict[dobj.parent_id]
                pl = dfind(dlist, p)
                if pl is None:
                    pl = self.dappend(dlist, p)
            else:
                pl = {dobj:None}
        else:
            pl = dlist[None]
        pl[dobj] = {}
        return pl[dobj]

    def create_dtree(self):
            dlist = {None:{}}
            for d in self.depts:
                    self.dappend(dlist, d)
            return dlist
    def print_dtree(self):
            dlist = self.create_dtree()
            print_dtree_(dlist)

    def formatd(self, l, dobj):
            fc = (u"%s" % dobj,)
            l[dobj] = fc
            return fc

    def create_dtree2(self):
            l = {}
            for d in self.depts:
                    self.formatd(l, d)
            l = l.items()
            l.sort(lambda x, y: cmp(x[1], y[1]))
            ll = []
            llen = len(l)
            for i in range(llen):
                    d = l[i]
                    level = len(d[1]) - 1
                    is_folder = (i < llen - 1) and (len(l[i + 1][1]) - 1 > level)
                    ll.append((d[0], d[1], level, is_folder, [' ', ]*level))
                    d[0].tree_level = level
                    d[0].tree_folder = is_folder
                    if level > self.max_level: self.max_level = level
            ml = 1000
            s = []
            for i in range(llen):
                    j = llen - i - 1
                    d = ll[j]
                    level = d[2]
                    prefix = d[4]
                    if level == 0: 
                            d[0].tree_prefix = []
                            continue
                    if (level not in s) and not (level == ml):
                            prefix[-1] = 'L'
#                        elif d[3]:                                # next is brother
#                                prefix[-1]='+'
                    else:                                # next is brother
                            prefix[-1] = 'l'
                    if level < ml:
                            if level not in s: s.append(level)
                            if ml in s: s.remove(ml)
                    if level > ml:
                            if level not in s: s.append(level)

                    #print level, ml, s
                    for k in range(len(s) - 1):
                            prefix[s[k] - 1] = 'l'
                    ll[j] = (d[0], d[1], d[2], d[3], prefix)
                    d[0].tree_prefix = prefix
                    ml = level
            return ll

    def print_dtree2(self):
            print self.html()

    def print_tree(self):
            for i in self.tree: print i[4] and "\t" + ("\t".join(i[4])) or "", "- %s" % i[0]

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

    def html_ul_li_(self, tree, pre=""):
        llen = len(tree)
        last_obj = None
        result = {}
        i = 0
        while i < llen:
            d = tree[i]
            obj = d[0]
            level = len(d[1])
            if not result:
                result[obj] = {}
                start_level = level
                #print pre+"start a node", obj, level, start_level
            else:
                if level > start_level:
                    #print pre+"start a tree", obj, level, start_level
                    ret, ll = self.html_ul_li_(tree[i:], pre + "\t")
                    i += ll - 1
                    result[last_obj] = ret
                    #start_level=level
                elif level == start_level:
                    result[obj] = {}
                    #print pre+"new a node", obj, level, start_level
                else: #level<last_level
                    #print pre+"end a tree", obj, level, start_level
                    break
            last_obj = obj
            last_level = level
            i += 1
            #print i
        return result, i 
    def html_ul_li(self, data=[]):
        lines = []
        t = self.html_ul_li_(self.tree)[0]
        for i, v in t.items():
            lines.append(format_a_ul_cb(i, v, data))
        return "".join(lines)

    def html_MultiChoice(self, data=[],
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
                                    'selected': obj.pk in [o.dept_id for o in data] and ' checked=checked ' or ""})
                                    
                    return "\n".join(lines)
    def html_jtree(self, data, root_id=None, next_level=1, include_root=False):
        l = self.tree
        if root_id is None:
            include_root = True
        lines = ["["]
        llen = len(l)
        root_level = 0         #根节点的部门级别
        low_level = next_level  #最大返回的部门级别
        left_level = -1
        for i in range(llen):
            d = l[i]
            obj = d[0]
            level = len(d[1])
            if root_id is not None: #指定了根节点
                if root_id == obj.pk:  #找到了根节点
                    root_level = level
                    low_level = root_level + next_level
                    left_level = root_level
                    #print "find root: root_level=%s, low_level=%s"%(root_level, low_level)
                elif root_level <= 0:   #还没有找到了根节点
                    continue         #继续找
                elif level <= root_level: #已经到了下一个与根节点平级或上级的节点，退出
#                    print "level(%s) <= root_level(%s), return"%(level, root_level)
                    break;
            if level <= low_level:   
#                print d
                is_folder = (i < llen - 1) and (len(l[i + 1][1]) > level)
                is_end = (i >= llen - 1) or (len(l[i + 1][1]) <= root_level) #整个部门树的最后一个部门
                is_last = is_end or (level > len(l[i + 1][1]))           #当前级别部门的最后一个
                if (not include_root) and (root_id == obj.pk): continue
                cls = ''
                if obj.pk in data: 
                    cls = ', classes: "selected"'
                    if is_folder:
                        cls = ', classes: "selected folder"'
                elif is_folder:
                    cls = ', classes: "folder"'
                if not is_folder:  #叶子节点
                    row = u'{id: %d, text: "%s"%s}' % (obj.pk, obj, cls)
                elif level == low_level: #已经是最大返回级别的部门了，仅仅标示有子节点，不展开子节点的具体项
                    row = u'{id: %d, text: "%s"%s, hasChildren: true}' % (obj.pk, obj, cls)
                else:
                    row = u'{id: %d, text: "%s"%s, expanded: true, children: [' % (obj.pk, obj, cls)
                    left_level = level
#                    print "start children: left_level=%s"%left_level
                if is_last:
#                    print "is_last, %sleft_level=%s, level=%s"%(is_end and "is_end, " or "", left_level,  level)
                    if is_end:
                        row += "]}" * (level - root_level - (include_root and 0 or 1))
                    else:
                        row += "]}" * (level - left_level) + ","
                elif not is_folder or level == low_level:
                    row += ","
#                print "\trow:", row
                lines.append(row)
        if len(lines) > 1:
            return "\n".join(lines) + "\n]"
        else:
            return "[]"


        
def print_dtree_(dlist, ident=""):
        for d in dlist:
                print "%s%s" % (ident, d)
                dl = dlist[d]
                if dl:
                        print_dtree(dl, ident + "| ")

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
    from mysite.personnel.models.model_meal import Meal
    return mealdropdown(Meal.objects.all()[4989:])

from django import forms
from django.forms.util import flatatt

#def dept_treeview():
#    from mysite.pos.models.model_splittime import SplitTime
#    vdata = filterdata_by_user(SplitTime.objects.filter(isvalid=1), threadlocals.get_current_user())
#    for ii in vdata:
#        if ii.parent_id is not None:
#            l = [e for e in vdata if  e.id == ii.parent_id]
#            if not l:ii.parent_id = None 
#    return mealdropdown(vdata).html_ul_li()

 
class ZMealChoiceWidget(forms.Select):
    flat = False
    def __init__(self, attrs={}, choices=()):
        super(ZMealChoiceWidget, self).__init__(attrs=attrs, choices=choices)
    def render(self, name, data, attrs=None):
        from dbapp.urls import surl
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
            btn_cancel = ""
            vdata = filterdata_by_user(self.choices.queryset.all().filter(available=1), threadlocals.get_current_user())
            if not required:
                btn_cancel='''<span class="span_selectNone Link_blue1" onclick="clear_none(this)">
                               <a href="javascript: void(0)">%(none)s</a>&nbsp;&nbsp;
                            </span>
                           '''%{"none":(u"%s"%_(u"撤销选择")).capitalize()}
            html = u"<div id='999' class='title' style='margin-left: 0px;'>"\
                               "<p style='margin-right: 110px;'>%s&nbsp;&nbsp;&nbsp; &nbsp;%s &nbsp; &nbsp;</p></div>" % (_(u'开始时间'), _(u'结束时间'))
            
            html+=mealdropdown(vdata).html_ul_li(data and [data.pk] or [])
            need_async_nodes=[]
            html_el = {"disp": data or "",
                "name": name,
                "value": data and data.pk or "",
                "attr": flatatt(self.attrs),
                "required":required,
                "id": self.attrs['id'],
                "uid":"%s" % id(self),
                "none": btn_cancel,
                "items": html,
                "ok":_(u"确定"),
                "need_async_nodes":",".join(need_async_nodes),
                "surl":surl,
                }
            if self.flat == False:#平铺
                return u'''<input %(required)s id="dropMeal" class="wZBaseCharField input_showDeptTree" type="text" readonly="readonly" value="%(disp)s"/><input type=hidden name="%(name)s" value="%(value)s"/>
                       <span class="btn_showDeptTree">
                           <img onclick="javascript:$(this).parent().find('#show_deptment').show();" src="/media/img/sug_down_on.gif" id="id_drop_dept"/>
                           <div  id="show_deptment" style="display: none;">
                               <div class="title">
                                   %(none)s
                                   <span onclick="javascript:$(this).parent().parent().hide();" class="close btn">%(ok)s</span>
                               </div>
                               <div id="id_dept">
                                   <ul id="%(uid)s" %(attr)s>%(items)s</ul>
                                   <script>
                                       render_dropdown($("#%(uid)s").parents("#show_deptment"), false,'%(need_async_nodes)s');
                                   </script>
                               </div>
                           </div>
                       </span>
                   '''%html_el            
                                
                
#                return ('<input %(required)s id="dropMeal" class="wZBaseCharField input_showq" type="text" readonly="readonly" value="%(disp)s"><input type=hidden name="%(name)s" value="%(value)s">' + \
#                    u'<span class="btn_showDeptTree"><img onclick="render_dropdown(this, false)" src="/media/img/sug_down_on.gif" id="id_drop_dept"><div  id="show_deptment" style="display: none;"><div class="title"><span   style="margin-left:-100px;" class="span_selectNone Link_blue1" onclick="clear_none(this)"><a href="javascript: void(0)">%(none)s</a>&nbsp;&nbsp;</span><span onclick="javascript:$(this).parent().parent().hide();" class="close btn">%(ok)s</span></div><div id="id_dept"><ul %(attr)s>%(items)s</ul></div></div></span>') % html_el            
            else:
                return u'<input type=hidden><input value="%(disp)s" type=hidden>%(value)s<div id="show_deptment"><div id=%(uid)s><ul %(attr)s>%(items)s</ul></div><script>render_dept_($("#%(uid)s"),false,true)</script></div>' % html_el
        except:
            print_exc()

class ZMealChoiceFlatWidget(ZMealChoiceWidget):
    flat=True

class ZMealMultiChoiceWidget(forms.SelectMultiple):
    flat=False
    def __init__(self, attrs={}, choices=()):
        super(ZMealMultiChoiceWidget, self).__init__(attrs=attrs, choices=choices)

    def render(self, name, data, attrs=None, choices=()):
        import time
        from dbapp.urls import surl
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
            need_async_nodes=[]
            vdata =filterdata_by_user(self.choices.queryset.all().filter(available=1),threadlocals.get_current_user())
#            for ii in vdata:
#                if ii.parent_id is not None:
#                    l=[e for e in vdata if  e.id==ii.parent_id]
#                    if not l:ii.parent_id=None
            html=mealdropdown(vdata).html_ul_li(data=data and datapk or [])
            html_el={
                "disp": data and ",".join([u"%s"%d for d in data]) or "", 
                "name": name, 
                "value": data and "".join(['<input type=hidden name="%s" value="%s">'%(name, d.pk) for d in data]) or "",
                "attr": flatatt(self.attrs),
                "id": self.attrs['id'],
                'uid': "%s"%id(self),
                "items": html,
                "ok":_(u"确定"),
                "selectchildren":u"%s"%_(u"包含下级"),
                "need_async_nodes":",".join(need_async_nodes),
                "surl":surl,
                }
            if self.flat: #平铺型
                return u'<input value="%(disp)s" type=hidden>%(value)s<div id="show_deptment"><div id="id_dept"><span id=%(uid)s></span><ul %(attr)s>%(items)s</ul></div><script>render_dept_tree("%(uid)s")</script></div>'%html_el
            else: #下拉框型
                return '''<input type="text" id="dropMeal" class="wZBaseCharField input_showDeptTree" readonly="readonly" value="%(disp)s"/>%(value)s<span class="btn_showDeptTree">
                             <img onclick="javascript:$(this).parent().find('#show_deptment').show();"  src="/media/img/sug_down_on.gif" id="id_drop_dept"/>
                             <div id="show_deptment" style="display: none;">
                                 <div class="title">
                                     <span class="span_selectchildren"  >
                                         
                                         <span class="title_selectchildren" style="display: none;" >%(selectchildren)s &nbsp;&nbsp;</span>
                                     </span>
                                     <span onclick="javascript:$(this).parent().parent().hide();" class="close btn">%(ok)s</span>
                                 </div>
                                 <div id="id_dept">
                                     <ul id="%(uid)s" %(attr)s>%(items)s</ul>
                                     <script>
                                         render_dropdown($("#%(uid)s").parent().parent(), true,'%(need_async_nodes)s');
                                     </script>
                                 </div>
                             </div>
                             
                         </span>
                 '''%html_el
                
#                return ('<input id="dropMeal" type="text" class="wZBaseCharField input_showDeptTree" readonly="readonly" value="%(disp)s">%(value)s'+\
#                        u'<span class="btn_showDeptTree" ><img onclick="render_dropdown(this, true)"  src="/media/img/sug_down_on.gif" id="id_drop_dept"><div id="show_deptment" style="display: none;"><div class="title"><span class="span_selectchildren" displayN></span><span onclick="javascript:$(this).parent().parent().hide();" class="close btn">%(ok)s</span></div><div id="id_dept"><ul %(attr)s>%(items)s</ul></div></div></span>')%html_el
        except:
            print_exc()

class ZMealMultiChoiceDropDownWidget(ZMealMultiChoiceWidget):
    flat=False

