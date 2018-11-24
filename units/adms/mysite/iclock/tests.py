# -*- coding: utf-8 -*-
#在此编写测试例程
import unittest
from models import device_pin, format_pin
from devview import get_device, Device
import datetime
import test
from test.client import Client

#python doctest 方式的测试例程-------------------------


def test_device_pin(pin):
    """
    >>> device_pin('000399')
    '399'
    >>> device_pin('00002')
    '2'
    """


#python unittest 方式的测试例程

class FormatPinTestCase(unittest.TestCase):
    def setUp(self):
        self.pin='98'
        #print "FormatPinTestCase: pin=%s"%self.pin
    def test_format_pin(self):
        from django.conf import settings
        pin=format_pin(self.pin)
        if settings.PIN_WIDTH>1:
            self.assertEquals(len(pin), settings.PIN_WIDTH)
        else:
            self.assertEquals(len(pin), len(self.pin))
        self.assert_(pin.find(self.pin)>=0)

#---测试考勤机发送数据到服务器
def post_many_trans(client, sn, c):
    from test.push_sdk import create_many_trans, DEFAULT_EMP_COUNT
    from mysite import settings
    d=datetime.datetime.now()-datetime.timedelta(days=settings.VALID_DAYS-1)
    dt=datetime.timedelta(seconds=1)
    for i in range(c):
        trans=create_many_trans(d.strftime("%Y-%m-%d %H:%M:%S"))
        d+=dt
        print client.post('/iclock/cdata?SN=%s&Stamp=111222'%sn, raw_post_data=trans)
    return c*DEFAULT_EMP_COUNT
                
class DevicePostTestCase(unittest.TestCase):
    def setUp(self):
        self.sn='1909200005'
        self.client=Client()
        try:
            d=Device.objects.get(sn=self.sn)
            d.delete()
        except: pass
    def test_post_trans(self): #考勤机提交考勤记录数据
        from models import Transaction, Employee
        self.client.get('/iclock/cdata?SN=%s&options=all'%self.sn)          #先自动创建设备
        d=Device.objects.get(sn=self.sn)
        self.assertEquals(d.sn, self.sn)
        count=1
        post_count=post_many_trans(self.client, self.sn, count)
        self.assertEquals(post_count, count*Employee.objects.all().count()) #创建的员工数
        self.assertEquals(post_count, Transaction.objects.all().count())    #创建的考勤记录数
        d.delete() 

class LoginTest(unittest.TestCase):
    def test_login(self):
        from django.contrib.auth.models import User
                
        u=User(username='root', is_superuser=True)
        u.set_password("root")
        u.save()

        c = Client()
        response = c.post('/accounts/login/?next=/u/adms/data/index/', {'username': 'root', 'password': 'root'})
        self.assertEquals(response.status_code,200)
                
class DeviceTestCase(unittest.TestCase):
    def setUp(self):
        self.sn='1909200005'
        self.client=Client()
        try:
            d=Device.objects.get(sn=self.sn)
            d.delete()
        except:
            pass
    def testCache(self):
        self.client.get('/iclock/cdata?SN=%s&options=all'%self.sn)
        #Device(sn=self.sn).save()
        d=Device.objects.get(sn=self.sn)
        self.assertEquals(d.sn, self.sn)
        self.assertEquals(Device.objects.filter(sn=self.sn).count(), 1)
        d.delete()
        print "test create ...."
        #Device(sn=self.sn).save()
        self.client.get('/iclock/cdata?SN=%s&options=all'%self.sn)
        print "test get"
        d=Device.objects.get(sn=self.sn)
        d.Fpversion='10'
        print "test save ...."
        d.save()
        print "test saved"
        d=Device.objects.get(sn=self.sn)
        self.assertEquals(d.Fpversion, '10')


def do_test():
    t=DeviceTestCase('testCache')
    t.setUp()
    t.testCache()
