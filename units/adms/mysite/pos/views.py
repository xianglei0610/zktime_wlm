#coding=utf-8

from mysite.settings import MEDIA_ROOT
from base import get_all_app_and_models
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from dbapp.utils import getJSResponse
from django.utils.encoding import smart_str
from django.utils.simplejson  import dumps 
from django.utils import simplejson 

from base.models import AppOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required, login_required
from  datetime   import datetime,date,time,timedelta
#from report import pos_danne,get_pos_record,get_add_record,get_subsidies_record,get_diningcalculate_record
#from report import funPosReport
from pos_reports import posStatisticalReports,get_ic_list_record,pos_list_Reports,get_id_list_record
from dbapp.datalist import save_datalist
from mysite.pos.pos_utils import LoadPosParam
from django.db import transaction
from  decimal import Decimal
from mysite.utils import get_option
#import datetime
@login_required
def consumeReport(request):
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    from mysite.pos.models import CarCashSZ
    from mysite.settings import MEDIA_ROOT
    from mysite.personnel.models.model_emp import EmpMultForeignKey,EmpPoPMultForeignKey
    from mysite.utils import GetFormField
    request.dbapp_url=dbapp_url
    apps=get_all_app_and_models()
    export=True
    empfield = EmpPoPMultForeignKey(verbose_name=_(u'人员'),blank=True,null=False)
    m_emp = GetFormField("emp",empfield) 
    return render_to_response('consumeReport.html', RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps, 
        "current_app":"pos",
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        
        "position": _(u'消费->消费报表'),
        #'item_list':item_list,
        #"model_name": consumeAppReport._model_name,
        "menu_focus": "consumeAppReport",
        "help_model_name":_(u'consume'),
        'export_perm':'export_name',
        'empfield':m_emp,
    }))
    

   
#消费设备管理
@login_required
def funPosDeviceDataManage(request):
       from dbapp.urls import dbapp_url
       from base import get_all_app_and_models
       request.dbapp_url =dbapp_url
       apps=get_all_app_and_models()
       return render_to_response('pos_DeviceDataManage.html',
               RequestContext(request,{
                       'dbapp_url': dbapp_url,
                       'MEDIA_URL':MEDIA_ROOT,
                       "current_app":'pos', 
                       'apps':apps,
                       "help_model_name":"DeviceDataManage",
                       "myapp": [a for a in apps if a[0]=="pos"][0][1],
                       'app_label':'pos',
                       'model_name':'Device',
                       'menu_focus':'PosDeviceDataManage',
                       'position':_(u'消费->消费设备管理'),
                       })        
               )

#导航
@login_required
def funPosGuide(request):
       from dbapp.urls import dbapp_url
       from base import get_all_app_and_models
       request.dbapp_url =dbapp_url
       apps=get_all_app_and_models()
       return render_to_response('pos_guide.html',
               RequestContext(request,{
                       'dbapp_url': dbapp_url,
                       'MEDIA_URL':MEDIA_ROOT,
                       "current_app":'pos', 
                       'apps':apps,
                       "myapp": [a for a in apps if a[0]=="pos"][0][1],
                       'app_label':'pos',
                       'menu_focus':'pos_guide',
                       'position':_(u'消费->导航'),
                       })        
               )
            
            
def funposParamSetting(request):
    la = LoadPosParam(True)
    qs = la.copy()
    return getJSResponse(smart_str(dumps(qs)))

#IC卡根据卡类验证卡余额
def blance_valid(type,newblance,user):
    try:
       from mysite.personnel.models.model_iccard import ICcard
       iccardobj= ICcard.objects.filter(pk=type)        
       lessmoney = iccardobj[0].less_money#卡类最小余额
       maxmoney = iccardobj[0].max_money#卡类最大余额
       if lessmoney>newblance and lessmoney>0:
            return getJSResponse("result=OUT_LESSMONEY")
       elif newblance>maxmoney and maxmoney>0:
            return getJSResponse("result=OUT_MAXMONEY")
       else:
            return "OK"
    except:
        import traceback;traceback.print_exc()


def funSavePosParamSetting(request):
    from mysite.pos.models import PosParam
    from mysite.personnel.models.model_issuecard import IssueCard
    obj = request.POST
    if IssueCard.objects.filter(sys_card_no__isnull=False).count() > 0:
        return getJSResponse("result=2")
    elif obj['system_pwd'] <> obj['pwd_again']:
        return  getJSResponse("result=1")
    elif obj['system_pwd'] == '123456':
        return  getJSResponse("result=3")
    elif len(obj['system_pwd']) <> 6:
        return  getJSResponse("result=4")
    
    else:
        try:
            pa = PosParam.objects.get(id=obj['param_id'])
            pa.max_money = obj['max_money']
            pa.main_fan_area = obj['main_fan_area']
            pa.minor_fan_area = obj['minor_fan_area']
            pa.system_pwd =  obj['system_pwd']
            pa.pwd_again =  obj['pwd_again']
            pa.save()
            objparam = PosParam.objects.get(id=obj['param_id'])
            request.session['obj_param'] = objparam
        except:
#            import traceback;traceback.print_exc()
            return getJSResponse("result=FAIL")
        return getJSResponse("result=0")
#修改卡资料
def funChangeCardInfo(request):
    from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE,CARD_VALID,POS_CARD
    from mysite.personnel.models.model_iccard import ICcard
    obj = request.POST
    request.session.save()
    sys_card_no = obj['sys_card_no']
    card_type = obj['type']
    pwd = obj['Password']
    issue_date = obj['issue_date']
    objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
    try:
        objIccard = ICcard.objects.get(pk=card_type)
    except:
        import traceback;traceback.print_exc()
        pass
    try:  
        iscardate = datetime.strptime(issue_date,'%Y-%m-%d').date();
        nowtime = datetime.now().date()
        daycount = (nowtime-iscardate).days
        maxday = objIccard.use_date
        if maxday>=daycount or maxday==0:
            objcard.cardstatus=CARD_VALID
        if daycount>maxday and maxday >0:
            objcard.cardstatus=CARD_OVERDUE
       
        objcard.type_id = card_type
        objcard.Password = pwd
        objcard.issuedate = iscardate
        objcard.save()
        return getJSResponse("result=OK")
    except:
        import traceback;traceback.print_exc()
        return getJSResponse("result=FAIL")
        pass

#验证卡的有效性
def funValidCard(request):
    from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE,CARD_VALID,POS_CARD
    from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
    obj = request.POST
    operate_type = obj['operate_type']
    if operate_type == '12':#换卡
        sys_card_no = obj['old_sys_card_no']
    elif operate_type in ['8','1']: #修改卡资料
        sys_card_no = obj['sys_card_no']
    try:
        objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
    except:
        return getJSResponse("result=Not_REGISTER_CARD")
    if objcard:
        if objcard.card_privage == PRIVAGE_CARD:
            return getJSResponse("result=PRIVAGE_CARD")
        elif operate_type == '12' and objcard.cardstatus in [CARD_OVERDUE,CARD_VALID]:
            return getJSResponse("result=CARD_OVERDUE_VALID")
        elif objcard.UserID.status == STATUS_LEAVE:
            return getJSResponse("result=STATUS_LEAVE")
        elif objcard.cardstatus ==CARD_STOP:
            return getJSResponse("result=CARD_STOP")
        elif operate_type <> '12' and objcard.cardstatus ==CARD_LOST:
            return getJSResponse("result=CARD_LOST")
        else:
            return getJSResponse("result=OK")
        
def get_pin(self):
        from mysite.personnel.models.model_emp import getuserinfo
        return getuserinfo(self.pk,"PIN")
          
def get_ename(self):
    from mysite.personnel.models.model_emp import getuserinfo
    return getuserinfo(self.pk,"EName")
def get_dept_name(self):
    u'''从缓存中得到部门的Name'''
    from mysite.personnel.models import Department
    dept_name=""
    try:
        dept_obj=Department.all_objects.get(id=self.DeptID_id)
        dept_name=dept_obj.name
    except:
        pass
    return dept_name

#IC保存充值，退款，退卡备份数据
@transaction.commit_on_success    
def funIssueCardBakSave(request):
    from mysite.pos.models.model_cardcashszbak import CarCashSZBak
    from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE
    obj = request.POST
    request.session.save()
    try:
        card = int(obj['card'])
        money = obj['money']
        card_serial_no = int(obj['card_serial_no']) 
        operate_type = obj['operate_type']
        sys_card_no = obj['sys_card_no']
        if operate_type in ['1','5']:
            card_new_blance = obj['op_card_blance']     
        if operate_type == '4':#退卡
            card_blance = Decimal(obj['card_blance'])
        objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
        if objcard:
            if objcard.card_privage == PRIVAGE_CARD and operate_type == '1':
                return getJSResponse("result=PRIVAGE_CARD")
            elif objcard.cardstatus == CARD_LOST and operate_type == '1':
                return getJSResponse("result=CARD_LOST")
            elif objcard.cardstatus ==CARD_STOP and operate_type == '1':
                return getJSResponse("result=CARD_STOP")
            elif objcard.cardstatus ==CARD_OVERDUE and operate_type == '1':
                return getJSResponse("result=CARD_OVERDUE")
            else:
                newblance = 0
                if operate_type == '5':#退款
                    newblance = Decimal(card_new_blance)
                    card_serial_no+=1
                    re_valid = blance_valid(objcard.type_id,newblance,objcard.UserID)#验证余额
                    if  not re_valid == "OK":
                        return re_valid
                if operate_type == '1':#充值
                    newblance = Decimal(card_new_blance)
                    re_valid = blance_valid(objcard.type_id,newblance,objcard.UserID)
                    if not re_valid == "OK":
                        return re_valid
                if operate_type == '8':#手工补消费
                    card_serial_no+=1
                    c_blance = Decimal(obj['blance'])
                    newblance = c_blance - Decimal(money)
                    re_valid = blance_valid(objcard.type_id,newblance,objcard.UserID)
                    if not re_valid == "OK":
                        return re_valid
                if operate_type == '4' and card_blance > 0:
                    card_serial_no+=1
                    CarCashSZBak(user_pin = get_pin(objcard.UserID),
                          user_name = get_ename(objcard.UserID),
                          user_dept_name = get_dept_name(objcard.UserID),
                          physical_card_no = card,
                          sys_card_no = sys_card_no,
                          checktime = datetime.now(),
                          money = card_blance,
                          blance = 0,
                          cardserial = card_serial_no,
                          hide_column = 5).save()
                    
                CarCashSZBak(user_pin = get_pin(objcard.UserID),
                          user_name = get_ename(objcard.UserID),
                          user_dept_name = get_dept_name(objcard.UserID),
                          physical_card_no = card,
                          sys_card_no = sys_card_no,
                          checktime = datetime.now(),
#                          type_id = operate_type,#charge type
                          money = money,
                          blance = newblance,
                          cardserial = card_serial_no,
                          hide_column = operate_type).save()
                return getJSResponse("result=OK")
    except:
        import traceback;traceback.print_exc()
        return getJSResponse("result=FAIL")
        

#发管理卡.操作卡
@transaction.commit_on_success 
def funSaveCardmanage(request):
    from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,POS_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE,CARD_VALID
    from mysite.iclock.models.dev_comm_operate import update_pos_device_info
    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
    from mysite.pos.models.model_cardmanage import CardManage
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.pos.pos_constant import TIMEOUT
    from django.core.cache import cache
    obj = request.POST
    request.session.save()
    card_privage = obj['card_privage']
    card = int(obj['cardno'])
    sys_card_no = obj['sys_card_no']
    pwd = obj['Password']
    dining_id = obj['dining']
    try:
        if IssueCard.objects.get(cardno=card):
            return getJSResponse("result=ISUSE")#卡号已经使用
    except:
        pass
    try:
        if IssueCard.objects.get(sys_card_no = sys_card_no):
            return getJSResponse("result=SYS_ISUSE")#卡账号重复
    except:
        pass
    try:
        CardManage(card_no = card,
        pass_word = pwd,
        dining_id = dining_id,
        cardstatus = CARD_VALID,
        sys_card_no = sys_card_no,card_privage = card_privage).save()
        IssueCard(
            cardno = card,
            sys_card_no = sys_card_no,
            cardstatus = CARD_VALID,
            card_privage = card_privage,
            Password = pwd,type = None ).save()
        dev = Device.objects.filter(device_type = DEVICE_POS_SERVER,dining = Dininghall.objects.get(pk=dining_id))
        objcard = IssueCard.objects.get(sys_card_no = sys_card_no)
        update_pos_device_info(dev,[objcard],"USERINFO")
        return getJSResponse("result=OK")
    except:
        cache.delete("IC_Card_Count")
        import traceback;traceback.print_exc()
        return getJSResponse("result=FAIL")
    
#IC保存发卡备份数据
@transaction.commit_on_success    
def funIssueAddCardBakSave(request):
    from mysite.pos.models import CarCashSZBak, CarCashType
    from mysite.personnel.models.model_emp import Employee    
    from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,POS_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE,CARD_VALID
    obj = request.POST
    request.session.save()
    try:
        if obj.has_key("UserID"):
            user_id = obj['UserID']
            emp = Employee.objects.get(id=user_id)
        else:
             user_pin = obj['user_pin']
             try:
                emp = Employee.objects.get(PIN=user_pin)
             except:
                return getJSResponse("result=EMP_LEAVE")#该人员已经离职
                pass
        card = int(obj['cardno'])
        money = Decimal(obj['blance'])
        card_serial_no = obj['card_serial_no'] 
        operate_type = obj['operate_type']
        sys_card_no = obj['sys_card_no']
        type = obj['type']
    except:
          import traceback;traceback.print_exc()
          pass
    try:
        obj = IssueCard.objects.filter(UserID = emp,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD,sys_card_no__isnull=False)
        if obj:
             return getJSResponse("result=HAVECARD")#该人员已有有效卡在使用
    except:
        pass
    try:
        if IssueCard.objects.get(cardno=card,sys_card_no__isnull=False):
            return getJSResponse("result=ISUSE")#卡号已经使用
    except:
        pass
    try:
       emp_card = IssueCard.objects.get(cardno=card,sys_card_no__isnull=True)
       if emp_card.cardstatus == CARD_LOST:
            return getJSResponse("result=CARD_LOST")#登记的卡号，已经挂失
       if emp_card.cardstatus == CARD_STOP:
            return getJSResponse("result=CARD_STOP")#登记的卡号，已经停用
       
       if emp_card.UserID <> emp:
            return getJSResponse("result=EMPNOTCARD")#卡号登记的人员跟时间发卡的人员不一致
    except:
       pass
    
    try:
        if IssueCard.objects.get(sys_card_no=sys_card_no):
            return getJSResponse("result=SYS_ISUSE")#卡账号号已经使用
    except:
            pass
    
    if operate_type == '12':#换卡
        newblance = 0
        money = 0
    else:
        newblance = money
    try:
        re_valid = blance_valid(type,newblance,emp)
        if re_valid == "OK":
            CarCashSZBak(user_pin = emp.PIN,
                      user_name = emp.EName,
                      user_dept_name = get_dept_name(emp),
                      physical_card_no = card,
                      sys_card_no = sys_card_no,
                      checktime = datetime.now(),
    #                  type_id = operate_type,#charge type
                      money = money,
                      blance = money,
                      cardserial = card_serial_no,
                      hide_column = operate_type).save()
            return getJSResponse("result=OK")
        else:
            return blance_valid(type,newblance,emp)#验证余额
    except:
        import traceback;traceback.print_exc()
        return getJSResponse("result=FAIL")

    
#发卡验证通过保存发卡数据    
@transaction.commit_on_success    
def funIssueAddCardSave(request):
    from mysite.pos.models import CarCashSZ, CarCashType
    from mysite.personnel.models.model_emp import Employee  
    from django.core.cache import cache
    from mysite.pos.pos_constant import TIMEOUT
    from mysite.iclock.models.dev_comm_operate import update_pos_device_info
    from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,PRIVAGE_CARD,POS_CARD,CARD_STOP,CARD_OVERDUE
    obj = request.POST
    request.session.save()
    try:
        if obj.has_key("UserID"):
            user_id = obj['UserID']
            emp = Employee.objects.get(id=user_id)
        else:
            user_pin = obj['user_pin']
            emp = Employee.objects.get(PIN=user_pin)
        card = int(obj['cardno'])
        money = Decimal(obj['blance'])
        card_serial_no = obj['card_serial_no'] 
        operate_type = obj['operate_type']
        sys_card_no = obj['sys_card_no']
        type = obj['type']
        card_cost = obj['card_cost']
        mng_cost = obj['mng_cost']
        card_privage = obj['card_privage']
        pwd = obj['Password']
        newblance = money
        if operate_type == '12':#换卡
            newblance = 0
            from mysite.pos.models import ReplenishCard
            old_sys_card_no = obj['old_sys_card_no']
            ReplenishCard(user=emp,
                       oldcardno=old_sys_card_no,
                       newcardno=sys_card_no,
                       blance=0).save()
            objcard = IssueCard.objects.get(sys_card_no=old_sys_card_no)
            objcard.cardstatus = CARD_STOP
            objcard.save()
            IssueCard(UserID = emp,
               cardno = card,
               sys_card_no = sys_card_no,
               cardstatus = CARD_VALID,
               card_privage = POS_CARD,
               card_cost = card_cost,
               mng_cost = mng_cost,
               issuedate = datetime.now().date(),
               type_id = type,blance = 0,Password = pwd,card_serial_num=card_serial_no ).save()
#            cache.set("IC_Card_Count",sys_card_no,TIMEOUT)
            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
            update_pos_device_info(dev,[objcard],"USERINFO")#下发原卡为黑名单
            new_objcard = IssueCard.objects.get(sys_card_no = sys_card_no)
            update_pos_device_info(dev,[new_objcard],"USERINFO")#下发白名单卡
        else:#发卡
            obj = IssueCard.objects.filter(UserID = emp,cardstatus__in = [CARD_OVERDUE,CARD_VALID],card_privage = POS_CARD,sys_card_no__isnull=True)
            if obj:
                obj[0].type_id = type
                obj[0].blance = money
                obj[0].Password = pwd
                obj[0].sys_card_no = sys_card_no
                obj[0].cardno = card
                obj[0].card_cost = card_cost
                obj[0].mng_cost = mng_cost 
                obj[0].card_serial_num = 1
                obj[0].issuedate = datetime.now().date() 
                obj[0].create_time = datetime.now()
                obj[0].save(force_update=True)
#                cache.set("IC_Card_Count",sys_card_no,TIMEOUT)
            else:
                IssueCard(UserID = emp,
                       cardno = card,
                       sys_card_no = sys_card_no,
                       cardstatus = CARD_VALID,
                       card_privage = card_privage,
                       card_cost = card_cost,
                       mng_cost = mng_cost,
                       issuedate = datetime.now().date(),
                       type_id = type,blance = money,Password = pwd,card_serial_num=1 ).save()
#                cache.set("IC_Card_Count",sys_card_no,TIMEOUT)
            objcard = IssueCard.objects.get(sys_card_no = sys_card_no)
            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
            update_pos_device_info(dev,[objcard],"USERINFO")#下发白名单卡
        if card_privage == POS_CARD:
#            blance_valid(type,newblance,emp)#验证余额
            CarCashSZ(user=emp,
                 card = card,
                 checktime = datetime.now(),
                 type_id = 7,#cost type 发卡
                 cardserial = card_serial_no,
                 money = card_cost,
                 sys_card_no = sys_card_no,
                 hide_column = 7,blance = newblance,log_flag = 2 ).save()
            if operate_type <> '12' and money>0:#换卡
                CarCashSZ(user = emp,
                     card = card,
                     sys_card_no = sys_card_no,
                     checktime = datetime.now(),
                     cardserial = card_serial_no,
                     type_id =1,#cost type发卡的时候充值
                     money = money,
                     hide_column = 1,blance = newblance,log_flag = 2).save()
            CarCashSZ(user = emp,
                 card = card,
                 sys_card_no = sys_card_no,
                 checktime = datetime.now(),
                 type_id =11,#cost type 管理费
                 cardserial = card_serial_no,
                 money=mng_cost,
                 hide_column=11,blance=newblance,log_flag = 2).save()
            return getJSResponse("result=OK")
    except:
        import traceback;traceback.print_exc()
        cache.delete("IC_Card_Count");
        return getJSResponse("result=FAIL")


#保存充值.退款.手工补消费数据
@transaction.commit_on_success    
def funIssueCardSave(request):
    from mysite.pos.models import CarCashSZ, CarCashType
    from base.cached_model import STATUS_INVALID,STATUS_LEAVE
    from mysite.personnel.models.model_issuecard import IssueCard,PRIVAGE_CARD,CARD_LOST,CARD_STOP,CARD_OVERDUE,CARD_VALID
    obj = request.POST
    request.session.save()
    card = int(obj['card'])
    operate_type = obj['operate_type']
    money = Decimal(obj['money'])
    sys_card_no = obj['sys_card_no']
    
    card_serial_no = int(obj['card_serial_no']) 
    operate_type = obj['operate_type']
    if operate_type == '8':#手工补消费
        name = obj['name']
        labor = obj['labor']
        meal = obj['meal']
        pos_device = obj['posdevice']
        date = obj['date']
        c_blance = Decimal(obj['blance'])
    if operate_type == '4':#退卡
        card_serial_no+=1
        card_blance = Decimal(obj['card_blance'])
    if operate_type in ['1','5']:#充值、退款
        card_new_blance = obj['op_card_blance']
    objcard=IssueCard.objects.get(sys_card_no = sys_card_no)
    if objcard:
#            blance_valid(objcard.type_id,newblance,objcard.UserID)#验证余额
        try:
            if operate_type == '4':#退卡操作，改变状态为无效
                objcard.status = STATUS_INVALID
                objcard.cardstatus = STATUS_INVALID
                objcard.blance = 0
                objcard.save()
                from mysite.iclock.models.dev_comm_operate import delete_pos_device_info,update_pos_device_info,sync_delete_user,sync_delete_user_privilege,sync_delete_user,sync_report_user
                from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                from mysite.pos.models.model_loseunitecard import LoseUniteCard
                from mysite.personnel.models.model_leave import get_leave_user_info
                dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                delete_pos_device_info(dev,[objcard],"USERINFO")#删除黑白名单
#                update_pos_device_info(dev,[objcard],"USERINFO")#添加黑名单
#                LoseUniteCard.objects.all().filter(UserID = objcard.UserID_id).delete()#删除挂失解挂记录
                if get_option("ATT") and not get_leave_user_info(objcard.UserID_id,"isClassAtt"):
                    from base.sync_api import SYNC_MODEL
                    if not SYNC_MODEL:
                        from mysite.iclock.models.model_cmmdata import adj_user_cmmdata
                        adj_user_cmmdata(objcard.UserID, [], objcard.UserID.attarea.all())
                    
                if get_option("IACCESS") and not get_leave_user_info(objcard.UserID_id,"isClassAccess"):
                        from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege               
                        newObj=objcard.UserID
                        accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
                        sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
                    
            else:
                if operate_type == '5' or operate_type == '1':#退款,充值
                    card_serial_no+=1
                    newblance = card_new_blance
                else:#手工补消费
                    card_serial_no+=1
                    newblance = c_blance - money
                objcard.blance = newblance
                objcard.card_serial_num = card_serial_no
                objcard.save()
                
            if operate_type == '8':#手工补消费
                from mysite.pos.models.model_handconsume import HandConsume
                HandConsume(
                card = card,
                sys_card_no = sys_card_no,
                blance = objcard.blance,
                name = name,
                labor = labor,
                meal_id = meal,
                posdevice_id = pos_device,
                money = money,date=date,card_serial_no = card_serial_no ).save()
            if operate_type == '4' and card_blance >0 :
                CarCashSZ(user = objcard.UserID,
                     card = card,
                     checktime = datetime.now(),
                     type_id = 5,#charge type
                     money = card_blance,
                     blance = 0,
                     sys_card_no = sys_card_no,
                     cardserial = card_serial_no,
                     hide_column = 5,log_flag = 2).save()
            if operate_type <> '8':
                CarCashSZ(user = objcard.UserID,
                      card = card,
                      checktime = datetime.now(),
                      type_id = operate_type,#charge type
                      money = money,
                      blance = objcard.blance,
                      sys_card_no = sys_card_no,
                      cardserial = card_serial_no,
                      hide_column = operate_type,log_flag = 2).save()
            return getJSResponse("result=OK")
        except:
            import traceback;traceback.print_exc()
            return getJSResponse("result=FAIL")
            


##消费卡管理   
#@login_required
#def funPosCarManage(request):
#       from dbapp.urls import dbapp_url
#       from base import get_all_app_and_models
#       request.dbapp_url =dbapp_url
#       apps=get_all_app_and_models()
#       return render_to_response('pos_CarDataManage.html',
#               RequestContext(request,{
#                       'dbapp_url': dbapp_url,
#                       'MEDIA_URL':MEDIA_ROOT,
#                       "current_app":'pos', 
#                       'apps':apps,
#                       "help_model_name":"CarManage",
#                       "myapp": [a for a in apps if a[0]=="pos"][0][1],
#                       'app_label':'pos',
#                       'model_name':'IssueCard',
#                       'menu_focus':'PosCarManage',
#                       'position':_(u'消费->消费卡管理  '),
#                       })        
#               )
#       

     
def get_diningroom(request):
    select_dininghall= request.REQUEST.get("dininghall", "")
    from mysite.iclock.models.model_dininghall import Dininghall
    from mysite.personnel.models.model_meal import Meal
    from django.contrib.auth.models import User
    from mysite.pos.models.model_cardmanage import CardManage
    from mysite.utils import get_option
    if select_dininghall:
       pass
    else:
        halls= Dininghall.objects.all().order_by('id').values_list('id','code','name')
        meals=Meal.objects.all().order_by('id').values_list('id','code','name')
        operates=User.objects.all().exclude(username = 'employee').order_by('id').values_list('id','username')
        if get_option("POS_IC"):
            operate_card = CardManage.objects.all().order_by('id').values_list('id','sys_card_no')
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all', 'operate_card':[op_card for op_card in operate_card],'operates':[operate for operate in operates],'meals':[meal for meal in meals],'halls': [hall for hall in halls]})))
        else:
            return getJSResponse(smart_str(simplejson.dumps({ 'type': 'all','operates':[operate for operate in operates],'meals':[meal for meal in meals],'halls': [hall for hall in halls]})))
            
@login_required
def fun_posreport(request):
    '''
    消费 报表
    '''
    from dbapp.urls import dbapp_url
    from base import get_all_app_and_models
    from mysite.pos.models import CarCashSZ
    from mysite.settings import MEDIA_ROOT
    from mysite.personnel.models.model_emp import EmpMultForeignKey,EmpPoPMultForeignKey
    from mysite.utils import GetFormField
    request.dbapp_url=dbapp_url
    apps=get_all_app_and_models()
    export=True    
    empfield = EmpPoPMultForeignKey(verbose_name=_(u'人员'),blank=True,null=True)
    m_emp = GetFormField("emp",empfield) 
    
    return render_to_response('posreport.html', RequestContext(request,{
        "app_label": "pos",
        "dbapp_url": dbapp_url,
        "MEDIA_ROOT": MEDIA_ROOT,
        "apps": apps, 
        "current_app":"pos",
        "myapp": [a for a in apps if a[0]=="pos"][0][1],
        
        "position": _(u'消费->统计报表'),
        #'item_list':item_list,
        #"model_name": consumeAppReport._model_name,
        "menu_focus": "PosReport",
        "help_model_name":_(u'report'),
        'export_perm':'export_name',
        'empfield':m_emp,
    }))
    

#@login_required
#def get_posreport(request):
#    '''
#    消费 原始记录表 ，前台传递过来的值有：
#    人员id、部门id、开始时间、结束时间、餐厅
#    '''
#    deptids=request.POST.get('DeptIDs',"")
#    userids=request.POST.get('UserIDs',"")
#    dining=request.POST.get('Dining',"")
##    type=request.GET.get('type','')
# 
#    st=request.POST.get('ComeTime','')
#    et=request.POST.get('EndTime','')
#    st=datetime.strptime(st,'%Y-%m-%d')
#    et=datetime.strptime(et,'%Y-%m-%d')
#    et=et+timedelta(days=1)
#    allr=get_pos_record(request,deptids,userids,st,et,False)    
#    loadall=request.REQUEST.get('pa','T')
#    if not loadall:
#       objdata={}
#       allr=get_pos_record(request,deptids,userids,st,et,True)
#       objdata['data']=allr['datas']
#       objdata['fields']=allr['fieldnames']
#       heads={}
#       for i  in  range(len(allr['fieldnames'])):
#           heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
#       objdata['heads']=heads
#       tmp_name=save_datalist(objdata)
#       allr['tmp_name']=tmp_name
#   
#    return getJSResponse(smart_str(simplejson.dumps(allr)))

#@login_required
#def get_addreport(request):
#    '''
#    消费 原始记录表 ，前台传递过来的值有：
#    人员id、部门id、开始时间、结束时间、餐厅
#    '''
#    deptids=request.POST.get('DeptIDs',"")
#    userids=request.POST.get('UserIDs',"")
#    dining=request.POST.get('Dining',"")
##    type=request.GET.get('type','')
# 
#    st=request.POST.get('ComeTime','')
#    et=request.POST.get('EndTime','')
#    st=datetime.strptime(st,'%Y-%m-%d')
#    et=datetime.strptime(et,'%Y-%m-%d')
#    et=et+timedelta(days=1)
#    allr=get_add_record(request,deptids,userids,st,et,False)    
#    loadall=request.REQUEST.get('pa','T')
#    if not loadall:
#       objdata={}
#       allr=get_add_record(request,deptids,userids,st,et,True)
#       objdata['data']=allr['datas']
#       objdata['fields']=allr['fieldnames']
#       heads={}
#       for i  in  range(len(allr['fieldnames'])):
#           heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
#       objdata['heads']=heads
#       tmp_name=save_datalist(objdata)
#       allr['tmp_name']=tmp_name
#   
#    return getJSResponse(smart_str(simplejson.dumps(allr)))



@login_required    
def get_ic_pos_record(request):
    '''
    消费明细
    '''
    deptids=request.POST.get('DeptIDs',"")
    userids=request.POST.get('UserIDs',"")
    dining=request.POST.get('Dining',"")
#    type=request.GET.get('type','')
 
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')
    st=datetime.strptime(st,'%Y-%m-%d')
    et=datetime.strptime(et,'%Y-%m-%d')
    operate=request.REQUEST.get('operate','')
    et=et+timedelta(days=1)
    pos_model =  request.REQUEST.get('pos_model','')
    dining =  request.REQUEST.get('dining','')
    loadall=request.REQUEST.get('pa','')
    if loadall:
        if get_option("POS_IC"):
            allr=get_ic_list_record(request,deptids,userids,dining,st,et,pos_model,operate,True)
        else:
            allr=get_id_list_record(request,deptids,userids,dining,st,et,pos_model,operate,True)
    else:
        if get_option("POS_IC"):
            allr=get_ic_list_record(request,deptids,userids,dining,st,et,pos_model,operate)
        else:
            allr=get_id_list_record(request,deptids,userids,dining,st,et,pos_model,operate)
    objdata={}
#    allr=get_ic_list_record(request,deptids,userids,st,et,pos_model,operate)
    objdata['data']=allr['datas']
    objdata['fields']=allr['fieldnames']
    heads={}
    for i  in  range(len(allr['fieldnames'])):
       heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
#    objdata['heads']=heads
#    tmp_name=save_datalist(objdata)
#    allr['tmp_name']=tmp_name
   
    return getJSResponse(smart_str(simplejson.dumps(allr)))

@login_required  
def posreport(request):
    '''
    消费统计报表入口点 开始统计  typeid为统计报表类型
    # 报表类型  
    #    110 表示  餐厅汇总表 
    #    120 表示  部门汇总
    #    130 表示  个人消费汇总表
    #    140 表示  设备汇总
    #    150 表示  收支统计
    
    '''
    deptids=request.POST.get('DeptIDs',"")
    userids=request.POST.get('UserIDs',"")
    dining=request.POST.get('Dining',"")
    meal = request.POST.get('Meal','')
    operate=request.GET.get('Operate','')
    
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')
    st=datetime.strptime(st,'%Y-%m-%d')
    et=datetime.strptime(et,'%Y-%m-%d')
    et=et+timedelta(days=1)
    typeid=request.GET.get('type','')#统计报表
    pos_model =  request.REQUEST.get('pos_model','')
    check_opreate =  request.REQUEST.get('check_operate','')
    loadall=request.REQUEST.get('pa','')
    if loadall: #分页查询
        allr=posStatisticalReports(request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,check_opreate,True)
    else:
        allr=posStatisticalReports(request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,check_opreate)
    #导出 的时候 需要
    objdata={}
#    allr=posStatisticalReports(request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,check_opreate,True)
    objdata['data']=allr['datas']
    objdata['fields']=allr['fieldnames']
    heads={}
    for i  in  range(len(allr['fieldnames'])):
       heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
    objdata['heads']=heads
#    tmp_name=save_datalist(objdata)
#    allr['tmp_name']=tmp_name
    return getJSResponse(smart_str(simplejson.dumps(allr)))





@login_required  
def pos_list_report(request):
    '''
    消费报表入口点 开始统计  typeid为统计报表类型
    # 报表类型  
    #    13 表示  发卡表 
    #    1 表示  充值表
    #    4 表示  退卡表
    #    5 表示  退款表
    #    2 表示  补贴表
    #    12 表示  卡余额表
    #    7 表示	卡成本表
    #    14 表示	消费异常明细表
    '''
    deptids=request.POST.get('DeptIDs',"")
    userids=request.POST.get('UserIDs',"")
    dining=request.POST.get('Dining',"")
    meal = request.POST.get('Meal','')
    operate=request.GET.get('operate','')
    st=request.POST.get('ComeTime','')
    et=request.POST.get('EndTime','')
    st=datetime.strptime(st,'%Y-%m-%d')
    et=datetime.strptime(et,'%Y-%m-%d')
    et=et+timedelta(days=1)
    typeid=request.GET.get('type','')#统计报表
    pos_model =  request.REQUEST.get('pos_model','')
    check_opreate =  request.REQUEST.get('check_operate','')
    loadall=request.REQUEST.get('pa','')
    if loadall: #分页查询
        allr=pos_list_Reports(request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,check_opreate,True)
    else:
        allr=pos_list_Reports(request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,check_opreate)
    #导出 的时候 需要
    objdata={}
#    allr=posStatisticalReports(request,deptids,userids,st,et,dining,meal,typeid,operate,pos_model,check_opreate,True)
    objdata['data']=allr['datas']
    objdata['fields']=allr['fieldnames']
    heads={}
    for i  in  range(len(allr['fieldnames'])):
       heads[allr['fieldnames'][i]]=allr['fieldcaptions'][i]
    objdata['heads']=heads
#    tmp_name=save_datalist(objdata)
#    allr['tmp_name']=tmp_name
    return getJSResponse(smart_str(simplejson.dumps(allr)))

 
 

    