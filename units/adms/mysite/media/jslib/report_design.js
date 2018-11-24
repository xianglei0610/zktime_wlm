/**
--组名列:
保存到数据中的g_report数据结构:
{
    "sel_datasource":"iclock__Template",
    //更改列的位置的时候同时修改此数组的顺序
    fields:["FingerID","UserID.EName","UserID.DeptID.name","公式字段","组名字段"],
    fields_attributes:{
        "FingerID":{
            "display":"指纹",
            "adv_search":{
                "in":[],
                "exact":[],
                "gt":"vv",
                "lt":"vv",
                "exclude":"",
                "contains":[],
            },
            "search":{"contains":"vvv"},
            "sort":"-",//|,-,+
            "is_group_field":"true",
            "is_expressions_field":"true",
            "expression":"FingerID",//"SUM(FingerID)",2*FingerID+30,
        },
        "UserID.EName":{"display":"员工名称","adv_search":{},"search":{},"sort":"|","is_group_field":"false",},
        UserID.DeptID.name":{...}
    },
    "record_per_page":15,//每页行数
    "report_title":"",//标题
    "report_header":{"left":"","center":"","right":""},//页眉
    "report_footer":{"left":"","center":"","right":""},//页脚
    "report_type":"id"//报表类型
}

--操作所要用到的常用数据
g_data={
    field_data:{},//所有字段的信息
    "UserID__name":{},//某个字段的信息,只用一级，便于访问
    "f2":{},
    "f3":{}
}
**/


/**
@surl 网站根地址
@data_container 数据源选择容器
@g_report 报表设计存储的数据结构
@function 得到所有报表数据源，以树状的形式展示
**/
function get_all_datasources(surl,data_container,g_report){
    var stamp=new Date().getTime();
    $.ajax({
        type:"GET",
        url: "/"+surl+"report/datasources/?stamp="+stamp,
        dataType: "json",
        async:false,
        success: function(data){
            var list_html=[];
            list_html.push(
                "<div class='filetree' style='overflow: auto; height: 390px;'>"
                +"<li><p style='*float:left;'>"+gettext("全部数据源")
                +"</p><ul class='treeview'>"
            );
            for(var k in data){
                var app=data[k];
                list_html.push("<li><p >"+app["verbose_name"]+"</p><ul>");
                for(var kk in app["models"]){
                    list_html.push("<li><p class='t' value='"+app["models"][kk][2]+"__"+app["models"][kk][1]+"'>"+app["models"][kk][0]+"</p></li>");
                }
                list_html.push("</ul></li>");
            }
            list_html.push("</ul></li></div>");
            data_container.find("#show_sources").append(list_html.join(""));
            data_container.treeview().show();
            var sources=data_container.find("p.t");
            var select_source=sources.eq(0);//默认数据源
            if(g_report["sel_datasource"]){
                select_source=data_container.find("p.t[value='"+g_report["sel_datasource"]+"']");
            }else{
                g_report["sel_datasource"]=select_source.attr("value");
            }
            sources.click(function(){
                if(select_source){
                    select_source.removeClass("s").addClass("t");
                }
                select_source=$(this);
                select_source.removeClass("t").addClass("s");
                var sv=select_source.attr("value");
                if(g_report["sel_datasource"]!=sv){
                    g_report["sel_datasource"]=sv;
                    g_report["fields"]=[];
                    g_report["fields_attributes"]={};
                }
            });
            select_source.addClass("s");
            //初始化设计数据
            //get_sources_attributes(surl,$("#id_step_two"),g_report);
        }
    });
}

/**
@data 数据源列的树形展示
@parent_field_list 字段上下级列表
@is_checkbox 是否是复选框,默认不是单选框
@function 返回data的数据列展示的树形html**/
function render_columns_tree(data,parent_field_list,is_checkbox){
    var checked_class="";
    if(is_checkbox){
        checked_class=" class='t'";
    }else{
        checked_class=" class='r'";
    }
    if(!parent_field_list){
        parent_field_list=[];
    }
    var html_data=[];
    
    html_data.push(
        "<li><p style='*float:left;' "+checked_class+">"+data["m_verbose_name"]+"</p><ul>"
    );
    for(var k in data["fields"]){
        var field=data["fields"][k];
        if(field["field_type"]=="ForeignKey" && field["fields"]){//外键
            var new_parent=[].concat(parent_field_list);
            new_parent.push(k);
            html_data.push(render_columns_tree(field,new_parent,is_checkbox));
        }else{
            var value=k;
            if(parent_field_list.length!=0){
                value=parent_field_list.join("__")+"__"+k;
            }
            g_data[value]=field;
            html_data.push("<li><p class='t' type='"+field["field_type"]+"' value='"+value+"'>"+field["f_verbose_name"]+"</p></li>");
        }
    }
    html_data.push("</ul></li>");
    return html_data.join("");
}

/**
@param data 数据
@id 容器id
@cls 容器样式类
@jdom 容器的父容器
**/
function render_tree_container(data,id,cls,jdom){
    var html_data=[];
    html_data.push("<div id='"+id+"' class='"+cls+"' style='overflow: auto; height: 380px;'>");
    html_data.push(render_columns_tree(data,[],true));
    html_data.push("</div>");
    jdom.append(html_data.join(""));
}



/**
@function 渲染报表头div
**/
function render_report_propertys(jdom,g_report){
    var report_property=jdom.find("#id_report_property");
    if(report_property.length==0){
        jdom.append('<div id="id_report_property" class="report_container_other">'
                        +'<div  style="margin-left:0px; margin-top:0px;margin-right: 5px ! important;width:100%;" class="div_box floatL">'
                        +'<h1 style="margin:0px 0px 5px 5px;margin:0px 0px 2px 5px\9;">&nbsp;</h1>'
                        +'<div id="show_sources" style="min-width:450px;height:124px;">'
                        +'</div>'
                    +'</div>'
        );
        var report_propertys=$("#report_propertys").clone();
        report_propertys.show();
        jdom.find("#id_report_property").find("#show_sources").append(report_propertys);
    }else{
        //修改相应的属性
    }
}

/**
@function 渲染所有的列
**/
function render_report_fields(jdom,g_report,obj_design_container){
    var field_property=jdom.find("#id_fields_propery");
    if(field_property.length==0){
        jdom.append('<div id="id_fields_propery" class="report_container_field">'
                        +'<div  style="margin-left:0px; margin-top:0px; margin-right: 5px !important;width:100%;" class="div_box floatL">'
                        +'<h1 style="margin:0px 0px 5px 5px;margin:0px 0px 2px 5px\9;">&nbsp;</h1>'
                        +'<div id="show_sources" style="min-width:575px;height:221px;">'
                        +'</div>'
                    +'</div>'
        );
        //如果是编辑则初始化左边列和容器总的列
        $.each(obj_design_container.find("#show_deptment p.t"),function(index,elem){
            var field_value=$(this).attr("value");
            if(!field_value){
                return;
            }
            for(var i in g_report["fields"]){
                if(field_value==g_report["fields"][i]){
                    $(this).trigger("click");
                }
            }
        });
    }else{
        //修改相应的属性
    }
    
}

/**
@swap_widget_prev 交换对象一
@swap_widget_next 交换对象二
function 交换两个小部件
**/
function change_position(swap_widget_prev,swap_widget_next,g_report){
    var position_one=null;
    var id_one=swap_widget_prev.attr("id");
    var position_two=null;
    var id_two=swap_widget_next.attr("id");
    var swap=null;
    for(var i in g_report.fields){
        if(g_report.fields[i]==id_one){
            position_one=i;
            swap=g_report.fields[i];
        }
        if(g_report.fields[i]==id_two){
            position_two=i;
        }
    }
    g_report.fields[position_one]=g_report.fields[position_two];
    g_report.fields[position_two]=swap;
    swap_widget_prev.before(swap_widget_next);
}


/**
@jdom 放置下拉列表的容器
@menu_title 下拉表的标题
@dict_items 下拉表的每项的点击事件
@function 渲染字段小部件
**/
function render_field_widget(jdom,id,menu_title,dict_items,g_report){
    //字段所有的html页面
    var html_data=[];
    html_data.push("<div id='"+id+"'  class='btn floatL field_widget' style='cursor:default;'>");
    html_data.push("<div  class='floatL go_left cursorP'>◄ </div>");
    
    html_data.push("<div  class='floatL Link_hui field_display'>");
    html_data.push("<span class='floatL nowrap color_blue' style='font-size:14px;'>"+menu_title+" </span><ul class='nav Link_blue2 font12 noUnderl floatL ul_action_more'><li>");
    html_data.push("<a href='javascript:void(0);'>"+gettext("设置")+"▼</a>");
    html_data.push("<ul class='action_more_list'>");
    for(var k in dict_items){
        html_data.push("<li style='width:150px;' id='"+k+"' field_display='"+menu_title+"' field_name='"+id+"'><a href='javascript:void(0);'>"+dict_items[k]["display"]+"</a></li>");
    }
    html_data.push("</ul>");
    html_data.push("</li></ul>");
    html_data.push("</div>");
    
    html_data.push("<div class='floatL go_right cursorP'> ►</div>");
    html_data.push("</div>");
    jdom.append(html_data.join(""));
    
    var obj_widget=jdom.find("#"+id);
    obj_widget.find("ul.nav li").sfHover();
    
    //交换顺序
    obj_widget.find("div.go_left").click(function(){
        var this_obj=$(this);
        var prev_field_widget=this_obj.parent().prev("div.field_widget");
        if(prev_field_widget.length!=0){
            change_position(prev_field_widget,this_obj.parent(),g_report);
        }
    });
    
    obj_widget.find("div.go_right").click(function(){
        var this_obj=$(this);
        var next_field_widget=this_obj.parent().next("div.field_widget");
        if(next_field_widget.length!=0){
            change_position(this_obj.parent(),next_field_widget,g_report);
        }
    });
    
    //设置项添加事件
    for(var k in dict_items){
        obj_widget.find("#"+k).click(dict_items[k]["event"]);
    }
}

/**
@jdom 存储列的dom元素
@g_report 全局结构
@function 检测fields是否增加或者删除，更新相应的界面显示
<div>
    <div class="div_box floatL">
        <h1>字段名称</h1>
        <div><ul><li>
            <a>下拉列表</a>
            <ul>
                <li>功能一</li>
                <li>功能二</li>
                <li>功能三</li>
            </ul>
        </li></ul></div>
    </div>
</div>
**/
function field_div_check(jdom,g_report){
    var dict_items={
        "common_property":{
            "display":gettext("常用属性"),
            "event":function(index,elem){
                alert('ok');
                //常用属性设置,包括显示名称display，排序方式sort，表达式expression
            }
        },
        "adv_search":{
            "display":gettext("添加查询条件"),
            "event":function(index,elem){
                var field_name=$(this).attr("field_name");
                var field=g_data[field_name];
                
                //高级查询的整个html
                var html_dialog=[
                    '<div class="adv_ctn"><form>',
                        '<table style="border-spacing:3px !important;"></tr>',
                            '<td>',
                                '<span>条件选择</span>',
                                '<span id="sel_filter">',
                                '</span>',
                            '</td>',
                            '<td>',
                                '<span>值域</span>',
                                '<span id="write_value"></span>',
                            '</td>',
                            '<td>',
                                '<input type="button" class="btn" style="margin:0px;" id="btn_add" value="'+gettext("添加")+'"/>',
                            '</td></tr></table>',
                        '</div>',
                        '<div class="has_sel_flt">',
                            '<span>'+gettext("已经增加的条件")+'</span>',
                            '<table class="filter_con table">',
                                '<thead>',
                                    '<tr><th>'+gettext("条件")+'</th><th>'+gettext("值")+'</th><th>'+gettext("操作")+'</th></tr>',
                                '</thead>',
                                '<tbody',
                                '</tbody>',
                            '</table>',
                        '</div>',
                        '<table class="flt_o_btn"><tr>',
                            '<td><input type="button" id="btn_ok" class="btn" value="'+gettext("确定")+'" /></td>',
                            '<td><input type="button" id="btn_cancel" class="btn" value="'+gettext("取消")+'" /></td>',
                            '<td><input type="button" id="btn_clear" class="btn" value="'+gettext("清除所有条件")+'" /></td>',
                        '</tr></table><div class="clear"></div>',
                    '</form></div>'
                ];
                
                //每种类型所对应的属性设置,包括它所具有的条件类型，验证方式，
                //以及其实用的widget,如果配置了就用的没有就取其默认的
                var fdict={
                    "DateField":{
                        filter_type:[
                            ["exact","等于"],["exclude","不等于"],["gt","大于"],["lt","小于"],
                            ["gte","大于等于"],["lte","小于等于"]
                        ]
                    },
                    "TimeField":{
                        filter_type:[
                            ["exact","等于"],["exclude","不等于"],["gt","大于"],["lt","小于"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "DateTimeField":{
                        filter_type:[
                            ["exact","等于"],["exclude","不等于"],["gt","大于"],["lt","小于"],
                            ["gte","大于等于"],["lte","小于等于"]
                        ] 
                    },
                    "CharField":{
                        filter_type:[
                           ["exact","等于"],["exclude","不等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                           ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "EmailField":{
                        filter_type:[
                            ["exact","等于"],["exclude","不等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "BooleanField":{
                        filter_type:[
                            ["exact","等于"],["exclude","不等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "FilePathField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "IPAddressField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "TextField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "DecimalField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "BigIntegerField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "FloatField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "IntegerField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    },
                    "SmallIntegerField":{
                        filter_type:[
                            ["exact","等于"],["gt","大于"],["lt","小于"],["in","满足任意一个"],
                            ["gte","大于等于"],["lte","小于等于"],["contains","包含"]
                        ] 
                    }
                };
                
                var obj_adv=$(html_dialog.join(""));
                
                //条件html
                var html_filter=[];
                var field_type_dict=fdict[field["field_type"]];
                html_filter.push("<select id='id_select'>");
                for(var i in field_type_dict["filter_type"]){
                    var tmp_item=field_type_dict["filter_type"][i];
                    html_filter.push("<option value='"+tmp_item[0]+"'>"+tmp_item[1]+"</option>");
                }
                html_filter.push("</select>");
                obj_adv.find("#sel_filter").append(html_filter.join(""));
                
                //值域html
                $.extend(field_type_dict,field);
                var obj_widget=field["widget"];
                obj_adv.find("#write_value").append(obj_widget);
                render_widgets(obj_adv);
                //“添加按钮”事件
                var f_adv_search=g_report.fields_attributes[field_name]["adv_search"];
                var add_condition=function(vf,df,vv,vd){
                    var filter_con=obj_adv.find("table.filter_con tbody");
                    var f_tr=$("<tr><td>"+df+"</td><td id='id_kv' value='"+vf+"__"+vv+"'>"+vd+"</td><td><a href='javascript:void(0)' class='Link_blue1'>"+gettext("删除")+"</a></td><tr></tr>");
                    
                    //给当前条件删除按钮添加事件
                    f_tr.find("a.btn_del_filter").click(function(){
                        var parent_tr=$(this).parent().parent("tr");
                        parent_tr.remove();
                    });
                    //添加一个条件
                    filter_con.append(f_tr);
                }
                
                //如果是编辑必须还原原来的条件现状
                for(var k in f_adv_search){
                    var vf=k;
                    var df=obj_adv.find("#id_select").find("option[value='"+vf+"']").text();
                    for(var i in f_adv_search[k]){
                        vv=f_adv_search[k][i];
                        vd="";
                        var obj_val=obj_adv.find("#id_wg_val");
                        if(obj_val.is("select")){
                            vd=obj_val.find("option[value='"+vv+"']").text();
                        }else{
                            vd=vv;
                        }
                        add_condition(vf,df,vv,vd);
                    }
                }
                obj_adv.find("#btn_add").click(function(){
                    if(!obj_adv.find("form").valid()){
                        return;
                    }
                    var obj_condition=obj_adv.find("#id_select").find("option:selected");
                    var vf=obj_condition.val();
                    var df=obj_condition.text();
                    
                    var obj_val=obj_adv.find("#write_value input");
                    var vv="";
                    var vd="";
                    if(obj_val.is("select")){
                        vv=obj_val.find("option:selected").val();
                        vd=obj_val.find("option:selected").text();
                    }else{
                        vv=vd=obj_val.val();
                    }
                    vv=$.trim(vv);
                    if(vd==""){
                        vd=gettext("空");
                    }
                    var filters=obj_adv.find("table.filter_con tbody tr #id_kv");
                    for(var i=0;i<filters.length;i++){
                        var kv=filters.eq(i).attr("value").split("__");
                        if(kv[0]==vf){
                            if(kv[1]==vv){
                                alert("条件已经添加!");
                                return ;
                            }else if(kv[0]=="exact"){
                                alert("此类条件只允许添加一个");
                                return;
                            }
                            break;
                        }
                    }
                    add_condition(vf,df,vv,vd);
                });
                //取消
                obj_adv.find("#btn_cancel").click(function(){
                    obj_adv.find("#id_close").click();
                });
                //删除全部
                obj_adv.find("#btn_clear").click(function(){
                    obj_adv.find("table.filter_con tbody").empty();
                });
                obj_adv.find("#btn_ok").click(function(){
                    var filters=obj_adv.find("table.filter_con tbody tr #id_kv");
                    var dict_filter={};
                    for(var i=0;i<filters.length;i++){
                        var kv=filters.eq(i).attr("value").split("__");
                        if(dict_filter[kv[0]]){
                            dict_filter[kv[0]].push(kv[1]);
                        }else{
                            dict_filter[kv[0]]=[kv[1]];
                        }
                    }
                    g_report.fields_attributes[field_name]["adv_search"]=dict_filter;
                    obj_adv.find("#id_close").click();
                });
                //弹出框
                obj_adv.dialog({title:field["f_verbose_name"]+gettext("添加高级查询")});
                
            }
        }
    };

    //检测小部件是否需要删除
    var exist_widgets=jdom.find(".field_widget");
    var g_fields=","+g_report.fields.join(",")+",";
    for(var i=0;i<exist_widgets.length;i++){
        var elem=exist_widgets.eq(i);
        if(g_fields.indexOf(","+elem.attr("id")+",")==-1){
            elem.remove();
        }
    }
    
    for(var i in g_report.fields){
        var id=g_report.fields[i];
        if(jdom.find("#"+id).length!=0){
            continue;
        }
         //没有添加小部件
        render_field_widget(jdom,id,g_report.fields_attributes[id]["display"],dict_items,g_report);
    }
    
}


/**
@surl 网站根地址
@obj_design_container 报表设计容器对象
@g_report 报表设置数据结构
@function 根据g_report初始化报表设计器
**/
function get_sources_attributes(surl,obj_design_container,g_report){
    var app_label=g_report["sel_datasource"].split("__")[0];
    var model_name=g_report["sel_datasource"].split("__")[1];
    var sel_cols_container=obj_design_container.find("#show_deptment");
    var design_container=$("#design_container");
    var init_div=sel_cols_container.add(design_container);
    $.ajax({
        type:"GET",
        url:"/"+surl+"report/get_model_attributes/"+app_label+"/"+model_name+"/?stamp"+new Date().getTime(),
        dataType:"json",
        success:function(data){
            init_div.empty();
            //g_report["field_data"]=data;
            g_data["field_data"]=data;
            var html=render_tree_container(data,"","filetree",sel_cols_container);
            sel_cols_container.width(199);
            sel_cols_container.append(html);
            //新增按钮
            if(sel_cols_container.find("#id_new_formula").length==0){
                sel_cols_container.append("<input type='button' value='新增' />");
            }
            
            sel_cols_container.parent().hide().treeview().show();
           
            //列点击事件
            sel_cols_container.find("p.t").click(function(){
                if($(this).hasClass("s")){//取消
                    var p_cancel=$(this).add($(this).parent("li").find("li>p.t"));
                    p_cancel.removeClass("s");
                    $.each(p_cancel,function(index,elem){
                        var field_value=$(elem).attr("value");
                        if(!field_value){//全选节点
                            return;
                        }
                        if(g_report.fields_attributes[field_value]){
                            delete g_report.fields_attributes[field_value];
                        }
                        for (var i in g_report.fields){
                            if(g_report.fields[i]==field_value){
                                g_report.fields.splice(i,1);
                                //删除相应的设计div
                                //render_report_fields(design_container,g_report,obj_design_container);
                                break;
                            }
                        }
                    });
                }else{//添加
                    var p_select=$(this).add($(this).parent("li").find("li>p.t"));
                    p_select.addClass("s");
                    
                    $.each(p_select,function(index,elem){
                        var field_value=$(elem).attr("value");
                        if(!field_value){//全选节点
                            return;
                        }
                        if(!g_report.fields_attributes[field_value]){
                            g_report.fields_attributes[field_value]={
                                "display":$(elem).text(),
                                "adv_search":{},
                                "search":{},
                                "sort":"|",
                                "is_group_field":"false",
                                "is_expressions_field":"false",
                                "expression":"FingerID"
                            };
                            g_report.fields[g_report.fields.length]=field_value;
                            //添加相应的设计div
                            //render_report_fields($("#design_container"),g_report,obj_design_container);
                        }
                    });
                }
                //核对需要新增加的列和需要删除的设置列
                field_div_check(design_container.find("#id_fields_propery").find("#show_sources"),g_report);
                return false;
            });
            //渲染报表列属性编辑容器
           render_report_fields(design_container,g_report,obj_design_container);
           //渲染报表其他属性
           render_report_propertys(design_container,g_report);
            
        }
    });
    
}


/**
@step 当前显示第几步
@function 显示当前功能所需要的div
**/
function show_report_div(step){
    var STEP_ONE=1;
    var STEP_TWO=2;
    var obj_step_one=$("#id_step_one");
    var obj_step_two=$("#id_step_two");
    if(step==STEP_ONE){
        obj_step_one.show();
        obj_step_two.hide();
    }
    if(step==STEP_TWO){
        obj_step_one.hide();
        obj_step_two.show();
    }
}


/**
@obj_btn 取消设计的按钮对象
@function 取消报表设计，关闭编辑界面，回到列表展示
**/
function init_cancel_report_btn(obj_btn){
    obj_btn.click(function(){
        var varDivEdit=$("div.class_div_edit");
        var grid=$("#id_datalist").get(0);
        if(grid.g.do_action_template){
            varDivEdit.empty();
        }else{
            varDivEdit.remove();
        }
        $(grid).show();
        grid.g.load_data(); 
        if(grid.g){
            $.zk._hide_switch(false,grid.g.do_action_masker_div);//隐藏
        }else{
            $.zk._hide_switch(false);
        }
    });
}


/**
@surl 网站根目录
@obj_btn 下一步按钮对象
@g_report 报表设计存储的数据结构
@function 初始化下一步按钮事件
**/
function init_step_one_btn(surl,obj_btn,g_report){
    obj_btn.click(function(){
        var STEP_TWO=2;
        //验证是否选择了数据源
        get_sources_attributes(surl,$("#id_step_two"),g_report);
        //隐藏第一步的相关div，显示第二步的相关div
        show_report_div(STEP_TWO);
    });
}


/**
@surl 网站根目录
@obj_btn 确定按钮对象
@g_report 报表设计存储的数据结构
@function 初始化确定按钮事件
**/
function init_step_two_btn(surl,obj_btn,g_report){
    obj_btn.click(function(){
        var STEP_ONE=1;
        //验证是否选择了数据源
        
        //隐藏第一步的相关div，显示第二步的相关div
        show_report_div(STEP_ONE);
    });
}

/**
@surl 根路径
@btn_jdom 确定按钮
@g_report 全局报表结构
**/
function init_ok_btn(surl,btn_jdom,g_report,pk){
    btn_jdom.click(function(){
        var report_property=$("#id_report_property");
        g_report["report_name"]=report_property.find("#id_name.wZBaseCharField").val();
        g_report["report_type"]=report_property.find("#id_report_type.wZBaseForeignKey option:selected").val();
        var post_url="/"+surl+"report/new_report/";
        if(pk!="None"){
            post_url="/"+surl+"report/edit_report/"+pk+"/";
        }
        if($("#id_edit_form").valid()){
            $.ajax({
                type:"POST",
                url:post_url,
                data:{"g_report":serialize_json(g_report)},
                dataType:"html",
                success:function(msg){
                    $("a.Cancel").click();
                }
            });
        }
    });
    
}

//序列化js对象pwp
function serialize_json(obj){
    var stack=[];
    var type="com";
    var obj_count=0;
    var result=[];
    stack.push(obj);
    obj_count++;
    
    while(obj_count!=0){
        var obj=stack.pop();
        obj_count--;
        
        if(typeof(obj)!="object"){
            result.push(String(obj));
            continue;
        }
        
        if(obj.length!=undefined){
            type="list";
            stack.push("[");
        }else{
            type="object";
            stack.push("{");
        }
        obj_count++;
        
        var flag=false;
        for(var i in obj){
            flag=true;
            var elem=obj[i];
            var type_e=typeof(elem);
            
            if(type=="list"){
                if(type_e!="object"){
                    stack.push('"'+elem+'"');
                    obj_count++;
                }else{
                    stack.push(elem);
                    obj_count++;
                }
            }else if(type=="object"){
                if(typeof(elem)!="object"){
                    stack.push('"'+i+'":"'+elem+'"');
                    obj_count++;
                }else{
                    stack.push('"'+i+'":');
                    stack.push(elem);
                    obj_count+=2;
                }
            }
            stack.push(",")
            obj_count++;
        }
        
        if(flag){//去除最后一个逗号
            stack.pop();
            obj_count--;
        }
        if(obj.length!=undefined){
            stack.push("]");
        }else{
            stack.push("}");
        }
        obj_count++;
    }
    
    return result.reverse().join("");
}