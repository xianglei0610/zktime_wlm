/**
 * reference dwz.util.date.js
 * @author ZhangHuihua@msn.com
 * 
 */
(function($){
	
	$.setRegional = function(key, value){
		if (!$.regional) $.regional = {};
		$.regional[key] = value;
	};
	
	var DWZ = {
		keyCode: {
			ENTER: 13, ESC: 27, END: 35, HOME: 36,
			SHIFT: 16, TAB: 9,
			LEFT: 37, RIGHT: 39, UP: 38, DOWN: 40,
			DELETE: 46, BACKSPACE:8
		}
	}
	$.setRegional("datepicker", {
		dayNames: ['日', '一', '二', '三', '四', '五', '六'],
		monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
	});

	$.fn.datepicker = function(opts){
		var setting = {
			box$:"#calendar",
			year$:"#calendar [name=year]", month$:"#calendar [name=month]",
			tmInputs$:"#calendar .time :input[type='text']", hour$:"#calendar .time .hh", minute$:"#calendar .time .mm", second$:"#calendar .time .ss",
			tmBox$:"#calendar .tm", tmUp$:"#calendar .time .up", tmDown$:"#calendar .time .down",
			close$:"#calendar .close", calIcon$:"a.inputDateButton",
			main$:"#calendar .main", days$:"#calendar .days", dayNames$:"#calendar .dayNames",
			clearBut$:"#calendar .clearBut", okBut$:"#calendar .okBut",nowBut$:"#calendar .nowBut"
		};

		function changeTmMenu(sltClass){
			var $tm = $(setting.tmBox$);
			$tm.removeClass("hh").removeClass("mm").removeClass("ss");
			if (sltClass) {
				$tm.addClass(sltClass);
				$(setting.tmInputs$).removeClass("slt").filter("." + sltClass).addClass("slt");
			}
		}
		function clickTmMenu($input, type){
			$(setting.tmBox$).find("."+type+" li").each(function(){
				var $li = $(this);
				$li.click(function(){
					$input.val($li.text());
				});
			});
		}
		function keydownInt(e){
			if (!((e.keyCode >= 37 && e.keyCode <= 40)||(e.keyCode >= 48 && e.keyCode <= 57)||e.keyCode==9||(e.keyCode >= 96 && e.keyCode <= 105) || (e.keyCode == DWZ.keyCode.DELETE || e.keyCode == DWZ.keyCode.BACKSPACE))) { return false; }
		}
		function changeTm($input, type){
			var ivalue = parseInt($input.val()), istart = parseInt($input.attr("start")) || 0, iend = parseInt($input.attr("end"));
			var istep = parseInt($input.attr('step') || 1);
			if (type == 1) {
				if (ivalue <= iend-istep){$input.val(ivalue + istep);}
			} else if (type == -1){
				if (ivalue >= istart+istep){$input.val(ivalue - istep);}
			} else if (ivalue > iend) {
				$input.val(iend);
			} else if (ivalue < istart) {
				$input.val(istart);
			}
		}
				
		return this.each(function(){
			var $this = $(this);
			var dp = new Datepicker($this.val(), opts);
			
			function generateCalendar(dp){
				var dw = dp.getDateWrap();
				var minDate = dp.getMinDate();
				var maxDate = dp.getMaxDate();

				var monthStart = new Date(dw.year,dw.month-1,1);
				var startDay = monthStart.getDay();
				var dayStr="";
				if (startDay > 0){
					monthStart.setMonth(monthStart.getMonth() - 1);
					var prevDateWrap = dp.getDateWrap(monthStart);
					for(var t=prevDateWrap.days-startDay+1;t<=prevDateWrap.days;t++) {
						var _date = new Date(dw.year,dw.month-2,t);
						var _ctrClass = (_date >= minDate && _date <= maxDate) ? '' : 'disabled';
						dayStr+='<dd class="other '+_ctrClass+'" chMonth="-1" day="' + t + '">'+t+'</dd>';
					}
				}
				for(var t=1;t<=dw.days;t++){
					var _date = new Date(dw.year,dw.month-1,t);
					var _ctrClass = (_date >= minDate && _date <= maxDate) ? '' : 'disabled';
					if(t==dw.day){
						dayStr+='<dd class="slt '+_ctrClass+'" day="' + t + '">'+t+'</dd>';
					}else{
						dayStr+='<dd class="'+_ctrClass+'" day="' + t + '">'+t+'</dd>';
					}
				}
				for(var t=1;t<=42-startDay-dw.days;t++){
					var _date = new Date(dw.year,dw.month,t);
					var _ctrClass = (_date >= minDate && _date <= maxDate) ? '' : 'disabled';
					dayStr+='<dd class="other '+_ctrClass+'" chMonth="1" day="' + t + '">'+t+'</dd>';
				}
				
				var $days = $(setting.days$).html(dayStr).find("dd");
				$days.not('.disabled').click(function(){
					var $day = $(this);
					
					if (!dp.hasTime()) {
						$this.val(dp.formatDate(dp.changeDay($day.attr("day"), $day.attr("chMonth"))));
						closeCalendar(); 
						$this.change() // 扩展,调用 绑定 日期控件的change 方法
					} else {
						$days.removeClass("slt");
						$day.addClass("slt");
					}
				});

				if (!dp.hasDate()) $(setting.main$).addClass('nodate'); // 仅时间，无日期
				
				if (dp.hasTime()) {
					$("#calendar .time").show();
					
					var $hour = $(setting.hour$).val(dw.hour).focus(function(){
						changeTmMenu("hh");
					});
					var iMinute = parseInt(dw.minute / dp.opts.mmStep) * dp.opts.mmStep;
					var $minute = $(setting.minute$).val(iMinute).attr('step',dp.opts.mmStep).focus(function(){
						changeTmMenu("mm");
					});
					var $second = $(setting.second$).val(dp.hasSecond() ? dw.second : 0).attr('step',dp.opts.ssStep).focus(function(){
						changeTmMenu("ss");
					});
					
					$hour.add($minute).add($second).click(function(){return false});
					
					clickTmMenu($hour,"hh");
					clickTmMenu($minute,"mm");
					clickTmMenu($second,"ss");
					$(setting.box$).click(function(){
						changeTmMenu();
					});
					
					var $inputs = $(setting.tmInputs$);
					$inputs.keydown(keydownInt).each(function(){
						var $input = $(this);
						$input.keyup(function(){
							changeTm($input, 0);
						});
					});
					$(setting.tmUp$).click(function(){
						$inputs.filter(".slt").each(function(){
							changeTm($(this), 1);
						});
					});
					$(setting.tmDown$).click(function(){
						$inputs.filter(".slt").each(function(){
							changeTm($(this), -1);
						});
					});
					
					if (!dp.hasHour()) $hour.attr("disabled",true);
					if (!dp.hasMinute()) $minute.attr("disabled",true);
					if (!dp.hasSecond()) $second.attr("disabled",true);
				}
				
			}
			
			function closeCalendar() {
				$(setting.box$).remove();
				$(document).unbind("click", closeCalendar);
			}

			$this.click(function(event){
				closeCalendar();
				var dp = new Datepicker($this.val(), opts);
				var offset = $this.offset();
				var iTop = offset.top+this.offsetHeight;
				var temp = '';
				temp+='<div id="calendar">';
				temp+='	<div class="main">';
				temp+='		<div class="head">';
				temp+='			<table width="100%" border="0" cellpadding="0" cellspacing="2">';
				temp+='			<tr>';
				temp+='				<td><select name="year"></select></td>';
				temp+='				<td><select name="month"></select></td>';
				temp+='				<td width="20"><span class="close">×</span></td>';
				temp+='			</tr>';
				temp+='			</table>';
				temp+='		</div>';
				temp+='		<div class="body">';
				temp+='			<dl class="dayNames"><dt>日</dt><dt>一</dt><dt>二</dt><dt>三</dt><dt>四</dt><dt>五</dt><dt>六</dt></dl>';
				temp+='			<dl class="days">日期列表选项</dl>';
				temp+='			<div style="clear:both;height:0;line-height:0"></div>';
				temp+='		</div>';
				temp+='		<div class="foot">';
				temp+='			<table class="time">';
				temp+='				<tr>';
				temp+='					<td>';
				temp+='						<input type="text" class="hh" maxlength="2" start="0" end="23"/>:';
				temp+='						<input type="text" class="mm" maxlength="2" start="0" end="59"/>:';
				temp+='						<input type="text" class="ss" maxlength="2" start="0" end="59"/>';
				temp+='					</td>';
				temp+='					<td><ul><li class="up">&and;</li><li class="down">&or;</li></ul></td>';
				temp+='				</tr>';
				temp+='			</table>';
				temp+='			<button type="button" class="nowBut">当前</button>';
				temp+='			<button type="button" class="clearBut">清空</button>';
				temp+='			<button type="button" class="okBut">确定</button>';
				temp+='		<div>';
				temp+='		<div class="tm">';
				temp+='			<ul class="hh">';
				temp+='				<li>0</li>';
				temp+='				<li>1</li>';
				temp+='				<li>2</li>';
				temp+='				<li>3</li>';
				temp+='				<li>4</li>';
				temp+='				<li>5</li>';
				temp+='				<li>6</li>';
				temp+='				<li>7</li>';
				temp+='				<li>8</li>';
				temp+='				<li>9</li>';
				temp+='				<li>10</li>';
				temp+='				<li>11</li>';
				temp+='				<li>12</li>';
				temp+='				<li>13</li>';
				temp+='				<li>14</li>';
				temp+='				<li>15</li>';
				temp+='				<li>16</li>';
				temp+='				<li>17</li>';
				temp+='				<li>18</li>';
				temp+='				<li>19</li>';
				temp+='				<li>20</li>';
				temp+='				<li>21</li>';
				temp+='				<li>22</li>';
				temp+='				<li>23</li>';
				temp+='			</ul>';
				temp+='			<ul class="mm">';
				temp+='				<li>0</li>';
				temp+='				<li>5</li>';
				temp+='				<li>10</li>';
				temp+='				<li>15</li>';
				temp+='				<li>20</li>';
				temp+='				<li>25</li>';
				temp+='				<li>30</li>';
				temp+='				<li>35</li>';
				temp+='				<li>40</li>';
				temp+='				<li>45</li>';
				temp+='				<li>50</li>';
				temp+='				<li>55</li>';
				temp+='			</ul>';
				temp+='			<ul class="ss">';
				temp+='				<li>0</li>';
				temp+='				<li>10</li>';
				temp+='				<li>20</li>';
				temp+='				<li>30</li>';
				temp+='				<li>40</li>';
				temp+='				<li>50</li>';
				temp+='			</ul>';
				temp+='		</div>';
				temp+='	</div>';
				temp+='</div>';


				$(temp).appendTo("body").css({
					left:offset.left+'px',
					top:iTop+'px'
				}).show().click(function(event){
					event.stopPropagation();
				});
				
				($.fn.bgiframe && $(setting.box$).bgiframe());
				
				var dayNames = "";
				$.each($.regional.datepicker.dayNames, function(i,v){
					dayNames += "<dt>" + v + "</dt>"
				});
				$(setting.dayNames$).html(dayNames);
				
				var dw = dp.getDateWrap();
				var $year = $(setting.year$);
				var yearstart = dp.getMinDate().getFullYear();
				var yearend = dp.getMaxDate().getFullYear();
				for(y=yearstart; y<=yearend; y++){
					$year.append('<option value="'+ y +'"'+ (dw.year==y ? 'selected="selected"' : '') +'>'+ y +'</option>');
				}
				var $month = $(setting.month$);
				$.each($.regional.datepicker.monthNames, function(i,v){
					var m = i+1;
					$month.append('<option value="'+ m +'"'+ (dw.month==m ? 'selected="selected"' : '') +'>'+ v +'</option>');
				});
				
				// generate calendar
				generateCalendar(dp);
				$year.add($month).change(function(){
					dp.changeDate($year.val(), $month.val());
					generateCalendar(dp);
				});
				
				// fix top
				var iBoxH = $(setting.box$).outerHeight(true);
				if (iTop > iBoxH && iTop > $(window).height()-iBoxH) {
					$(setting.box$).css("top", offset.top - iBoxH);
				}
				
				$(setting.close$).click(function(){
					closeCalendar();
				});
				$(setting.clearBut$).click(function(){
					$this.val("");
					closeCalendar();
				});
				
				$(setting.okBut$).click(function(){
					var $dd = $(setting.days$).find("dd.slt");
					
					if ($dd.hasClass("disabled")) return false;
					
					var date = dp.changeDay($dd.attr("day"), $dd.attr("chMonth"));
					if (dp.hasDate){
						date.setYear(parseInt($(setting.year$).val()));
						date.setMonth(parseInt($(setting.month$).val()-1))
					}
					if (dp.hasTime()) {
					 	date.setHours(parseInt($(setting.hour$).val()));
						date.setMinutes(parseInt($(setting.minute$).val()));
						date.setSeconds(parseInt($(setting.second$).val()));
					}
					
					$this.val(dp.formatDate(date));
					closeCalendar();
					$this.change() // 扩展,调用 绑定 日期控件的change 方法
				});
				
				$(setting.nowBut$).click(function(){
					var nowDate = new Date();
					var dp = new Datepicker(nowDate.formatDate("yyyy-MM-dd HH:mm:ss"), opts);
					$(setting.year$).val(nowDate.getFullYear());
					$(setting.month$).val(nowDate.getMonth()+1);
					generateCalendar(dp);
				});
				$(document).bind("click", closeCalendar);
				$("#id_model_extend a").bind("click",closeCalendar );
				return false;
			});
			
			$this.parent().find(setting.calIcon$).click(function(){
				$this.trigger("click");
				return false;
			});
		});
		
	}

	var Datepicker = function(sDate, opts) {
		this.opts = $.extend({
			pattern:'yyyy-MM-dd',
			minDate:"1900-01-01",
			maxDate:"2099-12-31",
			mmStep:1,
			ssStep:1
		}, opts);
		
		//动态minDate、maxDate
		var now = new Date();
		this.opts.minDate = now.formatDateTm(this.opts.minDate);
		this.opts.maxDate = now.formatDateTm(this.opts.maxDate);
		
		this.sDate = sDate.trim();
	}
	
	$.extend(Datepicker.prototype, {
		get: function(name) {
			return this.opts[name];
		},
		_getDays: function (y,m){//获取某年某月的天数
			return m==2?(y%4||!(y%100)&&y%400?28:29):(/4|6|9|11/.test(m)?30:31);
		},

		_minMaxDate: function(sDate){
			var _count = sDate.split('-').length -1;
			var _format = 'y-M-d';
			if (_count == 1) _format = 'y-M';
			else if (_count == 0) _format = 'y';
			
			return sDate.parseDate(_format);
		},
		getMinDate: function(){
			return this._minMaxDate(this.opts.minDate);
		},
		getMaxDate: function(){
			var _sDate = this.opts.maxDate;
			var _count = _sDate.split('-').length -1;
			var _date = this._minMaxDate(_sDate);
			
			if (_count < 2) { //format:y-M、y
				var _day = this._getDays(_date.getFullYear(), _date.getMonth()+1);
				_date.setDate(_day);
				if (_count == 0) {//format:y
					_date.setMonth(11);
				}
			}

			return _date;
		},
		getDateWrap: function(date){ //得到年,月,日
			if (!date) date = this.parseDate(this.sDate) || new Date();
			var y = date.getFullYear();
			var m = date.getMonth()+1;
			var days = this._getDays(y,m);
			return {
				year:y, month:m, day:date.getDate(),
				hour:date.getHours(),minute:date.getMinutes(),second:date.getSeconds(),
				days: days, date:date
			}
		},
		/**
		 * @param {year:2010, month:05, day:24}
		 */
		changeDate: function(y, m, d){
			var date = new Date(y, m - 1, d || 1);
			this.sDate = this.formatDate(date);
			return date;
		},
		changeDay: function(day, chMonth){
			if (!chMonth) chMonth = 0;
			var dw = this.getDateWrap();
			return this.changeDate(dw.year, dw.month+parseInt(chMonth), day);
		},
		parseDate: function(sDate){
			if (!sDate) return null;
			return sDate.parseDate(this.opts.pattern);
		},
		formatDate: function(date){
			return date.formatDate(this.opts.pattern);
		},
		hasHour: function() {
			return this.opts.pattern.indexOf("H") != -1;
		},
		hasMinute: function() {
			return this.opts.pattern.indexOf("m") != -1;
		},
		hasSecond: function() {
			return this.opts.pattern.indexOf("s") != -1;
		},
		hasTime: function() {
			return this.hasHour() || this.hasMinute() || this.hasSecond();
		},
		hasDate: function() {
			var _dateKeys = ['y','M','d','E'];
			for (var i=0; i<_dateKeys.length; i++){
				if (this.opts.pattern.indexOf(_dateKeys[i]) != -1) return true;
			}

			return false;
		}
	});
	
		/**
	 * 扩展String方法
	 */
	$.extend(String.prototype, {
		isPositiveInteger:function(){
			return (new RegExp(/^[1-9]\d*$/).test(this));
		},
		isInteger:function(){
			return (new RegExp(/^\d+$/).test(this));
		},
		isNumber: function(value, element) {
			return (new RegExp(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/).test(this));
		},
		trim:function(){
			return this.replace(/(^\s*)|(\s*$)|\r|\n/g, "");
		},
		startsWith:function (pattern){
			return this.indexOf(pattern) === 0;
		},
		endsWith:function(pattern) {
			var d = this.length - pattern.length;
			return d >= 0 && this.lastIndexOf(pattern) === d;
		},
		replaceSuffix:function(index){
			return this.replace(/\[[0-9]+\]/,'['+index+']').replace('#index#',index);
		},
		trans:function(){
			return this.replace(/&lt;/g, '<').replace(/&gt;/g,'>').replace(/&quot;/g, '"');
		},
		encodeTXT: function(){
			return (this).replaceAll('&', '&amp;').replaceAll("<","&lt;").replaceAll(">", "&gt;").replaceAll(" ", "&nbsp;");
		},
		replaceAll:function(os, ns){
			return this.replace(new RegExp(os,"gm"),ns);
		},
		replaceTm:function($data){
			if (!$data) return this;
			return this.replace(RegExp("({[A-Za-z_]+[A-Za-z0-9_]*})","g"), function($1){
				return $data[$1.replace(/[{}]+/g, "")];
			});
		},
		replaceTmById:function(_box){
			var $parent = _box || $(document);
			return this.replace(RegExp("({[A-Za-z_]+[A-Za-z0-9_]*})","g"), function($1){
				var $input = $parent.find("#"+$1.replace(/[{}]+/g, ""));
				return $input.val() ? $input.val() : $1;
			});
		},
		isFinishedTm:function(){
			return !(new RegExp("{[A-Za-z_]+[A-Za-z0-9_]*}").test(this)); 
		},
		skipChar:function(ch) {
			if (!this || this.length===0) {return '';}
			if (this.charAt(0)===ch) {return this.substring(1).skipChar(ch);}
			return this;
		},
		isValidPwd:function() {
			return (new RegExp(/^([_]|[a-zA-Z0-9]){6,32}$/).test(this)); 
		},
		isValidMail:function(){
			return(new RegExp(/^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/).test(this.trim()));
		},
		isSpaces:function() {
			for(var i=0; i<this.length; i+=1) {
				var ch = this.charAt(i);
				if (ch!=' '&& ch!="\n" && ch!="\t" && ch!="\r") {return false;}
			}
			return true;
		},
		isPhone:function() {
			return (new RegExp(/(^([0-9]{3,4}[-])?\d{3,8}(-\d{1,6})?$)|(^\([0-9]{3,4}\)\d{3,8}(\(\d{1,6}\))?$)|(^\d{3,8}$)/).test(this));
		},
		isUrl:function(){
			return (new RegExp(/^[a-zA-z]+:\/\/([a-zA-Z0-9\-\.]+)([-\w .\/?%&=:]*)$/).test(this));
		},
		isExternalUrl:function(){
			return this.isUrl() && this.indexOf("://"+document.domain) == -1;
		}
	});
})(jQuery);
 