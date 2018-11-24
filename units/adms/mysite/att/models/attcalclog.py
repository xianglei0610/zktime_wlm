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

from base.cached_model import CachingModel
from base.operation import Operation


class attCalcLog(models.Model):
    DeptID=models.IntegerField(db_column='DeptID',null=True,blank=True, default=0)
    UserID = models.IntegerField(db_column='UserId', blank=True)
    StartDate = models.DateTimeField( db_column='StartDate',blank=True,null=True)
    EndDate = models.DateTimeField(db_column='EndDate',blank=True)
    OperTime = models.DateTimeField(db_column='OperTime',blank=True)
    Type=models.IntegerField(null=True,default=0,blank=True, editable=False)
    class Admin(CachingModel.Admin):
        visible=False
    class Meta:
        app_label='att'
        db_table = 'attcalclog'
