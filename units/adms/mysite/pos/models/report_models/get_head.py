#! /usr/bin/env python
#coding=utf-8
from django.utils.translation import ugettext as _
from mysite.utils import get_option
def get_dining():
    from mysite.iclock.models.model_dininghall import Dininghall
    ids=Dininghall.objects.all().order_by('id').values_list('id','name')

def get_pos_list():
    '''
    IC消费明细显示字段
    '''
    if get_option("POS_IC"):
        r=[]
        FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','money','balance',
        'pos_model','pos_time','dining','meal_id','dev_sn','dev_serial_num','card_serial_num','meal_data','convey_time','create_operator','log_flag']
        FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'消费金额'),_(u'余额'),
        _(u'消费模式'),_(u'消费时间'),_(u'餐厅'),_(u'餐别'),_(u'设备序列号'),_(u'设备流水号'),_(u'卡流水号'),
        _(u'记餐日期'),_(u'上传时间'),_(u'操作员'),_(u'记录标志')]
        for i  in  range(len(FieldNames)):
            r.append((FieldNames[i],FieldCaption[i]))
        return [r,FieldNames,FieldCaption]
    else:
        r=[]
        FieldNames=['user_pin','user_name','dept_name','card','money','balance','discount','type_name',
        'pos_time','dining','dev_sn','dev_serial_num','card_serial_num','create_operator']
        FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'消费金额'),_(u'余额'),_(u'折扣'),_(u'类型名称'),
        _(u'消费时间'),_(u'餐厅'),_(u'设备序列号'),_(u'设备流水号'),_(u'卡流水号'),
        _(u'操作员')]
        for i  in  range(len(FieldNames)):
           r.append((FieldNames[i],FieldCaption[i]))
        return [r,FieldNames,FieldCaption]
        
        
        


def get_posreprots_fields(typeid):
    '''  
     #    1 表示 充值  汇总报表  
     #    2 表示 充值  报表
    3  b补贴
    4 退款
    '''
    r= []
    if typeid=="110" :    # 餐厅汇总 
        if get_option("POS_IC"):
#        FieldNames=['dining_name','breakfast_money','lunch_money','dinner_money','supper_money','back_money','summary_money','pos_date']
#        FieldCaption=[_(u'餐厅名称'),_(u'早餐合计（元）'),_(u'中餐合计（元）'),_(u'晚餐合计（元）'),_(u'夜宵合计（元）'),_(u'纠错金额（元）'),_(u'合计金额（元)'),_(u'消费日期')]
            FieldNames=['dining_name','pos_count','back_count','summary_total_time','error_summary_count','summary_count','meal_money','back_money','add_single_money','error_summary_money','summary_dev_money','summary_money','pos_date']
            FieldCaption=[_(u'餐厅名称'),_(u'餐厅消费总次数'),_(u'纠错总次数'),_(u'计次结算'),_(u'异常消费次数结算'),_(u'扣款消费次数结算（不含异常）'),_(u'餐厅消费总合计'),_(u'纠错合计'),_(u'补单合计'),_(u'异常消费金额结算'),_(u'实消费金额结算（不含异常）'),_(u'系统金额结算（含补单）'),_(u'消费日期')]
        
        else:
            FieldNames=['dining_name','pos_count','meal_money','back_count','back_money','summary_total_time','summary_total_money','add_single_money','summary_count','summary_dev_money','summary_money','pos_date']
            FieldCaption=[_(u'餐厅名称'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数结算'),_(u'计次结算'),_(u'补单合计'),_(u'实消费次数结算'),_(u'设备金额结算'),_(u'系统金额结算（含补单）'),_(u'消费日期')]
            
    elif typeid=="130":#个人消费汇总表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','pos_count','add_single_money','meal_money','back_count','back_money','summary_total_time','summary_count','summary_dev_money','summary_money','pos_date']
            FieldCaption=[_(u'人员编号'),_(u'人员姓名'),_(u'部门名称'),_(u'消费次数'),_(u'补单合计'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次结算'),_(u'实消费次数结算'),_(u'设备金额结算'),_(u'系统金额结算（含补单）'),_(u'消费日期')]
        else:
            FieldNames=['user_pin','user_name','dept_name','pos_count','add_single_money','meal_money','back_count','back_money','summary_total_time','summary_total_money','summary_count','summary_dev_money','summary_money','pos_date']
            FieldCaption=[_(u'人员编号'),_(u'人员姓名'),_(u'部门名称'),_(u'消费次数'),_(u'补单合计'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数结算'),_(u'计次结算'),_(u'实消费次数结算'),_(u'设备金额结算'),_(u'系统金额结算（含补单）'),_(u'消费日期')]
            
    elif typeid=="120": #部门汇总
       if get_option("POS_IC"):
           FieldNames=['dept_name','pos_count','meal_money','back_count','back_money','summary_total_time','summary_count','summary_money','pos_date']
           FieldCaption=[_(u'部门名称'),_(u'消费总次数'),_(u'消费总合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次结算'),_(u'实消费次数结算'),_(u'结算金额'),_(u'消费日期')]
       else:
           FieldNames=['dept_name','pos_count','meal_money','back_count','back_money','summary_total_time','summary_total_money','summary_count','summary_money','pos_date']
           FieldCaption=[_(u'部门名称'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数结算'),_(u'计次结算'),_(u'实消费次数结算'),_(u'结算金额'),_(u'消费日期')]
       
    elif typeid=="140": #设备汇总
        if get_option("POS_IC"):
           FieldNames=['device_name','device_sn','sum_device_count','pos_count','back_count','summary_total_time','error_summary_count','summary_count','meal_money','back_money','add_single_money','error_summary_money','summary_dev_money','summary_money','pos_date']
           FieldCaption=[_(u'设备名称'),_(u'设备序列号'),_(u'设备记录总次数'),_(u'消费总次数'),_(u'纠错总次数'),_(u'计次结算'),_(u'异常消费次数结算'),_(u'扣款消费次数结算（不含异常）'),_(u'设备消费总合计'),_(u'纠错合计'),_(u'补单合计'),_(u'异常消费金额结算'),_(u'实消费金额结算（不含异常）'),_(u'系统金额结算（含补单）'),_(u'消费日期')]
        else:
           FieldNames=['device_name','device_sn','pos_count','meal_money','back_count','back_money','summary_total_time','summary_total_money','add_single_money','summary_count','summary_dev_money','summary_money','pos_date']
           FieldCaption=[_(u'设备名称'),_(u'设备序列号'),_(u'消费次数'),_(u'消费合计'),_(u'纠错次数'),_(u'纠错合计'),_(u'计次次数结算'),_(u'计次结算'),_(u'补单合计'),_(u'实消费次数结算'),_(u'设备金额结算'),_(u'系统金额结算（含补单）'),_(u'消费日期')]
    elif typeid=="150": #收支统计
        if get_option("POS_IC"):
            FieldNames=['operate','recharge_count','refund_count','hairpin_count','back_card_count','recharge_money','refund_money','cost_money','manage_money','back_card_money','sz_money','summary_date']
            FieldCaption=[_(u'统计对象'),_(u'充值次数'),_(u'退款次数'),_(u'发卡次数'),_(u'退卡次数'),_(u'充值合计'),_(u'退款合计'),_(u'卡成本支入'),_(u'管理费支入'),_(u'卡成本支出'),_(u'收支合计'),_(u'汇总时间')]
        else:
            FieldNames=['operate','recharge_count','refund_count','hairpin_count','back_card_count','recharge_money','refund_money','cost_money','manage_money','back_card_money','sz_money','summary_date']
            FieldCaption=[_(u'统计对象'),_(u'充值次数'),_(u'退款次数'),_(u'发卡次数'),_(u'退卡次数'),_(u'充值合计'),_(u'退款合计'),_(u'卡成本支入'),_(u'管理费支入'),_(u'卡成本支出'),_(u'收支合计'),_(u'汇总时间')]
    
    elif typeid=="13": #发卡表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','issue_date','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'发卡日期'),_(u'操作员')]
        else:
            FieldNames=['user_pin','user_name','dept_name','card','issue_date','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'发卡日期'),_(u'操作员')]
            
    elif typeid=="1": #充值表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','card_serial','money','recharge_type','card_blance','check_time','convey_time','create_operator','dev_serial_num','dev_sn','log_flag']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'充值金额'),_(u'充值类型'),_(u'卡余额'),_(u'充值时间'),_(u'上传时间'),_(u'操作员'),_(u'设备流水号'),_(u'设备序列号'),_(u'记录类型')]
        else:
            FieldNames=['user_pin','user_name','dept_name','card','card_serial','money','card_blance','check_time','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡流水号'),_(u'充值金额'),_(u'卡余额'),_(u'充值时间'),_(u'操作员')]
    
    elif typeid=="5":# 退款表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','card_serial','money','card_blance','check_time','convey_time','create_operator','dev_serial_num','dev_sn','log_flag']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'退款金额'),_(u'卡余额'),_(u'退款时间'),_(u'上传时间'),_(u'操作员'),_(u'设备流水号'),_(u'设备序列号'),_(u'记录类型')]
        else:
            FieldNames=['user_pin','user_name','dept_name','card','card_serial','money','card_blance','check_time','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡流水号'),_(u'退款金额'),_(u'卡余额'),_(u'退款时间'),_(u'操作员')]
        
    elif typeid=="2":#补贴表
            if get_option("POS_IC"):
                FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','card_serial','allow_type','money','card_blance','check_time','convey_time','create_operator','dev_serial_num','dev_sn','log_flag']
                FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'补贴类型'),_(u'补贴金额'),_(u'卡余额'),_(u'补贴领取时间'),_(u'上传时间'),_(u'操作员'),_(u'设备流水号'),_(u'设备序列号'),_(u'记录类型')]
            else:
                FieldNames=['user_pin','user_name','dept_name','card','card_serial','money','card_blance','check_time','create_operator']
                FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡流水号'),_(u'补贴金额'),_(u'卡余额'),_(u'补贴时间'),_(u'操作员')]
            
    elif typeid=="4":#退卡表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','card_serial','money','check_time','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'卡流水号'),_(u'支出卡成本'),_(u'退卡时间'),_(u'操作员')]
        else:
            FieldNames=['user_pin','user_name','dept_name','card','card_serial','money','check_time','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡流水号'),_(u'支出卡成本'),_(u'退卡时间'),_(u'操作员')]
    
    elif typeid=="7":#卡成本表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','money','check_time','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'成本金额'),_(u'操作时间'),_(u'操作员')]
        else:
            FieldNames=['user_pin','user_name','dept_name','card','money','check_time','create_operator']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'成本金额'),_(u'操作时间'),_(u'操作员')]
    
    elif typeid=="12":#卡余额表
        if get_option("POS_IC"):
            FieldNames=['user_pin','user_name','dept_name','card','sys_card_no','card_type','money']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡账号'),_(u'卡类'),_(u'余额')]
        else:
            FieldNames=['user_pin','user_name','dept_name','card','card_type','money']
            FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'部门名称'),_(u'卡号'),_(u'卡类'),_(u'余额')]
    for i  in  range(len(FieldNames)):
        r.append((FieldNames[i],FieldCaption[i]))
#        r[FieldNames[i]] = FieldCaption[i]
    return [r,FieldNames,FieldCaption]
    
