#! /usr/bin/env python
#coding=utf-8
from django.db import models, connection
from base.models import CachingModel
from django.utils.translation import ugettext_lazy as _
from accdoor import AccDoor
from acctimeseg import AccTimeSeg
from base.operation import Operation
from dbapp import data_edit
from mysite.iclock.models.dev_comm_operate import sync_delete_user_privilege, sync_set_user_privilege, sync_set_user,sync_set_acc_user
from base.cached_model import SAVETYPE_EDIT
from django.shortcuts import render_to_response
from django.template import  RequestContext
import time
import threading
from redis_self.server import start_dict_server
from base.middleware import threadlocals
from mysite.personnel.models.model_emp import Employee,YESORNO,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey
from dbapp.widgets import get_list_from_file


from mysite.iaccess import sqls
class TThreadComm(object):
    def __init__(self,func,args):
        self.func = func
        self.args = args

    def __call__(self):
        apply(self.func, self.args)

def clear_progress_cache(devs, session_key = ""):
    d_server = start_dict_server()
    d_server.set_to_dict("DEV_COMM_SYNC_%s"%session_key, "%d,0"%(len(devs)*2))
    if devs:
        d_server.set_to_dict("DEV_COMM_PROGRESS_%s"%session_key, "%s,0"%devs[0].alias.encode("gb18030"))
    else:
        d_server.set_to_dict("DEV_COMM_PROGRESS_%s"%session_key, ",0")
    d_server.close()
    
def end_sync_userinfo(session_key=""):
    d_server = start_dict_server()
    d_server.delete_dict("DEV_COMM_SYNC_%s"%session_key)
    d_server.delete_dict("DEV_COMM_PROGRESS_%s"%session_key)
    d_server.close()
    
def sync_total_progress(dev, tol, cur, session_key=""):
    d_server = start_dict_server()
    d_server.set_to_dict("DEV_COMM_SYNC_%s"%session_key, "%d,%d"%(tol, cur))
    d_server.set_to_dict("DEV_COMM_PROGRESS_%s"%session_key, "%s,0"%dev.encode("gb18030"))
    d_server.close()

#向门禁权限组中添加人员    
def sync_userinfo(devs, objs, session_key=""):
    #print "sync_userinfo=", session_key
    tol=len(devs)*3
    cur=0
    for dev in devs:
        cur+=1
        sync_total_progress(dev.alias, tol, cur, session_key)
        dev.set_fqueue_progress(33, session_key)
        sync_set_acc_user([dev], objs, session_key)
        cur+=1
        sync_total_progress(dev.alias, tol, cur, session_key)
        dev.set_fqueue_progress(66, session_key)
        sync_set_user_privilege([dev], objs, session_key)
        cur+=1
        sync_total_progress(dev.alias, tol, cur, session_key)
        dev.set_fqueue_progress(100, session_key)
        time.sleep(2)
    end_sync_userinfo(session_key)
    return 0
    

#权限组 门变动 包含可能的时间段变动
def sync_level_door_edit(dev, session_key=""):
    clear_progress_cache(dev, session_key)              #progress end
    tol=len(dev)*10     
    cur=0 
    for d in dev:
        #cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)
        d.set_fqueue_progress(0, session_key)
        cur_progress = 0
        sync_delete_user_privilege([d], '*')#先删除该设备中的所有人员的权限*代表删除全部
        cur+=2
        cur_progress += 2
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(20, session_key)

        emp_list = d.search_accuser_bydevice()
        cur+=2
        cur_progress += 2
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(40, session_key)
 
        sync_set_acc_user([d], emp_list, session_key)
        cur += 3.0
        cur_progress += 3.0
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(cur_progress*10, session_key)
        sync_set_user_privilege([d], emp_list, session_key)#再同步所有人的新权限
        cur += 3.0
        cur_progress += 3.0
        sync_total_progress(d.alias, tol, cur, session_key)
        d.set_fqueue_progress(cur_progress*10, session_key)  
        d.set_fqueue_progress(100, session_key)  
        time.sleep(2)
    end_sync_userinfo(session_key)     #结束progress
    return


#权限组仅时间段变动
def sync_level_timeseg_edit(dev, session_key=""):
    clear_progress_cache(dev, session_key)
    tol=len(dev)*4     
    cur=0                        
    for d in dev:
        cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(25, session_key)

        duser=d.search_accuser_bydevice()
        cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(50, session_key)
        sync_delete_user_privilege([d], duser)
        cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(75, session_key)
        sync_set_user_privilege([d], duser, session_key)
        cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        d.set_fqueue_progress(100, session_key)
        time.sleep(2)
    end_sync_userinfo(session_key)     #结束progress
    return
    

#删除权限组
def sync_delete_levelset(dev, userset, session_key=""):
    clear_progress_cache(dev, session_key)
    tol=len(dev)*2    
    cur=0                        

    for d in dev:
        #duser=d.search_accuser_bydevice()
        cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        sync_delete_user_privilege([d], userset)
        cur+=1
        sync_total_progress(d.alias, tol, cur, session_key)   #progress
        sync_set_user_privilege([d], userset, session_key)
    end_sync_userinfo(session_key)     #结束progress
    return

ACCESS_LEVEL = 1
ELEVATOR_LEVEL = 2

LEVEL_TYPE_CHOICES =(
    (ACCESS_LEVEL,_(u'门禁权限组')),
    (ELEVATOR_LEVEL,_(u'梯控权限组')),
)

class AccLevelSet(CachingModel):
    u"""
    权限组
    """
    level_name = models.CharField(_(u'权限组名称'), null=True, max_length=30, blank=False, default="", unique=True)
    level_timeseg = models.ForeignKey(AccTimeSeg, verbose_name=_(u'时间段'), null=True, blank=False, editable=True)
    door_group = models.ManyToManyField(AccDoor, verbose_name=_(u'控制范围'), null=True, blank=True, editable=True)
    emp = models.ManyToManyField(Employee, verbose_name=_(u'人员'), null=True, blank=True, editable=False)
    levelset_type = models.IntegerField(_(u'权限组类型'), choices=LEVEL_TYPE_CHOICES, default=1, null=True, blank=True, editable=False)
    is_visitor = models.IntegerField(_(u'访客门禁权限组'), default=0, choices=YESORNO, editable=False) 
    def limit_door_group_to(self, queryset,limitleveltype=0):        
        #需要过滤掉用户权限不能控制的门（需要按照id排序）
        if limitleveltype:#先过滤控制器类型
            acptype=[]
            if limitleveltype == 1:
                is_elevator = 0#非电梯控制器
            else :
                if limitleveltype == 2:
                    is_elevator = 1#电梯控制器
            from mysite.iclock.models import Device
            queryset = queryset.filter(device__is_elevator__exact=is_elevator).order_by('id') 
        u = threadlocals.get_current_user()
        aa = u.areaadmin_set.all()
        if not u.is_superuser and aa:#非超级用户如果a不为空则默认全部区域
            areas = [a.area for a in aa]
            from mysite.iclock.models import Device
            queryset = queryset.filter(device__area__in=areas).order_by('id')
        return queryset.order_by('id')
    
    def limit_level_timeseg_to(self, queryset,limitleveltype=0):
        #通过时间段类型，过滤时间段
        from mysite.iaccess.models.acctimeseg import AccTimeSeg
        if limitleveltype:
            queryset = queryset.filter(timeseg_type=limitleveltype).order_by('id')
        else:
            pass 
        return  queryset.order_by('id') 
            
    

    def limit_acclevelset_to(self, queryset, user):#self 为class
        #需要过滤掉用户权限不能控制的权限组(列表datalist)
        aa = user.areaadmin_set.all()
        da = user.deptadmin_set.all()
        if not user.is_superuser and aa:#非超级用户如果a不为空则默认全部区域
            a_limit = [int(a.area_id) for a in aa]
            doors = AccDoor.objects.exclude(device__area__pk__in=a_limit)
            queryset = queryset.exclude(door_group__in=doors).order_by('id')#不包含不该有的门（设备）即可（可以没有门）
            if da:
                d_limit = [int(d.dept_id) for d in da]
                emps = Employee.objects.exclude(DeptID__in=d_limit)
                queryset = queryset.exclude(emp__in=emps).order_by('id')
        #print '----queryset=',queryset
        return queryset.order_by('id')
        
    def __unicode__(self):
        return self.level_name
    
    def data_valid(self, sendtype):
        tmp = AccLevelSet.objects.filter(level_name=self.level_name.strip())
        if tmp and tmp[0] != self:
            raise Exception(_(u'内容：%s 设置重复！')%self.level_name)

        if AccLevelSet.objects.count() == 255:
            raise Exception(_(u'权限组不能超过255个'))
        
        
    def save(self, *args, **kwargs):
        if self in [a for a in AccLevelSet.objects.all()]:#编辑
            obj = AccLevelSet.objects.filter(id=self.id)[0]
            obj.level_name = self.level_name
            obj.level_timeseg_id = self.level_timeseg_id
            obj.is_visitor = self.is_visitor
            for g in self.door_group.all():
                if g not in obj.door_group.all():
                    obj.door_group.add(g)

            super(AccLevelSet, obj).save(force_update=True, log_msg=_(u'该权限组已变动'))
        else:#新增
            super(AccLevelSet, self).save(force_insert=True)

    #此方法用于获取跟此权限组相关联的门
    def get_doors(self):
        return u",".join([door.door_name for door in self.door_group.all().order_by("id")]) or _(u'暂未设置门信息')
    
    def get_emps(self):
        list_emps = [u'%s %s'%(emp.PIN, emp.EName) for emp in self.emp.all()]
        return list_emps and u",".join(list_emps) or _(u'暂未设置人员信息')
#        if list_emps.__len__() > 10:#最多显示10个人
#            return u",".join(list_emps[0:10]) + u'... 共:%s'% list_emps.__len__()
#        else:
#            return list_emps and u",".join(list_emps) or _(u'尚未给权限组配置人员信息')

    def get_emp_count(self):
        return self.emp.count()
        
    def delete(self):
        devs = []
        userset = [e for e in self.emp.all()]     #权限组所有人
        if userset:#删除时如果权限组中没有人员，则不向设备下发命令。-darcy20110428
            for door in self.door_group.all():
                if door.device not in devs:
                    devs.append(door.device)    #权限组所有设备
            t = threading.Thread(target = TThreadComm(sync_delete_levelset, (devs, userset, "delete_level")))
            t.start()
        return super(AccLevelSet, self).delete()

    def clear_authorize(self):
        #print self.door_group.all(), self.emp.all()
        devs=[]
        if self.emp.all() is not None:
            for door in self.door_group.all():
                if door.device not in devs:
                    devs.append(door.device)
        #add progress
        clear_progress_cache(dev)   
        tol=len(devs)*2      
        cur=0                        
        for dev in devs:
            cur+=1
            sync_total_progress(dev.alias,tol, cur)              #progress end
            sync_delete_user_privilege([dev], self.emp.all())
            cur+=1
            sync_total_progress(d.alias, tol, cur)   #progress
            sync_set_user_privilege([dev], self.emp.all())
        end_sync_userinfo()

    def set_authorize(self, objs, session_key):
        devs=[]
        for door in self.door_group.all():
            if door.device not in devs:
                devs.append(door.device)
        clear_progress_cache(devs, session_key)
        t = threading.Thread(target = TThreadComm(sync_userinfo,(devs, objs, session_key)))
        t.start()
    
    class OpDelEmpFromLevel(Operation):
        verbose_name = _(u"删除人员")
        def action(self):
            pass
        
        
#    class OpDelFromVisitorLevel(Operation):
#        verbose_name = _(u"撤销访客权限组")
#        help_text = _(u'撤销访客权限组，该权限组将变成普通权限组！')
#        visible = False
#        
#        def action(self):
#            try:
#                self.object.is_visitor = 0
#                self.object.save()
#            except:
#                import traceback;traceback.print_exc()
        
#    class OpAddtoVisitorLevel(Operation):
#        verbose_name = _(u"设置为访客权限组")
#        help_text = _(u'设置为访客权限组，即用于访客可通过的权限组！')
#        visible = False
#    
#        def action(self):
#            self.object.is_visitor = 1
#            self.object.save()
#
    class OpAddEmpToLevel(Operation):
        verbose_name = _(u"添加人员")
        help_text = _(u"""向门禁权限组中添加人员，使其具有开门权限。""")
        params = []
                               
        def __init__(self, obj):
            super(AccLevelSet.OpAddEmpToLevel, self).__init__(obj)
            self.params.append(('level_id', models.IntegerField(_(u'权限ID'), null=True, blank=True, default=obj.id)))
            self.params.append(('emps', EmpMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)))

        def action(self, level_id, **args):
            from mysite.iclock.iutils import get_dept_from_all,get_max_in
            emps=args.pop('emps')
            dept_all = self.request.POST.getlist("mutiple_emp_dept_all")#'on'或者''
            onchild = self.request.POST.get("deptIDschecked_child","")
            obj = self.object  #对应权限组名称
            upload_file = self.request.FILES.get("upload_file","")
            file_name = str(upload_file)
            
            downlist = []
            oldemplist = obj.emp.values('id')
            old_emps = [o['id'] for o in oldemplist]
            
            try:
                if not dept_all:
                    if file_name:
                        emps = get_list_from_file(upload_file)
                        emp_query = Employee.objects.filter(id__in = emps)
                    else:
                        emps = self.request.POST.getlist("mutiple_emp")
                        emp_query = Employee.objects.filter(id__in = emps)
                    if len(emp_query)==0:
                        raise Exception(u"请选择人员!")
                    elif len(emp_query) >1000:
                        raise Exception(u"选择人员过多,最大支持1000人!")
                else:#勾选 选择部门下所有人员时
                    dept_id = self.request.POST.getlist("deptIDs")
                    if onchild == "on":
                        dept_id = get_dept_from_all(dept_id,self.request)
                    emp_query = Employee.objects.filter(DeptID__in = dept_id)
                    if len(emp_query)==0:
                        raise Exception(u"请选择人员!")
                    elif len(emp_query) >1000:
                        raise Exception(u"选择人员过多,最大支持1000人!")
                    import json
                    dept_id = json.dumps(dept_id).replace('[','(').replace(']',')').replace('"',"'")
                    cursor = connection.cursor()
#                    sql = '''insert into acc_levelset_emp(acclevelset_id,employee_id) \
#                        select '%s',userid from userinfo where defaultdeptid in %s and userid not in \
#                        (select employee_id from acc_levelset_emp where acclevelset_id='%s')''' % (obj.id,dept_id,obj.id)
                    sql=sqls.OpAddEmpToLevel_insert1(obj.id,dept_id)
                    cursor.execute(sql)
                    connection._commit()
                    connection.close()
                    
                #已经存在的不需要再次添加
                for e in emp_query:
                    if int(e.id) not in old_emps:
                        if not dept_all:
                            cursor = connection.cursor()
                            #sql = 'insert into acc_levelset_emp(acclevelset_id,employee_id) values(%d,%d)'%(obj.id, int(e.id))
                            sql=sqls.OpAddEmpToLevel_insert2(obj.id, int(e.id))
                            cursor.execute(sql)
                        downlist.append(e)
                if downlist is not None:
                    obj.set_authorize(downlist, self.request.session.session_key)
            finally:
                connection._commit()
                connection.close()
        
    class Admin(CachingModel.Admin):
        menu_index = 10003
        help_text = _(u'门禁权限组包含时间段、门组合以及能开门的人员，此处只设置时间段和门组合。<br>系统中不允许设置时间段和门组合完全相同的两个权限组。')
        list_display = ('level_name', 'level_timeseg', 'door_group', 'emp', 'emp_count','levelset_type',)
        #api_fields = ('level_name', 'level_timeseg', 'door_group', 'emp')#.door_name.EName, 'emp'
        api_m2m_display = { "door_group": "door_name", "emp": "PIN.EName" }#多对多字段导出显示关联表的字段。PIN.EName 将默认显示 PIN EName（中间为空格）
        query_fields = ('level_name', 'level_timeseg__timeseg_name',)
        search_field = ('level_name', 'level_timeseg')#过滤器
        newadded_column = {'door_group': 'get_doors', 'emp': 'get_emps', 'emp_count': 'get_emp_count' }#需要在changlist中添加一列时，将list_display中的字段名和该模型的方法组成一个字典即可
        disabled_perms = ['clear_acclevelset', 'dataimport_acclevelset', 'view_acclevelset', 'dataexport_acclevelset']
        hide_perms = ["opaddemptolevel_acclevelset", "opdelempfromlevel_acclevelset"]
        #select_related_perms = {"browse_acclevelset": "opaddemptolevel_acclevelset"}
        opt_perm_menu = { "opaddemptolevel_acclevelset":"iaccess.EmpLevelByLevelPage", "opdelempfromlevel_acclevelset":"iaccess.EmpLevelByLevelPage" }
        default_give_perms = ["contenttypes.can_EmpElevatorLevelSetPage","contenttypes.can_EmpLevelReportPage", "contenttypes.can_EmpLevelSetPage","can_EmpElevatorLevelByEmpPage","can_EmpElevtorLevelByLevelPage"]
        position = _(u'门禁系统 -> 门禁权限组')
    class Meta:
        app_label = 'iaccess'
        db_table = 'acc_levelset'
        verbose_name = _(u'门禁权限组')
        verbose_name_plural = verbose_name
  
def data_pre_check(sender, **kwargs):
    oldObj = kwargs['oldObj']
    model = kwargs['model'] 
    request = sender

    if model == AccLevelSet:
        pk = request.POST.get("pk", 0)#0 or None
        if pk == 'None':
            pk = 0

        door_group = request.POST.getlist("door_group")
        timeseg = request.POST.get("level_timeseg", 0)#不为空故！=0
        objs = AccLevelSet.objects.filter(level_timeseg=int(timeseg))
        for obj in objs:
            if obj.id != int(pk):
                doors = obj.door_group.all().order_by("id")
                if map(int, door_group) == [door.id for door in doors]:
                    raise Exception(_(u'已添加过时间段和门组合完全相同的两个权限组，请重新添加！'))

data_edit.pre_check.connect(data_pre_check)#不同于pre_save

#处理权限组
def DataPostCheck(sender, **kwargs):
    oldObj=kwargs['oldObj']
    newObj=kwargs['newObj']
    request=sender
    if isinstance(newObj, AccLevelSet):
        try:
            if oldObj:  #修改权限组
                #logmsg？
                #print '---newObj.emp_set=',type(newObj.emp_set)
                if newObj.emp_set == oldObj.emp_set == ():#修改时如果修改前后均不涉及到人员变化，则不需要同步数据
                    return
                
                if oldObj.door_group_set!= newObj.door_group_set:     #权限组修改变动
                    #print "door_group change"
                    accdev=[]
                    for door in oldObj.door_group_set:
                        if door not in newObj.door_group_set:
                            accdev.append(door.device)
                    for door in newObj.door_group_set:
                        if door not in oldObj.door_group_set:
                            accdev.append(door.device)
                    dev=list(set(accdev))
                    
                    t = threading.Thread(target = TThreadComm(sync_level_door_edit,(dev, request.session.session_key)))
                    t.start()
                elif oldObj.level_timeseg != newObj.level_timeseg:
                    #print "level_timeseg diff", newObj.door_group_set, oldObj.door_group_set
                    devs=[]
                    for door in newObj.door_group_set:
                        if door.device not in devs:
                            devs.append(door.device)

                    t = threading.Thread(target = TThreadComm(sync_level_timeseg_edit,(devs, request.session.session_key)))
                    t.start()
        except:
            import traceback;traceback.print_exc()

data_edit.post_check.connect(DataPostCheck)

