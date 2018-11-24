# -*- coding: utf-8 -*-
from django.db import models, connection
import datetime
from base.models import CachingModel, Operation,AppOperation
from mysite.personnel.models.model_dept import DeptForeignKey, DEPT_NAME, DeptManyToManyField, Department
from mysite.personnel.models.model_area import Area, AreaForeignKey, AreaManyToManyField

class TestData(CachingModel):
    dept=DeptForeignKey(verbose_name=DEPT_NAME)
    area=AreaForeignKey(verbose_name=u'所属区域', editable=True, default=1, null=True)
    admin_dept=DeptManyToManyField(Department, verbose_name="Admin Depts", related_name="admin_dept_s")
    admin_area=AreaManyToManyField(Area, verbose_name="Admin Areas", related_name="admin_area_s")
    class Admin(CachingModel.Admin):
        visible=False
        pass
    class Meta:
        app_label="iclock"

