# -*- coding: utf-8 -*-
import traceback
import string
import datetime
import os
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.conf import settings
from django.core.cache.backends.filebased import CacheClass
from django.db import connection
from mysite.personnel.models.model_meal import Meal
from django.core.cache import cache
from mysite.pos.models.model_batchtime import BatchTime
from mysite.pos.models.model_splittime import SplitTime
from mysite.pos.models.model_keyvalue import KeyValue
from mysite.pos.models.model_merchandise import Merchandise
from mysite.personnel.models.model_iccard import ICcard
from django.db.models import Q
from mysite.pos.pos_constant import TIMEOUT
from mysite.pos.models.model_loseunitecard import LoseUniteCard

from django.db import models
from django.db import IntegrityError, DatabaseError, models
from django.db import  connection as conn
from mysite.sql_utils import get_sql
from django.db import transaction

from dbapp.utils import getJSResponse
from django.utils import simplejson 
from django.utils.encoding import smart_str
from base.cached_model import cache_key
#conn = connections['default']
#获取消费参数
def LoadPosParam(reloadData=False):
    from mysite.pos.models import PosParam
    from base.crypt import encryption,decryption
    global pos_param
    if not reloadData and pos_param!={}:
        return pos_param
    pos_param = {
    'ID':1,
    'max_money':999,
    'main_fan_area':'1',
    'minor_fan_area':'2',
    'system_pwd':'123456',
    'pwd_again':'123456',
    }
    qryOptions=PosParam.objects.all()
    pos_param['ID'] = qryOptions[0].id
    pos_param['max_money'] = str(qryOptions[0].max_money)
    pos_param['main_fan_area'] = qryOptions[0].main_fan_area
    pos_param['minor_fan_area'] = qryOptions[0].minor_fan_area
    pos_param['system_pwd'] = decryption(qryOptions[0].system_pwd)
    pos_param['pwd_again'] = decryption(qryOptions[0].pwd_again)
    return pos_param


def enc(s):
    ser="zksoft"
    ret=""
    for k in range(6):
          ret += chr(ord(s[k])^ord(ser[k]))
    return ret

def customSql(sql,action=True):
    cursor = connection.cursor()
    cursor.execute(sql)
    if action:
        connection._commit()
    return cursor

#获取餐别缓存
def get_cache_meal():
    cacheobj = Meal.objects.all().filter(available=1)
    return cacheobj


#获取消费时间段缓存
def get_cache_batchtime():
#    cacheobj = cache.get("BatchTime")
#    if not cacheobj and not type(cacheobj)==list:
#       cacheobj = BatchTime.objects.filter(isvalid=1)
#       cache.set("BatchTime",list(cacheobj),TIMEOUT)
#    return cacheobj
    cacheobj = BatchTime.objects.filter(isvalid=1)
    return cacheobj

#获取分段定值信息缓存
def get_cache_splittime(device):
    cacheobj = SplitTime.objects.all().filter(Q(use_mechine__exact=None) | Q(use_mechine=device),isvalid=1)
    return cacheobj


#获取键值信息缓存
def get_cache_keyvalue(device):
    cacheobj = KeyValue.objects.all().filter(Q(use_mechine__exact=None) | Q(use_mechine=device))
    return cacheobj


#获取商品信息缓存
def get_cache_merchandise():
    cacheobj = Merchandise.objects.all()
    return cacheobj

#ICcard 获取卡类信息缓存
def get_cache_iccard():
    cacheobj = ICcard.objects.all()
    return cacheobj

#LoseUniteCard 获取挂失卡
def get_cache_loseunitecard():
    cacheobj = LoseUniteCard.objects.all().filter(cardstatus='3')
    return cacheobj

#LoseUniteCard 获取所有登记过卡账号的卡
def get_cache_issuecard():
    from mysite.personnel.models.model_issuecard import IssueCard
    cacheobj = IssueCard.all_objects.all().filter(sys_card_no__isnull=False)
    return cacheobj


def GetCurrentMonthDay(currentday):
    currentMonth = currentday.strftime('%m')
    currentYear = currentday.strftime('%Y')
    d1 = datetime.datetime(int(currentYear),int(currentMonth),1)
    d2 = datetime.datetime(int(currentYear),int(currentMonth)+1,1)
    days = d2 - d1
    day = days.days
    return datetime.date(int(currentYear),int(currentMonth),1),\
           datetime.date(int(currentYear),int(currentMonth),day)

#手动删除当前对象cache
def delete_model_cache(model_obj):
    key = cache_key(model_obj,model_obj.pk)
    cache.delete(key)
    

def check_repeated_data(stamp_name,data_obj):
    if stamp_name == 'pos_log_stamp' :
#        SELECT_ICCONSUMERLIST = "if  not exists(select user_id from pos_icconsumerlist where (dev_sn='%s' and sys_card_no='%s' and money='%s' and card_serial_num='%s'and dev_serial_num='%s' and pos_time ='%s'))" % (data_obj.dev_sn,data_obj.sys_card_no,data_obj.money,data_obj.card_serial_num,data_obj.dev_serial_num,data_obj.pos_time)
        params={}
        id_part={}
        params["dev_sn"] = data_obj.dev_sn
        params["sys_card_no"] = data_obj.sys_card_no
        params["money"] = data_obj.money
        params["card_serial_num"] = data_obj.card_serial_num
        params["dev_serial_num"] = data_obj.dev_serial_num
        params["pos_time"] = data_obj.pos_time
        SELECT_ICCONSUMERLIST = get_sql("ic_pos_utils",sqlid="pos_log_exists",app = "pos",params = params ,id_part = id_part )
        return SELECT_ICCONSUMERLIST
    elif stamp_name == 'full_log_stamp':
#        SELECT_FULL = "if not exists(select user_id from pos_carcashsz where (sn_name='%s' and hide_column='%s' and sys_card_no='%s' and money='%s' and checktime='%s'))" %(data_obj.sn_name,data_obj.hide_column,data_obj.sys_card_no,data_obj.money,data_obj.checktime)
        params={}
        id_part={}
        params["sn_name"] = data_obj.sn_name
        params["hide_column"] = data_obj.hide_column
        params["sys_card_no"] = data_obj.sys_card_no
        params["money"] = data_obj.money
        params["checktime"] = data_obj.checktime
        SELECT_FULL = get_sql("ic_pos_utils",sqlid="full_log_exists",app = "pos",params = params ,id_part = id_part )
        return SELECT_FULL
    elif stamp_name == 'allow_log_stamp':
#        SELECT_ALLOW ="if not exists(select user_id from pos_carcashsz where (sn_name='%s' and hide_column='%s' and sys_card_no='%s' and money='%s' and checktime='%s'))" %(data_obj.sn_name,data_obj.hide_column,data_obj.sys_card_no,data_obj.money,data_obj.checktime)
        params={}
        id_part={}
        params["sn_name"] = data_obj.sn_name
        params["hide_column"] = data_obj.hide_column
        params["sys_card_no"] = data_obj.sys_card_no
        params["money"] = data_obj.money
        params["checktime"] = data_obj.checktime
        SELECT_ALLOW = get_sql("ic_pos_utils",sqlid="allow_log_exists",app = "pos",params = params ,id_part = id_part )
        return SELECT_ALLOW
    
def cashier_state(state):
    if state == '0': return 1#充值
    if state == '1': return 5#退款
    if state == '2': return 13#优惠记录
    return state


##消费记录
#pos_log_statement="""
#    insert into pos_icconsumerlist 
#    (user_id,user_pin, user_name, dept_id, card, sys_card_no, 
#    dev_sn, card_serial_num,dev_serial_num,pos_time,convey_time,
#    type_name,money,balance,pos_model,dining_id,meal_id,meal_data,create_operator,log_flag)
#    values(%(user_id)s, %(user_pin)s, %(user_name)s, %(dept_id)s, %(card)s, %(sys_card_no)s, 
#    %(dev_sn)s,%(card_serial_num)s,%(dev_serial_num)s,%(pos_time)s, %(convey_time)s, 
#    %(type_name)s, %(money)s, %(balance)s, %(pos_model)s, %(dining_id)s,%(meal_id)s, %(meal_data)s,%(create_operator)s,%(log_flag)s)
#"""
#
##充值记录
#full_log_statement="""insert into pos_carcashsz
#(user_id, card, sys_card_no, sn_name, cardserial,serialnum,checktime,convey_time,
#type_id,money,blance,hide_column,create_operator,log_flag,status)
#values(%(user_id)s, %(card)s, %(sys_card_no)s, %(sn_name)s, %(cardserial)s, %(serialnum)s, 
#%(checktime)s,%(convey_time)s,%(type_id)s, %(money)s, %(blance)s, %(hide_column)s, %(create_operator)s,%(log_flag)s,%(status)s)""" 
#
##补贴记录
#allow_log_statement="""insert into pos_carcashsz 
#(user_id, card, sys_card_no, sn_name, cardserial,serialnum,checktime,convey_time,
#type_id,money,blance,hide_column,allow_type,allow_batch,allow_base_batch,log_flag,status)
#values(%(user_id)s, %(card)s, %(sys_card_no)s, %(sn_name)s, %(cardserial)s, %(serialnum)s,%(checktime)s,%(convey_time)s,
#%(type_id)s, %(money)s, %(blance)s, %(hide_column)s,%(allow_type)s,%(allow_batch)s,%(allow_base_batch)s,%(log_flag)s,%(status)s)""" 
#
#找出存在灰色记录的卡账号
#bak_log_sql = """
#   select sys_card_no,card_serial_num from pos_icconsumerlistbak where pos_model not in (4,7) group by sys_card_no,card_serial_num having count(1) >= 2
#   """

##找出最近三个月的消费记录中存在卡流水号重复的卡账号
#pos_log_sql = """
#select sys_card_no,cardserial from (
#select sys_card_no,cardserial from pos_carcashsz where log_flag != 2 and hide_column !=13 and checktime> DateAdd(Month,-3,getdate())
#union all
#select sys_card_no,card_serial_num from pos_icconsumerlist where pos_model not in (4,7) and pos_time> DateAdd(Month,-3,getdate()))as b  
#group by sys_card_no,cardserial having count(1) >= 2 order by cardserial desc 
#"""
#
#delete_break_log = """
#delete from pos_icconsumerlist where pos_model not in (4,7) and log_flag = 4 and  sys_card_no=%(sys_card_no)s and card_serial_num=%(card_serial_num)s 
#"""


def customSql(sql,action=True):
#    from django.db import connection
    cursor = conn.cursor()
    
    cursor.execute(sql)
    if action:
        connection._commit()
    return cursor

def remove_break_log():
    try:
#        break_card_list = cursor.execute(bak_log_sql).fetchall()
        cursor = conn.cursor()
        pos_log_sql = get_sql("ic_pos_utils",sqlid="filter_pos_log_sql",app = "pos",params = {} ,id_part = {} )
        pos_log_list = customSql(pos_log_sql,False).fetchall()
        for p_obj in pos_log_list:
            sys_card_no = p_obj[0]
            card_serial_num = p_obj[1]
#            delete_sql = delete_break_log%({"sys_card_no":sys_card_no,"card_serial_num":card_serial_num})
            params = {"sys_card_no":sys_card_no,"card_serial_num":card_serial_num}
            delete_sql = get_sql("ic_pos_utils",sqlid="delete_break_log",app = "pos",params = params ,id_part = {} )
            cursor.execute(delete_sql)
            conn._commit()
    except:
        conn.close()
        import traceback;traceback.print_exc();
        pass

def filter_break_log(stamp_name):
    """
        IC消费逃卡数据处理，默认没有开启这个功能
    """
    from mysite.pos.models.model_icconsumerlistbak import ICConsumerListBak
    from mysite.pos.models.model_cardcashszbak import CarCashSZBak
    from mysite.pos.models.model_carcashsz import CarCashSZ
    from mysite.pos.models.model_icconsumerlist import ICConsumerList
    from mysite.personnel.models.model_issuecard import IssueCard
    from mysite.pos.models.model_allowance import Allowance
    if stamp_name == 'pos_log_stamp':
        bak_list = ICConsumerListBak.objects.filter(log_flag=1)
        cursor = conn.cursor()
        try:
            for obj in bak_list:
                exits_sql = check_repeated_data('pos_log_stamp',obj)
                id_part = {}
                record_dict ={
                    "user_id":obj.user_id,
                    "user_pin":obj.user_pin,
                    "user_name":obj.user_name or 'NULL',
                    "dept_id":obj.dept_id,
                    "card":obj.card,
                    "sys_card_no":obj.sys_card_no,
                    "dev_sn":obj.dev_sn,
                    "card_serial_num":obj.card_serial_num,
                    "dev_serial_num":obj.dev_serial_num,
                    "pos_time":obj.pos_time and u"'%s'"%obj.pos_time.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                    "convey_time":obj.convey_time and u"'%s'"%obj.convey_time.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                    "type_name":8,
                    "money":obj.money,
                    "balance":obj.balance,
                    "pos_model":8,
                    "dining_id":obj.dining_id,
                    "meal_id":obj.meal_id,
                    "meal_data":obj.meal_data and u"'%s'"%obj.meal_data.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                    "create_operator":obj.create_operator,
                    "log_flag":8888,
                    }
#                insert_sql = pos_log_statement%record_dict
                insert_sql = get_sql("ic_pos_utils",sqlid="pos_log_stamp",app = "pos",params = record_dict ,id_part = id_part )
                execute_sql = exits_sql+insert_sql
                cursor.execute(execute_sql)
                obj.log_flag = 8888
                models.Model.save(obj,force_update=True)
            remove_break_log()
            conn._commit()
        except:
            conn.close()
            import traceback;traceback.print_exc();
            pass
    elif stamp_name == 'full_log_stamp':
        cursor = conn.cursor()
        full_list = CarCashSZBak.objects.filter(log_flag=1,hide_column__in=[1,5,13])
        all_card_list = IssueCard.all_objects.all().filter(sys_card_no__isnull=False)
        user_id = None
        try:
            for obj in full_list:
                exits_sql = check_repeated_data('full_log_stamp',obj)
                for card in all_card_list:
                    if str(card.sys_card_no) == obj.sys_card_no:
                        user_id = card.UserID_id
                if user_id:
                    id_part = {}
                    record_dict ={
                        "user_id":user_id,
                        "card":obj.physical_card_no,
                        "sys_card_no":obj.sys_card_no,
                        "sn_name":obj.sn_name,
                        "cardserial":obj.cardserial,
                        "serialnum":obj.serialnum,
                        "checktime":obj.checktime  and u"'%s'"%obj.checktime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "convey_time":obj.convey_time  and u"'%s'"%obj.convey_time.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "type_id":obj.hide_column,
                        "money":obj.money,
                        "blance":obj.blance,
                        "hide_column":obj.hide_column,
                        "create_operator":obj.create_operator,
                        "log_flag":8888,
                        "status":0,
                        }
#                    insert_sql = full_log_statement%record_dict
                    insert_sql = get_sql("ic_pos_utils",sqlid="pos_log_stamp",app = "pos",params = record_dict ,id_part = id_part )
                    
                    execute_sql = exits_sql+insert_sql
                    cursor.execute(execute_sql)
                    obj.log_flag = 8888
                    models.Model.save(obj,force_update=True)
            conn._commit()
        except:
            conn.close()
            import traceback;traceback.print_exc();
            pass
        
    elif stamp_name == 'allow_log_stamp':
        cursor = conn.cursor()
        full_list = CarCashSZBak.objects.filter(log_flag=1,hide_column=2)
        all_card_list = IssueCard.all_objects.all().filter(sys_card_no__isnull=False)
        user_id = None
        try:
            for obj in full_list:
                exits_sql = check_repeated_data('allow_log_stamp',obj)
                for card in all_card_list:
                    if str(card.sys_card_no) == obj.sys_card_no:
                       user_id = card.UserID_id
                if user_id:
                    id_part = {}
                    record_dict ={
                        "user_id":user_id,
                        "card":obj.physical_card_no,
                        "sys_card_no":obj.sys_card_no,
                        "sn_name":obj.sn_name,
                        "cardserial":obj.cardserial,
                        "serialnum":obj.serialnum,
                        "checktime":obj.checktime  and u"'%s'"%obj.checktime.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "convey_time":obj.convey_time  and u"'%s'"%obj.convey_time.strftime("%Y-%m-%d %H:%M:%S") or "NULL",
                        "type_id":obj.hide_column,
                        "money":obj.money,
                        "blance":obj.blance,
                        "hide_column":obj.hide_column,
                        "allow_type":obj.allow_type,
                        "allow_batch":obj.allow_batch,
                        "allow_base_batch":obj.allow_base_batch,
                        "log_flag":8888,
                        "status":0,
                        }
#                    insert_sql = allow_log_statement%record_dict
                    insert_sql = get_sql("ic_pos_utils",sqlid="allow_log_stamp",app = "pos",params = record_dict ,id_part = id_part )
                    execute_sql = exits_sql+insert_sql
                    cursor.execute(execute_sql)
                    obj.log_flag = 8888
                    models.Model.save(obj,force_update=True)
                    #更新补贴表补贴记录领取标示
                    allowance_obj = Allowance.objects.get(sys_card_no = obj.sys_card_no,batch = obj.allow_batch)
                    allowance_obj.is_ok = 1
                    allowance_obj.receive_money = obj.money
                    allowance_obj.receive_date = obj.checktime
                    allowance_obj.base_batch = obj.allow_batch
                    models.Model.save(allowance_obj,force_update=True)
            conn._commit()
        except:
            conn.close()
            import traceback;traceback.print_exc();
            pass
        
def online_getdata(device,data_url,data_type = None):
    """
        在线采集消费数据
    """
    from mysite.iclock.models.model_device import Device
    from mysite.iclock.models.model_cmmdata import pos_gen_device_cmmdata
    from mysite.pos.pos_ic.ic_sync_store import save_pos_file
    from mysite.pos.pos_constant import POS_IC_ADMS_MODEL,POS_DEAL_BAT_SIZE
    import urllib,urllib2
    import datetime
    import time
    from decimal import Decimal
#    a = time.time()
#    request = 'http://192.168.10.141/data/?Action=Query&Table=PosLog&Fields=*&Filter=RecNo>10000 and RecNo<10010'
    request = data_url
    request_sn = "http://%s/data/?Action=InfoQuery&Items=System.SN"%device.ipaddress
    return_tag = ""
    try:
        response_sn = urllib.urlopen(request_sn)
        return_sn = response_sn.readlines()[1:][0].split("=")[1].strip()
        if device.sn == return_sn: #验证设备序列号是否匹配
            response = urllib.urlopen(request)
        else:
            return "SN_FAIL",None
    except Exception, e:
        return "CONTENT_FAIL",None
    try:
        respose_data = response.readlines()
        data_count = respose_data[0:1][0].split("=")[1].strip()
        if data_count != "0":
            rawData = ""
            if data_type == "POSLOG":
                row_list = respose_data[2:]
                field =  row_list[-1:][0].split("\t")
                STAMPID = field[5] #获取当批记录的最大流水号
                head_data=":pos_log_stamp: SN=%s\tIP=%s\tTIME=%s\tSTAMP=8888\tSTAMPID=%s\tZ=%s"%(str(device.sn).strip(),device.ipaddress,datetime.datetime.now(),STAMPID,'1')
                for index in range(len(row_list)):
            #        print "row_list[index]====",row_list[index].replace(row_list[index].split("\t")[2],datetime.datetime.strptime(row_list[index].split("\t")[2],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"))
                    list_item = row_list[index].split("\t")[2]
                    f_time = "".join([list_item[0:4],"-",list_item[4:6],"-",list_item[6:8]," ",list_item[8:10],":",list_item[10:12],":",list_item[12:14]])
                    row_list[index] = row_list[index].replace(row_list[index].split("\t")[2],f_time)
                    
                    item_list = row_list[index].split("\t")
                    pos_money = int(Decimal(item_list[3])*100)
                    card_blance = int(Decimal(item_list[4])*100)
                    item_list[3] = str(pos_money)
                    item_list[4] = str(card_blance)
                    item_list.insert(10,item_list[5])
                    del item_list[5]
                    str_item = "\t".join(item_list)
                    rawData +=str_item
#                b = time.time()
#                rawData = " ".join(row_list)
            elif data_type == "FULLLOG":
                row_list = respose_data[2:]
                field =  row_list[-1:][0].split("\t")
                STAMPID = field[8] #获取当批记录的最大流水号
                head_data=":full_log_stamp: SN=%s\tIP=%s\tTIME=%s\tSTAMP=8888\tSTAMPID=%s\tZ=%s"%(str(device.sn).strip(),device.ipaddress,datetime.datetime.now(),STAMPID,'1')

                for index in range(len(row_list)):
                #        print "row_list[index]====",row_list[index].replace(row_list[index].split("\t")[2],datetime.datetime.strptime(row_list[index].split("\t")[2],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"))
                    list_item = row_list[index].split("\t")[3]
                    f_time = "".join([list_item[0:4],"-",list_item[4:6],"-",list_item[6:8]," ",list_item[8:10],":",list_item[10:12],":",list_item[12:14]])
                    row_list[index] = row_list[index].replace(row_list[index].split("\t")[3],f_time)
                    
                    item_list = row_list[index].split("\t")
                    pos_money = int(Decimal(item_list[4])*100)
                    card_blance = int(Decimal(item_list[5])*100)
                    item_list[4] = str(pos_money)
                    item_list[5] = str(card_blance)
                    item_list[7] = item_list[8]
                    item_list[8] = "0"
                    str_item = "\t".join(item_list)
                    rawData +=str_item
#                b = time.time()
#                rawData = " ".join(row_list)
                
            elif data_type == "ALLOWLOG":
                row_list = respose_data[2:]
                field =  row_list[-1:][0].split("\t")
                STAMPID = field[9] #获取当批记录的最大流水号
                head_data=":allow_log_stamp: SN=%s\tIP=%s\tTIME=%s\tSTAMP=8888\tSTAMPID=%s\tZ=%s"%(str(device.sn).strip(),device.ipaddress,datetime.datetime.now(),STAMPID,'1')

                for index in range(len(row_list)):
                #        print "row_list[index]====",row_list[index].replace(row_list[index].split("\t")[2],datetime.datetime.strptime(row_list[index].split("\t")[2],"%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"))
                    list_item = row_list[index].split("\t")[4]
                    f_time = "".join([list_item[0:4],"-",list_item[4:6],"-",list_item[6:8]," ",list_item[8:10],":",list_item[10:12],":",list_item[12:14]])
                    row_list[index] = row_list[index].replace(row_list[index].split("\t")[4],f_time)
                    item_list = row_list[index].split("\t")
                    pos_money = int(Decimal(item_list[5])*100)
                    card_blance = int(Decimal(item_list[6])*100)
                    item_list[5] = str(pos_money)
                    item_list[6] = str(card_blance)
                    str_item = "\t".join(item_list)
                    rawData +=str_item
#                b = time.time()
#                rawData = " ".join(row_list)
            try:
                s_data="%s\n%s\n\n"%(head_data, rawData)
            except:
                s_data="%s\n%s\n\n"%(head_data, rawData)
            
            if POS_IC_ADMS_MODEL:
                obj = save_pos_file(device,s_data,data_type)
            else:
                obj=pos_gen_device_cmmdata(device,s_data)
#            c = time.time()
#            print "format==============",c-a,len(s_data)
            return "OK",data_count
        else:
            return "NO_DATA",None
    except:
        import traceback;traceback.print_exc();
        return "FAIL",None


def get_pos_device_redis(request):
    """
        获取IC消费设备redis存放的内容
    """
    from mysite.pos.pos_ic.ic_sync_model import Pos_Device
    from mysite.pos.pos_ic.ic_sync_model import PosDeviceDoesNotExist
    from mysite.pos.pos_ic.ic_sync_action import init_ic_pos_device
    device_sn = request.REQUEST.get("sn", "")
    try:
        r_device=Pos_Device(device_sn)
        try:
            pos_device=r_device.get()
        except PosDeviceDoesNotExist:
            from mysite.iclock.models import Device as D
            device = D.objects.get(sn=device_sn)
            init_ic_pos_device(device)
            pos_device=r_device.get()
            return pos_device
        pos_log_stamp_id = pos_device.pos_log_stamp_id
        full_log_stamp_id = pos_device.full_log_stamp_id
        allow_log_stamp_id = pos_device.allow_log_stamp_id
        pos_dev_data_status = pos_device.pos_dev_data_status
        return getJSResponse(smart_str(simplejson.dumps({'ret':1,'pos_dev_data_status': pos_dev_data_status,'pos_log_stamp_id': pos_log_stamp_id,'full_log_stamp_id':full_log_stamp_id,'allow_log_stamp_id':allow_log_stamp_id})))
    except:
#        import traceback;traceback.print_exc();
        return getJSResponse(smart_str(simplejson.dumps({'ret': -1})))


    
    
    