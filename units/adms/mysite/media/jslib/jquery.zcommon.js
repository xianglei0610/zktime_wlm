/**
 * scrollable table with two div
**/

(function($) {
	$.fn.tbl_scrollable=function(settings){
		var $tbl=this;
		var g={
			datalist_div:$(document.createElement('div')),
			hdiv:$(document.createElement('div')),
			bdiv:$(document.createElement('div')),
			btable:$(document.createElement('table')),
			fields_width:[],
			maxheight:280,
			min_col_width:30,
			//max_col_width:150,
			minheight:80
		};
		$.extend(g,settings);
		var flag_hidden=false;
		var $tbl_parent=$tbl.parent();
		var vdt="";
		if($tbl.width()==0){
			flag_hidden=true;
			vdt=$("#id_visible_for_dt");
			if(vdt.length==0){
				$("body").append("<div style='visibility:hidden;' id='id_visible_for_dt'></div>");
				vdt=$("#id_visible_for_dt");
			}else{
				vdt.empty();
			}
			vdt.append($tbl);
		}
		$tbl.before(g.datalist_div);
		g.datalist_div.attr("id",$tbl.attr("id"));
		g.datalist_div.append(g.hdiv);
		g.datalist_div.append(g.bdiv);
		g.hdiv.append($tbl);
		var flag=true;
		if(g.fields_width.length!=0){
			flag=false;
		}
		var column_count=g.hdiv.find("th").length;
		var get_column_max_width=function(index){
			var max_w=0;
			var var_index;
			if(index==column_count){
				var_index=0;
			}else{
				var_index=index;
			}
			$.each(g.bdiv.find("tr:first td"),function(i,e){
				var this_index=i+1;
				if(this_index%column_count==var_index){
					max_w=$(e).width();
				}
			});
			return max_w;
		}
		$.each($("th",g.hdiv.find("thead")),function(index,elem){
			if(flag){
				var w=get_column_max_width(index+1);
				if(w<$(this).width()){
					w=$(this).width();
				}
				/*if(w>g.max_col_width){
					w=g.max_col_width;
				}else */
				if(w<g.min_col_width){
					w=g.min_col_width;
				}
				g.fields_width.push(w);
			}
			var tmp_div=$(document.createElement('div'));
			tmp_div.width(g.fields_width[index]);//.css({"overflow":"hidden"});
			tmp_div.append($(this).contents());
			//$(this).attr("title",tmp_div.text());
			$(this).width(g.fields_width[index]);
			$(this).empty().append(tmp_div);
		});
		g.bdiv.append(g.btable);
		//if($.browser.msie && g.hdiv.find("tr").length>1 ){
			//g.bdiv.addClass("dt_max_height dt_min_height");			
		//}else{
			//g.bdiv.css({"max-height":g.maxheight,"min-height":g.minheight});
		//}
		g.btable.append($tbl.find("tbody"));
		g.btable.append($tbl.find("tfoot"));
		$.each($("tr",g.bdiv),function(itr,etr){
			$.each($("td",$(this)),function(itd,etd){
				var tmp_div=$(document.createElement('div'));
				tmp_div.width(g.fields_width[itd]);//.css({"overflow":"hidden"});
				tmp_div.append($(this).contents());
				//$(this).attr("title",tmp_div.text());
				$(this).empty().append(tmp_div);
				$(this).width(g.fields_width[itd]);
			});
		});
		g.hdiv.addClass("dt_hdiv");
		g.hdiv.find("table").addClass("dt_hdiv_tbl table");
		g.bdiv.addClass("dt_bdiv");
		g.bdiv.find("table").addClass("dt_bdiv_tbl table");
		if(g.height){
			g.bdiv.height(g.height);
		}
		g.bdiv.scroll(function(event){
			g.hdiv.scrollLeft($(this).scrollLeft());
		});
		var dombdiv=g.bdiv.get(0);
		g.hdiv.parent().prepend('<div class="dt_hdiv_right"></div>');
		
		//according to resolution of the screen to adjust the height of datalist
		var bdiv=$tbl.parent().parent().find(".dt_bdiv");
		var bdiv1=$("#id_extend").find(".dt_bdiv");
		if(g.height){
			bdiv.css({height:g.height+"px"});
		}else{
			if(screen.height < 768){
				bdiv.css({height:"280px"});
			}
			else{
				var ah;
				if ($.browser.msie){
					if($.browser.version>7.0){
						ah=460;
					}else{
						ah=430;
					}
				}
				else{
					ah=450;
				}
				bdiv.css({height:screen.height - ah - $("#id_search").height()});
				//retain to 15 rows's height if resolution is too high
				if(bdiv.height()>395){
					bdiv.css({height:"395px"});
				}
			}
		}
		bdiv1.css({height:bdiv.height()});
		if(dombdiv.scrollHeight>dombdiv.clientHeight){
			g.hdiv.css({"overflow-y":"scroll"});
			g.bdiv.addClass("dt_bdiv_scrollY");
			g.datalist_div.find(".dt_hdiv_right").show();
		}
		else{
			g.datalist_div.find(".dt_hdiv_right").remove();
		}
        //控制 苹果浏览器显示
        if($.browser.safari){
        	g.hdiv.css({"overflow-x":"hidden"});
        }
		
		if(flag_hidden){
			$tbl_parent.append(g.datalist_div);
			vdt.css({visibility:'visible'});
		}
	}
})(jQuery);

/*
 *dialog
 *
*/

(function($) {
	$.fn.dialog=function(opt){
        opt=opt || {};
		$this_div=this;
		var div_dialog=this;
        var ov=$("div.for_all#overlay ");
        if(ov.length==0){
            $("body").append("<div id='overlay' class='for_all apple_overlay'><table align='center' cellpadding='0' cellspacing='0'>"
                +"<tr>"
                    +"<td class='corner_tl'></td>"
                    +"<td class='corner_tm'></td>"
                    +"<td class='corner_tr'></td>"
                  +"</tr>"
                  +"<tr>"
                    +"<td class='corner_ml'></td>"
                    +"<td class='corner_mm'><div class='contentWrap'></div></td>"//内容
                    +"<td class='corner_mr'></td>"
                  +"</tr>"
                  +"<tr>"
                    +"<td class='corner_bl'></td>"
                    +"<td class='corner_bm'></td>"
                    +"<td class='corner_br'></td>"
                  +"</tr></table>"				
             );
            ov=$("body").find("div.for_all#overlay");
            ov.bgiframe();
        }
        if(opt.title){
            $(this).addClass("div_box").prepend("<h1>"+opt.title+"</h1>");
        }
        ov.find(".contentWrap").html("");
        ov.find(".contentWrap").append(this);
        div_dialog=ov;
        $("div#overlay_target").remove();
        $("body").append("<div id=overlay_target style='display: none;'> </div>");
        target=$("div#overlay_target");
        
        if(opt.buttons){
            var btns=this.find("div.btns_class");
            if(btns.length==0) {
				$(this).append("<div class='btns_class'></div>");
				btns=$("div.btns_class",$(this));
			 }
            var f=function(j){ return opt.buttons[j] }
            for(var i in opt.buttons){
                if(btns.find("button#id_"+i).length==0)
                    btns.append("<button type='button' class='btn' id='id_"+i+"'>"+gettext(i)+"</button>")
                else
                    btns.find("button#id_"+i).text(gettext(i));
                var b=btns.find("button#id_"+i)
                b.click(f(i));
            }
        }
        if(this.parent().find("div#id_close").length==0){
            this.prepend("<div id='id_close' class='close'></div>");
        }
        
        this.find("div#id_close").click(function(){
            target.overlay().close();
            $this_div.remove();
        });
		
		var opt_overlay={ 
			  expose: {
		      		color: '#000000',
		      		loadSpeed: 200,
		        	opacity: 0.6
		    	},
			  opacity:'0.6', 
			  effect: 'apple', 
			  close:"#id_close",
			  fixed:false,
			  closeOnClick:false,
			  target:div_dialog,
			  closeOnEsc:false
		  }
	   if(opt.on_load){
	      opt_overlay["onLoad"]=opt.on_load;
	   }
	   ret = target.overlay(opt_overlay); 
		
       target.click();
	   $("body div:last").bgiframe();
       return ret;
  };
})(jQuery);


(function($) {
//tabs
//编写tabs插件
	 	/*格式
	 	<div id="id_test" style="padding:120px">
	 	    <div><ul><li><a>firsttab</a></li><li><a>secondtab</a></li></ul></div>
	 	    <div><div>contentone</div><div>contenttwo</div></div>
	 	</div>
	 	*/	
	 	$.addSelectClick=function($li,$content){
	 	   $li.find("a:first").click(function(){
	 			$li.parent("ul").find("li").removeClass("tabs_li_focus");//去除样式
	 			$li.addClass("tabs_li_focus");//给焦点添加特殊样式
	 			$content.parent().find(">div").hide();
	 			$content.show();
	 		});
	 		//添加关闭按钮
	 		$li.find("a").after('<a class="ui-icon ui-icon-close"></a>');
	 		var parent_li=$li.parent();
	 		$li.find("a:last").click(function(){
	 		    if($li.parent().find("li").length==1){
	 				return;
	 			}
	 			$content.remove();
	 			$li.remove();
	 			parent_li.find(">li:last a:first").trigger("click");
	 		});
	 	}
	 	//初始化tabs,调用$("#id_test").zktabs();
	 	$.fn.zktabs=function(){
	 		$(this).each(function(){
	 			//添加默认都有的样式
				var this_tabs=$(this);
	 			var this_lis=$(this).find(">div>ul>li");
	 			this_lis.addClass("tabs_li");
	 			this_lis.each(function(index){
	 			      var this_content= this_lis.parent().parent().next().find("div").eq(index);
	 				  $.addSelectClick($(this),this_content);
	 				//第一次以第一个标签作为焦点
	 				if(index==0){
	 					$(this).selectTab();
	 				}
	 			});
	 		});
	 	}
	 	//选中一个tab,li
	 	$.fn.selectTab=function(){
	 		$(this).find("a:first").trigger("click");
	 	}
	 	//添加一个tab
	 	$.fn.addTab=function(title,$content){
	 		var var_title=title.replace(/ /g,"");
	 		var var_li="<li class='tabs_li' ><table><tr><td></td><td></td><td class='tboc h1'></td><td></td><td></td></tr><tr><td></td><td class='tboc w1 h1'></td><td class='tbac'></td><td class='tboc w1'></td><td></td></tr><tr><td class='tboc w1'></td><td class='tbac tbg'></td><td class='tbac tabs_contant tbg'><a name='"+var_title+"'>"+title+"</a></td><td class='tbac tbg'></td><td class='tboc w1'></td></tr></table></li>";
	 		if($(this).find(">div>ul>li").length>6){
	 			alert(gettext("标签页不能多于6个!"));
	 			$content.remove();
	 			return;
	 		}
	 		$(this).each(function(){
	 		    //添加内容
	 			if($("a[name='"+var_title+"']").length>0){
	 				return;
	 			}
	 		    var var_divs=$(this).find(">div");
	 			var_divs.find(">ul").append(var_li);
	 			var_divs.eq(1).append($content);
	 			var var_content=var_divs.eq(1).find(">div:last");
	 			$.addSelectClick(var_divs.find(">ul>li:last"),var_content);
	 		    var_divs.find(">ul>li:last").selectTab();
	 		});
	 	}
})(jQuery);



(function($) {
	//把中控自己的函数加入jquery对象的子对象$.zk中
		$.zk={};
		$.extend(
			$.zk,
			{
			 sys_message:function($div,message,show_time){
				   $div.find("div.sys_Message_m").html("<div class='sys_Message_icon'></div>"+message);
				   $div.slideDown("normal");
				   setTimeout(function(){
						$div.slideUp("slow");
					},show_time);
			 },
			 _dataToGrid:function($div,json_data,cfg){
				/*json_data={
					fields:[]
					data:[]
				}
				*/
			
				var thead=""
				var fields=json_data.fields
				for(i=0;i<fields.length;i++)
				{
					thead+="<td>"+fields[i]+"</td>";
				}
				var header="<thead><tr>"+thead+"</tr></thead>"
				var data=json_data.data;
				var tbody="<tbody>"				
				for(i=0;i<data.length;i++)
				{
					var linedata=data[i];
					tbody+="<tr>";					
					for(j=0;j<linedata.length;j++)
					{	if(j==0)
						{
							tbody+="<input type='hidden' name='idlist' value='"+linedata[j]+"' />";
						}
						tbody+="<td>"+linedata[j]+"</td>";
					}
					tbody+="</tr>";
				}
				tbody+="</tbody>"				
				
				var html="<table class='showdatagrid'>"+thead+tbody+"</table>";
				$div.html(html);
			},
			//datalist.html中元素的显示与隐藏
			  _hide_switch:function(is_hide,do_action_masker_div){
					if(is_hide){
						for(var i in do_action_masker_div){
							do_action_masker_div[i].hide();
						}
						$("#id_model_extend").hide();
						$("#id_tab").find(".portlet-header").hide();
						$("#id_search").hide();
						$("#id_filter").hide();
						$("body").removeClass("indexBody");
						$("#id_extend").hide();
					}else{
						for(var i in do_action_masker_div){
							do_action_masker_div[i].show();
						}
						$("#id_model_extend").show();
						$("#id_tab").find(".portlet-header").show();
						$("#id_search").show();
						$("#id_filter").show();
						$("body").addClass("indexBody");
						$("#id_extend").show();
					}
				},
				//选人作为一个单独的功能来实现
				_select_emp:function(opt){
					var $grid=$("#"+opt.grid_id);
					var surl=opt.surl;
					var url=opt.model_url;
					var cfg_obj=opt;
					var scroll="";
                    var field_name = opt.field_name;
					if(opt.multiple_select){
						scroll={h:170,w:330};
					}else{
						scroll={h:170,w:"100%"};
					}
					var default_cfg_obj={
						 model_actions:false,
						 async:false,
                         prev_opt:{scroll_table:true},
						 object_actions:false,
						 row_operations:false,
						 obj_edit:false,
						 layout_types:[],
						 scrollable:{height:148},
						 model_url:url,
                         sort_fields:["PIN","DeptID.code"],
						 fields_show:["PIN","EName","DeptID.name","Card"],////["PIN","EName","DeptID","Gender","Title"],
						 record_per_page:7,
						 on_selected:function(grid, checked, index, key, $row_data){
							if(grid.g.multiple_select){
								var store_tr=$row_data.clone();
								store_tr.find("input").attr("checked","true")
                                var $store_emp=$(grid).find("#id_store_select_emp");
								if(checked){
									if($store_emp.find("tr[data='"+key+"']").length==0){
                                        store_tr.find("input").click(function(){
                                            $(grid).find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
                                        });
										$store_emp.append(store_tr);
                                        $(grid).find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
									}
									if(grid.g.field_name){
										store_tr.find("input").attr("name",grid.g.field_name);
									}
								}else{
									$store_emp.find("tr[data='"+key+"']").remove();
                                    $(grid).find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
								}
							}else if(grid.g.multiple_select == false){
								if(checked){
									$row_data.find("input").attr("name",grid.g.field_name);
									$grid.parents("#id_corner_tbl").find("span#id_close").click();
								}
							}
						 },
						 on_all_selected:function(grid,checked,input,seleted_rows){
							var $store_emp=$(grid).find("#id_store_select_emp");
							var clone_trs=$(grid).find("#id_tbl tbody tr").clone();
							if(checked){
								if(grid.g.field_name){
									clone_trs.find("input").attr("checked","true").attr("name",grid.g.field_name);
								}else{
									clone_trs.find("input").attr("checked","true");
								}
							}
							for(var i=0;i<clone_trs.length;i++){
								var clone_tr=clone_trs.eq(i);
								var k=clone_tr.attr("data");
								var store_trs=$store_emp.find("tr");
								var flag=true;
								for(var j=0;j<store_trs.length;j++){
									store_tr=store_trs.eq(j);
									ks=store_tr.attr("data");
									if(ks==k){
										flag=false;
										break;
									}
								}
								if(flag){
									if(checked){
										$store_emp.append(clone_tr);
										clone_tr.find("input").attr("checked","true").click(function(){
                                            $(grid).find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
                                        });
									}
								}else{
									if(!checked){
										store_tr.remove();
									}
								}
							}
                            $(grid).find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
							return true;
						}
					};
                    var all_emp=$("#id_all_emp");
                    var op_type = $("#id_op_type");
					var emp_cfg_obj=$.extend(default_cfg_obj,cfg_obj);
                    var i_query = []
                    if (all_emp.length!=0){
//                        emp_cfg_obj.init_query=["all_emp="+all_emp.val()];
                          i_query =["all_emp="+all_emp.val()];
                          //兼容消费 qj 2012--03--14
                          if (op_type.length!=0){
                             i_query.push("&op_type="+op_type.val());
                         }
                    }
                    emp_cfg_obj.init_query=i_query;
					$grid.model_grid(emp_cfg_obj);
                    //$grid.get(0).g.init_query=[];
					//搜索栏
					var $search_div=$("<div class='div_select clearB'>"
										+"<div class='select_dept floatL'>"
											+"<table cellspacing='0' width='630px'><tr><td style='padding:0px 0px 4px 0px;' width='100' align='left'>"
												+"<div >"
													+"<span class='nowrap'><input type='radio' name='change_search' checked='checked' value='d' />"+gettext('按部门查找')+"</span>&nbsp;&nbsp;"
												+"</div>"
											 +"</td><td align='left' width='150'>"
												+"<div class='div_search_form'>"
													+"<div id='form_search'>"
													+"<span><input type='radio' name='change_search' value='e' />"+gettext('按人员编号/姓名查找')
													+"&nbsp;&nbsp;</span></div>"								
												+"</div>"
                                            +"</td><td align='left' width='380'>"
                                                +"<div>"
                                                    +"<div id='form_search_upload' class='displayN'>"
                                                    +"<span><input type='radio' name='change_search' value='f' />"+gettext('导入人员编号文件')
                                                    +"&nbsp;&nbsp;</span></div>"  
                                                +"</div>"    
											  +"</td></tr><tr><td colspan='3' height='25px' align='left'>"
												+"<div id='id_d'>"
													+"<div id='id_dept_parent' class='floatL'></div>"
													+"<div class='floatL select_AllInDept'><input type='checkbox' name='"+field_name+"_dept_all' id='id_dept_all'/><span>"+gettext('选择部门下所有人员')+"</span></div>"
												+"</div>"
												+"<div id='id_e' class='displayN'>"
													+"<input type='text' id='searchbar' value='' name='q' size='10' title='"+gettext('按照人员编号或姓名查找')+"'/>"
													+"<input type='button' value='' title='"+gettext('查询')+"' class='select_EmpSubmit' />"
												+"</div>"
                                                +"<div id='id_f' class='displayN'>"
                                                    +"<input type='file' name='upload_file' id='id_upload_file' size='40' value=''/>"
                                                +"</div>"           
												+"</td></tr></table>"
										+"</div>"
									  +"</div>"
									);
					$search_div.find("input[type=radio][name=change_search]").click(function(e){
						if(this.value=='d'){
							$("#id_d",$search_div).show();
							$("#id_e",$search_div).hide();
                            $("#id_f",$search_div).hide();
//                            $(this).parent().parent().parent().find("#dept_select_info").css({display:"none"});
                            $(".div_estopList",$grid).hide();
						}else if(this.value=='e'){
							$("#id_d",$search_div).hide();
							$("#id_e",$search_div).show();
                            $("#id_f",$search_div).hide();
							$(".div_estopList",$grid).hide();
							$search_div.find("#id_dept_all").removeAttr("checked");
//                            $(this).parent().parent().parent().find("#dept_select_info").css({display:"none"});
                            $(".div_estopList",$grid).hide();
						}
                        else if(this.value=='f'){
                            $("#id_d",$search_div).hide();
                            $("#id_e",$search_div).hide();
                            $("#id_f",$search_div).show();
                            $(".div_estopList",$grid).hide();
                            $search_div.find("#id_dept_all").removeAttr("checked");
//                            $(this).parent().parent().parent().find("#dept_select_info").css({display:"block"});
                            ///$grid.find("#show_deptment").hide();
                            $(".div_estopList",$grid).show();
                        }
					});
					//搜索
					$search_div.find("#id_e #searchbar").keydown(function(e){
						if(window.event){ // IE
							keynum = e.keyCode;
						}
						else if(e.which){ // Netscape/Firefox/Opera
							keynum = e.which;
						}
						if(13==keynum){
							$(".select_EmpSubmit",$search_div).click();
						}
					});
					$search_div.find("#id_dept_all").click(function(){
                        var select_depts = []
                        $("#id_dept_parent").find("input[name='deptIDs']").each(function(){ 	select_depts.push($(this).val()); 	})
						if(select_depts.length > 2000)
                        {
                            alert(gettext("所选的部门总数不能大于2000"))
                            return false;
                        }
						if(this.checked){
							if($("#id_dept_parent >input",$search_div).length==1){
								alert(gettext("请选择部门"));
								return false;
							}
							//$(this).parent().append("<div id='dept_select_info' style='color:red;'>"+gettext("该部门下面的人员已经全部选择!")+"</div>");
//							$(this).parent().parent().parent().find("#dept_select_info").css({display:"block"});
							$grid.find("#show_deptment").hide();
							$(".div_estopList",$grid).show();
						}else{
							//$(this).parent().find("#dept_select_info").remove();
//							$(this).parent().parent().parent().find("#dept_select_info").css({display:"none"});
							$(".div_estopList",$grid).hide();
						}
					});
					$(".select_EmpSubmit",$search_div).click(function(){
						var search_input=$search_div.find("#id_e #searchbar").eq(0);
						var v=search_input.val();
						var s_radio=$search_div.find("input[type=radio][name=change_search][checked]").val();
						var query=[];
						var dv=[];
//                        if (all_emp.length!=0){
//                            query=["all_emp="+all_emp.val()];
//                        }
                        if (all_emp.length!=0){
                                 query=["all_emp="+all_emp.val()];
                                 //兼容消费 qj 2012--03--14
                                 if (op_type.length!=0){
                                    query.push("&op_type="+op_type.val());
                                }
                             }
						if(s_radio=="d"){//部门
							$.each($search_div.find("input[name=deptIDs]"),function(i,e){
								dv.push($(this).val());
							});
							dv=dv.join(",");
							if(dv.length!=0){
								query.push("DeptID__id__in="+dv);
							}
                            if($search_div.find("input#id_selectchildren").attr("checked")){
                                query.push("checked_child=true")
                            }else{
                                query.push("checked_child=false")
                            }
                            
						}
						if(s_radio=="e"){//人员
							if($.trim(v).length!=0){
								query.push("q="+v);
							}
						}
						
						var g=$grid.get(0).g;
						g.init_query=query;
						g.load_data();
						search_input.select();
						if(emp_cfg_obj.multiple_select){
							var tr=$grid.find("#id_tbl tbody tr");
							if(tr.length==1){
								var tr_tmp=tr.clone();
                                var $store_emp=$grid.find("#id_store_select_emp");
								var l=$store_emp.find("tr[data='"+tr_tmp.attr("data")+"']");
								if(l.length==0){
									var input_check=tr_tmp.find("td input");
                                    input_check.click(function(){
                                        $grid.find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
                                    });
									$store_emp.append(tr_tmp);//1
									input_check.attr("checked",true).attr("name",emp_cfg_obj.field_name);//2 一和二调换一下在ie中就不可以
                                    $grid.find("#id_count_s").text("("+$store_emp.find("tr input[checked]").length+")");
								}
							}
						}
						return false;
					});
					$grid.prepend($search_div);
					/**弹出开始***/
					if(emp_cfg_obj.popup){
						var corner_tbl=$grid.parents("#id_corner_tbl");
//						$grid.before("<div class='title noBgImg noBorder '><span id='id_close' style='margin-top: 1px;' class='close btn '>确定</span></div>");
						$search_div.append("<div class=' title noBgImg noBorder empOKBtn' id='emp_ok_btn'><span id='id_close' style='margin-top: 1px;' class='close btn '>确定</span></div>");

						var d=new Date();
						var div_drop="id_drop_"+d.getMinutes()+d.getSeconds()+d.getMilliseconds();
						corner_tbl.before("<div id='"+div_drop+"'>"
							+"<input type='text' id='id_pop_emp' class='wZBaseCharField required' data='' readonly='readonly' />"
							+"<span class='btn_showEmpBox'>"
								+"<img alt='"+gettext('打开选人框')+"' src='/media/img/sug_down_on.gif' id='id_drop_emp' />"
							+"</span>"
							+"</div>"
						);
						corner_tbl.css({position:"absolute"});
						corner_tbl.hide();
						corner_tbl.find("#id_close").click(function(){
							corner_tbl.hide();
							var obj_strings="";
							var k_strings="";
							if(emp_cfg_obj.multiple_select){
								$.each($grid.find("#id_store_select_emp").find("tr"),function(index,elem){
									if($(elem).find("input").attr("checked")){
										obj_strings+=$(elem).attr("title")+",";
										k_strings+=$(elem).attr("data")+",";
									}
								});
								$("#"+div_drop).find("#id_pop_emp").val(obj_strings).attr("data",k_strings);
							}else{
								var selected_objs=$grid.get_selected();
							    obj_strings=selected_objs.obj_strings.join(",");
								k_strings=selected_objs.keys.join(",");
								$("#"+div_drop).find("#id_pop_emp")
									.val(obj_strings)
									.attr("data",k_strings)
                                    .trigger("change");
							}
							return false;
						});
						if(emp_cfg_obj.select_record){//如果是编辑第一次加载的时候选中记录
							var title=$grid.find("#id_tbl tbody tr").attr("title");
							if(title){
								$("#"+div_drop).find("#id_pop_emp").val(title);
							}
						}
						$("#"+div_drop).find("#id_drop_emp").click(function(e){
							corner_tbl.show();
						});
					}else{
						$search_div.append("<div class='floatL btn_emp_slideUp' id='id_slide' title='"+gettext('收起')+"'></div>");
						$("#id_slide",$search_div).click(function(event){
							if($(this).hasClass("btn_emp_slideDown")){
								$(this).removeClass("btn_emp_slideDown").addClass("btn_emp_slideUp");
								$(this).attr("title",gettext('收起'));
							}else{
								$(this).removeClass("btn_emp_slideUp").addClass("btn_emp_slideDown");//btn_emp_slideUp
								$(this).attr("title",gettext('展开'));
							}
							$search_div.siblings().toggle();
						});
					}
					/**弹出结束***/
					if(emp_cfg_obj.select_record){//如果是编辑第一次加载的时候选中记录
						$grid.find("#id_tbl tbody tr td input").attr("checked","true").attr("name",emp_cfg_obj.field_name);
					}
					if(!emp_cfg_obj.multiple_select){
						$grid.find("#id_dept_all").parent("div").hide();
						$grid.find(".grid").attr("class","grid_only clearL");
					}

					$.ajax({ 
						type: "POST",
						url:"/"+surl+"data/personnel/Department/choice_data_widget?name=deptIDs&multiple=true&flat=False",
						dataType:"html",
						success:function(json){
							$grid.find("#id_dept_parent").html(json);
							$grid.find(".close").eq(0).click(function(e){
								$search_div.find("#id_e input.select_EmpSubmit").click();
							});
							/*$grid.find("#id_dept li").click(function(event){
									$search_div.find("#form_search input.select_EmpSubmit").click();
									return false;
							});*/
							
						}
					});	
					
					if(emp_cfg_obj.multiple_select){
						var mul_store=$("<div class='div_selection_emp'><div class='div_estopList'></div><div class='div_selection_emp_Title'>"+gettext("已选择人员")+"<span id='id_count_s'>(0)</span></div><div class='div_clearBtn'><span class='action_clear1'>&nbsp;</span><a id='id_clear' href='javascript:void(0);' class='Link_blue1' >"+gettext("清除")+"</a></div><div class='div_store_emp'><table id='id_store_select_emp' class='store_emp table' width='100%'></table></div></div>");
						$grid.append(mul_store);
						$("#id_clear",mul_store).click(function(event){
							var $store_emp=$grid.find("#id_store_select_emp");
                            $store_emp.empty();
                            $grid.find("#id_count_s").text("(0)");
						});
					}
					$grid.get(0).g.get_store_emp=function(){
						var ret=[]
						$grid.find("#id_store_select_emp input[type='checkbox']").each(function(){
							if($(this).attr("checked"))
							{
								ret.push($(this).val());
							}
						});
						return ret;
					};
					$grid.parent().bgiframe();
				},
				//连接和替换查询条件,list原[],add_list需要添加的[],返回连接后的[],缺少置空
				concat_query:function(list_obj,add_query_list){
					  var list_temp=add_query_list;
					  var c1=0;
					  var c2=0;
                      for(var i in list_obj){
						  var flag=true;
						  for(var j in add_query_list){
								  la=list_obj[i].split("=");
								  lb=add_query_list[j].split("=");
								  if(la[0]==lb[0]){
										if(lb[1]!="*"){
											flag=false;
										}else{
											flag=null;
											c1=j;
										}
								  }
						  }
						  if(flag){
								list_temp.push(list_obj[i]);
						  }else if(flag==null){
								list_temp.splice(c1-c2,1);
								c2++;
						  }
                      }
					  for(var j in list_temp){
						var v=list_temp[j].split("=");
						if(v[1]=="*"){
							list_temp.splice(j,1);
						}
					  }
                      return list_temp;
				
				},			
				//替换已有的查询条件，返回新的查询条件
			getQueryStr:function(q, keys, append)
				{
					if(append && append.indexOf('?')==0)
						append=append.substr(1,1000)
					if(q.indexOf('?')<0)
					{
						if(append) return "?"+append;
						return q;
					}
					var qry=q.split("?")[1].split("&");
					var newQry=[];
					var rm=0;
					for(var i in qry)
					{
						rm=0;
						qk=qry[i].split("=")[0];
						for(var j in keys)
						{
							var k=keys[j];
							if((k==qk) ||
								(k.substr(k.length-1,1)=="*" && qk.indexOf(k.substr(0,k.length-1))==0))
							{
								rm=1;
								break;
							}
						}
						if(0==rm && qry[i].length>0) newQry.push(qry[i]);
					}
					if(newQry.length)
						return "?"+newQry.join("&")+(append?("&"+append):"");
					else
						return append?("?"+append):q.split("?")[0];
				},		
				/*
				{
					"verbose_name":"传送到设备",
					"hint":"把员工传送到指定设备",
					"confirm":"Let %s 传送到设备, are you sure?",
					"params":[{'title':'选择要传送到的设备', 'name':'Device', 'validate':'', 'widget':choice_data("testapp","Device")},
						{'title':'选择在设备上的时间范围', 'name':'time_range', 'validate':'', 'widget':"time_range"}
					]
				}
				*/
			_choice_data:function($container, app, model, multiple, filter)
				{
					return function(name, validate){
						var id='id_div_param_'+name;
						var html="<div id='"+id+"' style='width: 100%;'><select><option>---</option></select></div>"
                        $container.find("form").append(html);
						var url=dbapp_url+app+"/"+model+"/choice_data_widget?name="+name;
						if(multiple) url+="&multiple=1";
						if(filter) url+="&"+filter;
						$.ajax({"url": url,
                            async: false,
                            type: "GET",
							success: function(data){
									var i=$container.find("form #"+id);
									if(i.length>0)
									{
										i.html(data);
										if(validate)
										{
											if(validate.indexOf("required")>=0)
											$("input,select", i).addClass('required');
										}
									}
							}
						});
					}
				},
				
			_build_widget:function(param)
				{
					if(typeof param.widget==typeof build_widget) return param.widget(param.name);
					var w=param.widget.split("|");
					var name=param.name
					var attr="";
					if(param.validate.indexOf("required")>=0) attr=" class=\"required\"";
					if(w[0]=='time_range')
						attr+=" maxlength=\"19\""
						return "<input "+attr+" name='"+name+"_from' size='19' /> <br /><label> to:<br /></label> <input "+attr+" name='"+name+"_to' size='19' />";
				},
				
			_default_buttons:function(dlg, ok_fun)
				{
					return { modal: true,
						buttons: {
							"Cancel": function() {
                                var c=dlg.find("#id_close")
                                return c.click();
								},
							"OK": function() {
								if(ok_fun && ok_fun()) return;
                                var c=dlg.find("#id_close")
                                return c.click();
								}
							}
						}
				},
			_data_filter_form:function(control, app, model, field, title)
				{
					var dlg=$('<div id="id_filter_param" title="'+title+'"><p><form id="id_filter_form"></form></p><div id="buttons"></div><div>');
					$.zk._choice_data(dlg, app, model, true)(app+'_'+model);
                    var opt=$.zk._default_buttons(dlg, function(){
						var f=$("form", dlg);
						if(f.valid())
						{
                            var values=[];
                            var va=f.serializeArray();
                            for(var i in va) values.push(va[i].value);
							if(values.length==0) return true;
							var query=field+"__in="+(values.join(','));
                            var g=$($(control).attr("rel")).get(0).g;
			                g.init_query=$.zk.concat_query(g.init_query,[query]);
		                    g.load_data();
            			}
						else return true;
						return false;
					});
					dlg.dialog(opt);
					render_widgets(dlg);
				},
				
			_timerange_filter_form:function(control, field, title)
				{
					var name="time_range"
					var html='<div id="id_filter_param" title="'+title+'"><p><form id="id_filter_form">';
					attr=" maxlength=\"19\" size=\"19\"";
					html+="<input  "+" class='date'"+attr+" name='"+name+"_from' /> <br /><label> to:<br /></label> <input "+" class='date'"+attr+" name='"+name+"_to' />";
					dlg=$(html);
					dlg.dialog($.zk._default_buttons(dlg, function(){
						var f=$("form", dlg);
						if(f.valid())
						{
							var from=$('form input[name=time_range_from]',dlg)[0].value;
							var to=$('form input[name=time_range_to]',dlg)[0].value;
							var newSearch="";
							if(from>"") newSearch=field+"__gte="+from;
							if(to>"") newSearch+=(newSearch>""?"&":"")+field+"__lte="+to;
							var grid=$("div.ui-widget-content:has(div table#changelist #"+control.id+")");
							grid.each(function(){ if($("#"+control.id, grid)[0]==control) $("#"+grid[0].id).get(0).g.load_data([field+"__*"], newSearch);});
						}
						else return true;
						return false;
					}))
					render_widgets();
				},                       
				//新建记录时执行此函数-remark added by darcy
				_processNewModel:function(urlAddr,grid, event,after_get){
					var varButtons={"Save and New":function(form){ form.submit(true);}}
					$.zk._processEdit(urlAddr,grid,varButtons, event,after_get);
				},
				//编辑记录时执行此函数-remark added by darcy
				_processEditId:function(urlAddr,gridId, event,after_get){
					$.zk._processEdit(urlAddr,$("#"+gridId).get(0),undefined, event,after_get);
				},		
				//新建记录和编辑记录时执行代码的公共部分-remark added by darcy	
				_processEdit:function(urlAddr,grid, additionsBtn, event,after_get){
					var varButtons={};
					if(additionsBtn){varButtons=additionsBtn;}
					$.extend(varButtons,{ 
						"OK":function(form){form.submit(); },	
						"Cancel": function(form)
						{
							form.close();
							if(typeof(after_cancel)=="function"){
								after_cancel();
							}
                            before_submit=undefined;			
						} 
					});
					$.zk._processForm(urlAddr,varButtons,grid, event,after_get);	
				}, 
	            _processForm:function(urlAddr, buttons,grid, event,after_get){ 
					var dt=new Date();
					var url_stamp="";
					if(urlAddr.indexOf("?")!=-1){
						url_stamp=urlAddr+"&stamp="+dt.getTime();
					}else{
						url_stamp=urlAddr+"?stamp="+dt.getTime();
					}
					$.ajax({ 
							type:"GET", 
							url:url_stamp, 
							dataType:"html", 
							//async:false, 
							success:function(msg){
								if($("div.class_div_edit").length>0){
									if(confirm(gettext("编辑还未完成，已临时保存，是否取消临时保存?"))){
										$("div.class_div_edit").remove();
									}else{
										return;
									}
								}
								$.zk._create_form_from_html(msg, urlAddr, buttons, grid, event,after_get,
									(msg.indexOf("swift-form")>0)? $.zk._processFormLoop_swift : $.zk._processFormLoop);
								if(grid.g){
									$.zk._hide_switch(true,grid.g.do_action_masker_div);//隐藏
								}else{
									$.zk._hide_switch(true);
								}
								if(after_get){
									after_get();
								}
							}
					}); 
				},
				_create_form_from_html: function(blockHtml, urlAddr, buttons, grid, event,after_get, form_process)
				{
						if(window.class_div_edit_id==undefined) {
							window.class_div_edit_id=1
						}
						var id="id_"+window.class_div_edit_id;
						window.class_div_edit_id+=1;
						var varDivEdit=null;
						if(grid.g.do_action_template){
							varDivEdit=grid.g.do_action_template;
							varDivEdit.append(blockHtml);
						}else{
							$(grid).after('<div class="class_div_edit" id="'+id+'" model_id='+$(grid).attr("id")+' style="display:none;">'+blockHtml+'</div>'); 
							varDivEdit=$("div.class_div_edit#"+id);
						}
						//添加按钮
						var varDivButtons="<div class='editformbtn'>";
						for( var i in buttons){
							varDivButtons+='<div class="lineH22 img_padding" ><span class="action_'+i.replace(/ /g,"")+'"></span><a class="Link_blue1" href="javascript:void(0)" id="'+i.replace(/ /g,"")+'" >'+gettext(i)+'</a></div>';
						}
						varDivButtons+="</div>";
                        var exist_buttons = $(".editformbtn");
                        if(exist_buttons.length != 0 ){//如果已经定义好了按钮容器editformbtn，就不自动生成
                            varDivEdit.append(exist_buttons);
                        }else{
                            varDivEdit.append(varDivButtons);
                        }
	
						//关闭事件{isReflash,isShow}
						var varClose=function(isReflash){
							if(grid.g.do_action_template){
								varDivEdit.empty();
							}else{
								varDivEdit.remove();
							}
						    $(grid).show();
							if(isReflash){
								if(grid) grid.g.load_data(); 
							}
							//if(is_back){
								if(grid.g){
									$.zk._hide_switch(false,grid.g.do_action_masker_div);//隐藏
								}else{
									$.zk._hide_switch(false);
								}
							//}
							
							if(typeof(after_close)!="undefined"){
								after_close();
							}
						}
						var varSubmit=function(isContinue){
							if(typeof(before_submit)!= "undefined"){
								if(!before_submit()){
									return;
                                };
                            }					

							$form=varDivEdit.find("#id_edit_form");
							if($form.valid()){ 
                                if(typeof(before_submit_edit)!="undefined"){
                                    before_submit_edit();
                                }
                                $form.ajaxSubmit({ 
                                    url:urlAddr, 
                                    dataType:"html", 
                                    //async:false, 
                                    success:function(msgback){ 
                                        var IS_BACK=true;
                                        var IS_REFLASH=true;
                                       
                                        if(msgback.indexOf('{ Info:"OK" }')!=-1){
                                            //isContinue?varClose(!IS_BACK,IS_REFLASH):varClose(IS_BACK,IS_REFLASH);
                                            if(isContinue){
                                                //$.zk._create_form_from_html(blockHtml,urlAddr,buttons,grid, event, form_process);
                                                $form.get(0).reset();
                                                grid.g.load_data();
                                                if(typeof(after_save_continue)!="undefined"){
                                                    after_save_continue();
                                                }
                                                //add for refresh
                                                varDivEdit.remove();
                                                $.zk._processForm(urlAddr, buttons, grid, event,after_get);
                                                var interval=window.setInterval(function(){after_back(interval)},50);
                                                function after_back(interval){
                                                    var $info_div=$("#id_info");
                                                    if($info_div.length!=0){
                                                        $info_div.html("<ul class='successlist'><li>"+gettext('保存成功!')+"</li></ul></td>").hide().show(100); 
                                                        window.clearInterval(interval);
                                                    }
                                                }
                                            }
                                            else
                                            {
                                                before_submit = undefined;//释放变量内存空间，防止各操作变混用变量(如新增和删除等)
                                                varClose(IS_REFLASH);
                                                if(typeof(after_save_return)!="undefined"){
                                                    after_save_return();//保存成功、删除成功并返回后执行的操作
                                                }
                                            }

                                            if(typeof(after_submit)!="undefined"){
                                                after_submit();
                                            }
                                        }else{ 
                                            //varClose(!IS_BACK);
                                            var $error=$(msgback).find("ul.errorlist");
                                            if($error.length!=0){
                                                $("#id_info").html($error.eq(0)).hide().show(100); 
                                            }else{
                                                $("#id_info").html(msgback);
                                            }
                                            //$.zk._create_form_from_html(msgback,urlAddr,buttons,grid, event, form_process); 
                                        }
                                    } 
                                }); 	
							}else{
                                $form.find("input.error").eq(0).focus();
                            }
						}
						var form={close:varClose,submit:varSubmit,form:varDivEdit}
						var fun=function(f){ return function(){ f(form); }; };
						for(var i in buttons){
							$(".editformbtn a#"+i.replace(/ /g,""), varDivEdit).click( fun(buttons[i]) );
						}
						if(typeof(after_init)!="undefined"){
							after_init();
						}
						form_process(event, varDivEdit, varClose, grid,varSubmit);
						if(typeof(after_process)!="undefined")
						{
							after_process();
						}
				},
	            _processFormLoop_swift:function(event, varDivEdit, varClose, grid,varSubmit){
                    $(grid).hide();
                    var var_close=varClose;
                    var var_div_edit=varDivEdit;
                    var var_submit=varSubmit;
                    varDivEdit.show().dialog({
                        on_load:function(obj){
                                var $overlay=obj.target.getOverlay();
                                $overlay.addClass($(grid).attr("id"));
                                var btn_close_dialog=$overlay.find("#id_close");
                                btn_close_dialog.unbind().click(function(){
                                    $("div#overlay_target").overlay().close();
                                    $overlay.find("div.class_div_edit").remove();
                                    var_close();
                                    $("body").removeClass("indexBody");
                                    $overlay.removeClass($(grid).attr("id"));
                                });
                                $overlay.find("#Cancel").unbind().click(function(){
                                    btn_close_dialog.click();
                                });
                                $overlay.find("#OK").click(function(){
                                    $("div#overlay_target").overlay().close();
                                    $overlay.find("div.class_div_edit").remove();
                                    var_submit();
                                    var interval=window.setInterval(function(){after_come_back(interval)},50);
                                    function after_come_back(interval){
                                        if($("body").hasClass("indexBody")){
                                            $("body").removeClass("indexBody");
                                            window.clearInterval(interval);
                                        }
                                    }
                                });
                        }
                    });
				},
				//编辑记录 
	            _processFormLoop:function(event, varDivEdit, varClose, grid,varSubmit){ 
						varDivEdit.find(".ui-icon-closethick").click(function(){
							varClose();
						});
						if(grid){
							if(grid.g.show_related_op){
								grid.g.render_row_operations(grid.current_row,$(".form_operation"));
							}
						}
						//未编辑完的文档暂时保持
						$("#id_tab").find(".portlet-header .ui-icon-contact").remove();
						varDivEdit.find(".ui-icon-circle-arrow-s").click(function(){
							varDivEdit.hide();
							var restore=$("#id_tab").find(".portlet-header").prepend('<span title="'+gettext("恢复")+'" class="ui-icon ui-icon-contact cursorP"></span>');
							restore.find(".ui-icon-contact").click(function(){
								$(grid).hide();
								varDivEdit.show();
								$(this).remove();
								if(grid.g){
									$.zk._hide_switch(true,grid.g.do_action_masker_div);//隐藏
								}else{
									$.zk._hide_switch(true);
								}
							});
						   $(grid).show();
						   if(grid.g){
								$.zk._hide_switch(false,grid.g.do_action_masker_div);//隐藏
							}else{
								$.zk._hide_switch(false);
							}
						});
						$(grid).hide();
						varDivEdit.show();
				}, 
	            _setWidgetMaxWidth:function () 
					{ 
						var form=$("#id_edit_form"); 
						var w=form.width()-$("tr th", form).width()-15; 
						$("tr td select, tr td div", form).each(function(){ 
								if($(this).width()>w) $(this).width(w); 
						}); 
					}
				
			}//end plugin zk
		);
		
})(jQuery);

function render_dropdown(tree_parent, multiple,need_async_nodes){
    //$treec=$(a).parent().find('#show_deptment');
    $treec=tree_parent;
	$treec.bgiframe();
    //var input=$treec.parent().parent().find(">input")[0];
    //$treec.css("margin-left", (12-$(input).width())+"px");
    return render_dept_($treec, multiple,true);
}

function clear_none(p){
    $treec=$(p).parent().parent();
    var inputs=$treec.parent().parent().find(">input");
    $treec.find("ul li#"+inputs[1].value+" p").removeClass("s");
    inputs[1].value="";
    inputs[0].value="";
    $treec.hide();
}

function render_dept_($treec, multiple,need_hide){
	$treec.find(".treeview li p").unbind('click');
	$treec.find(".treeview li div").remove();
    $treec.find("ul.filetree").treeview({
        collapsed: true
    });
    $treec.find("ul.filetree").find(">li div").click();
    if(need_hide){
        $treec.hide();
    }else{
        $treec.show();
    }
    var $all_nodes=$treec.find(".treeview li p");
    $all_nodes.click(function(ev, b, c){
			var node=ev.currentTarget;
			var id=node.parentNode.id;
			var inputs=$treec.parent().parent().find(">input");
			if(multiple){
                var hidden_input_name= $($treec.find("ul.treeview")[0]).attr("name");
				var selected=!($(node).hasClass("s"));//交替不影响node
				var nodes=null;
                nodes=[node];
                var insert_inputs=[];
                var objects_value=[];
                $.each(nodes,function(i,e){
                    var id=this.parentNode.id;
                    var $node=$(this);
                    var node_selected=$node.hasClass("s");
                    if(selected && node_selected){//排除父节点和子节点都选中
                    		return;
                    }else if(!selected && !node_selected){//排除父节点和子节点都没选中
                        return;
                    }
                    //父子不一致
                    if(selected){
                        //添加一个输入框
                        insert_inputs.push("<input type=hidden value="+id+" name="+hidden_input_name+">");
                    }
                    else{
                       //查找并删除该输入框
                      for(var i=1; i<inputs.length; i++){
                          if(inputs[i].value==id){
                              $(inputs[i]).remove();
                              inputs.splice(i,1);//减轻下一次循环的次数,这个地方可以不用合起来一起处理。
                              break;
                          }
                      }
                    }
                    $node.toggleClass("s");
                });
                //只在显示框中显示前50个部门的名称.
                $.each($all_nodes,function(ii,ee){
                    if(objects_value.length>50){
                        return;
                    }
                    if(objects_value.length==50){
                        objects_value.push("...");
                        return;
                    }
                    var $this=$(this);
                    if($this.hasClass("s")){
                        objects_value.push($this.html());
                    }
                });
                inputs.eq(0).val(objects_value.join(","));
                inputs.eq(0).after(insert_inputs.join(""));
                remove_inputs=null;
                insert_inputs=null;
			}else{
				$treec.find("ul li#"+inputs[1].value+" p").removeClass("s");
				$(node).addClass("s");
				inputs[1].value=id;
				inputs[0].value=$(node).text();
				if(need_hide){
					$treec.hide();
				}
			}
        });
    return false
}


function check_all(tree_ul)
{
    flag = $("#id_select_all").attr("checked");
    var $all_nodes=tree_ul.find(".treeview li p");
    $.each($all_nodes,function(i,e){
        var $node=$(this);
        var node_selected=$node.hasClass("s");
        if (node_selected && !flag ){
            $("#ck_title").text("选择全部")
            $node.click();
        }
        else if(!node_selected && flag)
        {
            $("#ck_title").text("全选取消")
            $node.click();
        }
//        alert("node_selected=="+node_selected)
        //var selected=!($(node).hasClass("s"))
        
    });
}

/** 
	* 用途：获取每月的最后一天日期值. 
	* 输入：date：年份；month：月份 
	* 返回：最大天数
	*/  
 function getMaxDay(year,month) {  
	 if(month==4||month==6||month==9||month==11)  
		 return 30;  
	 if(month==2)  
		 if((year%4==0&&year%100!=0) || (year%400==0))  
			 return 29;  
		 else  
			 return 28;  
	 return 31;  
 }   

function datetime_offset_by_month(dt, n){
	var year=dt.getFullYear();
	var month=dt.getMonth()+1+n;
	var day=dt.getDate();
	if(month>0){
		if(month>12){
			var c=Math.floor(month/12);
			month-=12*c;
			year+=c;
		}
	}else{
		var c=Math.ceil(month/12);
		month+=12*(-c+1)
		year-=(-c+1);
	}
	var tmp_day=getMaxDay(year,month);
	if(tmp_day<=day){
		day=tmp_day;
	} 
	return new Date(year,month-1,day);
}

 //将超过宽度的菜单放到下拉列表中去(处理缩放浏览器)
function resize_menu($container,$more,min_width,id_more){
    		var $app_menu=$container;
    		var $menu_more=$more;
            var min_width=min_width;
    		if($app_menu.width()<min_width)
    		{
    			var list=$("li",$menu_more);
                for(var i in list){
                    var $elem=list.eq(i);
                    $app_menu.append($elem);
                   
                    if($app_menu.width()>min_width)
                    {
                        $menu_more.prepend($elem);
                        return;
                    } 
                    
                }
    		}
    		else
    		{
    			var list=$app_menu.find("li");
    			for(var i=list.length-1;i>=0;i--)
    				{
    					$menu_more.prepend(list.eq(i));
    					 
    					if($app_menu.width()<min_width)
    					{
    						break;
    					}
    			}
    		}
            if($more.find("li").length==0){
                        $("#"+id_more).hide();
            }else{
                $("#"+id_more).show();
            }
			var mmli=$(".action_more_list").find("li");
			var mmw=0;
			for(i=0;i<=mmli.length-1;i++){
				if($(mmli[i]).width()>mmw)
				mmw=$(mmli[i]).width();
			}
			$(".action_more_list").css({width:mmw});
			$(".action_more_list>li").css({width:"100%"});
			$(".menu_more").bgiframe();
}
function selectck(){//初始化权限树的事件


    $.each($(".filetree").find("li ul ul "),function(){
      if($(this).find("li p").hasClass("s"))
    {
        $(this).parent("li").find("p").eq(0).addClass("s")
        $(this).parent("li").parent("ul").parent("li").find("p").eq(0).addClass("s")
    }
    });
    
	$(".filetree").find("li p").click(function(){
		//选中下级节点
	      if($(this).hasClass("s")){
	          var li_ps=$(this).next().find("p.t");
			  if(li_ps.length==0){//子节点
				$(this).removeClass("s");
				$(this).find("input").removeAttr("checked");
			  }else{
				  li_ps.add($(this)).removeClass("s");
				  li_ps.find("input").removeAttr("checked");
			  }
	      }else{
				var li_ps=$(this).next().find("p.t");
				if(li_ps.length==0){//子节点
					$(this).addClass("s");
					$(this).find("input").attr("checked","checked");
				}else{//全选的节点
					li_ps.add($(this)).addClass("s");
					li_ps.find("input").attr("checked","checked");
				}
	      }
		//结束选中下级节点
		//选中上级节点
		if($(this).hasClass("s")){
			$.each($(this).parent("li").parents("li"),function(index,elem){
				$(elem).find(">p.t").addClass("s");
				if($(elem).attr("operation")){
					$(elem).find(">ul > li >p[permission_code='can_"+$(elem).attr("operation")+"']")
							.addClass("s")
							.find(">input").attr("checked","checked");
				}else if(!$(elem).hasClass("root_node")){
				$(elem).find(">ul > li >p[permission_code*='browse']")
						.addClass("s")
						.find(">input").attr("checked","checked");
				}
			});
		}else{
			var p=$(this).parent("li");
			var li_p_li=p.parent("ul").parent("li");
			//选中的是浏览权限
			if(p.find(">p[permission_code*='browse']").length!=0 
			|| p.find(">p[permission_code='can_"+li_p_li.attr("operation")+"']").length!=0 ){
			   li_ps=li_p_li.find("p.t");
			   li_ps.removeClass("s");
			   li_ps.find("input").removeAttr("checked");
			}
		}
		//结束选中上级节点
		//选中当前权限时附带要选中的其他权限
		if($(this).hasClass("s")){
			var parent_li=$(this).parent("li");
			var selected_perms=$.trim(parent_li.attr("relate_perms"));
			if(selected_perms.length!=0){
				var list_perms=selected_perms.split(".");
				for(var i in list_perms){
					parent_li.parent("ul").find("p[permission_code="+list_perms[i]+"]").addClass("s").find(">input").attr("checked","checked");
				}
			}
		}
		//取消当前权限时附带取消AppOperation 浏览权限
		if(!$(this).hasClass("s")){
			var parent_ul=$(this).parents("ul");
			$.each(parent_ul.find("li"),function(index,elem){
				var cancel_perm=$(elem).attr("cancel_perms");
				if(cancel_perm){
					var list_cperms=cancel_perm.split(".");
					var flag=true;
					for(var i in list_cperms){
						p=parent_ul.find("p[permission_code='"+list_cperms[i]+"']");
						if(p.length==1 && p.hasClass("s")){
							flag=false;
							break;
						}
					}
					if(flag){
						$(elem).find(">p.t").removeClass("s").find(">input").removeAttr("checked");
						parent_ul.parent("li").find(">p.t").removeClass("s");
					}
					return true;//退出each
				}
			});
		}
		
		return false;
	  });
    $(".filetree").find(">li div").click();
}

function insert_tree_html(models){
	while(models.length!=0){
		var tmp=models.concat([]);
		var c=0;
		for(var i in tmp){
			if($("#"+tmp[i][0]).length!=0){
				$("#"+tmp[i][0]).find(">ul").append(tmp[i][2]);
				models.splice(i-c,1);
				c++;
			}else{//有可能是父节点还在models中，或者后台配置父节点有问题(删除)
                var flag=true;
                for(var j in tmp){
                    if(tmp[i][0]==tmp[j][1]){
                        flag=false;
                        break;
                    }
                }
                if(flag){
                    models.splice(i-c,1);
                    c++;
                }
            }
		}
	}
}

//但一个父节点只有一个根节点时，去掉父节点，只保留根节点。--darcy20110215
function remove_single_perm_node($root_node){
	$.each($root_node.find("li ul"),function(){
		if($(this).find("li").length==1){
			$(this).parent("li").replaceWith($(this).find("li"));
		}
	});
}

//用户多对多字段默认情况下
function check_selected(id){
    //所有节点添加标记，用来检查是否父节点和子节点被全选中--wangz
    $("#"+id+" .filetree").find("li p").addClass("u");
	
	//根节点 -- wangz
	var root = $("#"+id+" .filetree").find("li p:first");
	
	$("#"+id+" .filetree").find("li p").click(function(){
		//选中下级节点
		if($(this).hasClass("s")){
			var li_ps=$(this).next().find("p.t");
			if(li_ps.length==0){//子节点
				$(this).removeClass("s");
                $(this).addClass("u");
				$(this).find("input").removeAttr("checked");
                
                //任一子节点选中取消，根节点（全部项）取消选中--wangz
                root.removeClass("s");
                
				if($(this).parent().parent().find("p.s").length==0)//子节点全部不选中时，父节点也不能选中。
				{
					$(this).parents("li[id^='id_root_']").find("p:first").removeClass("s");
				}
			}
			else
			{
				li_ps.add($(this)).removeClass("s");
                li_ps.addClass("u");
				li_ps.find("input").removeAttr("checked");
                
                //父节点选中取消，根节点取消选中--wangz
                root.removeClass("s");                
			}
		}
		
		else
		{
			var li_ps=$(this).next().find("p.t");
			if(li_ps.length==0){//子节点
				$(this).addClass("s");
                $(this).removeClass("u");
				$(this).find("input").attr("checked","checked");
                
                //父节点被选中同时移除标记---added by wangz
                $(this).parents("li[id^='id_root_']").find("p:first").addClass("s");     
                $(this).parents("li[id^='id_root_']").find("p:first").removeClass("u");           
			}
			
			else
			{//全选的节点
				li_ps.add($(this)).addClass("s");
                $(this).removeClass("u");
                li_ps.removeClass("u");
				li_ps.find("input").attr("checked","checked");
			}
            
            if($("#"+id+" .filetree").children().find("li p.u").length==0)
            {
                root.addClass("s");
            }              
		}
		return false;
	  });
}

//编辑初始化时时检查
function check_root(id)
{   
    var root = $("#"+id+" .filetree").find("li p:first");
	var select_all=false;
    
    root.removeClass("s");
	$("#"+id+" li[id^='id_root_']").each(function(){

        if($(this).find("p.s").length == 0)//子节点没被选中
        {
            $(this).find("p:first").removeClass("s");
            $(this).find("p").addClass("u");
        }
        else
        {
            $(this).find("li p").addClass("u");
            $(this).find("li p.s").removeClass("u");
            $(this).find("p:first").addClass("s");
            $(this).find("p:first").removeClass("u");
        }
	});
    //子节点全被选中，添加全部项被选中状态
    if(!($("#"+id+" .filetree").children().find("li p.u").length > 0))//只有要一个未选中，就代表不能使用全选。-darcy20120131
    {
        root.addClass("s");
    }
	return false;
}

function page_load_effects(login_url,$gz,$loading_icon){
	//显示交互状态
	var hide_loading=["/iaccess/comm_error_msg/","/iaccess/GetRTLog/","/iaccess/GetDevLog/","/iaccess/EmpLevelSetPage/", "/iaccess/downdata_progress/", "/iaccess/GetData/?func=connect_dev", "/iaccess/GetData/?func=get_all_ip_com_sn","/iaccess/get_card_number/","/data/update_process","/data/get_import_progress"];
	$.ajaxSetup({ cache: false });
	$loading_icon 
		.bind(
				"ajaxSend", 
				function(evt, request, settings){
					var flag=false;
					for(var i in hide_loading){
						if(settings.url.indexOf(hide_loading[i])!=-1){
							flag=true;
						}
					}
					if(!flag){
						$gz.width(document.body.clientWidth)
						.height($(document).height() - 10 + "px")
						.show();
						$loading_icon.show();
                        //alert($(document).height()+","+$(window).height())
					} 
		}).bind(
				"ajaxComplete", 
				function(evt,request, settings){
                    if(request.responseText=="session_fail_or_no_permission" || request.responseText.indexOf("login_page_tag_for_ajax")!=-1){
                            if(settings.url.indexOf("jquery.zcommon.js")=="-1"){
                                alert(gettext("会话已经过期或者权限不够,请重新登入!"));
                                window.location.replace(login_url);
                            }
                            
                    }
					var flag=false;
					for(var i in hide_loading){
						if(settings.url.indexOf(hide_loading[i])!=-1){
							flag=true;
						}
					}
					if(!flag){
						setTimeout(function(){
							$loading_icon.hide();
							$gz.hide();
						},500);
					}
		}).bind(
				"ajaxSuccess",
				function(evt, request, settings){
					
				}
		); 
}

/*  
树形控件，多颗树时，ID不能一样。
dict_data:{
    "multiple":"",
    "dict_rows":[],
    "flat":true,
    "name":"",
    "disp":"",
    "value":"",
    "attr":{}
}
*/
function render_tree( dict_data ){
    var edit_object_id = null;

    //获取编辑的对象ID
    if (typeof(dict_data.attr.async_model+"_pk") == "function"){
        edit_object_id = eval(dict_data.attr.async_model+"_pk")();
    }else{
        edit_object_id = $("#id_model_pk").val();
    }
    //zTree树形控件配置项
    var settings = {
        checkable: dict_data["checkable"],
        async : true,
        isSimpleData : true,
        treeNodeKey : "id",
        treeNodeParentKey : "pId",
        asyncParam: ["id"], 
        asyncParamOther:{
            "checked_ids":dict_data.value,//需要选中的记录
            "multiple":dict_data.multiple,
            "edit_object_id":edit_object_id, //编辑的时候调用limit_parent_to
            "async_model":dict_data.attr.async_model,
            "limit":dict_data.attr.limit //树是否需要过滤本身和下级
        },
        showLine : true,
        showIcon : false,
        checkType :{ "Y": "", "N": "" },
        asyncUrl :"/personnel/get_children_nodes/",
        checkStyle :"radio",
        checkRadioType :"all"
    }
    
    var container = $("#"+dict_data["id"]);//树形控件ID
    //树形控件生存，异步构造异步加载
    if(dict_data["multiple"]){//是否多选
        settings.checkStyle = "checkbox";
    }
    if (dict_data.attr){ //异步的url
        if (dict_data.attr.async_url){
            settings.asyncUrl = dict_data.attr.async_url;
        }
    }
    
    var obj_tree = container.zTree(settings,dict_data["dict_rows"]);
    
    //container.get(0).obj_tree = obj_tree;//设置对象到dom中
    var parent_container = container.parent();
    obj_tree.setting.callback.beforeAsync = function (treeId, treeNode){//把当前要异步的节点的选中状态传到后台
        /*多选，异步请求的节点复选框选中了，则其子节点也要选中。
            如果没有选中，后台需要判断其关联关系中的节点要选中。*/
        /*单选，前端要判断是否复选框已经有选中的节点，
        如果有则前端js需要把返回回来的已经选中的几点把其置为不选中*/
        //如果多选，并且选中了是否选择下级复选框
        var has_checked_nodes = false;
        if (obj_tree.getCheckedNodes().length !=0){
            has_checked_nodes = true;
        }
        obj_tree.setting.asyncParamOther.checked  = treeNode.checked;
        obj_tree.setting.asyncParamOther.has_checked_nodes = has_checked_nodes;
        if(dict_data.multiple){ //多选需要传是否包含下级的参数
            var checked = parent_container.find("#id_selectchildren").attr("checked");
            obj_tree.setting.asyncParamOther.select_childrens = checked;
        }
        return true;
    }
    
    var refresh_data = function(event, treeId, treeNode,hide){//刷新，隐藏的input的值
        var nodes = obj_tree.getCheckedNodes();
        if(nodes.length>0){
            //单选多选都通用
            var inputs_ids = [];
            var verbose = [];
            for(var i=0 ; i<nodes.length; i++){
                inputs_ids.push('<input type="hidden" name="'+dict_data["name"] + '" value="'+nodes[i].id +'"/>');
                verbose.push(nodes[i].name);
            }
            verbose = verbose.join(" ");
            if (verbose.length>60){
                verbose = verbose.substr(0,50)+"...";
            }
            var tmp_show_input = parent_container.find("#id_show_input");
            tmp_show_input.val( verbose );
            tmp_show_input.nextAll("input:hidden").remove();
            tmp_show_input.after(inputs_ids.join(""));
            if (hide){ //弹出式
                parent_container.find("#show_deptment").hide();
            }
        }else{
            if( dict_data.multiple){
                var tmp_show_input = parent_container.find("#id_show_input");
                tmp_show_input.val("");
                tmp_show_input.nextAll("input:hidden").remove();
            }
        }
    };
    
    obj_tree.setting.callback.change =function(event, treeId, treeNode){
        
        if (dict_data.attr.change){//自定义事件
            try{
                eval(dict_data.attr.change)(event, treeId, treeNode);
            }catch(e){}
        }else{
            var hide = false;
            if( !dict_data.flat && ! dict_data.multiple ){ //弹出,单选需要隐藏，多选不需要隐藏
                hide = true;
            }
            refresh_data(event,treeId,treeNode,hide); 
        }
    }  //刷新，隐藏的input的值
    obj_tree.setting.callback.click =function(event, treeId, treeNode){
    	if (dict_data.attr.click){//自定义事件
	        try{
	            eval(dict_data.attr.click)(event, treeId, treeNode);
	        }catch(e){}
    	}
    };
    obj_tree.setting.callback.asyncSuccess =function(event, treeId, treeNode){ //点击异步图标，不需要隐藏控件
        refresh_data(event,treeId,treeNode,false);
    }  //刷新，隐藏的input的值
    
    //平铺单选html
    var single_flat ='<input id="id_show_input"  type="hidden" /> \
        <div class="parent_parent"> \
            <div id="show_deptment"> \
                <div id ="id_dept"> \
                </div> \
            </div> \
        </div>';
        
    //平铺多选html
    var multiple_flat ='<input id="id_show_input" type="hidden"> \
        <div id="show_deptment"> \
            <div id="id_dept"> \
                <div class="title"> \
                    <span class="span_selectchildren"> \
                        <span> \
                            <input type="checkbox" id="id_selectchildren" name="checked_child" ></input> \
                        </span> \
                        <span class="title_selectchildren">包含下级 &nbsp;&nbsp;</span> \
                    </span> \
                </div> \
            </div> \
        </div>';
    
    //弹出单选html
    var single_pop =
        '<input id="id_show_input" type="text" readonly="readonly" class="wZBaseCharField input_showDeptTree"> \
        <span class="btn_showDeptTree"> \
            <img id="id_drop_dept" src="/media/img/sug_down_on.gif" onclick="javascript:$(this).parent().find(\'#show_deptment\').show().bgiframe();"> \
            <div style="display: none;" id="show_deptment"> \
                <div class="title"> \
                    <span id = "id_empty_input" class="span_selectNone Link_blue1"> \
                        <a href="javascript: void(0)">撤销选择</a>&nbsp;&nbsp; \
                    </span> \
                    <span class="close btn">确定</span>\
                </div> \
                <div id="id_dept" class="dispayN"> \
                </div> \
            </div> \
        </span>';
    
    //弹出多选html
    var multiple_pop =
        '<input id="id_show_input" type="text" readonly="readonly" class="wZBaseCharField input_showDeptTree"> \
        <span class="btn_showDeptTree"> \
            <img id="id_drop_dept" src="/media/img/sug_down_on.gif" onclick="javascript:$(this).parent().find(\'#show_deptment\').show().bgiframe();"> \
            <div style="display: none;" id="show_deptment"> \
                <div class="title"> \
                    <span class="span_selectchildren"> \
                        <span> \
                            <input type="checkbox" id="id_selectchildren" name="checked_child" ></input> \
                        </span> \
                        <span class="title_selectchildren">包含下级 &nbsp;&nbsp;</span> \
                    </span> \
                    <span class="close btn">确定</span> \
                </div> \
                <div id="id_dept" style="height:220px;"  class="dispayN"> \
                </div> \
            </div> \
        </span>'; 
        
    if(dict_data.multiple){//多选初始化
        if( dict_data.flat){
            parent_container.prepend( multiple_flat );
        }else{
            parent_container.prepend( multiple_pop );
        }
        var checked_input  = parent_container.find("#id_selectchildren");
        checked_input.attr("name",dict_data.name+"checked_child");
        checked_input.click(function(){
            if($(this).attr("checked")){
                obj_tree.setting.checkType =  { "Y": "s", "N": "s" };
            }else{
                obj_tree.setting.checkType =  { "Y": "", "N": "" };
            }
        });
    }else{//单选初始化
        if( dict_data.flat){
            parent_container.prepend( single_flat );
        }else{
            parent_container.prepend( single_pop );
        }
        if(dict_data.required){
            parent_container.find("#id_show_input").addClass(" required ");
            parent_container.find("#id_empty_input").hide();
        }else{
            parent_container.find("#id_empty_input").click(function(){
                var tmp_show_input = parent_container.find("#id_show_input");
                tmp_show_input.val( "" );
                tmp_show_input.nextAll("input:hidden").remove();
            });
        }
    }
    
    if(dict_data["value"].length!=0){
        var exists_ids = dict_data["value"].split(",")
        var hidden_inputs =[] ;
        for(var i =0; i<exists_ids.length; i++){
            hidden_inputs.push('<input type="hidden" name ="'+dict_data["name"]+'" value = "'+exists_ids[i]+'"/>');
        }
        parent_container.find("#id_show_input").after(hidden_inputs.join(""));
    }
    
    
    if ( ! dict_data.flat){//弹出式控件
        parent_container.find(".close").click(function(){ //确定按钮初始化
            $(this).parent().parent().hide();
        });
    }
    
    parent_container.find("#id_dept").append(container);
    parent_container.find("#id_show_input").val(dict_data["disp"]);
    
    if(dict_data.attr.call_back){
        try{
            eval(dict_data.attr.call_back)(obj_tree);
        }catch(ee){}
    }
}
