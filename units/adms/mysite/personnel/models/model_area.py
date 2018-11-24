#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from depttree import DeptTree, ZDeptChoiceWidget
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

from base.cached_model import STATUS_INVALID
from django.conf import settings
from mysite.utils import get_option
class NestedAreaException(Exception): pass

AREA_NAME = _(u"区域")
AREA_NAME_2 = _(u"区域名称")
AREA_NAME_ID = _(u"区域编号")

AREA_TYPES = (
    ("unit", _(u"独立核算单位")),
    ("area", _(u"区域")),
    ("team", _(u"区域内的小组")),
)

def get_area_parents(areas,current_area):
    u"从areas中得到当前区域current_area的所有父区域"
    store=[]
    stack=[]
    stack.append(current_area)
    while len(stack)>0:
        pop=stack.pop()
        if pop.pk!=current_area.pk:
            store.append(pop)
        for elem in areas:
            if elem.pk==pop.parent_id:
                stack.append(elem)
    return store

class Area(CachingModel):
    areaid=models.CharField(max_length=20,verbose_name=_(u'区域编号'),editable=True)
    areaname=models.CharField(max_length=30,verbose_name=_(u'区域名称'),editable=True)
    parent=models.ForeignKey("self",verbose_name=_(u'上级区域'),editable=True,null=True,blank=True)
    remark=models.CharField(max_length=100,verbose_name=_(u'备注'),null=True,blank=True,editable=True)
    
    def limit_parent_to(self, queryset):
        #根区域不存在上级区域.
        if self.pk == 1:
            from django.db.models.query import QuerySet
            return Area.objects.none()
        valid_areas = filterdata_by_user(queryset, threadlocals.get_current_user())
        if self.pk:
            invalid_pks = [self.pk]#限制不能设置一个区域的上级区域为其自身
            
            for a in Area.objects.all():
                if self in a.parents():#限制不能设置一个区域的上级区域为子区域
                    invalid_pks.append(a.pk)
            return valid_areas.exclude(pk__in=invalid_pks)
        else:
            return valid_areas
    
    
    def save(self):
        from mysite.personnel.models.model_areaadmin import AreaAdmin
        tmp=Area.objects.filter(areaid__exact=self.areaid)
        if self.areaid and len(tmp)>0 and tmp[0].id!=self.id:
            raise Exception(_(u'区域编号已经存在!'))
        is_new = True
        if self.id:
            is_new = False
        
        if self.id==1:self.parent=None
        super(Area,self).save()
        if is_new:
            login_user = threadlocals.get_current_user()
            if login_user and not login_user.is_superuser and AreaAdmin.objects.filter(user__exact = login_user).count()>0:
                obj_ua = AreaAdmin()
                obj_ua.area = self
                obj_ua.user = login_user
                try:
                    obj_ua.save()
                except:
                    import traceback
                    traceback.print_exc()
        

    def delete(self):
        if self.id!=1:
            self.areaadmin_set.all().delete()
            super(Area,self).delete()
            
    @staticmethod
    def clear():
        for a in Area.objects.exclude(id=1): 
                a.delete()
#    class _clear(ModelOperation):
#            visible=False
#            help_text=_(u"清空区域") #删除选定的记录
#            verbose_name=u"清空区域"
#            def action(self):
#                for area in Area.objects.exclude(id=1): 
#                        area.delete()
    def get_user_count(self):
        verbose_name=_(u"该区域用户数")
        from model_emp import Employee
        return Employee.objects.filter(attarea__exact=self).count()    
    def __unicode__(self):
            if self.areaid:
                    return u"%s %s"%(self.areaid, self.areaname)
            else:
                    return u"%s"%self.areaname
    def export_unicode(self):
            return u"%s" % self.areaname
    
    def parents(self):
        ps = []
        area = self
        while area:
            try:
                area = Area.objects.get(id=area.parent_id)
                ps.append(area)
                if area == self: 
                    break;
            except:
                break
        return ps
    
    
    def children(self):
        return Area.objects.filter(parent=self)
    
    def all_children(self, start=[]):
        for a in self.children():
            if a not in start:
                start.append(a)
                a.all_children(start)
                    
    class _delete(Operation):
        help_text=_(u"撤消区域") 
        verbose_name=_(u"撤消区域")
        def action(self):
            if len(self.object.children())>0:
                    raise Exception,_(u'该区域还有下级子区域，不能撤消')
            from datetime import datetime
            dev=Area.device_set.related.model
            if len(dev.objects.filter(area=self.object))>0:
                raise Exception,_(u'该区域还有设备，不能撤消')

            if self.object.employee_set.all().count()>0:
                raise Exception,_(u'该区域还有人员，不能撤消')
            
            from django.conf import settings
            if get_option("IACCESS"):
                if Area.accmap_set.related.model.objects.filter(area=self.object).count() > 0:
                    raise Exception(_(u'该区域中已包含电子地图，不能撤消'))
 
            if self.object.id==1:
                raise Exception,_(u'根区域不能撤消')
            
            areaadmin= Area.areaadmin_set.related.model
            areaadmin.objects.filter(area=self.object).delete()
            self.object.delete()
            
    def get_parent(self):
        u"通过get得到父级部门,get具有缓存"
        ret=""
        if not self.parent_id:
            return ret
        try:
            ret=Area.objects.get(id=self.parent_id)
            ret = u"%s"%ret
        except:
            pass
        return ret
            
    class Admin(CachingModel.Admin):
            sort_fields=["areaid"]
            visible = not get_option("ONLY_POS")#单独消费的时候不显示
            app_menu="iclock"
            menu_group = 'iclock'
            menu_index=9990
            query_fields=['areaid','areaname','remark']     #需要查找的字段
            default_widgets={
                'parent': ZDeptChoiceWidget(
                                attrs={
                                    "async_model":"personnel__Area",
                                    "async_url" : "/personnel/get_children_nodes/",
                                    "limit":True,
                                }
                            ),
            }
            adv_fields=['areaid','areaname','parent','remark']
            list_display=['areaid','areaname','parent','remark']
            newadded_column = {
                'parent':'get_parent',
            }
            cache = 3600
            opt_perm_menu={"opadjustarea_area":"att.AttDeviceUserManage"}#{权限操作的名字（小写）:菜单的路径(app_menu.model)}
            disabled_perms = ["clear_area", "dataimport_area"]
            @staticmethod
            def initial_data(): #初始化时增加一个区域
                    if Area.objects.count()==0:
                            Area(areaname=u"%s"%_(u"区域名称"), areaid="1",parent=None).save()
                    pass
            
    class Meta:
            verbose_name=_(u'区域设置')
            verbose_name_plural=verbose_name
            app_label='personnel'
            
    class OpAdjustArea(ModelOperation):
          verbose_name=_(u"为区域添加人员")
          help_text=_(u'区域的调整,将会把该人员从所属原区域内的设备中清除掉，并自动下发到新区域内的所有设备中(每次最多能添加200人)')  
          #visible = not get_option("IACCESS")
          def action(self):
               from  mysite.personnel.models.model_emp import Employee
               #from mysite.iclock.models.dev_comm_operate import sync_delete_user,sync_set_user
               from base.sync_api import SYNC_MODEL
               if not SYNC_MODEL:
                   from mysite.iclock.models.model_cmmdata import adj_user_cmmdata,save_userarea_together
               import copy
               import datetime
               emps = self.request.POST.getlist('mutiple_emp')
               area =self.request.POST.getlist('AreaSelect')
               deptflag=self.request.POST.get('mutiple_emp_dept_all')
               if deptflag: #按部门选择
                  deptIDs=self.request.POST.getlist('deptIDs')
                  emps =Employee.objects.filter(DeptID__in=deptIDs)
               datalist=[] 
               print len(emps) #注意不能屏蔽掉~ 处理sqlserver2005的时候 为区域分配人员 仅分配100个人
               if len(emps)>200:
                    raise Exception(_(u'人员选择过多！'))
               for i in emps:
                    if deptflag:
                        emp=Employee.objects.get(pk=i.pk)
                    else:
                        emp=Employee.objects.get(pk=i)
#                    if emp.check_accprivage():
#                        devs=emp.search_device_byuser()
#                        sync_delete_user(devs, [emp]) 
                    oldarea=["%s"%u.pk for u in emp.attarea.select_related()]
                    
                    empchange=emp.__class__.empchange_set.related.model()
                    empchange.UserID=emp
                    empchange.changepostion=4
                    empchange.oldvalue=",".join(["%s"%i for i in  emp.attarea.select_related().values_list('pk')] )         
                    empchange.newvalue=",".join(area)
                    empchange.newids = [int(i) for i in area if i]
                    empchange.changedate=datetime.datetime.now()
                    empchange.save()
                    
                    emp.attarea=tuple(area)
                    emp.save()
                    #新增下载人员信息    
                      
                    #sync_set_user(emp.search_device_byuser(), [emp]) 
                    if not SYNC_MODEL:
                        datalist.append(adj_user_cmmdata(emp,Area.objects.filter(pk__in=oldarea),emp.attarea.all(),True))
                    
               if not SYNC_MODEL:
                   save_userarea_together(Employee.objects.filter(pk__in=emps),Area.objects.filter(pk__in=area),datalist)

class AreaForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(AreaForeignKey, self).__init__(Area, to_field=to_field, **kwargs)

class AreaManyToManyField(models.ManyToManyField):
        def __init__(self, *args, **kwargs):
                super(AreaManyToManyField, self).__init__(*args, **kwargs)
        
def update_area_widgets():
        from dbapp import widgets
        if AreaForeignKey not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
            from depttree import ZDeptChoiceWidget
            widgets.WIDGET_FOR_DBFIELD_DEFAULTS[AreaForeignKey]=ZDeptChoiceWidget(
                attrs={
                    "async_model":"personnel__Area",
                    "async_url" : "/personnel/get_children_nodes/",
                    "limit":True,
                }
            )
        if AreaManyToManyField not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
            from depttree import ZDeptMultiChoiceWidget
            widgets.WIDGET_FOR_DBFIELD_DEFAULTS[AreaManyToManyField]= ZDeptMultiChoiceWidget(
                attrs={
                    "async_model":"personnel__Area",
                    "async_url" : "/personnel/get_children_nodes/",
                    "limit":True,
                }

            )
update_area_widgets()



