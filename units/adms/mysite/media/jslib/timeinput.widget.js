//时间段时间输入框--start
function TimeZoneBox(id, pNode){
    this.id = id;
    this.onChange=new Function();
    this.onEnterKey=new Function();
    this.disabled=false;
   
    TimeZoneBox.all[id]=this;
    //alert(this.toString)
    var str_input = '<span id="'+this.id+'" style="border: 1px solid white;" class="' + TimeZoneBox.EnabledClassName + '" >'
                   +'<input class="min" style="border: 1px solid white; text-align:center;" onkeypress="TimeZoneBox.evt.keypress(this,event)" onkeydown="TimeZoneBox.evt.keydown(this,event)" onfocus="TimeZoneBox.evt.focus(this,event)" onpaste="TimeZoneBox.evt.change(this,event);" oninput="TimeZoneBox.evt.change(this,event);" onchange="TimeZoneBox.evt.change(this,event);" type="text" size=1 id="'+this.id+'_1" maxlength="2"/>:'
                   +'<input class="sec" style="border: 1px solid white; text-align:center;" onkeypress="TimeZoneBox.evt.keypress(this,event)" onkeydown="TimeZoneBox.evt.keydown(this,event)" onfocus="TimeZoneBox.evt.focus(this,event)" onpaste="TimeZoneBox.evt.change(this,event);" oninput="TimeZoneBox.evt.change(this,event);" onchange="TimeZoneBox.evt.change(this,event);" type="text" size=1 id="'+this.id+'_2" maxlength="2"/>'
                   +'</span>';
    
    $("#"+pNode).append(str_input);
//    if(pNode)
//    {
//        if(typeof pNode=="string")
//        {
//            pNode=document.getElementById(pNode);
//        }
//        pNode.innerHTML=this.toString();
//    }
}
TimeZoneBox.all={};

TimeZoneBox.EnabledClassName="";//启用时样式
TimeZoneBox.DisabledClassName="ipInput oneInputDisabled";// 禁用时样式

TimeZoneBox.prototype={
    focus:function(index){
        //alert(index)
        if(!index)
        {
            index=1;
        }
        document.getElementById(this.id+"_"+index).focus();
    },
    //可用于编辑时禁用
    setEnable:function(bEnable){
        var b=bEnable;
        this.disabled=bEnable;
        var boxes=document.getElementById(this.id).getElementsByTagName("input");
        for(var i=0;i<boxes.length;i++)
        {
            boxes[i].readOnly=b;
        }
        document.getElementById(this.id).className=bEnable?TimeZoneBox.EnabledClassName:TimeZoneBox.DisabledClassName
    },
    getValue:function(){
        var tz = [
            document.getElementById(this.id+"_1").value,
            document.getElementById(this.id+"_2").value
        ];
        return tz.join(":");
       
    },
    setValue:function(tz){
        //alert(tz)
        //tz = tz.replace(/[^\d.]/g, "");???
//        if(tz == "")
//        {
//            tz = "..."
//        }
        tz = tz.split(":");
        document.getElementById(this.id+"_1").value = tz[0];
        document.getElementById(this.id+"_2").value = tz[1];
    }
}

TimeZoneBox.evt={
    focus:function(obj, evt){
        obj.select();
    },
    change:function(obj,evt){
        //alert(obj.className)
        var min_val = 0;
        var max_val = 0;
        if(obj.className === "min")
        {
            max_val = 23;
        }
        else//sec
        {
            max_val = 59;
        }

        var v = parseInt(obj.value, 10);
        if( v >= min_val && v <= max_val )
        {
            if(v != obj.value)
            {
                obj.value = v;
            }
        }
        else
        {
            obj.value="";
        }
        TimeZoneBox.all[ obj.id.replace(/_\d$/,"") ].onChange();
    },
    keypress:function(obj, evt){
        //alert('keypress')
        //alert(evt.charCode)
        //alert(evt.keyCode)
        var key = evt.charCode || evt.keyCode;//至少有一个为0，取不为零的
        //alert(key)
        var pos = TimeZoneBox.evt.getSelection(obj);
        //alert(pos)
        var value = obj.value;
        //alert(value)
        var c = String.fromCharCode(key);
        //alert(c)
        //alert(key)
        if(key >= 48 && key <= 57)//57
        {
            value = ""+value.substring(0,pos.start)
                + c + value.substring(pos.end,value.length);
            //alert(value)
            var max_val_press = 0;
            //alert(obj.className)
            if(obj.className.indexOf('min') != -1)//0 1 2
            {
                max_val_press = 24; 
            }
            else//sec 
            {
                max_val_press = 60
            }
            //alert(max_val_press)
            if(parseInt(value, 10) < max_val_press)
            {
                var id = obj.id;
                //alert('----id='+id);
                /(.*)_(\d)$/.test(id);//sunday_start1_span_1
                var index = RegExp.$2;//匹配第一个括号的值_后面的1
                tz_id = RegExp.$1;//匹配第二个括号的值。代表input的id， /(.*)_(\d)$/中的第一部分 sunday_start1_span  ？  tz_id=textarea？》
                //alert('---index='+index);//不能放到index定义后
                //alert('---tz_id='+tz_id);
                //alert(value)
                if(parseInt(value, 10) >= 10)//两位
                {
                    if(parseInt(index, 10) < 2)//填完小时自动跳转到秒（focus）
                    {
                        id=id.replace(/(\d)$/,parseInt(index, 10)+1 );
                        //alert('--id2='+id)
                        setTimeout("document.getElementById('"+id+"').focus();"+
                            "document.getElementById('"+id+"').select();",200);
                    }
                }
                setTimeout("TimeZoneBox.all['"+tz_id+"'].onChange()",0);
                return true;
            }
            else
            {
                if(evt.preventDefault)
                {
                    evt.preventDefault();
                }
                evt.returnValue=false;
                return false;
            }
        }
        else
        {
            if(evt.preventDefault)
            {
                evt.preventDefault();
            }
            evt.returnValue=false;
        }
    },
    keydown:function(obj, evt){
        //alert('---keydown')
        var key = evt.charCode || evt.keyCode;
		///alert(key+"------key");
        var pos = TimeZoneBox.evt.getSelection(obj);
        var value = obj.value;
        var c = String.fromCharCode(key);
        var id = obj.id;
        /^(.*)_(\d)$/.test(id);
        var index = RegExp.$2;
        var tz_id = RegExp.$1;
        //alert(index)
        //alert(tz_id)
        //alert(key)
        switch(key)
        {
            case 13://回车
                TimeZoneBox.all[tz_id].onEnterKey(); 
                //alert(value)  
                break;
 
            case 46://delete
                
                var text_selected = TimeZoneBox.evt.get_selected_text(obj);
                //alert(pos.start)
                //alert(text_selected)
                //alert(obj.value.length)
                if(pos.start == 0)//没有值不响应--一个或两个值，光标最左--选择第一个值或两个值
                {
                    if(obj.value.length == 1)//含放在该值值左边和选中唯一的这一个值
                    {
                        $("#"+id).val("");
                    }
                    else if(obj.value.length == 2)
                    {
                        if(text_selected == "")//未选中
                        {
                            $("#"+id).val(obj.value.split("")[1]);
                        }
                        else//选中两个值
                        {
                            $("#"+id).val("");
                        }
                    }
                }
                else if(pos.start == 1)//一个值时不响应----两个值时删第二个--两个值时选中第二个 删第二个
                {
                    if(obj.value.length == 2)
                    {
                        $("#"+id).val(obj.value.split("")[0]);
                        document.getElementById(id).select();//防止光标变换方位
                    }
                }
                //alert('end')
                break;

            case 229://FF .主键盘
            case 190://ie下.主键盘
            case 110://.小键盘
                if(index == 1 && value != "")
                {
                    //$(obj).val(value.replace(".", ""));
                    document.getElementById(id).value = value.replace(".", "");
                    id = id.replace(/(\d)$/,parseInt(index, 10)+1 );
                    document.getElementById(id).focus();
                    document.getElementById(id).select();
                }
                break;
            case 8://backspace
                //alert(pos.start)
                if(pos.start == 2)
                {
                    $("#"+id).val(obj.value.split("")[0]);
                }
                else
                {
                    var text_selected = TimeZoneBox.evt.get_selected_text(obj);
                     //alert(text_selected)
                    if(pos.start == 1)
                    {
                        if(text_selected == "")//光标两数字之间或只有一个数字且在该数字之后
                        {
                            if(obj.value.length == 2)
                            {
                                $("#"+id).val(obj.value.split("")[1]);
                            }
                            else//一个数字直接清空
                            {
                                $("#"+id).val("");
                            }
                        }
                        else//两个数字且选中第二个数字
                        {
                            $("#"+id).val(obj.value.split("")[0]);
                        }
                    }
                    else//=0，光标最左边，或选中第一个数字或同时选中两个数字
                    {
                        if(text_selected.length == 2)
                        {
                            $("#"+id).val("");
                        }
                        else if(text_selected.length == 1)
                        {
                            if(obj.value.length == 2)
                            {
                                $("#"+id).val(obj.value.split("")[1]);
                            }
                            else
                            {
                                $("#"+id).val("");
                            }
                        }
                    }
                }

                break;

            case 37://left
                //alert(pos.end)
                if(index == 2)// pos.end==0 &&  pos.end 0 1 2
                {
                    id=id.replace(/(\d)$/,parseInt(index,10)-1 );
                    document.getElementById(id).focus();
                    document.getElementById(id).select();
                }
                else//index=1
                {
                    //alert(id)//start1
                    var cur_td = $($("#"+id).parents("td")[0]);
                    if(cur_td.prev().length != 0)//未到达最左端-到达后不做处理
                    {
                        $(cur_td.prev().find("input")[2]).focus();//cur_td.next().find("input[class='min']") 如果有值，是null
                        $(cur_td.prev().find("input")[2]).select();
                    }
                }
                break;
            case 38://up
                var id_up_tail = id.replace(id.split('_')[0], "");
                var up_input = $("#"+id).parents("tr").prev().find("input[id*="+id_up_tail+"]");
                if(up_input.length != 0)//第一行不能再up
                {
                    up_input.focus();
                    up_input.select();
                }
                break;

            case 9://tab
            case 39://right
                //alert(pos.start +"   "+value.length)
                //alert(index)
                if(index == 1)//start为1和2， pos.start <= value.length && 
                {
                    //控制完成小时后（start为1或2，特别是1）不再输入了，手动跳转到秒
                    id = id.replace(/(\d)$/,parseInt(index, 10)+1 );
                    //alert(id)
                    //alert(document.getElementById(id).value)
                    document.getElementById(id).focus();
                    document.getElementById(id).select();
                    //alert(33333)
                }
                else if(index == 2)
                {
                    //alert(id)
                    var cur_td = $($("#"+id).parents("td")[0]);//我的工作面板（不同——）
                    if(cur_td.next().length != 0)
                    {
                        $(cur_td.next().find("input")[1]).focus();//cur_td.next().find("input[class='min']") 如果有值，是null
                        //$(cur_td.next().find("input")[1]).select();
                    }
                    else//到达最右端--调到下一行左边第一个
                    {
                        $(cur_td.parent().next("tr").find("input")[1]).focus();
                        //$(cur_td.parent().next("tr").find("input")[1]).select();//[class='min']:first
                    }
                }
                //停止---防止ie下，继续执行，跳转多余input
                if(evt.preventDefault)
                {
                    evt.preventDefault();
                }
                evt.returnValue=false;
                
                //alert(key)
                break;
            case 40://down
                var id_down_tail = id.replace(id.split('_')[0], "");
                var down_input = $($("#"+id).parents("tr")[0]).next().find("input[id*="+id_down_tail+"]");//含我的工作面板
                if(down_input.length != 0)//最后一行不能再down
                {
                    down_input.focus();
                    down_input.select();
                }
                break;
        }
    },
    keyup:function(obj, evt){
        //alert(obj.value)
        if(obj.value != "" && obj.className.indexOf("error") != -1)//去掉错误类
        {
            $(obj).removeClass("error");
        }
    },
    //获取选区位置
    getSelection:function(oInput){
        var T = this;
        if(oInput.createTextRange)
        {
            var s=document.selection.createRange().duplicate();
            s.moveStart("character",-oInput.value.length);
            var p1=s.text.length;
            var s=document.selection.createRange().duplicate();
            s.moveEnd("character",oInput.value.length);
            var p2=oInput.value.lastIndexOf(s.text);
            if(s.text=="")
            {
                p2=oInput.value.length;
            }
            return {start:p2,end:p1};
        }
        else 
        {
            return {start:oInput.selectionStart,end:oInput.selectionEnd};
        }
    },
    //获取选定的文本
    get_selected_text: function(obj_input){
        //alert(obj_input.selectionStart)
        //alert(obj_input.selectionEnd)
        if(obj_input.selectionStart != undefined && obj_input.selectionEnd != undefined)//for ff
        {
            var start = obj_input.selectionStart;
            var end = obj_input.selectionEnd;
            //alert(obj_input.value.substring(start, end))
            return obj_input.value.substring(start, end);
        }
        else
        {
            return document.selection.createRange().text;  // for ie
        }
    }
}
//IP地址输入框--end

