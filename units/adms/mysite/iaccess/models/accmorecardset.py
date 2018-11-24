#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _
from mysite.personnel.models import AccMoreCardEmpGroup
from accdoor import AccDoor
from dbapp import data_edit
from mysite.iclock.models.dev_comm_operate import sync_set_multicard, sync_del_multicard

class AccMoreCardSet(CachingModel):
    u"""
    多卡开门组合（多卡开门组的组合）
    """ 
    door = models.ForeignKey(AccDoor, verbose_name=_(u'当前门'), null=True, blank=True, editable=True)
    comb_name = models.CharField(_(u'组合名称'), null=True, max_length=30, blank=False, unique=True)#Combination Name

    def limit_accmorecardset_to(self, queryset, user):#self 为class
        #需要过滤掉用户权限不能控制的多卡开门组合(列表datalist)
        da = user.deptadmin_set.all()
        if not user.is_superuser and da:#非超级用户如果a不为空则默认全部区域
            d_limit = [int(d.dept_id) for d in da]
            from mysite.personnel.models import Employee
            emps = Employee.objects.filter(DeptID__in=d_limit)#范围内的人
            empgroups_limit = []#所有有效的多卡开门人员组（即有效人所属的组）id
            for emp in emps:
                group = emp.morecard_group
                if group:
                    empgroups_limit.append(group)
            empgroups_all = AccMoreCardEmpGroup.objects.all()#所有多卡开 门人员组
            null_empgroups = empgroups_all.filter(employee__isnull=True)
            for ne in null_empgroups:
                empgroups_limit.append(ne)
            invisible_empgroups = [eg for eg in empgroups_all if eg not in set(empgroups_limit)]#不可见的多卡开门人员组
            #print  '-----empgroups_limit=',empgroups_limit
            #print  '-----invisible_empgroups=',invisible_empgroups
            invisible_morecardset = queryset.filter(accmorecardgroup__group__in=invisible_empgroups)#
            #print '----invisible_morecardset=',invisible_morecardset
            visible_morecardset = [ms.pk for ms in queryset if ms not in invisible_morecardset]
            #print '------visible_morecardset=',visible_morecardset
            queryset = queryset.filter(pk__in=visible_morecardset)#AccMoreCardGroup
        return queryset
    
    def __unicode__(self):
        return u"%s" % self.comb_name
    
    def data_valid(self, sendtype):
        tmp = AccMoreCardSet.objects.filter(comb_name=self.comb_name.strip())
        if tmp and tmp[0] != self:   #新增时不能重复。
            raise Exception(_(u'内容：%s 设置重复！')%self.comb_name)
    
    def get_groups(self):
        return ",".join([unicode(group) for group in self.accmorecardgroup_set.all()]) or _(u'暂无多卡开门组合设置信息')
    
    def save(self, *args, **kwargs):
        super(AccMoreCardSet, self).save()#log_msg=False
   
    def delete(self):
        sync_del_multicard(self)
        super(AccMoreCardSet, self).delete()
        self.door.device.check_muliticard_options(self.door)
         
    class Admin(CachingModel.Admin):
        menu_index = 1000271
        menu_focus = 'DoorSetPage'
        parent_model = 'AccDoor'
        menu_group = 'acc_doorset_'
        disabled_perms = ['clear_accmorecardset', 'dataimport_accmorecardset', 'dataexport_accmorecardset', 'view_accmorecardset', 'clear_accmorecardset']
        list_display = ('comb_name', 'morecardgroup')
        newadded_column = {'morecardgroup': 'get_groups'}
        position = _(u"门禁系统 ->门设置 -> 多卡开门设置")#组合
        help_text = _(u'最多五人同时开门，且五人至少要来自一个组。')
    
    class Meta:
        app_label = 'iaccess'
        db_table = 'acc_morecardset'
        verbose_name = _(u'多卡开门设置')#组合
        verbose_name_plural = verbose_name

class AccMoreCardGroup(CachingModel):
    u"""多卡开门组  开门组（人的组合）的组合,相当于AccMoreCardEmpGroup的组合"""
    comb = models.ForeignKey(AccMoreCardSet, verbose_name=_(u'多卡开门组合'), null=True, blank=True, editable=True)
    group = models.ForeignKey(AccMoreCardEmpGroup, verbose_name=_(u'多卡开门人员组合'), null=True, blank=True, editable=True)
    opener_number = models.IntegerField(_(u'人数'), null=True, blank=True, editable=True)

    def __unicode__(self):
        return u"%s(%s)" % (self.group, self.opener_number)

    def save(self, *args, **kwargs):
        super(AccMoreCardGroup, self).save(log_msg=False)

    class Admin(CachingModel.Admin):
        menu_focus = 'DoorSetPage'
        visible = False

    class Meta:
        app_label = 'iaccess'
        db_table = 'acc_morecardgroup'
        verbose_name = _(u'多卡开门组')
        verbose_name_plural = verbose_name
        
def DataPostBack(sender, **kwargs):
    oldObj=kwargs['oldObj']
    newObj=kwargs['newObj']
    request=sender
    if isinstance(newObj, AccMoreCardSet):
        groups = request.POST.getlist("group")
        numbers = request.POST.getlist("number")
        #groups= [u'1', u'2', u'3']
        #number= [u'2', u'', u'1'] 
        existed_objs = AccMoreCardGroup.objects.filter(comb = newObj)#此处和oldObj不同
        if existed_objs:
            #print "-------------exist"
            #print AccMoreCardGroup.objects.filter(comb = newObj)
            existed_objs.delete()
            #print AccMoreCardGroup.objects.filter(comb = newObj)
        
        for index, number in enumerate(numbers):
            if number and int(number) != 0:#0,00....
                #print groups[index]
                #print number
                
                obj = AccMoreCardGroup()
                obj.comb = newObj
                obj.group =  AccMoreCardEmpGroup.objects.filter(pk=int(groups[index]))[0]#QuerySet object => object instance
                obj.opener_number = int(number)
               
                try:
                    obj.save(force_insert=True)
                except:
                    import traceback;traceback.print_exc()
        try:
            sync_set_multicard(newObj)
        except:
            import traceback;traceback.print_exc()
        
data_edit.post_check.connect(DataPostBack)
