function search_and_load(js)
{
	var scripts = document.getElementsByTagName('script');
		for (var i=0; i<scripts.length; i++) {
				var idx = scripts[i].src.indexOf('jslib/'+js);
				if(idx>0) return i;
			}
	document.write("<script src='/media/jslib/"+js+"'>");
	return -1;
}
function formatNum(num){
    if(num<10)
		return "0"+parseInt(num)
	else{
		return num
	}
}

function after_close(){
	$("#calendar").hide();
}
function setDate($input,tmp_date){
		var dSplit=$.trim($input.val());
		if(dSplit.indexOf(":")==-1){
		    dSplit="";
		}else{
			dSplit=dSplit.substring(dSplit.indexOf(":")-2,dSplit.length);
		}
		var strDate=tmp_date;
		$input.val(strDate+" "+dSplit);
}

function getToday(varH){
	var d = new Date();
	var $input=$(varH).parent().parent().find("input");
	var strToday=d.getUTCFullYear()+"-"+formatNum(d.getMonth()+1)+"-"+formatNum(d.getDate());
	setDate($input,strToday);
}

function setTime($input,tmp_time){
	var dSplit=$.trim($input.val());
	if(dSplit.indexOf("-")==-1){
		dSplit="";
	}else{
		 dSplit=$.trim(dSplit.split(" ")[0]);
	}	
	var strNow=tmp_time;
	$input.val(dSplit+" "+strNow+":00");
}

function getNow(varH){
    var d = new Date();
	var $input=$(varH).parent().parent().find("input");
	var strNow=formatNum(d.getHours())+":"+formatNum(d.getMinutes())+":"+formatNum(d.getSeconds());
	setTime($input,strNow);
}

function setDataPostion(){
	$("#id_tmp_form label").each(function(){
		var var_field_id=$(this).attr("for");
		$(":[pos='"+var_field_id+"']").eq(0).html($(this).parent().next().eq(0).html());
	});
	$("#id_tmp_form").parent().parent("tr").remove();
}
function render_widgets($render_form)
{
//	var months=gettext('January February March April May June July August September October November December').split(' ');
//	var days=gettext('S M T W T F S').split(' ');
//	var varInputValue="";
//	if($render_form.find("input.wZBaseDateTimeField").length!=0){
//			$.each($render_form.find("input.wZBaseDateTimeField"),function(index,elem){
//				alert(11111)
//				$(elem).datePicker({
//					startDate:"1900-01-01",
//					endDate :"2999-01-01",
//					datetime:true
////					showOn: 'button', buttonImage: '/media/img/icon_calendar.gif', 
////					buttonImageOnly: true,
////					changeYear:true,
////					changeMonth:true,
////					dateFormat:'yy-mm-dd',
////					beforeShow:function(){
////						varInputValue=$(this).val();
////					},
////					onClose:function(){
////						var varTmpValue=$(this).val();
////						$(this).val(varInputValue);
////						setDate($(this),varTmpValue);
////					}
//				});
//			});
//			var w_datetimes=$render_form.find("input.wZBaseDateTimeField");
//			$.each(w_datetimes,function(index, elem){
//				var this_parent=$(elem).parent();
//				this_parent
//				.find("span.pop_cal a#calendarlink")
//				.replaceWith(this_parent.find("a.dp-choose-date"));
//				this_parent
//				.find("span.pop_time a#clocklink img")
//				.clockpick({
//					starthour : 0,
//					endhour : 23,
//					useBgiframe:true,
//					military:true,
//					minutedivisions: 12			
//					},function(args){
//						setTime($(elem),args);
//				});
//			});
//	}
//
//	if($render_form.find("input.wZBaseDateField").length!=0){
//		$render_form.find("input.wZBaseDateField").datePicker({ 
//			startDate:"1900-01-01",
//			endDate :"2999-01-01"
////			showOn: 'button', buttonImage: '/media/img/icon_calendar.gif', 
////			buttonImageOnly: true,			
////			changeYear: true, 
////			changeMonth: true, 
////			monthNames: months,
////			monthNamesShort: months,
////			dayNamesMin: days,
////			dayNamesShort: days,
////			dateFormat:'yy-mm-dd'
//		});
//	}
//	
//	if($render_form.find("input.wZBaseTimeField").length!=0){
//		$("input.wZBaseTimeField").parent().find("span a#clocklink img").clockpick({
//			starthour : 0,
//			endhour : 23,
//			minutedivisions: 30,
//			useBgiframe:true,
//			military:true
//			//layout:'horizontal'
//		},function(args){
//			$(this).parent().parent().parent().find("input").val(args+":00");
//		});
//	}
	if($render_form.find("input.date").length!=0){
		$render_form.find("input.date").each(function(){
			var $this = $(this);
			var opts = {};
			if ($this.attr("format")) opts.pattern = $this.attr("format");
			if ($this.attr("yearstart")) opts.yearstart = $this.attr("yearstart");
			if ($this.attr("yearend")) opts.yearend = $this.attr("yearend");
			$this.datepicker(opts);
		})
	}
	
	//构造标签页
	if($("#id_tabs ul").length==0){
		$("#id_tabs").remove();
	}else{
			$('#id_tabs').tabs("#id_tabs > div");
			$("#id_tabs").find("tr:[title]").each(function(){
					var var_title=$(this).attr("title");
					$(this).after($("label:[for^="+var_title+"]").parent().parent());
					$(this).remove();
			});
	}
	var tooltip_opt={
		// place tooltip on the right edge
		position: "center right",
		// a little tweaking of the position
		offset: [-2, 10], 
		// custom opacity setting
		opacity: 0.7,
		// use this single tooltip element
		tip: '#error_tooltip',
		events: { 
		       input: 'mouseover click focus, blur mouseout',
		       checkbox: 'mouseover click, mouseout' 
		}
		}

	var err_in=$("td:has(.errorlist) input");
	err_in.each(function(){
		var tip_text=$(this).parent().find("ul").text();
		$(this).addClass("error");
		tooltip_opt["onBeforeShow"]=function(){ $("#error_tooltip").html(tip_text); }
		$(this).tooltip(tooltip_opt);
		$(".errorlist", $(this).parent()).remove();
	});
	if(err_in.length>0)
		err_in[0].focus();

	$("#id_edit_form,#id_action_form").add($render_form.find("form")).validate({
		errorPlacement: function(error, element) {
			element[0].error_text=error.text()
			tooltip_opt["onBeforeShow"]=function(){
				$("#error_tooltip").html(element[0].error_text);
			}
			element.tooltip(tooltip_opt);
			}
		});
}

function wgCheckNo(field,divname,container,dbapp_url,app_lable,model)
{
	dbapp_url="/"
	var url=dbapp_url+"checkno/"+app_lable+"/"+model+"/?"+field+"__exact=";
	tt="input#id_"+field
	var v=$(container).parent().parent().parent().find(tt).val();
	
	if (v=="")
		return;
	url+=v;
	var div= $(container).parent().parent().parent().find("#"+divname);
	
	div.removeClass("color_green lineH22").addClass("color_orange lineH22");
	
	$.ajax({
		type:"POST",
		dataType:"json",
		url:encodeURI(url),
		success:function(msg){
			div.html(msg["info"]);
			//如果验证为可使用，使用绿色--wangz
			if(msg["ret"] == 2)
			{
				div.removeClass("color_orange lineH22").addClass("color_green lineH22"); 
			}  			
		}
	});
}

//$obj为下拉菜单需要伸长的select id
//主要解决IE6,7,8下，下拉菜单内容过长不能完全显示的问题---wangz
function adjust_dropdown_list($obj)
{
	if($.browser.msie)
	{
		$obj.hide();
		//模拟下拉框的全部脚本
		var html = "<div id='dropdown_box' class='dropdown_box'>\
						<div class='dropdown_boxImg'>&nbsp;---------</div>\
						<div>\
							<img class='dropdown_img' src='/media/img/sug_down_on.gif' ></img>\
						</div>\
					</div>\
					<div class='dropdown_box_list'></div>";

		$obj.parent().append(html);
		var list = $obj.parent();
		
		$(document).click(function(event){
			var element_class = window.event.srcElement.className;
			//当点击下拉框以外地方，下拉框隐藏
			if(element_class == "" || ((element_class.indexOf("dropdown_img") == -1) && (element_class.indexOf("dropdown_box_list") == -1) && (element_class.indexOf("dropdown_box") == -1)))
			{
				if(list.find(".dropdown_box_list").is(":visible"))
				{
					list.find(".dropdown_box_list").hide();
				}
				else
				{
					list.find(".dropdown_boxImg").removeClass("dropdown_list_blue");
				}	
			}
			list.find(".dropdown_box_list").bgiframe();
		});

		var zx = 0;//下拉框宽度基值
		var check_len = "";//判断包含中文字符串长度
		var temp_html = "";//下拉框每个div
		var temp_id = "";//下拉框每个div的id
		//根据select生成一个模拟下拉框
		$obj.find("option").each(function(){
			var option_text = $(this).text();
			check_len = option_text.match(/[^\x00-\xff]/ig); //英文下返回null，中文下则拆分汉字
			temp_zx = option_text.length + (check_len == null ? 0 : check_len.length);
			if(temp_zx > zx)
			{
				zx = temp_zx;
			} 
			temp_html = "<div id=" + this.value + ">&nbsp;" + option_text + "</div>";
			list.find(".dropdown_box_list").append(temp_html);
		});
		
		//定义下拉div的事件，鼠标移出移入和点击
		list.find(".dropdown_box_list").find("div").mouseover(function(){
			$(this).removeClass("dropdown_list_white");
			$(this).addClass("dropdown_list_blue");
		});
		list.find(".dropdown_box_list").find("div").mouseout(function(){
			$(this).removeClass("dropdown_list_blue");
			$(this).addClass("dropdown_list_white");
		});
		list.find(".dropdown_box_list").find("div").click(function(){
			temp_id = $(this).attr("id");
			$obj.val(temp_id);
			list.find(".dropdown_boxImg").html($(this).text());
			list.find(".dropdown_boxImg").addClass("dropdown_list_blue");
		});

		var temp = false;
		list.find(".dropdown_box").click(function(){
			//是否隐藏下拉框 
			if(temp == false)
			{
				list.find(".dropdown_box_list").show();
				list.find(".dropdown_box_list").find("div:first").addClass("dropdown_list_blue");
				list.find(".dropdown_boxImg").removeClass("dropdown_list_blue");
				temp = true;
			}
			else
			{
				list.find(".dropdown_box_list").hide();
				list.find(".dropdown_box_list").find("div:first").removeClass("dropdown_list_blue");
				list.find(".dropdown_boxImg").addClass("dropdown_list_blue");
				temp = false;
			}
			list.find(".dropdown_box_list").width(zx*8);
		});
		
		list.find(".dropdown_box_list").width(zx*8);

		//点击清除按钮时正确情况选项和文本内容，ie下加载顺序不一样，此处必须使用live委托
		$("#id_header_clear").live("click",function(){
			$obj.find("option:selected").val("");
			list.find(".dropdown_boxImg").html("&nbsp;---------");
		});
		
		//编辑页面下，需根据选项值初始化下拉框显示文本
		var edit_value = list.find("select:first").val();
		list.find(".dropdown_box_list").find("div").each(function(){
			var div_id = $(this).attr("id");
			if(edit_value == div_id)
			{
				list.find(".dropdown_boxImg").html($(this).html());
			}
		});
	}
}
