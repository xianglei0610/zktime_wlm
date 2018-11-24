# coding=utf-8

from mysite.utils import loads
from django.utils.translation import ugettext as _
from dbapp.utils import getJSResponse

AttAbnomiteRptIDs=(1000,1007,1008,1009,1004,1001,1002,1005,1013,1012,1003)
AttRuleStrKeys=()

def LoadAttRule():
    '''
    获取考勤规则
    '''
    AttRule = {
        'EarlyAbsent':0,                #一次早退大于   分钟记
        'LateAbsent':0,                 #一次迟到大于   分钟记
        'MaxShiftInterval':660,         #最长的班次时间不超过
        'MinRecordInterval':5,            #最小的记录间隔
        'MinsEarly' : 5,                  #提前多少分钟记早退
        'MinsLateAbsent':100,             #多少分钟迟到后开始计算缺勤
        'MinsEarlyAbsent':100,            #多少分钟早退后开始计算缺勤
        'MinShiftInterval':120,          #最短的班次时段
        'MinsLate' : 10,                  #超过多长时间记迟到
        'MinsNoIn' : 60,                  #无签到时记多少分钟
        'MinsNoOut' : 60,                 #无签到时记多少分钟  
        'MinsOutOverTime' : 60,           #下班后多少分钟后开始计算加班。
        'MinsWorkDay' : 480,              #日工作时间
        'MinsWorkDay1' : 0,            #计算用
        'NoInAbsent':1,                   #上班无签到是否计算缺勤
        'NoOutAbsent':1,                  #下班无签退是否计算缺勤
        'TakeCardIn':1,                   #上班签到取卡规则
        'TakeCardOut':1,                #下班签到取卡规则
        'jbd_action_type':1,                #加班单作用方式
        'OTCheckRecType':2,               #加班状态
        'OutCheckRecType':3,              #外出记录的处理方式(考勤参数)
        'OutOverTime' :1,                 #下班后记加班
        'TwoDay' : '0',                   #班次跨天时计为第一天还是第二天。
        'WorkMonthStartDay' : 1,          #工作月开始日
        'WorkWeekStartDay' : 0,           #工作周开始日
        'LeaveClass': [{
            'RemaindCount': 1,
            'Classify': 0,
            'LeaveType': 3,
            'LeaveId': 1000,
            'Color': 0,
            'RemaindProc': 1,
            'ReportSymbol': u' ',
            'MinUnit': 0.5,
            'IsLeave': 1,
            'LeaveName': u'应到/实到',
            'Unit': 3
        },
        {
            'RemaindCount': 1,
            'Classify': 0,
            'LeaveType': 3,
            'LeaveId': 1001,
            'Color': 0,
            'RemaindProc': 2,
            'ReportSymbol': u'>',
            'MinUnit': 10.0,
            'IsLeave': 1,
            'LeaveName': u'迟到',
            'Unit': 2
        },
        {
            'RemaindCount': 1,
            'Classify': 0,
            'LeaveType': 3,
            'LeaveId': 1002,
            'Color': 0,
            'RemaindProc': 2,
            'ReportSymbol': u'<',
            'MinUnit': 10.0,
            'IsLeave': 1,
            'LeaveName': u'早退',
            'Unit': 2
        },
        {
            'RemaindCount': 1,
            'Classify': 0,
            'LeaveType': 3,
            'LeaveId': 1003,
            'Color': 0,
            'RemaindProc': 1,
            'ReportSymbol': u'V',
            'MinUnit': 1.0,
            'IsLeave': 1,
            'LeaveName': u'请假',
            'Unit': 2
        },
        {
            'RemaindCount': 1,
            'Classify': 0,
            'LeaveType': 3,
            'LeaveId': 1004,
            'Color': 0,
            'RemaindProc': 1,
            'ReportSymbol': u'A',
            'MinUnit': 0.5,
            'IsLeave': 1,
            'LeaveName': u'旷工',
            'Unit': 3
        },
        {
            'RemaindCount': 1,
            'Classify': 0,
            'LeaveType': 3,
            'LeaveId': 1005,
            'Color': 0,
            'RemaindProc': 1,
            'ReportSymbol': u'+',
            'MinUnit': 1.0,
            'IsLeave': 1,
            'LeaveName': u'加班',
            'Unit': 1
        },
        {
            'RemaindCount': 0,
            'Classify': 0,
            'LeaveType': 2,
            'LeaveId': 1008,
            'Color': 0,
            'RemaindProc': 2,
            'ReportSymbol': u'[',
            'MinUnit': 1.0,
            'IsLeave': 1,
            'LeaveName': u'未签到',
            'Unit': 1
        },
        {
            'RemaindCount': 0,
            'Classify': 0,
            'LeaveType': 2,
            'LeaveId': 1009,
            'Color': 0,
            'RemaindProc': 2,
            'ReportSymbol': u']',
            'MinUnit': 1.0,
            'IsLeave': 1,
            'LeaveName': u'未签退',
            'Unit': 1
        }]
    }
    import cPickle
    try:
        f = open('att_param.data')
        AttRule = cPickle.load(f)
        f.close()
        return AttRule
    except:
        f = open('att_param.data',"w")
        cPickle.dump(AttRule,f)
        f.close()
        return AttRule

SchClass_list = None
def get_SchClass(reload=False):
    '''
    获取系统所有时段供全局公用
    '''
    from mysite.att.models import AttParam
    global SchClass_list
    if not reload and SchClass_list:
        return SchClass_list
    from mysite.att.models import SchClass
    _all = SchClass.objects.all()
    ret = {}
    for e in _all:
        ret[e.pk] ={'CheckIn':e.CheckIn,'CheckOut':e.CheckOut,'shiftworktime':e.shiftworktime,'WorkDay':e.WorkDay,'LateMinutes':e.LateMinutes,'EarlyMinutes':e.EarlyMinutes,'IsOverTime':e.IsOverTime,'OverTime':e.OverTime}
    SchClass_list = ret
    return ret


def transLeaName(leaveID):
    '''
    统计项目ID和名称的映射
    '''
    LeaName={
              1000:_(u'应到/实到'),  
              1001:_(u'迟到'),
              1002:_(u'早退'),
              1003:_(u'请假'),
              1004:_(u'旷工'),
              1005:_(u'加班'), 
              1007:_(u'休息日'),
              1008:_(u'未签到'),
              1009:_(u'未签退'),
              1010:_(u'出'),    
              1011:_(u'出'),  
              1012:_(u'外出'),
              1013:_(u'自由加班'),
              }
    return LeaName[leaveID]


def FetchLeaveClass(dataobj,type=0):
    '''
    获取某个假类或者统计项目的参数信息
    type =0 表示为假类对象 否则为统计项目对象
    '''
    Result={}
    Result['LeaveId']=int(dataobj.LeaveID)
    if type==1:
        Result['LeaveName']=transLeaName(dataobj.LeaveID)
    else:
        Result['LeaveName']=dataobj.LeaveName
    Result['MinUnit']=float(dataobj.MinUnit)    #最小值
    Result['RemaindProc']=int(dataobj.RemaindProc)              #舍入控制0,1,2
    if dataobj.Unit==-1:    #单位
        Result['Unit']=1
    else:
        Result['Unit']=int(dataobj.Unit)
    Result['RemaindCount']=int(dataobj.RemaindCount)       #隐藏状态 累计后进行舍入
    Result['ReportSymbol']=dataobj.ReportSymbol
    Result['Color']=int(dataobj.Color)
    Result['Classify']=int(dataobj.Classify)
    if dataobj.LeaveType:
        Result['LeaveType']=int(dataobj.LeaveType)  #所属内置类别
    else:
        Result['LeaveType']=0
    if type==0:
        if dataobj.clearance:
            Result['clearance']=int(dataobj.clearance)
        else:
            Result['clearance']=0
        
    Result['IsLeave']=0
    if dataobj.LeaveID!=999:
        Result['IsLeave']=1
        if dataobj.Classify!='null':
            if (dataobj.Classify & 0x80)!=0:
                Result['IsLeave']=0
    
    return Result

#获取假类参数,type!=0时仅获取假类参数
def GetLeaveClasses(type=0):
    '''
    获取当前所有假类参数数据 默认包含获取统计项目参数数据
    '''
    from mysite.att.models.model_leaveclass1 import LeaveClass1
    from mysite.att.models.model_leaveclass import LeaveClass
    
    Result=[]

    if (type ==0):
        from mysite.att.calculate.global_cache import C_ATT_RULE
        qry1 = C_ATT_RULE.value['LeaveClass']
        for r in qry1:
            if len(r)>0:
                Result.append(r)

    from mysite.att.calculate.global_cache import C_LEAVE_CLASS
    qry = C_LEAVE_CLASS.value
    for t in qry:
        r=FetchLeaveClass(t)
        if len(r)>0:
            Result.append(r)
    return Result

AttAbnomiteRptIndex={}        
def GetRptIndex(AttAbnomiteRptItems):
    global AttAbnomiteRptIndex
    j=0
    for f in AttAbnomiteRptItems:
        AttAbnomiteRptIndex[f['LeaveId']]=j
        j+=1
    return AttAbnomiteRptIndex
        
def SaveAttRule(AttRules):
    '''
    保存考勤参数处理
    '''
    AttRule = LoadAttRule()
    keys=AttRule.keys()
    post_keys = AttRules.keys()
    for t in post_keys:
        if t in keys:
            if t == 'LeaveClass':
                s=AttRules['LeaveClass']
                lc=loads(s)
                AttRule['LeaveClass'] = []
                for item in lc:
                    for k in item.keys():
                        if k in ('LeaveName','ReportSymbol'):
                            item[k] = item[k]
                        elif k == 'MinUnit':
                            item[k] = float(item[k])
                        else:
                            item[k] = int(item[k])
                    AttRule['LeaveClass'].append(item)
            else:
                if AttRules[t]=='on':
                    AttRule[t]=1
                elif t not in AttRuleStrKeys:
                    AttRule[t]=int(AttRules[t])
                else:
                    AttRule[t]=AttRules[t]
    import cPickle
    f = open('att_param.data',"w")
    cPickle.dump(AttRule,f)
    f.close()
        
def submitAttParam(request):
    '''
    保存考勤参数视图
    '''
    SaveAttRule(request.POST)
    from mysite.att.calculate.global_cache import C_ATT_RULE
    C_ATT_RULE.refresh()
    return getJSResponse("result=0")