
$(function(){
	var td=new Date()

	render_widgets($("#id_calculateform"));
	
	$("#id_cometime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-01")
	$("#id_endtime").val(td.getFullYear()+"-"+N2((td.getMonth()+1))+"-"+N2(td.getDate()))
//	$.ajax({
//	    url:"../../pos/choice_widget_for_select_emp/?multiple=T",
//	    type:"POST",
//	    dataType:"html",
//	    success:function(sdata){
//	        $("#show_emp_tree").html(sdata);
//        }
//    });
	
	$('#calculatetabs').tabs("#calculatetabs > div");
	
	
$("#monitor_pos_model").hide();
$("#monitor_hall").hide();
});


function data_valid(type_id)
{		
		var st=new Date($("#id_cometime").val().replace(/-/g,"/"));
		var et=new Date($("#id_endtime").val().replace(/-/g,"/"));
		
		var users=$("#show_emp_tree");
		var emp_labor=$("#emp_labor");
		
		if(type_id=='4' || type_id == '11' || type_id == '5'|| type_id == '12')
		{
			users.hide();
			emp_labor.hide();
		}
		else
		{
			users.show();
			emp_labor.show();
		}
		
		if(st>et)
		{
			alert(gettext("开始日期不能大于结束日期"));
			return false;
		}
		else if(et>new Date())
		{
			alert(gettext("结束日期不能大于今天"));
			return false;
		}
		else if(type_id=='9')
		{
			if(((et-st)>31*24*60*60*1000)|| (et.getMonth()>st.getMonth() && et.getDate()>=st.getDate()))
			{
				alert(gettext("统计只能当月日期，或者天数不能超过开始日期的月份天数！ "));
				return false;	
			}
			else
				return true;
		}
		else
			return true;
}

function getquerystringforid()//退款，卡成本
{   
	hide_or_show()
	var operate=$("#monitor_operate").find("option:selected").val()
	var where=[]
		ds=[]
	$("#id_divsearch").find("input[name='deptIDs']").each(function(){
		ds.push($(this).val());
	})
	var depts=ds.toString();
	var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
	$("input[name='UserIDs']").val(users.toString());
	if(users.length==0)
	{
		$("input[name='DeptIDs']").val(depts);
		$("input[name='UserIDs']").val("");
		if(depts.length>0)
		{
			where.push('user__DeptID__in='+depts)
		}		
	}
	else
	{
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(users.toString());
//		if(users.length>0)
//		{
//			where.push('user__in='+users)		
//		}
	}
	st=$("#id_cometime").val();
	et=$("#id_endtime").val();
	det=new Date(et.replace(/-/g,"/"))
	det.setDate(det.getDate()+1)
	ett=det.getFullYear()+"-"+N2(det.getMonth()+1)+"-"+N2(det.getDate())
	
	
	switch(parseInt($("#id_current_report").val()))
	{
	
		case 1://退款
		    $("#monitor_pos_model").hide();
			if (operate!=9999)
			{
				where.push('hide_column=5');
				where.push('create_operator='+operate+'');
				where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
			else
			{
				where.push("hide_column=5");
				where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");}
			break;
		case 2://卡成本
		    $("#monitor_pos_model").hide();
			if (operate!=9999)
				//where.push('hide_column=7&create_operator='+operate+'&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push('hide_column=7');
					where.push('create_operator='+operate+'');
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
					
				}
			else
				{
					where.push("hide_column=7");
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			break;
		
		case 9://消费刷卡记录表
				//where.push('hide_column__in=6,9,10,12&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push('hide_column__in=6,8,9,10,12');
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			break;
		case 8://充值表
		    $("#monitor_pos_model").hide();
			if (operate!=9999)
				//where.push('type=1&create_operator='+operate+'&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push('hide_column__in=1,13');
					where.push('create_operator='+operate+'');
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			else
				//where.push('type=1&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push("hide_column__in=1,13");
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			break;
		case 6://退卡表
			$("#monitor_pos_model").hide();
			if (operate!=9999)
				//where.push('type=4&create_operator='+operate+'&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push('hide_column=4');
					where.push('create_operator='+operate+'');
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
									
				}
				
			else
				//where.push('type=4&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push("hide_column=4");
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			break;
			case 7://发卡表
				$("#monitor_pos_model").hide();
				if (operate!=9999)
					//where.push('type=4&create_operator='+operate+'&checktime__range=("'+ st +'","'+ ett +'")');
					{
						where.push('hide_column=7');
						where.push('create_operator='+operate+'');
						where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
					}
				else
				//where.push('type=4&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push("hide_column=7");
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			break;
		
//		case 11://管理卡
//			$("#monitor_pos_model").hide();
//			if(operate!=9999)
//				where.push('time__range=("'+ st +'","'+ ett +'")&create_operator='+operate+'');
//			else
//				where.push('time__range=("'+ st +'","'+ ett +'")');
//			
//			break;
		
		case 10://补助表
			$("#monitor_pos_model").hide();
			if (operate!=9999)
				//where.push('type=2&create_operator='+operate+'&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push('hide_column=2');
					where.push('create_operator='+operate+'');
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
									
				}
				
			else
				//where.push('type=2&checktime__range=("'+ st +'","'+ ett +'")');
				{
					where.push("hide_column=2");
					where.push("checktime__range=(\""+ st +"\",\""+ ett +"\")");
				}
				
			break;
		case 4://挂失解挂表
			$("#monitor_pos_model").hide();
			if(operate!=9999)
				where.push('time__range=("'+ st +'","'+ ett +'")&create_operator='+operate+'');
			else
				where.push('time__range=("'+ st +'","'+ ett +'")');
			break;
		case 5://补卡表
			$("#monitor_pos_model").hide();
			if (operate!=9999)
				where.push('time__range=("'+ st +'","'+ ett +'")&create_operator='+operate+'');
			else
			    where.push('time__range=("'+ st +'","'+ ett +'")');
			break;
		
		
		
	}
	//PunchCardReport(where);
	return where
}
function hide_or_show()
{
	if(parseInt($("#id_current_report").val())==3)
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
function setPostData(sub_obj)
{
	ds=[]
	$("#id_divsearch").find("input[name='deptIDs']").each(function(){
		ds.push($(this).val());
	})
	var depts=ds.toString();	
	var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
//	if(depts=="" && users=="")
//	{	
////		alert(gettext("请选择人员或部门"));
//		$(sub_obj).empty()
//		return false
//	}
	$("input[name='UserIDs']").val(users.toString());
	if(users.length==0)
	{
		$("input[name='DeptIDs']").val(depts);
		$("input[name='UserIDs']").val("");
	}
	else
	{
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(users.toString());
	}
	return true
}
//设置报表，操作相关的共用属性
function SetProperty(reportid,app,model,reportname)
{
		//每次点击不同报表时，将清除已经选择的人员列表
		if($("#id_current_report").val()!=reportid);
		{
			
			$("#id_current_report").val(reportid);
			$("#subtabs-"+reportid).empty();
		}
		if(reportid==2 || reportid==9 || reportid==8 || reportid==9)//数据计算模型		
		{
			$("#id_sys_isModelExport").val("false")
		}
		else//数据表模型
		{
			$("#id_sys_isModelExport").val("true")

		}
		if(reportid==9)
		{
			$("#id_posexcept_desc").show();
		}
		else
		{
			$("#id_posexcept_desc").hide();
		}
		$("#id_sys_cur_app").val(app);
   		$("#id_sys_cur_model").val(model);
   		$("#id_sys_cur_grid").val("#subtabs-"+reportid);
   		$("#id_sys_cur_exporttitle").val(reportname);
		
}



function posReimburese(where)//退款明细
{
	if(!data_valid())
		return;
//	SetProperty("1",'pos','CarCashSZ',gettext('退款明细'));
//	$("#subtabs-1").model_grid(getPubOpt('pos','CarCashSZ',getquerystringforid(),5));
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-1"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=5"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("1",'list',data.tmp_name,gettext('退款明细报表'));
						$("#subtabs-1").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);
	
}

function posCarCost(where)//卡成本
{
	if(!data_valid())
		return;
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-2"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=7"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("2",'list',data.tmp_name,gettext('卡成本明细报表'));
						$("#subtabs-2").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}


function load_description()
{
	$.ajax({
					url:"../../att/getallexcept/",
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
						$("#id_posexcept_desc").html(html);
					}
				});
	
}


function CarBalanceReport(where)//卡余额
{
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	$("#show_emp_tree").show();
	$("#emp_labor").show();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-3"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=12"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("3",'list',data.tmp_name,gettext('卡余额明细报表'));
						$("#subtabs-3").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}	
function NOCarBalanceReport(where)//无卡退卡卡余额
{
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	$("#show_emp_tree").hide();
	$("#emp_labor").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-15"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=12&card_type=999"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("15",'list',data.tmp_name,gettext('无卡退卡卡余额明细报表'));
						$("#subtabs-15").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}	


function posLostCard(where)//卡挂失
{
	if(!data_valid("4"))
		return;
	$("#monitor_hall").hide();
	SetProperty("4",'pos','LoseUniteCard',gettext('卡挂失'));
	$("#subtabs-4").model_grid(getPubOpt_lost('pos','LoseUniteCard',getquerystringforid()));
}

//消费异常明细表
function pos_error_data(where)
{
	if(!data_valid("12"))
			return;
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-12"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=14"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("12",'list',data.tmp_name,gettext('消费异常明细表'));
						$("#subtabs-12").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}


function ManageCard(where)//管理卡
{
	if(!data_valid("11"))
		return;
	$("#monitor_hall").hide();
	SetProperty("11",'pos','CardManage',gettext('管理卡'));
	$("#subtabs-11").model_grid(getPubOpt_lost('pos','CardManage',getquerystringforid()));
}

function posReplenishCard(where)//补卡
{ 
	if(!data_valid("5"))
		return;
	SetProperty("5",'pos','ReplenishCard',gettext('换卡表'));
	$("#subtabs-5").model_grid(getPubOpt_lost('pos','ReplenishCard',getquerystringforid()));
}

function N2(nc)
{
	var tt= "00"  +nc.toString()
   
    tt=tt.toString();
    return tt.substr(tt.length-2);
}   

function FlushCard(where)
{
	if(!data_valid())
		return;
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	SetProperty("9",'pos','CarCashSZ',gettext('消费明细表'));
	where = getquerystringforid();//+'&type='+7
	$("#subtabs-9").model_grid(getPubOpt('pos','CarCashSZ', where));/*消费类型*/
}

function FlushCard_ic(where)
{		
	$('#monitor_cometime').show();
	$('#monitor_endtime').show();
	$('#div_cometime').show();
	$('#div_endtime').show();
	$('#monitor_operate').show();
	
	if(!data_valid("9"))
			return;
	$("#monitor_pos_model").show();
	$("#monitor_hall").show();
	var pos_model=$("#search_id_pos_model").find("option:selected").val();
	var dining=$("#monitor_hall").find("option:selected").val();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-9"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/get_ic_list/?pos_model="+pos_model+"&operate="+operate+"&dining="+dining
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("9",'list',data.tmp_name,gettext('消费明细表'));
						$("#subtabs-9").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
}


function ChargeRecord(where)
{
	if(!data_valid())
			return;
	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-8"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=1"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("8",'list',data.tmp_name,gettext('充值明细报表'));
						$("#subtabs-8").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}


function IssueCard(where)
{	
	if(!data_valid())
			return;

	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-7"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=13"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("7",'list',data.tmp_name,gettext('发卡明细报表'));
						$("#subtabs-7").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	

}

function ReturnCard(where)
{
	if(!data_valid())
			return;

	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-6"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=4"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("6",'list',data.tmp_name,gettext('退卡明细报表'));
						$("#subtabs-6").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}

function Allowance(where)
{
	if(!data_valid())
			return;

	$("#monitor_pos_model").hide();
	$("#monitor_hall").hide();
	var operate=$("#monitor_operate").find("option:selected").val();
	if(!setPostData("#subtabs-10"))
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/pos_list_report/?type=2"+"&operate="+operate
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("10",'list',data.tmp_name,gettext('补贴明细报表'));
						$("#subtabs-10").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);	
	
}

