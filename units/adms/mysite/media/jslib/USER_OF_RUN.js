schClass=[];
shifts=[];
assignedShifts=[];
MayUsedAutoIds=[];
AutoSchPlan=1;
MinAutoPlanInterval=24;

function show_during_times(t1,t2)
{	
	
	if(t1==t2)
		return "";
	else
		return getDuring_time_Str(t1)+"-"+getDuring_time_Str(t2);
}
function getDuring_time_Str(t)
{
	var sec=1/24/60/60;
	t_hour=parseInt((t+sec)*24*60/60)
	t_minute=Math.round((t+sec)*24*60%60)
	return getTimeStr(t_hour)+":"+getTimeStr(t_minute);
	
}
function getTimeStr(t)
{	if(t<10)
		return "0"+t;
	else
		return t;
}
function normalP(v)
{	
	return v*810/10000;  
}
function getTZDateAlt(index,sdate)
{
	if(sdate==undefined)
        return "";
    var tmp=new Date(sdate.valueOf()+index*1000*3600*24);
	var m="00"+(tmp.getMonth()+1);
	var d="00"+tmp.getDate();
	return	tmp.getFullYear()+"-"+m.substring(m.length-2)+"-"+d.substring(d.length-2);
}
function createTZTable(tzData, dayLabelFun, dayCount,sDate)
{
    var N=tzData.N[0];
    tzData=tzData.data;
    var pos,tdays
	
	//计算当前日期在班次模板中的起始位置
    post=0
    if(N[5]==1)//周
    {
        tdays=N[4]*7 
        pos=sDate.getDay() 
    }
    if(N[5]==2)//月
    {
        tdays=N[4]*31
        pos=sDate.getDate()-1
    }
    if(N[5]==0)//天
    {
        tdays=N[4]*1    
        pos=0
    }
	
	//格式完整班次模板
	var tp
	var i=0
	var r=0
	var t=0,dayi=0
	var tz, dayi=0, curDay=0, timei=0, temp=[]; 
	tp=[]
	for(i=0;i<tdays;i++)
	{
		if(r<tzData.length)
			dayi=Math.floor(tzData[r].StartTime)
		else
			dayi=-1
		
		if(i==dayi)
		{
			var subtemplate=[]
			while(r<tzData.length)
			{
				dayi=Math.floor(tzData[r].StartTime)
				if(i==dayi)
				{
					subtemplate.push(tzData[r]);
					r+=1;	
				}
				else
				{					
					break;
				}
			}
			tp.push(subtemplate)
		}
		else 
		{
			tp.push("");	

		}
		
	}
	
	d=0			//总天数循环变量
	t=pos		//班次天数循环变量
	
	
	//周，月，天 都从0开始
	
	
	html='<div id="id_timezone_header"></div><div id="id_timezone_body"><table class="timezone-table">';
	
	while(d<dayCount)
	{
		if(t>=tp.length)
		{
			t=0
		}
		if(tp[t]=="")
		{
			html+='<tr><td class="timezones-week">'+dayLabelFun(d,sDate)+'</td><td class="timezones-container" ></td></tr>'
		}
		else
		{
			sub=tp[t]
			html+='<tr><td class="timezones-week">'+dayLabelFun(d,sDate)+'</td><td class="timezones-container" >'
			var width=0.0000
			for(var si=0;si<sub.length;si++)
			{
				tz=sub[si];
				if(tz.StartTime==0 && tz.EndTime==0){
					
				}else{
					dayi=Math.floor(tz.StartTime)
					var dayi2=Math.floor(tz.EndTime)
					var time1=Math.round((tz.StartTime-Math.floor(tz.StartTime))*10000);
					var time2=Math.round((tz.EndTime-Math.floor(tz.EndTime))*10000);
					
	//				html+='<div style="width: '+ (normalP(time1-timei) - width) +'px;" class="tzbar space"></div>'
					html+='<div alt0="'+tz['StartTime']+'" alt1="'+tz['EndTime']+'" alt2="'+getTZDateAlt(d,sDate)+'" alt4="'+tz['SchClassID']+'" style="text-align: center; width: 100%;'+
						(tz['Color']==undefined?' ':' background-color: #'+(tz['Color']).toString(16)+' ')+
						'" class="tzbar"><span alt3="'+tz['SchName']+'" style="color:red;font-size:10px;vertical-align:top;">'+show_during_times(tz.StartTime-Math.floor(tz.StartTime),tz.EndTime-Math.floor(tz.EndTime))+'</span></div>'
	//				width= width + normalP(time1-timei) + normalP(time2-time1)
				}
			}
			html+="</td></tr>"
		}		
		t+=1		
		d+=1
		
	}
	html+='<tr style="background: #ccc;display:none;"><td colspan="2" style="height:2px;"></td></tr></table></div>'
	return html
	
	
}

//$(function(){
//
//	$("#id_div_op_for_tab").empty()
//	$("#id_div_op_for_tab").append("<ul>"
//		+"<li id='id_add_empShift'><a hre='#'>New Shift</a></li>"
//		+"<li id='id_addsch_tmpShift'><a hre='#'>New Temp Shift</a></li>"
//		+"<li id='id_clearall_tmpShift'><a hre='#'>Clear Temp Shift</a></li></ul>"
//	);
//	
////	var currDate=new Date();
//    
////    $.ajax({
////        url:"../../att/choice_widget_for_select_emp/?multiple=T&popup=T&name=UserID",
////        type:"POST",
////        dataType:"html",
////        success:function(sdata){
////            $("#show_dept_emp_tree").html(sdata);
////        }
////    });
//	
//
////	td=currDate.getFullYear()
////		+"-"
////		+(currDate.getMonth()+1<10?"0"+(currDate.getMonth()+1):currDate.getMonth()+1)
////		+"-"
////		+currDate.getDate()
////	if($.cookie("ComeTime")){
////		$("#id_ComeTime").val($.cookie("ComeTime"))
////		$("#id_EndTime").val($.cookie("EndDate"))
////	}
////	else{
////		$("#id_ComeTime").val(td)
////		$("#id_EndTime").val(td)
////	}
//	//getDept_to_show_emp(235);
//    
//    
////	$("#id_opt_tree").css("width",270)
//
//	
////	$.ajax({ 
////		type: "POST",
////		url:"../../att/getshifts/",
////		dataType:"json",
////		success:function(json){
////					shifts=json;
////				}
////	});
////	$.ajax({ 
////			type: "POST",
////			url:"../../att/getschclass/",
////			dataType:"json",
////			success:function(json){
////						schClass=json;
////					}
////		});
//	
//	
//});



