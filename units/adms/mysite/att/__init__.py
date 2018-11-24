import base
from django.template import add_to_builtins
add_to_builtins('mysite.att.templatetags.att_tags')
import datetime

from django.conf import settings
settings.ATT_CALCULATE_NEW = True

def auto_fill_trans(dept=None,st=datetime.datetime.now()):
	from mysite.personnel.models import Employee
	from models import CheckExact
	
	import random
	now=st
	st=datetime.date(now.year,now.month,1)
	et=datetime.date(now.year,now.month+1,1)
	cday=st
	if dept:
		emps=Employee.objects.filter(DeptID__code__exact=dept)
	else:
		emps=Employee.objects.all()	
	
	while cday<et:
		#print "current date :%s"%cday
		for u in emps:
			#print "%s  current user :%s"%(cday,u)
			for i in range(2):
				insert=True
				am=datetime.datetime(cday.year,cday.month,cday.day,07,45,int(random.random()*100)%60)
				pm=datetime.datetime(cday.year,cday.month,cday.day,18,0,int(random.random()*100)%60)
				if cday.weekday in [5,6]:
					t=int(random.random()*10)
					if t%3!=0:
						insert=False
				if insert:
					t=int(random.random()*100)
					c=CheckExact()
					c.UserID=u
					if i%2:
						c.CHECKTIME=am+datetime.timedelta(minutes=t)
						c.CHECKTYPE="I"
					else:
						c.CHECKTIME=pm+datetime.timedelta(minutes=t)
						c.CHECKTYPE="O"
					c.save()
		cday=cday+datetime.timedelta(days=1)
	
	