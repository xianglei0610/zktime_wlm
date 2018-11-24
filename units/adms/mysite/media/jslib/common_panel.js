var common_opt = Class.create();

common_opt.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		$.ajax({
			type:"GET",
			dataType:"html",
			url:"../../worktable/common_op/",
			success:function(msg){
				$(wc.parent.content).html(msg);
			},
			error:function (XMLHttpRequest, textStatus, errorThrown){
				alert(XMLHttpRequest+","+textStatus+","+errorThrown);
			}
		});
//		wc.repeatLoad = window.setInterval(function () {
//			ajax.send("../../worktable/common/", wc.load.bind(wc));
//		},2000)
	},
	close : function(){
		var wc =this;
		if ( wc.repeatLoad){
			window.clearInterval(wc.repeatLoad);
		}
	}
	
};
common_opt.loaded=true;

// 其中open,close函数 ,loaded属性必须要有
var common_search = Class.create();

common_search.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		$.ajax({
			type:"GET",
			dataType:"html",
			url:"../../worktable/common_search/",
			async:false,
			success:function(msg){
				$(wc.parent.content).html(msg);
			},
			error:function (XMLHttpRequest, textStatus, errorThrown){
				alert(XMLHttpRequest+","+textStatus+","+errorThrown);
			}
		});
//		wc.repeatLoad = window.setInterval(function () {
//			ajax.send("../../worktable/common/", wc.load.bind(wc));
//		},2000)
	},
	close : function(){
		var wc =this;
		if ( wc.repeatLoad){
			window.clearInterval(wc.repeatLoad);
		}
	}
	
};
common_search.loaded=true; 


// 其中open,close函数 ,loaded属性必须要有
var common_monitor = Class.create();

common_monitor.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		$.ajax({
			type:"GET",
			dataType:"html",
			url:"../../worktable/common_monitor/",
			async:false,
			success:function(msg){
				$(wc.parent.content).html(msg);
			},
			error:function (XMLHttpRequest, textStatus, errorThrown){
				alert(XMLHttpRequest+","+textStatus+","+errorThrown);
			}
		});
//		wc.repeatLoad = window.setInterval(function () {
//			ajax.send("../../worktable/common/", wc.load.bind(wc));
//		},2000)
	},
	close : function(){
		var wc =this;
		if ( wc.repeatLoad){
			window.clearInterval(wc.repeatLoad);
		}
	}
	
};
common_monitor.loaded=true; 

var accquickstart = Class.create();

accquickstart.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		wc.parent.content.innerHTML = gettext("加载中......");
        $.ajax({
                type:"GET",
                dataType:"html",
                url:"../../worktable/accquickstart/",
                success:function(msg){
                    
                    $(wc.parent.content).html(msg);
                },
                error:function (XMLHttpRequest, textStatus, errorThrown){
                    alert(XMLHttpRequest+","+textStatus+","+errorThrown);
                }
            });
        
		
	
	},
	close : function(){
		
	}
	
};
accquickstart.loaded=true; 
var attquickstart = Class.create();

attquickstart.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		wc.parent.content.innerHTML = gettext("加载中......");
        $.ajax({
                type:"GET",
                dataType:"html",
                url:"../../worktable/attquickstart/",
                success:function(msg){
                    
                    $(wc.parent.content).html(msg);
                },
                error:function (XMLHttpRequest, textStatus, errorThrown){
                    alert(XMLHttpRequest+","+textStatus+","+errorThrown);
                }
            });
        
		
	
	},
	close : function(){
		
	}
	
};
attquickstart.loaded=true; 

var attrate = Class.create();

attrate.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		wc.parent.content.innerHTML = gettext("加载中......");
        $.ajax({
                type:"GET",
                dataType:"html",
                url:"../../worktable/attrate/",
                success:function(msg){
                    $(wc.parent.content).html(msg);
                },
                error:function (XMLHttpRequest, textStatus, errorThrown){
                    alert(XMLHttpRequest+","+textStatus+","+errorThrown);
                }
            });
        
		
	
	},
	close : function(){
		
	}
	
};
attrate.loaded=true; 

var empstructure = Class.create();

empstructure.prototype = {
	
	initialize : function () {
		var wc = this;
		wc.parent = null;
		wc.ajax = new CDrag.Ajax;
		wc.repeatLoad = null;
	},
	
	load : function (json) {
		var wc = this;
		wc.parent.content.innerHTML = json;
	},
	
	open : function () {
		var wc = this, ajax = wc.ajax;
		wc.parent.content.innerHTML = gettext("加载中......");
        $.ajax({
                type:"GET",
                dataType:"html",
                url:"../../worktable/empstructure/",
                success:function(msg){
                    $(wc.parent.content).html(msg);
                },
                error:function (XMLHttpRequest, textStatus, errorThrown){
                    alert(XMLHttpRequest+","+textStatus+","+errorThrown);
                }
            });
        
		
	
	},
	close : function(){
		
	}
	
};
empstructure.loaded=true; 
