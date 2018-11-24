#! /usr/bin/env python
#coding=utf-8
from django.db import models
from base.models import CachingModel, Operation
from django.utils.translation import ugettext_lazy as _
from dbapp import data_edit
from base.middleware import threadlocals
from django.db.models import Q

from django.conf import settings
from mysite.utils import get_option
#visible_AccMoreCardEmpGroup=True
#if settings.APP_CONFIG.personnel.AccMoreCardEmpGroup=="False":
#    visible_AccMoreCardEmpGroup=False


class AccMoreCardEmpGroup(CachingModel):
        u"""
        多卡开门人员组表
        """
        group_name = models.CharField(_(u'组名称'), max_length=30, null=False, blank=False, editable=True, unique=True)
        memo = models.CharField(_(u'备注'), max_length=70, null=True, blank=True, editable=True)

        def limit_accmorecardempgroup_to(self, queryset, user):#self 为class
            #需要过滤掉用户权限不能控制的多卡开门人员组(列表datalist)
            da = user.deptadmin_set.all()
            if not user.is_superuser and da:#非超级用户如果a不为空则默认全部区域
                d_limit = [int(d.dept_id) for d in da]
                from model_emp import Employee
                emps = Employee.objects.exclude(DeptID__in=d_limit)#当前用户无权管理的人
                m = queryset.filter(employee__in=emps)
                n = AccMoreCardEmpGroup.objects.all()
                mn = [nn.pk for nn in n if nn not in m]
                queryset = queryset.filter(pk__in=mn)
                #queryset = queryset.exclude(employee__in=emps).distinct()#原来的
                #print '----queryset3=',queryset
            return queryset

        def __unicode__(self):
            return self.group_name

        def data_valid(self, sendtype):
            tmp = AccMoreCardEmpGroup.objects.filter(group_name=self.group_name.strip())
            if len(tmp)>0 and tmp[0] != self:   #编辑状态
                raise Exception(_(u'内容：%s 设置重复！')%self.group_name)

        def save(self, *args, **kwargs):
            super(AccMoreCardEmpGroup, self).save(log_msg=False)

        @staticmethod
        def clear():
            for obj in AccMoreCardEmpGroup.objects.all():
                #避免删除正在被人员使用的多卡开门人员组
                if obj.employee_set.all():
                    obj.employee_set.clear()

                obj.delete()#没有初始化的数据，故可不使用init参数

        def delete(self):
            if self.employee_set.all():
                #self.employee_set.remove(self.employee_set.all()[0])#删除对象时避免将人员信息同时删除
                raise Exception(_(u'该组中已包含人员，请先删除组中的人员再删除该组！'))
            if self.accmorecardgroup_set.all():
                raise Exception(_(u'该组已被使用，请先删除对应的多卡开门组合再删除该组！'))
            super(AccMoreCardEmpGroup, self).delete()

        def get_count(self):
            return self.employee_set.all().__len__()

        class OpDelEmpFromMCEGroup(Operation):
            verbose_name = _(u"删除人员")
            #help_text = u"""从多卡开门人员组中删除人员，删除的人员将不再属于任何一个组。"""
            def action(self):
                pass

        class OpAddEmpToMCEGroup(Operation):
            verbose_name = _(u"添加人员")
            help_text = _(u"""向多卡开门人员组中添加人员，已经添加过组的人员将不能重复添加。要更改某个人员的组别，请先将其从原有组中删除。""")
            only_one_object = True
            def action(self):
                from model_emp import Employee
                from mysite.iclock.models.dev_comm_operate import sync_set_userinfo
                dept_all = self.request.POST.getlist("dept_all")#'on'或者''
                if not dept_all:
                    emps = self.request.POST.getlist("mutiple_emp")
                else:#勾选 选择部门下所有人员时
                    dept_id = self.request.POST.getlist("deptIDs")#dept_all  on
                    #user = threadlocals.get_current_user()#根据当前用户能管理的部门进行判断
                    #da = user.deptadmin_set.all()
                    #if not user.is_superuser and da:
                        #limit_depts = [int(d.dept_id) for d in da]
                        #dept_id = [int(left) for left in dept_id if int(left) in limit_depts]#剩余的部门list
                    #dept_id = [int(left) for left in dept_id if int(left) in limit_depts]#剩余的部门list
                    #print '----------dept_id=',dept_id
                    emps = [e.id for e in Employee.objects.filter(DeptID__in=dept_id, morecard_group__isnull=True)]#选择出来部门里没有分过组的人

                for emp in emps:
                    try:
                        self.object.employee_set.add(Employee.objects.get(pk = int(emp) or None))#建立当前对象与人的关联关系
                        #devs = emp.search_accdev_byuser()
                        accmorecardgroups = self.object.accmorecardgroup_set.all()
                        if accmorecardgroups:
                            devs = []
                            emp = Employee.objects.get(pk = int(emp))
                            devs_emp = emp.search_accdev_byuser()
                            for acc_group in accmorecardgroups:
                                acc_doors = acc_group.comb.door
                                dev = acc_doors.device
                                if dev in devs_emp:#只有当设备中有用户权限时才下更新多卡开门人员信息的命令
                                    devs.append(dev)
                            sync_set_userinfo(set(devs), [emp])#更新多卡开门人员信息
                    except:
                        import traceback; traceback.print_exc()


        class Admin(CachingModel.Admin):
            list_display = ('group_name', 'morecard_emp_count', 'memo')#count为组内人数
            newadded_column = { "morecard_emp_count" : "get_count" }
            query_fields = ('group_name', 'memo')
            menu_index = 1000272
            parent_model = 'DoorSetPage'
            app_menu = "iaccess"
            menu_group = 'acc_doorset'
            menu_focus = 'DoorSetPage'
            position = _(u'门禁系统 -> 门设置 -> 多卡开门人员组')
            disabled_perms = ['dataimport_accmorecardempgroup', 'dataexport_accmorecardempgroup', 'view_accmorecardempgroup', 'clear_accmorecardempgroup']
            #select_related_perms = {"browse_accmorecardempgroup": "opaddemptomcegroup_accmorecardempgroup"}
            help_text =_(u'多卡开门人员组是对人员的分组，每个人员只能属于一个组。')
            visible= get_option("IACCESS")
        class Meta:
            app_label='personnel'
            db_table = 'acc_morecardempgroup'
            verbose_name = _(u'多卡开门人员组')
            verbose_name_plural = verbose_name
            #unique_together = (("gid", "group_id"),)
