# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation
from mysite.personnel.models.depttree import DeptTree
from base.operation import ModelOperation
from base.cached_model import STATUS_INVALID
from django.conf import settings
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from mysite.utils import get_option

class NestedDeptException(Exception): pass

DEPT_NAME = _(u"部门")
DEPT_NAME_2 = _(u"部门名称")
DEPT_NAME_ID = _(u"部门编号")

DEPT_TYPES = (
    ("unit", _(u"独立核算单位")),
    ("dept", _(u"部门")),
    ("team", _(u"部门内的小组")),
)

def get_dept_parents(depts,current_dept):
    u"从depts中得到当前部门current_dept的所有父部门"
    store=[]
    stack=[]
    stack.append(current_dept)
    while len(stack)>0:
        pop=stack.pop()
        if pop.pk!=current_dept.pk:
            store.append(pop)
        for elem in depts:
            if elem.pk==pop.parent_id:
                stack.append(elem)
    return store


class Department(CachingModel):
        id = models.AutoField(_(u'部门ID'), db_column="DeptID", primary_key=True, editable=False)
        name = models.CharField(DEPT_NAME_2, db_column="DeptName", max_length=50)
        code = models.CharField(DEPT_NAME_ID, max_length=20, null=True, blank=True)
        parent = models.ForeignKey("self", db_column='supdeptid', verbose_name=_(u'上级部门'), null=True, blank=True)
        type = models.CharField(_(u'部门类型'), max_length=10, null=False, blank=False, default='dept', choices=DEPT_TYPES, editable=False)
        invalidate = models.DateField(_(u'失效日期'), null=True, blank=True, editable=True)
        
        def limit_parent_to(self, queryset):
            #根部门不存在上级部门.
            if self.pk == 1:
                return Department.objects.none()
            valid_depts = filterdata_by_user(queryset, threadlocals.get_current_user())
            if self.pk:
                invalid_pks = [self.pk]#限制不能设置一个部门的上级部门为其自身
                
                for dept in valid_depts:
                    if self in get_dept_parents(valid_depts,dept):#限制不能设置一个部门的上级部门为子部门
                        invalid_pks.append(dept.pk)
                return valid_depts.exclude(pk__in=invalid_pks)
            else:
                return valid_depts

        @staticmethod
        def clear():
            #为保证服务器和设备中数据的一致性，删除部门前先删除这些部门所包含的人员。-comment by darcy
            depts_to_clear = Department.objects.exclude(id=1)
            from mysite.personnel.models import Employee
            emps_to_clear = Employee.objects.filter(DeptID__in=depts_to_clear)
#            emps_to_clear=list(emps_to_clear)
#            emps_to_clear.delete()
#            depts_to_clear.delete()
            for emp in emps_to_clear:
                emp.delete()
            for dept in depts_to_clear:
                dept.delete()

        def parents(self):
                ps = []
                d = self
                while d:
                        try:
                                d = Department.objects.get(id=d.parent_id)
                                ps.append(d)
                                if d == self: break;
                        except:
                                break
                return ps
        def children(self):
                return Department.objects.filter(parent=self)
        def all_children(self, start=[]):
                for d in self.children():
                        if d not in start:
                                start.append(d)
                                d.all_children(start)
        def __unicode__(self):
                if self.code:
                        return u"%s %s" % (self.code, self.name)
                else:
                        return u"%s" % self.name
        def export_unicode(self):
                return u"%s" % self.name
        
        def data_valid(self, sendtype):
            #print "sendtype:%s" % sendtype
            tmp = Department.all_objects.filter(code__exact=self.code)
            if self.code and len(tmp) > 0 and tmp[0].id != self.id:
                raise Exception(u"%(a)s %(b)s"%{"a":self.code,"b":_(u'部门编号已经存在!')})

            if self.id == 1: self.parent = None
            #print self.name
            if self in self.parents():
                    raise NestedDeptException(_(u'不能设置一个部门的上级部门为其自身或其子部门'))
            if not self.parent_id:
                    if self.type != 'unit': self.type = 'unit'

        def save(self):
                if not self.code:
                    raise Exception(_(u'部门编号不能为空!'))                
                if self.id == 1: self.parent = None
                tmp = Department.objects.filter(code__exact=self.code)
                if tmp:
                    if self.id:
                       if self.id !=tmp[0].id: 
                           raise Exception(u"%(a)s %(b)s"%{"a":self.code,"b":_(u'部门编号已经存在!')})
                    else:
                        raise Exception(u"%(a)s %(b)s"%{"a":self.code,"b":_(u'部门编号已经存在!')})
                if len(tmp) > 0 and tmp[0].id != self.id:
                    raise Exception(u"%(a)s %(b)s"%{"a":self.code,"b":_(u'部门编号已经存在!')})
                
                super(Department, self).save()
                if self.id == 1 and get_option("ATT"):
                    from mysite.att.models.attparam import  AttParam
                    a = AttParam.objects.filter(ParaName__exact='CompanyLogo')
                    if a:
                        a = a[0]
                        a.ParaValue = self.name
                        a.save()
                    else:
                        a = AttParam()
                        a.ParaValue = self.name
                        a.ParaName = 'CompanyLogo'
                        a.save()

                #else:
                #        raise Exception("Parent is not exist.")
        def delete(self):
#                for r in self._meta.get_all_related_objects():
#                        objs=getattr(self,r.var_name+"_set").all()
#                        for d in objs:  #设置关联数据的部门为要删除部门的父部门
#                                setattr(d, r.field.name, self.parent)
#                                d.save()
            if self.pk > 1:
                self.deptadmin_set.all().delete()
                super(Department, self).delete()

        class dataimport(ModelOperation):
                help_text = _(u"导入数据") #导入
                verbose_name = _(u"导入")
                def action(self):
                    from django.db import connection
                    from mysite.personnel.dept_import import ImportDeptData
                    obj_import = ImportDeptData(req = self.request,input_name = "import_data")
                    obj_import.exe_import_data()
                    ret_error = obj_import.error_info
                    if ret_error:
                        import traceback
                        traceback.extract_stack()
                        raise Exception(u"%(ret)s"%{
                                    "ret":";".join(ret_error)
                              })


        class _delete(Operation):
                help_text = _(u"撤消部门") #删除选定的记录
                verbose_name = _(u"撤消")
                def action(self):
                        if len(self.object.children()) > 0:
                                raise Exception, _(u'该部门还有下级子部门，不能撤消')
                        from datetime import datetime
                        #from model_emp import Employee
                        emp = Department.employee_set.related.model
                        from model_position import Position     
                        if len(Position.objects.filter(DeptID=self.object)) > 0:
                            raise Exception, _(u'该部门还有职位，不能撤消')
                        
                        if len(emp.objects.filter(DeptID=self.object)) > 0:
                                raise Exception, _(u'该部门还有人员，不能撤消')
                        if self.object.id == 1:
                            raise Exception, _(u'根部门不能撤消')
                        self.object.invalidate = datetime.now().strftime("%Y-%m-%d")
                        self.object.status = STATUS_INVALID
                        deptadmin = Department.deptadmin_set.related.model
                        deptadmin.objects.filter(dept=self.object).delete()
                        self.object.save()
#        class _clear(ModelOperation):
#                visible=False
#                help_text=_(u"清空部门") #删除选定的记录
#                verbose_name=u"清空部门"
#                def action(self):
#                    for dept in Department.objects.exclude(id=1):
#                            dept.delete()
#        class _add(ModelOperation):
#                help_text = _(u"新增部门") #删除选定的记录
#                verbose_name = _(u"新增部门")
#                def action(self):
#                    super(_add, self)._add().action(self)
        def get_parent(self):
            #u"通过get得到父级部门,get具有缓存"
            ret=""
            if not self.parent_id:
                return ret
            try:
                ret=Department.objects.get(id=self.parent_id)
                ret = u"%s"%ret
            except:
                pass
            return ret
        
        def get_parent_code(self):
            #u"通过get得到父级部门代码,get具有缓存"
            ret=""
            if not self.parent_id:
                return ret
            try:
                ret=Department.objects.get(id=self.parent_id)
                ret = ret.code
            except:
                pass
            return ret
            
        class Admin(CachingModel.Admin):
                from depttree import ZDeptChoiceWidget
                sort_fields = ["name", "code"]
                app_menu = "personnel"
                help_text = _(u"如果新增的部门在部门列表中未能显示，请联系管理员到用户编辑中重新授权部门！")
                search_fields = ['name', 'code']
                list_display = ('code', 'name', 'parent')
                adv_fields = ['code', 'name']
                list_filter = ('type', 'parent', 'invalidate')
                newadded_column = {
                   'parent':'get_parent',
                }
                
                import_fields = ['code', 'name', 'parent']
                default_widgets = {
                    'parent': ZDeptChoiceWidget(attrs={
                    "async_model":"personnel__Department",
                    "async_url":"/personnel/get_children_nodes/",
                    "limit":True,
                })}
                
                query_fields = ['code', 'name']
                disabled_perms = ["clear_department"]
                menu_index = 1
                cache = 3600
                report_fields=['code', 'name', 'parent']
                @staticmethod
                def initial_data(): #初始化时增加一个部门
                        if Department.objects.count() == 0:
                                Department(name=u"%s"%_(u"部门名称"), code="1").save()
                        pass
        class Meta:
                app_label = 'personnel'
                db_table = 'departments'
                ordering = ('code', 'name')
                verbose_name = _(u'部门')
                verbose_name_plural = verbose_name
class DeptForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(DeptForeignKey, self).__init__(Department, to_field=to_field, **kwargs)

class DeptManyToManyField(models.ManyToManyField):
        def __init__(self, *args, **kwargs):
                super(DeptManyToManyField, self).__init__(*args, **kwargs)

        def formfield(self, **kwargs):
                from django import forms
                defaults = {'form_class': forms.ModelMultipleChoiceField, 'queryset': self.rel.to._default_manager.complex_filter(self.rel.limit_choices_to)}
                defaults.update(kwargs)

                if defaults.get('initial') is not None:
                        initial = defaults['initial']
                        if callable(initial):
                                initial = initial()
                        defaults['initial'] = initial  #return object collection
                return super(models.ManyToManyField, self).formfield(**defaults)


def update_dept_widgets():
        from dbapp import widgets
        from depttree import ZDeptMultiChoiceWidget
        if DeptForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                from depttree import ZDeptChoiceWidget
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[DeptForeignKey] = ZDeptChoiceWidget(attrs={
                    "async_model":"personnel__Department",
                    "async_url":"/personnel/get_children_nodes/"
                })
        if DeptManyToManyField not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
                widgets.WIDGET_FOR_DBFIELD_DEFAULTS[DeptManyToManyField] = ZDeptMultiChoiceWidget(attrs={
                    "async_model":"personnel__Department",
                    "async_url":"/personnel/get_children_nodes/"
                })

update_dept_widgets()



