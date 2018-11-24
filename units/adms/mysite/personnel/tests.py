#-- coding=utf-8 --
import unittest
from models import Employee

class EmployeeTestCase(unittest.TestCase):
    def setUp(self):
        Employee.objects.all().delete()
        self.c=5
        for i in range(1,self.c+1):
            Employee(PIN='%05d'%i).save()
        print "setUp OK"
    def testCache(self):
        pin='5'
        self.assertEquals(Employee.objects.all().count(), self.c)
        self.assertEquals(Employee.objects.get(PIN=pin).PIN, pin)
        self.assertEquals(Employee.objects.count(), self.c)
        Employee.clear()
        self.assertEquals(Employee.objects.count(), 0)
        self.assertEquals(Employee.objects.filter(PIN=pin).count(), 0)
        try:
            emp=Employee.objects.get(PIN=pin)
        except:
            emp=None
        self.assertEquals(emp, None)

