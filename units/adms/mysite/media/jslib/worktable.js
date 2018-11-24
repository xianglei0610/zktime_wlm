/********************常用操作****************/
function init_common_opt(surl,dbapp_url){
		/**新增***/
		function fun_submit(href,div_dialog,msg,btn_trans){
			$("#id_span_title",div_dialog).find("span:not(.icon_SiteMap)").remove();
			if($("#ret_info",div_dialog).length==0){
				div_dialog.append("<div id='id_ret_info' class='ret_info'></div>"); 
			}
			var CONTINUE=true;
			var NOCONTINUE=false;
			var ok_event=function(is_continue){
				return function(){
					var post_href=href;
					var post_data={K:[]};
					if(typeof(post_href)=="function"){
						var postlist=post_href();
						post_href=postlist[1];
						post_data=postlist[0];
						query_key=[];
						for(var i in post_data){
							query_key.push("K="+post_data[i]);
						}
						post_href+="&"+query_key.join("&");
					}
					var $form=$("form",div_dialog);
					
					if($form.valid()){
						$form.ajaxSubmit({
							url:post_href, 
							dataType:"html", 
							//async:false, 
							success:function(msgback){ 
								if(msgback=='{ Info:"OK" }'){
									var ret_div=$("#id_ret_info",div_dialog);
									ret_div.html("<ul class='successlist'><li>"+gettext("保存成功!")+"</li></ul></td>").hide().show(100);
									$("form",div_dialog).get(0).reset();
									//if(!is_continue){
										$("#id_close",div_dialog).click();
									//}
								}else{
									var ret_div=$("#id_ret_info",div_dialog);
									 ret_div.html($(msgback).find("ul.errorlist")).hide().show(100);
								} 
							} 
						});
					}
				};
			};
			var btns={
				//"Save and Continue":ok_event(CONTINUE),
				"OK":ok_event(CONTINUE),
				"Cancel":function(){
					$("#id_close",div_dialog).click();
				}
				
			};
			if(btn_trans){
				$.extend(btns,btn_trans);
			}
			var f=function(j){ return btns[j] };
			var $btns_div=$("<div class='btns_class'></div>");
			var btn_read = $("#read_card")
			if (btn_read.length ==0)
			{
				for(var i in btns)
				{
					if(div_dialog.find("button#id_"+i).length==0)
						$btns_div.append("<button type='button' id='id_"+i+"' class='btn'>"+gettext(i)+"</button>")
					else
						$btns_div.find("button#id_"+i).text(gettext(i));
					var b=$btns_div.find("button#id_"+i)
					b.click(f(i));
				}
			}
			else
				{
					$("#btnclose").hide();
					$(".editformbtn").hide();
					$btns_div.append(btn_read);
					$btns_div.append("<button type='button' id='id_Cancel' class='btn'>"+gettext('Cancel')+"</button>")
					var b=$btns_div.find("button#id_Cancel")
					b.click(f('Cancel'));
				}
			div_dialog.append($btns_div);
		}

        var  $common_opt=$("#id_common_opt");
		$common_opt.find("a[relgo]").click(function(e){
			var this_a=this;
			var href=$(this).attr("relgo");
			var d=new Date();
			if(href.indexOf("?")==-1){
				href=href+"?stamp="+d.getTime();
			}else{
				href=href+"&stamp="+d.getTime();
			}
			$.ajax({
				url:href,
				type:"GET",
				//async:false,
				success:function(msg){
					if($("#id_opt_message").length==0){
						$("body").append("<div id='id_opt_message' style='visibility:hidden'></div>");
					}
					var msg_dialog=$("#id_opt_message");
					msg_dialog.append(msg);
					$("#id_span_title",msg_dialog).remove();
					$("#pre_addition_fields",msg_dialog).remove();
					fun_submit(href,msg_dialog,msg);
					msg_dialog.dialog({
							title:$(this_a).text(),
							on_load:function(obj){
									var $overlay=obj.target.getOverlay();
									$overlay.find("input[type=text]:not(:hidden):first").focus();
							}
						});
					msg_dialog.css("visibility","visible");
				}
			});
			return false;
		}); 
		/***非新增操作*****/
		$common_opt.find("a[relgoopt]").click(function(event){
			var href=$(this).attr("relgoopt");
			var a_this=this;
			var mul=$("#id_op_for_model").attr("data")=="True" ? "T" : "F";
			var d=new Date();
			if(href.indexOf("?")==-1){
				href=href+"?stamp="+d.getTime();
			}else{
				href=href+"&stamp="+d.getTime();
			}
			$.ajax({
					url:href,
					type:"GET",
					//async:false,
					success:function(msg){
						if($("#id_opt_message").length==0){
							$("body").append("<div id='id_opt_message' style='visibility:hidden'></div>");
						}
						var msg_dialog=$("#id_opt_message");
						msg_dialog.html(msg);
						$("#id_span_title",msg_dialog).remove();
						var f=function(msg_dialog){
							return function(){
								var keys=[];
								if(mul=="T"){
									keys=window.emp_select_objs[$("div[id^=emp_select_]",msg_dialog).attr("id")].get_store_emp();
								}else{
									keys=$("#id_pop_emp",msg_dialog).attr("data").split(",");
								}
								var postdata=[keys,href];
								return postdata;
							}
						}
						
						$.ajax({
							url:"/"+surl+"personnel/choice_widget_for_select_emp/?popup=T&multiple="+mul,
							type:"POST",
							dataType:"html",
							success:function(html_emp){
								var var_tr="<tr id='id_select_emp'><th><label class='required'>"+gettext("人员选择:")+"</label></th><td>"+html_emp+"</td></tr>";
								$("#pre_addition_fields",msg_dialog).replaceWith(var_tr);
								if(href.indexOf("OpRegisterFinger")!=-1){
									msg_dialog.find("#id_pop_emp").change(function(){
										$.ajax({
											 url:href+"&K="+$(this).attr("data"),
										     type:"GET",
											 success:function(msg){
													var $html=$(msg).find("tr.fg");
													msg_dialog
													.find(".tbl_data_edit>tbody tr:not(#id_select_emp)")
													.remove();
													msg_dialog.find(".tbl_data_edit>tbody").append($html);
													var count=msg_dialog.find("#id_tfcount").val();
													var count10=msg_dialog.find("#id_tfcount10").val();
													msg_dialog.find("#div_id_finngerT").html(gettext("已登记指纹")+count );
													msg_dialog.find("#div_id_finngerT10").html(gettext("已登记指纹")+count10 );
													
											  }
										});
									});
								}
							}
						});
						fun_submit(f(),msg_dialog,msg);
						msg_dialog.dialog({
							title:$(a_this).text(),
							on_load:function(obj){
									var $overlay=obj.target.getOverlay();
									$overlay.find("input[type=text]:not(:hidden):first").focus();
							}
						});
						msg_dialog.css("visibility","visible");
					}
				});
				return false;
			
		});
	//取消空td，按照顺序合并
	var $tds=$("#id_common_opt").find("td");
	var $trs=$("#id_common_opt").find("tr");
	for(var i=0;i<$tds.length;i++){
		if($.trim($tds.eq(i).html())==""){
			$tds.eq(i).remove();
			$tds.splice(i,1);
			i--;
		}
	}
	for(var j=0;j<$trs.length;j++){
		if($tds.length>0){
			$trs.eq(j).append($tds.eq(0)).append($tds.eq(1));
			$tds.splice(0,2);
		}
	}	
}

/*******************常用查找******************/
function init_commom_search(surl,dbapp_url){
		var search_fields={
			employee_num:[
				gettext("人员查询"),
				'<td><label  for="id_PIN">'+gettext("人员编号")+'</label></td>'
				+'<td><input type="text" id="id_PIN" maxlength="20"  fieldname="PIN"></td>'
				+'<td><label for="id_EName">'+gettext('姓名')+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="EName" id="id_EName"></td>'
			],
			identitycard:[
				gettext("身份证号查询"),
				'<td><label for="id_identitycard">'+gettext("身份证号码")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="identitycard" id="id_identitycard"></td>'
			],
			device:[
				gettext("考勤设备查询"),
				'<td><label  for="id_alias">'+gettext('设备名称')+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="alias" id="id_alias"></td>'
			],
			leave:[
				gettext("离职人员查询"),
				'<td><label  for="id_UserID__PIN">'+gettext("人员编号")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="UserID__PIN" id="id_UserID__PIN"></td>'
				+'<td><label for="id_UserID__EName" >'+gettext("姓名")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="UserID__EName" id="id_UserID__EName"></td>'
			],
			translog:[
				gettext("考勤原始数据查询"),
				'<td><label class="" for="id_UserID__PIN">'+gettext("人员编号")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="UserID__PIN" id="id_UserID__PIN"></td>'
				+'<td ><label for="id_UserID__EName" >'+gettext("姓名")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="UserID__EName" id="id_UserID__EName"></td>'
			],
			empchange:[
				gettext("员工调动查询"),
				'<td ><label  for="id_UserID__PIN">'+gettext("人员编号")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="UserID__PIN" id="id_UserID__PIN"></td>'
				+'<td ><label for="id_UserID__EName" >'+gettext("姓名")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="UserID__EName" id="id_UserID__EName"></td>'
			],
			issuecard:[
				gettext("卡片查询"),
				'<td ><label  for="id_UserID__PIN">'+gettext("人员编号")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="UserID__PIN" id="id_UserID__PIN"></td>'
				+'<td ><label for="id_UserID__EName" >'+gettext("姓名")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="UserID__EName" id="id_UserID__EName"></td>'
				+'<td ><label for="id_cardno" >'+gettext("卡号")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="cardno" id="id_cardno"></td>'
			],
			department:[
				gettext("部门查询"),
				'<td ><label for="id_code" >'+gettext("部门编号")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="code" id="id_code"></td>'
				+'<td ><label class="" for="id_name">'+gettext("部门名称")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="name" id="id_name"></td>'
			],
			checkexact:[
				gettext("补签卡查询"),
				'<td><label  for="id_UserID__PIN">'+gettext("人员编号")+'</label></td>'
				+'<td><input type="text" maxlength="20" fieldname="UserID__PIN" id="id_UserID__PIN"></td>'
				+'<td><label for="id_UserID__EName" >'+gettext("姓名")+'</label></td>'
				+'<td><input type="text" maxlength="40" fieldname="UserID__EName" id="id_UserID__EName"></td>'
			],
			postmsg:[
			    gettext("发送信息查询"),
				'<td><label for="id_msg_type">'+gettext("消息类型")+'</label></td>'
				+'<td><input type="text" maxlength="10" fieldname="msg_type" id="id_msg_type"></td>'
				+'<td><label for="id_msg_title">'+gettext(" 信息标题")+'</label></td>'
				+'<td><input type="text" maxlength="100" fieldname="msg_title" if="id_msg_title"></td>'
			]
		}
		var s_900=["employee_num","identitycard","device","translog"];
		$(".commom_search").find("a[relgo]").click(function(event){
			var href=$(this).attr("relgo");
			var key_search=$(this).attr("searchfield");
			var t_search_fields=search_fields[key_search];
			var d=new Date();
			if(href.indexOf("?")==-1){
				href=href+"?stamp="+d.getTime();
			}else{
				href=href+"&stamp="+d.getTime();
			}
			
			$.ajax({
				type:"GET",
				dataType:"html",
				async:false,
				url:href,
				success:function(msg){
					if($("#id_opt_message").length==0){
						$("body").append("<div id='id_opt_message' style='overflow:hidden'></div>");
					}
					var $msg_dialog=$("#id_opt_message");
					$msg_dialog.html(msg);
					$("#id_title",$msg_dialog).html(t_search_fields[0]);
					$("#id_form_search tr",$msg_dialog).prepend(t_search_fields[1]);
					for(var i in s_900){
					    if (key_search==s_900[i]){
							if($msg_dialog.width()>900){
								$msg_dialog.width(900);
							}
						}
					}

					$msg_dialog.dialog({
						on_load:function(obj){
							var $overlay=obj.target.getOverlay();
							$overlay.find("input[type!=hidden]:first").focus().select();
							$overlay.find("input").keydown(function(event){//按回车键直接查询
								if(event.keyCode==13)
								{
								   $overlay.find("#id_header_search").click();
								}
								
							});
							//$overlay.width($overlay.width());
					}});
					
					setTimeout(function(){
						$msg_dialog.width($msg_dialog.width());
						//$msg_dialog.parent(".contentWrap").css("overflow","hidden");
					},1000);
				},
				error:function(one,two,three){
					alert(gettext("服务器加载数据失败,请重试!"));
				}
			});
			return false;
		});
	//取消空td，按照顺序合并
	var $tds=$(".commom_search").find("td");
	var $trs=$(".commom_search").find("tr");
	for(var i=0;i<$tds.length;i++){
		if($.trim($tds.eq(i).html())==""){
			$tds.eq(i).remove();
			$tds.splice(i,1);
			i--;
		}
	}
	for(var j=0;j<$trs.length;j++){
		if($tds.length>0){
			$trs.eq(j).append($tds.eq(0)).append($tds.eq(1));
			$tds.splice(0,2);
		}
	}
}

/*****************即时消息******************/
function init_instant(surl,dbapp_url){
		function instant_msg_fun(surl){
			$.ajax({
					url:"/"+surl+"worktable/instant_msg/",
					type:"POST",
					dataType:"json",
					success:function(d){
						var fields=d.fields;
						for(var i in d.fields){
							fields[d.fields[i]]=i;
						}
						var html_json=[];
						html_json.push("<ul class='clearB'>");
						var data=d.data;
						var rowstyle="row3";
						for(var j in data){
							if(j%2 == 0){
								rowstyle="row2"
							}else{
								rowstyle="row3"
							}
							var msgtype="<div class='msg_type'>["+data[j][fields["msgtype"]]+"]&nbsp;</div>";
							var content=data[j][fields["content"]];
							var var_cursorP="";
							var show_content="";
							var title="";
							if(content.length>22){
							   show_content=content.substr(0,21)+"<span class='msg_more'>...</span>"+"<span class='color_gray'>["+data[j][fields["change_time"]]+"]</span>";
							   var_cursorP="cursorP";
							   title="title="+gettext("点击查看消息详情");
							}else{
							   show_content=content+"<span class='color_gray'>["+data[j][fields["change_time"]]+"]</span>";
							}		
							html_json.push("<li  cc='"+content+"' class='li_select "+rowstyle+" clearB'><div class='floatL msg_content "+var_cursorP+"' "+title+"> "+msgtype+show_content+"</div><div class='floatR clearR'><a class='set_read' href='javascript:void(0)' relgo='/"+surl+"worktable/instant_msg/"+data[j][fields["id"]]+"/' title="+gettext("删除该消息")+">"+gettext("关闭")+"</a></div></li>");
						}
						html_json.push("</ul>");
						$("#id_datalist",".common_monitor").html(html_json.join(" "));
						
						var $alinks=$("a.set_read",".common_monitor");
						$alinks.parents("li.li_select").find(">div.msg_content").click(function(e){
							if($(this).find("span.msg_more").length!=0){
								$("<div class='div_box div_msg_detail'>"+"<h1>"+gettext('公告详情')+"</h1><div class='div_msg_detailContent'>"+$(this).parent().attr("cc")+"</div></div>").dialog();
							}
						  })/*.end().mouseover(function(){
								$(this).find("a.set_read").addClass("msg_close");
						  }).mouseout(function(){
								$(this).find("a.set_read").removeClass("msg_close");
						  });*/
						function noDataCheck(){
							if($(".common_monitor").find("div#id_datalist>ul>li").length == 0){
								$(".common_monitor").find("div#id_datalist>ul").hide();
								$(".common_monitor").find("div#id_datalist").prepend(gettext('暂无提醒及公告信息')+"!");
							}
						}
						noDataCheck();
						$alinks.click(function(){
							var $obj_a=$(this);
							var href=$obj_a.attr("relgo");
							$.ajax({
								url:href,
								type:"POST",
								dataType:"html",
								success:function(msg){
									if(msg=='{ Info:"OK" }'){
										$obj_a.parents("li.li_select").remove();
									}
								noDataCheck();
								},
								error:function(f,s,t){
									alert(f+","+s+","+t);
								}
							});
						});
						
					}
			});
			
		}
		
		instant_msg_fun(surl);
		setInterval(
			function(){
				instant_msg_fun(surl)
			},
			900000
		);
}

//工作面板列表高度自适应
function process_scroll(){
	var bdiv=$(".move").find("div.dt_bdiv");
	for(var i=0;i<bdiv.length;i++){
		bdiv.eq(i).css({height:"auto"});
		if($.browser.msie && bdiv[i].scrollWidth>bdiv[i].clientWidth){
			//bdiv.eq(i).css({"padding-bottom":"20px"});
			bdiv.eq(i).css({height:bdiv.eq(i).height()+ 20 +"px"});
		}
	}

}
//请假，
function init_specday(surl,dbapp_url){
	var getPubOpt=function(app,model,where){
		var pubopt={
			dbapp_url:"", 
			model_url:dbapp_url+app+"/"+model+"/",                      //根目录地址
			record_per_page: 8,                 //每页记录数
			max_no_page: 8,                 //记录数少于该数据时，不分页显示
			row_operations: true,               //对象操作true表示全部显示(默认)，false表示全部不显示，对象表示操作["New","Delete",["Leave",...]]
			obj_edit:false,
			disabled_actions: ['_add','_delete','_clear','_change'],
			model_actions:false,
			object_actions:true,
			scrollable:{heigh:340},
			disable_cols:['UserID_id','UserID.pk','get_attpic'],
			obj_edit:false,
			init_query:where,
			init_after_get_jdata:function(){
				var g_grid=this;
				$(".div_leftBottomLine").hide();
				$("body").removeClass("indexBody");
				g_grid["actions"]["OpSpecAudit"]["add_query"]=["_t=EmpSpecDay_OpSpecAudit_pop.html"];
			},
			ajax_callback:process_scroll
		}
		return pubopt;
	}
	
	var opt=getPubOpt("att","EmpSpecDay",["audit_status__in=1,4"]);
	$("#audit_specday").model_grid(opt);
}
//加班单
function init_overtime(surl,dbapp_url){
	var getPubOpt=function(app,model,where){
		var pubopt={
			dbapp_url:"", 
			model_url:dbapp_url+app+"/"+model+"/",                      //根目录地址
			record_per_page: 8,                 //每页记录数
			max_no_page: 8,                 //记录数少于该数据时，不分页显示
			row_operations: true,               //对象操作true表示全部显示(默认)，false表示全部不显示，对象表示操作["New","Delete",["Leave",...]]
			obj_edit:false,
			disabled_actions: ['_add','_delete','_clear','_change'],
			model_actions:false,
			object_actions:true,
			scrollable:{heigh:340},
			disable_cols:['UserID_id','UserID.pk','get_attpic'],
			obj_edit:false,
			init_after_get_jdata:function(){
				var g_grid=this;
				$(".div_leftBottomLine").hide();
				$("body").removeClass("indexBody");
				g_grid["actions"]["OpAuditManyEmployee"]["add_query"]=["_t=OverTime_OpAuditManyEmployee_pop.html"];
			},
			init_query:where,
			ajax_callback:process_scroll			
		}
		return pubopt;
	}
	
	var opt=getPubOpt("att","OverTime",["audit_status__in=1,4"]);
	$("#audit_overtime").model_grid(opt);
}

//补签卡
function init_checkexact(surl,dbapp_url){
	var getPubOpt=function(app,model,where){
		var pubopt={
			dbapp_url:"", 
			model_url:dbapp_url+app+"/"+model+"/",                      //根目录地址
			record_per_page: 8,                 //每页记录数
			max_no_page: 8,                 //记录数少于该数据时，不分页显示
			row_operations: true,               //对象操作true表示全部显示(默认)，false表示全部不显示，对象表示操作["New","Delete",["Leave",...]]
			obj_edit:false,
			disabled_actions: ['_add','_delete','_clear','_change'],
			model_actions:false,
			object_actions:true,
			scrollable:{heigh:340},
			disable_cols:['UserID_id','UserID.pk','get_attpic'],
			obj_edit:false,
			init_after_get_jdata:function(){
				var g_grid=this;
				$(".div_leftBottomLine").hide();
				$("body").removeClass("indexBody");
				g_grid["actions"]["OpAuditCheckexact"]["add_query"]=["_t=CheckExact_OpAuditCheckexact_pop.html"];
			},
			init_query:where,
			ajax_callback:process_scroll
		}
		return pubopt;
	}
	
	var opt=getPubOpt("att","CheckExact",["audit_status__in=1,4"]);
	$("#audit_checkexact").model_grid(opt);
}

//初始化本日出勤率
function init_attrate(surl,dbapp_url){
	$.ajax({
		url:"/"+surl+"worktable/outputattrate/",
		type:"POST",
		dataType:"json",
		success:function(data){
			if(data.length==0){
				$("#id_attrate").html("<img src='/"+surl+"media/images/icon_NoData.gif'></img>");
				return;
			}
			var dict={
				"jdiv":$("#id_attrate"),
				"is_show":true
			};
			if(dict.jdiv.width()==0){
				return;
			}
			if(dict.jdiv.filter(":hidden").length!=0){
				dict.jdiv.parent().show();
				dict.is_show=false;
			}
			if($.browser.msie){
				var datas=[
							$("#id_attrate"), 
							data,
							{
								pies: {show: true, autoScale: true, fillOpacity: 1},
								hide_x_y:true
							}
							
						];
				$("#id_attrate").get(0).data=datas;
			}
			
			$.plot(
					dict.jdiv, 
					data,
					{
						pies: {show: true, autoScale: true, fillOpacity: 1},
						hide_x_y:true
					}
			);
			
			if(!dict.is_show){
				dict.jdiv.parent().hide();
			}
		}
	});
}

//初始化人力构成分析图
function init_empstructure(surl,dbapp_url){
	var inputs=$("#id_category>input")
	inputs.click(function(){
		$.ajax({
			url:"/"+surl+"worktable/outputEmpStructureImage/?t="+$(this).val(),
			type:"POST",
			dataType:"json",
			success:function(data){
				if(data.length==0){
					$("#id_empstructure").html("<img src='/"+surl+"media/images/icon_NoData.gif'></img>");
					return;
				}
				var dict={
					"jdiv":$("#id_empstructure"),
					"is_show":true
				};
				if(dict.jdiv.width()==0){
					return;
				}
				if(dict.jdiv.filter(":hidden").length!=0){
					dict.jdiv.parent().show();
					dict.is_show=false;
				}
				
				if($.browser.msie){
					var datas=[
								$("#id_empstructure"),
								data,
								{
									pies: {show: true, autoScale: true, fillOpacity: 1},
									hide_x_y:true
								}
							];
					$("#id_empstructure").get(0).data=datas;
				}
				
				$.plot(
						dict.jdiv, 
						data,
						{
							pies: {show: true, autoScale: true, fillOpacity: 1},
							hide_x_y:true
						}
				);
				if(!dict.is_show){
					dict.jdiv.parent().hide();
				}
				
			}
		});
		
	});
	if(inputs.length!=0){
		inputs[0].click();
	}
}


