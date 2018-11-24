#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel, Operation
from django.utils.translation import ugettext_lazy as _
from dbapp import data_edit
from mysite.personnel.models.model_emp import Employee, EmpMultForeignKey
from base.cached_model import SAVETYPE_EDIT
from accdoor import AccDoor
from acctimeseg import AccTimeSeg
from mysite.iclock.models.dev_comm_operate import sync_set_firstcard, sync_delete_firstcard
from base.middleware import threadlocals

class  AccFirstOpen(CachingModel):
        u"""
        首卡常开
        """
        door = models.ForeignKey(AccDoor, verbose_name=_(u'门名称'), default=1,editable=True, null=True)
        timeseg = models.ForeignKey(AccTimeSeg, verbose_name=_(u'门禁时间段'), editable=True, null=True)#, default=1
        emp = EmpMultForeignKey(verbose_name=_(u'人员'), null=True, blank=True, editable=False)

        def limit_accfirstopen_to(self, queryset, user):#self 为class
            #需要过滤掉用户权限不能控制的首卡开门人员组(列表datalist)
            da = user.deptadmin_set.all()
            if not user.is_superuser and da:#非超级用户如果a不为空则默认全部区域
                d_limit = [int(d.dept_id) for d in da]
                emps = Employee.objects.exclude(DeptID__in=d_limit)
                queryset = queryset.exclude(emp__in=emps)
            return queryset
        
        def __unicode__(self):
            return u"%s"% self.door

        def save(self, *args, **kwargs):
            super(AccFirstOpen, self).save()#log_msg=False
        
        def delete(self):
            sync_delete_firstcard(self.door)
            super(AccFirstOpen, self).delete()
            self.door.device.check_firstcard_options(self.door)
        
        def get_count(self):
            return self.emp.all().count()
        
        def data_valid(self, sendtype):
            door = AccDoor.objects.get(pk=self.door.pk)#get the door object.sure to exist 
            if sendtype == SAVETYPE_EDIT:
                obj = AccFirstOpen.objects.filter(id=self.id)[0]
                if obj.timeseg_id != self.timeseg_id:
                    if self.timeseg_id in [a.timeseg_id for a in door.accfirstopen_set.all().exclude(timeseg=obj.timeseg_id)]:#如果当前时间段已经存在于该门设定时间段内(自身除外）。
                        raise Exception(_(u'当前用户或其他用户已添加过该门在当前时间段内的首卡常开设置'))
                obj.timeseg_id = self.timeseg_id
            else:#新增
                if self.timeseg_id in [a.timeseg_id for a in door.accfirstopen_set.all()]:#如果当前时间段已经存在于该门设定时间段内。
                    raise Exception(_(u'当前用户或其他用户已添加过该门在当前时间段内的首卡常开设置'))
        class OpDelEmpFromFCOpen(Operation):
            verbose_name = _(u"删除开门人员")
            def action(self):
                pass
        
        class OpAddEmpToFCOpen(Operation):
            verbose_name = _(u"添加开门人员")
            help_text = _(u"""添加具有首卡常开权限人员。""")
            params = []
                                           
            def __init__(self, obj):
                super(AccFirstOpen.OpAddEmpToFCOpen, self).__init__(obj)
                self.params.append(('level_id', models.IntegerField(_(u'权限ID'), null=True, blank=True, default=obj.id)))
            
            def action(self, level_id):
                dept_all = self.request.POST.getlist("dept_all")#'on'或者''
                obj = self.object  #对应权限组名称
                
                if not dept_all:
                    emps = set(self.request.POST.getlist("mutiple_emp"))#添加时mutiple_emp，新增时emp
                else:#勾选 选择部门下所有人员时
                    dept_id = self.request.POST.getlist("deptIDs") 
                    #print '---accfirstopen--dept_id=',dept_id
                    emps = [e.id for e in Employee.objects.filter(DeptID__in = dept_id)]
                
                old_emps = [o.id for o in self.object.emp.all()]
                
                for e in emps:
                    if int(e) not in old_emps:#已添加的不再添加
                        self.object.emp.add(e)
                sync_set_firstcard(self.object.door)

        class Admin(CachingModel.Admin):
            help_text = _(u'首卡常开设置时,系统不允许对门添加重复的时间段。')
            menu_group = 'acc_doorset_'
            menu_focus = 'DoorSetPage'
            parent_model = 'AccDoor'
            menu_index = 100028
            list_display = ('timeseg', 'foemp_count')
            newadded_column = { 'foemp_count':'get_count' }
            #newadded_column = { 'employees': 'get_emp' }
            position = _(u"门禁系统 -> 门设置 -> 首卡常开设置")
            disabled_perms = ['clear_accfirstopen', 'dataimport_accfirstopen', 'dataexport_accfirstopen', 'view_accfirstopen', 'clear_accfirstopen']
            #hide_perms = ["opaddemptofcopen_accfirstopen"]
            #select_related_perms = {"browse_accfirstopen": "opaddemptofcopen_accfirstopen"}
        
        class Meta:
            app_label = 'iaccess'
            db_table = 'acc_firstopen'
            verbose_name = _(u'首卡常开设置')
            verbose_name_plural = verbose_name


def DataPostCheck(sender, **kwargs):
        oldObj=kwargs['oldObj']
        newObj=kwargs['newObj']
        request=sender
        if isinstance(newObj, AccFirstOpen):
            if oldObj is None:
                sync_set_firstcard(newObj.door)
            else:
                if (oldObj.emp_set != newObj.emp_set) or (oldObj.timeseg != newObj.timeseg):
                    sync_set_firstcard(newObj.door)
data_edit.post_check.connect(DataPostCheck)