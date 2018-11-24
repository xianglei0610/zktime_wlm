$(function(){
	init_meeting_page();
	showOrHide();
	showOrHide2();
});

function showOrHide(){
	$("#showMA").click(function(){
		if($("#test_div").is(":hidden")){//:hidden  :visible
			$("#test_div").show();
			$(".test_m").show();
		}else{
			$("#test_div").hide();
			$(".test_m").hide();
		};
	});
	$("#test_div").hover(function(){
		$("#test_div").show();
		$(".test_m").show();
	},function(){
		if($(".test_m").is(":visible")){//:hidden  :visible
			$(".test_m").fadeOut(500);
			$("#test_div").fadeOut(500);
			var meeting_Names = []
			$("input[name='meetingAll']").each(function(){
				if ($(this).attr("checked")){
					meeting_Names.push($(this).val());
				}
			});
			$("#showMeetingAll").val(meeting_Names)
		};
	});
}
function showOrHide2(){
	$("#showMA2").click(function(){
		if($("#test_div2").is(":hidden")){//:hidden  :visible
			$("#test_div2").show();
			$(".test_m2").show();
		}else{
			$("#test_div2").hide();
			$(".test_m2").hide();
		};
	});
	$("#test_div2").hover(function(){
		$("#test_div2").show();
		$(".test_m2").show();
	},function(){
	
		if($(".test_m2").is(":visible")){//:hidden  :visible
			$(".test_m2").fadeOut(500);
			$("#test_div2").fadeOut(500);
			var meeting_checkTypes = []
			$("input[name='checkType']").each(function(){
				if ($(this).attr("checked")){
					meeting_checkTypes.push($(this).val());
				}
			});
			$("#showMeetingCheckType").val(meeting_checkTypes)
		};
	});
}

    $.fn.extend({
        checks_select: function(options){
            jq_checks_name = null;
            jq_checks_select = null;
            $("#showMA").click(function(){
                jq_check = $("#test_div");
                jq_check.attr("class", "");
                if (jq_checks_name == null) {
                    jq_checks_name = $("<div class ='checks_div_name'></div>").appendTo(jq_check);
                    jq_checks_select = $("<div id='checks_div_select' class='checks_div_select'></div>").appendTo(jq_check);
                    $.each(options, function(i, n){
						if(typeof n != "undefined"){
							$("<div class='test_m' ><input type='checkbox' id="+i+" name='meetingAll' value='" + n + "'>" + n + "</div>").appendTo(jq_checks_select);
						}
                    });
                }
            });
        }
    });
    $.fn.extend({
        checks_select2: function(options){
            jq_checks_name2 = null;
            jq_checks_select2 = null;
            
            $("#showMA2").click(function(){
                jq_check2 = $("#test_div2");
                jq_check2.attr("class", "");
                if (jq_checks_name2 == null) {
                    jq_checks_name2 = $("<div class ='checks_div_name2'></div>").appendTo(jq_check2);
                    jq_checks_select2 = $("<div id='checks_div_select2' class='checks_div_select2'></div>").appendTo(jq_check2);
                    $.each(options, function(i, n){
						if(typeof n != "undefined"){
							$("<div class='test_m2' ><input type='checkbox' id="+i+" name='checkType' value='" + n + "'>" + n + "</div>").appendTo(jq_checks_select2);
						}
                    });
                }
            });
        }
    });
    


function init_meeting_page(){//初始化页面
	var names = new Array();
	$.ajax({
		url:"/meeting/show_meetingAll/",
		type:"POST",
		dataType:"json",
		success:function(meeting_dict){
			var datas = eval(meeting_dict);    
			var num = 0
			for(var i in datas){
				names[i] = datas[i];
			}
			$("#test_div").checks_select(names);
			/***********第一中读取字典类型***************/
//			$.each(datas , function(key, value) {
//				alert(datas.key.length)
//				alert(key + ":" + value); 
//
//			});
		}
//		error: function(e) {
//			alert(e.responseText);
//			alert('errors');
//		},
		
	});
	//------------会议考勤状态------------------
	
    var Types = new Array();
	$.ajax({
		url:"/meeting/show_checkTypeAll/",
		type:"POST",
		dataType:"json",
		success:function(meeting_dict){
			var datas = eval(meeting_dict);    
			var num = 0
			for(var i in datas){
				Types[i] = datas[i];
			}
			$("#test_div2").checks_select2(Types);
			/***********第一中读取字典类型***************/
//			$.each(datas , function(key, value) {
//				alert(datas.key.length)
//				alert(key + ":" + value); 
//
//			});
		}
//		error: function(e) {
//			alert(e.responseText);
//			alert('errors');
//		},
		
	});
	

	$("body").removeClass("indexBody").css("width","auto");
	$(".rightBox").eq(1).attr("class","rightBox1");
	$(".leftBox").eq(1).remove();
	var td=new Date();
	render_widgets($("#id_calculateform"));
	
//	$("#id_cometime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-01")
//	$("#id_endtime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-"+N2(td.getDate()))
	$.ajax({
	    url:"/meeting/choice_widget_for_select_emp/?multiple=T&popup=T",
	    type:"POST",
	    dataType:"html",
	    success:function(sdata){
	        $("#show_emp_tree").html(sdata).show();
        }
    });

	
	$('#calculatetabs').tabs("#calculatetabs > div");
	
	var refresh_current_page=function(){
		var typevalue=	parseInt($("#id_current_report").val());
		var where="";
		switch(typevalue){
			case 4:
				DetailMeeting(where)
				break;
			case 5:
				StatisticsMeeting(where)
				break;
			case 1:
				OriginalRecord(where)
				break;
		    case 2:
			    ValidRecord(where)
				break;		
			default:
				break;
		}
	}
	
	//统计
	$("#id_calculate").click(function(){
//		var st=new Date($("#id_cometime").val().replace(/-/g,"/"));
//		var et=new Date($("#id_endtime").val().replace(/-/g,"/"));
		var meetingNames = []
		$("input[name='meetingAll']").each(function(){
				if ($(this).attr("checked")){
					meetingNames.push($(this).attr("id"));
				}
		});
		if(meetingNames.length<1){
			alert("请选择会议")
			return ;
		}
		
		
//		if(st>et){
//			alert(gettext("开始日期不能大于结束日期"));
//			return;
//		}
//		if(et>new Date()){
//			alert(gettext("结束日期不能大于今天"));
//			return;
//		}
//		if(((et-st)>31*24*60*60*1000)|| (et.getMonth()>st.getMonth() && et.getDate()>=st.getDate())){
//			alert(gettext("统计只能当月日期，或者天数不能超过开始日期的月份天数！ "));
//			return;			
//		}
		if(!setPostData()){
			return ;
		}
		if( confirm(gettext("统计的时间可能会较长，请耐心等待"))==false){
			return ;
		}
		var current_rep = parseInt($("#id_current_report").val());
		if(current_rep == 1 || current_rep == 2){
			$("#id_calculateform").ajaxSubmit({
				url:"/meeting/validRecord/?meetingIDS="+meetingNames,
				type:"POST",
				success:function(data){			    
					refresh_current_page();
				}
			});
		}else{
			$("#id_calculateform").ajaxSubmit({
				url:"/meeting/meetingReCalc/?meetingIDS="+meetingNames,
				type:"POST",
				success:function(data){
					refresh_current_page();
				}
			});
		}
	});
	
	//查询
	$("#id_query").click(function(){
		 refresh_current_page();
	});
	

	
	
}

function getPubOpt(app,model,where){//得到模型属性
	var pubopt={
		dbapp_url:"/data/", 
		model_url:"/data/"+app+"/"+model+"/",                      //根目录地址
		//record_per_page: 15,                 //每页记录数
		max_no_page: 50,                 //记录数少于该数据时，不分页显示
		row_operations: false,               //对象操作true表示全部显示(默认)，false表示全部不显示，对象表示操作["New","Delete",["Leave",...]]
		obj_edit:false,
		disabled_actions: ['_add','_delete','_clear'],
		model_actions:false,
		object_actions:false,
		scrollable:{heigh:340},
		disable_cols:['UserID_id','UserID.pk','get_attpic'],
		obj_edit:false,
		init_query:where,
		scroll_table:false
	}
	return pubopt;
	
}

function getDataOpt(datajson,url,multiple){//得到非模型属性
	var hiddencol=["userid","data_verbose_column"]
	var data=[]
	var fn=datajson.fieldnames;
	for(var j=0;j<datajson.datas.length;j++)
	{
		var td=datajson.datas[j];
		var tmp=[]
		for(var i=0;i<fn.length;i++)
		{			
			tmp.push(encodeTxt(td[fn[i]]));			
		}
		data.push(tmp);
	}
	var var_multiple = true;
	if (multiple != undefined ){
		var_multiple = multiple;
	}
	var opt={
	  heads:datajson.fieldcaptions,//是一个列表，表示显示在列表表头上的文字; 
	  fields:datajson.fieldnames,//是一个列表，表示显示在列表表头上的文字; 
	  data:data,//二维列表，表示多行的数据；
	  disable_cols:hiddencol,//不可见的列
	  key_field:"id",  //关键字段名
	  data_verbose_column:"", //数据显示字段名，为空字符串
	  show_head: true,//显示头
	  actions: {},//是一个对象，表示定义在该数据模型上的操作列表，其每一个操作是一个json对象
	  base_url: "", //表示当前数据页面的URL; 
	  row_operations: [],//为一个列表，表示要放在对当前记录进行的操作栏的操作名（字符串）
	  multiple_select: var_multiple,//是否多选"multiple_select":null
	  page_count: datajson.page_count, //每页显示的数据行
	  current_page: datajson.page, //页号
	  record_count: datajson.item_count, //如果为零，则不在页面上显示总记录数
	  layout: "table",
	  scroll_table:false,
	  scrollable:{heigh:340},
	  grid_name:"",//记录的名字
	  tbl_id:"id_tbl",//"table"-表格形式显示, "icon"-大图标形式显示, "compact"-小图标形式显示 
	  on_pager:function(grid,p){  			  		
	  		var gd=grid;	  		
	  		$("#id_calculateform").append("<input type='hidden' name='p' value='"+p +"' \>");
	  		if($("#id_calculateform").find("input[name='pa']").length==0)	  
	  			$("#id_calculateform").append("<input type='hidden' name='pa' value='T' \>");
	  		var u_url=url	
	  		var option={
				url:u_url,	
				dataType:"json",					
				type:"POST",
				success:function(data){	
					$.extend(gd.g,getDataOpt(data,u_url));									
					gd.g.reload_data();					
				}
			}
			$("#id_calculateform").ajaxSubmit(option);
			$("#id_calculateform").find("input[name='p']").remove();
	  	return false;
	  }
	};
	return opt
}

function getDataOpt2(datajson,url){ //去掉多选
	return getDataOpt(datajson,url,null);
}

function getquerystring(){ //构造查询条件
	var where=[]; //时间条件
	var depts=[]; //部门条件
	var self_services_emp = $("#id_self_services");
	var meetingNames = []
	var checkTypes = []
	$("input[name='meetingAll']").each(function(){
		if ($(this).attr("checked")){
			meetingNames.push($(this).attr("id"));
		}
	});
	
	if(meetingNames.length!=0){	    
		where.push('meetingID__in='+meetingNames)
	}
	$("input[name='checkType']").each(function(){
		if ($(this).attr("checked")){
			checkTypes.push($(this).attr("id"));
		}
	});

	if(checkTypes.length!=0){
		where.push('checkType__in='+checkTypes)
	}

	if(self_services_emp.length !=0){//员工自助
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(self_services_emp.val());
		where.push('user__in='+self_services_emp.val());
	}else{
		$("#id_divsearch").find("input[name='deptIDs']").each(function(){
			depts.push($(this).val());
		})
		var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
		if (users.length!=0){
			$("input[name='DeptIDs']").val("");
			$("input[name='UserIDs']").val(users.toString());
			if(users.length>0){
				where.push('user__in='+users)
			}
		}

		if(depts.length>0 && $("input#id_dept_all").attr("checked")){ //部门用户都选择了，那么就以部门为准
			$("input[name='DeptIDs']").val(depts.toString());
			$("input[name='UserIDs']").val("");
				where.push('UserID__DeptID__in='+depts.toString());
	            if($("input#id_selectchildren").attr("checked")){
	                where.push("deptIDschecked_child=on");
	            }else{
	                where.push("deptIDschecked_child=off");
	            }	
		}
	}
	
//	st=$("#id_cometime").val();
//	et=$("#id_endtime").val();
//	det=new Date(et.replace(/-/g,"/"));
//	det.setDate(det.getDate()+1);
//	ett=det.getFullYear()+"-"+N2(det.getMonth()+1)+"-"+N2(det.getDate());
	switch(parseInt($("#id_current_report").val())){//暂时没有用上
		case 1:
//			where.push('startTime__range=("'+ st +'","'+ ett +'")')
			break;
		case 2:
//			where.push('checkTime__range=("'+ st +'","'+ ett +'")')
			break;		
		default:
			break;
	}
	return where
}


function setPostData(){//设置选人，选部门隐藏input值
	var depts=[];
	var self_services_emp = $("#id_self_services");//员工自助
	if(self_services_emp.length !=0){//员工自助
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(self_services_emp.val());
	}else{
		$("#id_divsearch").find("input[name='deptIDs']").each(
			function(){
			depts.push($(this).val());
		});
		var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
//		if(depts.length==0 && users.length == 0){	
//			alert(gettext("请选择人员或部门"));
//			return false
//		}
		
		if(users.length!=0){
			$("input[name='DeptIDs']").val("");
			$("input[name='UserIDs']").val(users.toString());
		}
		if(depts.length != 0 && $("#id_dept_all").attr("checked")){ //以部门为最后
			$("input[name='DeptIDs']").val(depts.toString());
			$("input[name='UserIDs']").val("");
		}
	}
	return true;
}
//设置报表，操作相关的共用属性
function SetProperty(reportid,app,model,reportname){
		//每次点击不同报表时，将清除已经选择的人员列表
		$("#id_current_report").val(reportid);
		$("#subtabs-"+reportid).empty();
		if(reportid==5 || reportid==8 || reportid==9 )//数据计算模型		
		{
			$("#id_sys_isModelExport").val("false");
		}
		else//数据表模型
		{
			$("#id_sys_isModelExport").val("true");
		}
		if(reportid==3 || reportid==5 || reportid==8)
		{
			$("#id_attexcept_desc").show();
		}
		else
		{
			$("#id_attexcept_desc").hide();
		}
		$("#id_sys_cur_app").val(app);
   		$("#id_sys_cur_model").val(model);
   		$("#id_sys_cur_grid").val("#subtabs-"+reportid);
   		$("#id_sys_cur_exporttitle").val(reportname);
		
}




function load_description()
{
	$.ajax({
		url:"/meeting/getValidRecords/",
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

function hide_div(){ //隐藏人员和考勤状态
	$('#id_drop_emp').hide();
	$('#show_user').attr('style','display:none');
	$('#show_emp_widget').attr('style','display:none');  
	$('#check_type').attr('style','display:none');
	$('#show_type').attr('style','display:none');
    
}

function show_div(){ //显示人员和考勤状态
	$('#id_drop_emp').show();
	$('#show_user').attr('style','display:inner');
	$('#show_emp_widget').attr('style','display:inner');  
	$('#check_type').attr('style','display:inner');
	$('#show_type').attr('style','display:inner');
    
}

function DetailMeeting(where){ //会议统计详情
    show_div();
	SetProperty("4",'meeting','DetailMeeting',gettext('会议统计详情'));
	$("#subtabs-4").model_grid(getPubOpt('meeting','DetailMeeting',getquerystring()));
}
function StatisticsMeeting(where){//会议统计汇总
    //会议统计汇总时隐藏人员和考勤状态
	hide_div();   
	SetProperty("5",'meeting','StatisticsMeeting',gettext('会议统计汇总'));
	$("#subtabs-5").model_grid(getPubOpt('meeting','StatisticsMeeting',getquerystring()));
}
function OriginalRecord(where){//会议签到签退
    show_div();    
	SetProperty("1",'meeting','OriginalRecord',gettext('会议签到签退'));
	$("#subtabs-1").model_grid(getPubOpt('meeting','OriginalRecord',getquerystring()));
}
function ValidRecord(where){//会议签到签退ValidRecord
    $('#show_user').attr('style','display:inner');
    $('#show_emp_widget').attr('style','display:inner');  
    $('#check_type').attr('style','display:inner');
    $('#show_type').attr('style','display:inner');
    
	SetProperty("2",'meeting','ValidRecord',gettext('会议考勤明细'));
	$("#subtabs-2").model_grid(getPubOpt('meeting','ValidRecord',getquerystring()));
}
function getdata(opt){
	$.ajax({ 
	   type: "POST",
	   url:opt.url+"?r="+Math.random(),
	   data:opt.data,
	   dataType:"json",
	   success:function(json){
			var gridd=$(opt.ddiv);
			json.multiple_select=null;
			json.on_pager=function(grid,p){
				$.ajax({
					type:"POST",
					url:opt.url+"?p="+p,
					data:opt.data,
					dataType:"json",
					success:function(msg){
						$.extend(grid.g,msg);
						grid.g.reload_data(msg);
					}
				});
				return false;
			 }; 
			SetProperty("9","list" ,json.tmp_name)
			gridd.grid(json);
	  }
  });
}

function N2(nc){
	var tt= "00" + nc.toString();
    tt=tt.toString();
    return tt.substr(tt.length-2);
}   
