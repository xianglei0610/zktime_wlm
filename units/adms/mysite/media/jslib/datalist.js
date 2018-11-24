(function($){
 /*******基于模型的datalist开始,正对前面代码的一个应用实例********/
    $.fn.set_opt=function(opt){//设置配置参数
        $.extend(this.get(0).g,opt);
    }
    //query ["p=1","q=2"]
    $.fn.reload_data=function(query){
        this.get(0).g.load_data(query);
    }
    /*该函数首先是用传进去的参数覆盖默认的参数，
        再获取该模型的数据信息，
        而后再应用传进去的参数设置*/
    $.fn.model_grid=function(opt){
        var self=this.get(0);
        
        var g ={
            async:true,
            show_related_op:false,//编辑操作时，是否显示相关联的操作
            first_load_data:true,//第一次是否加载数据
            detail_opt:true,//对从表的配置信息，如果是false表示不使用，true表示使用默认，如果为对象就表示使用此配置
            actions:{},
            do_action_masker_div:[],//操作所需要覆盖的div
            do_action_template:null,//响应操作时使用的模板
            dbapp_url:null, 
            key_field:"",
            model_url:null,                      //根目录地址
            model: null,                  //数据模型名称 att/shift
            base_query: [],               //基础查询条件，该数据列表内进行的每次查询都附件上该条件
            init_query: [],               //初始查询条件，该数据列表第一次加载数据时的查询条件 
            record_per_page: 20,                 //每页记录数
            max_no_page: 50,                 //记录数少于该数据时，不分页显示
            detail_model: [],     //作为主从关系的子表 ["att/shift_detail"]
            detail_model_container: null,        //一个jQuery对象，用于放置子对象模型的操作 $bottom_div
            need_plus_sign: true,//存在主从关系的两个表，是否需要在主表上显示加号，主要用于不同界面上的不同需求，默认为需要
            children_models:[],     //所有的子表,以该模型为外键的表
            related_model: [],  //关联对象表["att/user_of_run_detail"],外键
            fields_show: [],          //显示那些字段[](默认是显示所有 )
            sort_fields: [],         //排序的字段["-id","Name"]
            model_actions: true,         //模型操作true表示全部显示(默认)，false表示全部不显示，{op1:{},op2:{}}表示显示这些操作
            object_actions: true,            //对象操作true表示全部显示(默认)，false表示全部不显示，{op1:{},op2:{}}表示显示这些操作
            row_operations: true,               //对象操作true表示全部显示(默认)，false表示全部不显示，对象表示操作["New","Delete",["Leave",...]]
            obj_edit:true,
            show_pager: true,                    //是否显示分页器
            show_head: true,                     //是否显示表头
            addition_actions: {},    //附加的操作{OP1:{},OP2:{}}
            disabled_actions: [], //不需要的操作   ["New","Delete"]
            model_action_container: null,   //一个jQuery对象，用于放置对模型的操作 $left_div
            model_action_template: null,//对模型的操作的输出模板 <li>{0}</li>
            object_action_container: null,   //一个jQuery对象，用于放置对选择对象的操作 $top_div
            object_action_template: null,//对选择对象的操作的输出模板 <li>{0}</li>
            multiple_select: true,    //是否可以多选 null/false/true
            layout: "table",         //数据列表的显示布局方式(图表方式:photo)
            concat_options:function(){//根据传进来的参数和模型中取得的参数，组织好配置项传给zgrid
                var g=self.g;
                if(!g.first_load_data){
                    g.data=[];
                    g.record_count=0;
                    g.first_load_data=true;
                }
                g.base_url=g.model_url;
                var str_disable=g.disabled_actions.join(",");
                
                /*****column setting start******/
                var disable_cols=[];
                var str_fields_show=","+g.fields_show.join(",")+",";
                if(g.fields_show.length!=0){
                    var index=0;
                    for(var i in g.fields){
                        if(str_fields_show.indexOf(","+g.fields[i]+",")==-1){
                            disable_cols[index]=g.fields[i];
                            index++;
                        }
                    }
                }
                if(g.disable_cols){
                    g.disable_cols=g.disable_cols.concat(disable_cols);
                }else{
                    g.disable_cols=disable_cols;
                }
                g.disable_cols=g.disable_cols.concat(["id","data_verbose_column"]);
                /*******column setting end********/
                
                /********for actions start******/
                var actions_all={};
                if(typeof(g.model_actions)=="object"){
                    $.extend(actions_all,g.model_actions);
                }
                if(typeof(g.object_actions)=="object"){
                    $.extend(actions_all,g.object_actions);
                }
                //g.model_actions和g.object_actions不是对象
                for(var a in g.actions){
                    /****给操作添加默认事件开始****/
                    g.actions[a].on_click=function(grid,selected_objs,event,elem){
                        var href=$(event.target).attr("ref");
                        var op_name=$(event.target).attr("alt");
                        var op=g.actions[op_name];
                        
                        var f= function(){
                            var $show_op= $("#id_edit_form #objs_for_op");
                            if(op.for_model){
                                if(op_name=="_clear"){
                                   $show_op.prepend(gettext("是否")+op.verbose_name+"?");
                                }
                            }
                            else{
                                if(grid.g.is_select_all){
                                    $show_op.prepend($.validator.format(gettext("选择所有 {0}(s)"), grid.g.title))
                                }else if(!elem){
                                    $show_op.prepend($.validator.format(gettext("选择 {0}(s): "),grid.g.title)+selected_objs.obj_strings.join("; "));
                                }else{
                                    $show_op.prepend($.validator.format(gettext("选择 {0}(s): "),grid.g.title)+$(elem).attr("title"));
                                }
                            }
                            if($.trim($show_op.text())==""){
                                $show_op.remove();
                            }
                            else{
                                $show_op.addClass("objs_for_op");
                                $show_op.parents("#pre_addition_fields").css("height",60);		
                            }
                            //用来执行操作时的回调函数，比如为人员添加权限组时--darcy20110330
                            if(typeof(after_object_action)!="undefined"){
                                after_object_action();
                            }
                        }
                        if(elem){
                            href+="?K="+$(elem).attr("data");
                            if (op.add_query){
                                href+="&"+op.add_query.join("&");
                            }
                            $.zk._processEdit(href, grid, undefined, event,f);
                        }else{
                            href+="?"+selected_objs.query_string;
                            if (op.add_query){
                                href+="&"+op.add_query.join("&");
                            }
                            $.zk._processEdit(href, grid, undefined, event,f);
                        }
                        return false;
                    };
                    if(a=="_add"){
                       g.actions[a].on_click=function(grid,event){
                           var url=g.model_url+"_new_/";
                           //if (gOptions.additionFilter)
                           url += "?_lock=1";
                           //+gOptions.additionFilter.replace("__id=", "=");
                           $.zk._processNewModel(url, grid, event);
                           return false;
                       }
                   }
                   /****给操作添加默认事件结束****/
                
                    if(g.actions[a].for_model && (g.model_actions == true) && (str_disable.indexOf(a)==-1)){
                        actions_all[a]=g.actions[a];
                    }else if((g.actions[a].for_model == false) && (g.object_actions == true) && (str_disable.indexOf(a)==-1) ){
                        g.actions[a].for_select=true;
                        actions_all[a]=g.actions[a];
                    }
                }
                
                $.extend(actions_all,g.addition_actions);//合并操作
                g.actions=actions_all;
                /*****for actions end*****/
                
                
                /********pager start**/
                if(!g.show_pager){
                    g.record_count=0;
                }else{
                    g.on_pager=function(grid,p){
                        grid.g.init_query=$.zk.concat_query(grid.g.init_query,["p="+p]);
                        grid.g.load_data();
                        return false;
                    };
                }
                /*******pager end*****/
                
                
                /******edit start*****/
                if(g.obj_edit){
                   /* g.on_dbl_click=function(grid,index,key,row_data,e){
                        var Href=grid.g.model_url+key+"/";
                        $.zk._processEdit(Href, grid, undefined, e);
                        return false;
                    };*/
                    g.on_row_href=function(grid,index,key,row_data,e){
                        var Href=grid.g.model_url+key+"/";
                        $.zk._processEdit(Href, grid, undefined, e);
                        return false;
                    };
                }
                /*********edit end********/
                
                
                /***row operations****/
                   if(g.row_operations == true){
                       g.row_operations=g.row_actions;
                   }else if(g.row_operations == false){
                        g.row_operations=[];
                   }else{
                        var get_row_op=function(str_op){//判断g.row_actions里面是否有str_op操作
                            for(var i in g.row_actions){
                                var flag=true;
                                var tmp_op=g.row_actions[i];
                                var k="";
                                if(typeof(tmp_op)=="string"){
                                        k=tmp_op;
                                }else if(typeof(tmp_op)=="object"){
                                    if(tmp_op.length==undefined){//obj
                                        for(var j in tmp_op){
                                            k=j;
                                        }
                                    }else{//Array
                                        flag=false;
                                        for(var p in tmp_op){
                                            for(var j in tmp_op[p]){
                                                var group_title=j;
                                                var group_data=tmp_op[p][j];
                                                for(var f in group_data){
                                                    if(f==str_op){
                                                        var ret_op={};
                                                        ret_op[f]=group_data[f];
                                                        return ret_op;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                } 
                                if(flag && (k==str_op)){
                                    return tmp_op;
                                }
                            }
                            return null;
                        }
                        for(var j=0;j<g.row_operations.length;j++){
                            if(typeof(g.row_operations[j])=="string"){
                                var op=get_row_op(g.row_operations[j]);
                                if(op){
                                    g.row_operations[j]=op;
                                }
                            }else if(typeof(g.row_operations[j])=="object"){
                                if(g.row_operations[j].length!=undefined){
                                    for(var i in g.row_operations[j]){
                                        var group_obj=g.row_operations[j][i];
                                        if(typeof(group_obj)=="string"){
                                            var op=get_row_op(group_obj);
                                            if(op){
                                                g.row_operations[j][i]=op;
                                            }
                                        }else{
                                            for(var f in group_obj){
                                                //f group title
                                                var group={};
                                                var data={};
                                                group[f]=data;
                                                for(var p in group_obj[f]){
                                                    var op=get_row_op(group_obj[f][p]);
                                                    if(op){
                                                        $.extend(data,op);
                                                    }
                                                }
                                                g.row_operations[j][i]=group; 
                                            }
                                        }
                                    }
                                }
                            }
                       }
                   } 
                /****row operations end***/
                
                /*********master/detail start***/
                if(g.detail_model.length!=0){
                    g.on_child_click=function(grid,index,key,row_data,$child,elem,e){
                        if(!g.dbapp_url){
                            return;
                        }
                        var href=grid.g.dbapp_url+g.detail_model[0]+"/";
                        var relation_key=g.detail_model[0].split("/").join(":").toLowerCase();
                        var child_fk_field=grid.g.children_models[relation_key][3];
                        var master_id=grid.g.key_field;
                        var opt={
                            dbapp_url:grid.g.dbapp_url,
                            model_actions:false,
                            object_actions:false,
                            row_operations:false,
                            obj_edit:false,
                            model_url:href,
                            scrollable:false,
                            multiple_select:null,
                            base_query:[child_fk_field+"__"+master_id+"="+key]
                        }
                        if(typeof(g.detail_opt)=="object"){
                            g.detail_opt.base_query=opt.base_query;
                            opt=g.detail_opt;
                        }else if(g.detail_opt==false){
                            return;
                        }
                        var id_child="child_"+grid.g.detail_model[0].split("/").join("_");
                        var $child_div=$("tr.child_row:has(td div#"+id_child+")");
                        
                        if(grid.g.detail_model_container){//放入指定位置
                            grid.g.detail_model_container.empty();
                            grid.g.detail_model_container.model_grid(opt);
                        }else{
                            if($child.hasClass("child_show")){//默认放入该行的下边
                                var column_count=$(elem).find("td").length;
                                var $container=$("<tr class='child_row'><td class='childcontent' colspan="+column_count+"><div id='"+id_child+"'></div></td></tr>");
                                if($child_div.length!=0){
                                    $child_div.remove();
                                }
                                index--;
                                $("#id_row_"+index).after($container);
                                $container.find("#"+id_child).model_grid(opt);
                            }
                        }
                        /**交换图标开始**/
                        if($child.hasClass("child_show")){
                            $child.attr("class","child_hide");
                            if(grid.g.child_click && $child.attr("alt")!=grid.g.child_click.attr("alt")){
                                grid.g.child_click.attr("class","child_show");
                            }
                        }else{
                            $child.attr("class","child_show");
                            $child_div.remove();
                        } 
                        grid.g.child_click=$child;//标记上次点击的链接
                        /**交换图标结束**/
                        return false;
                    };
                }
                /*********master/detail end*****/
                
            },
            get_model_json_data:function(is_reload){
                var g=self.g;
                g.init_query=$.zk.concat_query(g.init_query,["stamp="+new Date().getTime()]);
                var list_sort=[];
                for(var i in g.sort_fields){
                    list_sort[i]=g.sort_fields[i].split(".").join("__");
                }
                
                var sort_str="o="+list_sort.join(",");
                if(g.store_sort_fields){
                    var temp=[];
                    var count=0;
                    for(var kk in g.store_sort_fields){
                       if(g.store_sort_fields[kk]!=""){
                         temp[count++]=g.store_sort_fields[kk];
                       }
                    }
                    sort_str="o="+temp.join(",");
                }
                if(sort_str!="o="){
                    g.init_query=$.zk.concat_query(g.init_query,[sort_str]);
                }
                if(g.max_no_page){
                    g.base_query=$.zk.concat_query(g.base_query,["mnp="+g.max_no_page]);
                }
                if(g.record_per_page){
                    g.base_query=$.zk.concat_query(g.base_query,["l="+g.record_per_page]);
                }
                var add_split=g.model_url.split("?");
                if(add_split.length>1){
                    g.model_url=add_split[0];
                    g.init_query=$.zk.concat_query(g.init_query,add_split[1].split("&"));
                }
                var post_url=g.model_url+"?"+g.init_query.join("&")+"&"+g.base_query.join("&");
                var post_data=[];
                var async=g.async;
				var render_grid=function (msg) {
                        if(msg.errorCode==undefined)
                        {   
                            g=self.g;
                            var hide_fields=g.disable_cols;
                            var layout_types=g.layout_types;
                            for(var k in msg){
                                if(k=="options"){
                                    $.extend(g,msg.options);
                                }else{
                                    g[k]=msg[k];
                                }
                            }
                            if(g.prev_opt){
                               $.extend(g,g.prev_opt);
                               delete g["prev_opt"];
                            }
                            if(hide_fields){
                                g.disable_cols=hide_fields;
                            }
                            if(layout_types){
                                g.layout_types=layout_types;
                            }
                            if(!g.actions._change){
                                g.obj_edit=false;
                            }
                            g.data_verbose_column="data_verbose_column";
                            //应用到zgrid
                            if(!is_reload){
                                g.create_related_objs();
                                g.concat_options();
                                $(self).grid(g);
                                if(g.init_after_get_jdata){
                                    g.init_after_get_jdata();
                                }
                            }else{
                                g.concat_options();
                                g.set_opt(g);
                                g.reload_data();
                                if(g.reload_after_get_jdata){
                                    g.reload_after_get_jdata();
                                }
                            }
                            
                            if(typeof(g.ajax_callback)=="function"){
                                g.ajax_callback(g);
                            }
                            
                        }
                        
                    };
				if(g.cached_data && !g.data)
				{
					render_grid(g.cached_data);
					delete g.cached_data;
				}
	            else 
				$.ajax({
                    url:encodeURI(post_url),
                    type:"POST",
                    async:async,
                    dataType:"json",
                    cache:false,
                    timeout:300000,//5分钟超时
                    data:post_data,
                    success: render_grid,
                    error:function (xmlreq, textStatus, errorThrown) {//XMLHttpRequest
                        //alert(gettext("服务器处理数据失败，请重试！"));//服务器加载数据失败,请重试!
                        //alert("服务器加载数据失败,error_msg:"+errorThrown+",textStatus:"+textStatus);
                    }
                });
            },
            create_related_objs:function(){
                var g=self.g;
                g.row_actions=[];
                var related_actions=[];
                var add_group_label=gettext("新建相关数据");
                var browse_group_label=gettext("浏览相关数据");
                var group_add={};
                var group_browse={};
                group_add[add_group_label]={};//添加组
                group_browse[browse_group_label]={};//浏览组
                var related_fk=g.relations;

                var children_models=g.children_models;
                var c=false;
                for(var index in children_models)
                {
                    c=true;
                    var tmp_action=new Object();
                    //add
                    var cm=children_models[index];
                    var var_on_click=g.dbapp_url+cm[0]+'/'+cm[1]+'/_new_/?_lock=1&'+cm[3]+'=';
                    var verbose_relate="add_"+cm[1];
                    var on_click=function(param_on_click){
                        return function(grid,selected_objs,event,elem){
                             var href=param_on_click+$(elem).attr("data");
                              window.open (href);
                             //$.zk._processEdit(href, grid, undefined, event);
                             return false;
                        }
                     }
                    tmp_action.help_text=gettext("添加")+cm[2];
                    tmp_action.for_select=true;
                    tmp_action.on_click=on_click(var_on_click);
                    tmp_action.verbose_name=gettext("添加")+" "+cm[2];
                    tmp_action.is_related=true;//需要加id
                    group_add[add_group_label][verbose_relate]=tmp_action;
                    //browse
                    tmp_action=new Object();
                    tmp_action.help_text=gettext("浏览")+cm[2];
                    tmp_action.for_select=true;
                    verbose_relate="browse_"+cm[1];
                    var_on_click=g.dbapp_url+cm[0]+'/'+cm[1]+'/?'+cm[3]+'__'+g.key_field+'=';
                    tmp_action.on_click=on_click(var_on_click);
                    tmp_action.verbose_name=gettext("浏览")+" "+cm[2];
                    tmp_action.is_related=true;
                    group_browse[browse_group_label][verbose_relate]=tmp_action;
                }
                if(g.obj_edit){//默认添加编辑操作
                    var op_edit={
                        op_edit:{
                            verbose_name: gettext("编辑"),
                            help_text:gettext("编辑选定记录"),
                            params:0,
                            for_select:true,
                            confirm:true,
                            on_click:function(grid,selected_objs,event,elem){
                                if(elem){
                                    var href=grid.g.model_url+$(elem).attr("data")+"/"
                                    $.zk._processEdit(href, grid, undefined, event);
                                }
                                return false;
                            }
                        }
                    }
                    g.row_actions[0]=op_edit;
                }
                if(g.actions["_delete"]){//默认添加删除操作
                    g.row_actions[g.row_actions.length]="_delete";
                }
                if(c){
                    related_actions[0]=group_add;
                    related_actions[1]=group_browse;
                    g.row_actions[g.row_actions.length]=related_actions;
                }
                
            },
            load_data:function(query){
                var g=self.g;
                if(query){
                    g.init_query=$.zk.concat_query(g.init_query,query);
                }
                g.get_model_json_data(true);//取得model数据
              //  g.concat_options();
               // g.set_opt(g);
               // g.reload_data();//调用
            },
            sort_data:function(){
                //list头
                var g=self.g;
                var $elem=$(self).find("#id_tbl thead tr:first,#id_tbl tbody tr:first,.dt_hdiv thead tr:first,.dt_bdiv tbody tr:first");
                var sort_fields="";
                if(g.sort_fields){
                    sort_fields=","+g.sort_fields.join(",")+",";
                }
                //加入样式
                $ths=$elem.eq(0).find("th");
                $tds=$elem.eq(1).find("td");
                $.each($ths,function(iii,eee){
                    var f=$(eee).attr("field");
                    if(f){
                        if(sort_fields.indexOf(","+f+",")!=-1 || sort_fields.indexOf(",-"+f+",")!=-1){
                            $(eee).addClass('sort_flat_class');
                            $tds.eq(iii).addClass('sort_flat_class');
                        }
                    }
                });
                //添加事件
                $.each($ths,function(){
//                alert($(".dt_bdiv").height())
                $(".dt_bdiv").css({height:"400px"})
					if($.browser.msie){
						if($(".dt_bdiv").height() >= 260){
								$(".dt_bdiv").css({height:"390px"})
						}else if($(".dt_bdiv").width() < $(".dt_bdiv_tbl").width()){
						$(".dt_bdiv").addClass("sy");
						}
					}
                    if($(this).hasClass("sort_flat_class")){
                        $(this).tooltip({
                          position: ($.browser.msie && parseFloat($.browser.version)<7) ? "bottom center" : "bottom center",
                          opacity: 1.0,
                          tip: '#obj_tooltip',
                          onBeforeShow:function(){
                                if($.browser.msie && parseFloat($.browser.version)<7){
                                    $('#obj_tooltip').addClass("sort_tooltip_class");
                                }
                                var $target=$(this.getTrigger());
                                var field=$target.attr("field");
                                var html="<div id='sort_menu' style='position:absolute;z-index:1000;display:block'><ul>"
                                            +"<li class='sort_D_class'><a s='"+field+"' href='javascript:void(0);'>"+gettext("升序")+"</a></li>"
                                            //+"<li><a s='' href='javascript:void(0);'>"+gettext("取消")+"</a></li>"
                                            +"<li class='sort_A_class'><a s='-"+field+"' href='javascript:void(0);'>"+gettext("降序")+"</a></li>"
                                        +"</ul></div>";
                                var $sort_menu=$(html);
                                $sort_menu.find("li>a").click(function(){
                                       // if(g.store_sort_fields){
                                         //   g.store_sort_fields[field]=$(this).attr("s");
                                        //}else{
                                            g.store_sort_fields ={};
                                            g.store_sort_fields[field]=$(this).attr("s").split(".").join("__");
                                        //}
                                        var async=g.async;
                                        g.async=false;
                                        g.load_data();
                                        g.async=async;
                                       //刷新完之后根据g.store_sort_fields存储的排序重新添加样式
                                       var $$elem=$(self).find("#id_tbl thead tr:first,#id_tbl tbody tr:first,.dt_hdiv thead tr:first,.dt_bdiv tbody tr:first");
                                       var $td_elems=$$elem.eq(1);
                                       $.each($$elem.eq(0).find("th"),function(ii,ee){
                                           var $this=$(this);
                                           for(var kk in g.store_sort_fields){
                                               if($this.attr("field")==kk){
                                                   //if(g.store_sort_fields[kk]=="")
                                                   //{
                                                   //    $this.addClass("sort_flat_class").removeClass("sort_A_class sort_D_class");
                                                   //    $td_elems.find("td").eq(ii).addClass("sort_flat_class").removeClass("sort_A_class sort_D_class");
                                                   //}else 
                                                   if(g.store_sort_fields[kk].substr(0,1)=="-"){
                                                       $this.addClass("sort_A_class").removeClass("sort_D_class sort_flat_class");
                                                       $td_elems.find("td").eq(ii).addClass("sort_A_class").removeClass("sort_D_class sort_flat_class");
                                                   }else{
                                                       $this.addClass("sort_D_class").removeClass("sort_A_class sort_flat_class");
                                                       $td_elems.find("td").eq(ii).addClass("sort_D_class").removeClass("sort_A_class sort_flat_class");
                                                   }
                                               }
                                           }
                                       });
                                });
                                $target.find("#sort_menu").remove();
                                $("#obj_tooltip").empty().append($sort_menu);
                          }
                        });
                    }
              });
            }
         };
        //取得要配置数据
        $.extend(g,opt);
        self.g=g;
        g.get_model_json_data();
        //g.create_related_objs();
        //g.concat_options();
        // $(self).grid(g);
    };
 /*******基于模型的datalist结束********/
 
})(jQuery);

