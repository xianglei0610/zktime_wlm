//登入函数
function init_login(
        is_focus_username,doc_username_id,doc_pwd_id,
        submit_id,form_id,reset_id,post_url,redirect_url,finger_login_id
){
    var $user_name=$("#"+doc_username_id);
    var $user_pwd=$("#"+doc_pwd_id);
    var $login = $("#"+submit_id);
    var $reset = $("#"+reset_id);
    var $login_form = $("#"+form_id);
    var $finger_login = $("#"+finger_login_id);
    //语言
    var client_language="";
    if(navigator.systemLanguage){
        client_language=navigator.systemLanguage
    }else{
        client_language=navigator.language
    }
    //焦点
    if(is_focus_username){
		$user_name.focus();
    }
    
    $user_pwd.keypress(function(event){
        if(event.keyCode==13){
            $login.click();
        }
    }); 
    
    $reset.click(function(){
		if (reset_id=='id_reset_self')
		{
	        $("#id_username_self").val('');
	        $("#id_password_self").val('');
	        $("#id_username_self").select();
		}
        $("#id_username").val('');
        $("#id_password").val('');
        $("#id_username").select();
    });
    
    //密码登入
    $login.click(function(){
        $(".messageBox").html("").show();
        if($.trim($user_name.val())=="" || $.trim($user_pwd.val())==""){
            $(".messageBox").html($("#id_corrent_up_info").val()).show();
            $user_name.select();
            return false;
        }
        $("#id_login_type").val('pwd');
        serialize_form=$login_form.serialize();

        $.ajax({
            url:post_url,
            type:"POST",
            data:serialize_form,
            dataType:"html",
            success:function(msg){
                if(msg=='ok'){
                    var index=window.location.href.indexOf("?next=");
                    var self_index = window.location.href.indexOf("selfservice");
                    if(index!=-1 && is_focus_username && self_index==-1){
                        window.location.href=window.location.href.substring(index+6);
                    }else{
                        window.location.href=redirect_url;
                    }
                }else{
                    $("#id_username").select();
                    $("#id_password").val('');
                    $(".messageBox").html(msg).show();
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
               // alert(textStatus+" "+errorThrown);
            }
        });
    });
    
    
    //指纹登入
    $finger_login.click(function(){
        $(".messageBox").html("").show();
        $("#id_pwdlogin").attr("disabled",true);
        $("#id_login_type").val('fp');
        $user_name.val("");
        $user_pwd.val("");
        $user_name.select();
        if($("#id_client_language").val().toLowerCase() == 'zh-cn'){
            zkonline.SetLanguageFile("zkonline.chs")  //设置为中文界面
        }
        if($("#id_client_language").val().toLowerCase() == 'en'){
            zkonline.SetLanguageFile("zkonline.en")  //设置为英文界面
        }
        zkonline.FPEngineVersion = '10';
        //zkonline.FPEngineVersion = '9';
        if(zkonline.GetVerTemplate()){
            $("#id_template10").val(zkonline.VerifyTemplate.toString());
            serialize_form=$("#login-form").serialize();
            $(".messageBox").html(gettext("比对验证中，请稍等!")).show();
            $.ajax({
                url:post_url,
                type:"POST",
                data:serialize_form,
                dataType:"html",
                success:function(msg){
                    $("#id_pwdlogin").attr("disabled", false);
                    if(msg=='error'){
                        $(".messageBox").html(gettext("验证失败，请重试!")).show();
                        return false;                    
                    }else if(msg == "2"){
                        $(".messageBox").html(gettext("10.0指纹算法许可失败!")).show();
                        return false;
                    }else {
                        $(".messageBox").html(gettext("验证通过，登录系统!")).show();
                        window.location.href=redirect_url;
                    }
                }
            });                      
        }
        else{
            $(".messageBox").html(gettext("获取指纹失败，请重试!")).show();
            return false;
        }
    });
    
    if(!$.browser.msie){
        $("#id_fp_identify,#id_fp_identify_self").attr({disabled:"true", title:gettext("登记指纹功能只支持IE浏览器")}).css({cursor:"default",color:"#888888"}).unbind().click(function(){
            //$(".messageBox").html(gettext('登记指纹功能只支持IE浏览器')).show();
            return false;
        });
    }
    else{
        var flag = false;
        for(var i in zkonline){
           if(i == "FPEngineVersion"){
              flag = true;
           }
        } 
        if(!flag){
            $("#id_fp_identify").attr({disabled:"true", title: gettext("请安装指纹仪驱动")}).css({cursor:"default",color:"#888888"}).unbind().click(function(){
                return false;
            });
        }
    }
    
    if ($.trim($("#id_change_css").val())=="TRUE"){
        $("#login_btn_box").css("margin-left", "70px");//4.1没有指纹登录时临时修改样式
    }
    
}



$(function(){
   if(document.body.offsetWidth < 900 || document.body.offsetHeight < 360){
       top.moveTo(0,0);
       top.resizeTo(screen.availWidth,screen.availHeight);
   }
   //button style
    var login_btn=$(".login_btn0").find("div>span");
       for(var i=0; i<login_btn.length;i++){
           login_btn.eq(i).hover(
               function(){
                   $(this).parents(".login_btn0").attr("class","login_btn1");
               },
               function(){
                   $(this).parents(".login_btn1").attr("class","login_btn0");
               }
           )					
       }

    //Login Type Selection
    var list_li=$(".login_middle_title>ul>li");
    var gvar={};
    gvar.click_row=list_li.eq(0);
    list_li.click(function(){
        if(!$(this).hasClass("line_focus ")){
            $(this).addClass("line_focus");
            $(this).parents(".login_middle_title").attr("class","login_middle_title "+$(this).attr("cc"));
        }
        if(gvar.click_row && gvar.click_row.get(0)!=this){
            gvar.click_row.removeClass("line_focus");
        }
        gvar.click_row=$(this);	
    });
    //默认登入
    init_login(true,'id_username','id_password','id_login','login-form','id_reset','/accounts/login/','../../data/index/','id_fp_identify')
    //员工自助登入
    init_login(false,'id_username_self','id_password_self','id_login_self','login-self-form','id_reset_self','/selfservice/login/','/selfservice/index/','id_fp_identify_self')
});