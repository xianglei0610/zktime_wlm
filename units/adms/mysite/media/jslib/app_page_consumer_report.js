$(function(){
	init_att_page();
//	$("#grid_frame").load(function(){
//		$("#id_page_load").hide()
//		//特殊处理 iframe session 过期后 刷新整个界面,重新登录
//		var title_flag = $("#grid_frame").contents().find("title")
//		if(title_flag.length>0 && title_flag.html().indexOf("登录")!=-1){
//			alert("会话已经超时,请重新登录!");
//			window.location.reload();
//		}
//	})
});

function init_att_page(){//初始化页面
	$("body").removeClass("indexBody").css("width","auto");
	$(".rightBox").eq(1).attr("class","rightBox1");
	$(".leftBox").eq(1).remove();
	var td=new Date();
	render_widgets($("#id_calculateform"));
	
	$("#id_cometime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-01")
	$("#id_endtime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-"+N2(td.getDate()))

	select_filter('1')
	
	$("#calculatetabs a").each(function(){
	    $(this).click(function(){
		    $("#id_page_load").show()
	    	$("#calculatetabs a").removeClass('current');
	        $(this).addClass('current');
	    })
	})
	
//	var refresh_current_page=function(){  //刷新表格
//		if (! valid_date()) return;
//		if (!setPostData()) return;
//		var typevalue=	parseInt($("#id_current_report").val());
//		switch(typevalue){
//			case 1:
//				AttRecAbnormite()
//				break;
//			case 2:
//				DailyReport()
//				break;
//			case 3:
//				AttShifts()
//				break;
//			case 5:
//				CalculateReport()
//				break;
//			case 8:
//				LeaveReport()
//				break;
//			case 9:
//				LEReport()
//				break;
//			case 10:
//				YCReport()
//				break;
//			case 11:
//				CardTimesReport()
//				break;
//			default:
//				break;
//		}
//	}

//	//统计
//	$("#id_calculate").click(function(){
//		if (!valid_date())
//			return;
//		if(!setPostData())
//			return ;
//		if(confirm(gettext("统计的时间可能会较长，请耐心等待"))==false)
//			return ;
//		$("#id_page_load").show()
//		$("#id_calculateform").ajaxSubmit({
//			url:"/att/AttReCalc/",			
//			type:"POST",
//			success:function(data){
//				$("#id_page_load").hide()
//				refresh_current_page();
//			}
//		});
//	});
	
//	//查询
//	$("#id_query").click(function(){
//		 refresh_current_page();
//	});
}


function N2(nc){
	var tt= "00" + nc.toString();
    tt=tt.toString();
    return tt.substr(tt.length-2);
}

	
var valid_date= function(){  //验证选择日期的有效性
	if ($("#id_cometime").val()=="" || $("#id_endtime").val()==""){
		alert("请选择开始日期和结束日期");
		return false;
	}
	var st=new Date($("#id_cometime").val().replace(/-/g,"/"));
	var et=new Date($("#id_endtime").val().replace(/-/g,"/"));
	if(st>et){
		alert(gettext("开始日期不能大于结束日期"));
		return false;
	}
	if(et>new Date()){
		alert(gettext("结束日期不能大于今天"));
		return false;
	}
	if(((et-st)>31*24*60*60*1000)|| (et.getMonth()>st.getMonth() && et.getDate()>=st.getDate())){
		alert(gettext("时间跨度不能超过一个月！ "));
		return false;			
	}
	return true
}

var setPostData = function (){//设置选人，选部门隐藏input值
	var depts=[];
	var ds=[];
	var self_services_emp = $("#id_self_services");//员工自助
    var pos_model=$("#search_id_pos_model").find("option:selected").val();
    var dining=$("#monitor_hall").find("option:selected").val();
    var operate=$("#monitor_operate").find("option:selected").val();
    $("input[name='Dining']").val(dining);
    $("input[name='operate']").val(operate);
    $("input[name='pos_model']").val(pos_model);
	
	var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
	$("#id_divsearch").find("input[name='deptIDs']").each(function(){
		ds.push($(this).val());
	})
	
	var depts=ds.toString();
	
	
	if(users.length!=0){
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(users.toString());
	}
	else
	{
		$("input[name='DeptIDs']").val(depts);
		$("input[name='UserIDs']").val("");
	}
	return true;
}

var get_where = function(){ // 获取查询条件
	if (!valid_date()) return;
	if (!setPostData()) return;
	where = ["pure"]
	
	
	if($("input#id_selectchildren").attr("checked")){
		where.push("deptIDschecked_child=on");
	}else{
		where.push("deptIDschecked_child=off");
	}	
	
	$("#id_calculateform input").each(function(){
		if ($(this).attr("name")!= "deptIDschecked_child")
		{
			if ($(this).attr("name")!= ""){
				where.push($(this).attr("name")+"="+$(this).val())
			}
		}
	})
	return where;
}

function load_data(url){
	$("#grid_frame").attr("src",url)
}



function time_hide_or_show(typeid)
{
	if(typeid=='9')
	{
		$('#monitor_cometime').hide();
		$('#monitor_endtime').hide();
		$('#div_cometime').hide();
		$('#div_endtime').hide();
		$('#monitor_operate').hide();
		$('#monitor_pos_model').hide();
	}
	else
	{
		$('#monitor_cometime').show();
		$('#monitor_endtime').show();
		$('#div_cometime').show();
		$('#div_endtime').show();
		$('#monitor_operate').show();
	}
}

function select_filter(typeid)
{
	time_hide_or_show(typeid)
	var users=$("#show_emp_tree");
	var emp_labor=$("#emp_labor");
	var dining=$("#monitor_hall");
	var meal=$("#monitor_meal");
	var operate=$("#monitor_operate");
	var st=$("#id_calculateform");
	var pos_model=$("#monitor_pos_model");
	
//	var check_btn=$("#check_operate");
	switch(typeid)
	{
		
		case '1'://发卡表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			break;
		case '2'://充值表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			
			break;
		case '3'://退款表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			break;
		case '4'://补贴表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			break;
		case '5'://退卡表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			break;
		case '6'://卡成本表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			break;
		case '7'://卡余额表
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			break;
		case '8'://无卡退卡表
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			break;
		case '9'://管理卡表
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			break;
		case '10'://挂失解挂表
			operate.show();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			break;
		case '11'://异常消费明细表
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			break;
		case '12'://消费明细表
			operate.show();
			dining.show();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.show();
			break;
		case '13'://换卡表
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			break;
		
		default:
			break;
	
	}
	
}


function show_table(curr_rep_id,src_url,show_desc){
	/**
	 * @parm:
	 * curr_rep_id: 当前报表id
	 * 
	 * src_url: 当前报表url
	 * 
	 * show_desc: 是否显示表下面的描述
	 */
	$("#id_current_report").val(curr_rep_id);
	if(!setPostData()){
		return ;
	}
	select_filter(curr_rep_id)
	var url = src_url+"?"+get_where().join("&");
	load_data(url)
	if (show_desc){
		$("#id_posexcept_desc").show();
	}else{
		$("#id_posexcept_desc").hide();
	}
}

function IssueCard(){ //发卡表
	show_table("1",'/page/pos/GetIssuecardReport/',false);
}
function ChargeRecord()//充值表
{
	show_table("2",'/page/pos/GetRechargeReport/',false);
}

function posReimburese()//退款表
{
	show_table("3",'/page/pos/GetReimbureseReport/',false);
}
 
function Allowance()//补贴表
{
	show_table("4",'/page/pos/GetAllowReport/',false);
}	

function ReturnCard(){//退卡表
	show_table("5",'/page/pos/GetReturnCardReport/',false);
}	

function posCarCost(){//卡成本
	show_table("6",'/page/pos/GetCostReport/',false);
}

function CarBalanceReport(){//卡余额表
	show_table("7",'/page/pos/GetCardBlanceReport/',false);
}

function NoCardReport(){//无卡退卡表
	show_table("8",'/page/pos/GetNoCardBlanceReport/',false);
}

function ManageCard(){//管理卡表
	show_table("9",'/page/pos/ManageCardReport/',false);
}


function posLostCard(){//挂失解挂表
	show_table("10",'/page/pos/LostCardReport/',false);
}


function errorLlistReport(){//异常消费明细表
	show_table("11",'/page/pos/GetErrorPosListReport/',true);
	var html = "<span >报表解释:</span><span style = 'font-weight:bold;' class='color_orange'>该报表记录的是消费设备上来的消费记录在系统中找不到对应的卡账号的记录。通常情况下是由于消费设备中的测试记录没有删除才会产生这样的情况！这些记录不会统计到系统账目中去！当前报表只充当异常查询的作用！</span>"
	$("#id_posexcept_desc").html(html)
	
}


function FlushCard_ic(){//消费明细表
	show_table("12",'/page/pos/GetPosListReport/',true);
	var html = "<span >消费日期异常解释:</span><span style = 'font-weight:bold;' class='color_orange'>（情况一）：系统使用过程中，设备时间发生错乱，导致员工的消费时间小于发卡日期！这种情况产生的异常记录不会影响账目结算结果。<br/>（情况二）：系统正式上线使用前，消费机中存在测试记录！实际消费金额计算公式：消费金额=实消费总额 — 异常合计总额</span>"
	$("#id_posexcept_desc").html(html)
}


function posReplenishCard(){//换卡表
	show_table("13",'/page/pos/PosReplenishCard/',false);
}

   
