(function (jQuery){
/*
 * jQuery Plugin - Messager
 * Author: corrie	Mail: corrie@sina.com	Homepage: www.corrie.net.cn
 * Copyright (c) 2008 corrie.net.cn
 * @license http://www.gnu.org/licenses/gpl.html [GNU General Public License]
 *
 * $Date: 2008-08-30 
 * $Vesion: 1.1
 @ how to use and example: Please Open demo.html
 */
	this.version = '@1.1';
	this.layer = {'width' : 200, 'height': 100};
	this.title = gettext('信息提示');
	this.time = 4000;//默认显示4s--Darcy
	this.anims = {'type' : 'slide', 'speed' : 600};
    this.immediate = false;
	
	this.inits = function(title, text){
		if($("#message").is("div")){ return; }
		$(document.body).prepend('<div id="message" style="border:#b9c9ef 1px solid;z-index:100;width:'+this.layer.width+'px;height:'+this.layer.height+'px;position:absolute; display:none;background:#cfdef4; bottom:0; right:0;">'
                                    +'<div id="message_up" style="border:1px solid #fff;border-bottom:none;width:100%;font-size:12px;color:#1f336b;">'
                                        +'<span id="message_close" style="float:right;padding:5px 0 5px 0;width:16px;line-height:auto;color:red;font-size:12px;font-weight:bold;text-align:center;cursor:pointer;">X</span>'
                                        +'<div id="message_title" style="padding:2px 0 5px 5px;width:100px;line-height:18px;text-align:left;">'+title+'</div><div style="clear:both;"></div>'
                                    +'</div>'
                                    +'<div id="message_down" style="padding-bottom:5px;border:1px solid #fff;border-top:none;width:100%;height:200px;font-size:12px;">'
                                        +'<div id="message_content" style="margin:0 5px 0 5px;border:#b9c9ef 1px solid;padding:5px 0 5px 5px;font-size:12px;width:'+(this.layer.width-17)+'px;height:'+(this.layer.height-50)+'px;color:#1f336b;text-align:left;">'+text+'</div>'
                                    +'</div>'
                                +'</div>');
	};
	this.show = function(title, text, time){
		if($("#message").is("div"))
        { 
            return;
        }
		if(title==0 || !title)
        {
            title = this.title;
        }
		this.inits(title, text);
		if(time)
        {
            this.time = time;
        }
		switch(this.anims.type)
        {
			case 'slide':
                $("#message").slideDown(this.anims.speed);
                break;
			case 'fade':
                $("#message").fadeIn(this.anims.speed);
                break;
			case 'show':
                $("#message").show(this.anims.speed);
                break;
			default:
                $("#message").slideDown(this.anims.speed);
                break;
		}
		$("#message_close").click(function(){		
			setTimeout('this.close()', 1);
		});
		//$("#message").slideDown('slow');
        if(time)//修改为不配置time时一直显示
        {
            this.rmmessage(this.time);
        }
	};
	this.lays = function(width, height){
		if($("#message").is("div"))
        { 
            return; //避免重复
        }
		if(width!=0 && width)
        {
            this.layer.width = width;
        }
		if(height!=0 && height)
        {
            this.layer.height = height;
        }
	}
	this.anim = function(type,speed){
		if($("#message").is("div"))
        { 
            return;
        }
		if(type!=0 && type)
        {
            this.anims.type = type;
        }
		if(speed!=0 && speed){
			switch(speed){
				case 'slow' : ;break;
				case 'fast' : 
                    this.anims.speed = 200; 
                    break;
				case 'normal' : 
                    this.anims.speed = 400; 
                    break;
				default:					
					this.anims.speed = speed;
			}			
		}
	}
	this.rmmessage = function(time){
		setTimeout('this.close()', time);
		//setTimeout('$("#message").remove()', time+1000);
	};
	this.close = function(immediate){
		switch(this.anims.type){
			case 'slide':
                $("#message").slideUp(this.anims.speed);
                break;
			case 'fade':
                $("#message").fadeOut(this.anims.speed);
                break;
			case 'show':
                $("#message").hide(this.anims.speed);
                break;
			default:
                $("#message").slideUp(this.anims.speed);
                break;
		};
        if(immediate)
        {
            $("#message").remove();
        }
        else
        {
            setTimeout('$("#message").remove();', this.anims.speed);
        }
		//this.original();
	};
	this.original = function(){	
		this.layer = {'width' : 200, 'height': 100};
		this.title = '信息提示';
		this.time = 4000;
		this.anims = {'type' : 'slide', 'speed' : 600};
        this.immediate = false;
	};
    jQuery.messager = this;
    return jQuery;
})(jQuery);