from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys

class Command(BaseCommand):
	option_list = BaseCommand.option_list + ()
	help = "Starts data comm center process."
	args = ''
 
	def handle(self, *args, **options):
		from mysite.iaccess.dev_comm_center import rundatacommcenter
		print "DataCommCenter starting... ..."
		try:
		    rundatacommcenter()
		except:
		    import traceback; traceback.print_exc()
