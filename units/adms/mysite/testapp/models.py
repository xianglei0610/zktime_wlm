# -*- coding: utf-8 -*-
from django.db import models
from base.models import CachingModel, Operation
from base.base_code import base_code_by
from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q

verbose_name=_(u"测试")

class Department(CachingModel):
        """
        部门表，实现单位的组织架构
        """
        name=models.CharField(_(u'名字'), max_length=40)
        parent=models.ForeignKey("Department", verbose_name=_(u'父级部门'), help_text=_(u'父部门'), null=True, blank=True)
        dept_type=models.CharField(max_length=40, null=True, blank=True, verbose_name=_(u"类型"), help_text=_(u'部门类型'),
                choices=base_code_by('ORG')
                )
        def limit_parent_to(self, queryset):
                #限制不能设置一个部门的上级部门为其自身或子部门
                if not self: return queryset
                result=[]
                for d in queryset:
                        dd=d
                        while dd:
                                if dd.id==self.id: break
                                dd=dd.parent
                        if not dd:
                                result.append(d.id)
                return queryset.filter(id__in=result)
        def __unicode__(self): 
                return self.name
        class Admin(CachingModel.Admin):
                app_menu="att"
                initial_data=[
                {'name': 'test1'},
                {'name': 'test2', "parent":{'name': 'test1'}}
                ]

class Device(CachingModel):
        SN=models.CharField(max_length=40)
        alias=models.CharField(max_length=40)
        ip_address=models.CharField(max_length=40)
        dept=models.ForeignKey(Department)
        def __unicode__(self): return self.alias or self.SN
        class Admin(CachingModel.Admin):
                initial_data=[
                        {"dept": {'name': 'test1'}, 'alias':"device1", 'SN':"1111111"},
                        {"dept": {'name': 'test3', "parent":{'name':'test2'}}, 'alias':"device2", 'SN':"2222222"},
                        {"dept": {'name': 'test_dept', "parent":{'name':'test3'}}, 'alias':"device3", 'SN':"33333333"}
                ]
                app_menu="att"

class Staff(CachingModel):
        name=models.CharField(max_length=40)
        age=models.IntegerField(default=23)
        dept=models.ForeignKey(Department)
        sex=models.CharField(max_length=2, choices=base_code_by("SEX"))
        hired=models.DateField(_(u"雇佣时间"))
        title=models.CharField(max_length=4, choices=base_code_by("title"), default='dept')
        def __unicode__(self): return self.name
        class opLeave(Operation):
                u"""
                对员工进行离职操作
                """
                operation_name=u'离职'
                confirm=u"Let %s leave, are you sure?"
                def action(self):
                        print u"%s is leave now"%self.object
                def can_action(self):
                        return self.object.status in (STATUS_OK, STATUS_PAUSED)
        class opToDevice(Operation):
                u"""
                把员工传送到指定设备
                """
                operation_name=u"传送到设备"
                confirm=u'Let %s '+operation_name+u', are you sure?'
#                params=(ParamChoiceData(u'选择要传送到的设备', Device),
#                        ParamDateTime(u'选择在设备上的时间范围', param_name='time_range', required=False))
                def action(self, Device, time_range):
                        print u"%s is be delivered to device [%s] during %s!"%(self.object, Device, time_range)
        class Admin(CachingModel.Admin):        
                cache=False
                app_menu="att"

class opStaffShift(Operation):
        u"""给员工排班"""
        operation_name=u"排班"
        def action(self, **kargs):
                print u"给员工 %s 排班成功！"%self.object

Staff.opStaffShift=opStaffShift

#import mysite.db.widgets as widgets
from django import forms

class staff_form(forms.ModelForm):
#        dept=forms.ModelChoiceField(Department.objects.all(), widget=widgets.ZBaseTestWidget)
        class Meta:
                model=Staff
#                exclude=("dept",)
#staff._form_class=staff_form


def createTestData():
        depts=Department.objects.all()
        c=depts.count()
        print "createTestData: ", c
        for i in range(10000-c):
                Department(name="dept_%s"%(i+c), parent=depts[c-i%c-1], dept_type='dept').save()
        
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
from django.core.files import File
#f=open("E:/nature/1.jpg","rb")
#f=File(f)
#c.photo.save("1.jpg",f)
#c.save()

temp_storage = FileSystemStorage(location=settings.APP_HOME,base_url="file")

#update_to 子目录
class Car(CachingModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    photo = models.ImageField(storage=temp_storage, upload_to='cars')
    normal = models.FileField(storage=temp_storage, upload_to='tests')
    class Admin(CachingModel.Admin):        
            cache=False
