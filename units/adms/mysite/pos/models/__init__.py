#coding=utf-8
from django.db import models
from django.conf import settings
from base.models import CachingModel
from base.operation import Operation, ModelOperation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

#from model_iccard import ICcard
#from model_dininghall import Dininghall#餐厅资料
#from model_meal import Meal#自己定义的模型，餐别资料

from model_allowance import Allowance#, AllowanceSetting
from model_handconsume import HandConsume
#from consumeAppOperation import consumeAppReport
from consumeAppOperation import consumeAppReport,PosReport,pos_guide,PosDeviceDataManage
from model_carcashsz import CarCashSZ
#from model_reimburse import Reimburese
from model_splittime import SplitTime
from model_carcashtype import CarCashType
from model_timeslice import TimeSlice
from model_poslog import PosLog
from model_posdevlog import PosDevLog
from model_keyvalue import KeyValue
from model_merchandise import Merchandise
from model_timebrush import TimeBrush
from model_cardmanage import CardManage
from model_errors import Errors
from model_loseunitecard import LoseUniteCard
from model_batchtime import BatchTime
from model_replenishcard import ReplenishCard
from database import PosFormPage,SplitTimePage,BatchTimePage,DiningPage,MealPage,MerchandisePage,KeyValuePage
from model_posparam import PosParam
from model_cardserial import CardSerial
from model_cardcashszbak import CarCashSZBak
from model_icconsumerlist import ICConsumerList
from model_icconsumerlistbak import ICConsumerListBak
from model_icerrorlog import IcErrorLog
from model_storedetail import StoreDetail
from model_keydetail import KeyDetail
from model_timedetail import TimeDetail
from consumer_summary_report import ConsumerSummaryReport
from consumer_report import ConsumerReport
from report_models.get_issuecard_report  import GetIssuecardReport
from report_models.get_recharge_report  import GetRechargeReport
from report_models.get_card_blance_report  import GetCardBlanceReport
from report_models.get_cost_report  import GetCostReport
from report_models.get_return_card_report  import GetReturnCardReport
from report_models.get_reimburese_report  import GetReimbureseReport
from report_models.get_allow_report  import GetAllowReport 
#from report_models.get_ic_error_list_record  import GetIcErrorListReport
from report_models.get_manage_card_report  import ManageCardReport
from report_models.get_lost_card_report  import LostCardReport 
from report_models.get_pos_replenish_card_report import PosReplenishCard
from report_models.get_pos_list_report import GetPosListReport
from report_models.get_ic_error_list_report import GetErrorPosListReport
from report_models.get_no_card_blance_report import GetNoCardBlanceReport
from report_models.get_emp_summary_report import GetEmpSummaryReport
from report_models.get_dept_summary_report import GetDeptSummaryReport
from report_models.get_dining_summary_report import GetDiningSummaryReport
from report_models.get_device_summary_report import GetDeviceSummaryReport
from report_models.get_sz_summary_report import GetSzSummaryReport
#from model_cardcost import CardCost, ChargeRecord, CardInfo, ReturnCard

verbose_name = _(u'消费')#应用名称，顶部菜单
_menu_index = 6#在菜单之前

