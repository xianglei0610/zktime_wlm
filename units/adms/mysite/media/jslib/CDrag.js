//创建类
var Class = {
	create : function () {
		return function () {
			this.initialize.apply(this, arguments);
		};
	}
};

//转换数组
var $A = function (a) {
	return a ? Array.apply(null, a) : new Array;
};

//追加方法
Object.extend = function (des, src) {
	for(var i in src) {
		des[i] = src[i];
	}
	return des;
};

Object.extend(Object, {
	//添加函数
	addEvent : function (obj, event_list, fun_event, pop_type) {
		if (obj.attachEvent){
			obj.attachEvent(event_list[0],fun_event);
		}
		else {
			obj.addEventListener(
				event_list[1] || event_list[0].replace(/^on/, ""), 
				fun_event, 
				pop_type || false
			);
		}
		return fun_event;
	},
	
	delEvent : function (a, b, c, d) {
		if (a.detachEvent) a.detachEvent(b[0], c);
		else a.removeEventListener(b[1] || b[0].replace(/^on/, ""), c, d || false);
		return c;
	},
	
	//获取Event	
	reEvent : function () {

		return window.event ? window.event : (function (o) {
			do {
				o = o.caller;
			} while (o && !/^\[object[ A-Za-z]*Event\]$/.test(o.arguments[0]));  //firefox
			return o.arguments[0];
		})(this.reEvent);
	}
	
});


//获取Event
Function.prototype.bind = function () {
	var wc = this;
	var a = $A(arguments);
	var o = a.shift();
	return function () {
		wc.apply(o, a.concat($A(arguments)));
	};
};

var CDrag = Class.create();

Object.extend(CDrag,{
	IE : /MSIE/.test(window.navigator.userAgent),
	//加载对象,定时刷新
	load : function (obj_string, func,time) {
		var index = 0;
		var timer = window.setInterval(function () {
			try {
				if (eval(obj_string + ".loaded")) { //判断是否加载完成
					window.clearInterval(timer);
					func(eval("new " + obj_string));
				}
			} catch (exp) {}

			if (++ index == 20) {//如果对象20秒还没有创建就关闭
				window.clearInterval(timer);
			}
				
		}, time + index * 3);	
	},
	database:	{
			//数据存储
		json : [
				{ id : "m_1_1_common_opt", title : gettext("常用操作"), className : "common_opt", src : "/media/jslib/common_panel.js" },
				
				{ id : "m_1_2_common_search", title : gettext("常用查询"), className : "common_search", src : "/media/jslib/common_panel.js" },
				
				//{ id : "m_1_3_attquickstart", title : gettext("考勤快速上手"), className : "attquickstart", src : "/media/jslib/common_panel.js" },
				
				{ id : "m_1_4_overtime_audit", title : gettext("加班单审核"), className : "overtime_audit", src : "/media/jslib/common_panel.js" },
				
				{ id : "m_1_5_specday_audit", title : gettext("请假单审核"), className : "specday_audit", src : "/media/jslib/common_panel.js" },
				
				{ id : "m_2_1_common_monitor", title : gettext("系统提醒、公告"), className : "common_monitor", src : "/media/jslib/common_panel.js" },
				
				{ id : "m_2_2_empstructure", title : gettext("人力构成分析"), className : "empstructure", src : "/media/jslib/common_panel.js" },

				{ id : "m_2_3_attrate", title : gettext("本日出勤率"), className : "attrate", src : "/media/jslib/common_panel.js" },

				{ id : "m_2_4_accquickstart", title : gettext("门禁快速上手"), className : "specday_audit", src : "/media/jslib/common_panel.js" },
				
				{ id : "m_2_5_checkexact_audit", title : gettext("补签卡审核"), className : "checkexact", src : "/media/jslib/common_panel.js" }
				
			],
		parse : function (id) {//查找资源
			var json = this.json;
			for (var i in json) {
				if (json[i].id == id){
					return json[i];
				}
			}
		}
	}

});


CDrag.Ajax = Class.create();

Object.extend(CDrag.Ajax, {

	getTransport: function() {
		var returnValue;
		var list_funs=[
			function () { return new ActiveXObject('Msxml2.XMLHTTP') }, 
			function () { return new ActiveXObject('Microsoft.XMLHTTP') }, //IE 5.0、IE 6.0中创建 XMLHttpRequest
			function () { return new XMLHttpRequest() }   //非IE浏览器中创建XMLHttpRequest
		];
		
		for (var i = 0 ; i < list_funs ; i ++) {
			try {
				returnValue = list_funs[i]();
				break;
			} catch (exp){
			}
		}
		return returnValue || false;
	}
});

CDrag.Ajax.prototype = {

	initialize : function (url) {
	//初始化
		var wc = this;
		wc.ajax = CDrag.Ajax.getTransport();
	},
	
	load : function (func) {
		var wc = this;
		var ajax = wc.ajax;
		if (ajax.readyState == 4 && ajax.status == 200){
			func(ajax.responseText);
		}
	},
	
	send : function (url, func) {
		var wc = this;
		var ajax = wc.ajax;
		var querys = url + new Date().getTime() + (10000 + parseInt(Math.random() * 10000)) +"/";
		ajax.open("get", querys, true);
		ajax.onreadystatechange = wc.load.bind(wc, func);
	//	ajax.send(null);
		
	}
	
};

CDrag.Table = Class.create();

CDrag.Table.prototype = {
//列的拖拽暂时不考虑

	initialize : function () {
	//初始化
		var wc = this;
		wc.items = []; //创建列组
	},
	
	add : function () {
	//添加列
		var tbl = this;
		var col_index = tbl.items.length;
		var  arg = arguments;
		var dom_div=arg[0];
		tbl.items[col_index] = new CDrag.Table.Cols(col_index, tbl, dom_div);
		return tbl.items[col_index];
	}
};

CDrag.Table.Cols = Class.create();

CDrag.Table.Cols.prototype = {
	
	initialize : function (id, parent, element) {
	//初始化
	    
		var wc = this;
		wc.items = []; //创建列组
		wc.id = id;
		wc.parent = parent;
		wc.element = element;
	},
	
	add : function () {
	//添加行
		var class_col = this;
		var row_index = class_col.items.length;
		var arg = arguments;
		var row_id=arg[0];
		var win=arg[1];
		var locks=arg[2];
		class_col.items[row_index] = new CDrag.Table.Rows(row_index,class_col, row_id,win,locks); 
		return class_col.items[row_index];//这一列的第几行
	},
	
	ins : function (num, row) {
	//插入行
		var wc = this, items = wc.items, i;
		
		if (row.parent == wc && row.id < num) num --; //同列向下移动的时候
		for (i = num ; i < items.length ; i ++) items[i].id ++;
		
		items.splice(num, 0, row);
		row.id = num, row.parent = wc;
		
		return row;
	},
	
	del : function (num) {
	//删除行
		var wc = this, items = wc.items, i;
		
		if (num >= items.length) return;
		for (i = num + 1; i < items.length ; i ++) items[i].id = i - 1;
		return items.splice(num, 1)[0];
	}
	
};

CDrag.Table.Rows = Class.create();

CDrag.Table.Rows.prototype = {
	initialize : function (id, parent, element, window, locks) {
	//初始化
		var wc = this;
		var temp;
		wc.id = id;
		wc.parent = parent;
		wc.root_id = element;		
		wc.window = window;
		//wc.element = wc.element_init();不初始化了，直接自己布局好html
		wc.element=document.getElementById(wc.root_id);
		//清楚空格
		var cleanWhitespace = function( element ) {
			// If no element is provided, do the whole HTML document
			element = element || document;
			
			for (var i = 0; i < element.childNodes.length; i++) {
				var node = element.childNodes[i];
				if (node.nodeType == 3 && !/\S/.test(node.nodeValue))
					element.removeChild(node);
			}
			
			for (var i = 0; i < element.childNodes.length; i++)
				cleanWhitespace( element.childNodes[i] );
		}
		cleanWhitespace(wc.element);
		
		temp = wc.element.childNodes[0];
		
		wc.title = temp.childNodes[2];
		wc.reduce = temp.childNodes[1];
		wc.close = temp.childNodes[0];
		wc.content = wc.element.childNodes[1];
		wc.Class = wc.mousedown = wc.reduceFunc = wc.closeFunc = null;
		wc.init();
		wc.load();//不去后台请求了
	},
	
	element_init : function () {
	//初始化元素
		var wc = this, div = document.getElementById("root_row").cloneNode(true);
		wc.parent.element.appendChild(div);
		div.style.display = "block";
		return div;
	},
	
	init : function () {
	//初始化信息
		var wc = this;
		if (wc.window == 0) {
			wc.content.style.display = "none";
			//wc.reduce.innerHTML = "放大";
			wc.reduce.setAttribute(CDrag.IE ? "className" : "class", "title_maximize");
			wc.reduce.setAttribute("title" , gettext("展开"));
			
		} else {
			wc.content.style.display = "block";
			//wc.reduce.innerHTML = "缩小";
			wc.reduce.setAttribute(CDrag.IE ? "className" : "class", "title_minimize");
			wc.reduce.setAttribute("title" , gettext("收缩"));
		}
	},
	
	load : function () {
	//获取相关信息

		var wc = this, info = CDrag.database.parse(wc.root_id), script;
		
		wc.title.innerHTML = info.title;
		
//		if (info.src) {
//			wc.content.innerHTML = gettext("加载中......");
//			script = document.createElement("script");
//			script.src = info.src //, script.defer = true;
//			document.getElementsByTagName("head")[0].appendChild(script);
//			
//			CDrag.load(info.className, wc.upload.bind(wc),5);
//		} else	wc.content.innerHTML = info.className;
	},
	
	upload : function (obj) {
	
		var wc = this;
		wc.Class = obj;
		wc.Class.parent = wc;
		wc.Class.open();
		
	},
	
	lockF : function () {
	//检索锁定
		var wc = this, arg = $A(arguments), root = arg.shift(), func = arg.shift();
		return function () {
			if (!wc.locks) func.apply(root, arg.concat($A(arguments)));
		};
	}
	
};

CDrag.Add = Class.create();

CDrag.Add.prototype = {
	
	initialize : function (parent) {
	//初始化参数
		var wc = this;
//		wc.div = document.createElement("div"); //最外层div
//		wc.iframe = document.createElement("iframe"); //协助wc.div盖select的iframe
		wc.node = document.createElement("div"); //内容底层div
		wc.content = document.createElement("div"); //内容层div
		wc.button = document.createElement("button"); //内容处理按钮
		wc.cancelbutton=document.createElement("button");
		wc.parent = parent;
		wc.json = null;
		
		wc.button.onclick = wc.execute.bind(wc, wc.content); //向按钮指向方法
		wc.cancelbutton.onclick=function(){
		$("#id_close",$(wc.node)).click();
		}
		wc.init_element();
	},
	
	init_element : function () {
	//初始化元素
		var wc = this;
		
//		wc.div.setAttribute(CDrag.IE ? "className" : "class", "Dall_screen");
//		wc.iframe.setAttribute(CDrag.IE ? "className" : "class", "Iall_screen");
		wc.node.setAttribute(CDrag.IE ? "className" : "class", "Nall_screen div_box");
		wc.content.setAttribute(CDrag.IE ? "className" : "class", "Call_screen");
		
		title= document.createElement("h1");
		$(title).html(gettext("自定义工作面板"));
		wc.node.appendChild(title);
		
		wc.button.innerHTML = gettext("确定");
		wc.cancelbutton.innerHTML=gettext("取消");
		wc.node.appendChild(wc.content);
		
		
		wc.node.btnDIV = document.createElement("div"); 
		wc.node.btnDIV.setAttribute(CDrag.IE ? "className" : "class", "btns_class");
		wc.node.appendChild(wc.node.btnDIV);		
		wc.node.btnDIV.appendChild(wc.button);
		wc.node.btnDIV.appendChild(wc.cancelbutton);
//		wc.node.appendChild(wc.cancelbutton);
//		wc.node.appendChild(wc.button);
	},
	
	init_json : function () {
	//初始化原始数据信息串
		var wc = this, parent = wc.parent,
			cols = parent.table.items, new_json = {}, init_json = CDrag.database.json, r, i, j;
	    		
		for (i = 0 ; i < init_json.length ; i ++) //遍历原始数据
			new_json[init_json[i].id] = { id : init_json[i].id, row : null, title : init_json[i].title };
			
		for (i = 0 ; i < cols.length ; i ++) //遍历修改生成的串的属性
			for (r = cols[i].items, j = 0 ; j < r.length ; j ++){
				new_json[r[j].root_id].row = r[j];
			}
		return new_json;
	},
	
	init_node : function () {
	//初始化内容层div的数据
		var wc = this, json = wc.json = wc.init_json(), boxary = [], i;
		for (i in json){
			boxary[boxary.length] = [
				'<input type="checkbox"', json[i].row ? 'checked="checked"' : "",
				' value="', json[i].id, '" />&nbsp;&nbsp;', json[i].title, '<br \/>'
			].join("");
        }
		wc.content.innerHTML = boxary.join(""); //写入内容层
	},
	
	execute : function (div) {
	//处理table类结构
		var wc = this, parent = wc.parent, json = wc.json, items = div.getElementsByTagName("input"), row, c, i;
		try {
		
			for (i = 0 ; i < items.length ; i ++) {
			
				if (items[i].type != "checkbox") continue;
				row = json[items[i].value];
                
				if ((!!row.row) != items[i].checked) {
					if (row.row) parent.remove(row.row); //删除
					else{ parent.add(parent.table.items[0].add(row.id, 1, false)); //向第一行追加数据
					    
					}
					//c = true;
				}
				
			}
			
			div.innerHTML = "";
			//if (c) 
			
		} catch (exp) {}
		parent.set_cookie();
		window.location.reload();
		wc.close();
	},
	
	add : function () {
	//添加数据
	    
		var wc = this
		//, div = wc.div, iframe = wc.iframe;
		wc.init_node();
//		div.style.height = iframe.style.height = Math.max(document.documentElement.scrollHeight, document.documentElement.offsetHeight) + "px";
//		div.style.width = iframe.style.width = Math.max(document.documentElement.scrollWidth, document.documentElement.offsetWidth) + "px";
		//document.getElementsByTagName("html")[0].style.overflow = "hidden";
//		document.body.appendChild(iframe);
//		document.body.appendChild(div);
		document.body.appendChild(wc.node);
		$(wc.node).dialog();  //{title:gettext("自定义工作面板")}
		//alert('1')
		//alert($(wc.node).html())
	},
	
	close : function () {
	//关闭添加框
		var wc = this
		//, div = wc.div, iframe = wc.iframe;
		document.getElementsByTagName("html")[0].style.overflow = CDrag.IE ? "" : "auto";
//		document.body.removeChild(iframe);
//		document.body.removeChild(div);
//		document.body.removeChild(wc.node);
		$("#id_close").click()
	}
	
};

CDrag.prototype = {
	
	initialize : function () {
	//初始化成员
		var wc = this;
		
		wc.table = new CDrag.Table; //建立表格对象
		wc.addc = new CDrag.Add(wc); //建立添加对象
		
		wc.iFunc = wc.eFunc = null;
		wc.obj = { on : { a : null, b : "" }, row : null, left : 0, top : 0 };
		wc.temp = { row : null, div : document.createElement("div") };
		wc.temp.div.setAttribute(CDrag.IE ? "className" : "class", "CDrag_temp_div");
		wc.temp.div.innerHTML = "&nbsp;";
	},
	
	reMouse : function (a) {
	//获取鼠标位置
		var e = Object.reEvent();
		return {
			x : document.documentElement.scrollLeft + e.clientX,
			y : document.documentElement.scrollTop + e.clientY
		};
	},
	
	rePosition : function (o) {
	//获取元素绝对位置
		var $x = $y = 0;
		do {
			$x += o.offsetLeft;
			$y += o.offsetTop;
		} while ((o = o.offsetParent)); // && o.tagName != "BODY"
		return { x : $x, y : $y };
	},
	
	execMove : function (status, on_obj, in_obj, place) {
	//处理拖拽过程细节
		var wc = this, obj = wc.obj.on, temp = wc.temp, px;
		
		obj.a = on_obj, obj.b = status;
		
		if (place == 0) {
		//向上
			px = in_obj.element.clientWidth;
			in_obj.element.parentNode.insertBefore(temp.div, in_obj.element);
		} else if (place == 1) {
		//新加入
			px = in_obj.element.clientWidth - 2;
			in_obj.element.appendChild(temp.div);
		} else {
		//向下
			px = in_obj.element.clientWidth;
			in_obj.element.parentNode.appendChild(temp.div);
		}
		
		wc.obj.left = Math.ceil(px / temp.div.offsetWidth * wc.obj.left); //处理拖拽换行后宽度变化，鼠标距离拖拽物的距离的误差.
		temp.row.style.width = temp.div.style.width = px + "px"; //处理换列后对象宽度变化
	},
	
	sMove : function (o) {
	//当拖动开始时设置参数
		
		var wc = this;
		if (o.locks || wc.iFunc || wc.eFinc) return;
		
		var mouse = wc.reMouse(), obj = wc.obj, temp = wc.temp, div = o.element, position = wc.rePosition(div);
		
		
		obj.row = o;
		obj.on.b = "me";
		obj.left = mouse.x - position.x;
		obj.top = mouse.y - position.y;
		
		temp.row = document.body.appendChild(div.cloneNode(true)); //复制预拖拽对象
		temp.row.style.width = div.clientWidth + "px";
		
		with (temp.row.style) {
		//设置复制对象
			position = "absolute";
			left = mouse.x - obj.left + "px";
			top = mouse.y - obj.top + "px";
			zIndex = 100;
			opacity = "0.3";
			filter = "alpha(opacity:30)";
		}
		
		with (temp.div.style) {
		//设置站位对象
			height = div.clientHeight + "px";
			width = div.clientWidth + "px";
		}
		

		div.parentNode.replaceChild(temp.div, div);
		
		wc.iFunc = Object.addEvent(document, ["onmousemove"], wc.iMove.bind(wc));
		wc.eFunc = Object.addEvent(document, ["onmouseup"], wc.eMove.bind(wc));
		document.onselectstart = new Function("return false");
	},
	
	iMove : function () {
	//当鼠标移动时设置参数
		var wc = this, mouse = wc.reMouse(), cols = wc.table.items, obj = wc.obj, temp = wc.temp,
			row = obj.row, div = temp.row, t_position, t_cols, t_rows, i, j;
		
		with (div.style) {
			left = mouse.x - obj.left + "px";
			top = mouse.y - obj.top + "px";
		}
		
		for (i = 0 ; i < cols.length ; i ++) {
			t_cols = cols[i];
			//if (t_cols != obj.row.parent) continue;
			t_position = wc.rePosition(t_cols.element);
			if (t_position.x < mouse.x && t_position.x + t_cols.element.offsetWidth > mouse.x) {
				if (t_cols.items.length > 0) { //如果此列行数大于0
					if (t_cols.items[0] != obj.row && wc.rePosition(t_cols.items[0].element).y + 20 > mouse.y) {
						//如果第一行不为拖拽对象并且鼠标位置大于第一行的位置即是最上。。
						//向上
						wc.execMove("up", t_cols.items[0], t_cols.items[0], 0);
					} else if (t_cols.items.length > 1 && t_cols.items[0] == row &&
						wc.rePosition(t_cols.items[1].element).y + 20 > mouse.y) {
						//如果第一行是拖拽对象而第鼠标大于第二行位置则，没有动。。
						//向上
						wc.execMove("me", t_cols.items[1], t_cols.items[1], 0);
					} else {
						for (j = t_cols.items.length - 1 ; j > -1 ; j --) {
							//重最下行向上查询
							t_rows = t_cols.items[j];
							if (t_rows == obj.row) {
								if (t_cols.items.length == 1) {
								//如果拖拽的是此列最后一行
									wc.execMove("me", t_cols, t_cols, 1);
								}
								continue;
							}
							if (wc.rePosition(t_rows.element).y < mouse.y) {
								//如果鼠标大于这行则在这行下面
								if (t_rows.id + 1 < t_cols.items.length && t_cols.items[t_rows.id + 1] != obj.row) {
									//如果这行有下一行则重这行下一行的上面插入
									wc.execMove("down", t_rows, t_cols.items[t_rows.id + 1], 0);
								} else if (t_rows.id + 2 < t_cols.items.length) {
									//如果这行下一行是拖拽对象则插入到下两行，即拖拽对象返回原位
									wc.execMove("me", null, t_cols.items[t_rows.id + 2], 0);
								} else {
									//前面都没有满足则放在最低行
									wc.execMove("down", t_rows, t_rows, 2);
								}
								return;
							}
						}
					}
				} else {
				//此列无内容添加新行
					wc.execMove("new", t_cols, t_cols, 1);
				}
			}
		}
	},
	
	eMove : function () {
	//当鼠标释放时设置参数
		var wc = this, obj = wc.obj, temp = wc.temp, row = obj.row, div = row.element, o_cols, n_cols, number;
		
		if (obj.on.b != "me") {
			number = (obj.on.b == "down" ? obj.on.a.id + 1 : 0);
			n_cols = (obj.on.b != "new" ? obj.on.a.parent : obj.on.a);
			o_cols = obj.row.parent;
			n_cols.ins(number, o_cols.del(obj.row.id));
			
			wc.set_cookie();
		}
		
		temp.div.parentNode.replaceChild(div, temp.div);
		temp.row.parentNode.removeChild(temp.row);
		delete temp.row;
		
		Object.delEvent(document, ["onmousemove"], wc.iFunc);
		Object.delEvent(document, ["onmouseup"], wc.eFunc);
		document.onselectstart = wc.iFunc = wc.eFunc = null;
		if($.browser.msie && $(div).find("canvas").length>0){
			//重绘
			var datas=$(div).find("canvas").parent().get(0).data;
			$.plot(datas[0],datas[1],datas[2]);
		}
		
	},
	
	reduce : function (o) {
	//变大变小
		var wc = this;
		if ((o.window = (o.window == 1 ? 0 : 1))) {
			o.content.style.display = "block";
			//o.reduce.innerHTML = "缩小";
			o.reduce.setAttribute(CDrag.IE ? "className" : "class", "title_minimize");
			o.reduce.setAttribute("title" , gettext("收缩"));
			
		} else {
			o.content.style.display = "none";
			//o.reduce.innerHTML = "放大";
			o.reduce.setAttribute(CDrag.IE ? "className" : "class", "title_maximize");
			o.reduce.setAttribute("title" , gettext("展开"));
		}
		wc.set_cookie();
	},
	
	lock : function (o) {
	//锁定
		var wc = this;
		if (o.locks) {
			o.locks = false;
			o.lock.innerHTML = gettext("锁定");
		} else {
			o.locks = true;
			o.lock.innerHTML = gettext("解除");
		}
		wc.set_cookie();
	},
	
	close : function (o) {
	//关闭对象
		var wc = this;
		wc.remove(o);
		wc.set_cookie();
	},
	
	remove : function (o) {
	//移除对象
		var wc = this, parent = o.parent;
		
		Object.delEvent(o.close, ["onclick"], o.closeFunc);
		Object.delEvent(o.reduce, ["onclick"], o.reduceFunc);
		Object.delEvent(o.title, ["onmousedown"], o.mousedown);
		
		o.mousedown = o.reduceFunc = o.closeFunc = null;
		$(o.element).hide();
		//parent.element.removeChild(o.element);
		parent.del(o.id);
		if (o.Class)o.Class.close(); 
		
		delete wc.Class;
		delete o;
	},
	
	create_json : function () {
	//生成json串
		var wc = this, cols = wc.table.items, a = [], b = [], i, j, r;
		for (i = 0 ; i < cols.length ; i ++) {
			for (r = cols[i].items, j = 0 ; j < r.length ; j ++)
				b[b.length] = "{id:'" + r[j].root_id + "',window:" + r[j].window + ",locks:" + r[j].locks + "}";
			a[a.length] = "cols:'" + cols[i].element.id + "',rows:[" + b.splice(0, b.length).join(",") + "]";
		}
		return escape("[{" + a.join("},{") + "}]");
	},
	
	parse_json : function (cookie) {
	//解释json成对象
		return eval("(" + cookie + ")");
	},
	
	get_cookie : function () {
	//获取COOKIE
//		var cookie_k="wdrag";
//		var reg=new RegExp(cookie_k+'=([^;]+)(?:;|$)',"ig");
//		return (reg.exec(document.cookie) || [,])[1];
		return (/wdrag=([^;]+)(?:;|$)/.exec(document.cookie) || [,])[1];
	},
	
	set_cookie : function () {
	//设置COOKIE
		var wc = this, date = new Date;
		date.setDate(date.getDate() + 365);
		document.cookie = "wdrag=" + wc.create_json() + ";expires=" + date.toGMTString();
		//document.cookie = "CDrag=" + wc.create_json() + ";expires=" + date.toGMTString();
	},
	
	del_cookie : function () {
	//删除COOKIE
		var wc = this, cookie = wc.get_cookie(), date;
		if (cookie) {
			date = new Date;
			date.setTime(date.getTime() - 1);
			document.cookie = "wdrag=" + cookie + ";expires=" + date.toGMTString();
			//document.cookie = "CDrag=" + cookie + ";expires=" + date.toGMTString();
		}
	},
	
	parse : function (o) {
	//初始化成员
		try {
			var wc = this;
			var table = wc.table;
			var cols;
			var rows;
			var div;
			for (var i = 0 ; i < o.length ; i ++) {
				div = document.getElementById(o[i].cols);
				cols = table.add(div);
				for (var j = 0 ; j < o[i].rows.length ; j ++){
					var id=o[i].rows[j].id;
					var	w=o[i].rows[j].window;
					var l=o[i].rows[j].locks;
					var var_add=cols.add(id, w, l);
				    wc.add(var_add);
				}
			}
		} catch (exp) {
			wc.del_cookie();
		}
	},
	
	add : function (o) {
	//添加对象
		var wc = this;
		
		o.mousedown = Object.addEvent(o.title, ["onmousedown"], o.lockF(wc, wc.sMove, o));
		o.reduceFunc = Object.addEvent(o.reduce, ["onclick"], o.lockF(wc, wc.reduce, o));
		o.closeFunc = Object.addEvent(o.close, ["onclick"], o.lockF(wc, wc.close, o));
		
	},
	
	append : function () {
		var wc = this;
		wc.addc.add();
	}
	
};

//如果页面中没有则删除
for(var i=0;i<CDrag.database.json.length;i++){
   var row=CDrag.database.json[i];
	if(!document.getElementById([row["id"]])){
		CDrag.database.json.splice(i,1);
		i--;
	}
}
Object.addEvent(window, ["onload"], function () {
	var wc = new CDrag;
	var cookie = wc.get_cookie();
		
	var json = cookie 
		? wc.parse_json(unescape(cookie)) 
		: [
				{	
				cols : "m_1", 
				rows : [
							{ id : "m_1_1_common_opt", window : 1, locks : false },
							{ id : "m_1_2_common_search", window : 1, locks : false },
							{ id : "m_1_3_attquickstart", window : 1, locks : false },
							{ id : "m_1_4_overtime_audit", window : 1, locks : false },
							{ id : "m_1_5_specday_audit", window : 1, locks : false }
						]
				},
				{
				cols : "m_2", 
				rows : [
							{ id : "m_2_1_common_monitor", window : 1, locks : false },
							{ id : "m_2_2_empstructure", window : 1, locks : false },
							{ id : "m_2_3_attrate", window : 1, locks : false },
							{ id : "m_2_4_accquickstart", window : 1, locks : false },
							{ id : "m_2_5_checkexact_audit", window : 1, locks : false }
						] 
				}
		 ];
	//页面中有但是json对象中没有，则删除
	var move_panels = $("div.move");
	//删除没有权限的面板
	for(var i=0;i<json.length;i++){
	   var row=json[i]["rows"];
	   var col=json[i]["cols"];
	   for(var j=0;j<row.length;j++){
			var id = row[j]["id"];
			var flag=true;
			 for(var k in CDrag.database.json){
			    if(CDrag.database.json[k]["id"]==id){
					flag=false;
					continue;
				}	
			 }
			if(flag){
				row.splice(j,1);
				j--;
			}else{
				for(var k=0;k<move_panels.length;k++){
					var elem=move_panels.eq(k);
					if (elem.attr("id")==id){
						move_panels.splice(k,1);
						k--;
					}
				}
				
			}

			$("#"+col).append($("#"+id));//面板排序
	   }
		 
	}
	move_panels.hide();
	wc.parse(json);
	
	(function (wc) {
		
		document.getElementById("DEL_CDrag").onclick = function () {
			wc.del_cookie();
			window.location.reload();
		};
		
		document.getElementById("ADD_CDrag").onclick = function () {
			wc.append();
		};
		
	})(wc);

	wc = null;
});
