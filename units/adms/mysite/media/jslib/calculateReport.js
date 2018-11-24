$(function(){
	init_att_page();
});

function init_att_page(){//初始化页面
	$("body").removeClass("indexBody").css("width","auto");
	$(".rightBox").eq(1).attr("class","rightBox1");
	$(".leftBox").eq(1).remove();
	var td=new Date();
	render_widgets($("#id_calculateform"));
	
	$("#id_cometime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-01")
	$("#id_endtime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-"+N2(td.getDate()))
	load_description();
	$("#id_attexcept_desc").hide();
	
	$("#calculatetabs a").each(function(){
	    $(this).click(function(){
	    	$("#calculatetabs a").removeClass('current');
	        $(this).addClass('current');
	        $("#id_page_load").show();
	    })
	})
	
	var refresh_current_page=function(){  //刷新表格
//		if (! valid_date()) return;
//		if (!setPostData()) return;
		var typevalue=	parseInt($("#id_current_report").val());
		switch(typevalue){
			case 1:
				AttRecAbnormite()
				break;
			case 2:
				DailyReport()
				break;
			case 3:
				AttShifts()
				break;
			case 5:
				CalculateReport()
				break;
			case 8:
				LeaveReport()
				break;
			case 9:
				LEReport()
				break;
			case 10:
				YCReport()
				break;
			case 11:
				CardTimesReport()
				break;
			default:
				break;
		}
	}

	//统计
	$("#id_calculate").click(function(){
//		if (!valid_date())
//			return;
//		if(!setPostData())
//			return ;
		if(confirm(gettext("统计的时间可能会较长，请耐心等待"))==false)
			return ;
		$("#id_page_load").show()
		var where = get_where();
		where.shift();  // 去掉数组第一个 pure
		var url = "/att/AttReCalc/?"+where.join("&");
		$.ajax({
			url:url,
			type:"POST",
			timeout: 600000,    //10分钟
			success:function(ret){
				$("#id_page_load").hide();
				refresh_current_page();
			}
		});
	});
	
	//查询
	$("#id_query").click(function(){
		 $("#id_page_load").show();
		 refresh_current_page();
	});
}


function N2(nc){
	var tt= "00" + nc.toString();
    tt=tt.toString();
    return tt.substr(tt.length-2);
}
function load_description()
{
	$.ajax({
		url:"/att/getallexcept/",
		dataType:"json",
		type:"POST",
		success:function(ret){
			var html=""
			data=ret.data
			for(var i=0;i<data.length;i++)
			{
				var tmp=data[i]
				html+="<span>"+tmp[0]+":<span class='color_orange'>"+ tmp[2] +"( "+tmp[1]+" )</span></span>&nbsp;&nbsp;";
			}
			$("#id_attexcept_desc").html(html);
		}
	});
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
	var users=[];
	var self_services_emp = $("#id_self_services");//员工自助
	if(self_services_emp.length !=0){//员工自助
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(self_services_emp.val());
	}else{
		if ($("#id_dept_all").attr("checked")){
			//以部门为主
			
			$("input[name='dept_child']").val($("#id_selectchildren").attr("checked")?"1":"0")
//			alert("before get deptid")
			$("#id_divsearch").find("input[name='deptIDs']").each(
				function(){
				depts.push($(this).val());
			});
//			alert("after get deptid")
//			alert("before pingcou deptid")
			$("input[name='DeptIDs']").val(depts.length==0?"":depts.toString());
//			alert("after pingcou deptid")
			$("input[name='UserIDs']").val("");	
		}else{
			//以选择的人员为主
			users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
			$("input[name='UserIDs']").val(users.length == 0?"":users.toString());	
			$("input[name='DeptIDs']").val("");
		}
	}
	return true;
}

var get_where = function(){ // 获取查询条件
	if (!valid_date()) return;
	if (!setPostData()) return;
	where = ["pure"]
	$("#id_calculateform input").each(function(){
		if ($(this).attr("name")!= ""){
			where.push($(this).attr("name")+"="+$(this).val())
		}
	})
	return where;
}

function load_data(url){
	$("#grid_frame").attr("src",url)
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
	var url = src_url+"?"+get_where().join("&");
	load_data(url)
	if (show_desc){
		$("#id_attexcept_desc").show();
	}else{
		$("#id_attexcept_desc").hide();
	}
}

function AttRecAbnormite(){ //统计结果详情
	show_table("1",'/page/att/RecAbnormite/',false);
}
function DailyReport()//每日考勤统计表
{
	show_table("2",'/page/att/DayList/',true);
}

function AttShifts()//考勤明细表
{
	show_table("3",'/page/att/AttShiftsBase/',true);
}
 
function CalculateReport()//考勤统计汇总表
{
	show_table("5",'/page/att/EmpSum/',true);
}	

function LEReport(){//统计每天最早与最晚记录
	show_table("9",'/page/att/FirstLast/',false);
}	

function YCReport(){//考勤异常明细表
	show_table("10",'/page/att/DayAbnormal/',false);
}

function CardTimesReport(){//打卡详情表
	show_table("11",'/page/att/CardTimes/',false);
}

function LeaveReport(){//请假汇总表
	show_table("8",'/page/att/ExceptionSum/',true);
}
   
