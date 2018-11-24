(function($){
/**************与模型无关的datalist开始*************/
//事件函数API
    var jquery_fun=[ 
                    "on_row_click","on_dbl_click","on_selected",
                    "on_all_selected","on_pager","on_child_click",
                    "after_create"
                  ];
    for(var i in jquery_fun){
        var fun_k=jquery_fun[i];
        var def_fun=function(fun_k){
            return function(f){
                this.get(0).g[fun_k]=f;
            };
        };
        $.fn[fun_k]=def_fun(fun_k);
    }
    $.fn.get_selected=function(){
        return this.get(0).g.get_selected();
    };
    //grid的创建
    $.fn.grid=function(opt){
        var self=this.get(0);
        var g={
        	action_onclick_continue:true,	//on_click 后，href是否继续
            scrollable:false,//是否滚动,true默认滚动，false不滚动,{h:300,w:600}使用高为300，宽为600
            heads:[],//是一个列表，表示显示在列表表头上的文字; 
            fields:[],//是一个列表，表示显示在列表表头上的文字; 
            data:[],//二维列表，表示多行的数据；
            disable_cols:["id","data_verbose_column"],//不可见的列
            key_field:"id",  //关键字段名
            data_verbose_column:"", //数据显示字段名，为空字符串
            show_head: true,//显示头
            actions: {},//是一个对象，表示定义在该数据模型上的操作列表，其每一个操作是一个json对象
            base_url: "", //表示当前数据页面的URL; 
            row_operations: [],//为一个列表，表示要放在对当前记录进行的操作栏的操作名（字符串）
            multiple_select: true,//是否多选
            page_count: 11, //页总数
            current_page: 1, //当前页码
            record_count: 160, //如果为零，则不在页面上显示总记录数
            layout: "table",
            grid_name:"",//记录的名字
            tbl_id:"id_tbl",//"table"-表格形式显示, "icon"-大图标形式显示, "compact"-小图标形式显示 
            a_div:$('<div class="action Link_blue1"></div>'),//操作的div
            p_div:$('<div  class="pages floatR Link_blue2"></div>'),//放置分页的div
            t_div:$('<div class="list_outBox"></div>'),//放置列表的div
			//r_div:$('<div class="dt_hdiv_right"></div>'),//遮挡thead滚动条的div
			grid_div:$('<div class="grid clearL"></div>'),//
            init_data:function(){//初始化数据
                g.fields_store=g.fields.concat([]);
                var tmp_fields=g.fields.concat([]);
                for(var i in tmp_fields){
                    g.fields[tmp_fields[i]]=i;
                }
                g.key_index=g.fields[g.key_field];
                g.data_verbose_index=g.fields[g.data_verbose_column];
                if($("body").find("#obj_tooltip").length==0){
                    $("body").prepend("<div id='obj_tooltip'></div>");
                }
            },
            render_tbl:function(){//按照配置条件，生成html列表
                var data=g.data;
                var fields=g.fields;
                var heads=g.heads;
                var disable_cols=","+g.disable_cols.toString()+",";//不显示的列
                var key_index=g.key_index;//id的列索引
                var data_verbose_index=fields[g.data_verbose_column];
                var html_tbl="";
                var html_thead="";
                var html_tbody="";
                var html_tfoot="";//"<tfoot></tfoot>";
                var url=g.base_url;
                //头部
                for(var i=0;i<heads.length;i++){
                    if(disable_cols.indexOf(","+fields[i]+",")==-1){
                        html_thead+="<th field='"+fields[i]+"' id='"+fields[i]+"'>"+heads[i]+"</th>";
                    }
                }
                var chk_selected_all="";
                if(g.multiple_select!=null){
                    if(g.multiple_select)
                        chk_selected_all="<th class='class_select_col'><input type='checkbox' class='chk_selected_all'/></th>";
                    else
                        chk_selected_all="<th><input type='checkbox' class='chk_selected_all' name='chk' disabled='disabled' /></th>";
                }
                html_thead="<thead><tr>"+chk_selected_all+html_thead+"</tr></thead>";
                if(!g.show_head){
                    html_thead="<thead></thead>";
                }
                //数据区
                var name=g.grid_name?" name='"+g.grid_name+"'":"";
                var rows=[];
                for(var i in data){
                    var html_row="";
                    var key=data[i][key_index];
                    var display=data[i][data_verbose_index];
                    var row=data[i];
                    var row_class =[];
                    
                    row_class.push("row"+(i%2));
                    
                    try{
                        if (typeof(eval("get_row_color_"+g.model))=="function"){
                            row_class.push(eval("get_row_color_"+g.model)(i,row));
                        }
                    }catch(eee){}
                    
                    html_row="<tr class='"+row_class.join(" ")+"' title='"+display+"' data='"+key+"' id='id_row_"+i+"'>";
                    
                    if(g.multiple_select!=null){
                        html_row+="<td class='class_select_col'><input class='select_row' "+name+" type='checkbox' value='"+key+"'"+"/></td>";
                    }      
                    var flag=0;
                    for(var j=0;j<row.length;j++){
                        if(disable_cols.indexOf(","+fields[j]+",")==-1){
                            flag++;
                            row[j]=(row[j]=="None" ? "" :row[j]);
                            var $row_txt=$("<div>"+row[j]+"</div>");
                            var txt= $row_txt.text();
                            var v_txt=row[j];
                            var column_class="";
                            try{
                                if(typeof(eval("get_column_color_"+g.model))=="function"){
                                    column_class=eval("get_column_color_"+g.model)(j,row);
                                }
                            }catch(eee){}
                            
                            if(flag==1 && g.detail_model && g.detail_model.length!=0 && g.need_plus_sign){
                                var a_image="<a class='child_show' alt='master_detail"+i+"'></a>";
                                html_row+="<td title='"+txt+"' class='Link_blue1 "+column_class+"'>"+a_image+v_txt+"</td>";
                            }else if(flag==1){
                                if(g.obj_edit){
                                    html_row+="<td title='"+txt+"' class='Link_blue1 "+column_class+"'><a class='obj_edit_href' ref='"+key+"' href='javascript:void(0);'>"+v_txt+"</a></td>";
                                }else{
                                    html_row+="<td title='"+txt+"'  class='"+column_class+"'>"+v_txt+"</td>";
                                }
                            }else{
                                html_row+="<td title='"+txt+"'  class='"+column_class+"'>"+v_txt+"</td>";
                            }
                        }
                    }
                    html_row=html_row+"</tr>";
                    rows.push(html_row);
                }
                html_tbody+=rows.join("\n");
                html_tbody="<tbody>"+html_tbody+"</tbody>"
                           +html_tfoot;
                html_tbl="<table class='table' id='"+g.tbl_id+"'>"+html_thead+html_tbody+"</table>";
                $(g.t_div).append(html_tbl);
            },
            get_selected:function() {//取得选中的记录
                var data=g.data;
                var key_index=g.key_index;
                var ret="";
                var keys=[];
                var c=0;
                var indexes=[];//表示所选择的数据的索引列表，如 [0,1]；
                var ss=[];
                var sindex=0;//data_verbose_index
                if(data!="")
                {
                    sindex=g.data_verbose_index;
                }
                for(i=0; i<data.length; i++)
                {
                    var obj=$(self).find("#"+g.tbl_id+" #id_row_"+i+" input.select_row");
                    if(obj.length>0 && obj[0].checked)
                    {
                        indexes.push(i);
                        c++;
                        ret+="&K="+data[i][key_index];
                        keys.push(data[i][key_index]);
                        ss.push(data[i][sindex]);
                    }
                }
                var result={count: c, indexes:indexes,query_string: ret, obj_strings: ss, keys: keys};
                return result;
            },
            render_action_obj:function(k,obj_op,elem){//href会动态的变化,返回一个jquery操作对象
                var html_op="<li id='id_"+k+"' title='"
                    +obj_op.help_text+"' name='"+k+"'>"
                    +"<a href='javascript:void(0)' ref='"+g.base_url+"_op_/"+k+"/' alt='"+k+"'>"
					+"<span class='action_"+k+"'></span>"
                    +obj_op.verbose_name+"</a></li><div class='div_leftBottomLine'></div>";
                var $op=$(html_op);
                var is_select_all=g.is_select_all;
                //添加事件
                $op.find("a").click(function(event){
                   if(event.target.nodeName!="A"){
                        event.target=$(event.target).parent("a");
                   }
                   var selected_objs=g.get_selected();
                   var href="";
                   if(typeof(obj_op.on_click)== "string"){
                        href=obj_op.on_click;
                   }
                   var query_str="?"+(is_select_all?'is_select_all=1':selected_objs.query_string);
                   if(elem){//行级操作
                      query_str="";
                      href+=$(elem).attr("data");
                   } 
                   
                   if(obj_op.for_select && !elem){//跟选择数据是否有关
                       if(selected_objs.count==0){
                           alert(gettext('没有选择要操作的对象')+"!");
                           return false;
                       }
                       if(selected_objs.count>1 && obj_op.only_one){
                           alert(gettext('进行该操作只能选择一个对象')+"!");
                           return false;
                       }
                   }
                   if(obj_op.on_click){
                       if(typeof(obj_op.on_click)=="string"){
                            if(obj_op.for_select){
                               href+=query_str;
                               window.location.href=href;
                               return false;
                            }else{//跟列无关
                                window.location.href=obj_op.on_click;
                                if(g.action_onclick_continue)
                                	return true;
                                else
                                	return false;
                            }
                       }else if(typeof(obj_op.on_click) == "function"){
                           if(obj_op.on_click(self,selected_objs,event,elem)){
                                return true;
                            }else{
                                return false;
                            }
                       }
                   }else{//没有定义
                       var href=$(this).attr("ref")+query_str;
                       window.location.href=href;
                       return true;
                   }
                });
                return $op;
            },                
            render_action_batch_row:function(){//action top 批量操作
                // var a=$.validator.format('<li>{0}</li>',"helloworld")
                //render_actions
                var actions=g.actions;
                var $actions=g.a_div;
                for(var  k in actions){
                    var obj_op=actions[k];
                    $op=g.render_action_obj(k,obj_op);
                    if(g.model_action_container && obj_op.for_model){
                        g.model_action_container.append($op);
                    }else if(g.object_action_container && (obj_op.for_model==false)){
                        g.object_action_container.append($op);
                    }else{
                        $actions.append($op);
                    }
                }
            },
            render_row_operations:function(elem,$form_operation){//返回对当前行的平铺操作和弹出式操作数组
                 /*****最后一列菜单开始****/
                    var $show_direct=$("<ul class='ul_row_menu'></ul>");
                    var $show_pop=$("<div class='pop_menuBox'></div>");
                    var $tmp="";
                    var is_direct_empty=true;
                    var is_pop_empty=true;
                    for(var i in g.row_operations){
                        //alert("i"+i)
                        var op=g.row_operations[i];
                        if(typeof(op) == "string"){//直接取操作中的对象
                            //var key=$(this).attr("data");
                           // var single_row_obj={count:1,indexes:[i],query_string:"&"+key,keys:[key],obj_strings:[$(this).attr("display")]};
                            //alert("op"+op)
                           //alert("gg"+ g.actions[op])
                            if(g.actions[op]){
                                $tmp=g.render_action_obj(op,g.actions[op],elem);//对单行的操作
                                $show_direct.append($tmp);
                                is_direct_empty=false;
                            }
                        }else if(typeof(op) == "object"){
                            if(op.length==undefined){
                                is_direct_empty=false;
                                for(var k in op){
                                  $tmp=g.render_action_obj(k,op[k],elem)
                                  $show_direct.append($tmp); 
                                }
                            }else{//弹出菜单
                                var $groups=$('<ul><div class="op_menu_title">'+$(elem).attr('title')+'</div></ul>');
                                for(var j in op){
                                    is_pop_empty=false;
                                    var group_op=op[j];
                                    if(typeof(group_op)=="string"){//字符串
                                        if(g.actions[group_op]){
                                            $tmp=g.render_action_obj(group_op,g.actions[group_op],elem);
                                            $groups.append($tmp);
                                        }
                                    }else{//对象,每个对象表示一个组的操作
                                        for(var j in group_op){
                                           var $ul_group=$("<li><span>"+j+"</span></ul>");
                                            for(var k in group_op[j]){
                                                $tmp=g.render_action_obj(k,group_op[j][k],elem);
                                                $ul_group.append($tmp);
                                            }
                                            $groups.append($ul_group);//放入一个组
                                        }
                                    }
                                }
                                $show_pop.append($groups);
                            }
                        }
                    }
                    if($form_operation){
                        $form_operation.append($show_pop);
                        return false;
                    }else {
                        return {direct_div:$show_direct,pop_div:$show_pop,is_direct_empty:is_direct_empty,is_pop_empty:is_pop_empty};
                    }					
                /*****最后一列菜单结束****/
            },
            render_action_all_row:function(){//action row,关联操作都放在弹出式菜单当中
                $.each($(self).find("#"+g.tbl_id+" tr"),function(index,elem){
                    //list数据行
                    if(index>0){
                        var index_data=index-1;
                        /***单击事件开始**/
                        $(elem).click(function(event){
                        	self.current_row=this;
                            if(self.click_row){
                                self.click_row.removeClass("click_row");
                            }
                            $(this).addClass('click_row');
                            self.click_row=$(this);
                            if(g.on_row_click){ 
                                return g.on_row_click(self,index,g.data[index_data][g.key_index],g.data[index_data],event);
                            }
                            return true;
                        });
                        /***单击事件结束**/
                        
                        /***行级链接单击事件**/
                        $(elem).find("a.obj_edit_href").click(function(event){
                        	self.current_row=this;
                            if(g.on_row_href){
                                return g.on_row_href(self,index,g.data[index_data][g.key_index],g.data[index_data],event);
                                return true;
                            }
                        });
                        /***双击事件开始**/
                        $(elem).dblclick(function(event){
                        	self.current_row=this;
                            if(g.on_dbl_click) return g.on_dbl_click(self,index,g.data[index_data][g.key_index],g.data[index_data],event);
                            return true;
                        });
                        
//                        .mouseover(function(){
//                            self.current_row=this;
//                        });
                        /***双击事件结束**/
                        
                        /***主从表单击事件开始***/
                        var a_master_detail=$("a[alt='master_detail"+index_data+"']",$(elem));
                        if(a_master_detail.length!=0){
                            a_master_detail.click(function(event){
                                if(g.on_child_click) return g.on_child_click(self,index,g.data[index_data][g.key_index],g.data[index_data],a_master_detail,elem,event);
                                return true;
                            });
                        }
                        /***主从表单击事件结束***/
                    }
                    //alert("catch it"+g.row_operations+index)
                    if(g.row_operations.length!=0){
                        if(index==0){
                            $(elem).append("<th>"+gettext("相关操作")+"</th>");
                        }else{
                               //alert("number"+index+elem)
                               var op_objs=g.render_row_operations(elem);
                            //alert(op_objs+op_objs.is_direct_empty+op_objs.is_pop_empty)
                                if(op_objs.is_direct_empty && op_objs.is_pop_empty){
                                        if(index==1){
                                            $(elem).parents("tbody").prev("thead").find("th:last").remove();
                                        }
                                        return;
                                }
                                //一行的后面添加操作列
                               $(elem).append("<td id='id_td_row_menu' class='Link_blue1'></td>");
                               if(!op_objs.is_direct_empty){
                            	   if (typeof(is_row_operations_show)!="undefined"&&!is_row_operations_show(g.data[index_data])){
                            			$(elem).find("#id_td_row_menu").html("");
                					}else{
                						$(elem).find("#id_td_row_menu").prepend(op_objs.direct_div);//直接显示
                            	   }
                               }
                               if(!op_objs.is_pop_empty){
                                   //$(elem).find("#id_td_row_menu").append("<span id='op_menu_span' class='op_menu ui-icon ui-icon-gear displyI'>&nbsp;</span>");
								   $(elem).find("#id_td_row_menu").append("<span id='op_menu_span' class='op_menu ui-icon ui-icon-gear floatL'>&nbsp;</span><div style='width:100px' class='clear'></div>");
                                   $menu_div=$("#obj_tooltip");//页面必须有此对象
                                   $(".op_menu", $(elem)).tooltip({
                                       position: "center left",
                                       opacity: 1.0,
                                       tip: '#obj_tooltip',
                                       onBeforeShow:function(){
                                           var op_objs=g.render_row_operations(elem);
                                           $menu_div.empty();
                                           $menu_div.append(op_objs.pop_div);
                                       }
                                   });
                               }
                        }
                    }
               });
            },
            render_all_selected:function(){//全选的checkbox
                $(self).find("#"+g.tbl_id+" thead th input").click(function(){
                    var ret=true;
                    var checked=$(this).attr("checked");
                    var input_selected=this;
                    if(g.on_all_selected) ret=g.on_all_selected(self,checked,input_selected,g.get_selected());
                    if(ret){
                        var inputs=$(self).find("#"+g.tbl_id+" tbody td input");
						var tbl_tr=$(self).find("#"+g.tbl_id+" tbody tr");
                        //如果设置了展示风格
                        if(g.layout && g.layout!="table"){
                            inputs=$(self).find("#"+g.tbl_id+" div.obj_container input");
                            tbl_tr=$(self).find("#"+g.tbl_id+" div.obj_container");
                        }
                        if($(this).attr("checked")){
                            inputs.attr("checked","true");
							tbl_tr.addClass("select_row_style");
                        }else{
                            inputs.removeAttr("checked");
							tbl_tr.removeClass("select_row_style");
                        }
                    }
                });
            },
            render_selected:function(){//每一行tr前面的checkbox
                var $rows=$(self).find("#"+g.tbl_id+" tbody tr");
                var sel_cbs=$rows.find("td input.select_row");
                $.each(sel_cbs,function(index,elem){
                    $(this).click(function(){
                        var checked=$(this).attr("checked");
                        if(g.multiple_select==false && checked) //不能多选
                        {
                            sel_cbs.attr("checked", false);
                            $(this).attr("checked", true);
                        }
                        var key=g.data[index][g.key_index];
                        var $row_data=$rows.eq(index);
                        if(checked){
                            $row_data.addClass("select_row_style");
                        }else{
                            $row_data.removeClass("select_row_style");
                        }
                        if(g.on_selected) return g.on_selected(self, checked, index, key, $row_data);
                        return true;
                    });
                });
            },
            render_pages:function(){//翻页
                var $pages=g.p_div;
                if(g.record_count!=0){
                    var page_count=g.page_count;
                    var page_num=g.current_page;
                    var record_count=g.record_count;
                    var first_page=1;
                    var pre_page=page_num-1==0 ?1:page_num-1;
                    var next_page=(page_num+1== page_count+1)?page_count:page_num+1;
                    var last_page=page_count;
                    
                    var str_pages=""
                                  +"<div class='page_info'>"
                                        +gettext("共")+" <span class='color_orange'>"+record_count+"</span> "+gettext("记录")+"/<span class='color_orange'>"+page_count+"</span> "+gettext("页")
                                  +"</div>"
                                  +"<div class='page_nav_go'><div class='page_nav'>"
                                        +"<a class='first_page' href='?p="+first_page+"' alt='"+first_page+"' title='"+gettext('首页')+"'></a> "
                                        +"<a class='pre_page' href='?p="+pre_page+"' alt='"+pre_page+"' title='"+gettext('前一页')+"'></a> "
                                        +"<a class='next_page' href='?p="+next_page+"' alt='"+next_page+"' title='"+gettext('后一页')+"'></a> "
                                        +"<a class='last_page' href='?p="+last_page+"' alt='"+last_page+"' title='"+gettext('最后一页')+"'></a>"
                                  +"</div>"
                                  +"<div class='page_go'>"
                                        +"<input type='text' value='"+page_num+"' id='id_page_num_input' class='page_num_input'>"
                                        +"<a id='go_page' class='go_page' href='javascript:void(0)' title='go'></a>"
                                  +"</div></div>"
                    $pages.append(str_pages);
                    $pages.find("#id_page_num_input").keypress(function(e){//回车事件
                        if(window.event){ // IE
                            keynum = e.keyCode;
                        }
                        else if(e.which){ // Netscape/Firefox/Opera
                            keynum = e.which;
                        }
                        if(13==keynum){
                            $("#go_page", $pages).trigger("click");
                        }
                    });
                    $pages.find(".page_nav a").click(function(){//翻页事件
                        if(g.on_pager)
                           return g.on_pager(self,$(this).attr("alt"));
                    });
                    $pages.find(".page_go #go_page").click(function(){//翻页事件
                        var p_num=$pages.find("#id_page_num_input").val();
                        if(g.on_pager)
                            if(g.on_pager(self,p_num))
                                window.location.href="?p="+p_num;
                        return false;
                    });
                }else{
                    if(g.show_pager){
                        $pages.append("<div class='page_info'>"
                                            +gettext("共")+" <span class='color_orange'>0</span> "+gettext("记录")+"/<span class='color_orange'> 0 </span> "+gettext("页")
                                      +"</div>"
                                    );
                    }
                    else
                    {
                        $pages.html("").hide();
                    }
                }
            },
            set_opt:function(opt){//设置属性
                if(opt){
                    $.extend(self.g,opt);
                }
            },
            reload_data:function(){//重新加载
                //self.g.a_div.empty();
                self.g.p_div.empty();
                self.g.t_div.empty();
//                if(self.g.model_action_container){
//                    self.g.model_action_container.empty();
//                }
//                if(self.g.object_action_container){
//                   self.g.object_action_container.empty();
//                }
                self.g.init_data();
                self.g.render_tbl();
                self.g.render_pages();
                self.g.render_selected();
                self.g.render_all_selected();
                //self.g.render_action_batch_row();
                self.g.render_action_all_row();
				if(g.scrollable && g.layout=="table" && g.scroll_table!=false){
                  g.t_div.find("table").tbl_scrollable({height:g.scrollable.height});
                }else if (g.layout=="table" && g.scroll_table!=false){
                  g.t_div.find("table").tbl_scrollable();
                }else if(g.scroll_table == false && g.layout=="table"){
                  g.t_div.addClass("table_t");
                }
                if(g.after_create){
                    g.after_create(self);
                }
                g.switch_layout();
                if(g.sort_data){
                    g.sort_data();
                }
            },
            switch_layout:function(){
                            if(g.grid_div.find("#id_show_style")){
                                g.grid_div.find("#id_show_style").remove();
                            }
                            var $show_style=$("<div id='id_show_style'  class='div_id_middiv div_show_style floatR'><ul></ul></div>");
                            if(g.layout_types && g.layout_types.length!=0){
                                for(var j in g.layout_types){
                                    var chk="";
                                    if(g.layout_types[j]==g.layout){
                                        chk='_focus';
                                    }
                                    //$show_style.append('&nbsp;<input type="radio" '+chk+' value="'+g.layout_types[j]+'" name="rdo_style">'+gettext(g.layout_types[j]));
            						$show_style.find('ul').append('<li cc="'+g.layout_types[j]+'" class="show_style_'+g.layout_types[j]+chk+'" title="'+gettext(g.layout_types[j])+'"></li>');
                                }
                            }
                            $("li",$show_style).click(function(){
                                g.layout=$(this).attr('cc');
                                g.reload_data();
                            });
                            g.p_div.after($show_style);
                            if(g.layout=="photo"){
                                //整个列表框
                                var $tbl_list=g.t_div.find("#"+g.tbl_id);
                                var $tbl_list_elems=$tbl_list.contents();
                                var $tbl_div=$("<div class='select_all_photos'></div>");
                                $tbl_div
                                .append($tbl_list_elems)
                                .attr("id",g.tbl_id);
                                $tbl_list.replaceWith($tbl_div);
                                g.t_div.append($tbl_div);
                                
                                //修改thead转化为div
                                var $thead=g.t_div.find("#"+g.tbl_id+" thead:first");
                                var $select_all_input=$thead.find("tr th input:first");
                                var $select_all_div=$("<div class='div_selectAll'>"+gettext("选择全部")+"</div>");
                                if(g.multiple_select==null){
                                    $select_all_div.html("");
                                }
                                $select_all_div.prepend($select_all_input);
                                $thead.replaceWith($select_all_div);
                                
                                //修改tbody转换为div
                                var $tbody=g.t_div.find("#"+g.tbl_id+" tbody");
                                var $trs=$tbody.find("tr");
                                var $list_div=$("<div class='objs_container'></div>");
                                $list_div.append("<div class='clear'></div>");
                                $list_div.prepend($trs);
                                $tbody.replaceWith($list_div);
                                
                                //修改tr转换为div
                                $.each($trs,function(ii,ee){
                                    var $elems=$(this).find("td");
                                    var $elem_div=$("<div class='obj_container'></div>");
                                    //图片
                                    var src="/media/img/model/"+g.model+$(this).attr("data");
                                    var src_tran="";
            
                                    if(g.photo_path){
                                        if(g.photo_path.indexOf(".jpg")!=-1){
                                            if(g.photo_path.indexOf(".jpg").indexOf("/")!=0){
                                                src=g.photo_path;
                                            }else{
                                                src="/media/img/model/"+g.photo_path;
                                            }
                                        }else{
                                            if(g.fields[g.photo_path]){
                                                var photo_field_value=g.data[ii][g.fields[g.photo_path]];
                                                if(photo_field_value!="None" && photo_field_value.length!=0){
                                                    if (photo_field_value.indexOf("/file/")==-1)
                                                    {
                                                        src="/file/"+photo_field_value;
                                                    }
                                                    else
                                                    {
                                                        src=photo_field_value;
                                                    }
                                                }
                                            } 
                                       
                                            if(g.fields[g.photo_path_tran]){
                                                var photo_field_value=g.data[ii][g.fields[g.photo_path_tran]];
                                                if(photo_field_value!="None" && photo_field_value.length!=0){
                                                    if (photo_field_value.indexOf("/file/")==-1)
                                                    {
                                                        src_tran="/file/"+photo_field_value;
                                                    }
                                                    else
                                                    {
                                                        src_tran=photo_field_value;
                                                    }
                                                }
                                            } 
                                        }
                                    }
                                                            
                                    if(src_tran == ""){
                                        var $img_div = $("<div class='obj_photo'><span><img onerror=\"this.src='/media/images/userImage_default.gif'\" class='list_img' width='75px' height='90px' src='" + src + "'/></span></div>");
                                    }else{
                                        var $img_div = $("<div class='obj_photo'><a href='javascript:void(0)' class='obj_photo_change'><img onerror=\"this.src='/media/images/userImage_default.gif'\" class='list_img' width='75px' height='90px' src='" + src_tran + "'/></a></div><div class='obj_photo'><a href='javascript:void(0)' class='obj_photo_change'><img onerror=\"this.src='/media/images/userImage_default.gif'\" class='list_img' width='75px' height='90px' src='" + src + "'/></a></div>");                            
                                        //var $img_div = $("<div class='obj_photo'><span><a href='javascript:voic(0)' class='hoverToChangImg'><img onerror=\"this.src='/media/images/userImage_default.gif'\" class='list_img' width='75px' height='90px' src='" + src_tran + "'/></a></span></div><div class='obj_photo'><span><a href='javascript:voic(0)' class='hoverToChangImg'><img onerror=\"this.src='/media/images/userImage_default.gif'\" class='list_img' width='75px' height='90px' src='" + src + "'/></a></span></div>");
            						}
              
                                    var $href_div=$("<div class='obj_title Link_blue1'></div>");
                                    $href_div.prepend($elems.eq(0).contents());
                                    $href_div.append($elems.eq(1).contents());
                                    //$href_div.append($(this).attr("title"));
                                    $elem_div
                                    .prepend($href_div)
                                    .prepend($img_div)                        
                                    .attr("id",$(this).attr("id"))
                                    .addClass("tran_container");
                                    $(this).replaceWith($elem_div);
                                    $img_div.tooltip({
                                            position:"bottom center",
                                            opacity: 1.0,
                                            tip: '#obj_tooltip',
                                            onBeforeShow:function(){
                                                var row_data=g.data[ii];
                                                var header=g.heads;
                                                var disable_cols=","+g.disable_cols.toString()+",";//不显示的列
                                                var html_list=[];
                                                for(var i in row_data){
                                                    if(i==0 || i==row_data.length-1 || disable_cols.indexOf(","+g.fields[i]+",")!=-1){
                                                        continue;
                                                    }
                                                    if(row_data[i]=="None"){
                                                        row_data[i]="";
                                                    }
                                                    html_list[i]="<li><span class='details_header nowrap'>"+header[i]+":</span><span class='details_content wrapA'>"+row_data[i]+"</span></li>";
                                                }
                                                html_list="<ul class='list_obj_tooltip'>"+html_list.join("")+"</ul>";
                                                $("#obj_tooltip").html(html_list);
                                            }
                                    });
                                });
                            }
                        }
                    }
            
        //组织整个grid
        $.extend(g,opt);//替换默认属性
        self.g=g;
		g.grid_div.append(g.a_div);
		g.grid_div.append(g.p_div);
		g.grid_div.append(g.t_div);
		//g.grid_div.append(g.r_div);
		$(this).append(g.grid_div);                             
        g.init_data();
        g.render_tbl();
        g.render_pages();
        g.render_selected();
        g.render_all_selected();
        g.render_action_batch_row();
        g.render_action_all_row();
		if(g.scrollable && g.layout=="table" && g.scroll_table!=false){
		  g.t_div.find("table").tbl_scrollable({height:g.scrollable.height});
		}else if (g.layout=="table" && g.scroll_table!=false){
		  g.t_div.find("table").tbl_scrollable();
		}else{
          g.t_div.addClass("table_t");
        }
        if(g.after_create){
            g.after_create(self);
        }
        g.switch_layout();
        if(g.sort_data){
            g.sort_data();
        }
    };
 /**************与模型无关的datalist结束*************/ 
})(jQuery)
function encodeTxt(strTmp)
{
    if (strTmp==null)
        return "";
    return strTmp.toString().replace(/</g,"&lt;").replace(/>/g,"&gt;")
}

