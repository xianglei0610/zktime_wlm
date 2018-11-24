
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
	select_filter(1)
//	consumeCollect("");

$("#id_is_operate").click(function() {
	     if ($(this).attr("checked") == true) {
	        $("input[name='check_operate']").val("checked");
	    }
	    else{ 
	        $("input[name='check_operate']").val("");
	    }
	    });

	
});


function data_valid()
{
		var st=new Date($("#id_cometime").val().replace(/-/g,"/"));
		var et=new Date($("#id_endtime").val().replace(/-/g,"/"));
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
		else if(((et-st)>31*24*60*60*1000)|| (et.getMonth()>st.getMonth() && et.getDate()>=st.getDate()))
		{
			alert(gettext("统计只能当月日期，或者天数不能超过开始日期的月份天数！ "));
			return false;			
		}
		else
			return true;
}

function getquerystring()
{
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
			where.push('UserID__DeptID__in='+depts)
		}		
	}
	else
	{
		$("input[name='DeptIDs']").val("");
		$("input[name='UserIDs']").val(users.toString());
		if(users.length>0)
		{
			where.push('UserID__in='+users)
		}
	}
	st=$("#id_cometime").val();
	et=$("#id_endtime").val();
	det=new Date(et.replace(/-/g,"/"))
	det.setDate(det.getDate()+1)
	ett=det.getFullYear()+"-"+N2(det.getMonth()+1)+"-"+N2(det.getDate())
	switch(parseInt($("#id_current_report").val()))
	{
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
function setPostData(typeid)
{
	ds=[]
	$("#id_divsearch").find("input[name='deptIDs']").each(function(){
		ds.push($(this).val());
	})
	var depts=ds.toString();		
	if ($("#id_divsearch").find("div[id^='emp_select_']").get(0)==undefined)
		var users=[]
	else
		var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
	var pos_model=$("#search_id_pos_model").find("option:selected").val();
	var dining=$("#monitor_hall").find("option:selected").val()
	var meal=$("#monitor_meal").find("option:selected").val()
	var operate=$("#monitor_operate").find("option:selected").val()
	$("input[name='Dining']").val(dining.toString());
	$("input[name='Meal']").val(meal.toString());
	$("input[name='Operate']").val(operate.toString());
	$("input[name='pos_model']").val(pos_model.toString());
	
//	if(typeid == 1 && depts=="" && users=="")
//	{	
//		alert(gettext("请选择人员或部门"));
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
		if(reportid==2 || reportid==5 || reportid==8 || reportid==9)//数据计算模型		
		{
			$("#id_sys_isModelExport").val("false")
		}
		else//数据表模型
		{
			$("#id_sys_isModelExport").val("true")

		}
//		if(reportid==2 || reportid==3 || reportid==5 || reportid==8)
//		{
//			$("#id_posexcept_desc").show();
//		}
//		else
//		{
//			$("#id_posexcept_desc").hide();
//		}
		$("#id_sys_cur_app").val(app);
   		$("#id_sys_cur_model").val(model);
   		$("#id_sys_cur_grid").val("#subtabs-"+reportid);
   		$("#id_sys_cur_exporttitle").val(reportname);
		
}


//消费统计 报表 开始
//rechargeCollect, 
//充值汇总表  type=1 ，
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
		
		case 1://个人消费汇总
			operate.hide();
			dining.hide();
			meal.hide();
			users.show();
			emp_labor.show();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case 120://部门汇总
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case 110://餐厅汇总
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case 140:
			operate.hide();
			dining.hide();
			meal.hide();
			users.hide();
			emp_labor.hide();
			st.show();
			pos_model.hide();
			check_btn.hide();
			break;
		case 150:
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
function rechargeCollect(where)
{	
	select_filter(110)
	if(!data_valid())
	{$("#subtabs-3").empty();return;}
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=110"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("3",'list',data.tmp_name,gettext('餐厅汇总表'));
					$("#subtabs-3").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
}	
//个人消费汇总表 
function consumeCollect(where)
{
    select_filter(1);
	if(!data_valid())
	{$("#subtabs-1").empty();return;}
	if(!setPostData(1))
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=130"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("1",'list',data.tmp_name,gettext('个人消费汇总表'));
					$("#subtabs-1").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
}
//部门汇总表
function allowanceCollect(where)
{
	select_filter(120)
	if(!data_valid())
	{$("#subtabs-2").empty();return;}
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=120"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("2",'list',data.tmp_name,gettext('部门汇总表'));
					$("#subtabs-2").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
}
//退款 type=4
function refundRepord(where)
{
	select_filter(140)
	if(!data_valid())
	{$("#subtabs-4").empty();return;}
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=140"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("4",'list',data.tmp_name,gettext('设备汇总表'));
					$("#subtabs-4").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
}

//计次type=10
function szRepord(where)
{
    select_filter(150)
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=150"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("6",'list',data.tmp_name,gettext('收支汇总表'));
					$("#subtabs-6").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
}

//现金实收表
function businessReport(where)
{
	select_filter(5)
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=5"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("5",'list',data.tmp_name,gettext('支入汇总表'));
					$("#subtabs-5").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
	
}

//营业报表
function expendReport(where)
{ 
    select_filter(7)
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=6"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("7",'list',data.tmp_name,gettext('支出汇总表'));
					$("#subtabs-7").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
	
}

//月结算表
function monthReport(where)
{
	 select_filter(8)
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/posreport/?type=7"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("8",'list',data.tmp_name,gettext('月结算表'));
					$("#subtabs-8").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
	
}

function addRecord(where)
{
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/addreport/?type='2'"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("2",'list',data.tmp_name,gettext('冲值记录表'));
					$("#subtabs-2").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);	
	
}
function subsidiesRecord(where)
{
	if(!setPostData())
		return ;
	$("#id_calculateform").find("input[name='pa']").remove();	
	var url="../../pos/subsidiesreport/?type='3'"
	var option={
				url:url,	
				dataType:"json",	
				data:"pa=T",	
				type:"POST",
				success:function(data){
					SetProperty("3",'list',data.tmp_name,gettext('补贴记录表'));
					$("#subtabs-3").grid(getDataOpt(data,url));					
				}
			}
	$("#id_calculateform").ajaxSubmit(option);
	
}
function diningcalculateRecord(where)
{
	if(!setPostData())
			return ;
		$("#id_calculateform").find("input[name='pa']").remove();	
		var url="../../pos/diningcalculatereport/?type='6'"
		var option={
					url:url,	
					dataType:"json",	
					data:"pa=T",	
					type:"POST",
					success:function(data){
						SetProperty("4",'list',data.tmp_name,gettext('餐厅消费统计'));
						$("#subtabs-4").grid(getDataOpt(data,url));					
					}
				}
		$("#id_calculateform").ajaxSubmit(option);
	
}





getdata=function(opt){
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
  })
}

function PunchCardReport(where)
{
	var dt1=$("#id_cometime").val()
	var dt2=$("#id_endtime").val()
	if (dt1=="" || dt2==""){
		alert(gettext("请选择开始日期或结束日期!"));
		return
	}
	if (dt1>dt2){
		alert(gettext("开始日期不能大于结束日期!"));
		return
	}
	var ddt1 = new Date(dt1)
	var ddt2 = new Date(dt2)
    iDays = parseInt(Math.abs(ddt2 - ddt1) / 1000 / 60 / 60 /24) +1
    if (iDays>31){
		alert(gettext("最多只能查询31天的数据!"));
		return
	}
	var depts=$("#id_divsearch").find("input[name='id_input_department']").val();		
	var users=$("#id_divsearch").find("div[id^='emp_select_']").get(0).g.get_store_emp();
	
	postdata={"starttime":dt1,"endtime":dt2,"deptids":depts,"empids":users}
	getdata({"url":"../../att/GenerateEmpPunchCard/","ddiv":"#subtabs-9","data":postdata})
	
	
}
	
function getUserId(g)
{
	
	var rid=$("#id_current_report").val();
	var userids=[]
	if(g==undefined)
		return userids
	if(rid==2 || rid==5 ||rid==8 )
	{
		var selected=g.get_selected().indexes
		for(var s=0	;s< selected.length;s++)
		{
			var tmp=g.data[selected[s]][0]			
			userids.push(tmp)
		}		
	}
	else
	{
		var selected=g.get_selected().indexes
		for(var s=0	;s< selected.length;s++)
		{
			var tmp=g.data[selected[s]][1]
//			tmp=tmp.substr(0,tmp.indexOf(" "));
			userids.push(tmp)
		}
	}
	return userids
	
}
function showDialog(url,title,width,height,event)
{
	var advhtml=""
    var userlist=[]
    var sdata={}
	var userid=getUserId($("#calculatetabs").find("#subtabs-"+$("#id_current_report").val()).get(0).g);  //查询结果中选择的人员
	
	if( userid.length<=0)
	{
		alert(gettext('请在查询结果中选择人员！'));
		return;
	}
	//alert(selected.toString());
	//var userid=selected.query_string;
	//userid=userid.replace(/K/g,'UserID');
	var tmp=[]
	for(var i=0;i<userid.length;i++)
	{
		var append=true;
		for(var j=0;j<tmp.length;j++)
		{
			if(tmp[j]==userid[i])
			{
				append=false;
				break;
			}
		}
		if(append)
		{
			tmp.push(userid[i]);
		}
	}
	userid=tmp

	$.ajax({
		type:"GET",
		url:url+"?_lock=1&UserID="+userid.join("&UserID="),
		//async:false,
		success:function(data){
		
			$(data).find("#id_span_title").hide();	
			advhtml=$("<div id='id_list'>"+data+"<div id='id_result_error'></div></div>")

			
			var cancel=function(div){					
				$("#id_list").find("#id_close").click();
			};
			var save_ok=function(){	
				if(!advhtml.find("#id_edit_form").valid())
				{
					return;
				}
				
				var opt={
					type:"POST",
					url:url,
					success:function(data){
						
						//alert(data);					
						if(data=='{ Info:"OK" }')
						{
							$("#id_list").find("#id_close").click();
						}else{
							$("#id_result_error").html("").append($(data).find(".errorlist").eq(0));
						}
					}					
				}		
				advhtml.find("#id_edit_form").ajaxSubmit(opt);		
			};
			//alert($(advhtml).find(".form_help").length);
			advhtml.find(".form_help").remove();
			advhtml.find(".zd_Emp").addClass("displayN");
			advhtml.find("#id_span_title").remove();
			advhtml.find("#objs_for_op").addClass("displayN");
			var d={}
			d["buttons"]={}
			d["buttons"][gettext('确认')]=save_ok;
			d["buttons"][gettext('取消')]=cancel;
			d["title"]=title;
			advhtml.dialog(d);
			
			/*
			//把选择的人员加入到表单中
			
			
			var ud=""
			for(var i=0;i<selected.keys.length;i++)			
			{	
				ud+="<input type='hidden' name='UserID' value='"+ selected.keys[i] +"'>"
			}
			
			var_divreport.find("#id_edit_form").append(ud)
			*/

			
		}
	});    	
	
	return;
}
function N2(nc)
{
	var tt= "00"  +nc.toString()
   
    tt=tt.toString();
    return tt.substr(tt.length-2);
}   
