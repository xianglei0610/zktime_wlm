# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.conf import settings
import dict4ini
current_path = settings.WORK_PATH
pos_config=dict4ini.DictIni(current_path+"/pos/pos_config.ini")

TIMEOUT=settings.COMMAND_TIMEOUT*3600*24
POS_IC_ADMS_MODEL = True


#----------------------------IC消费数据解析批次最大值
POS_DEAL_BAT_SIZE = 50
POS_DEAL_BAT_SIZE = pos_config["Options"]["POS_DEAL_BAT_SIZE"]
#---------------------------------IC消费在线补贴------------------------
ONLINE_ALLOWANCE = False
is_online_allowance = pos_config["Options"]["ONLINE_ALLOWANCE"]
if is_online_allowance.lower()=="true":#是否在线补贴模式
    ONLINE_ALLOWANCE = True 
ONLINE_ALLOWANCE = ONLINE_ALLOWANCE

#---------------------------------消费模块业务调试开关------------------------
POS_DEBUG = False #消费模块调试开关，用来打印日志信息跟踪调试
pos_debug = pos_config["Options"]["POS_DEBUG"]
if pos_debug.lower()=="true":#是否在线补贴模式
    POS_DEBUG = True 
POS_DEBUG = POS_DEBUG


#----------------------------IC消费数据解析是否需要多进程模式
IS_DISTRIBUTED = False
is_distributed = pos_config["Options"]["IS_DISTRIBUTED"]
if is_distributed.lower()=="true":#是否分布式部署
    IS_DISTRIBUTED = True 
IS_DISTRIBUTED = IS_DISTRIBUTED

#----------------------------消费报表切换
OLD_CONSUMER_REPORT = False
OLD_CONSUMER_SUMMARY_REPORT = False

NEW_CONSUMER_REPORT = True
NEW_CONSUMER_SUMMARY_REPORT = True

old_consumer_report = pos_config["Options"]["OLD_CONSUMER_REPORT"]
if old_consumer_report.lower()=="true":#旧版消费报表
    OLD_CONSUMER_REPORT = True 
OLD_CONSUMER_REPORT = OLD_CONSUMER_REPORT

old_consumer_summary_report = pos_config["Options"]["OLD_CONSUMER_SUMMARY_REPORT"]
if old_consumer_summary_report.lower()=="true":#旧版汇总报表
    OLD_CONSUMER_SUMMARY_REPORT = True 
OLD_CONSUMER_SUMMARY_REPORT = OLD_CONSUMER_SUMMARY_REPORT


new_consumer_report = pos_config["Options"]["NEW_CONSUMER_REPORT"]
if new_consumer_report.lower()=="true":#新版消费报表
    NEw_CONSUMER_REPORT = True 
NEw_CONSUMER_REPORT = NEw_CONSUMER_REPORT

new_consumer_summary_report = pos_config["Options"]["NEW_CONSUMER_SUMMARY_REPORT"]
if new_consumer_summary_report.lower()=="true":#新版汇总报表
    NEW_CONSUMER_SUMMARY_REPORT = True 
NEW_CONSUMER_SUMMARY_REPORT = NEW_CONSUMER_SUMMARY_REPORT





