# -*- coding: utf-8 -*-
from django.db import models, connection
import datetime
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation, ModelOperation
from django.db.models.signals import post_save
from dbapp import data_edit
from mysite.personnel.models.model_dept import DeptForeignKey, DEPT_NAME, Department
from redis_self.server import start_dict_server, queqe_server
from mysite.personnel.models.model_emp import Employee, format_pin, YESORNO, photo_storage


#证件类型
CERTIFICATE_TYPES = (
    (1, _(u'二代身份证')),
    (2, _(u'防伪身份证')),
    (3, _(u'普通身份证')),
    (4, _(u'驾照')), 
    (5, _(u'护照')),
)

#来访事由
VISIT_REASON = (
    (1, _(u'送水')),
    (2, _(u'商谈业务')),
    (3, _(u'快递')),
    (4, _(u'面试')),     
)

#车类型 定义几个范围
CAR_TYPE = (
    (1, _(u'小车')),
    (2, _(u'大巴')),
    (3, _(u'劳斯莱斯')),
)


VISIT_STATE = (
    (1, _(u'进入')),
    (2, _(u'离开')),
)


class VisitorManage(CachingModel):
    """
    访客管理
    """
    visitor_pin = models.CharField(_(u'访客编号'), null=False, max_length=9)#与人员表关联
    certificate_type = models.CharField(_(u'证件类型'), max_length=100, null=False, choices=CERTIFICATE_TYPES, blank=True, default=1)
    certificate_number = models.CharField(_(u'证件号码'), null=True, max_length=20, blank=True)
    visitor_company = models.CharField(_(u'来访单位'), null=False, max_length=24, blank=True, default="")
    visit_reason = models.CharField(_(u'来访事由'), max_length=30, null=True, choices=VISIT_REASON, blank=True)
    visitor_number = models.IntegerField(_(u'来访人数'), max_length=3, null=True, editable=True, blank=True)
    visit_state = models.CharField(_(u'来访状态'), max_length=100, null=True, choices=VISIT_STATE, default=1, blank=True)
    enter_time = models.DateTimeField(_(u'进入时间'), null=True, blank=True, editable=True)
    leave_time = models.DateTimeField(_(u'离开时间'), null=True, blank=True, editable=True)
    entrance = models.CharField(_(u'进入地点'),  max_length=100, null=True, blank=True)
    leave_place = models.CharField(_(u'离开地点'),  max_length=100, null=True, blank=True)
    certificate_photo = models.ImageField(verbose_name=_(u'证件图片'), upload_to='photo', max_length=200)#证件上的头像图片
    capture_photo = models.ImageField(verbose_name=_(u'抓拍图片'), upload_to='photo', max_length=200)
    #scan_photo = models.ImageField(verbose_name=_(u'证件扫描图片'),storage=photo_storage, upload_to='photo',max_length=200)#整个证件的扫描图
    car_type = models.CharField(_(u'车类型'), max_length=100, null=True, choices=CAR_TYPE, blank=True)
    car_number = models.CharField(_(u'车牌号码'), max_length=15, null=True, blank=True)
    park_number = models.CharField(_(u'停车号'), max_length=15, null=True, blank=True)
    accompanying_article = models.TextField(_(u'携带物品'), max_length=150, null=True, blank=True)
    visitor_form_id = models.CharField(_(u'单号'), max_length=30, null=True, blank=True)#访客单单号
    visited_emp = models.ForeignKey(Employee, verbose_name=_(u'被访人'), null=True, max_length=20, blank=True)#用于查询被访人信息
    is_alarm = models.BooleanField(_(u'是否已报警'), editable=True, null=False, blank=True, choices=YESORNO, default=0)
    is_has_visited = models.BooleanField(_(u'是否有来访过'), editable=True, null=False, blank=True, choices=YESORNO, default=0)
    
    def __unicode__(self):
        return u"%s"%(self.visitor_pin  or "")#？？？

    class _delete(Operation):
        visible = False
        verbose_name=_(u'删除')
        def action(self):
            pass

    class _change(Operation):
        visible = True
        verbose_name=_(u'编辑')
        def action(self):
            pass
        
        
    class _add(ModelOperation):
        visible = True
        verbose_name=_(u'进入登记')
        help_text = _(u'''访客进入登记''')
        def action(self):
            pass
    

    def save(self):
        self.visitor_pin = format_pin(self.visitor_pin)
        if self.is_has_visited == 1:#访客已经来访过了，已经有一条记录，不需要再增加，只需更新来访的一些信息
            #print '---343434---laiguo'
            update_visitor_enter_info(self)
            return
        try:
            #print 'self.visit_state=====', self.visit_state
#            if not self.visit_state:
#                self.visit_state = 1
            super(VisitorManage, self).save()
            save_visitor_report(self)
            #update_cache(self)
        except Exception, e:
            print '----visitor_save--ee==', e
            
    def get_visitor_name(self):
        verbose_name = _(u"访客")
        try:
            #print '--------get_visitor_name---self==', dir(self)
            visitor = Employee.objects.get(PIN=self.visitor_pin)
            return visitor.EName
        except:
            pass
            
            
    class OpLeaveRegister(ModelOperation):
        help_text = _(u'''访客离开登记''')
        verbose_name = _(u"离开登记")
        
        def action(self):
            leave_time  = self.request.POST.get("leave_time", "")#离开时间
            leave_place = self.request.POST.get("leave_place", "")#离开地点
            visitor_form_id = self.request.POST.get("visitor_form_id", "")#访客单单号
            certificate_number = self.request.POST.get("certificate_number", "")#证件号码
            card = self.request.POST.get("card", "")#卡号
    
            try:
                if visitor_form_id == "" and certificate_number == "":#？？？分开
                    raise Exception(_(u'单号不能为空'))
                #离开登记后，将记录保存到访客历史记录报表里
                visitor = get_visitor_info(certificate_number, visitor_form_id)
                try:
                    #print '---leave register----visitor=', visitor
                    visitor.leave_time = leave_time
                    visitor.leave_place = leave_place
                    visitor.visit_state = 2
                    visitor.is_has_visited = 0
                    visitor.save()
                    save_visitor_report(visitor)
                    #update_cache(visitor.visitor_pin, "out", visitor.leave_time)#离开登记后更新缓存
                except:
                    raise Exception(_(u'没有该访客的登记记录！'))
                
            except Exception, e:
                #print '-------------eeee=',e
                import traceback; traceback.print_exc();
                raise Exception(_(u'没有该访客的登记记录！'))
    
    #转换到前端页面显示
    def get_visit_reason(self):
        return self.visit_reason and unicode(dict(VISIT_REASON)[int(self.visit_reason)]) or ""
    
    
    def get_visit_state(self):
        return unicode(dict(VISIT_STATE)[int(self.visit_state)])
    
    
    class Admin(CachingModel.Admin):
        from mysite.personnel.models.depttree import ZDeptChoiceWidget
        
        sort_fields = ["-enter_time", "leave_time"]
        app_menu = "visitor"
        #help_text = _(u"如果新增的访客在访客列表中未能显示，请联系管理员！")
        #search_fields = ['pin', 'visitor']
        list_display = ('get_visitor_name', 'visitor_company', 'certificate_number', 'visited_emp', 'get_visit_reason', 'visitor_number', 'entrance', 'leave_place', 'enter_time', 'leave_time', 'get_visit_state', )
        adv_fields = ['visit_reason', 'entrance', 'leave_place', 'enter_time', 'leave_time', 'visitor_number', 'visit_state']
        query_fields = ['entrance', 'leave_place', 'enter_time', 'leave_time', 'visitor_number', 'visit_state']
#        default_widgets = {
#            'dept_id':ZDeptChoiceWidget(attrs={"async_model":"personnel__Department"}),
#        }
        newadded_column = {
            'visitor_name': 'get_visitor_name',
        }
        
        menu_index = 10002
        cache = 3600
        position = _(u'访客系统 -> 访客管理')

    class Meta:
        app_label = 'visitor'
        db_table = 'visitor_manage'
        verbose_name = _(u'访客管理')
        verbose_name_plural = verbose_name


#更新访客来访时长缓存
def update_cache(visitor_pin=None, state=None, visit_time=None):
    #print '--------update----cache=====', visitor_pin, '----state--', state, '---', visit_time
    d_server = start_dict_server()
    visitor_alarm_info = d_server.get_from_dict("visitor_alarm_info")
    if visitor_alarm_info:
        alarm_pin_list = d_server.get_from_dict("visitor_alarm_info")[0]
        alarm_time_list = d_server.get_from_dict("visitor_alarm_info")[1]
        alarm_time_length = d_server.get_from_dict("visitor_alarm_info")[2]

        visitor_pin = int(visitor_pin)
        try:
            if state == "in":
                if alarm_pin_list.count(visitor_pin) > 0:#如果访客已在缓存中，更新进入的时间，放到缓存中最后一位
                    #print '---if----already ----here----'
                    index = alarm_pin_list.index(visitor_pin)
                    alarm_time_list.pop(index)
                    alarm_pin_list.remove(visitor_pin)
                time = visit_time + datetime.timedelta(hours=alarm_time_length)
#                print '--------time---', time
#                print '-----visit_time---',visit_time
#                print '-----hours-----', datetime.timedelta(hours=alarm_time_length)
                alarm_pin_list.append(visitor_pin)
                alarm_time_list.append(time)
            elif state == "out":#离开,删除访客在缓存中的信息
                #print '-----out----'
                index = alarm_pin_list.index(visitor_pin)
                alarm_time_list.pop(index)
                alarm_pin_list.remove(visitor_pin)
                
            d_server.set_to_dict("visitor_alarm_info", [alarm_pin_list, alarm_time_list, alarm_time_length])
        except Exception, e:
            print '====update_cache===eeee===',e
        finally:
            d_server.close()#关闭缓存

#获取访客的信息
def get_visitor_info(number=None, form_id=None):
    try:
        visitor = VisitorManage.objects.get(certificate_number=number)
    except:
        visitor = VisitorManage.objects.get(visitor_form_id=form_id)
    return visitor

#更新来访过的访客进入的信息,用sql语句更新
def update_visitor_enter_info(visitor):
    visited_emp = "null"
    if visitor.visited_emp:
        visited_emp = visitor.visited_emp.id
        
    sql = '''update visitor_manage set visitor_company='%s', visitor_number='%s', certificate_number='%s', \
        certificate_type='%s', visit_reason='%s', enter_time='%s', entrance='%s', car_number='%s', park_number='%s',\
        accompanying_article='%s', visited_emp_id=%s, is_has_visited=1, leave_place='', leave_time=null, visit_state=1 where visitor_pin='%s'\
        '''%(visitor.visitor_company or "", visitor.visitor_number or "", visitor.certificate_number or "", 
        visitor.certificate_type or "", visitor.visit_reason or "", visitor.enter_time, visitor.entrance, visitor.car_number,
        visitor.park_number, visitor.accompanying_article, visited_emp, visitor.visitor_pin)
    try:
        #print sql
        cursor = connection.cursor()
        cursor.execute(sql)
        connection._commit()
        connection.close()
        save_visitor_report(visitor)
    except Exception, e:
        print '--update_visitor_enter_info--e-=',e


#保存访客来访记录信息
def save_visitor_report(visitor):
    from model_report import ReportManage
    
#    sql = "select name, card from userinfo where badgenumber=%s"%visitor.visitor_pin
#    cursor = connection.cursor()
#    cursor.execute(sql)
#    connection.close()
#    emp = cursor.fetchone()
    emp = Employee.objects.get(PIN=visitor.visitor_pin)
    #print '--1--emp--',emp
    #print '--2---state=', visitor.visit_state
    if int(visitor.visit_state) == 1:#进入登记,插入一条记录
        print '-----jin ru---'
        report = ReportManage()
        if visitor.visited_emp:#有没有被访人
            report.visited_emp_pin = visitor.visited_emp.PIN or None#被访人编号
            report.visited_person = visitor.visited_emp.EName or None#被访人姓名
            report.dept = visitor.visited_emp.DeptID.name or None

        report.visitor_pin = visitor.visitor_pin
        report.visitor = emp.EName#访客姓名
        report.card = emp.Card or None#访客的卡号
        report.visitor_company = visitor.visitor_company#来访单位
        report.visit_reason = visitor.visit_reason#来访事由
        report.visitor_number =  visitor.visitor_number#来访人数
        report.entrance = visitor.entrance
        report.enter_time = visitor.enter_time
    elif int(visitor.visit_state) == 2:#离开登记，更新记录
        try:
            report = ReportManage.objects.filter(visitor_pin=visitor.visitor_pin).order_by("-enter_time")[0]#取时间间隔最近的记录                    
            report.leave_time = visitor.leave_time
            report.leave_place = visitor.leave_place
        except:#没有任何记录，返回
            return
    report.visit_state = visitor.visit_state
    report.save()
    

def check_visitor(sender, instance, created, **kwargs):
    pass
    
post_save.connect(check_visitor, sender=Employee)  


#访客进入登记后更新缓存
def DataPostCheck(sender, **kwargs):
    oldObj = kwargs['oldObj']
    newObj = kwargs['newObj']
    request = sender
    if isinstance(newObj, VisitorManage):
        certificate_photo = request.POST.get("certificate_photo", "")
        capture_photo = request.POST.get("capture_photo", "")
#        newObj.certificate_photo = certificate_photo
#        newObj.capture_photo = capture_photo
#        newObj.save()
        sql = "update visitor_manage set certificate_photo='%s', capture_photo='%s' where visitor_pin='%s'"%(certificate_photo, capture_photo, newObj.visitor_pin)
        #print '----sql==',sql
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.close()

data_edit.post_check.connect(DataPostCheck)
