// -*- coding: utf-8 -*-
___f=function(){
jQuery.validator.messages.required="Required"
jQuery.validator.messages.email="Not an email address"
jQuery.validator.messages.date="Please input a valid date: yyyy/mm/dd."
jQuery.validator.messages.dateISO="Please input a valid (ISO) date: yyyy-mm-dd."
jQuery.validator.messages.wZBaseDateField="Please input a valid date: yyyy-mm-dd."
jQuery.validator.messages.wZBaseDateTimeField="Please input a valid date: yyyy-mm-dd hh:mm:ss."
jQuery.validator.messages.wZBaseTimeField="Please input valid time: hh:mm:ss."
jQuery.validator.messages.wZBaseIntegerField="Please input an integer."
jQuery.validator.messages.number="Please input a valid value."
jQuery.validator.messages.digits="Only numeric allowed"
jQuery.validator.messages.equalTo="Different"
jQuery.validator.messages.minlength=$.validator.format("at least {0} character(s)")
jQuery.validator.messages.maxlength=$.validator.format("at most {0} character(s)")
jQuery.validator.messages.rangelength=$.validator.format("between {0} and {1} characters")
jQuery.validator.messages.range=$.validator.format("between {0} and {1}")
jQuery.validator.messages.max=$.validator.format("Please input a value not larger than {0}.")
jQuery.validator.messages.min=$.validator.format("Please input a value not smaller than {0}.")
jQuery.validator.messages.xPIN="only numeric or letter allowed"
jQuery.validator.messages.xNum="only numeric allowed"
jQuery.validator.messages.xMobile="Wrong mobile phone number"
jQuery.validator.messages.xTele="Wrong fixed-line telephone number"
jQuery.validator.messages.xSQL="\" or \' not allowed."
}

___f();

if(typeof(catalog)=="undefined") {catalog={}}

//in file--D:\trunk\units\adms\mysite/templates\advenquiry.html
catalog["请选择一个字段"] = "Please select a filed.";
catalog["'满足任意一个' 值域必须是以','隔开的多个值"] = "Only multiple value divided with ',' can meet any ' value range.";
catalog["输入的值错误"] = "Wrong input value";
//in file--D:\trunk\units\adms\mysite/templates\base_page_frame.html
catalog["确定注销系统?"] = "Are you sure to log out of the system?";
catalog["通讯失败"] = "Failure";
catalog["确定"] = "OK";
catalog["确认"] = "OK";
//in file--D:\trunk\units\adms\mysite/templates\data_edit.html
catalog["日志"] = "Logs";
//in file--D:\trunk\units\adms\mysite/templates\data_list.html
//in file--D:\trunk\units\adms\mysite/templates\DbBackupLog_list.html
catalog["请选择一条历史备份记录!"] = "Please select a history backup entry.";
catalog["还原成功!"] = "Restored successfully";
//in file--D:\trunk\units\adms\mysite/templates\DbBackupLog_opform_OpBackupDB.html
catalog["间隔时间不能超过一年"] = "Interval cannot exceed one year.";
catalog["间隔时间不能小于24小时"] = "Interval cannot be less than 24 hours.";
catalog["在当前时间的一个小时内只能备份一次"] = "Backup can be done only once within one hour of current time!";
catalog["请先在服务控制台中设置数据库备份路径"] = "Please set the database backup path in the service console first";
//in file--D:\trunk\units\adms\mysite/templates\DbBackupLog_opform_OpInitDB.html
catalog["全部"] = "All";
//in file--D:\trunk\units\adms\mysite/templates\restore.html
catalog["数据格式必须是json格式!"] = "The data must be in json format.";
//in file--D:\trunk\units\adms\mysite\iclock\templates\Area_opform_OpAdjustArea.html
catalog["请选择人员!"] = "Please select a person!";
catalog["考勤"] = "Attendance";
//in file--D:\trunk\units\adms\mysite\iclock\templates\Device_edit.html
catalog["设备名称不能为空"] = "The name of device cannot be empty.";
catalog["设备序列号不能为空"] = "The device serial number cannot be empty.";
catalog["通讯密码必须为数字"] = "The communication password must be a numeric.";
catalog["请输入一个有效的IPv4地址"] = "Please input a valid IPv4 address.";
catalog["请输入一个有效的IP端口号"] = "Please input a valid IP port number.";
catalog["请输入一个RS485地址"] = "Please input a RS485 address.";
catalog["RS485地址必须为1到63之间的数字"] = "A RS485 address must be a numeric between 1 and 63.";
catalog["请选择串口号"] = "Please select a serial port number.";
catalog["请选择波特率"] = "Please select a baud rate.";
catalog["请选择设备所属区域"] = "Please select an area for the device.";
catalog["串口：COM"] = "Serial port COM";
catalog[" 的RS485地址："] = "'s RS485 address";
catalog[" 已被占用！"] = " has been occupied!";
catalog[" 已添加过波特率不为："] = " has added the device not with the baudrate:";
catalog[" 的设备！同一个串口下不允许存在多个波特率不同的设备。请重新选择波特率！"] = ". Please make sure that one serial port can only exist devices with the same baudrate and choose the baudrate again!";
catalog["后台通讯忙，请稍后重试！"] = "Background communication is busy, please try again later!";
catalog["提示：设备连接成功，但获取设备扩展参数失败，继续添加？"] = "Tip: The device is connected successfully, but failed to get the extended parameters for device, Continue to add?";
catalog["提示：设备连接成功，但控制器类型与实际不符，将修改为"] = "Tip: The device is connected successfully, but the type of the access control panel differs from the actual one, modify it to ";
catalog["门控制器，继续添加？"] = "door(s) control panel. Continue to add?";
catalog["提示：设备连接成功，确定后将添加设备！"] = "Tip: The device is connected successfully,and types of the access control panels match. Add the device after confirmation!";
catalog["提示：设备连接失败（错误码："] = "Tip: The device fails to be connected (error code:";
catalog["），确定添加该设备？"] = "). Are you sure to add this device?";
catalog["提示：设备连接失败（原因："] = "Tip: The device fails to be connected (cause: ";
catalog["您选择了[新增时删除设备中数据]，系统将自动删除设备中的数据(事件记录除外)，确定要继续？"] = "You have checked [Clear Data in the Device when Adding], the system will automatically clear the data (except the event log) in the device, sure to continue?";
catalog["您没有选择[新增时删除设备中数据]，该功能仅用于系统功能演示和测试。请及时手动同步数据到设备，以确保系统中和设备中权限一致，确定要继续？"] = "You haven't checked [Clear Data in the Device when Adding], this function is only used for demonstration and testing of the system. Please synchronize the data to the device manually, to ensure the consistency of the levels in system and device, sure to continue?";
catalog["编辑设备信息("] = "edit device information";
catalog["对不起，您没有访问该页面的权限，不能浏览更多信息！"] = "Sorry, you have no right to visit this page, so you cannot browse more information!";
//in file--D:\trunk\units\adms\mysite\iclock\templates\Dev_RTMonitor.html
catalog["确定要清除命令队列？"] = "Are you sure to clear command queues?";
catalog["清除缓存命令成功！请及时手动同步数据到设备，以确保系统中和设备中权限一致！"] = "The cache commands are cleared successfully!Please synchronize the data to the device manually, to ensure the consistency of the levels in system and device!";
catalog["清除缓存命令失败!"] = "The cache commands are not cleared successfully!";
//in file--D:\trunk\units\adms\mysite\att\templates\att_USER_OF_RUN.html
catalog["员工排班表"] = "Personnel schedule table";
catalog["临时排班表"] = "Temporary schedule table";
catalog["排班时间段详细明细"] = "Schedule shift TimeTable details";
catalog["排班时间段详细明细(仅显示三个月)"] = "schedule shift TimeTable details (only three months)";
catalog["排班时间段详细明细(仅显示到年底)"] = "schedule shift TimeTable details (only to year-end";
//in file--D:\trunk\units\adms\mysite\att\templates\NUM_RUN_edit.html
catalog["请选择时段"] = "Select shift TimeTable";
catalog["选择日期"] = "Select date";
catalog["第"] = "No.";
catalog["天"] = "day";
catalog["周的周期不能大于52周"] = "A weekly period cannot exceed 52 weeks.";
catalog["月的周期不能大于12个月"] = "A monthly period cannot exceed 12 months.";
catalog["第"]="No.";
catalog["天"] = "day";
//in file--D:\trunk\units\adms\mysite\att\templates\NUM_RUN_list.html
catalog["时间段明细"] = "Shift TimeTable details";
catalog["确定删除该时段吗？"] = "Are you sure to delete this shift TimeTable?";
catalog["操作失败 {0} : {1}"] = "operation failure {0} : {1}";
//in file--D:\trunk\units\adms\mysite\att\templates\NUM_RUN_opform_OpAddTimeTable.html
catalog["已选择"] = "selected";
//in file--D:\trunk\units\adms\mysite\att\templates\USER_OF_RUN_opform_OpAddTempShifts.html
catalog["日期格式输入错误"] = "Wrong date format";
catalog["日期格式不正确！"] = "The date format is wrong!"
catalog["夏令时名称不能为空！"] = "The DST name cannot be null!"
catalog["起始时间不能和结束时间相等！"] = "Start time cannot be equal to the end time!";
//in file--D:\trunk\units\adms\mysite\att\templates\USER_OF_RUN_opform_OpAddUserOfRun.html
catalog["请选择一个班次"] = "Select a shift";
catalog["结束日期不能小于开始日期!"] = "End date cannot be earlier than start date!";
catalog["请输入开始日期和结束日期! "] = "Please input start date and end date.";
catalog["只能设置一个班次! "] = "You can only set one shift.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccAntiBack_edit.html
catalog["当前选择设备的扩展参数获取失败，无法对该设备进行反潜设置！"] = "The current selected device fails to obtain extension parameter, so Anti-Passback setting is unavailable to the device.";
catalog["读取到错误的设备信息，请重试！"] = "Wrong device information is read. Please try again!";
catalog["或"] = " or ";
catalog["反潜"] = " Anti-Passback";
catalog["读头间反潜"] = "Anti-Passback between readers";
catalog["反潜"] = " Anti-Passback";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccAntiBack_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccDoor_edit.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccFirstOpen_edit.html
catalog["当前门:"] = "Current Door:";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccFirstOpen_list.html
catalog["删除开门人员"] = "Delete an opening person";
catalog["请先选择要删除的人员！"] = "First select the person you want to delete.";
catalog["确认要从首卡常开设置信息中删除开门人员？"] = "Are you sure to delete the opening person from the first card always-open setting information?";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccFirstOpen_opform_OpAddEmpToFCOpen.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccInterLock_edit.html
catalog["当前选择设备的扩展参数获取失败，无法对该设备进行互锁设置！"] = "The current selected device fails to obtain extension parameter, so interlock setting is unavailable to the device.";
catalog["门:"] = "Door: ";
catalog["与"] = "and";
catalog["互锁"] = " Interlock";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccInterLock_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLevelSet_list.html
catalog["数据下载进度"] = "Data Downloading Progress";
catalog["设备名称"] = "Device Name";
catalog["总进度"] = "Total Progress";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLevelSet_opform_OpAddEmpToLevel.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLinkageIO_edit.html
catalog["当前选择设备的扩展参数获取失败，无法对该设备进行联动设置！"] = "The current selected device fails to obtain extension parameter, so linkage setting is unavailable to the device.";
catalog["当前选择设备的扩展参数异常,请删除设备并重新添加后重试！"] = "The current selected device has exceptional extension parameter. Please delete the device and then re-add it to try again.";
catalog["请输入联动设置名称！"] = "Please input a linkage setting name.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccLinkageIO_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMap_edit.html
catalog["请选择地图！"] = "Please choose the map!";
catalog["图片格式无效！"] = "Invalid picture format!";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardEmpGroup_list.html
catalog["浏览多卡开门人员组："] = "Browse Multi-Card opening personnel group:";
catalog[" 的人员"] = " member";
catalog["当前不存在多卡开门人员组"] = "There is no Multi-Card opening personnel group at present.";
catalog["删除人员"] = "Delete a person";
catalog["确认要从多卡开门人员组中删除人员？"] = "Are you sure to delete the person from the Multi-Card opening personnel group?";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardEmpGroup_opform_OpAddEmpToMCEGroup.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardSet_edit.html
catalog["请至少在一个组内填入开门人数！"] = "Please input a number of opening personnel in one group at least.";
catalog["至少两人同时开门！"] = "At least two persons can open the door at the same time!";
catalog["最多五人同时开门！"] = "At most five persons can open the door at the same time!";
catalog["人"] = "Person";
catalog["您还没有设置多卡开门人员组！请先添加！"] = "You have not set any Multi-Card opening personnel group. Please add one first.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccMoreCardSet_list.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccTimeSeg_edit.html
catalog["请在文本框内输入有效的时间！"] = "Please input valid time in the field.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\AccWiegandFmt_list.html
catalog["对不起,您没有韦根卡格式设置的权限,不能进行当前操作！"] = "Sorry, you have no right to set the Wiegand card format, and cannot perform the current operation.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Door_Mng.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Door_Set.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Electro_Map.html
catalog["添加门到当前地图"] = "Add doors onto the current map";
catalog["请选择要添加的门！"] = "Please choose the doors you want to add!";
catalog["确定要删除当前电子地图："] = "Confirm that you will delete the current map: ";

//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_EmpLevel_Byemp.html
catalog["浏览人员："] = "Browse personnel:";
catalog[" 所属权限组"] = " access level";
catalog["当前不存在人员"] = "No person now";
catalog["删除所属权限组"] = "Delete access level";
catalog["请先选择要删除的权限组！"] = "Please select the access level you want to delete.";
catalog["确认要删除人员所属权限组？"] = "Are you sure to delete the access level?";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_EmpLevel_Bylevel.html
catalog["数据处理进度"] = "Data Processing Progress";
catalog["浏览权限组："] = "Browse access level ";
catalog[" 的开门人员"] = " opening personnel";
catalog["当前不存在权限组"] = "No access level now";
catalog["从权限组中删除"] = "Delete from access level";
catalog["权限组列表"]="Access Level List";
catalog["门列表"]="Doors List"
catalog["人员列表"]="Personnel List"
catalog["浏览 "]="Browse "
catalog["可以进出的门"]=" having Level to Access"
catalog["当前不存在人员"]="No Personnel"
catalog["以人员查询"]="By Personnel"
catalog["以门查询"]="By Door "
catalog["以权限组查询"]="By Access Level"
catalog["确认要从权限组中删除人员？"] = "Are you sure to delete the person from the access level?";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Monitor_All.html
catalog["远程开门"] = "Remote Open";
catalog["选择开门方式"] = "Choose Door Opening Mode";
catalog["开门："] = "Open the Door for ";
catalog[" 秒"] = " Second(s)";
catalog["常开"] = "Normal Open";
catalog["启用当天常开时间段"] = "Enable Intraday Passage Mode Time Zone";
catalog["远程关门"] = "Remote Close";
catalog["选择关门方式"] = "Choose Door Closing Mode";
catalog["关门"] = "Close the Door";
catalog["禁用当天常开时间段"] = "Disable Intraday Passage Mode Time Zone";
catalog["发送请求失败！"] = "Failed to send the request!";
catalog["发送请求成功！"] = "Successfully sending the request!";
catalog["发送请求失败，请重试！"] = "Failed to send the request! Please try again!";
catalog["当前没有符合条件的门！"] = "There is no door that meets the condition.";
catalog["请输入有效的开门时长！必须为1-254间的整数！"] = "Please enter a valid door-opened interval! Must be an integer between 1-254!";
catalog["禁用"] = "Disabled";
catalog["离线"] = "Offline";
catalog["报警"] = "Alarm";
catalog["门开超时"] = "Opening Timeout";
catalog["关闭"] = "Closed";
catalog["打开"] = "Opened";
catalog["无门磁"] = "No Door Sensor";
catalog["当前设备状态不支持该操作！"] = "Current device status does not support this operation!";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_alarm.html
catalog["导出报表"] = "Export Report";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_allevent.html
catalog["设置定时获取记录时间"] = "Set the time for obtaining new entries";
catalog["每天"] = "Obtain new entries ";//特殊翻译请核对页面
catalog[" 点自动从设备获取新记录"] = " o'clock each day automatically.";
catalog["注：请确保服务器在设置的时间点处于开机状态。"] = "Note: Make sure the server is turned on during the time you set.";
catalog["定时下载记录时间设置成功！该设置将在软件服务或者操作系统重启后生效！"] = "Setting the time succeed! The settings will take effect after rebooting the software service or the operating system";
catalog["定时下载记录事件设置失败！请重试！"] = "Setting the time failed! Please try again!";
catalog["请输入有效的时间点(0-23)！"] = "Please input a valid time(0-23)!";
catalog["无"] = "None";
catalog["注：1.请确保服务器在设置的时间点处于开机状态。<br/> 2.如需设置多个时间点，请以逗号分开。"] = "Note: 1.Please ensure that the server is turned on in the set time. <br/> 2. To set multiple time points, separated by commas.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Acc_Reportform_emplevel.html
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Device_opform_OpChangeIPOfACPanel.html
catalog["请输入有效的IPv4地址！"] = "Please input a valid IPv4 address.";
catalog["请输入有效的网关地址！"] = "Please input a valid gateway address.";
catalog["请输入有效的子网掩码！"] = "Please input a valid subnet mask.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Device_opform_OpCloseAuxOut.html
catalog["获取设备扩展参数失败，当前操作不可用！"] = "Failed to obtain the extended parameters for device, the current operation is not available!";
catalog["请选择要关闭的辅助输出点！"] = "Please check the auxiliary port you want to close.";
//in file--D:\trunk\units\adms\mysite\iaccess\templates\Device_opform_OpSearchACPanel.html
catalog["退出"] = "Exit";
catalog["正在搜索中,请等待!"] = "Searching. Please wait!";
catalog["当前共搜索到的门禁控制器总数为："] = "The total number of access control panels found now is:";
catalog["自定义设备名称"] = "Customize Device Name";
catalog["新增时删除设备中数据"] = "Clear Data in the Device when Adding";
catalog["设备名称不能为空，请重新添加设备！"] = "The device name cannot be empty. Please add a device again.";
catalog["的设备添加成功！"] = " device is added successfully!";
catalog["已添加设备数："] = "number of devices added";
catalog["IP地址："] = "IP address";
catalog[" 已存在！"] = "already exist!";
catalog["序列号："] = "Serial number";
catalog["IP地址为："] = "IP address:";
catalog[" 的设备添加失败！原因："] = " failed to be added, reason: ";
catalog[" 的设备添加失败！"] = " device fails to be added!";
catalog[" 的设备添加异常！"] = " device is added exceptionally.";
catalog["的设备添加成功，但设备扩展参数获取失败！"] = " device is added successfully, but its extension parameter fails to be obtained.";
catalog["设备连接成功，但无数据返回，添加设备失败！"] = "The device is connected successfully, but there is no data returned, indicating the device fails to be added.";
catalog["设备连接失败(错误码："] = "The device fails to be connected (error code: ";
catalog[")，无法添加该设备！"] = "), so it cannot be added.";
catalog["设备连接失败(原因："] = "The device fails to be connected (cause:";
catalog["修改设备IP地址"] = "Modify Device IP Address";
catalog["原IP地址"] = "Original IP address";
catalog["新IP地址"] = "New IP address";
catalog["网关地址"] = "Gateway address";
catalog["子网掩码"] = "Subnet mask";
catalog["请输入设备通讯密码:"] = "Input a device communication password:";
catalog["新的IP地址不能为空！"] = "The new IP address cannot be empty.";
catalog["请输入一个有效的IPv4地址！"] = "Please input a valid IPv4 address.";
catalog["请输入一个有效的网关地址！"] = "Please input a valid gateway address.";
catalog["请输入一个有效的子网掩码！"] = "Please input a valid subnet mask.";
catalog["该IP地址的设备已存在或该IP地址已被使用，不能添加！请重新输入！"] = "There is already a device with this IP address or this IP address has been used, so it cannot be added. Please input another.";
catalog["操作失败！原因："] = "The operation failed! Reason:";
catalog["设备连接成功，但修改IP地址失败！"] = "The device is connected successfully, but the IP address fails to be modified.";
catalog["设备连接失败，故修改IP地址失败！"] = "The device fails to be connected, so the IP address fails to be modified.";
catalog["没有搜索到门禁控制器！"] = "No access control panel found.";
catalog["获取到错误的设备类型！"] = "Wrong device type value!";
//in file--D:\trunk\units\adms\mysite\personnel\templates\Department_list.html
catalog["显示部门树"] = "Show department tree";
catalog["隐藏部门树"] = "Hide department tree";
//in file--D:\trunk\units\adms\mysite\personnel\templates\EmpChange_edit.html
catalog["请选择一个调动栏位"] = "Please select a transfer position.";
//in file--D:\trunk\units\adms\mysite\personnel\templates\EmpItemDefine_list.html
catalog["部门花名册"] = "department roll";
catalog["学历构成分析表"] = "education composition analysis";
catalog["人员流动表"] = "personnel turnover report";
catalog["人员卡片清单"] = "personnel card list";
catalog["请选择开始日期和结束日期"] = "Please select start date and end date.";
catalog["开始日期不能大于结束日期"] = "Start date cannot be later than end date.";
//in file--D:\trunk\units\adms\mysite\personnel\templates\Employee_edit.html
catalog["图片格式无效!"] = "Invalid picture format";
catalog["人员编号必须为数字"] = "Personnel No. must be numeric.";
catalog["请输入有效的E_mail!"]="Please enter a valid E_mail!";
catalog["身份证号码不正确"] = "Wrong ID card number";
catalog["没有可选的门禁权限组！"] = "No available access level .";
catalog["指纹模板错误，请立即联系开发人员！"] = "Fingerprint template error,please contact us as soon as possible!";
catalog["指纹模板错误，请重新登记！"] = "Fingerprint template error,please register the fingerprint again!";

catalog["修改密码"] = "Modify Password";
catalog["旧密码："] = "Old Password:";
catalog["新密码："] = "New Password:";
catalog["确认密码："] = "Confirm Password:";
catalog["最大6位整数"] ="max 6-digit integer";

//in file--D:\trunk\units\adms\mysite\personnel\templates\Employee_list.html
//in file--D:\trunk\units\adms\mysite\personnel\templates\Employee_opform_OpAddLevelToEmp.html
//in file--D:\trunk\units\adms\mysite\personnel\templates\IssueCard_opform_OpBatchIssueCard.html
catalog["每次发卡数量不能超过100"] = "No more than 100 cards can be issued at a time.";
catalog["起始编号长度不能超过"] = "The start number length cannot exceed ";
catalog["位"] = " digits.";
catalog["结束编号长度不能超过"] = "The end number length cannot exceed";
catalog["起始人员编号与结束人员编号的长度位数不同！"] = "The start No. and end No. are different in length.";
//in file--D:\trunk\units\adms\mysite\personnel\templates\LeaveLog_list.html
//in file--D:\trunk\units\adms\mysite\worktable\templates\worktable_common_monitor.html
catalog["点击查看消息详情"] = "Click to view message detail";
catalog["删除该消息"] = "Delete this message";
catalog["公告详情"] = "Notice Details";
//in file--D:\trunk\units\adms\mysite\worktable\templates\worktable_common_opt.html
catalog["保存成功!"] = "Saved Successfully";
catalog["人员选择:"] = "Select a Person:";
//in file--D:\trunk\units\adms\mysite\worktable\templates\worktable_common_search.html
catalog["人员查询"] = "personnel query";
catalog["人员编号"] = "Personnel No.";
catalog["姓名"] = "Name";
catalog["身份证号查询"] = "ID card number query";
catalog["身份证号码"] = "ID card number";
catalog["考勤设备查询"] = "attendance device query";
catalog["离职人员查询"] = "Departure personnel query";
catalog["考勤原始数据查询"] = "original attendance data query";
catalog["员工调动查询"] = "personnel transfer query";
catalog["卡片查询"] = "card query";
catalog["卡号"] = "card number";
catalog["部门查询"] = "department query";
catalog["部门编号"] = "department number";
catalog["部门名称"] = "department name";
catalog["补签卡查询"] = "append log query";
catalog["服务器加载数据失败,请重试!"] = "The server fails to load data. Please try again.";
//in file--D:\trunk\units\adms\mysite\media\jslib\calculate.js
catalog["补签卡"] = "append log";
catalog["补请假"] = "append leave";
catalog["新增排班"] = "add schedule";
catalog["临时排班"] = "temporary schedule";
catalog["结束日期不能大于今天"] = "End date cannot be later than today.";
catalog["统计只能当月日期，或者天数不能超过开始日期的月份天数！ "] = "Statistics involve only the dates of the month, or the number of days involved cannot exceed the number of the days contained in the month of the start date.";
catalog["统统计的时间可能会较长，请耐心等待"] = "Statistics of the time may be longer, please be patient";
catalog["请选择人员或部门"] = "Please select a person or department.";
catalog["统计结果详情"] = "statistic result";
catalog["每日考勤统计表"] = "daily statistic table";
catalog["考勤明细表"] = "attendance detail";
catalog["请假明细表"] = "leave detail";
catalog["考勤统计汇总表"] = "statistic summary";
catalog["原始记录表"] = "AC log table";
catalog["补签卡表"] = "append log table";
catalog["请假汇总表"] = "leave summary";
catalog["请选择开始日期或结束日期!"] = "Please select start date or end date.";
catalog["开始日期不能大于结束日期!"] = "Start date cannot be later than end date.";
catalog["最多只能查询31天的数据!"] = "At most 31 days of data can be queried.";
catalog["请在查询结果中选择人员！"] = "Please a person from the query result.";
catalog["取消"] = "Cancel";
//in file--D:\trunk\units\adms\mysite\media\jslib\CDrag.js
catalog["展开"] = "Unfold";
catalog["收缩"] = "Fold";
catalog["自定义工作面板"] = "Customize Work Panel";
catalog["锁定"] = "lock";
catalog["解除"] = "unlock";
catalog["常用操作"] = "Common Operation";
catalog["常用查询"] = "Common Query";
catalog["考勤快速上手"] = "Attendance Quick Start";
catalog["门禁快速上手"] = "Access Control Quick Start";
catalog["系统提醒、公告"] = "System Reminder and Notice";
catalog["人力构成分析"] = "Personnel Composition Analysis";
catalog["最近门禁异常事件"] = "Recent Access Control Exception";
catalog["本日出勤率"] = "Attendance Rate of the Day";
catalog["加载中......"] = "loading...";
//in file--D:\trunk\units\adms\mysite\media\jslib\datalist.js
catalog["是否"] = "Yes/No";
catalog["选择所有 {0}(s)"] = "Select all {0}(s)";
catalog["选择 {0}(s): "] = "Select {0}(s):";
catalog["服务器处理数据失败，请重试！"] = "The server fails to process data. Please try again!";
catalog["新建相关数据"] = "Create related data";
catalog["浏览相关数据"] = "Browse related data";
catalog["添加"] = "Add";
catalog["浏览"] = "Browse";
catalog["编辑"] = "Edit";
catalog["编辑选定记录"] = "edit this row ";
catalog["升序"] = "Ascend";
catalog["降序"] = "Descend";
//in file--D:\trunk\units\adms\mysite\media\jslib\datalistadd.js
catalog["该模型不支持高级查询功能"] = "This model does not support advanced query functions.";
catalog["高级查询"] = "Advanced Query";
catalog["导入"] = "Import";
catalog["请选择一个上传的文件!"] = "Please select a file to upload.";
catalog["标题行号必须是数字!"] = "A title row number must be a numeric.";
catalog["记录行号必须是数字!"] = "An entry row number must be a numeric.";
catalog["请选择xls文件!"] = "Please select an xls file.";
catalog["请选择csv文件或者txt文件!"] = "Please select a csv or txt file.";
catalog["文件标头"] = "file header";
catalog["文件记录"] = "file record";
catalog["表字段"] = "table filed";
catalog["请先上传文件！"] = "Please upload a file first.";
catalog["导出"] = "Export";
catalog["页记录数只能为数字"] = "The quantity of entries in a page can only be a numeric.";
catalog["页码只能为数字"] = "Page number can only be a numeric.";
catalog["记录数只能为数字"] = "The quantity of entries can only be a numeric.";
catalog["用户名"] = "User name";
catalog["动作标志"] = "Action flag";
catalog["增加"] = "Add";
catalog["修改"] = "Modify";
catalog["删除"] = "Delete";
catalog["其他"] = "Others";
//in file--D:\trunk\units\adms\mysite\media\jslib\electro_map.js
catalog["地图宽度到达上限(1120px)，不能再放大！"] = "Reach the upper limit of the map width(1120px), can not enlarge!";
catalog["地图宽度到达下限(400px)，不能再缩小！"] = "Reach the minimum of the map width(400px), can not reduced!";
catalog["地图高度到达下限(100px)，不能再缩小！"] = "Reach the minimum limit of the map height(100px), can not reduced!";
catalog["门图标的位置（Top或Left）到达下限，请稍作调整后再进行缩小操作！"] = "The location(Top or Left) of the door icon has reached minimum, please make some adjustments and then continue to narrow the map!";

//in file--D:\trunk\units\adms\mysite\media\jslib\importAndExport.js
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.plus.js
catalog["信息提示"] = "Tips";
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.plus.js
catalog["日期"] = "date";
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.zcommon.js
catalog["标签页不能多于6个!"] = "There cannot be more than 6 tabs.";
catalog["按部门查找"] = "Search by Department";
catalog["选择部门下所有人员"] = "Select all Personnel in the Department";
catalog["(该部门下面的人员已经全部选择!)"] = "(All the personnel under this department have been selected.)";
catalog["按人员编号/姓名查找"] = "Search by Personnel No./Name";
catalog["按照人员编号或姓名查找"] = "Search by Personnel No./Name";
catalog["查询"] = "query";
catalog["请选择部门"] = "select a department";
catalog["该部门下面的人员已经全部选择!"] = "All the personnel under this department have been selected.";
catalog["打开选人框"] = "open the selection box";
catalog["收起"] = "Close";
catalog["已选择人员"] = "Selected Personnel ";
catalog["清除"] = "Clear";
catalog["编辑还未完成，已临时保存，是否取消临时保存?"] = "The editing is not completed yet, and is saved temporarily. Do you want to cancel temporary saving?";
catalog["恢复"] = "Restore";
catalog["会话已经过期或者权限不够,请重新登入!"] = "The session has expired or your right is limited. Please log in again.";
//in file--D:\trunk\units\adms\mysite\media\jslib\jquery.zgrid.js
catalog["没有选择要操作的对象"] = "No object is selected for operation";
catalog["进行该操作只能选择一个对象"] = "Only one object can be selected for this operation.";
catalog["相关操作"] = "Related operation";
catalog["共"] = "Total";
catalog["记录"] = "Entry";
catalog["页"] = "Page";
catalog["首页"] = "First";
catalog["前一页"] = "Previous";
catalog["后一页"] = "Next";
catalog["最后一页"] = "Last";
catalog["选择全部"] = "All";
//in file--D:\trunk\units\adms\mysite\media\jslib\widgets.js
catalog["January February March April May June July August September October November December"] = "January February March April May June July August September October November December";
catalog["S M T W T F S"] = "S M T W T F S";
//---------------------------------------------------------
catalog["记录条数不能超过10000"] = "the max 10000";
catalog["请输入大于0的数字"] = "Please enter a number greater than 0";
catalog["当天存在员工排班时"] = "had schedule in current day";

catalog["暂无提醒及公告信息"] = "No reminder and notice";
catalog["关于"] = "About ";
catalog["版本号"] = "Version number";
catalog["本系统建议使用浏览器"] = "The browsers which we recommended";
catalog["显示器分辨率"] = "Monitor resolution";
catalog["及以上像素"] = "pixels and above";
catalog["软件运行环境"] = "The environment for running this software";
catalog["系统默认"] = "Default";

catalog["photo"] = "Photo";
catalog["table"] = "Table";

catalog["此卡已添加！"] = "This card has been added!";
catalog["卡号不正确！"] = "The card number is wrong!";
catalog["请输入要添加的卡号！"] = "Please input the card number!";
catalog["请选择刷卡位置！"] = "Please select the position of swiping card!";
catalog["请选择人员！"] = "Select a person!";
catalog["table"] = "Table";
catalog["table"] = "Table";
catalog["首字符不能为空!"]="The first character can not be empty!";
catalog["密码长度必须大于4位!"]="Password length must be greater than 4！";

catalog["当前列表中没有卡可供分配！"] = "There are no card can be assigned in the current list!";
catalog["当前列表中没有人员需要分配！"] = "There are no person need to assign card in the current list!";
catalog["没有已分配人员！"] = "There was no person that has been assgined!";
catalog["请先点击停止读取！"] = "Please stop to read the card number first!";
catalog["请选择需要分配的人员！"] = "Please select the person who need to assign card!";

catalog["请选择一个介于1到223之间的数值！"] = "Please specify a value between 1 and 223!";
catalog["备份路径不存在，是否自动创建？"] = "The backup path does not exist,create it automatically?";
catalog["处理中"] = "Processing"
catalog["是"] = "Yes"
catalog["否"] = "No"
//------------------------------------------------------------------------
//in file--D:\trunk\units\adms\mysite\media\jslib\worktable.js
catalog["已登记指纹"] = "Registered Fingerprint:"
//人员判断哪里 验证 输入不合法
catalog["不合法"] = "Illegal";

catalog["通讯密码"] = "Communication Password";

catalog["登记指纹功能只支持IE浏览器"] = "The function only supports IE brower.";

catalog["请安装指纹仪驱动"] = "Please install Fingerprint Reader Driver.";

catalog["解析xml文件出错"] = "Load xml failed!";

catalog["该通道已达最大访问量！"] = "The visitor number of the channel has reached the maximum value!";

catalog["当前没有可用的角色,请先添加角色"] = "No available role to choose now，please create one or more roles first!";

catalog["当前设备IP地址和服务器不在同一网段，请先将其调整到一个网段，再尝试添加！"] = "The device and server are in different network segment,please adjust them to be the same network segment and try again!";

catalog["数据库将备份到:"]="The database will be backuped to:";


catalog["所选的部门总数不能大于2000"]="Selected departments can not exceed 2000 total";


catalog["当前位置：梯控系统->梯控时间段->增加"]="Current Window: Elevator Access Control System -> Elevator Access Time Zones->Add"

catalog["当前位置"]="Current Window";

catalog["当前位置：梯控系统->梯控权限组->增加"]="Current Window: Elevator Access Control System -> Elevator Access Level->Add"
catalog["没有可选的梯控权限组！"] = "No available elevator level .";
catalog["楼层编号:"] = "Floor Number:";
catalog["楼层名称:"] = "Floor Name:";
catalog["楼层有效时间段:"] = "Floor Active Time Zone:";
catalog["楼层常开时间段:"] = "Floor Passage Mode Time Zone:";
catalog["继电器驱动时长"] = "lock open duration:";
catalog["将该设置应用到当前所有楼层:"] = "Apply this settings to all the floors of current elevator access control panel:";
catalog["必须设定楼层有效时间段才能启用该楼层。<br>将当前的设置信息应用于其他楼层，这里的当前楼层指的是当前电梯控制器控制的所有楼层。"] = "";
catalog["当前位置：梯控系统->楼层设置->详情"] = "Current Window: Elevator Access Control System -> Floor Setting->Detail";

catalog["比对验证中，请稍等!"] = "Verifying, please wait!";
catalog["验证失败，请重试!"] = "Failed! Please try again!";
catalog["10.0指纹算法许可失败!"] = "The fingerprint algorithm 10.0 license verifying failed!";
catalog["验证通过，登录系统!"] = "Verified,logging in the system!";
catalog["获取指纹失败，请重试!"] = "Failed to obtain fingerprint, please try again!";
catalog["所选的部门总数不能大于2000"]="Selected departments can not exceed 2000 total";

catalog["操作成功！"] = "The operation succeed!";
catalog["操作失败！"] = "The operation failed!";
catalog["服务器处理数据失败，请重试！错误码："] = "The server fails to process data. Please try again! Error code:";
catalog["重连间隔时间必须为整数！"] = "The reconnection inverval must be a numeric!";
catalog["设置成功，重启服务后生效！"]="Set successfully, the settings will take effect after rebooting the software service or the operating system";
catalog["设置成功！"] = "Set successfully!";
catalog["保存参数成功！"] = "Guardado correctamente!";
catalog["获取记录时间点不能为空！"] = "The time of obtaining new entries can not be empty!";
catalog["一体机，继续添加？"] = "access control device. Continue to add?";
catalog["用户注册失败，请检查设备配置"] = "Failed to register a user,please check the device configuration";
catalog["目前该功能仅支持IE系列及IE内核的浏览器，请更换！"] = "This function can only support IE seris browsers currently!";
catalog["请选择视频设备！"] = "Please choose a device!";
catalog["控件初始化失败，请确定视频设备类型是否选择正确或重装控件！"] = "Failed to initialize ocx, please make sure the device type is correct or reinstall ocx!";
catalog["预览失败"] = "Failed to preview";
catalog["条人员编号没有记录"] = "item of Staff Numbers have no record";
catalog["是否继续?"] = "Whether to continue?";
catalog["请选择上传文件!"] = "Please choose the upload files!";
catalog["导入人员编号文件"] = "Import staff Numbers files";
catalog["上传文件类型错误,必须为以下文件类型：xls/txt/csv"] = "Upload file types error, must be one of the following file types: XLS/TXT/CSV";