#coding=utf-8
import datetime
from django.db import models
from dbapp.utils import save_tmp_file
from mysite.personnel.models import Employee

class AttCalculateBase(object):
    '''
    考勤计算报表工具类
    '''
    def __init__(self,dic,pagesize=30):
        self.current_page = 1
        self.pagesize = pagesize
        
        self.dic = dic
        self.__fieldcaptions= [e[1] for e in self.dic]
        self.__fieldnames =  [e[0] for e in self.dic]
        self.CalculateItem = {}
        self.CalculateItems = []
        self.PagedItems = []
        self.result = {}
        self.ReItemObj()
        
    def NewItem(self):
        for e in self.CalculateItem.keys():
            self.CalculateItem[e]=''
        return self.CalculateItem
       
    def AddItem(self,obj):
        self.CalculateItems.append(obj.copy())
        
    def ReItemObj(self,dic = None):
        if dic:
            self.dic = dic
            self.__fieldcaptions= [e[1] for e in self.dic]
            self.__fieldnames =  [e[0] for e in self.dic]            
        for e in self.__fieldnames:
            self.CalculateItem[e]=None
            
    def SaveTmp(self):
        file_name="_tmp_%s"%id(self.result)
        attrs=dict([(str(k), models.CharField(max_length=1024, verbose_name=self.__fieldcaptions[self.__fieldnames.index(k)])) for k in self.__fieldnames])
        admin_attrs={"read_only":True, "cache": False, "log":False}
        save_tmp_file(file_name, (attrs, admin_attrs, self.CalculateItems))
        return file_name
    
    def paging(self,item_count=None,offset=None,pagesize=None):
        '''
        实现标准的分页功能
        @param    item_count    记录总数
        @param    offset    当前页
        @param    pagesize 每页记录数
        @return    返回起止记录号、分页信息字典
        '''
        if not item_count:
            item_count = len(self.CalculateItems)
        if not offset:
            offset = self .current_page
        if not pagesize:
            pagesize = self.pagesize
        
        if pagesize:
            limit = pagesize
        else:
            limit = 12#settings.PAGE_LIMIT
        if item_count % limit==0:
            page_count =item_count/limit
        else:
            page_count =int(item_count/limit)+1                        
        if offset>page_count and page_count:offset=page_count
        Result = {}
        Result['item_count']=item_count
        Result['page']=offset
        Result['limit']=limit
        Result['from']=(offset-1)*limit+1
        Result['page_count']=page_count
        begin = (offset-1)*limit
        end = offset*limit
        self.PagedItems = self.CalculateItems[begin:end]
        self.result.update(Result)
    def ItemData(self):
        for e in self.CalculateItems:
            print e
    def ItemCount(self):
        return  len(self.CalculateItems)
    def GetDatas(self):
        dd = []
    def ResultDic(self,page=1):
        self.paging(offset=page)
        self.result['fieldcaptions'] = [e[1] for e in self.dic]
        self.result['fieldnames'] =  [e[0] for e in self.dic]
        self.result['disableCols'] = []
        self.result['tmp_name'] = self.SaveTmp()
        self.result['datas'] = self.PagedItems
        return self.result
    
def get_emps_by_deptidlist(deptlist,child = False):
    from mysite.sql_utils import p_query
    if child :
        # 包含下级
        sql = """
            
            WITH NODES     
             AS (   
             SELECT DeptID,supdeptid FROM DBO.departments par WHERE par.DeptID in (%s)
             UNION ALL     
             SELECT child.DeptID,child.supdeptid FROM departments AS child INNER JOIN   
              NODES  AS RC ON child.supdeptid = RC.DeptID)    
              select userid from userinfo  where userinfo.defaultdeptid in( (SELECT DeptID  FROM NODES N )
            )
        """%deptlist
    else:
        sql = """
           select u.userid from userinfo u
            left join departments d on u.defaultdeptid=d.DeptID
            where d.DeptID in (%s)
        """%deptlist
#    print sql
    res = p_query(sql)
    if res:
        return ["%d"%(r[0]) for r in res]
    else:
        return ["-1"]
def get_emps_by_req(request):
    '''
            用来返回报表查询中选人控件选中了包含下级时的人员列表
    request 请求上下文
    return  返回所选择的对象id列表
    '''
    from mysite.iclock.iutils import get_dept_from_all
    userids=request.REQUEST.get('UserIDs',"-1")
    deptids=request.REQUEST.get('DeptIDs',"")
    dept_child = request.REQUEST.get('dept_child',"0")
    uid_list = []
    depts = []
    if deptids:
    # 以部门的选择为主
        #包含下级/不包含
        ch = dept_child == "1" and True or False
        uid_list = get_emps_by_deptidlist(deptids,ch)
    else:
    # 以人员的选择为主
        u_l = userids.split(",")
        uid_list = ["%s"%us for us in u_l if us != ""]
    return uid_list

def filter_userid(userids,sql_where):
    """
    根据数据库 条件 过滤人员id ，返回过滤后的人员id
    """
    from mysite.sql_utils import p_query
    ret = []
    if userids and sql_where:
        lens = len(userids)
        batch = 900
        times = lens%batch ==0 and lens/batch or (lens/batch + 1)
        in_str = "userid in (%s)" %(") or userid in (".join([str(userids[i*batch:(i+1)*batch]).replace("[","").replace("]","").replace("u","") for i in range(times)]))
        select_sql= """
            select userid from userinfo 
                where  %s  and  %s
        """%(sql_where,in_str)
#        print "select_sql=", select_sql
        res = p_query(select_sql)
        if res:
            ret = [i[0] for i  in res] 
    return ret

def parse_report_arg(request,only_uid=False):
    '''
    考勤计算报表请求数据处理
    '''
    userids = get_emps_by_req(request)
    userids = [str(e) for e in userids if e!=""]
    userids = ','.join(userids).split(',')
    deptids = []      
    st=request.REQUEST.get('ComeTime','')
    et=request.REQUEST.get('EndTime','')+" 23:59:59"
    d1=datetime.datetime.strptime(st,'%Y-%m-%d')
    d2=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
    try:
        offset = int(request.REQUEST.get('p', 1))
    except:
        offset=1
    return userids,deptids,d1,d2,offset

def parse_grid_arg(request):
    '''
    考勤计算报表请求数据处理
    '''
    try:
        userids = get_emps_by_req(request)
#        userids = [str(e) for e in userids if e!=""]
#        if len(userids)>0:
#            userids = ','.join(userids).split(',')
#        else:
#            userids = []
        st=request.REQUEST.get('ComeTime','')
        et=request.REQUEST.get('EndTime','')+" 23:59:59"
        d1=datetime.datetime.strptime(st,'%Y-%m-%d')
        d2=datetime.datetime.strptime(et,'%Y-%m-%d %H:%M:%S')
#        print  userids,d1,d2
        return userids,d1,d2
    except:
        import traceback;traceback.print_exc();
        return [],None,None

def get_ExceptionID(Exception,UserID,AttDate):
    '''例外情况'''
    import datetime
    from django.conf import settings
    from mysite.att.models import LeaveClass,AttException,attShifts,EmpSpecDay
    if settings.ATT_CALCULATE_NEW:
        from mysite.att.report_utils import NormalAttValue
    else:
        from mysite.iclock.datas import NormalAttValue
    try:
        if Exception:
            t=[long(i) for i in Exception.split(",")]
            ex=AttException.objects.filter(UserID=UserID,pk__in=t)
        else:
            ex=""
        if ex:
            val={}
            for e  in ex:
               #l=LeaveClass.objects.get(pk=e.ExceptionID)
               l=EmpSpecDay.objects.get(pk=e.ExceptionID).leaveclass
               k=u"%s"%l.LeaveName
               ad=attShifts.objects.filter(AttDate=AttDate,UserID=UserID) 
               atttime=0
               for a  in ad:
                    atttime=atttime+a.AttTime
               if not val.has_key( k):
                  
                  val[k]=NormalAttValue(e.InScopeTime,l.MinUnit,l.Unit,l.RemaindProc,1,atttime)
               else:
                  val[k]=float(val[k])+float(NormalAttValue(e.InScopeTime,l.MinUnit,l.Unit,l.RemaindProc,1,atttime))
            return ";".join([u"%s:%s"%(k,v) for k,v in val.items()])
        else:
            return ""
    except:
        import traceback;traceback.print_exc();

def formatdTime(value):
    if value=='' or value==0:
        return value
    #print "value:%s type:%s"%(value,type(value))
    t='%s:%.2d'%(int(float(value)/60),int(float(value)%60))
    return t

(auDay, auHour, auMinute, auWorkDay, auTimes)=range(5) #考勤计算单位
(rmTrunc, rmRound, rmUpTo, rmCount)=range(4)

def NormalAttValue(Value, MinUnit,AttUnit, RemaindProc,WorkdayFlag=auHour,minsworkday=480):
    '''
    请假值的处理
    MinUnit    最小值
    AttUnit    单位
    RemaindProc    舍入控制类型
    WorkdayFlag 是否为工作日
    minsworkday    时段分钟数之和
    '''
    from mysite.att.calculate.global_cache import C_ATT_RULE
    from decimal import ROUND_HALF_UP,Decimal
    AttRule=C_ATT_RULE.value
    Result=0
    if Value=='null':
        return Value
    if Value=='':
        return Value
    if MinUnit < 0.01:
        MinUnit = 0.01
    ''' 确定度量除数 '''    
    if (Value > 0) and (AttUnit == auTimes):    #次数
        Result = 1
        return Result
    elif AttUnit == auTimes:
        Result = 0
        return Result
    else:
        if AttUnit==auDay:  #天
            MinsUnit=1*24*60*60
        elif AttUnit==auWorkDay:    #工作日
            AttRule['MinsWorkDay1']=minsworkday #不明确
            if WorkdayFlag!=auWorkDay:
                MinsUnit = AttRule['MinsWorkDay1']  ######时段分钟数之和
            else:
                MinsUnit=MinUnit
        elif AttUnit==auHour:   #小时
            MinsUnit=60*60
        elif AttUnit==auMinute: #分钟
            MinsUnit=1*60
    Value=float(Value)
    MinsUnit=float(MinsUnit)
    if MinsUnit==0:
        MinsUnit=float(minsworkday)
    '''度量转化'''
    if WorkdayFlag!=auWorkDay:
        Value = Value/MinsUnit
    '''各类型舍入控制 '''       
    if RemaindProc==rmTrunc:
        c = int(Value/MinUnit)
    elif RemaindProc==rmUpTo:
        c = int(Value/MinUnit)
        if Value>MinUnit*c:
            c +=1
    elif RemaindProc==rmRound:
        c = round(Value/MinUnit)
    if RemaindProc!=rmCount:
        Result = c*MinUnit
    else:
        Result=round(Value*100)/100
    '''格式化最后结果并返回'''
    r=Decimal(str(Result))
    return str(r.quantize(Decimal('0.0'),ROUND_HALF_UP))

#汇总统计数据
def SaveValue(dictv,value):
    '''
    汇总数据
    '''
    from decimal import ROUND_HALF_UP,Decimal
    if value==None or value=="" or value=='null':
        value=0
    if dictv==None or dictv=="" or dictv=='null':
        dictv=0
    if type(value)==type(1):
        value=int(value)
    else:
        value=float(value)
    Result=""
    dictv=float(dictv)
    if dictv+value==0:
        return '0.0'
    else:
        Result=dictv+value
        return str(Decimal(str(Result)).quantize(Decimal('0.0'),ROUND_HALF_UP))