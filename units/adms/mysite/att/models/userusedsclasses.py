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


class UserUsedSClasses(models.Model):
    UserID = models.IntegerField(_(u"人员"), db_column='UserId',blank=True)
    SchId=models.IntegerField(null=True,db_column='SchId',editable=False)
    class Admin:
        visible=False

    class Meta:
        app_label='att'
        db_table = 'useruusedsclasses'
        unique_together = (("UserID","SchId"),)
