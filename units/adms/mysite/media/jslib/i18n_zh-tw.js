// -*- coding: utf-8 -*-
___f=function(){
jQuery.validator.messages.required="必填"
jQuery.validator.messages.email="不是一個email位址"
jQuery.validator.messages.date="請輸入一個合法的日期：yyyy/mm/dd"
jQuery.validator.messages.dateISO="請輸入一個合法的 (ISO)日期：yyyy-mm-dd"
jQuery.validator.messages.wZBaseDateField="請輸入一個合法的日期：yyyy-mm-dd"
jQuery.validator.messages.wZBaseDateTimeField="請輸入一個合法的日期：yyyy-mm-dd hh:mm:ss"
jQuery.validator.messages.wZBaseTimeField="請輸入一個合法的時間：hh:mm:ss"
jQuery.validator.messages.wZBaseIntegerField="請輸入一個整數"
jQuery.validator.messages.number="請輸入一個合法的數值."
jQuery.validator.messages.digits="只能輸入數位"
jQuery.validator.messages.equalTo="不一致"
jQuery.validator.messages.minlength=$.validator.format("最少{0}個字元")
jQuery.validator.messages.maxlength=$.validator.format("最多{0}個字元")
jQuery.validator.messages.rangelength=$.validator.format("必須是{0}到{1}個字元之間")
jQuery.validator.messages.range=$.validator.format("必須是{0}到{1}之間的值")
jQuery.validator.messages.max=$.validator.format("請輸入一個不大於 {0} 的值")
jQuery.validator.messages.min=$.validator.format("請輸入一個不小於 {0} 的值.")
jQuery.validator.messages.xPIN="只能輸入數位或字母。"
jQuery.validator.messages.xNum="只能輸入數位。"
jQuery.validator.messages.xMobile="手機號輸入不正確。"
jQuery.validator.messages.xTele="座機號不正確。"
jQuery.validator.messages.xSQL="不能輸入\"或\'。"
}

___f();

if(typeof(catalog)=="undefined") {catalog={}}

//in file--D:\trunk\units\adms\mysite/templates\advenquiry.html
catalog["请选择一个字段"] = "請選擇一個字段";
catalog["'满足任意一个' 值域必须是以','隔开的多个结果"] = "满足任意一个'值域必須是以','隔開的多個結果";
catalog["输入的值错误"] = "輸入的值錯誤";
//in file--D:\trunk\units\adms\mysite/templates\base_page_frame.html
catalog["确定注销系统?"] = "確定註銷系統？";
catalog["通讯失败"] = "通訊失敗";
catalog["确定"] = "確定";
catalog["服务器处理数据失败，请重试！错误码：-616"] = "服務器處理數據失敗，請重試！錯誤碼：-616.";
//in file--D:\trunk\units\adms\mysite/templates\data_edit.html
catalog["日志"] = "日誌";
//in file--D:\trunk\units\adms\mysite/templates\data_list.html
//in file--D:\trunk\units\adms\mysite/templates\DbBackupLog_list.html
catalog["请选择一条历史备份记录!"] = "請選擇一條歷史備份記錄！";
catalog["还原成功!"] = "還原成功";
//in file--D:\trunk\units\adms\mysite/templates\DbBackupLog_opform_OpBackupDB.html
catalog["间隔时间不能超过一年"] = "間隔時間不能超過一年";
catalog["间隔时间不能小于24小时"] = "間隔時間不能小於24小時";
catalog["在当前时间的一个小时内只能备份一次"] = "在當前時間的一個小時內只能備份一次";
catalog["请先在服务控制台中设置数据库备份路径"] = "請先在服務控制台中設置數據庫備份路徑";
//in file--D:\trunk\units\adms\mysite/templates\DbBackupLog_opform_OpInitDB.html
catalog["全部"] = "全部";
//in file--D:\trunk\units\adms\mysite/templates\restore.html
catalog["数据格式必须是json格式!"] = "數據格式必須是json格式";
//in file--D:\trunk\units\adms\mysite\iclock\templates\Area_opform_OpAdjustArea.html
catalog["请选择人员!"] = "請選擇人員！";
catalog["考勤"] = "考勤";
//in file--D:\trunk\units\adms\mysite\iclock\templates\Device_edit.html
catalog["设备名称不能为空"] = "設備名稱不能為空";
catalog["设备序列号不能为空"] = "設備序列號不能為空";
catalog["通讯密码必须为数字"] = "通訊密碼必須為數字";
catalog["请输入一个有效的IPv4地址"] = "請輸入一個有效的IPv4地址";
catalog["请输入一个有效的IP端口号"] = "請輸入一個有效的IP端口號";
catalog["请输入一个RS485地址"] = "請輸入一個RS485地址";
catalog["RS485地址必须为1到63之间的数字"] = "RS485地址必須為1到63之間的數字";
catalog["请选择串口号"] = "請選擇串口號";
catalog["请选择波特率"] = "請選擇波特率";
catalog["请选择设备所属区域"] = "請選擇設備所屬區域";
catalog["串口：COM"] = "串口：COM";
catalog[" 的RS485地址："] = " 的RS485地址";
catalog[" 已被占用！"] = " 已被佔用";
catalog["后台通讯忙，请稍后重试！"] = "後臺通訊忙，請稍後重試!";
catalog["提示：设备连接成功,但控制器类型与实际不符，将修改为"] = "提示：設備連接成功，但控制器類型與實際不符，將修改為";
catalog["门控制器，继续添加？"] = "們控制器，繼續添加？";
catalog["提示：设备连接成功，确定后将添加设备！"] = "提示：設備連接成功，確定后將添加設備！";
catalog["提示：设备连接失败（错误码："] = "提示：設備連接失敗（錯誤碼：";
catalog["），确定添加该设备？"] = "），確定添加設備？";
catalog["提示：设备连接失败（原因："] = "提示：設備連接失敗（原因：";
catalog["服务器处理数据失败，请重试！错误码：-615"] = "服務器處理數據失敗，請重試！錯誤碼：-615.";
catalog["您选择了[新增时删除设备中数据]，系统将自动删除设备中的数据(事件记录除外)，确定要继续？"] = "您選擇了[新增時刪除設備中數據]，系統將自動刪除設備中的數據(事件記錄除外)，確定要繼續？";
catalog["您没有选择[新增时删除设备中数据]，该功能仅用于系统功能演示和测试。请及时手动同步数据到设备，以确保系统中和设备中权限一致，确定要继续？"] = "您沒有選擇[新增刪除設備中數據]，該功能僅用於系統功能演示和測試。請及時手動同步數據到設備，以確保系統中和設備中權限一致，確定要繼續？";
catalog["编辑设备信息("] = "編輯設備信息(";
catalog["对不起，您没有访问该页面的权限，不能浏览更多信息！"] = "對不起，您沒有訪問該頁面的權限，不能瀏覽更多信息！";
//in file--D:\trunk\units\adms\mysite\iclock\templates\Dev_RTMonitor.html
catalog["确定要清除命令队列？"] = "確定要清除命令隊列？";
catalog["清除缓存命令成功！请及时手动同步数据到设备，以确保系统中和设备中权限一致！"] = "清除緩​​存命令成功！請及時手動同步數據到設備，以確保系統中和設備中權限一致！";
catalog["清除缓存命令失败!"] = "清除緩​​存命令失敗!";
//in file--D:\trunk\units\adms\mysite\att\templates\att_USER_OF_RUN.html
catalog["员工排班表"] = "員工排班表";
catalog["临时排班表"] = "臨時排班表";
catalog["排班时间段详细明细"] = "排班時間段詳細明細";
catalog["排班时间段详细明细(仅显示三个月)"] = "排班時間段詳細明細(僅顯示三個月)";
catalog["排班时间段详细明细(仅显示到年底)"] = "排班時間段詳細明細(僅顯示到年底)";
//in file--D:\trunk\units\adms\mysite\att\templates\NUM_RUN_edit.html
catalog["请选择时段"] = "請選擇時段";
catalog["选择日期"] = "選擇日期";
catalog["第"] = "第";
catalog["天"] = "天";
catalog["周的周期不能大于52周"] = "週的周期不能大於52週";
catalog["月的周期不能大于12个月"] = "月的周期不能大於12個月";
catalog["第"]="第";
catalog["天"] = "天";
//in file--D:\trunk\units\adms\mysite\att\templates\NUM_RUN_list.html
catalog["时间段明细"] = "時間段明細";
catalog["确定删除该时段吗？"] = "確定刪除該時段嗎？";
catalog["操作失败 {0} : {1}"] = "操作失敗{0} : {1}";
//in file--D:\trunk\units\adms\mysite\att\templates\NUM_RUN_opform_OpAddTimeTable.html
catalog["已选择"] = "已選擇";
//in file--D:\trunk\units\adms\mysite\att\templates\USER_OF_RUN_opform_OpAddTempShifts.html
catalog["日期格式输入错误"] = "日期格式輸入錯誤";
catalog["日期格式不正确！"] = "日期格式不正確！";
catalog["夏令时名称不能为空！"] = "夏令時名稱不能為空！"
catalog["起始时间不能和结束时间相等！"] = "起始時間不能和結束時間相等！";
//in file--D:\trunk\units\adms\mysite\att\templates\USER_OF_RUN_opform_OpAddUserOfRun.html
catalog["请选择一个班次"] = "請選擇一個班次";
catalog["结束日期不能小于开始日期!"] = "結束日期不能小於開始日期!";
catalog["请输入开始日期和结束日期! "] = "請輸入開始日期和結束日期! ";
catalog["只能设置一个班次! "] = "只能設置一個班次!";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccAntiBack_edit.html
catalog["当前选择设备的扩展参数获取失败，无法对该设备进行反潜设置！"] = "當前選擇設備的擴展參數獲取失敗，無法對該設備進行反潛設置！";
catalog["服务器处理数据失败，请重试！错误码：-601"] = "服務器處理數據失敗，請重試！錯誤碼：-601";
catalog["读取到错误的设备信息，请重试！"] = "讀取到錯誤的設備信息，請重試！";
catalog["服务器处理数据失败，请重试！错误码：-602"] = "服務器處理數據失敗，請重試！錯誤碼：-602";
catalog["或"] = "或";
catalog["反潜"] = "反潛";
catalog["读头间反潜"] = "讀頭間反潛";
catalog["反潜"] = "反潛";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccAntiBack_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccDoor_edit.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccFirstOpen_edit.html
catalog["当前门:"] = "當前門:";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccFirstOpen_list.html
catalog["删除开门人员"] = "刪除開門人員";
catalog["请先选择要删除的人员！"] = "請先選擇要刪除的人員！";
catalog["确认要从首卡常开设置信息中删除开门人员？"] = "確認要從首卡常開設置信息中刪除開門人員？";
catalog["删除开门人员成功！"] = "刪除開門人員成功！";
catalog["删除开门人员失败！"] = "刪除開門人員失敗！";
catalog["服务器处理数据失败，请重试！错误码：-603"] = "服務器處理數據失敗，請重試！錯誤碼：-603";
catalog["服务器处理数据失败，请重试！错误码：-604"] = "服務器處理數據失敗，請重試！錯誤碼：-604";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccFirstOpen_opform_OpAddEmpToFCOpen.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccInterLock_edit.html
catalog["当前选择设备的扩展参数获取失败，无法对该设备进行互锁设置！"] = "當前選擇設備的擴展參數獲取失敗，無法對該設備進行互鎖設置！";
catalog["服务器处理数据失败，请重试！错误码：-605"] = "服務器處理數據失敗，請重試！錯誤碼：-605";
catalog["门:"] = "門:";
catalog["与"] = "與";
catalog["互锁"] = "互鎖";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccInterLock_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLevelSet_list.html
catalog["数据下载进度"] = "數據下載進度";
catalog["设备名称"] = "設備名稱";
catalog["总进度"] = "總進度";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLevelSet_opform_OpAddEmpToLevel.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLinkageIO_edit.html
catalog["当前选择设备的扩展参数获取失败，无法对该设备进行联动设置！"] = "當前選擇設備的擴展參數獲取失敗，無法對該設備進行聯動設置！";
catalog["当前选择设备的扩展参数异常,请删除设备并重新添加后重试！"] = "當前選擇設備的擴展參數異常,請刪除設備並重新添加後重試！";
catalog["服务器处理数据失败，请重试！错误码：-606"] = "服務器處理數據失敗，請重試！錯誤碼：-606";
catalog["服务器处理数据失败，请重试！错误码：-607"] = "服務器處理數據失敗，請重試！錯誤碼：-607";
catalog["请输入联动设置名称！"] = "請輸入聯動設置名稱！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLinkageIO_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMap_edit.html
catalog["请选择地图！"] = "請選擇地圖！";
catalog["图片格式无效！"] = "圖片格式無效！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardEmpGroup_list.html
catalog["浏览多卡开门人员组："] = "瀏覽多卡開門人員組：";
catalog[" 的人员"] = " 的人員";
catalog["当前不存在多卡开门人员组"] = "當前不存在多卡開門人員組";
catalog["删除人员"] = "刪除人員";
catalog["确认要从多卡开门人员组中删除人员？"] = "確認要從多卡開門人員組中刪除人員？";
catalog["从组中删除人员成功！"] = "從組中刪除人員成功！";
catalog["从组中删除人员失败！"] = "從組中刪除人員失敗！";
catalog["服务器处理数据失败，请重试！错误码：-608"] = "服務器處理數據失敗，請重試！錯誤碼：-608";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardEmpGroup_opform_OpAddEmpToMCEGroup.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardSet_edit.html
catalog["请至少在一个组内填入开门人数！"] = "請至少在一個組內填入開門人數！";
catalog["至少两人同时开门！"] = "至少兩人同時開門！";
catalog["最多五人同时开门！"] = "最多五人同時開門！";
catalog["人"] = "人";
catalog["您还没有设置多卡开门人员组！请先添加！"] = "您還沒有設置多卡開門人員組！請先添加！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardSet_list.html
catalog["服务器处理数据失败，请重试！错误码：-609"] = "服務器處理數據失敗，請重試！錯誤碼：-609";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccTimeSeg_edit.html
catalog["请在文本框内输入有效的时间！"] = "請在文本框內輸入有效的時間！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccWiegandFmt_list.html
catalog["对不起,您没有韦根卡格式设置的权限,不能进行当前操作！"] = "對不起,您沒有韋根卡格式設置的權限,不能進行當前操作！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Door_Mng.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Door_Set.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Electro_Map.html
catalog["服务器处理数据失败，请重试！错误码：-617"] = "服務器處理數據失敗，請重試！錯誤碼：-617";
catalog["添加门到当前地图"] = "添加門到當前地圖";
catalog["请选择要添加的门！"] = "請選擇要添加的門！";
catalog["添加门成功！"] = "添加門成功！";
catalog["添加门失败！"] = "添加門失敗！";
catalog["服务器处理数据失败，请重试！错误码：-618"] = "服務器處理數據失敗，請重試！錯誤碼：-618";
catalog["服务器处理数据失败，请重试！错误码：-619"] = "服務器處理數據失敗，請重試！錯誤碼：-619";
catalog["移除门成功！"] = "添加門成功！";
catalog["移除门失败！"] = "添加門失敗！";
catalog["服务器处理数据失败，请重试！错误码：-620"] = "服務器處理數據失敗，請重試！錯誤碼：-620";
catalog["添加或修改地图成功！"] = "添加或修改地圖成功！";
catalog["确定要删除当前电子地图："] = "確定要刪除當前電子地圖：";
catalog["删除地图成功！"] = "刪除地圖成功！";
catalog["删除地图失败！"] = "刪除地圖失敗！";
catalog["服务器处理数据失败，请重试！错误码：-621"] = "服務器處理數據失敗，請重試！錯誤碼：-621";
catalog["保存成功！"] = "保存成功！";
catalog["保存失败！"] = "保存失敗！";
catalog["服务器处理数据失败，请重试！错误码：-622"] = "服務器處理數據失敗，請重試！錯誤碼：-622";

//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_EmpLevel_Byemp.html
catalog["浏览人员："] = "瀏覽人員：";
catalog[" 所属权限组"] = " 所屬權限組";
catalog["当前不存在人员"] = "當前不存在人員";
catalog["删除所属权限组"] = "刪除所屬權限組";
catalog["请先选择要删除的权限组！"] = "請先選擇要刪除的權限組！";
catalog["确认要删除人员所属权限组？"] = "確認要刪除人員所屬權限組？";
catalog["删除人员所属权限组成功！"] = "刪除人員所屬權限組成功！";
catalog["删除人员所属权限组失败！"] = "刪除人員所屬權限組失敗！";
catalog["服务器处理数据失败，请重试！错误码：-610"] = "服務器處理數據失敗，請重試！錯誤碼：-610";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_EmpLevel_Bylevel.html
catalog["数据处理进度"] = "數據處理進度";
catalog["浏览权限组："] = "瀏覽權限組：";
catalog[" 的开门人员"] = " 的開門人員";
catalog["当前不存在权限组"] = "當前不存在權限組";
catalog["从权限组中删除"] = "從權限組中刪除";
catalog["确认要从权限组中删除人员？"] = "確認要從權限組中刪除人員？";
catalog["从权限组中删除人员成功！"] = "從權限組中刪除人員成功！";
catalog["从权限组中删除人员失败！"] = "從權限組中刪除人員失敗！";
catalog["服务器处理数据失败，请重试！错误码：-611"] = "服務器處理數據失敗，請重試！錯誤碼：-611";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Monitor_All.html
catalog["远程开门"] = "遠程開門";
catalog["选择开门方式"] = "選擇開門方式";
catalog["开门："] = "開門：";
catalog[" 秒"] = " 秒";
catalog["常开"] = "常開";
catalog["启用当天常开时间段"] = "啟用當天常開時間段";
catalog["远程关门"] = "遠程關門";
catalog["选择关门方式"] = "選擇關門方式";
catalog["关门"] = "關門";
catalog["禁用当天常开时间段"] = "禁用當天常開時間段";
catalog["取消报警失败！"] = "取消報警失敗！";
catalog["取消报警成功！"] = "取消報警成功！";
catalog["发送开门请求失败！"] = "發送開門請求失敗！";
catalog["发送开门请求成功！"] = "發送開門請求成功！";
catalog["发送关门请求失败！"] = "發送關門請求失敗！";
catalog["发送关门请求成功！"] = "發送關門請求成功！";
catalog["发送开关门或取消报警请求失败，请重试！"] = "發送開關門或取消報警請求失敗，請重試！";
catalog["当前没有符合条件的门！"] = "當前沒有符合條件的門！";
catalog["请输入有效的开门时长！必须为1-254间的整数！"] = "請輸入有效的開門時長！必須為1-254間的整數！";
catalog["禁用"] = "禁用";
catalog["离线"] = "離線";
catalog["报警"] = "報警";
catalog["门开超时"] = "門開超時";
catalog["关闭"] = "關閉";
catalog["打开"] = "打開";
catalog["无门磁"] = "無門磁";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_alarm.html
catalog["导出报表"] = "導出報表";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_allevent.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_emplevel.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Device_opform_OpChangeIPOfACPanel.html
catalog["请输入有效的IPv4地址！"] = "請輸入有效的IPv4地址！";
catalog["请输入有效的网关地址！"] = "請輸入有效的網關地址！";
catalog["请输入有效的子网掩码！"] = "請輸入有效的子網掩碼！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Device_opform_OpCloseAuxOut.html
catalog["获取设备扩展参数失败，当前操作不可用！"] = "獲取設備擴展參數失敗，當前操作不可用！";
catalog["服务器处理数据失败，请重试！错误码：-623"] = "服務器處理數據失敗，請重試！錯誤碼：-623";
catalog["请选择要关闭的辅助输出点！"] = "請選擇要關閉的輔助輸出點！";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Device_opform_OpSearchACPanel.html
catalog["退出"] = "退出";
catalog["正在搜索中,请等待!"] = "正在搜索中,請等待!";
catalog["服务器处理数据失败，请重试！错误码：-612"] = "服務器處理數據失敗，請重試！錯誤碼：-612";
catalog["当前共搜索到的门禁控制器总数为："] = "當前共搜索到的門禁控制器總數為：";
catalog["自定义设备名称"] = "自定義設備名稱";
catalog["新增时删除设备中数据"] = "新增時刪除設備中數據";
catalog["设备名称不能为空，请重新添加设备！"] = "設備名稱不能為空，請重新添加設備！";
catalog["的设备添加成功！"] = "的設備添加成功！";
catalog["已添加设备数："] = "已添加設備數：";
catalog["IP地址："] = "IP地址：";
catalog[" 已存在！"] = " 已存在！";
catalog["序列号："] = "序列號：";
catalog["IP地址为："] = "IP地址為：";
catalog[" 的设备添加失败！原因："] = " 的設備添加失敗！原因：";
catalog[" 的设备添加失败！"] = " 的設備添加失敗！";
catalog[" 的设备添加异常！"] = " 的設備添加異常！";
catalog["的设备添加成功，但设备扩展参数获取失败！"] = "的設備添加成功，但設備擴展參數獲取失敗！";
catalog["设备连接成功，但无数据返回，添加设备失败！"] = "設備連接成功，但無數據返回，添加設備失敗！";
catalog["设备连接失败(错误码："] = "設備連接失敗(錯誤碼：";
catalog[")，无法添加该设备！"] = ")，無法添加該設備！";
catalog["设备连接失败(原因："] = "設備連接失敗(原因：";
catalog["服务器处理数据失败，请重试！错误码：-613"] = "服務器處理數據失敗，請重試！錯誤碼：-613";
catalog["修改设备IP地址"] = "修改設備IP地址";
catalog["原IP地址"] = "原IP地址為";
catalog["新IP地址"] = "新IP地址";
catalog["网关地址"] = "網關地址";
catalog["子网掩码"] = "子網掩碼";
catalog["请输入设备通讯密码:"] = "請輸入設備通訊密碼:";
catalog["确认"] = "確認";
catalog["新的IP地址不能为空！"] = "新的IP地址不能為空！";
catalog["请输入一个有效的IPv4地址！"] = "請輸入一個有效的IPv4地址！";
catalog["请输入一个有效的网关地址！"] = "請輸入一個有效的網關地址！";
catalog["请输入一个有效的子网掩码！"] = "請輸入一個有效的子網掩碼！";
catalog["该IP地址的设备已存在或该IP地址已被使用，不能添加！请重新输入！"] = "該IP地址的設備已存在或該IP地址已被使用，不能添加！請重新輸入！";
catalog["修改IP地址成功！"] = "修改IP地址成功！";
catalog["修改IP地址失败！原因："] = "修改IP地址失敗！原因：";
catalog["设备连接成功，但修改IP地址失败！"] = "設備連接成功，但修改IP地址失敗！";
catalog["设备连接失败，故修改IP地址失败！"] = "設備連接失敗，故修改IP地址失敗！";
catalog["服务器处理数据失败，请重试！错误码：-614"] = "服務器處理數據失敗，請重試！錯誤碼：-614";
catalog["没有搜索到门禁控制器！"] = "沒有搜索到門禁控制器！";
//in file--D:\trunk\units\adms\mysite\personnel\templates\Department_list.html
catalog["显示部门树"] = "顯示部門樹";
catalog["隐藏部门树"] = "隱藏部門樹";
//in file--D:\trunk\units\adms\mysite\personnel\templates\EmpChange_edit.html
catalog["请选择一个调动栏位"] = "請選擇一個調動欄位";
//in file--D:\trunk\units\adms\mysite\personnel\templates\EmpItemDefine_list.html
catalog["部门花名册"] = "部門花名冊";
catalog["学历构成分析表"] = "學歷構成分析表";
catalog["人员流动表"] = "人員流動表";
catalog["人员卡片清单"] = "人員卡片清單";
catalog["请选择开始日期和结束日期"] = "請選擇開始日期和結束日期";
catalog["开始日期不能大于结束日期"] = "開始日期不能大於結束日期";
//in file--D:\trunk\units\adms\mysite\personnel\templates\Employee_edit.html
catalog["图片格式无效!"] = "圖片格式無效!";
catalog["人员编号必须为数字"] = "人員編號必須為數字";
catalog["请输入有效的E_mail!"]="請輸入有效的E_mail!";
catalog["身份证号码不正确"] = "身份證號碼不正確";
catalog["没有可选的门禁权限组！"] = "沒有可選的門禁權限組！";
catalog["指纹模板错误，请立即联系开发人员！"] = "指紋模板錯誤，請立即聯繫開發人員！";

catalog["修改密码"] = "修改密碼";
catalog["旧密码："] = "舊密碼：";
catalog["新密码："] = "新密碼：";
catalog["确认密码："] = "確認密碼：";
catalog["最大6位整数"] ="最大6位整數";

//in file--D:\trunk\units\adms\mysite\personnel\templates\Employee_list.html
//in file--D:\trunk\units\adms\mysite\personnel\templates\Employee_opform_OpAddLevelToEmp.html
//in file--D:\trunk\units\adms\mysite\personnel\templates\IssueCard_opform_OpBatchIssueCard.html
catalog["每次发卡数量不能超过100"] = "每次發卡數量不能超過100";
catalog["起始编号长度不能超过"] = "起始編號長度不能超過";
catalog["位"] = "位";
catalog["结束编号长度不能超过"] = "結束編號長度不能超過";
catalog["起始人员编号与结束人员编号的长度位数不同！"] = "起始人員編號與結束人員編號的長度位數不同！";
//in file--D:\trunk\units\adms\mysite\personnel\templates\LeaveLog_list.html
//in file--D:\trunk\units\adms\mysite\worktable\templates\worktable_common_monitor.html
catalog["点击查看消息详情"] = "點擊查看消息詳情";
catalog["删除该消息"] = "刪除該消息";
catalog["公告详情"] = "公告詳情";
//in file--D:\trunk\units\adms\mysite\worktable\templates\worktable_common_opt.html
catalog["保存成功!"] = "保存成功!";
catalog["人员选择:"] = "人員選擇";
//in file--D:\trunk\units\adms\mysite\worktable\templates\worktable_common_search.html
catalog["人员查询"] = "人員查詢";
catalog["人员编号"] = "人員編號";
catalog["姓名"] = "姓名";
catalog["身份证号查询"] = "身份證號查詢";
catalog["身份证号码"] = "身份證號碼";
catalog["考勤设备查询"] = "考勤設備查詢";
catalog["离职人员查询"] = "離職人員查詢";
catalog["考勤原始数据查询"] = "考勤原始數據查詢";
catalog["员工调动查询"] = "員工調動查詢";
catalog["卡片查询"] = "卡片查詢";
catalog["部门查询"] = "部門查詢";
catalog["部门编号"] = "部門編號";
catalog["部门名称"] = "部門名稱";
catalog["补签卡查询"] = "補簽卡查詢";
catalog["服务器加载数据失败,请重试!"] = "服務器加載數據失敗,請重試!";
//in file--D:\trunk\units\adms\mysite\media\jslib\calculate.js
catalog["补签卡"] = "補簽卡";
catalog["补请假"] = "補請假";
catalog["新增排班"] = "新增排班";
catalog["临时排班"] = "臨時排班";
catalog["结束日期不能大于今天"] = "結束日期不能大於今天";
catalog["统计只能当月日期，或者天数不能超过开始日期的月份天数！ "] = "統計只能當月日期，或者天數不能超過開始日期的月份天數！ ";
catalog["统统计的时间可能会较长，请耐心等待"] = "統計的時間可能會較長，請耐心等待";
catalog["请选择人员或部门"] = "請選擇人員或部門";
catalog["统计结果详情"] = "統計結果詳情";
catalog["每日考勤统计表"] = "每日考勤統計表";
catalog["考勤明细表"] = "考勤明細表";
catalog["请假明细表"] = "請假明細表";
catalog["考勤统计汇总表"] = "考勤統計匯總表";
catalog["原始记录表"] = "原始記錄表";
catalog["补签卡表"] = "補簽卡表";
catalog["请假汇总表"] = "請假匯總表";
catalog["请选择开始日期或结束日期!"] = "請選擇開始日期或結束日期!";
catalog["开始日期不能大于结束日期!"] = "開始日期不能大於結束日期!";
catalog["最多只能查询31天的数据!"] = "最多只能查詢31天的數據!";
catalog["请在查询结果中选择人员！"] = "請在查詢結果中選擇人員！";
catalog["取消"] = "取消";
//in file--D:\trunk\units\adms\mysite\media\jslib\CDrag.js
catalog["展开"] = "展開";
catalog["收缩"] = "收縮";
catalog["自定义工作面板"] = "自定義工作面板";
catalog["锁定"] = "鎖定";
catalog["解除"] = "解除";
catalog["常用操作"] = "常用操作";
catalog["常用查询"] = "常用查詢";
catalog["考勤快速上手"] = "考勤快速上手";
catalog["门禁快速上手"] = "門禁快速上手";
catalog["系统提醒、公告"] = "系統提醒、公告";
catalog["人力构成分析"] = "人力構成分析";
catalog["最近门禁异常事件"] = "最近門禁異常事件";
catalog["本日出勤率"] = "本日出勤率";
catalog["加载中......"] = "加載中......";
//in file--D:\trunk\units\adms\mysite\media\jslib\datalist.js
catalog["是否"] = "是否";
catalog["选择所有 {0}(s)"] = "選擇所有{0}(s)";
catalog["选择 {0}(s): "] = "擇 {0}(s): ";
catalog["服务器处理数据失败，请重试！"] = "服務器處理數據失敗，請重試！";
catalog["新建相关数据"] = "新建相關數據";
catalog["浏览相关数据"] = "瀏覽相關數據";
catalog["添加"] = "添加";
catalog["浏览"] = "瀏覽";
catalog["编辑"] = "編輯";
catalog["编辑选定记录"] = "編輯選定記錄";
catalog["升序"] = "升序";
catalog["降序"] = "降序";
//in file--D:\trunk\units\adms\mysite\media\jslib\datalistadd.js
catalog["该模型不支持高级查询功能"] = "該模型不支持高級查詢功能";
catalog["高级查询"] = "高級查詢";
catalog["导入"] = "導入";
catalog["请选择一个上传的文件!"] = "請選擇一個上傳的文件!";
catalog["标题行号必须是数字!"] = "標題行號必須是數字!";
catalog["记录行号必须是数字!"] = "記錄行號必須是數字!";
catalog["请选择xls文件!"] = "請選擇xls文件!";
catalog["请选择csv文件或者txt文件!"] = "請選擇csv文件或者txt文件!";
catalog["文件标头"] = "文件標頭";
catalog["文件记录"] = "文件記錄";
catalog["表字段"] = "表字段";
catalog["请先上传文件！"] = "請先上傳文件！";
catalog["导出"] = "導出";
catalog["页记录数只能为数字"] = "頁記錄數只能為數字";
catalog["页码只能为数字"] = "頁碼只能為數字";
catalog["记录数只能为数字"] = "記錄數只能為數字";
catalog["用户名"] = "用戶名";
catalog["动作标志"] = "動作標誌";
catalog["增加"] = "增加";
catalog["修改"] = "修改";
catalog["删除"] = "刪除";
catalog["其他"] = "其他";
//in file--D:\trunk\units\adms\mysite\media\jslib\electro_map.js
catalog["地图宽度到达上限(1120px)，不能再放大！"] = "地圖寬度到達上限(1120px)，不能再放大！";
catalog["地图宽度到达下限(400px)，不能再缩小！"] = "地圖寬度到達下限(400px)，不能再縮小！";
catalog["地图高度到达下限(100px)，不能再缩小！"] = "地圖高度到達下限(100px)，不能再縮小！";
catalog["门图标的位置（Top或Left）到达下限，请稍作调整后再进行缩小操作！"] = "門圖標的位置（Top或Left）到達下限，請稍作調整後再進行縮小操作！";

//in file--D:\trunk\units\adms\mysite\media\jslib\importAndExport.js
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.plus.js
catalog["信息提示"] = "信息提示";
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.plus.js
catalog["日期"] = "日期";
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.zcommon.js
catalog["标签页不能多于6个!"] = "標籤頁不能多於6個!";
catalog["按部门查找"] = "按部門查找";
catalog["选择部门下所有人员"] = "選擇部門下所有人員";
catalog["(该部门下面的人员已经全部选择!)"] = "(該部門下面的人員已經全部選擇!)";
catalog["按人员编号/姓名查找"] = "按人員編號/姓名查找";
catalog["按照人员编号或姓名查找"] = "按照人員編號或姓名查找";
catalog["查询"] = "查詢";
catalog["请选择部门"] = "請選擇部門";
catalog["该部门下面的人员已经全部选择!"] = "該部門下面的人員已經全部選擇!";
catalog["打开选人框"] = "打開選人框";
catalog["收起"] = "收起";
catalog["已选择人员"] = "已選擇人員";
catalog["清除"] = "收起";
catalog["编辑还未完成，已临时保存，是否取消临时保存?"] = "編輯還未完成，已臨時保存，是否取消臨時保存?";
catalog["恢复"] = "恢復";
catalog["会话已经过期或者权限不够,请重新登入!"] = "會話已經過期或者權限不夠,請重新登入!";
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.zgrid.js
catalog["没有选择要操作的对象"] = "沒有選擇要操作的對象";
catalog["进行该操作只能选择一个对象"] = "進行該操作只能選擇一個對象";
catalog["相关操作"] = "相關操作";
catalog["共"] = "共";
catalog["记录"] = "記錄";
catalog["页"] = "頁";
catalog["首页"] = "首頁";
catalog["前一页"] = "前一頁";
catalog["后一页"] = "後一頁";
catalog["最后一页"] = "最後一頁";
catalog["选择全部"] = "選擇全部";
//in file--D:\trunk\units\adms\mysite\media\jslib\widgets.js
catalog["January February March April May June July August September October November December"] = "January February March April May June July August September October November December";
catalog["S M T W T F S"] = "S M T W T F S";
//---------------------------------------------------------
catalog["记录条数不能超过10000"] = "記錄條數不能超過10000";
catalog["当天存在员工排班时"] = "當天存在員工排班時";

catalog["暂无提醒及公告信息"] = "暫無提醒及公告信息";
catalog["关于"] = "關於";
catalog["版本号"] = "版本號";
catalog["本系统建议使用浏览器"] = "本系統建議使用瀏覽器";
catalog["显示器分辨率"] = "顯示器分辨率";
catalog["及以上像素"] = "及以上像素";
catalog["软件运行环境"] = "軟件運行環境";
catalog["系统默认"] = "系統默認";

catalog["photo"] = "照片";
catalog["table"] = "列表";

catalog["此卡已添加！"] = "此卡已添加！";
catalog["卡号不正确！"] = "卡號不正確！";
catalog["请输入要添加的卡号！"] = "請輸入要添加的卡號！";
catalog["请选择刷卡位置！"] = "請選擇刷卡位置！";
catalog["请选择人员！"] = "請選擇人員！";
catalog["table"] = "列表";
catalog["table"] = "列表";

catalog["首字符不能为空!"]="首字符不能為空!";
catalog["密码长度必须大于4位!"]="密碼長度必須大於4位!";

catalog["当前列表中没有卡可供分配！"] = "當前列表中沒有卡可供分配！";
catalog["当前列表中没有人员需要分配！"] = "當前列表中沒有人員需要分配！";
catalog["没有已分配人员！"] = "沒有已分配人員！";
catalog["请先点击停止读取！"] = "請先點擊停止讀取！";
catalog["请选择需要分配的人员！"] = "請選擇需要分配的人員！";

catalog["请选择一个介于1到223之间的数值！"] = "請選擇一個介於1到223之間的數值！";
catalog["备份路径不存在，是否自动创建？"] = "備份路徑不存在，是否自動創建？";
catalog["处理中"] = "處理中";
catalog["是"] = "是";
catalog["否"] = "否";
//------------------------------------------------------------------------
//in file--D:\trunk\units\adms\mysite\media\jslib\worktable.js
catalog["已登记指纹"] = "已登記指紋";
//人員判斷哪裡 驗證 輸入不合法
catalog["不合法"]="不合法";

//in file ..\..\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_emplevel.html
catalog["权限组列表"]="權限組列表";
catalog["门列表"]="門列表";
catalog["人员列表"]="人員列表";
catalog["浏览 "]="瀏覽";
catalog["可以进出的门"]="可以進出的門";
catalog["以人员查询"]="以人員查詢";
catalog["以门查询"]="以門查詢";
catalog["以权限组查询"]="以權限組查詢";

catalog["通讯密码"]="通訊密碼";
catalog["OK"] = "确定";
catalog["Cancel"] = "取消";
catalog["Save and Continue"] = "保存並繼續";
catalog["Browse"] = "浏览"
catalog["Browse "] = "浏览 "
