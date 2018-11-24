import redis_self.server as q
import time

def exeTime(func):  
    def newFunc(*args, **args2):  
        t0 = time.time()  
        print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)  
        back = func(*args, **args2)  
        print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)  
        print "@%.3fs taken for {%s}" % (time.time() - t0, func.__name__)  
        return back  
    return newFunc  

@exeTime
def test_push(c):
	qs=q.queqe_server()
	for i in range(c):
		qs.lpush("dev", "device %s"%i)
	
@exeTime
def test_pop(c):
	qs=q.queqe_server()
	for i in range(c):
		d=qs.rpop("dev")
		d0="device %s"%i
		if not d==d0:
			raise Exception("expect %s but %s")

"""
------------- test on 192.168.1.8
In [12]: test_push(3000)
	@17:10:28, {test_push} start
	@17:10:28, {test_push} end
	@0.348s taken for {test_push}

In [13]: test_pop(3000)
	@17:10:43, {test_pop} start
	@17:10:44, {test_pop} end
	@0.344s taken for {test_pop}
/dev/sda6 on / type ext4 (rw,relatime,errors=remount-ro)

------------- test on 10.1.1.150, colinux virtual machine
>>> test_push(3000)
	@09:01:56, {test_push} start
	@09:01:58, {test_push} end
	@1.410s taken for {test_push}
>>> test_pop(3000)
	@09:02:06, {test_pop} start
	@09:02:07, {test_pop} end
	@1.040s taken for {test_pop}

------------- test on www.iclockserver.com, amazon ec2 virtual machine
>>> test_push(3000)
	@01:25:06, {test_push} start
	@01:25:07, {test_push} end
	@1.037s taken for {test_push}
>>> test_pop(3000)
	@01:25:07, {test_pop} start
	@01:25:08, {test_pop} end
	@1.055s taken for {test_pop}

------------- test on www.bio-iclock.com
>>> test_push(3000)
	@09:36:15, {test_push} start
	@09:36:16, {test_push} end
	@0.880s taken for {test_push}
>>> test_pop(3000)
	@09:36:16, {test_pop} start
	@09:36:17, {test_pop} end
	@1.043s taken for {test_pop}
/dev/sda3 on / type reiserfs (rw)

------------- test on 10.1.1.176
>>> test_push(3000)
	@21:30:23, {test_push} start
	@21:30:24, {test_push} end
	@1.136s taken for {test_push}
>>> test_pop(3000)
	@21:30:24, {test_pop} start
	@21:30:25, {test_pop} end
	@1.077s taken for {test_pop}
/dev/loop0 on / type ext4 (rw,errors=remount-ro)

------------- test on 10.1.1.176
>>> test_push(3000)
	@22:04:26, {test_push} start
	@22:04:28, {test_push} end
	@1.875s taken for {test_push}
>>> test_pop(3000)
	@22:04:28, {test_pop} start
	@22:04:30, {test_pop} end
	@1.828s taken for {test_pop}
c:/ NTFS

------------- test on 10.6.1.121
>>> test_push(3000)
	@09:42:24, {test_push} start
	@09:42:24, {test_push} end
	@0.717s taken for {test_push}
>>> test_pop(3000)
	@09:42:24, {test_pop} start
	@09:42:25, {test_pop} end
	@0.625s taken for {test_pop}
/dev/sda3 on / type reiserfs (rw)




"""
