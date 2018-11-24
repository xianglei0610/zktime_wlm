#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os
import time,datetime
import sys
from mysite.att.models.model_syncset import use_ftp ,SyncSet
from mysite.att.ftp_trans import ftp_trans
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "Starts FTP  Synchronous process."
    args = ''
    def handle(self, *args, **options):
        print "FTP sync starting... ..."
        try:
            yesterday=datetime.datetime.now().date()
            info = SyncSet.objects.order_by('syncTime').all()
            for i in info :
                print "info-------------------",i.syncTime,i.times
                
            ftp_trans()
        except:
            import traceback; traceback.print_exc()
