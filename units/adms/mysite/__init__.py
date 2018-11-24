def test_cache(times):
	from personnel.models import Employee
	from iclock.models import Device
	import time
	err_count=0
	Device.objects.filter(id__gt=100).delete()
	
	#for i  in range(times):
	i=0
	while i<times:		
		try:
			e=Device()
			e.alias='test_'+str(i)
			e.sn=str(i+1)
			e.save()
			#print "current e id: %s  %s   current record:%s"%(e.id,e.alias,i)
			e.fw_version="modify_"+str(i)
			e.device_name=str(i+1)
			e.save()
			#print "current e id: %s  %s   current record:%s"%(e.id,e.device_name,i)
			
			
		except:
			#print "cur err count:%s"%err_count
			err_count=err_count+1
			import traceback;traceback.print_exc()
		i=i+1
			