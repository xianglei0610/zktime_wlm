# -*- coding: utf-8 -*-
from django.conf import settings
if settings.DATABASE_ENGINE=='pool':
	settings.DATABASE_ENGINE=settings.POOL_DATABASE_ENGINE

from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys
from mysite.iclock.constant import REALTIME_EVENT, DEVICE_POST_DATA
import thread
import datetime

def process_writedata_handler():
	from mysite.iclock.models.model_cmmdata import process_writedata
	from django.db import connection as conn
	while True:
		process_writedata()
		try:
			#退出的时候防止是断网，不断开连接而不能处理数据，所以关闭该连接
			cur=conn.cursor()
			cur.close()
			conn.close()
		except:
			pass
		
def process_upload_handler():
	from mysite.iclock.models.model_device import Device
	from mysite.iclock.models.model_devcmd import DevCmd
	from mysite.iclock.models.model_trans import Transaction
	
	startTime=datetime.date.today() - datetime.timedelta(days=3)
	EndTime=datetime.date.today()			
	devices=Device.objects.all()
	for dev in devices:
		trans=Transaction.objects.filter(sn_name=dev.sn,TTime__range=(startTime, EndTime))
		cmdStr="ACCOUNT Start=%s       End=%s       Count=%s"%(str(startTime),str(EndTime),str(len(trans)))
		try:
			cmd=DevCmd(SN=dev, CmdContent=cmdStr, CmdCommitTime=datetime.datetime.now())
			cmd.save(force_insert=True)
		except:
			import traceback
			traceback.print_exc()

		

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "Starts write data process."
    args = ''
    
    def handle(self, *args, **options):
        from base.sync_api import SYNC_MODEL
        if SYNC_MODEL:
            from server_update import update_user,update_device, clean_cache
            from base.sync_api import server_update_data as ser_update
            last_clean = datetime.datetime.now()
            while True:
                now = datetime.datetime.now()
                if (now - last_clean).seconds>3600:
                    thread.start_new_thread(clean_cache,())
                    last_clean = now
                ret = ser_update()
                emps = ret['employee']
                devs = ret['device']
                update_user(emps)
                update_device(devs)
                time.sleep(1)
        else:
			thread.start_new_thread(process_writedata_handler,())
			first = True
			while True:
				if first:
					h = datetime.datetime.now().hour
					if h==3:
						thread.start_new_thread(process_upload_handler,())
						first = False
					else:
						time.sleep(60)
				else:
					thread.start_new_thread(process_upload_handler,())
					time.sleep(60*60*24)
			
