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

	$('#calculatetabs').tabs("#calculatetabs > div");
	load_description();
	$("#id_attexcept_desc").hide();
	var refresh_current_page=function(){
		var st=new Date($("#id_cometime").val().replace(/-/g,"/"));
		var et=new Date($("#id_endtime").val().replace(/-/g,"/"));
		if(st>et){
			alert(gettext("开始日期不能大于结束日期"));
			return;
		}
		if(et>new Date()){
			alert(gettext("结束日期不能大于今天"));
			return;
		}
		if(((et-st)>31*24*60*60*1000)|| (et.getMonth()>st.getMonth() && et.getDate()>=st.getDate())){
			alert(gettext("查询只能当月日期，或者天数不能超过开始日期的月份天数！ "));
			return;			
		}
		var typevalue=	parseInt($("#id_current_report").val());
		var where="";
		switch(typevalue){
			case 1:
				AttRecAbnormite(where)
				break;
			case 2:
				DailyReport(where)
				break;
			case 3:
				AttShifts(where)
				break;
			case 5:
				CalculateReport(where)
				break;
			case 8:
				LeaveReport(where)
				break;
			case 9:
				LEReport(where)
				break;
			case 10:
				YCReport(where)
				break;
			case 11:
				CardTimesReport(where)
				break;
			default:
				break;
		}
	}
	
	//统计
	$("#id_calculate").click(function(){
		var st=new Date($("#id_cometime").val().replace(/-/g,"/"));
		var et=new Date($("#id_endtime").val().replace(/-/g,"/"));
		if(st>et){
			alert(gettext("开始日期不能大于结束日期"));
			return;
		}
		if(et>new Date()){
			alert(gettext("结束日期不能大于今天"));
			return;
		}
		if(((et-st)>31*24*60*60*1000)|| (et.getMonth()>st.getMonth() && et.getDate()>=st.getDate())){
			alert(gettext("统计只能当月日期，或者天数不能超过开始日期的月份天数！ "));
			return;			
		}
		
		if(!setPostData()){
			return ;
		}
		if( confirm(gettext("统计的时间可能会较长，请耐心等待"))==false){
			return ;
		}
		
		$("#id_calculateform").ajaxSubmit({
			url:"/att/AttReCalc/",			
			type:"POST",
			success:function(data){
				refresh_current_page();
			}
		});
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
		init_query:where,
		scroll_table:false,
		multiple_select: null
		
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
	  multiple_select: null,//是否多选"multiple_select":null
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
	
	if(self_services_emp.length !=0){//员工自助
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(self_services_emp.val());
		where.push('UserID__in='+self_services_emp.val());
	}else{
		$("#id_divsearch").find("input[name='deptIDs']").each(function(){
			depts.push($(this).val());
		})
		var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
		
		if (users.length!=0){
			$("input[name='DeptIDs']").val("");
			$("input[name='UserIDs']").val(users.toString());
			if(users.length>0){
				where.push('UserID__in='+users)
			}
		}
		
		if(depts.length != 0){ //部门用户都选择了，那么就以部门为准
			$("input[name='DeptIDs']").val(depts.toString());
			$("input[name='UserIDs']").val("");
			if(depts.length>0 && $("#id_dept_all").attr("checked")){
				where.push('UserID__DeptID__in='+depts.toString())
			}		
		}
	}
	
	st=$("#id_cometime").val();
	et=$("#id_endtime").val();
	det=new Date(et.replace(/-/g,"/"));
	det.setDate(det.getDate()+1);
	ett=det.getFullYear()+"-"+N2(det.getMonth()+1)+"-"+N2(det.getDate());
	switch(parseInt($("#id_current_report").val())){
		case 1:
			where.push('checktime__range=("'+ st +'","'+ ett +'")')
			break;
		case 3:
			where.push('AttDate__range=("'+ st +'","'+ et +'")')
			break;
		case 4:
			where.push('StartTime__gte='+ st )
			where.push('EndTime__lte='+ ett)
			break;
		case 6:
			where.push('TTime__range=("'+ st +'","'+ ett +'")')
			break;
		case 7:
			where.push('CHECKTIME__range=("'+ st +'","'+ ett +'")')
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
		if(depts.length==0 && users.length == 0){	
//			alert(gettext("请选择人员或部门"));
//			return false
			$("input[name='DeptIDs']").val("");
			$("input[name='UserIDs']").val("-1");
			
		}
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
		if(reportid==2 || reportid==5 || reportid==8 || reportid==9 )//数据计算模型		
		{
			$("#id_sys_isModelExport").val("false");
		}
		else//数据表模型
		{
			$("#id_sys_isModelExport").val("true");
		}
		if(reportid==2 || reportid==3 || reportid==5 || reportid==8)
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
function AttRecAbnormite(where){ //统计结果详情
	$("#id_current_report").val("1");
	if(!setPostData()){
		return ;
	}
	$("#id_calculateform").find("input[name='pa']").remove();	
	//load_description();
	$("#id_calculateform").ajaxSubmit({
		url:"/att/attRecAbnormite_report/",	
		dataType:"json",	
		data:"pa=T",	
		type:"POST",
		success:function(data){
			SetProperty("1",'list',data.tmp_name,gettext('统计结果详情'));
			$("#subtabs-1").grid(getDataOpt(data,"/att/attRecAbnormite_report/"));
			
		}
	});
}
function DailyReport(where)//每日考勤统计表
{
	$("#id_current_report").val("2");
	if(!setPostData()){
		return ;
	}
	$("#id_calculateform").find("input[name='pa']").remove();	
	//load_description();
	$("#id_calculateform").ajaxSubmit({
		url:"/att/DailyCalcReport/",	
		dataType:"json",	
		data:"pa=T",	
		type:"POST",
		success:function(data){
			SetProperty("2",'list',data.tmp_name,gettext('每日考勤统计表'));
			$("#subtabs-2").grid(getDataOpt(data,"/att/DailyCalcReport/"));
			
		}
	});
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
function AttShifts(where)//考勤明细表
{
	$("#id_current_report").val("3");
	if(!setPostData()){
		return ;
	}
	$("#id_calculateform").find("input[name='pa']").remove();	
	//load_description();
	$("#id_calculateform").ajaxSubmit({
		url:"/att/attShifts_report/",	
		dataType:"json",	
		data:"pa=T",	
		type:"POST",
		success:function(data){
			SetProperty("3",'list',data.tmp_name,gettext('考勤明细表'));
			$("#subtabs-3").grid(getDataOpt(data,"/att/attShifts_report/"));
			
		}
	});
}
 
function CalculateReport(where)//考勤统计汇总表
{
	$("#id_current_report").val("5");
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="/att/CalcReport/"
	var option={
		url:url,	
		dataType:"json",	
		data:"pa=T",	
		type:"POST",
		success:function(data){
			SetProperty("5",'list',data.tmp_name,gettext('考勤统计汇总表'));
			$("#subtabs-5").grid(getDataOpt(data,url));
			
		}
	}
	$("#id_calculateform").ajaxSubmit(option);
	//load_description();
}	

function LEReport(where){//统计每天最早与最晚记录
	if(!setPostData()){
		return ;
	}
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="/att/lereport/";
	$("#id_calculateform").ajaxSubmit({
		url:url,	
		dataType:"json",	
		data:"pa=T",	
		type:"POST",
		success:function(data){
			SetProperty("9",'list',data.tmp_name,gettext('统计最早与最晚'));
			$("#subtabs-9").grid(getDataOpt2(data,url));
			
		}
	});
}	

function YCReport(where){//考勤异常明细表
	if(!setPostData()){
		return;
	}
	$("#id_calculateform").find("input[name='pa']").remove();
	var url="/att/ycreport/";
	$("#id_calculateform").ajaxSubmit({
		url:url,
		dataType:"json",
		data:"pa=T",
		type:"POST",
		success:function(data){
			SetProperty("10", 'list', data.tmp_name, gettext('考勤异常明细表'));
			$("#subtabs-10").grid(getDataOpt(data, url));
		}
	});
}

function CardTimesReport(where){//打卡详情表
	if(!setPostData()){
		return;
	}
	$("#id_calculateform").find("input[name='pa']").remove();
	var url="/att/CardTimesReport/";
	$("#id_calculateform").ajaxSubmit({
		url:url,
		dataType:"json",
		data:"pa=T",
		type:"POST",
		success:function(data){
			SetProperty("11", 'list', data.tmp_name, gettext('打卡详情表'));
			$("#subtabs-11").grid(getDataOpt(data, url));
		}
	});	
}

function LeaveReport(where){//请假汇总表
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();
	var url="/att/CalcLeaveReport/";
	$("#id_calculateform").ajaxSubmit({
		url:url,	
		dataType:"json",		
		data:"pa=T",
		type:"POST",
		success:function(data){
			SetProperty("8",'list',data.tmp_name,gettext('请假汇总表'));
			$("#subtabs-8").grid(getDataOpt(data,url));
				
		}
	});
	//load_description();
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
