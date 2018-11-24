#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from mosys.custom_model import AppPage,GridModel
from apps.personnel.widgets import FormatDateTimeFieldWidget,MultySelectFieldWidget
from apps.personnel.models.model_custom import GetAuthoIDs

from mosys import forms

from apps import dbpool
connection = dbpool.connection()

class OrderReport(GridModel):
    '''
            出勤明细
    '''
    from django.utils.translation import ugettext as _
    verbose_name=u'出勤明细'
    app_menu ="att"
    menu_index=20
    visible = False
#    template = 'order_report.html'
    head = [('id',u'id'),('userid',u'userid'),('DeptID',u'DeptID'),('name',u'姓名'),('badgenumber',u'身份证号'),
            ('DeptName',u'组织名称'),('areaname',u'项目名称'),('attdate',u'考勤日期'),('attTimes',u'出勤时长'),
            ('attdays',u'出勤工作日'),('overtimes',u'加班时间'), ('leaveimes',u'请假时长'),
            ('stopWorkTimes',u'停工时长'), ('remark',u'备注'),
            ]
#    search_form = [
#                   ('userid',MultySelectField(verbose_name=_(u'人员'), add_attrs = {'url':'/page/personnel/EmpSelect/?pure'})),
#                   ('DeptID',MultySelectField(verbose_name=_(u'组织'), add_attrs = {'url':'/page/personnel/DeptSelect/?pure'})),
#                   ('badgenumber',models.CharField(verbose_name=_(u'身份证号'))),
#                   ('startDate', FormatDateTimeField(verbose_name=_(u'开始日期'),add_attrs = {'format':'yyyy-MM-dd','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-01'))),
#                   ('endDate', FormatDateTimeField(verbose_name=_(u'结束日期'),add_attrs = {'format':'yyyy-MM-dd','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-%d'))),
#                   ]
    option = {
            "usepager": True,
            "useRp": True,
            "rp": 20,
            "height":300,
            'checkbox' : False,
            "showTableToggleBtn":False,
            "onToggleCol" : False,
#            "buttons":[
#                       {"name": '导出', "bclass": 'export', "onpress" : '$do_export$'},
#                       ],
              }
    def __init__(self, request):
        super(OrderReport, self).__init__()
        #设置sql
        self.grid.sql = '''
            select ar.id,u.userid,d.DeptID,u.name,u.badgenumber,d.DeptName,ar.areaname,
                ar.attdate, ar.attTimes,ar.attdays,ar.overtimes,
                ar.leaveimes,ar.stopWorkTimes,ar.remark
                from attResult ar
                left join userinfo u on ar.userid = u.userid
                left join departments d on u.defaultdeptid = d.DeptID
                where u.status=0
            '''
        
        def fooAttdate(r):
            """
                            时间转化
            """
            val = r[7] #考勤日期对应sql语句中的第8列,如果sql语句中发生变化,请注意调整该处
            if val=="" or val=="None" :
                return ""
            else:
                return val.strftime('%Y-%m-%d')
        
        #设置 colum 属性
        self.grid.fields["name"]["width"]=100
        self.grid.fields["badgenumber"]["width"]=150
        self.grid.fields["DeptName"]["width"]=100
        self.grid.fields["areaname"]["width"]=180
        self.grid.fields["attdate"]["width"]=80
        self.grid.fields["attTimes"]["width"]=50
        self.grid.fields["attdays"]["width"]=70
        self.grid.fields["overtimes"]["width"]=50
        self.grid.fields["leaveimes"]["width"]=50
        self.grid.fields["stopWorkTimes"]["width"]=50
        self.grid.fields["remark"]["width"]=130
        
        self.grid.fields["attTimes"]["sortable"]=True
        self.grid.fields["attdays"]["sortable"]=True
        
        self.grid.colum_trans["attdate"] = fooAttdate
        
        self.grid.fields["id"]["hide"] = True
        self.grid.fields["userid"]["hide"] = True
        self.grid.fields["DeptID"]["hide"] = True
   
    def MakeData(self,request,**arg):
        #添加数据
        UserID_id = request.params.get("userid", '')
        if UserID_id:
            self.grid.sql += " and u.userid in (%s)"%UserID_id
            
        deptids = GetAuthoIDs(request.user,1)
        defaultdeptid = request.params.get("DeptID", '')
        if defaultdeptid:
            self.grid.sql += " and d.DeptID in (%s)"%defaultdeptid
        elif deptids:
            self.grid.sql += " and d.DeptID in (%s)"%deptids
            
        badgenumber =  request.params.get("badgenumber", '')
        if badgenumber:
            self.grid.sql += " and u.badgenumber like ('%%%%%s%%%%')"%badgenumber
        startDate = request.params.get("startDate", '')
        endDate = request.params.get("endDate", '')
        if startDate:
            startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d')
            self.grid.sql += " and ar.attdate >= '%s'"%startDate
        if endDate:
            endDate = datetime.datetime.strptime((endDate+" 23:59:59"),'%Y-%m-%d %H:%M:%S')
            self.grid.sql += " and ar.attdate <= '%s'"%endDate
        pass
    
class SumReport(GridModel):
    '''
            出勤汇总
    '''
    from django.utils.translation import ugettext as _
    verbose_name=u'出勤报表'
    app_menu ="att"
    menu_index=20
    visible = False
    template = 'sum_report.html'
    head = [('userid',u'userid'),('DeptID',u'DeptID'),('name',u'姓名'),('badgenumber',u'身份证号'),
            ('DeptName',u'组织名称'),('attTimes_sum',u'累计时长'),
            ('attDays_sum',u'累计工作日'),('overtimes_sum',u'加班时间'), ('leaveimes_sum',u'请假时长'),
            ('stopWorkTimes_sum',u'停工时长'), ('completionRate',u'完成率'),
            ]
    search_form = [
                   ('userid',forms.CharField(label=u'人员',widget=MultySelectFieldWidget(attrs= {'url':'/page/personnel/EmpSelect/?pure'}) )  ),
                   ('DeptID',forms.CharField(label=u'组织',widget=MultySelectFieldWidget(attrs= {'url':'/page/personnel/DeptSelect/?pure'}) )  ),
                   ('badgenumber',forms.CharField(label=u'身份证号')),
                   ('startDate', forms.DateTimeField(label=u'开始日期',widget =FormatDateTimeFieldWidget(attrs= {'format':'yyyy-MM-dd','readonly':'true'}),initial=datetime.datetime.now().strftime('%Y-%m-01'))),
                   ('endDate', forms.DateTimeField(label=u'结束日期',widget =FormatDateTimeFieldWidget(attrs= {'format':'yyyy-MM-dd','readonly':'true'}),initial=datetime.datetime.now().strftime('%Y-%m-%d'))),
                   ]
    option = {
            "usepager": True,
            "useRp": True,
            "rp": 20,
            "height":290,
            'checkbox' : False,
            "showTableToggleBtn":False,
            "onToggleCol" : False,
            "buttons":[
                       {"name": '导出', "bclass": 'export', "onpress" : '$do_export$'},
                       ],
              }
    def __init__(self, request):
        super(SumReport, self).__init__()
        #设置sql
        self.grid.sql = '''
            select u.userid,d.DeptID,u.name,u.badgenumber,d.DeptName,
                SUM(ar.attTimes) attTimes_sum,
                SUM(ar.attDays) attDays_sum,
                SUM(ar.overtimes) overtimes_sum,
                SUM(ar.leaveimes) leaveimes_sum,
                SUM(ar.stopWorkTimes) stopWorkTimes_sum,
                1 completionRate 
            from attResult ar
            left join userinfo u on u.userid =  ar.userid
            left join departments d on u.defaultdeptid = d.DeptID
            where 1=1 
                group by u.userid,u.name,u.badgenumber,d.DeptName,d.DeptID
            '''
        def isZJ(pos):
            """判断用户是否有总监的职位"""
            for p in pos:
                if p.id == 1:
                    return True
            return False
        def fooRate(r):
            """
                                完成率颜色变化
            """
            val = r[10] #出勤率对应sql语句中的第2列,如果sql语句中发生变化,请注意调整该处
            useid = r[0] #员工工号
            attTimes = r[5]#出勤时长
            attDays = r[6] #工作日
            leaveimes = r[8] # 请假
            stopWorkTimes = r[9] # 停工
            
            rate = 0
            sum  = attDays*8-leaveimes-stopWorkTimes
            if sum<>0:
                rate = attTimes/sum
            emp = Employee.all_objects.get(id=useid)
            pos = emp.position.all()
            
            flag = isZJ(pos)
            if flag: 
                if rate<0.5:
                    return u"<font color=red>%10.2f(不达标)</font>"%rate
            else:
                if rate<0.8:
                    return u"<font color=red>%10.2f(不达标)</font>"%rate
            return rate
        
            
        def fooName(r):
            """
                                姓名转化
            """
            val = r[2] #人员姓名对应sql语句中的第2列,如果sql语句中发生变化,请注意调整该处
            val_id = r[0]
            return '<a href="javascript:showDetail(%s);" title="点击查看详情">%s</a>'%(val_id,val)
        
        #设置 colum 属性
        self.grid.fields["name"]["width"]=100
        self.grid.fields["badgenumber"]["width"]=150
        self.grid.fields["DeptName"]["width"]=100
        self.grid.fields["attTimes_sum"]["width"]=80
        self.grid.fields["attDays_sum"]["width"]=80
        self.grid.fields["overtimes_sum"]["width"]=80
        self.grid.fields["leaveimes_sum"]["width"]=80
        self.grid.fields["stopWorkTimes_sum"]["width"]=80
        self.grid.fields["completionRate"]["width"]=150
        

        
        self.grid.fields["attTimes_sum"]["sortable"]=True
        self.grid.fields["attDays_sum"]["sortable"]=True
        self.grid.colum_trans["completionRate"] = fooRate
        self.grid.colum_trans["name"] = fooName
        
        self.grid.fields["userid"]["hide"] = True
        self.grid.fields["DeptID"]["hide"] = True
   
    def MakeData(self,request,**arg):
        #添加数据
        self.grid.sql = self.grid.sql.replace("group by u.userid,u.name,u.badgenumber,d.DeptName,d.DeptID","")
        UserID_id = request.params.get("userid", '')
        if UserID_id:
            self.grid.sql += " and u.userid in (%s)"%UserID_id
            
        deptids = GetAuthoIDs(request.user,1)
        defaultdeptid = request.params.get("DeptID", '')
        if defaultdeptid:
            self.grid.sql += " and d.DeptID in (%s)"%defaultdeptid
        elif deptids:
            self.grid.sql += " and d.DeptID in (%s)"%deptids
            
        badgenumber =  request.params.get("badgenumber", '')
        if badgenumber:
            self.grid.sql += " and u.badgenumber like ('%%%%%s%%%%')"%badgenumber
        startDate = request.params.get("startDate", '')
        endDate = request.params.get("endDate", '')
        if startDate:
            startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d')
            self.grid.sql += " and ar.attdate >= '%s'"%startDate
        if endDate:
            endDate = datetime.datetime.strptime((endDate+" 23:59:59"),'%Y-%m-%d %H:%M:%S')
            self.grid.sql += " and ar.attdate <= '%s'"%endDate
        self.grid.sql+=" group by u.userid,u.name,u.badgenumber,d.DeptName,d.DeptID"
        pass
    
#class SumReport_In(SumReport):
#    visible = True
#    
#class OrderReportWindow(OrderReport):
#    '''
#    window出勤表
#    '''
#    verbose_name=u' 个人出勤表'
#    app_menu ="personnel"
#    menu_index=15
#    visible = False
#    template = 'grid_model_window.html'
#    search_form = [
#                   ('startDate', FormatDateTimeField(verbose_name=u'开始日期',add_attrs = {'format':'yyyy-MM-dd','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-01'))),
#                   ('endDate', FormatDateTimeField(verbose_name=u'结束日期',add_attrs = {'format':'yyyy-MM-dd','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-%d'))),
#                   ]
#    option = {
#            "usepager": True,
#            "useRp": True,
#            "rp": 20,
#            "height":320,
#            'checkbox' : True,
#            "showTableToggleBtn":False,
#            "onToggleCol" : False
#              }
#    
#class AttRecord(GridModel):
#    '''
#        原始记录表
#    '''
#    from django.utils.translation import ugettext as _
#    verbose_name = u'原始记录'
#    app_menu = "personnel"
#    menu_index = 11
#    visible = True
##    template = 'order_report.html'
#    head = [('id',u'id'),('userid',u'userid'),('DeptID','DeptID'),('badgenumber',u'身份证号'),('name',u'姓名'),
#            ('DeptName',u'组织名称'),('areaname',u'项目区域'),('checktime',u'考勤时间')
#            ]
#    search_form = [
#                   ('userid',MultySelectField(verbose_name=u'人员', add_attrs = {'url':'/page/personnel/EmpSelect/?pure'})),
#                   ('DeptID',MultySelectField(verbose_name=u'组织', add_attrs = {'url':'/page/personnel/DeptSelect/?pure'})),
#                   ('areaid',MultySelectField(verbose_name=u'项目区域', add_attrs = {'url':'/page/personnel/AreaSelect/?pure'})),
#                   ('startDate', FormatDateTimeField(verbose_name=u'起始日期',add_attrs = {'format':'yyyy-MM-dd','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-%d'))),
#                   ('endDate', FormatDateTimeField(verbose_name=u'结束日期',add_attrs = {'format':'yyyy-MM-dd','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-%d'))),
#                   ]
#    option = {
#            "usepager": True,
#            "useRp": True,
#            "rp": 20,
#            "height":300,
#            'checkbox' : True,
#            "showTableToggleBtn":False,
#            "onToggleCol" : False,
#            "buttons":[
#                       {"name": '导出', "bclass": 'export', "onpress" : '$do_export$'},
#                       ],
#              }
#    def __init__(self):
#        super(AttRecord, self).__init__()
#        #设置sql
#        self.grid.sql = '''
#            select c.id,u.userid,d.DeptID,u.badgenumber,u.name,d.DeptName,
#                  (SELECT areaname 
#                       FROM ( 
#                           SELECT  areaname + ',' 
#                                FROM (
#                                    SELECT DISTINCT areaname 
#                                        FROM personnel_area a,userinfo_attarea ua
#                                        where ua.area_id=a.id and ua.employee_id=u.userid
#                                      ) AS SUM_COL 
#                                FOR XML PATH('') 
#                            )as SUM_AREA(areaname)
#                    ) as areaname,
#                    c.checktime
#                from checkinout c
#                left join userinfo u on u.userid = c.userid
#                left join departments d on u.defaultdeptid = d.DeptID
#                where u.status=0 
#            '''
#        
#        def fooChecktime(r):
#            """
#                            时间转化
#            """
#            val = r[7] #考勤时间对应sql语句中的第8列,如果sql语句中发生变化,请注意调整该处
#            if val=="" or val=="None" :
#                return ""
#            else:
#                return val.strftime('%Y-%m-%d %H:%M:%S')
#        
#        #设置 colum 属性
#        self.grid.fields["id"]["width"]=10
#        self.grid.fields["userid"]["width"]=10
#        self.grid.fields["DeptID"]["width"]=10
#        self.grid.fields["areaname"]["width"]=200
#        self.grid.fields["name"]["width"]=100
#        self.grid.fields["badgenumber"]["width"]=150
#        self.grid.fields["DeptName"]["width"]=150
#        self.grid.fields["checktime"]["width"]=150
#        
#        self.grid.colum_trans["checktime"] = fooChecktime
#        
#        self.grid.fields["id"]["hide"] = True
#        self.grid.fields["userid"]["hide"] = True
#        self.grid.fields["DeptID"]["hide"] = True
#   
#    def MakeData(self,request,**arg):
#        def GetIds(sql):
#            cursor = connection.cursor()
#            cursor.execute(sql)
#            rows = cursor.fetchall()
#            return [str(row[0]) for row in rows]
#        #添加数据
#        emp_ids = []
#        areaid = request.REQUEST.get("areaid", '')
#        if areaid:
#            emp_ids +=  GetIds("select employee_id from userinfo_attarea where area_id in (%s)"%areaid)
#            if not emp_ids:
#                self.grid.sql += " and 1=2 "   
#        UserID_id = request.REQUEST.get("userid", '')
#        if UserID_id:
#            emp_ids+=UserID_id.split(",")
#        if emp_ids:
#            m_emp = ','.join(set(emp_ids))
#            self.grid.sql += " and u.userid in (%s)"%m_emp    
#        deptids = GetAuthoIDs(request.user,1)
#        defaultdeptid = request.REQUEST.get("DeptID", '')
#        if defaultdeptid:
#            self.grid.sql += " and d.DeptID in (%s)"%defaultdeptid
#        elif deptids:
#            self.grid.sql += " and d.DeptID in (%s)"%deptids
#            
#        startDate = request.REQUEST.get("startDate", '')
#        endDate = request.REQUEST.get("endDate", '')
#        if startDate:
#            startDate = datetime.datetime.strptime(startDate,'%Y-%m-%d')
#            self.grid.sql += " and c.checktime >= '%s'"%startDate
#        if endDate:
#            endDate = datetime.datetime.strptime((endDate+" 23:59:59"),'%Y-%m-%d %H:%M:%S')
#            self.grid.sql += " and c.checktime <= '%s'"%endDate
#        pass
#class CheckInOut(GridModel):
#    '''
#            原始记录 ,提供给用户访问
#    '''
#    from django.utils.translation import ugettext as _
#    verbose_name=u'原始记录'
#    app_menu ="att"
#    menu_index=16
#    visible = False
##    template = 'realtimeStatisticsRes_list.html'
#    template = 'CheckInOut.html'
#    head = [('DeptID',u'DeptID'),('userid',u'userid'),('badgenumber',u'人员编号'),('name',u'姓名'),
#            ('DeptName',u'单位名称'), ('code',u'项目名称'),('checktime',u'考勤时间'),('SN',u'位置信息'),
#            ('phone',u"手机号码"),('sendMsg',u"短信通知")
#            ]
#    search_form = [
##                   ('userid',MultySelectField(verbose_name=u'人员', add_attrs = {'url':'/page/personnel/EmpSelect/?pure'})),
##                   ('DeptID',LookupForeignKey("personnel.Department",verbose_name=u'部门',add_attrs = {"tree_type":"treeFolder treeAsync"})),
#                   ('startDate', FormatDateTimeField(verbose_name=u'起始时间',add_attrs = {'format':'yyyy-MM-dd %H:%M:%S','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-%d 00:00:00'))),
#                   ('endDate', FormatDateTimeField(verbose_name=u'结束时间',add_attrs = {'format':'yyyy-MM-dd %H:%M:%S','readonly':'true'},default=datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))),
#                   ]
#    option = {
#            "usepager": True,
#            "useRp": True,
#            "rp": 20,
#            "height":340,
#            'sortname' : "checktime",
#            'sortorder' : "desc",
#            'checkbox' : False,
#            "showTableToggleBtn":False,
##            "onToggleCol" : True,
##            "buttons":[
##                       {"name": '导出', "bclass": 'export', "onpress" : '$do_export$'},
##                       ],
#              }
#    def __init__(self):
#        super(CheckInOut, self).__init__()
#        #设置sql
#        self.grid.sql = '''
#              select  d.DeptID,u.userid,u.badgenumber,u.name,
#                    d.DeptName,d.code,c.checktime,'sn' as SN,u.pager as phone,'sendMsg' as sendMsg
#                 from  checkinout c
#                left join userinfo u on  u.userid = c.userid
#                left join departments d on u.defaultdeptid = d.DeptID 
#                where 1=1
#
#            '''
#        
#        def fooDate(r):
#            """
#                                日期转化
#            """
#            val = r[6] #考勤日期对应sql语句中的第7列,如果sql语句中发生变化,请注意调整该处
#            if val=="" or val=="None" :
#                return ""
#            else:
#                return val.strftime('%Y-%m-%d %H:%M:%S')
#            
#        def fooSN(r):
#            val = r[7] #对应sql语句中的第7列,如果sql语句中发生变化,请注意调整该处
#            if val=="" or val=="None" :
#                return "当前位置"
#            else:
#                return '''<a href="javascript:goToPositionPage('%s');" title="点击查看当前位置">当前位置</a>'''%val
#        
#        def fooSendMsg(r):
#            phone = r[8]
#            if phone:
#                return '''<a href="javascript:sendMsg('%s');" title="点击发送短信">发送短信</a>'''%phone
#            else:
#                return ""
#        
#        #设置 colum 属性
#        self.grid.fields["code"]["width"]=80
#        self.grid.fields["DeptName"]["width"]=100
#        self.grid.fields["badgenumber"]["width"]=80
#        self.grid.fields["name"]["width"]=80
#        self.grid.fields["checktime"]["width"]=140
#        self.grid.fields["SN"]["width"]=80
#        self.grid.fields["phone"]["width"]=100
#        self.grid.fields["sendMsg"]["width"]=80
#        
#        self.grid.fields["checktime"]["sortable"]=True
#        self.grid.fields["badgenumber"]["sortable"]=True
#        
#        self.grid.colum_trans["checktime"] = fooDate
#        self.grid.colum_trans["SN"] = fooSN
#        self.grid.colum_trans["sendMsg"] = fooSendMsg
#        
#        self.grid.fields["DeptID"]["hide"] = True
#        self.grid.fields["userid"]["hide"] = True
#   
#    def MakeData(self,request,**arg):
##        deptids = GetAuthoIDs(request.user,1)
#
#        id_str = request.REQUEST.get("DeptID","")
#        if id_str:
#            ids = id_str.split("_")
#            if ids[0]=="d":
#                self.grid.sql += " and d.DeptID in (%s)"%ids[1]
#            if ids[0]=="e":
#                self.grid.sql += " and u.userid in (%s)"%ids[1]
#        pass
#
#
#
#class ZKAttReport(AppPage):
#    from django.utils.translation import ugettext as _
#    verbose_name=u'原始记录'
#    app_menu ="att"
#    menu_index=26
#    visible = False
#    template = 'zkattreport_window.html'
#
#class Attcalpic(AppPage):
#    from django.utils.translation import ugettext as _
#    verbose_name=u'考勤统计图'
#    app_menu ="att"
#    menu_index=27
#    visible = False
#    template = 'attcalpic.html'
#    search_form = [
#               ('userid',MultySelectField(verbose_name=u'人员', add_attrs = {'url':'/page/personnel/EmpSelect/?pure'})),
#               ('calDate', FormatDateTimeField(verbose_name=u'选择月份',add_attrs = {'format':'yyyy-MM','readonly':'true'},default=(datetime.datetime.now()+datetime.timedelta(days=-30)).strftime('%Y-%m'))),
#               ]
#    def context(self):
#        addition = {}
#        if self.search_form:
#            ''' 查询表单的处理 '''
#            from django.forms import forms
#            from dbapp import widgets
#            form=forms.Form()
#            for e in self.search_form:
#                field = e[1]
#                widget=None                               
#                if field.__class__ in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
#                    widget=widgets.WIDGET_FOR_DBFIELD_DEFAULTS[field.__class__]
#                if widget:
#                    form_field = field.formfield(widget=widget)
#                    if hasattr(field,'add_attrs'):
#                        form_field.widget.attrs.update(field.add_attrs)
#                        #form_field.widget_attrs = lambda o,w:field.add_attrs
#                    form.fields[e[0]]=form_field
#                else:
#                    form.fields[e[0]]=field.formfield()
#            addition["search_form"] = form
#        return addition
#    