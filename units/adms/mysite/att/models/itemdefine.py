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


PUBLISHED=(
(0, "NOT SHARE"),
(1, "SHARE READ"),
(2, "SHARE READ/WRITE")
)

class ItemDefine(models.Model):
    ItemName=models.CharField(primary_key=True,max_length=100,null=False)
    ItemType=models.CharField(max_length=20,null=True)
    Author=models.ForeignKey(User, null=False)
    ItemValue=models.TextField(max_length=100*1024,null=True)
    Published=models.SmallIntegerField(null=True, choices=PUBLISHED, default=0)
    class Admin:
        pass
    class Meta:
        app_label='att'
