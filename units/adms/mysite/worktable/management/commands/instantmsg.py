# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys

class Command(BaseCommand):
	option_list = BaseCommand.option_list + ()
	help = "Starts monitor instant message."
	args = ''
 
	def handle(self, *args, **options):
		from mysite.worktable.common_panel import monitor_instant_msg
		print self.help
		monitor_instant_msg()

