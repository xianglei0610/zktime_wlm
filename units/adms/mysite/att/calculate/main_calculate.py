# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext as _
from schclass_result import schclass_report
from mysite.att.models import attShifts,AttException,attRecAbnormite

def get_calculate_result(emp,start_date=None,end_date=None):
    '''
    取卡计算最终结果
    '''
    from leave_calculate import deal_att_leave
    result = deal_att_leave(emp,start_date,end_date)
    return  result

def att_calculate(emp_ids,d1,d2):
    '''循环每个人员'''
    #print 'starting att calculate',emp_ids,d1,d2
    import time
    from global_cache import C_ATT_RULE, C_NUM_RUN, C_HOLIDAY, C_SCH_CLASS,JBD_DATA
    C_ATT_RULE.refresh()
    C_ATT_RULE.action_init()    #设置该次计算动作涉及到的全局值
    C_NUM_RUN.action_init()
    C_HOLIDAY.action_init()
    C_SCH_CLASS.action_init()
    for emp in emp_ids:
        '''获取考勤计算结果,以考勤时间点为行'''
        records_result = get_calculate_result(emp,d1,d2)
        attShifts.objects.filter(UserID=emp,AttDate__gte=d1.date(),AttDate__lte=d2.date()).delete()#清空考勤明细表相关数据
        AttException.objects.filter(UserID=emp,StartTime__gte=d1,EndTime__lte=d2).delete() #清空例外明细表相关记录
        attRecAbnormite.objects.filter(UserID=emp,AttDate__gte=d1.date(),AttDate__lte=d2.date()).delete() #清空统计结果详情表相关记录
        _len = len(records_result)
        '''循环计算每个时段'''
        for i in range(_len):
            next = i+1
            if next % 2==0:
                continue
            if next+1>_len:
                break
            '''处理每个时段的数据'''
            schclass_report(records_result[i],records_result[next])
        if JBD_DATA.has_key(emp):
            del JBD_DATA[emp]
        time.sleep(0.1)

def main(request):
    '''
    考勤计算过程入口
    '''
    from dbapp.utils import getJSResponse
    from mysite.att.report_utils import parse_report_arg,parse_grid_arg,filter_userid
    empids,d1,d2 = parse_grid_arg(request)
    #emp_ids = filter_userid(empids,"isatt=1")
    att_calculate(empids,d1,d2)
    return getJSResponse("result=0;message=%s%s%d sec"%(_(u'计算成功'),_(u'总时间'),0))

def auto_calculate(calculate_all):
    from mysite.att.models import WaitForProcessData
    from mysite.personnel.models import Employee
    from mysite.att.models import att_autocal_log
    import time
    objs=WaitForProcessData.objects.filter(flag=1).order_by("id")
    for obj in objs:
        try:                  
            #print "process id '%(pk)s'    %(user)s"%{'pk':obj.pk,'user':obj.UserID} 
            endtime=obj.endtime
            if obj.endtime>datetime.datetime.now():
                endtime=datetime.datetime.now()
            att_calculate([obj.UserID.pk],obj.starttime,endtime)
            obj.flag=2
        except:
            obj.flag=3
            import traceback;traceback.print_exc()    
        try:
            obj.save()
        except:
            pass
        time.sleep(0.1)
    '''每日进行一次前一天的考勤计算'''
    
    if calculate_all:  
        logs = att_autocal_log.objects.all().order_by("-cal_date")
        y=datetime.datetime.now().date()+datetime.timedelta(days=-1)
        s= None
        if logs:
            s=logs[0].cal_date+datetime.timedelta(days=1)
        else:
            s=y          
        emp_ids=Employee.objects.filter(OffDuty__lt=1,isatt__exact=1).values_list('id', flat=True).order_by(*['PIN','DeptID'])
        start = datetime.datetime(s.year,s.month,s.day,0,0,0)
        end = datetime.datetime(y.year,y.month,y.day,23,59,59)
        att_calculate(emp_ids,start,end)
        
#       保存计算日志
        save_date = s 
        while save_date<=y:
            try: 
                cal_log = att_autocal_log()
                cal_log.cal_date = save_date
                cal_log.cal_time = datetime.datetime.now()
                cal_log.save()
                save_date = save_date+datetime.timedelta(days=1)
            except:
                import traceback;traceback.print_exc()
                pass

def day_report(day,schclass_report_list):
    '''
    每日考勤报告
    '''
    start = datetime.datetime(2011,6,1,0,0,0)
    end = datetime.datetime(2011,7,1,23,59,59)
    emp_id = schclass_report_list[0]['emp_id']
    date = day
    
    must_in = 0
    must_out = 0
    not_in = 0
    not_out = 0
    
    late_num = 0
    early_num = 0
    absent_num = 0
    late_sum = 0
    early_sum = 0
    absent_sum = 0
    for e in schclass_report_list:
        pass

