
$(function(){
	//filter list by app
	var list_n=$("#id_help_mainLeft>div[ID]");
	var j=0,h="";
	for(var i=0;i<=list_n.length;i++){
		if($("#id_appData:contains("+list_n.eq(i).attr('ID')+")").length != 1){
			list_n.eq(i).css({display:"none"});			
		}else{
			j++;
			h=h+ list_n.eq(i).attr('ID')+" ";
		}
	}
	if(j==1){
		$(".help_mainContainer").addClass(h.substr(7));
		$('#main').load(function(){   
			$('#main').contents().find(".help_mainContant").addClass(h.substr(7));  
		});  
	}else{
		$(".help_mainContainer").addClass("zkeco");
		$('#main').load(function(){   
			$('#main').contents().find(".help_mainContant").addClass("zkeco");  
		});  
	}
	//focus left list
	var list_p=$(".help_title_corner").find(".inner").find("p");
	var gvar={};	
	var list_a=$(".help_title_corner").find(".inner>ul").find("li>a");
	var avar={};
	gvar.click_row=list_p.eq(0);
	list_p.click(function(){
		if($(this).parent().parent().hasClass("corner_focus")){
			$(this).parent().parent().removeClass("corner_focus");
		}else{
			$(this).parent().parent().addClass("corner_focus");
		}
		if(gvar.click_row && gvar.click_row.get(0)!=this){
			gvar.click_row.parent().parent().removeClass("corner_focus");
		}
		gvar.click_row=$(this);		
	})
	list_a.click(function(){
		$(this).addClass("list_focus");
		if(avar.click_a && avar.click_a.get(0)!= this){
			avar.click_a.removeClass("list_focus");
		}
		avar.click_a=$(this);
	})
	
	//displays the help of current page in the help center
	if($("#id_model_address").text() != ""){
		var page_url=$("#id_model_address").text().split("/")[4];
		for(var i=0;i<$(".ul_help_list>li").find("a").length;i++){			
			var link_a=$(".ul_help_list>li").find("a").eq(i);
			var link_url=link_a.attr("href").split("/")[3];
			if(page_url == link_url){				
				link_a.bind("click",
					function(){
						$("#main").attr("src",link_a.attr("href"));
						return false;
					});
				link_a.parents("div.inner").find("p").trigger("click");
				link_a.click();
				break;
			}
		}
		$("#id_model_address").remove();
	}else{
		$("#main").attr("src","/file/help_en/index.html");
	}
})

//goTop
function stat(){ 
var a = pageYOffset+window.innerHeight-0 
$("#bar").top = a 
setTimeout('stat()',2) 
} 
function fix(){ 
nome=navigator.appName 
if(nome=='Netscape'){ 
stat() 
} 
else{ 
var a=document.body.scrollTop+document.body.clientHeight-document.all.bar.offsetHeight+0 
bar.style.top = a 
}} 

	//close btn
	function closeHelp(){
		var truthBeTold = window.confirm("Are you sure to close this page?");			
		if(truthBeTold){
			window.close()
		}else{				
		}
	}
	//colseGoTop btn
	function GoTop_down(){
		$("#bar").css({height:"7px"});
		$(".help_goTop_down").hide();
		$(".help_goTop_up").css({display:"block"});
		$(".help_goTop").addClass("help_goTop_bgDown");
		fix();
	}
	function GoTop_up(){
		$("#bar").css({height:"33px"});
		$(".help_goTop_up").hide();
		$(".help_goTop_down").css({display:"block"});
		$(".help_goTop").removeClass("help_goTop_bgDown");
		fix();
	}
	
// iframe height
function setIframeHeight(obj)
{
  var iframe = obj;
  if (document.getElementById)
  {
    if (iframe && !window.opera)
    {              
		if (iframe.contentDocument && iframe.contentDocument.body.offsetHeight)
		{
			iframe.height = iframe.contentDocument.body.offsetHeight+20;                       
		}
		else if(iframe.Document && iframe.Document.body.scrollHeight)
		{
			iframe.height = iframe.Document.body.scrollHeight+20;                       
		}               
    }
  }
}
function iframeload(obj)
{
	//interval = setInterval("setIframeHeight(document.getElementById('main'))",10);
	//setTimeout("clearInterval(interval);",1000); //"1000" is the time of the page load		
}
