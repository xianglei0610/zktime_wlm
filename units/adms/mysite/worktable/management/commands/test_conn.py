# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys
import dict4ini
from django.conf import settings

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "test connnection"
    args = ''
 
    def handle(self, *args, **options):
        import os
        from django.db import connection as conn
        conn_result=True
        try:
            cur=conn.cursor()
        except Exception,e:
            import traceback;traceback.print_exc();
            conn_result=u"%s"%e
            
        #test_dict=dict4ini.DictIni(settings.APP_HOME+"/test_conn.ini")
        #test_dict["test_result"]["success"]="%s"%conn_result
        #test_dict.save()
        
