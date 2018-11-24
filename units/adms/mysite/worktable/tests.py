# -*- coding: utf-8 -*-
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.http import HttpResponse
from django.test import TestCase
import threading

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

def create_department(num=500):
    from mysite.personnel.models import Department
    import random
    dept_all=list(Department.objects.all())
    if len(dept_all)==0:
        d=Department(name="our company",parent=None)
        d.save()
        dept_all.append(d)
    for i in range(num):
        try:
            d=Department(name="department"+str(i),code="code"+str(i))
            d.parent=dept_all[int(random.random()*len(dept_all))]
            d.save()
            dept_all.append(d)
            #print 'ok %s'%i
        except:
            import traceback;traceback.print_exc()

def delete_deparment(num=500):
    from mysite.personnel.models import Department
    Department.objects.all().delete();
    
class TreadTest(object):
    def __init__(self,func,args):
        self.func = func
        self.args = args

    def __call__(self):
        apply(self.func, self.args)

#要处理的主请求
import time
global count_all
count_all={}
def test_progress(request):
    session_key=request.session.session_key
    print 'session_key:',session_key,'\n'
    def func_process(count_number):
        global count_all
        count=0
        while(True):
            count=count+1
            count_all[session_key]=count
            print count
            if count==count_number:
                count_all[session_key]="END"
                break
            time.sleep(0.01)
        return "ok"
    t = threading.Thread(target = TreadTest(func_process, (100000,)))
    t.start()
    return HttpResponse("main_request_end")

#取得主请求的进度
def progress_bar(request):
    session_key=request.session.session_key
    print 'session_key',session_key,'\n'
    global count_all
    if count_all.has_key(session_key):
        return HttpResponse("result:%s\n"%count_all[session_key])
    else:
        return HttpResponse("result:have not start!\n")

def test_sql_export():
    from mysite.personnel.models import Employee
    from django.db import connection
    sql="select u.defaultdeptid,u.name,u.lastname, u.Birthday, d.DeptName,d.code from userinfo u,departments  d where u.defaultdeptid= d.DeptId"
    cur=connection.cursor()
    cur.execute(sql)
    cur.fetchall()
    cur._commit()
    