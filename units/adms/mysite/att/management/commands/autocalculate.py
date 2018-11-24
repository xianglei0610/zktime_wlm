from django.conf import settings
if settings.DATABASE_ENGINE=='pool':
    settings.DATABASE_ENGINE=settings.POOL_DATABASE_ENGINE

from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys
import datetime

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "Automatic calculate attdance"
    args = ''

    def handle(self, *args, **options):
        if settings.ATT_CALCULATE_NEW:
            from mysite.att.calculate import auto_calculate
        else:
            from mysite.iclock.attcalc import auto_calculate
        import time
        
        auto_calculate(True)
        yesterday=datetime.datetime.now().date()
        while True:
            try:   
                calculate_all=False
                t_now=datetime.datetime.now()
                if t_now.date()>yesterday and t_now.hour == 2 :# 
                    calculate_all=True
                    yesterday=t_now.date()             
                auto_calculate(calculate_all)
                time.sleep(5)
            except:
                time.sleep(30)
                import traceback;traceback.print_exc()
        #send_msg()
            
