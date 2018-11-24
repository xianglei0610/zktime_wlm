#! /usr/bin/env python
#coding=utf-8

from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from model_emp import LEAVETYPE,YESORNO
from base.cached_model import  STATUS_OK,STATUS_INVALID,STATUS_LEAVE
from dbapp import dataviewdb, data_edit
from mysite.personnel.models.model_emp import Employee,EmpForeignKey,EmpMultForeignKey,EmpPoPForeignKey,EmpPoPMultForeignKey



from django.conf import settings
from mysite import settings as st
from mysite.utils import get_option
init_settings = []
if settings.APP_CONFIG["remove_permision"]:
    init_settings = [ k.split(".")[1] for k,v in settings.APP_CONFIG["remove_permision"].items() if v=="False" and k.split(".")[0]=="LeaveLog"]
    
#acc=[]
#if get_option("IACCESS"):#zkeco+iaccess
#    acc=["isClassAccess",]
               

class LeaveLog(CachingModel):
        """
        离职操作
        """
        UserID=EmpPoPForeignKey(verbose_name=_(u"人员"),null=False,editable=True)
        leavedate=models.DateField(verbose_name=_(u'离职日期'),editable=True)
        leavetype=models.IntegerField(verbose_name=_(u'离职类型'),choices=LEAVETYPE,editable=True)
        reason=models.CharField(verbose_name=_(u'离职原因'),max_length=200,null=True,blank=True,editable=True)        
        isReturnTools =models.BooleanField(verbose_name=_(u'是否归还工具'),choices=YESORNO, null=False,default=True,  editable=True)
        isReturnClothes=models.BooleanField(verbose_name=_(u'是否归还工衣'),choices=YESORNO, null=False,default=True,  editable=True)
        isReturnCard=models.BooleanField(verbose_name=_(u'是否归还卡'),choices=YESORNO, null=False,default=True, editable=True)
        isClassAtt=models.BooleanField(verbose_name=_(u'立即关闭考勤'),choices=YESORNO, null=False,default=0, editable=False)
        isClassAccess=models.BooleanField(verbose_name=_(u'立即关闭门禁'),choices=YESORNO, null=False,default=0, editable=False)
        is_close_pos=models.BooleanField(verbose_name=_(u'立即关闭消费'),choices=YESORNO, null=False,default=0, editable=False)
        
        def __unicode__(self):
                from mysite.personnel.models import Employee
                emp=""
                try:
                    Employee.can_restore=True
                    emp=Employee.objects.get(pk=self.UserID_id)
                    Employee.can_restore=False
                except:
                    return ""
                
                return emp.PIN +"  "+ (emp.EName and u" %s"%emp.EName or "")
        def save(self):
                try:    
#                    from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP
#                    iscard = IssueCard.objects.filter(UserID=self.UserID,cardstatus = CARD_VALID)
#                    if get_option("POS"):#zkeco+pos
#                        if iscard and self.is_close_pos:#立即关闭消费
#                            iscard[0].cardstatus = CARD_STOP
#                            iscard[0].save(force_update=True)
#                            if get_option("POS_IC") and iscard[0].sys_card_no:
#                                from mysite.iclock.models.dev_comm_operate import update_pos_device_info
#                                from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
#                                dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
#                                update_pos_device_info(dev,[iscard[0]],"USERINFO")
                            
                    super(LeaveLog,self).save()
                    if self.UserID.status==0:            
                        self.UserID.status=STATUS_LEAVE
                        self.UserID.save()
                    
                except Exception,e:
                        raise Exception(e)
                        import traceback;traceback.print_exc()
                        pass
        class _delete(Operation):
            help_text = _(u"删除选定记录") #删除选定的记录
            verbose_name = _(u"删除")
            visible = True
            def action(self):
                from mysite.personnel.models import Employee
                self.object.delete()   
                Employee.all_objects.filter(id=self.object.UserID_id).delete()  
        class OpRestoreEmpLeave(Operation):
                help_text=_(u'恢复离职人员')
                verbose_name=_(u'离职恢复')
                def action(self):
                    import datetime
                    emp=self.object.UserID
                    if emp.isblacklist==1:
                        raise Exception(_(u'黑名单不能处理离职恢复！'))
                    emp.__class__.can_restore=True
                    emp.isblacklist=None
                    emp.status=STATUS_OK
                    emp.Hiredday=datetime.datetime.now().strftime("%Y-%m-%d")
                    emp.save()
                    emp.__class__.can_restore=False
                    #下载到设备
                    newObj=self.object.UserID
                    from mysite.iclock.models.dev_comm_operate import sync_set_userinfo, sync_set_user_privilege, sync_set_acc_user_fingerprint    #-----2012.02.02   xiaoxiaojun                 
                    #sync_set_user(newObj.search_device_byuser(), [newObj])
                    accdev = newObj.search_accdev_byuser() #查询出人员对那些设备具有操作权限
                    sync_set_userinfo(accdev, [newObj])   #同步人员基本信息到设备
                    sync_set_acc_user_fingerprint(accdev, [newObj]) #同步人员指纹信息到设备
                    sync_set_user_privilege(accdev, [newObj]) #下放人员权限到设备
                    from base.sync_api import SYNC_MODEL
                    if not SYNC_MODEL:
                        # 离职恢复
                        from mysite.iclock.models.model_cmmdata import adj_user_cmmdata 
                        adj_user_cmmdata(newObj,[],newObj.attarea.all())
                    self.object.delete()

        class OpCloseAtt(Operation):
                help_text=_(u'关闭考勤')
                verbose_name=_(u'关闭考勤')
                visible = get_option("ATT")
                def action(self):
                    from mysite.iclock.models.dev_comm_operate import sync_delete_user
                    oldObj=self.object.UserID
                    if self.object.isClassAtt==1:
                            raise Exception(_(u"考勤已经关闭！"))                    
                    self.object.isClassAtt=1
                    self.object.save()
                    from base.sync_api import SYNC_MODEL, delete_emp
                    if SYNC_MODEL:
                        if oldObj.isatt:
                            delete_emp(oldObj.PIN)
                    else:
                        devs=oldObj.search_device_byuser()
                        sync_delete_user(devs, [oldObj])
                    
        class OpClosePos(Operation):
            help_text=_(u'关闭消费')
            verbose_name=_(u'关闭消费')
            visible = get_option("POS")
            def action(self):
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_OVERDUE
                from mysite.iclock.models.dev_comm_operate import update_pos_device_info,sync_report_user
                iscard = IssueCard.objects.filter(UserID=self.object.UserID,cardstatus__in = [CARD_VALID,CARD_OVERDUE])
                if self.object.is_close_pos==1:
                    raise Exception(_(u"消费已经关闭！"))
                self.object.is_close_pos=1
                self.object.save()
                if iscard :#立即关闭消费
                    try:
                        if get_option("POS_IC") and iscard[0].sys_card_no:
                            iscard[0].cardstatus = CARD_STOP
                            iscard[0].save(force_update=True)
                            from mysite.iclock.models.model_device import Device,DEVICE_POS_SERVER
                            dev = Device.objects.filter(device_type = DEVICE_POS_SERVER)
                            update_pos_device_info(dev,[iscard[0]],"USERINFO")
#                            if get_option("IACCESS"):
#                                oldObj=iscard[0].UserID
#                                if oldObj.check_accprivilege():
#                                    devs=oldObj.search_accdev_byuser()
#                                    sync_report_user(devs,[oldObj]) 
#                            if get_option("ATT"):
#                                oldObj=iscard[0].UserID
#                                devs=oldObj.search_device_byuser()
#                                sync_report_user(devs, [oldObj])
                        elif get_option("POS_ID"):
                            iscard[0].cardstatus = CARD_STOP
                            iscard[0].save(force_update=True)
#                            if get_option("IACCESS"):
#                                oldObj=iscard[0].UserID
#                                if oldObj.check_accprivilege():
#                                    devs=oldObj.search_accdev_byuser()
#                                    sync_report_user(devs,[oldObj]) 
#                            if get_option("ATT"):
#                                oldObj=iscard[0].UserID
#                                devs=oldObj.search_device_byuser()
#                                sync_report_user(devs, [oldObj])
                    except:
                        import traceback;traceback.print_exc()
                        
        class _change(ModelOperation):
            visible=False
            def action(self):
                pass            
        class OpCloseAccess(Operation):
                help_text=_(u'关闭门禁')
                verbose_name=_(u'关闭门禁')
                visible = get_option("IACCESS")
                def action(self):
                    from mysite.iclock.models.dev_comm_operate import sync_delete_user_privilege,sync_delete_user
                    oldObj=self.object.UserID
                    if oldObj.check_accprivilege():
                        devs=oldObj.search_accdev_byuser()
                        sync_delete_user(devs,[oldObj]) 
                        sync_delete_user_privilege(devs,[oldObj])
                    if self.object.isClassAccess==1:
                        raise Exception(_(u"门禁已经关闭！"))
                    self.object.isClassAccess=1
                    self.object.save()
                    
        def get_pin(self):
            from mysite.personnel.models.model_emp import getuserinfo
            return getuserinfo(self.UserID_id,"PIN")

        def get_ename(self):
            from mysite.personnel.models.model_emp import getuserinfo
            return getuserinfo(self.UserID_id,"EName")

        def get_user_dept(self):
            from mysite.personnel.models.model_emp import getuserinfo
            return getuserinfo(self.UserID_id,"DeptID")

        def get_isblacklist(self):
            from mysite.personnel.models.model_emp import getuserinfo
            isblack = getuserinfo(self.UserID_id,"isblacklist")
            if isblack == 0:
               return _(u'否')
            else:
               return _(u'是') 
                        
        class Admin(CachingModel.Admin):
                sort_fields=["UserID.PIN","leavedate"]
                app_menu="personnel"
                menu_index=5
                visible = get_option("LEAVE_VISIBLE") #not (get_option("IACCESS") and settings.ZKACCESS_ATT and 'en' in dict(settings.LANGUAGES).keys())
                list_filter=('UserID','leavedate','leavetype','isReturnTools','isReturnCard','isReturnClothes')
                query_fields=['UserID__PIN','UserID__EName','leavedate','leavetype','reason']

                list_display=get_option("LEAVE_LIST_DISPLAY")                 
                newadded_column={
                   "UserID.PIN":"get_pin",
                   "UserID.EName":"get_ename",
                   "UserID.DeptID":"get_user_dept",
                   "UserID.isblacklist":"get_isblacklist"
                }
                cache = 3600
                disabled_perms=get_option("LEAVE_DISABLED_PERMS")+init_settings
                help_text=get_option("LEAVE_HELP_TEXT")
#                hide_fields = get_option("LEAVE_DISABLE_COLS")
        class Meta:
                verbose_name=_(u'人员离职')
                verbose_name_plural=verbose_name
                app_label='personnel'


def get_leave_user_info(user_pk,attr):
    u'''取得用户pk为user_pk的属性attr'''
    try:
        emp=LeaveLog.objects.get(UserID=user_pk)
        if hasattr(emp,attr):
            return getattr(emp,attr)
    except:
        pass
    return False


#在表单生成前加入自定义字段 或操作
def detail_resplonse(sender, **kargs):
        from dbapp.templatetags import dbapp_tags
        from mysite.personnel.models.model_emp import Employee
        from dbapp.widgets import form_field, check_limit
        if kargs['dataModel']==LeaveLog:
                form=sender['form']
                #print form.fields
                field = models.BooleanField(_(u'是否黑名单'), choices=YESORNO, default=0)
                form.fields['isblacklist']=form_field(field)
                if get_option("ATT"):
                    closeatt=models.BooleanField(verbose_name=_(u'立即关闭考勤'),default=True)
                    form.fields['opcloseatt']=form_field(closeatt)
                if get_option("IACCESS"):
                    closeacc=models.BooleanField(verbose_name=_(u'立即关闭门禁'),default=True)
                    form.fields['opcloseacc']=form_field(closeacc)
                if get_option("POS"):
                    closepos=models.BooleanField(verbose_name=_(u'立即关闭消费'),default=True)
                    form.fields['opclosepos']=form_field(closepos)
                    
#                field=Employee._meta.get_field('isblacklist')       
data_edit.pre_detail_response.connect(detail_resplonse)        


#在表单提交后，对自定义字段进行处理
def DataPostCheck(sender, **kwargs):
        from mysite.personnel.models.model_emp import device_pin,Employee
        from mysite.iclock.models.modelproc  import getEmpCmdStr
        oldObj=kwargs['oldObj']
        newObj=kwargs['newObj']
        request=sender
        if isinstance(newObj, LeaveLog):
                bl=request.REQUEST.get("isblacklist","")
                att=request.REQUEST.get("opcloseatt","")
                acc=request.REQUEST.get("opcloseacc","") 
                pos=request.REQUEST.get("opclosepos","")                 
                if acc:
                        newObj.OpCloseAccess(newObj).action()
                if bl:
                        newObj.UserID.isblacklist=bl
                        newObj.UserID.save()
                if att:
                        newObj.OpCloseAtt(newObj).action()   
                if pos:
                        newObj.OpClosePos(newObj).action() 
                        
                from mysite.personnel.models.model_issuecard import IssueCard,CARD_VALID,CARD_STOP,CARD_OVERDUE
                iscard = IssueCard.objects.filter(UserID=newObj.UserID,cardstatus__in = [CARD_VALID,CARD_OVERDUE])        
                if not get_option("POS"):
                    if  newObj.isReturnCard==1 and iscard:
                            for e in iscard:e.delete()
                
                        
data_edit.post_check.connect(DataPostCheck)
                