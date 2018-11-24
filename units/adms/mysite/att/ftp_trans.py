#! /usr/bin/env python
#coding:utf-8
from django.utils.translation import ugettext_lazy as _
import time,datetime

from mysite.sql_utils import p_query,p_execute
from mysite.att.models.model_syncset import use_ftp ,SyncSet
from mysite.settings import cfg
import os

def ftp_trans():
    while True:
        print "1111111111111"
        time.sleep(10)
        
        
         