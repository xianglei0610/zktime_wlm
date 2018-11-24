# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator

BOOLEANS=((0,_(u"否")),(1,_(u"是")),)
class DataItem(models.Model):        
    dataName=models.CharField(max_length=100,null=False)
    dbServer=models.CharField(max_length=100,null=False)
    contentType=models.ForeignKey(ContentType, null=False)
    format=models.CharField(max_length=1024,null=False)
    class Admin:
        pass
    class Meta:
        app_label='iclock'
        
class ExportDB(models.Model):
    expName=models.CharField(primary_key=True,max_length=100,null=False)
    dbEngine=models.CharField(max_length=100,null=False)
    dbServer=models.CharField(max_length=100,null=False)
    dbName=models.CharField(max_length=100,null=False)
    dbUser=models.CharField(max_length=100,null=False)
    dbPassword=models.CharField(max_length=100,null=False)
    class Admin:
        pass
    class Meta:
        app_label='iclock'

OverwriteOptions=(
(0, "Skip"),
(1, "Overwrite Always"),
(2, "Overwrite If Empty"),
)
        
class ExportDBItem(models.Model):
    expDB=models.ForeignKey(ExportDB, null=False)
    tableName=models.CharField(max_length=100,null=False)
    fieldName=models.CharField(max_length=100,null=False)
    isKeyField=models.SmallIntegerField(max_length=100, null=False, choices=BOOLEANS, default=0)
    overwrite=models.SmallIntegerField(null=False, choices=OverwriteOptions, default=0)
    dbPassword=models.CharField(max_length=100,null=False)
    contentType=models.ForeignKey(ContentType, null=False)
    dataItem=models.ForeignKey(DataItem, null=False)
    class Admin:
        pass
    class Meta:
        app_label='iclock'
        
