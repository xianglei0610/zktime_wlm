function init_pwd_change(){
    $("#id_btn_changePW").unbind().click(function(){
        var url=$(this).attr("ref")
        var html="<div><form id='form_change_pwd'>"
           +"<table>"
               +"<tr><th>"+gettext("原 密 码:")+"</th><td><input type='password' name='org_pwd'></input></td></tr>"
               +"<tr><th>"+gettext("新 密 码:")+"</th><td><input type='password' name='new_pwd' id='id_new_pwd'></input></td></tr>"
               +"<tr><th>"+gettext("再次输入:")+"</th><td><input type='password' name='new_again_pwd' id='id_new_again_pwd'></input></td></tr>"
           +"</table>"
           +"<div id='id_div_result_error' class='displayN'><ul class='errorlist'><li></li></ul></div>"
           +"</form></div>"
        var showhtml=$(html)
        var cancel=function(div){					
               $("#id_close").click();
        };
        var save_ok=function(){	
           if($("#id_new_pwd").val()!=$("#id_new_again_pwd").val()){
               alert(gettext("新密码，两次输入不一致"));
               return;
           }
           showhtml.find("#form_change_pwd").ajaxSubmit({
                   type:"POST",
                   url:url,
                   success:function(data){
                       if(data=='{ Info:"OK" }'){
                           alert(gettext("保存成功"));
                           $("#id_close").click();
                       }else{
                           $("#id_div_result_error").removeClass("displayN")
                           $("#id_div_result_error").find("li").html(data)
                       }
                   }					
            });	
        };
        var ok_name = gettext('确认');
        var cancel_name = gettext('取消');
        var btn_dict={};
        btn_dict["buttons"]={}
        btn_dict["buttons"][ok_name]=save_ok;
        btn_dict["buttons"][cancel_name]=cancel;
        btn_dict["title"]=gettext("密码修改");
        showhtml.dialog(btn_dict);
    });
}

$(function(){
    init_pwd_change();
});