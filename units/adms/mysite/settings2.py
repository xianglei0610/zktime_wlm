from mysite.settings import *

if DATABASES['default']['ENGINE']=="pool":
	DATABASES['default']['ENGINE']=DATABASES['default']['POOL_ENGINE']
	print DATABASES

