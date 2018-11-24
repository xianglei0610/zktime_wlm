#coding:utf-8
from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys

class Command(BaseCommand):
	option_list = BaseCommand.option_list + ()
	help = "Starts redis_self process."
	args = ''
 
	def handle(self, *args, **options):
		from mysite.iaccess.linux_or_win import run_acc_dictmanager
		print "redis_self starting... ..."
		try:
		    run_acc_dictmanager()
		except:
		    import traceback; traceback.print_exc()
