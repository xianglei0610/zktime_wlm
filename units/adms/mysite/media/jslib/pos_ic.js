/********************读卡：判断读卡方式是否正确****************/
function clearNoNum(obj)
	{
         obj.bind('onkeyup',function(){
        //先把非数字的都替换掉，除了数字和.
            obj.value = obj.value.replace(/[^\d.]/g,"");
            //必须保证第一个为数字而不是.
            obj.value = obj.value.replace(/^\./g,"");
            //保证只有出现一个.而没有多个.
            obj.value = obj.value.replace(/\.{2,}/g,".");
            //保证.只出现一次，而不能出现两次以上
            obj.value = obj.value.replace(".","$#$").replace(/\./g,"").replace("$#$",".");
        });
	}
//function getCount() {
//	var p_url = "/mysite/templates/SessionKeeper.html?RandStr="+Math.random();
//     $.ajax({
//        type: "POST",
////        url: "/{{request.surl}}data/personnel/IssueCard/",
//		url:p_url,
//        data: {},
//        success: function(msg){
//        },
//        error:function()
//        {
//        }
//     });
// 
// }
//
//var id_of_setinterval;
//
//function begin_interval()
//{
//    id_of_setinterval=setInterval("getCount()",10000);//3分钟请求一次服务器。防止session过期。
//}
//
//function close_interval()
//{
//	clearInterval(id_of_setinterval);
//}
//
//$(window).unload( function () { close_interval} );//离开页面时停止


//读卡间隔延时
function readCardSleep()
{
	
}
function readCard()//读卡
    {   
        var t1 = zkonline.ZK_PosReadCardSerial(0);
		readCardSleep();
        var t2 = zkonline.ZK_PosReadCardSerial(0);
        $("#id_info").remove();
		if ( t1 != t2)
		{ 
			return '999'
		}
        else if (t1==t2 && t1.length >4 && t2.length>4 )
        {            
            return t1;
        }
        else
        {
            return t1;
        }
    }

/********************读卡错误返回值信息****************/
function check_card(errCode)
   {
       switch(errCode.toString())
         {
			case '999':
			  $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>卡号不一致,操作失败！</li></ul></div>');
			  return false;
			  break;
            case '-2':
               $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>主备扇区数据不一致，该卡片需要在消费机上刷一次后，才能正常使用</li></ul></div>');
               return false;
               break;
            case '131':
               $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>没有找到IC卡或者卡是否损坏</li></ul></div>');
               return false;
               break;
            case '140':
               $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>扇区密码错误</li></ul></div>');
               return false;
               break;
            case '5':
              $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>请连接读卡器</li></ul></div>');
              return false;
              break;
			default:
				$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>'+errCode.toString()+'</li></ul></div>');
				return false;
				break;
				
			
         } 
   }

/********************字符转换16进制ASCII码***************/
function stringToBytes ( str ) { 
     var ch, st, re = []; 
     for (var i = 0; i < str.length; i++ ) { 
       
       ch = str.charCodeAt(i).toString(16);
       st = [];                 // set up "stack" 
       do { 
         st.push( ch & 0xFF );  // push byte to stack 
         ch = ch >> 8;          // shift value down by 1 byte 
       }   
       while ( ch ); 
       re = re.concat( st.reverse() ); 
     } 
     return re; 
   } 

/********************验证是否为空白卡***************/
function isEmptyCard()
    {
        var retInfo = zkonline.ZK_PosReadICCard(0,stringToBytes(sys_pwd),main_fan,minor_fan);
        var strlist = retInfo.split(',');
//        alert(retInfo);
        var flag = false;
        if (strlist.length >1)
        {
            for(i=0;i<2;i++)
            {
                if(strlist[i].split('=')[1]==0 && strlist[4].split('=')[1]==0 && strlist[6].split('=')[1]==0)
                {
                   flag = true;
                }
                else
                 {
                    flag = false;
                    return flag;
                    break;    
                 }   
            }
            return flag;
        }
        else
        {
            return retInfo
        }
            
    }


function isOnline()
{	
    if(!$.browser.msie)
       {
//          $("#id_info").remove();
          $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作只支持IE浏览器</li></ul></div>');
          return;
       } 
    else
    {
        t = zkonline.ZK_PosReadCardSerial(0);
        if (t!='5') 
           {
               $("#read_card").attr("disabled","");
               $("#read_card").attr('style','none');
               return true;
           }
        else
        {
           $("#id_info").remove();
           $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>请连接发卡器</li></ul></div>');
           return false;
        }
    }
    
}


/*s_money = 操作金额 b_money = 补贴金额*/
function writeICMoney(comm_handle,pwd,s_money,b_money,main_sec,back_sec)
{
    return zkonline.ZK_PosWriteICCardMoney(comm_handle,pwd,s_money,main_sec,back_sec);
}

/****after_money = 充值，退款后金额 
m_money = 充值，退款金额
 begin_money = 操作前卡上金额*/
function isvild_write_card(card_serial_no,m_money,after_money,begin_money)
{
    var retInfo = zkonline.ZK_PosReadICCard(0,stringToBytes(sys_pwd),main_fan,minor_fan);
    var current_serial_no = Number(retInfo.split(',')[7].split('=')[1]);
    var card_money = retInfo.split(',')[6].split('=')[1];
    var margin = current_serial_no - card_serial_no;
//    alert("current_serial_no=="+current_serial_no+"card_serial_no=="+card_serial_no+"card_money=="+card_money+"after_money==="+after_money);
	
    if ( margin == 1 && card_money == after_money)
    {
        return true;
    } 
    else
    {
        money = -m_money;
        var v =  writeICMoney(0,stringToBytes(sys_pwd),money,0,main_fan,minor_fan);
        return false;
    }
}




/**** 验证制卡时数据
after_money = 制卡后金额 
m_money = 制卡时充值金额
 begin_money = 制卡前卡上金额*/
function isvild_write_Add_card(card_serial_no,m_money,after_money,begin_money)
{
   // alert(card_serial_no+"++++"+"sys_pwd="+sys_pwd +"after_money="+after_money+"++++"+begin_money+"+++++"+main_fan +"SSSSS" + minor_fan);
    var retInfo = zkonline.ZK_PosReadICCard(0,stringToBytes(sys_pwd),main_fan,minor_fan);
    
//    alert(retInfo);
    var current_serial_no = Number(retInfo.split(',')[7].split('=')[1]);
    var card_money = retInfo.split(',')[6].split('=')[1];
    var margin = current_serial_no - card_serial_no;
//	alert(margin+"===="+card_money+"====="+after_money)
    if ( margin == 1 && card_money == after_money)
    {
        return true;
    } 
    else
    {
        //清空卡
        zkonline.ZK_PosClearICCard(0,stringToBytes(sys_pwd),main_fan,minor_fan)
        return false;
    }
}


/*验证操作卡的有效性*/

function funValidCard()
{   
    var queryStr=$("#id_edit_form").formSerialize();  
	var return_tag = false;  
    $.ajax({ 
        type: "POST",
        url:"/pos/valid_card/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    return_tag = true;
                    break;
                case "PRIVAGE_CARD":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为管理卡，操作失败！</li></ul></div>');
                    return_tag = false;
                    break;  
                case "CARD_STOP":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为停用卡，操作失败！</li></ul></div>');
                    return_tag = false;
                    break;
				case "CARD_LOST":
					$("#id_info").remove();   
					$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为挂失卡，操作失败！</li></ul></div>');
					return_tag = false;
					break;
                case "Not_REGISTER_CARD":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片没有登记卡账号，操作失败！</li></ul></div>');
                    return_tag = false;
                    break;
                case "CARD_OVERDUE_VALID":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>请先挂失卡片，操作失败</li></ul></div>');
                    return_tag = false;
                    break;
				case "STATUS_LEAVE":
					$("#id_info").remove();   
					$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡片对应人员已经离职，操作失败</li></ul></div>');
					return_tag = false;
					break;
				
            }
        }
    }); 
    return return_tag;
}

function page_valid(card_status,type)
{
    val_tag = false
    switch(card_status)
    {
        case "1":
            val_tag = true;
            break;
        case "3":
            $("#id_info").remove();   
            $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为挂失卡，不允许操作！</li></ul></div>');
            val_tag = false;
            break;
        case "5":
            $("#id_info").remove();   
            $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为停用卡，不允许操作！</li></ul></div>');
            val_tag = false;
            break;
        case "4":
			if (type =='1')
			{
				$("#id_info").remove();   
				$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为过期卡，不允许操作！</li></ul></div>');
				val_tag = false;
			}
			else  val_tag = true;
            break;
    }
    return val_tag
}

/*充值，退款，发卡时把数据存入备份表*/
var bak_tag = false;
function funSaveBakData()
{
    var queryStr=$("#id_edit_form").formSerialize();    
    $.ajax({ 
        type: "POST",
        url:"/pos/save_operate_bak_data/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    bak_tag = true;
                    break;
                case "FAIL":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>系统出错，操作失败！</li></ul></div>');
                    bak_tag = false;
                    break;  
                case "PRIVAGE_CARD":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为管理卡，操作失败！</li></ul></div>');
                    bak_tag = false;
                    break;  
                case "CARD_LOST":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为挂失卡，操作失败！</li></ul></div>');
                    bak_tag = false;
                    break;
                case "CARD_STOP":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为停用卡，操作失败！</li></ul></div>');
                    bak_tag = false;
                    break;
                case "CARD_OVERDUE":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前操作卡片为过期卡，操作失败！</li></ul></div>');
                    bak_tag = false;
                    break;
                case "IS_NEGATIVE_NUMBER":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>金额不能为负数</li></ul></div>');
                    bak_tag = false;
                    break;
                case "IS_ZERO":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>金额不能为零</li></ul></div>');
                    bak_tag = false;
                    break;
                case "OUT_LESSMONEY":
                   $("#id_info").remove();   
                   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>低于卡类最小余额</li></ul></div>');
                   bak_tag = false;
                   break;
                case "OUT_MAXMONEY":
                   $("#id_info").remove();   
                   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>超出卡类最大余额</li></ul></div>');
                   bak_tag = false;
                   break;
                
            }
        }
    }); 
    return bak_tag;
}

/*发卡时把数据存入备份表*/
var add_tag = false;
function funSaveAddCardBakData()
{ 
    var queryStr=$("#id_edit_form").formSerialize();  
    $.ajax({ 
        type: "POST",
        url:"/pos/save_add_card_bak_data/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    add_tag = true;
                    break;
                case "FAIL":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>制卡失败</li></ul></div>'); 
                    add_tag = false;
                    break;
				case "CARD_LOST":
					$("#id_info").remove();   
					$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡号已经挂失</li></ul></div>');
					add_tag = false;
					break;
				case "CARD_STOP":
					$("#id_info").remove();   
					$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡号已经停用，请先做无卡退卡操作</li></ul></div>');
					add_tag = false;
					break;
                case "HAVECARD":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>该人员已有正在使用的卡</li></ul></div>');
                    add_tag = false;
                    break;
				case "EMPNOTCARD":
					$("#id_info").remove();   
					$("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡号已登记人员跟实际发卡人员不一致，请核对后再发卡</li></ul></div>');
					add_tag = false;
					break;
                case "ISUSE":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡号已被使用，如需继续使用该卡，请先退卡！</li></ul></div>');
                    add_tag = false;
                    break;
                case "OUT_LESSMONEY":
                   $("#id_info").remove();   
                   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>低于卡类最小余额</li></ul></div>');
                   add_tag = false;
                   break;
                case "OUT_MAXMONEY":
                   $("#id_info").remove();   
                   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>超出卡类最大余额</li></ul></div>');
                   add_tag = false;
                   break;
				case "SYS_ISUSE":
				   $("#id_info").remove();   
				   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>卡账号已使用，请刷新当前页面！</li></ul></div>');
				   add_tag = false;
				   break;
				case "EMP_LEAVE":
				   $("#id_info").remove();   
				   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡号登记的人员，已经离职！发卡失败！</li></ul></div>');
				   add_tag = false;
				   break;
				
            }
        }
    }); 
    return add_tag;
}

/*制卡成功把保存数据到卡表*/
var iss_tag = false;
function funSaveIssuecardData()
{
    var queryStr=$("#id_edit_form").formSerialize();    
    $.ajax({ 
        type: "POST",
        url:"/pos/save_issuecard_data/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    iss_tag = true;
                    break;
                case "FAIL":
                    iss_tag = false;
                    break;
            }
        }
    }); 
    return iss_tag;
}

var m_tag = "";
function funSaveCardManage()
{
    var queryStr=$("#id_edit_form").formSerialize();    
    $.ajax({ 
        type: "POST",
        url:"/pos/save_card_manage/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    m_tag = "OK";
                    break;
                case "FAIL":
                    m_tag = "FAIL";
                    break;
                case "ISUSE":
                   $("#id_info").remove();   
                   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>当前卡号已被使用，如需继续使用该卡，请先退卡！</li></ul></div>');
                   m_tag = "ISUSE";
                   break;
				case "SYS_ISUSE":
				   $("#id_info").remove();   
				   $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>卡账号已使用，请刷新当前页面！</li></ul></div>');
				   m_tag = "SYS_ISUSE";
				   break;
				
            }
        }
    }); 
    return m_tag;
}


// 取消按钮
function from_close()
{
  $("#id_datalist").get(0).g.load_data();
  $("#Cancel").click();
}

/*修改卡资料*/
var iss_tag = false;
function funChangeCardInfo()
{
    var queryStr=$("#id_edit_form").formSerialize();    
    $.ajax({ 
        type: "POST",
        url:"/pos/change_card_info/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    iss_tag = true;
                    break;
                case "FAIL":
                    iss_tag = false;
                    break;
            }
        }
    }); 
    return iss_tag;
}

/*充值，退款，发卡时把数据存入收支表*/
var save_tag = false;
function funSaveData()
{
    var queryStr=$("#id_edit_form").formSerialize();    
    $.ajax({ 
        type: "POST",
        url:"/pos/save_operate_data/",
        data:queryStr,
        dataType:"text",
        cache: false,  
        async:false,
        success:function(retdata){
            switch(retdata.split('=')[1])
            {
                case "OK":
                    save_tag = true;
                    break;
                case "FAIL":
                    $("#id_info").remove();   
                    $("#id_edit_form").append('<div id="id_info" style="display: block;"><ul class="errorlist"><li>系统出错，操作失败！</li></ul></div>');
                    save_tag = false;
                    break;
            }
        }
    }); 
    return save_tag;
}

