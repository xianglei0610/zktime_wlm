$(function(){
	init_att_page();
//	$("#grid_frame").load(function(){
//	    $("#id_page_load").hide()
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
	
	$("#id_is_operate").click(function() {
		     if ($(this).attr("checked") == true) {
		        $("input[name='check_operate']").val("checked");
		    }
		    else{ 
		        $("input[name='check_operate']").val("");
		    }
		    });
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
	var dining=$("#monitor_hall").find("option:selected").val()
	var meal=$("#monitor_meal").find("option:selected").val()
	var operate=$("#monitor_operate").find("option:selected").val()
	$("input[name='Dining']").val(dining.toString());
	$("input[name='Meal']").val(meal.toString());
	$("input[name='Operate']").val(operate.toString());
	$("input[name='pos_model']").val(pos_model.toString());
    

	var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
	$("#id_divsearch").find("input[name='deptIDs']").each(function(){
		ds.push($(this).val());
	})
	
	var depts=ds.toString();
	
	var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
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


function select_filter(typeid)
{
	var users=$("#show_emp_tree");
	var emp_labor=$("#emp_labor");
	var dining=$("#monitor_hall");
	var meal=$("#monitor_meal");
	var operate=$("#monitor_operate");
	var st=$("#id_calculateform");
	var pos_model=$("#monitor_pos_model");
	var check_btn=$("#check_operate");
	switch(typeid)
	{
		
		case '1'://个人消费汇总
			operate.hide();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case '2'://部门汇总
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case '3'://餐厅汇总
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case '4':
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case '5':
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.show();
			break;
		case 5:
			operate.show();
			dining.hide();
			meal.hide();
			users.show();
			st.show();
			break;
		case 7:
			operate.hide();
			dining.hide();
			meal.hide();
			users.show();
			st.show();
			break;
		case 8:
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			st.hide();
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

function consumeCollect(){ //个人汇总表
	show_table("1",'/page/pos/GetEmpSummaryReport/',false);
}
function deptCollect()//部门汇总表
{
	show_table("2",'/page/pos/GetDeptSummaryReport/',false);
}

function diningCollect()//餐厅汇总表
{
	show_table("3",'/page/pos/GetDiningSummaryReport/',true);
	var html = "<span>汇总列名解释:</span><span style = 'font-weight:bold;' class='color_orange'>《餐厅消费总次数》= 设备所有刷卡记录汇总（包含了纠错记录）；《餐厅消费总合计》= 餐厅扣款刷卡记录消费汇总（包含了纠错记录）；《计次结算》= 设备计次模式汇总；《纠错合计》= 纠错记录汇总；《扣款消费次数结算》=《设备消费总次数》— 《纠错总次数》- 《计次结算》—《异常消费次数》；《实消费金额结算》=《设备消费总合计》— 《纠错合计》— 《异常消费金额结算》；《系统金额结算》=《实消费金额结算》+《补单合计》；</span>"
	$("#id_posexcept_desc").html(html)
	
}
 
function deviceCollect()//设备汇总表
{
	show_table("4",'/page/pos/GetDeviceSummaryReport/',true);
	var html = "<span>汇总列名解释:</span><span style = 'font-weight:bold;' class='color_orange'>《设备记录总次数》= 设备所有刷卡记录汇总；《消费总次数》= 设备扣款刷卡记录汇总（包含了纠错记录）；《设备消费总合计》= 设备所有刷卡记录消费汇总（包含了纠错记录）；《计次结算》= 设备计次模式汇总；《纠错合计》= 设备纠错记录汇总；《扣款消费次数结算》=《设备消费总次数》— 《纠错总次数》- 《计次结算》—《异常消费次数》；《实消费金额结算》=《设备消费总合计》— 《纠错合计》— 《异常消费金额结算》；《系统金额结算》=《实消费金额结算》+《补单合计》；</span>"
	$("#id_posexcept_desc").html(html)
	
}	

function szCollect(){//现金收支汇总表
	show_table("5",'/page/pos/GetSzSummaryReport/',false);
}	


   
