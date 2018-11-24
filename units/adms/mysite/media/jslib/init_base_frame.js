var surl=$("#id_surl").val();
var dbapp_url=$("#id_dbapp_url").val();

function init_page(){
    var mmli=$(".help_more_list").find("li");
    var mmw=0;
    for(i=0;i<=mmli.length-1;i++){
        if($(mmli[i]).width()>mmw)
        mmw=$(mmli[i]).width();
    }
    $(".help_more_list").css({width:mmw});
    $(".help_more_list>li").css({width:"100%"});
    $(".help_more_list").bgiframe();
            
    $("#id_copy_right").click(function(){
        var sys_type = $("#id_sys_type").val();//zkeco zkaccess zktime
        var is_oem = $("#id_oem").val();
        var is_zkaccess_att = $("#id_zkaccess_att").val();
        var is_zkaccess_5to4 = $("#id_zkaccess_5to4").val();
        var id_pos_type = $("#id_pos_type").val();
        var id_meeting_type = $("#id_meeting_type").val();
        var title_name = "ZKECO";
        var att_name = "ZKTime";
        var acc_name = "ZKAccess";
        var pos_name = "ZKPos"//消费
        var meeting_name = "ZKMeeting" //会议
        var version = "3.5.2.30917";
        var version_name = "ZKTeco Inc";
        var version_logo = "";
        var oem_class = "";
        var att_version = "8.5.2";
        var acc_version = "5.1.2";
        var pos_version = "2.0.1";
        var meeting_version = "1.0.2";
        var daginfo = $("#id_dog_info").val()
        if(is_zkaccess_5to4 == "True")
        {
            acc_version = "4.5.20_plus";
        }
        
        if(sys_type == 'zkaccess')
        {
            if(is_oem == "True")
            {
                title_name = "Access";
                acc_name = "Access";
                version_name = "";
                oem_class = "_oem";
            }
            else
            {
                title_name = "ZKAccess";
            }
            version = acc_name + ": " + acc_version + "<br /><span>";
        }
        else if(sys_type == 'zktime')
        {
            if(is_oem == "True")
            {
                title_name = "Attendance";
                att_name = "Time";
                version_name = "";
                oem_class = "_oem";
                att_version = "8.2.0";
            }
            else
            {
                title_name = "ZKECO";
            }
            version = att_name + ": " + att_version + "<br /><span>";
        }
         else if(sys_type == 'zkmeeting')
        {
            if(is_oem == "True")
            {
                title_name = "Meeting";
                meeting_name = "Meeting";
                version_name = "";
                oem_class = "_oem";
            }
            else
            {
                title_name = "ZKMeeting";
            }
            version = meeting_name + ": " + meeting_version + "<br /><span>";
        }
        else if(sys_type == 'zkeco')
             {
                if(is_oem == "True")
                    {
                        title_name = "ECO";
                        att_name = "ZKECO";
                        version_name = "";
                        oem_class = "_oem";
                    }
                else
                {
                    title_name = "ZKECO";
                    //att_name = "ZKECO";
                    version = title_name + ": " + version + ";" +att_name + ":" + att_version + ";" +acc_name +": "+acc_version+";";
                    if (id_pos_type=="True")
                		version = version+pos_name + ": "+ pos_version+";";
                	if (id_meeting_type=="True")
                		version = version+meeting_name +": "+meeting_version;
                	version=version+"<br /><span>";
                }
             }
        
        else if(sys_type=='ZKPos')
       {
           if(is_oem == "True")
           {
               title_name = "ZkPos";
               att_name = "ZkPos";
               version_name = "";
               oem_class = "_oem";
           }
           else
           {
               title_name = "ZkPos";
           }
           version = pos_name + ": " + pos_version + "<br /><span>";
       }
        
        else
        {   
            if(is_zkaccess_att == "True")
            {
                if(is_oem == "True")
                {
                    title_name = "Access";
                    acc_name = "Access";
                    version_name = "";
                    oem_class = "_oem";
                }
                else
                {
                    title_name = "ZKAccess";
                    version_name = "";
                }
                version = acc_name + ": " + acc_version + "<br /><span>";
            }
            else
            {
                if(is_oem == "True")
                {
                    title_name = "ECO";
                    att_name = "Attendance";
                    acc_name = "Access";
                    version_name = "";
                    oem_class = "_oem";
                }
                version = title_name + ": 3000<br />"
                    + att_name+": " + att_version + "<br />"
                    + acc_name+": " + acc_version + "<br /><span>";
            }
        }
        
        var vbox=$("<div class='version_box'>"
                + "<div class='version_content_box"+oem_class+"'>"
                    + "<div class='version_details_box'><span>"
                        + gettext("版本号")+":</span><br />"							
                        + version
                        + gettext("加密狗信息")+":</span><br />"
                        + daginfo	
                        + gettext("<br /><span>本系统建议使用浏览器")
                        + ":</span><br />Internet Explorer 8.0+/Firefox 3.6+<br /><span>"
                        + gettext("显示器分辨率")
                        + ":</span><br />1024×768 "
                        + gettext("及以上像素")+"<br /><span>"
                        + gettext("软件运行环境")
                        + ":</span><br />WindowsXP/Windows2003/Windows7<br />MS SQL Server 2005/2008"
                    + "</div>"
                    + "<div class='version_copyRight'>Copyright &copy; "+$("#id_current_year").val()+" "+version_name+".</div>"
                    + "</div>"
                + "</div>");
        vbox.dialog({title:gettext("关于") +" "+ title_name});
    });

    $("#id_page_load").bgiframe();
    $("#eMeng").bgiframe();
    var var_app_menu=$("#id_app_menu");
    //菜单行超过宽度产生折行时，把最后一个菜单项放到下拉列表中去
    //while(var_app_menu.width()>825)
    //解决IE下门禁参数设置Tab无法显示的问题
    //IE7:width=803
    while(var_app_menu.width()>850)
    {
       var var_li=$("li.tabs_li:last", var_app_menu);
       $(".menu_more").prepend(var_li);
    }					
    if($(".menu_more").find("li").length==0){
        $("#nav").hide();
    }
    else{
        $("#nav").show();
    }
    var mli=$(".menu_more").find("a");
    var mw=0;
    for(i=0;i<=mli.length-1;i++){
        if($(mli[i]).width()>mw)
        mw=$(mli[i]).width();
    }
    mw=mw + 20;
    $(".menu_more").css({width:mw});
    $(".menu_more>li").css({width:"100%"});
       //根目录
        document.title=$("#id_browse_title").val();
    //console.log("on page load start");
    $("#id_page_load").hide();
    if($.browser.msie){
        document.execCommand("BackgroundImageCache", false, true);
    }

      page_load_effects("/"+surl+"accounts/login/",$("#id_gz"),$("#id_page_load"));
    //处理菜单
      $("#id_true_app li").each(function(){
        if($(".app_"+$(this).attr("name")).length>0){//如果在别的地方配置了这个应用的app_app_name样式,就删除之
            $(this).remove();
        }
    });
    //我的工作台
    $("#id_worktable").attr("href",dbapp_url+"worktable/");	
    $('.nav li').sfHover();
    $("#id_btn_logout").click(function(){
        if(confirm(gettext('确定注销系统?'))){
                $.ajax({
                    type:"POST",
                    url:$(this).attr("ref"),
                    success:function(msg){
                        if(msg=="ok"){
                            window.location.replace("/"+surl+"accounts/login/");
                        }
                    }
                });
        }
    })
    $("#id_btn_option,#id_btn_changePW").click(function(){
        var a_this=this;
        var btn_values=[gettext("确定"),gettext("取消")]
        if($(this).attr("btn_values")){
            btn_values=$(this).attr("btn_values").split("__");
        }
        var d=new Date();
        var href=$(this).attr("ref")+"?stamp="+d.getTime();
        var next_checking="ok";
        $.ajax({
            url:href,
            type:"GET",
            success:function(msg){
                if($("#id_opt_message").length==0){
                    $("body").append("<div id='id_opt_message'></div>");
                }
                var msg_dialog=$("#id_opt_message");
                msg_dialog.append(msg);
                render_widgets(msg_dialog);
                if($("#ret_info",msg_dialog).length==0){
                    msg_dialog.append("<div id='id_ret_info' class='ret_info'></div>"); 
                }
                
                var btns='<div class="btns_class"><button class="btn" id="id_OK" type="button">'+btn_values[0]+'</button>'
                        +'<button class="btn" id="id_Cancel" type="button">'+btn_values[1]+'</button></div>'
                var $form=msg_dialog.find("form");
                $form.find("input[type!=hidden]").keydown(
                    function(event){
                        if(event.keyCode==13)
                        {
                            msg_dialog.find("#id_OK").click();
                        }
                });
               
                
                $("#id_new_password1").attr("maxlength","18"); 
                $("#id_new_password2").attr("maxlength","18");//修改密码 限制位数

                $form.append(btns);
                $("#id_span_title",msg_dialog).find("span:not(.icon_SiteMap)").remove();
                msg_dialog.find("#id_Cancel").click(function(){
                    $("#id_close",msg_dialog).click();
					$(".bgiframe78").remove();
                });
                msg_dialog.find("#id_OK").click(function(){
                    var pwd1=$("#id_new_password1").val();
                    var pwd2=$("#id_new_password2").val();
                    if (pwd1)
                    {   
                        next_checking="ok";
                        if((pwd1[0]==" ") || (pwd2[0]==" "))
                        {
                            alert(gettext('首字符不能为空!'));
                            next_checking="no";
                            return false;
                        
                        }
                        if (pwd1.length < 5 ||pwd2.length <5 )
                        {
                            alert(gettext('密码长度必须大于4位!'));
                            next_checking="no";
                            return false;
                        }
                    }
                    if($form.valid()&&next_checking=="ok"){
                        $form.ajaxSubmit({ 
                            url:href, 
                            dataType:"html", 
                            async:false, 
                            success:function(msgback){ 
                                if(msgback.indexOf('{ Info:"OK" }')!=-1){
                                    $("#id_close",msg_dialog).click();
									$(".bgiframe78").remove();
                                    if($(a_this).attr("id")=="id_btn_option"){
                                        window.location.reload();
                                    }
                                }else{
                                    var ret_div=$("#id_ret_info",msg_dialog);
                                    ret_div.html($(msgback).find("ul.errorlist").eq(0));
                                    if($(a_this).attr("class")=="btn_changePW"){
                                        var $inputs=msg_dialog.find("input[type!=hidden]");
                                        $inputs.eq(0).select();
                                        $inputs.not(":first").val("");
                                    }
                                }
                            }
                        });
                    }
                });
                
                msg_dialog.dialog({
                    title:$(a_this).text(),
                    on_load:function(obj){
                        obj.target.getOverlay().find("input[type!=hidden]:first").focus().select();
						if($.browser.msie && $.browser.version > 6){
							$("#overlay").prepend("<iframe class='bgiframe78' frameborder='0' style='filter: Alpha(Opacity=\"0\"); position:absolute; width:"+$("#overlay").width()+"px;height:"+$("#overlay").height()+"px;z-index:-1'></iframe>")
						}
                }});
				
                
            },
            error:function (XMLHttpRequest, textStatus, errorThrown) {
                alert(gettext("服务器处理数据失败，请重试！错误码：-616"));//服务器加载数据失败,请重试!
            }
            
        });
    });
}


function OnCommError() {
    var d=new Date()
    getUrl='/'+surl+'iaccess/comm_error_msg/';
    $.ajax({ 
        type:"GET", 
        url:getUrl, 
        dataType:"json", 
        async:true, 
        success:function(rtlog)
        {
            rtlisthtml = ""
            for(var index in rtlog.data) 
            {
                datas = rtlog.data[index];
                if (datas != undefined)
                {
                    rtlisthtml += "<P align=left><a target='_blank' href='/"+surl+"iclock/DevRTMonitorPage/'><font color=#FF0000>" + datas.devname + gettext('通讯失败') + "</font></a></P>"
                }
            }
            $("#id_comm_error marquee").empty();
            $("#id_comm_error marquee").prepend(rtlisthtml);
            window.setTimeout('OnCommError()', 10000)//等*秒执行刷新函数原来20s
        }
    });
}
function init_iaccess(){
    //window.setTimeout('OnCommError()', 1000);
}