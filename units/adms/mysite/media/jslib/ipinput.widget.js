//IP地址输入框--start
function IpV4Box(id,pNode,type){
    this.id = id;
    this.onChange=new Function();
    this.onEnterKey=new Function();
    this.disabled=false;
   
    IpV4Box.all[id]=this;
    if(pNode)
    {
        if(typeof pNode=="string")
        {
            pNode=document.getElementById(pNode);
        }
        pNode.innerHTML=this.toString(type);
    }
}
IpV4Box.all={};

IpV4Box.EnabledClassName="";//启用时样式
IpV4Box.DisabledClassName="ipInput oneInputDisabled";// 禁用时样式

IpV4Box.prototype={
    focus:function(index){
        if(!index)
        {
            index=1;
        }
        document.getElementById(this.id+"_"+index).focus();
    },
    setEnable:function(bEnable){
        var b=bEnable;
        this.disabled=bEnable;
        var boxes=document.getElementById(this.id).getElementsByTagName("input");
        for(var i=0;i<boxes.length;i++)
        {
            boxes[i].readOnly=b;
        }
        document.getElementById(this.id).className=bEnable?IpV4Box.EnabledClassName:IpV4Box.DisabledClassName
    },
    toString:function(type){
        return '<span id="'+this.id+'" style="border: 1px solid rgb(141, 182, 205);" class="' + IpV4Box.EnabledClassName + '" >\
            <input style="border:0px none;" onkeypress="IpV4Box.evt.keypress(this,event)" onkeydown="IpV4Box.evt.keydown(this,event)" onfocus="IpV4Box.evt.focus(this,event)" onpaste="IpV4Box.evt.change(this,event);" oninput="IpV4Box.evt.change(this,event);" onchange="IpV4Box.evt.change(this,event);" onblur="IpV4Box.evt.blur(this,event,'+type+');" type="text" size=1 id="'+this.id+'_1" maxlength=3\
            />.<input style="border:0px none;" onkeypress="IpV4Box.evt.keypress(this,event)" onkeydown="IpV4Box.evt.keydown(this,event)" onfocus="IpV4Box.evt.focus(this,event)" onpaste="IpV4Box.evt.change(this,event);" oninput="IpV4Box.evt.change(this,event);" onchange="IpV4Box.evt.change(this,event);" type="text" size=1 id="'+this.id+'_2" maxlength=3\
            />.<input style="border:0px none;" onkeypress="IpV4Box.evt.keypress(this,event)" onkeydown="IpV4Box.evt.keydown(this,event)" onfocus="IpV4Box.evt.focus(this,event)" onpaste="IpV4Box.evt.change(this,event);" oninput="IpV4Box.evt.change(this,event);" onchange="IpV4Box.evt.change(this,event);" type="text" size=1 id="'+this.id+'_3" maxlength=3\
            />.<input style="border:0px none;" onkeypress="IpV4Box.evt.keypress(this,event)" onkeydown="IpV4Box.evt.keydown(this,event)" onfocus="IpV4Box.evt.focus(this,event)" onpaste="IpV4Box.evt.change(this,event);" oninput="IpV4Box.evt.change(this,event);" onchange="IpV4Box.evt.change(this,event);" type="text" size=1 id="'+this.id+'_4" maxlength=3/>\
        </span>';
    },
    getValue:function(){
        var ip=[
            document.getElementById(this.id+"_1").value,
            document.getElementById(this.id+"_2").value,
            document.getElementById(this.id+"_3").value,
            document.getElementById(this.id+"_4").value
        ];
        return ip.join(".");
       
    },
    setValue:function(ip){
        ip=ip.replace(/[^\d.]/g,"");
        if(ip=="")
        {
            ip="..."
        }
        ip=ip.split(".");
        document.getElementById(this.id+"_1").value = ip[0];
        document.getElementById(this.id+"_2").value = ip[1];
        document.getElementById(this.id+"_3").value = ip[2];
        document.getElementById(this.id+"_4").value = ip[3];
    }
}

IpV4Box.evt={
    focus:function(obj,evt){
        obj.select();
    },
    blur:function(obj,evt,type){
        if(type == 0)
        {
            return;
        }
        var value=obj.value;
        if(parseInt(value,10)>223 ||(parseInt(value,10)==0))
        {
            if(evt.preventDefault)
            {
                evt.preventDefault();
            }
            evt.returnValue=false;

            alert(gettext("请选择一个介于1到223之间的数值！"));
            if(parseInt(obj.value,10)<1)
            {
                obj.value="1";
            }
            else
            {
                obj.value="223";
            }
            return;
            
            return;
        }
        
    },
    change:function(obj,evt){
        var v=parseInt(obj.value,10);
        if( v >= 0 && v <= 255 )
        {
            if(v != obj.value)
            {
                obj.value=v;
            }
        }
        else
        {
            obj.value="";
        }
   
        IpV4Box.all[ obj.id.replace(/_\d$/,"") ].onChange();
    },
    keypress:function(obj,evt,type){
        var key=evt.charCode||evt.keyCode;
        var pos=IpV4Box.evt.getSelection(obj);
        var value=obj.value;
        var c=String.fromCharCode(key);
        if(key>=48 && key<=57)
        {
            value=""+value.substring(0,pos.start)
                + c + value.substring(pos.end,value.length);
           
            if(parseInt(value,10)<=255)
            {
                var id=obj.id;
                /(.*)_(\d)$/.test(id);
                var index = RegExp.$2;
                IP_id = RegExp.$1;
               
                if(value.length==3)
                {
                    if(parseInt(index,10)<4)
                    {
                        id=id.replace(/(\d)$/,parseInt(index,10)+1 );
                        setTimeout("document.getElementById('"+id+"').focus();"+
                            "document.getElementById('"+id+"').select();",200);
                    }
                }
                setTimeout("IpV4Box.all['"+IP_id+"'].onChange()",0);
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
    keydown:function(obj,evt,type){
        var key=evt.charCode||evt.keyCode;
		///alert(key+"------key");
        var pos=IpV4Box.evt.getSelection(obj);
        var value=obj.value;
        var c=String.fromCharCode(key);
        var id=obj.id;
        /^(.*)_(\d)$/.test(id);
        var index=RegExp.$2;
        var Ip_Id=RegExp.$1;
        switch(key)
        {
            case 13://回车
                IpV4Box.all[Ip_Id].onEnterKey();   
                break;       

            case 110://.小键盘
            case 190://.主键盘
            case 9:  //制表符
                
                if(index<4 && value!="")
                {
                    id=id.replace(/(\d)$/,parseInt(index,10)+1 );
                    document.getElementById(id).focus();
                    document.getElementById(id).select();
                }
                break;
            case 8://backspace
                //alert((navigator.userAgent.indexOf("Firefox")>0)+"----firefox");
                if(navigator.userAgent.indexOf("Firefox")>0){
                    if(obj.readOnly==true)
                    {
                        return;
                    }
                    if(pos.start>=0)
                    {
                        if (obj.value.length>0)
                        {
                            var a=new Array(obj.value.length-1);
                            for (var i=0;i<obj.value.length-1;i++ )
                            {
                                a[i]=obj.value.charAt(i);
                            }
                            obj.value=a.join("");
                        }
                        else
                        {
                            if(index == 1){return;}
                            id=id.replace(/(\d)$/,parseInt(index,10)-1 );
                            document.getElementById(id).focus();
                            document.getElementById(id).select();				
                        }
                        return;
                    }
                }
                else
                {
                    if(pos.start>0)
                    {
                        return;
                    }
                }
            case 37://left
                if(pos.end==0 && index>1)
                {
                    id=id.replace(/(\d)$/,parseInt(index,10)-1 );
                    document.getElementById(id).focus();
                    document.getElementById(id).select();
                }
                break;
            case 39://right
                if(pos.start==value.length && index<4)
                {
                    id=id.replace(/(\d)$/,parseInt(index,10)+1 );
                    document.getElementById(id).focus();
                    document.getElementById(id).select();
                }
                break;
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
    }
}
//IP地址输入框--end

