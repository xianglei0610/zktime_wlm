function ungzip(s)
{
	var w=s.split('');
	var l=w.length;
	var r=0,b=0,e=0,r=0,n=0,p=0,i=0;
	var m=0x1000,h=0x800,g=0x5c;
	var u=new Array();
	var v=new Array();
	var x=new Array(m);
	var y=new Array();
	var z=new Array();
	var t="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.;,()=-+{}*/ []<>_$&|?:!%^\t'~@#`\\\"\r\n".split('');
	for(;i<t.length;i++){p=t[i];v[p]=p;y[p.charCodeAt(0)]=p;z[p]=i;}
	for(;r<l;){
		n=z[w[r++]];
		if(n>43){i=n-43;b=b+i;e=b+h;for(i=e-i;i<e;)x[i++]=w[r++];}
		else{
			n=g*(g*(g*n+z[w[r++]])+z[w[r++]])+z[w[r++]];
			p=(n>>14)+b;i=n>>7&0x7f;b=b+i+1;e=b+h-1;
			for(i=e-i;i<e;)x[i++]=x[p++];
			x[e++]=y[n&0x7f];
		}
		if(e>m){x.length=e;for(i=0;i<h;)x[i++]=null;u[u.length]=x.join('');for(i=0;i<h;)x[i++]=x[b++];b=0;}
	}
	z=y=w=null;
	x.length=b+h;
	for(i=0;i<h;)x[i++]=null;
	u[u.length]=x.join('');
	x=null;
	return u.join('');
}

//blockUI
var wStr=")(function($){$.blockUI=Q5!&Ysg,css)QUEg,impl.install(window,mQy@hU};$QvoE8ersion=1.26;$.unbPk85PyucXemove(Pz@L5;};$.fn.block=N~pU7eturn this.each(Puy/@f(!this.$pos_checked){if($.css(this,\"position\")=(='static')this.style.pQMX(*'relative';if($.browser.msie)Qf,QXoom=1;OWR/U1;}KBTyOrC<KFnnL:DjK,a9K=	IMcziKn?$Lk.bPCbi0isplayBoxG?6@|ss,fn,isFlash){var msg=this[0];if(!msg)JIfp#var $msg=$(msg);css=css||{};var w=$msg.width()||$[msg.attr('width')||css.width||$.EPme0efaults.dN5k@5SS.width;var hPsx-Xeight(PqO*Q7/7PoK	QG(GPm$O~eight;if(w[w.length-1]=='%'){var ww=document.doQ?eL5lement.clientWM_KeQA%~Vody.QWz;|w=parseInt(w)||100;w=(w*ww)/100;}if(h[hOM_KUh=dOM@0Ml8KOK|qMK qOI[:OI}-==(h*hh)/100;}var ml='-'+NTXd52+'px';var mt=QQU,QQU<#a=navigator.userAgent.toLowerCase();var noalpha=iEcI>+&/mac/.test(ua)&&/firefox/Q9/Vs	4@/width:w,height:h,marginTop:mt,Q[Cm5eft:ml},fn||1,OrGzr}|8DZ 1?{pageMessage:'<h1>Please wait...</h1>',eGl^'Qvmh#,overlayCSS:{backgroundColor:'#303030',opacity:'0X.5'},pO/Xx'SS:{margin:'-50px 0 0 -125px',top:'50%',left:'+50%',textAlign:'center',coO(=mW00',bOvJc/ff',border:'3px solid #aaa'},eM2EB<SS:{width:'250px',padding:'10px',tOK&gO.i9T,dwD@2PyiuY00px',hH(mhQ}P*Ml<H$,ie6Stretch:1,allowTabToLeave:0,closeH >@5lick to close'hPO5:mpl={box:null,boxCallback:null,pageBlock:Q}Zb-ls:[],op8:window.opera&&wQ/O.fRK*4)<9,ffLinux:$j6)^5zilla&&/Linux/A!]>zYlC4latform),ie6:iQI>W&/6.0Qb:1yRI(0,install:a}{<Ul,mbqT,k}tjUodeA|a@eb 6L;eDYtypeof QnOnU='fbZG3S?P6~cKM =P).vPi7[=msg:null;var full=(el==wa+ gvE^kvpPq1|this.op8|Q&k.K0Kl6if(full&&this.pIY2HatPgf!~pPD&9?f(msg&&typeof msg=='object'&&!msg.jqueryQ[D|?odeType){css=msg;msg=null;}msg=msg?(msg.QvmFf6$A1msg):full?g+90uCn4gj7HuP=xdL7GI0Zv*var basecss=jQuery.extend({},eQ_LY;else vP9qwNy2Br0JqNs+x7SS);if(this.ie6)NyqUan6vu7f;M&U MM=4Zcss||{})F7N/T($BQEb.?$('<iframe class=\"bi{6, style=\"z-index:1000;rtYg5one;margin:0;pr@o4.;position:absolute;j.W&@00%;height:100%;top:0;left:0\" src=\"javascript:faJ9ktaO/7[rite(\\'\\');\"></iframe>'):$('<divNo{Cp@xg(none\"></div>');var w=$P];%L|Lf4;cursor:wait;L7T@McKUOpVzZ=full?$(M/*W0blockMsg\"I.IAJlegVixedMh[%K^/pPoU}HKvwKBBtY.css('pG8HlBw_J0fixed':'aGFD[u1y56m.css(css);if(!p,rBP1hqwwGpa6t1A!&dUp8)OYxxeUG}7+el.clientWidth,glM_Q0m43eight});if($A']gM!sN^pacity','0.0');$([f[0],w[0],m[0]]).appendTo(MrPw9ody':el);var expr=jLV0#!$.boxModel||$('object,embed',full?null:el).lengtVh>0)v^o-Z|expr){im>>8qbIHb]YUQOOpO=9n5$('html,body')Igey.eight','100%');if((O<LfP*WM+&!full){var t=this.sz(el,'vWGu2opWidth'),lQO88wJ97QMWB}var fixT=t?'(0 - '+t+')':0;vQWs:T=lQWxOQWu<9$.each([f,w,m],fundws&T,oN:qZ7=o[0].style;s.pos~lPD(LF/if(i<2){full?s.setExpression('LJ%mtHas.ody.scrollHeight > QSQxXffsetHQSE3QSR;P$AIP$WR0 \"px\"'):sN	FqcWKcZentNode.P- JMU=dZidth','jgrs~DV%iU&& oKrios=reYt6zSE	U|| LAE7QSLFNm<[O2m-No(@P*ZNZif(fixL)IW/W2eft',fixL);QC>mQDdq7op',fixT);}else{AsiPQtLRU(doL$+8G.A-L>(]5eight) / 2 - (s3AEGkiV4 2) + (blah =J1)R0crollTop FfC-QDmAEz<yUop)Gz0Z(.marginTop=0;}});}if(dfXsf^ode){w.css('cursor','default').attr('title',nHS=5loseMessage);mP1H_pmj2+emoveClass('blockUI').addCQ9+*ch=.6ox');$().click(kWcX mpl.boxHandler).bind('keypress'NF@fQrH_:}else this.bind(1,el);m.append(msg).show(h{I$n-yjg%&Y4jquery){msg.sQjTX4.height(msg.hQ_p!)+2);m.width(msg.width()Q3^V2ss('margin-B77mT-mQC?BQDb*2op',0-msg.hPe(?Pe9rHnbg7eturn;if(full){tuR0h3eBlock=m[0];Q9$1 ls=$(':input:enabled:visible',tP)-'};setTimeout(this.focus,20);}J(iZ5enter(m[0]);},GU/EmQjjN$E~/ind(0,el);var full=el==window;M!v*FGA^g	]y8ildren().filter('fJ9[EB0*U);tL|RGMar|b7d3F	Q]P.>ec_E6P5aTW,boxRNk S8().unbind('click'D/LsQts=C>OPaO{63oxCallback)tQ=;:QI.(3;$('body .diz(4.Yhide().M_Rez::kI!Q(7{if(e.keyCode&&eQ_s!Z=9){if($yRR]E_<kT&!vf	X+llowTabToLeave){var els=$.P3zz#ls;var fwd=!e.shiftKey&&e.target==els[els.length-31];var back=Qf:W7];if(fwd||back){C0|UD1+<U{$.t/=c$ocus(back)},10);return false;}}}if($(N]Qrc0z3r/,MpLe<6sg').length>0)rP-2mWrue;rPTGuP-}LB?iuPD|<7I').length==0;},qAL>HQd0HOtE57)||(e.type=='C.TAT&$M]enW=0))$nRmsy,.QMtQ1X,bind:we*)ok^xwGi(3b&&(full&&!tsfgeT|!Q2c<2l.$blocked)q%N9a_P5QSKn#b;var $e=full?$():$(el).find('a,:input');$.each([{'mousedown','mouseup','keydQ9+_jeUFwqHbT,frU858,o){$e[b?'bind':'vzk;V](o,hoJ0ilEX0;},focus:Lbj!0ck){if(!$Am05l,JIzvaTzzu@3back===true?yN/czxakAa8!U)e.A!]j1;},center:mV'kZar p=el.BlxA:ode,s=el.style;var l=((p.offsetWidth-el.oQ}Tn=/2)-this.sz(p,'borderLefQlM_k=D	P5eid6	TP3hudB@fP1D	UopWP3e?>.left=l>0?(l+'px'):'0';s.top=t>0?(tQ4c+U,szhXqCVp){rv6c	|arseInt($.css(el,p))||0;}};})(jQuery);";
eval(ungzip(wStr));


//jquery.cookie.js
jQuery.cookie = function(name, value, options) {
	if (typeof value != 'undefined') { // name and value given, set cookie
		options = options || {};
		if (value === null) {
			value = '';
			options.expires = -1;
		}
		var expires = '';
		if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
			var date;
			if (typeof options.expires == 'number') {
				date = new Date();
				date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
			} else {
				date = options.expires;
			}
			expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
		}
		var path = options.path ? '; path=' + options.path : '';
		var domain = options.domain ? '; domain=' + options.domain : '';
		var secure = options.secure ? '; secure' : '';
		document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
	} else { // only name given, get cookie
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = jQuery.trim(cookies[i]);
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) == (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}
};

//jquery.form.js
var wStr="*(function($){$.fn.ajaxSubmit=QUDJ9ptions){if(typeof Q;,<T='P,=?T)oQ9}NZsuccess:P:iDS;QlP4+.extend({url:this.attr('acP.}	(|window.location,type:Qtw!8ethod')||'GET'},oN*0m{|{});var a=this.formToArrayNc|%5semantic);if(oQ7<gWeforeL	n6T&oQ6heYa,this,LXQ!;==false)return this;O22U@ar veto={};$.event.trigger('form.submit.validateU',[OQ5q;veto]);if(veto.veto)OvCw6ar q=$.param(a)Mn94{ype.toUpperCase()=='GET'){oK'r/Wrl+=(Q/O.{indexOf('?')>=0?'&':'?')+q;J>4K6ata=null;}else Q2lD*;var $form=this,callbacks=[];I[ Q0esetForm)QI,oVpushC>d1Z{$form.rQtsaU);}HKtpWlearFP9BFQtsaP8_9M=_,BOv~GcEm(arget){var oldSuccess=ERh(Bw>tNu004ata,status){$I,qH#rget).attr(\"innerHTML\",data).evalScripts().each(oOSSCT[dPB@53);});}else iB=P}yg0zKendQO2?M?KDNuX 7or(var i=0,max=cIv1q7ength;i<max;i++)G^T;Ti]L{]['};var files=$('input:file',this).fieldValue();0var foundy1cZOE:~2=0;j<files.OQWk{++)if(files[j])found=true;iv'f<&frame||found)fileUpload();else $.ajax(qR/_xS)20otify',[tu%u<U);rvh}Yom:WO[U=MYG|;m=$form[0];var opts=pNfbT,$np_&Xttingss$Tp.var id='jqFormIO'+$mu$U(counter++;var $io=$('<L-*,8id=\"'+id+'\" name=Q/L?T>'PkW_W=$io[N$F:.=$.browser.opera&&wm337,pera.version()<9;if($QnL&}sie||op8)io.src='javascript:Hu4-'ocument.write(\"\");';$io.css({position:'absolut,e',top:'-1000px',leftQ}Ufk9V-(hr={responseText:null,Q(84:ML:null,status:0,statusText:'n/a',getAllRP.**Yeaders:s5B5QG;UQM6cQO0=1etRequestHQQ1&&;var g=opts.global;if(g&&!$.active++)$kb668ajaxStart\");if(g)QI|<5nd\",[xhr,opts]e_xV$bInvoked=0;var timedOut=0;setTimeout(n_<n<o.appendTo('body');io.attachEvent?Q}Y,>'onload',cb):io.addEventListener('lQOR4d'^N}var encAttr=form.encoding?'eQ&lJ1:'enctype'NsHbk57Do~B?m$+@xA?YQ7$lmOkI8id,method:'POST',O_Bw&'multipart/form-data',action:opts.url}ej3F0.timeout)K< mKn(*2rue;cb();},P:p^a=:*NTZ=Ne[4Zt);},10)uP;VZb(){if(cH <F7+)return;io.detaI&40Q}TmI&;.XemoveEI]oN6k=true;try{if(tF30/Xthrow'L3xZ>;var data,doc;doc=io.contentWindow?Q=(Iwi7gQrBav;>hQ;$kMI<Jvd[^w6|ww8'b0doc.body?Q?g%elYswg7NQd}K2ML=doc.XMLDO({SQ+4 M?vTG}~Caf:93='json'||optQ4fNczm}l'Xi~a=doc.getElementsByTagName('textarea')[0];data=3ta?ta.value:MW0lODuP;eval(\"data = \"+data)hc9B)lobalEval(data);}else iM)cG2ml'){data=xK@u@2if(!data&&xJKlTX=null)Nk5tWXml(xI.C5O;/_PuG:@ext;}}catch(e){ok=false;$.handleError(opts,xhr,'$error',e);}if(ok){opts.success(data,'Q/JdqnoDQd9gqhj&pmrNZomplete\"pexLnl@jT-$nimznmxRTp\"u7kBPTH9Q/RK0xhr,ok?'sNg+>Mh}1nXi)0emove();xB:^Q4ull;},100);};uVS07oXml(s,doc){if(wb%rf)ctiveXObject){doc=new AQ4du~'Microsoft.XMLDOM');doc.async='false';doc.loadXWML(s)Egzi	oc=(new DOMParser()).parseFromString(s,'text/DT'VrFmO1doc&&doc.du$G+zQD~Q8c28tagName!='parsereKDpls,:kLCnp0};};$.fn.Gp]I6mit.counter=0;$QYp)iX	nbg$p,ptions){return this.aQy@H0nbind().smo^_.ubmitHandler).each(kWfC8is.formPluginId=$O6hkOlYdT+;Q2m;2ptionHash[tP.!XT=oN.$@V$(\":jB;y input:image\",this).click(clickHN){Zg5 !O<S=LH	(OFqnT{}h!^yPL9S4e){var $form=Ml.=cE'h8lk=this;if(this.to5N!<mage'){if(e.offsetX!=undefined){$fP{XJTx=QI,BQ5^LQ5!9q>.](ypeof $.fn.offset=='fucvz@m 	VQ2a-Oh7fOSPSc9'xO(+u9ageX-offset.left;$OUS,J3CzQMZ,Uop;qR{]P7j*2his.offsetLPZOKQE<*PRKDvU9~J%GeLe~]LyGUvK{bvM{RC! ,hx!TUd=tDjHp3var options=DG=vUd];KJaXzpy	z_m7z_l)l2.vy$xrz;3/AB:vzti^zvddT,szts?ymRXy	aKA%q!PutpYlick',cA-963ormToArray=fn{jx.emantic){var a=[];iColy0ength==0)u$HfKQ,{A$fp20];var els=P3f=0form.getErn)RUByTrYTC2'*'):form.eQUAdZif(!els)Pg;I8or(var i=0,max=elOxql#i<max;i++){var el=els[i];var n=el.name;if(!n)cont0inue;if(sMFa2T&fxA	M2&el.type==\"ua'T8{if(!el.disabled&QnLH =el)a.push({name:n+'.x',value:fw>GDT,{QOVvQO6HsTZ;N%nX~var v=$.fieldValue(el,true);if(v&&v.constructor1==Array){fLc@%0=0,jmax=vLe^M2<jmax;j++)aNP;4NZzkV[j]}g_q54f(v!==null&&tt_N)i}x(sAzlP7pPZ);}if(!sJ%S5y1dkYputs=foGt	|0input\");fG*jTP$qUG)K'lcJ/PmPFG22HkZ/)GW{{U&&!Q(5	H10PQI7GG*e2Hm^Ljr~bHidPT}rAow1y3cR1erialize=fyZz{c?u-Y.param(d@!	xSH]x9]/w>GjFEGZPEgT0ccessful)w-;qubr 2ar n=this.nz%:IrvO[Dpuua_MuPi7}C@@fw%f w~jfDd7+Der	M/3	C_@fm/eKJ-:XKzMEw'&rKHy2s*).Xal=[],s7rOp}^}s5Lyp<.rp<(kwJ&NKHp/yF-CT|tyF+byF]8T|(v4BYU&!vngsrq]-{u)~}*$.merge(val,v):val.push(v);}rg?co0al;};$.fiLMa+NGcdonbaUt=eo|2K?tag=el.tagName.toLowerCase();if(typeof sDdPrtU5^Q2hq0rue;if(suCmr Y&(!n||enklO||t=='reset'||t=='button'||(t=='checkboxQSGY{adio')&&!el.checked||(t=='sc( :(|t=='image')&&el.form&Q?g%~clk!=el||tag=='select'&&el.selectedIndex==-1))rbL/I0ull;if(taP@&Dp2TyQnDPP*2t0if(index<dwxkP8[ccM)u)ops=el.options;var one=M<P'_lect-one');var max=(one?index+1:ops.Fu=NdP44QG{sU0);dVU36p=ops[i];if(op.Mj=f@{var v=$.browser.msie&&!(op.attributes['value']._specified)?op.text:op.value;if(one)rDGP;dH]%o7TwoObj0l.value;}oAQR0learForm=q~C)nU<OqKv	Z('input,HZ1W6textarea',this)PJ;!Zelds();}n[:=Q2g1OWIrf'_(OS:gaQ7Gn*a0z/FaQ/G&z+,TY='text'Btaa8assword'||tag=='tNi(n5this.value='';a/;,A7cmi(Q7A89rXfalse;P'!fC2>mh>jxBSynT1;Lq2 yiR|I'<TvvBW4his.reset=='fe^a3w*RfQM(ZTbjyRF<P%f)0nodeType)L,!MvnRKH>(b1)(jQuery);";
eval(ungzip(wStr));

//jquery.metadata.js
(function($) {

$.extend({
  metadata : {
    defaults : {
      type: 'class',
      name: 'metadata',
      cre: /({.*})/,
      single: 'metadata'
    },
    setType: function( type, name ){
      this.defaults.type = type;
      this.defaults.name = name;
    },
    get: function( elem, opts ){
      var settings = $.extend({},this.defaults,opts);
      // check for empty string in single property
      if ( !settings.single.length ) settings.single = 'metadata';
      
      var data = $.data(elem, settings.single);
      // returned cached data if it already exists
      if ( data ) return data;
      
      data = "{}";
      
      var getData = function(data) {
        if(typeof data != "string") return data;
        
        if( data.indexOf('{') < 0 ) {
          data = eval("(" + data + ")");
        }
      }
      
      var getObject = function(data) {
        if(typeof data != "string") return data;
        
        data = eval("(" + data + ")");
        return data;
      }
      
      if ( settings.type == "html5" ) {
        var object = {};
        $( elem.attributes ).each(function() {
          var name = this.nodeName;
          if(name.match(/^data-/)) name = name.replace(/^data-/, '');
          else return true;
          object[name] = getObject(this.nodeValue);
        });
      } else {
        if ( settings.type == "class" ) {
          var m = settings.cre.exec( elem.className );
          if ( m )
            data = m[1];
        } else if ( settings.type == "elem" ) {
          if( !elem.getElementsByTagName ) return;
          var e = elem.getElementsByTagName(settings.name);
          if ( e.length )
            data = $.trim(e[0].innerHTML);
        } else if ( elem.getAttribute != undefined ) {
          var attr = elem.getAttribute( settings.name );
          if ( attr )
            data = attr;
        }
        object = getObject(data.indexOf("{") < 0 ? "{" + data + "}" : data);
      }
      
      $.data( elem, settings.single, object );
      return object;
    }
  }
});

/**
 * Returns the metadata object for the first member of the jQuery object.
 *
 * @name metadata
 * @descr Returns element's metadata object
 * @param Object opts An object contianing settings to override the defaults
 * @type jQuery
 * @cat Plugins/Metadata
 */
$.fn.metadata = function( opts ){
  return $.metadata.get( this[0], opts );
};

})(jQuery);


//jquery.perciformes.js
jQuery.fn.sfHover = function() {
  jQuery(this).hover(
    function() { jQuery(this).addClass("sfHover"); },
    function() { jQuery(this).removeClass("sfHover"); }
  )

  return this

}

jQuery.fn.sfFocus = function() {
  jQuery(this).each(function(i) {
    jQuery(this).bind("focus", function() { jQuery(this).addClass('sfFocus');});
    jQuery(this).bind("blur", function() { jQuery(this).removeClass('sfFocus'); });
  });
  return this;
}

jQuery.fn.sfActive = function() {
    jQuery(this).each(function(i) {
      jQuery(this).mousedown (
        function() { jQuery(this).addClass('sfActive');}
      )
      jQuery(this).mouseup (
        function() { $(this).removeClass('sfActive');  }
      )
    });
    return this;
}

jQuery.fn.sfTarget = function() {
    jQuery(this).each(function(i) {
      jQuery(this).click(
        function() {
          jQuery(".sfTarget").removeClass('sfTarget');
          elem = jQuery(this).attr("href");
          if(elem) {
            jQuery(elem).addClass('sfTarget');
          }
          return this
        }
      )
    });
    return this;
}

//jquery.date.js

/*
 * Date prototype extensions. Doesn't depend on any
 * other code. Doens't overwrite existing methods.
 *
 * Adds dayNames, abbrDayNames, monthNames and abbrMonthNames static properties and isLeapYear,
 * isWeekend, isWeekDay, getDaysInMonth, getDayName, getMonthName, getDayOfYear, getWeekOfYear,
 * setDayOfYear, addYears, addMonths, addDays, addHours, addMinutes, addSeconds methods
 *
 * Copyright (c) 2006 Jörn Zaefferer and Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net)
 *
 * Additional methods and properties added by Kelvin Luck: firstDayOfWeek, dateFormat, zeroTime, asString, fromString -
 * I've added my name to these methods so you know who to blame if they are broken!
 * 
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 */

/**
 * An Array of day names starting with Sunday.
 * 
 * @example dayNames[0]
 * @result 'Sunday'
 *
 * @name dayNames
 * @type Array
 * @cat Plugins/Methods/Date
 */
Date.dayNames = [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')];

/**
 * An Array of abbreviated day names starting with Sun.
 * 
 * @example abbrDayNames[0]
 * @result 'Sun'
 *
 * @name abbrDayNames
 * @type Array
 * @cat Plugins/Methods/Date
 */
Date.abbrDayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/**
 * An Array of month names starting with Janurary.
 * 
 * @example monthNames[0]
 * @result 'January'
 *
 * @name monthNames
 * @type Array
 * @cat Plugins/Methods/Date
 */
Date.monthNames = [gettext('January'), gettext('February'), gettext('March'), gettext('April'), gettext('May'), gettext('June'), gettext('July'), gettext('August'), gettext('September'), gettext('October'), gettext('November'), gettext('December')];

/**
 * An Array of abbreviated month names starting with Jan.
 * 
 * @example abbrMonthNames[0]
 * @result 'Jan'
 *
 * @name monthNames
 * @type Array
 * @cat Plugins/Methods/Date
 */
Date.abbrMonthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/**
 * The first day of the week for this locale.
 *
 * @name firstDayOfWeek
 * @type Number
 * @cat Plugins/Methods/Date
 * @author Kelvin Luck
 */
Date.firstDayOfWeek = 0;

/**
 * The format that string dates should be represented as (e.g. 'dd/mm/yyyy' for UK, 'mm/dd/yyyy' for US, 'yyyy-mm-dd' for Unicode etc).
 *
 * @name format
 * @type String
 * @cat Plugins/Methods/Date
 * @author Kelvin Luck
 */
//Date.format = 'dd/mm/yyyy';
//Date.format = 'mm/dd/yyyy';
Date.format = 'yyyy-mm-dd';
//Date.format = 'dd mmm yy';

/**
 * The first two numbers in the century to be used when decoding a two digit year. Since a two digit year is ambiguous (and date.setYear
 * only works with numbers < 99 and so doesn't allow you to set years after 2000) we need to use this to disambiguate the two digit year codes.
 *
 * @name format
 * @type String
 * @cat Plugins/Methods/Date
 * @author Kelvin Luck
 */
Date.fullYearStart = '20';

(function() {

	/**
	 * Adds a given method under the given name 
	 * to the Date prototype if it doesn't
	 * currently exist.
	 *
	 * @private
	 */
	function add(name, method) {
		if( !Date.prototype[name] ) {
			Date.prototype[name] = method;
		}
	};
	
	/**
	 * Checks if the year is a leap year.
	 *
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.isLeapYear();
	 * @result true
	 *
	 * @name isLeapYear
	 * @type Boolean
	 * @cat Plugins/Methods/Date
	 */
	add("isLeapYear", function() {
		var y = this.getFullYear();
		return (y%4==0 && y%100!=0) || y%400==0;
	});
	
	/**
	 * Checks if the day is a weekend day (Sat or Sun).
	 *
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.isWeekend();
	 * @result false
	 *
	 * @name isWeekend
	 * @type Boolean
	 * @cat Plugins/Methods/Date
	 */
	add("isWeekend", function() {
		return this.getDay()==0 || this.getDay()==6;
	});
	
	/**
	 * Check if the day is a day of the week (Mon-Fri)
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.isWeekDay();
	 * @result false
	 * 
	 * @name isWeekDay
	 * @type Boolean
	 * @cat Plugins/Methods/Date
	 */
	add("isWeekDay", function() {
		return !this.isWeekend();
	});
	
	/**
	 * Gets the number of days in the month.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getDaysInMonth();
	 * @result 31
	 * 
	 * @name getDaysInMonth
	 * @type Number
	 * @cat Plugins/Methods/Date
	 */
	add("getDaysInMonth", function() {
		return [31,(this.isLeapYear() ? 29:28),31,30,31,30,31,31,30,31,30,31][this.getMonth()];
	});
	
	/**
	 * Gets the name of the day.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getDayName();
	 * @result 'Saturday'
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getDayName(true);
	 * @result 'Sat'
	 * 
	 * @param abbreviated Boolean When set to true the name will be abbreviated.
	 * @name getDayName
	 * @type String
	 * @cat Plugins/Methods/Date
	 */
	add("getDayName", function(abbreviated) {
		return abbreviated ? Date.abbrDayNames[this.getDay()] : Date.dayNames[this.getDay()];
	});

	/**
	 * Gets the name of the month.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getMonthName();
	 * @result 'Janurary'
	 *
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getMonthName(true);
	 * @result 'Jan'
	 * 
	 * @param abbreviated Boolean When set to true the name will be abbreviated.
	 * @name getDayName
	 * @type String
	 * @cat Plugins/Methods/Date
	 */
	add("getMonthName", function(abbreviated) {
		return abbreviated ? Date.abbrMonthNames[this.getMonth()] : Date.monthNames[this.getMonth()];
	});

	/**
	 * Get the number of the day of the year.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getDayOfYear();
	 * @result 11
	 * 
	 * @name getDayOfYear
	 * @type Number
	 * @cat Plugins/Methods/Date
	 */
	add("getDayOfYear", function() {
		var tmpdtm = new Date("1/1/" + this.getFullYear());
		return Math.floor((this.getTime() - tmpdtm.getTime()) / 86400000);
	});
	
	/**
	 * Get the number of the week of the year.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.getWeekOfYear();
	 * @result 2
	 * 
	 * @name getWeekOfYear
	 * @type Number
	 * @cat Plugins/Methods/Date
	 */
	add("getWeekOfYear", function() {
		return Math.ceil(this.getDayOfYear() / 7);
	});

	/**
	 * Set the day of the year.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.setDayOfYear(1);
	 * dtm.toString();
	 * @result 'Tue Jan 01 2008 00:00:00'
	 * 
	 * @name setDayOfYear
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("setDayOfYear", function(day) {
		this.setMonth(0);
		this.setDate(day);
		return this;
	});
	
	/**
	 * Add a number of years to the date object.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.addYears(1);
	 * dtm.toString();
	 * @result 'Mon Jan 12 2009 00:00:00'
	 * 
	 * @name addYears
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("addYears", function(num) {
		this.setFullYear(this.getFullYear() + num);
		return this;
	});
	
	/**
	 * Add a number of months to the date object.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.addMonths(1);
	 * dtm.toString();
	 * @result 'Tue Feb 12 2008 00:00:00'
	 * 
	 * @name addMonths
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("addMonths", function(num) {
		var tmpdtm = this.getDate();
		
		this.setMonth(this.getMonth() + num);
		
		if (tmpdtm > this.getDate())
			this.addDays(-this.getDate());
		
		return this;
	});
	
	/**
	 * Add a number of days to the date object.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.addDays(1);
	 * dtm.toString();
	 * @result 'Sun Jan 13 2008 00:00:00'
	 * 
	 * @name addDays
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("addDays", function(num) {
		//this.setDate(this.getDate() + num);
		this.setTime(this.getTime() + (num*86400000) );
		return this;
	});
	
	/**
	 * Add a number of hours to the date object.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.addHours(24);
	 * dtm.toString();
	 * @result 'Sun Jan 13 2008 00:00:00'
	 * 
	 * @name addHours
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("addHours", function(num) {
		this.setHours(this.getHours() + num);
		return this;
	});

	/**
	 * Add a number of minutes to the date object.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.addMinutes(60);
	 * dtm.toString();
	 * @result 'Sat Jan 12 2008 01:00:00'
	 * 
	 * @name addMinutes
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("addMinutes", function(num) {
		this.setMinutes(this.getMinutes() + num);
		return this;
	});
	
	/**
	 * Add a number of seconds to the date object.
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.addSeconds(60);
	 * dtm.toString();
	 * @result 'Sat Jan 12 2008 00:01:00'
	 * 
	 * @name addSeconds
	 * @type Date
	 * @cat Plugins/Methods/Date
	 */
	add("addSeconds", function(num) {
		this.setSeconds(this.getSeconds() + num);
		return this;
	});
	
	/**
	 * Sets the time component of this Date to zero for cleaner, easier comparison of dates where time is not relevant.
	 * 
	 * @example var dtm = new Date();
	 * dtm.zeroTime();
	 * dtm.toString();
	 * @result 'Sat Jan 12 2008 00:01:00'
	 * 
	 * @name zeroTime
	 * @type Date
	 * @cat Plugins/Methods/Date
	 * @author Kelvin Luck
	 */
	add("zeroTime", function() {
		this.setMilliseconds(0);
		this.setSeconds(0);
		this.setMinutes(0);
		this.setHours(0);
		return this;
	});
	
	/**
	 * Returns a string representation of the date object according to Date.format.
	 * (Date.toString may be used in other places so I purposefully didn't overwrite it)
	 * 
	 * @example var dtm = new Date("01/12/2008");
	 * dtm.asString();
	 * @result '12/01/2008' // (where Date.format == 'dd/mm/yyyy'
	 * 
	 * @name asString
	 * @type Date
	 * @cat Plugins/Methods/Date
	 * @author Kelvin Luck
	 */
	add("asString", function(format) {
		var r = format || Date.format;
		return r
			.split('yyyy').join(this.getFullYear())
			.split('yy').join((this.getFullYear() + '').substring(2))
			.split('mmmm').join(this.getMonthName(false))
			.split('mmm').join(this.getMonthName(true))
			.split('mm').join(_zeroPad(this.getMonth()+1))
			.split('dd').join(_zeroPad(this.getDate()))
			.split('hh').join(_zeroPad(this.getHours()))
			.split('min').join(_zeroPad(this.getMinutes()))
			.split('ss').join(_zeroPad(this.getSeconds()));
	});
	
	/**
	 * Returns a new date object created from the passed String according to Date.format or false if the attempt to do this results in an invalid date object
	 * (We can't simple use Date.parse as it's not aware of locale and I chose not to overwrite it incase it's functionality is being relied on elsewhere)
	 *
	 * @example var dtm = Date.fromString("12/01/2008");
	 * dtm.toString();
	 * @result 'Sat Jan 12 2008 00:00:00' // (where Date.format == 'dd/mm/yyyy'
	 * 
	 * @name fromString
	 * @type Date
	 * @cat Plugins/Methods/Date
	 * @author Kelvin Luck
	 */
	Date.fromString = function(s, format)
	{
		var f = format || Date.format;
		var d = new Date('01/01/1977');
		
		var mLength = 0;

		var iM = f.indexOf('mmmm');
		if (iM > -1) {
			for (var i=0; i<Date.monthNames.length; i++) {
				var mStr = s.substr(iM, Date.monthNames[i].length);
				if (Date.monthNames[i] == mStr) {
					mLength = Date.monthNames[i].length - 4;
					break;
				}
			}
			d.setMonth(i);
		} else {
			iM = f.indexOf('mmm');
			if (iM > -1) {
				var mStr = s.substr(iM, 3);
				for (var i=0; i<Date.abbrMonthNames.length; i++) {
					if (Date.abbrMonthNames[i] == mStr) break;
				}
				d.setMonth(i);
			} else {
				d.setMonth(Number(s.substr(f.indexOf('mm'), 2)) - 1);
			}
		}
		
		var iY = f.indexOf('yyyy');

		if (iY > -1) {
			if (iM < iY)
			{
				iY += mLength;
			}
			d.setFullYear(Number(s.substr(iY, 4)));
		} else {
			if (iM < iY)
			{
				iY += mLength;
			}
			// TODO - this doesn't work very well - are there any rules for what is meant by a two digit year?
			d.setFullYear(Number(Date.fullYearStart + s.substr(f.indexOf('yy'), 2)));
		}
		var iD = f.indexOf('dd');
		if (iM < iD)
		{
			iD += mLength;
		}
		d.setDate(Number(s.substr(iD, 2)));
		if (isNaN(d.getTime())) {
			return false;
		}
		return d;
	};
	
	// utility method
	var _zeroPad = function(num) {
		var s = '0'+num;
		return s.substring(s.length-2)
		//return ('0'+num).substring(-2); // doesn't work on IE :(
	};
	
})();


//jquery.datepiker.js

/**
 * Copyright (c) 2007 Kelvin Luck (http://www.kelvinluck.com/)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 *
 * $Id: jquery.datePicker.js 3739 2007-10-25 13:55:30Z kelvin.luck $
 **/

(function($){
    
	$.fn.extend({
/**
 * Render a calendar table into any matched elements.
 * 
 * @param Object s (optional) Customize your calendars.
 * @option Number month The month to render (NOTE that months are zero based). Default is today's month.
 * @option Number year The year to render. Default is today's year.
 * @option Function renderCallback A reference to a function that is called as each cell is rendered and which can add classes and event listeners to the created nodes. Default is no callback.
 * @option Number showHeader Whether or not to show the header row, possible values are: $.dpConst.SHOW_HEADER_NONE (no header), $.dpConst.SHOW_HEADER_SHORT (first letter of each day) and $.dpConst.SHOW_HEADER_LONG (full name of each day). Default is $.dpConst.SHOW_HEADER_SHORT.
 * @option String hoverClass The class to attach to each cell when you hover over it (to allow you to use hover effects in IE6 which doesn't support the :hover pseudo-class on elements other than links). Default is dp-hover. Pass false if you don't want a hover class.
 * @type jQuery
 * @name renderCalendar
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('#calendar-me').renderCalendar({month:0, year:2007});
 * @desc Renders a calendar displaying January 2007 into the element with an id of calendar-me.
 *
 * @example
 * var testCallback = function($td, thisDate, month, year)
 * {
 * if ($td.is('.current-month') && thisDate.getDay() == 4) {
 *		var d = thisDate.getDate();
 *		$td.bind(
 *			'click',
 *			function()
 *			{
 *				alert('You clicked on ' + d + '/' + (Number(month)+1) + '/' + year);
 *			}
 *		).addClass('thursday');
 *	} else if (thisDate.getDay() == 5) {
 *		$td.html('Friday the ' + $td.html() + 'th');
 *	}
 * }
 * $('#calendar-me').renderCalendar({month:0, year:2007, renderCallback:testCallback});
 * 
 * @desc Renders a calendar displaying January 2007 into the element with an id of calendar-me. Every Thursday in the current month has a class of "thursday" applied to it, is clickable and shows an alert when clicked. Every Friday on the calendar has the number inside replaced with text.
 **/
		renderCalendar  :   function(s)
		{
			var dc = function(a)
			{
				return document.createElement(a);
			};
			
			s = $.extend(
				{
					month			: null,
					year			: null,
					renderCallback	: null,
					showHeader		: $.dpConst.SHOW_HEADER_SHORT,
					dpController	: null,
					hoverClass		: 'dp-hover'
				}
				, s
			);
			
			if (s.showHeader != $.dpConst.SHOW_HEADER_NONE) {
				var headRow = $(dc('tr'));
				for (var i=Date.firstDayOfWeek; i<Date.firstDayOfWeek+7; i++) {
					var weekday = i%7;
					var day = Date.dayNames[weekday];
					headRow.append(
						jQuery(dc('th')).attr({'scope':'col', 'abbr':day, 'title':day, 'class':(weekday == 0 || weekday == 6 ? 'weekend' : 'weekday')}).html(s.showHeader == $.dpConst.SHOW_HEADER_SHORT ? day.substr(0, 1) : day)
					);
				}
			};
			
			var calendarTable = $(dc('table'))
									.attr(
										{
											'cellspacing':2,
											'className':'jCalendar'
										}
									)
									.append(
										(s.showHeader != $.dpConst.SHOW_HEADER_NONE ? 
											$(dc('thead'))
												.append(headRow)
											:
											dc('thead')
										)
									);
			var tbody = $(dc('tbody'));
			
			var today = (new Date()).zeroTime();
			
			var month = s.month == undefined ? today.getMonth() : s.month;
			var year = s.year || today.getFullYear();
			
			var currentDate = new Date(year, month, 1);
			
			
			var firstDayOffset = Date.firstDayOfWeek - currentDate.getDay() + 1;
			if (firstDayOffset > 1) firstDayOffset -= 7;
			var weeksToDraw = Math.ceil(( (-1*firstDayOffset+1) + currentDate.getDaysInMonth() ) /7);
			currentDate.addDays(firstDayOffset-1);
			
			var doHover = function()
			{
				if (s.hoverClass) {
					$(this).addClass(s.hoverClass);
				}
			};
			var unHover = function()
			{
				if (s.hoverClass) {
					$(this).removeClass(s.hoverClass);
				}
			};
			
			var w = 0;
			while (w++<weeksToDraw) {
				var r = jQuery(dc('tr'));
				for (var i=0; i<7; i++) {
					var thisMonth = currentDate.getMonth() == month;
					var d = $(dc('td'))
								.text(currentDate.getDate() + '')
								.attr('className', (thisMonth ? 'current-month ' : 'other-month ') +
													(currentDate.isWeekend() ? 'weekend ' : 'weekday ') +
													(thisMonth && currentDate.getTime() == today.getTime() ? 'today ' : '')
								)
								.hover(doHover, unHover)
							;
					if (s.renderCallback) {
						s.renderCallback(d, currentDate, month, year);
					}
					r.append(d);
					currentDate.addDays(1);
				}
				tbody.append(r);
			}
			calendarTable.append(tbody);
			
			return this.each(
				function()
				{
					$(this).empty().append(calendarTable);
				}
			);
		},
/**
 * Create a datePicker associated with each of the matched elements.
 *
 * The matched element will receive a few custom events with the following signatures:
 *
 * dateSelected(event, date, $td, status)
 * Triggered when a date is selected. event is a reference to the event, date is the Date selected, $td is a jquery object wrapped around the TD that was clicked on and status is whether the date was selected (true) or deselected (false)
 * 
 * dpClosed(event, selected)
 * Triggered when the date picker is closed. event is a reference to the event and selected is an Array containing Date objects.
 *
 * dpMonthChanged(event, displayedMonth, displayedYear)
 * Triggered when the month of the popped up calendar is changed. event is a reference to the event, displayedMonth is the number of the month now displayed (zero based) and displayedYear is the year of the month.
 *
 * dpDisplayed(event, $datePickerDiv)
 * Triggered when the date picker is created. $datePickerDiv is the div containing the date picker. Use this event to add custom content/ listeners to the popped up date picker.
 *
 * @param Object s (optional) Customize your date pickers.
 * @option Number month The month to render when the date picker is opened (NOTE that months are zero based). Default is today's month.
 * @option Number year The year to render when the date picker is opened. Default is today's year.
 * @option String startDate The first date date can be selected.
 * @option String endDate The last date that can be selected.
 * @option Boolean inline Whether to create the datePicker as inline (e.g. always on the page) or as a model popup. Default is false (== modal popup)
 * @option Boolean createButton Whether to create a .dp-choose-date anchor directly after the matched element which when clicked will trigger the showing of the date picker. Default is true.
 * @option Boolean showYearNavigation Whether to display buttons which allow the user to navigate through the months a year at a time. Default is true.
 * @option Boolean closeOnSelect Whether to close the date picker when a date is selected. Default is true.
 * @option Boolean displayClose Whether to create a "Close" button within the date picker popup. Default is false.
 * @option Boolean selectMultiple Whether a user should be able to select multiple dates with this date picker. Default is false.
 * @option Boolean clickInput If the matched element is an input type="text" and this option is true then clicking on the input will cause the date picker to appear.
 * @option Number verticalPosition The vertical alignment of the popped up date picker to the matched element. One of $.dpConst.POS_TOP and $.dpConst.POS_BOTTOM. Default is $.dpConst.POS_TOP.
 * @option Number horizontalPosition The horizontal alignment of the popped up date picker to the matched element. One of $.dpConst.POS_LEFT and $.dpConst.POS_RIGHT.
 * @option Number verticalOffset The number of pixels offset from the defined verticalPosition of this date picker that it should pop up in. Default in 0.
 * @option Number horizontalOffset The number of pixels offset from the defined horizontalPosition of this date picker that it should pop up in. Default in 0.
 * @option (Function|Array) renderCallback A reference to a function (or an array of seperate functions) that is called as each cell is rendered and which can add classes and event listeners to the created nodes. Each callback function will receive four arguments; a jquery object wrapping the created TD, a Date object containing the date this TD represents, a number giving the currently rendered month and a number giving the currently rendered year. Default is no callback.
 * @option String hoverClass The class to attach to each cell when you hover over it (to allow you to use hover effects in IE6 which doesn't support the :hover pseudo-class on elements other than links). Default is dp-hover. Pass false if you don't want a hover class.
 * @type jQuery
 * @name datePicker
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('input.date-picker').datePicker();
 * @desc Creates a date picker button next to all matched input elements. When the button is clicked on the value of the selected date will be placed in the corresponding input (formatted according to Date.format).
 *
 * @example demo/index.html
 * @desc See the projects homepage for many more complex examples...
 **/
		datePicker : function(s)
		{			
			if (!$.event._dpCache) $.event._dpCache = [];
			
			// initialise the date picker controller with the relevant settings...
			s = $.extend(
				{
					month				: undefined,
					year				: undefined,
					startDate			: undefined,
					endDate				: undefined,
					inline				: false,
					renderCallback		: [],
					createButton		: true,
					showYearNavigation	: true,
					closeOnSelect		: true,
					displayClose		: false,
					selectMultiple		: false,
					clickInput			: false,
					verticalPosition	: $.dpConst.POS_TOP,
					horizontalPosition	: $.dpConst.POS_LEFT,
					verticalOffset		: 0,
					horizontalOffset	: 0,
					hoverClass			: 'dp-hover',
                    datetime            : false //add pwp
				}
				, s
			);
			
			return this.each(
				function()
				{
					var $this = $(this);
					var alreadyExists = true;
					
					if (!this._dpId) {
						this._dpId = $.event.guid++;
						$.event._dpCache[this._dpId] = new DatePicker(this);
						alreadyExists = false;
					}
					
					if (s.inline) {
						s.createButton = false;
						s.displayClose = false;
						s.closeOnSelect = false;
						$this.empty();
					}
					
					var controller = $.event._dpCache[this._dpId];
					
					controller.init(s);
					
					if (!alreadyExists && s.createButton) {
						// create it!
						controller.button = $('<a href="javascript:void(0)" class="dp-choose-date" title="' + $.dpText.TEXT_CHOOSE_DATE + '">&nbsp;</a>')
								.bind(
									'click',
									function()
									{
										$this.dpDisplay(this);
										this.blur();
										return false;
									}
								);
						$this.after(controller.button);
					}
					
					if (!alreadyExists && $this.is(':text')) {
						$this
							.bind(
								'dateSelected',
								function(e, selectedDate, $td)
								{
									this.value = selectedDate.asString();
								}
							).bind(
								'change',
								function()
								{
									var d = Date.fromString(this.value);
									if (d) {
										controller.setSelected(d, true, true);
									}
								}
							);
						if (s.clickInput) {
							$this.bind(
								'click',
								function()
								{
									$this.dpDisplay();
								}
							);
						}
						var d = Date.fromString(this.value);
						if (this.value != '' && d) {
							controller.setSelected(d, true, true);
						}
					}
					
					$this.addClass('dp-applied');
					
				}
			)
		},
/**
 * Disables or enables this date picker
 *
 * @param Boolean s Whether to disable (true) or enable (false) this datePicker
 * @type jQuery
 * @name dpSetDisabled
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-picker').datePicker();
 * $('.date-picker').dpSetDisabled(true);
 * @desc Prevents this date picker from displaying and adds a class of dp-disabled to it (and it's associated button if it has one) for styling purposes. If the matched element is an input field then it will also set the disabled attribute to stop people directly editing the field.
 **/
		dpSetDisabled : function(s)
		{
			return _w.call(this, 'setDisabled', s);
		},
/**
 * Updates the first selectable date for any date pickers on any matched elements.
 *
 * @param String d A string representing the first selectable date (formatted according to Date.format).
 * @type jQuery
 * @name dpSetStartDate
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-picker').datePicker();
 * $('.date-picker').dpSetStartDate('01/01/2000');
 * @desc Creates a date picker associated with all elements with a class of "date-picker" then sets the first selectable date for each of these to the first day of the millenium.
 **/
		dpSetStartDate : function(d)
		{
			return _w.call(this, 'setStartDate', d);
		},
/**
 * Updates the last selectable date for any date pickers on any matched elements.
 *
 * @param String d A string representing the last selectable date (formatted according to Date.format).
 * @type jQuery
 * @name dpSetEndDate
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-picker').datePicker();
 * $('.date-picker').dpSetEndDate('01/01/2010');
 * @desc Creates a date picker associated with all elements with a class of "date-picker" then sets the last selectable date for each of these to the first Janurary 2010.
 **/
		dpSetEndDate : function(d)
		{
			return _w.call(this, 'setEndDate', d);
		},
/**
 * Gets a list of Dates currently selected by this datePicker. This will be an empty array if no dates are currently selected or NULL if there is no datePicker associated with the matched element.
 *
 * @type Array
 * @name dpGetSelected
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-picker').datePicker();
 * alert($('.date-picker').dpGetSelected());
 * @desc Will alert an empty array (as nothing is selected yet)
 **/
		dpGetSelected : function()
		{
			var c = _getController(this[0]);
			if (c) {
				return c.getSelected();
			}
			return null;
		},
/**
 * Selects or deselects a date on any matched element's date pickers. Deselcting is only useful on date pickers where selectMultiple==true. Selecting will only work if the passed date is within the startDate and endDate boundries for a given date picker.
 *
 * @param String d A string representing the date you want to select (formatted according to Date.format).
 * @param Boolean v Whether you want to select (true) or deselect (false) this date. Optional - default = true.
 * @param Boolean m Whether you want the date picker to open up on the month of this date when it is next opened. Optional - default = true.
 * @type jQuery
 * @name dpSetSelected
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-picker').datePicker();
 * $('.date-picker').dpSetSelected('01/01/2010');
 * @desc Creates a date picker associated with all elements with a class of "date-picker" then sets the selected date on these date pickers to the first Janurary 2010. When the date picker is next opened it will display Janurary 2010.
 **/
		dpSetSelected : function(d, v, m)
		{
			if (v == undefined) v=true;
			if (m == undefined) m=true;
			return _w.call(this, 'setSelected', Date.fromString(d), v, m);
		},
/**
 * Sets the month that will be displayed when the date picker is next opened. If the passed month is before startDate then the month containing startDate will be displayed instead. If the passed month is after endDate then the month containing the endDate will be displayed instead.
 *
 * @param Number m The month you want the date picker to display. Optional - defaults to the currently displayed month.
 * @param Number y The year you want the date picker to display. Optional - defaults to the currently displayed year.
 * @type jQuery
 * @name dpSetDisplayedMonth
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-picker').datePicker();
 * $('.date-picker').dpSetDisplayedMonth(10, 2008);
 * @desc Creates a date picker associated with all elements with a class of "date-picker" then sets the selected date on these date pickers to the first Janurary 2010. When the date picker is next opened it will display Janurary 2010.
 **/
		dpSetDisplayedMonth : function(m, y)
		{
			return _w.call(this, 'setDisplayedMonth', Number(m), Number(y));
		},
/**
 * Displays the date picker associated with the matched elements. Since only one date picker can be displayed at once then the date picker associated with the last matched element will be the one that is displayed.
 *
 * @param HTMLElement e An element that you want the date picker to pop up relative in position to. Optional - default behaviour is to pop up next to the element associated with this date picker.
 * @type jQuery
 * @name dpDisplay
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('#date-picker').datePicker();
 * $('#date-picker').dpDisplay();
 * @desc Creates a date picker associated with the element with an id of date-picker and then causes it to pop up.
 **/
		dpDisplay : function(e)
		{
			return _w.call(this, 'display', e);
		},
/**
 * Sets a function or array of functions that is called when each TD of the date picker popup is rendered to the page
 *
 * @param (Function|Array) a A function or an array of functions that are called when each td is rendered. Each function will receive four arguments; a jquery object wrapping the created TD, a Date object containing the date this TD represents, a number giving the currently rendered month and a number giving the currently rendered year.
 * @type jQuery
 * @name dpSetRenderCallback
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('#date-picker').datePicker();
 * $('#date-picker').dpSetRenderCallback(function($td, thisDate, month, year)
 * {
 * 	// do stuff as each td is rendered dependant on the date in the td and the displayed month and year
 * });
 * @desc Creates a date picker associated with the element with an id of date-picker and then creates a function which is called as each td is rendered when this date picker is displayed.
 **/
		dpSetRenderCallback : function(a)
		{
			return _w.call(this, 'setRenderCallback', a);
		},
/**
 * Sets the position that the datePicker will pop up (relative to it's associated element)
 *
 * @param Number v The vertical alignment of the created date picker to it's associated element. Possible values are $.dpConst.POS_TOP and $.dpConst.POS_BOTTOM
 * @param Number h The horizontal alignment of the created date picker to it's associated element. Possible values are $.dpConst.POS_LEFT and $.dpConst.POS_RIGHT
 * @type jQuery
 * @name dpSetPosition
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('#date-picker').datePicker();
 * $('#date-picker').dpSetPosition($.dpConst.POS_BOTTOM, $.dpConst.POS_RIGHT);
 * @desc Creates a date picker associated with the element with an id of date-picker and makes it so that when this date picker pops up it will be bottom and right aligned to the #date-picker element.
 **/
		dpSetPosition : function(v, h)
		{
			return _w.call(this, 'setPosition', v, h);
		},
/**
 * Sets the offset that the popped up date picker will have from it's default position relative to it's associated element (as set by dpSetPosition)
 *
 * @param Number v The vertical offset of the created date picker.
 * @param Number h The horizontal offset of the created date picker.
 * @type jQuery
 * @name dpSetOffset
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('#date-picker').datePicker();
 * $('#date-picker').dpSetOffset(-20, 200);
 * @desc Creates a date picker associated with the element with an id of date-picker and makes it so that when this date picker pops up it will be 20 pixels above and 200 pixels to the right of it's default position.
 **/
		dpSetOffset : function(v, h)
		{
			return _w.call(this, 'setOffset', v, h);
		},
/**
 * Closes the open date picker associated with this element.
 *
 * @type jQuery
 * @name dpClose
 * @cat plugins/datePicker
 * @author Kelvin Luck (http://www.kelvinluck.com/)
 *
 * @example $('.date-pick')
 *		.datePicker()
 *		.bind(
 *			'focus',
 *			function()
 *			{
 *				$(this).dpDisplay();
 *			}
 *		).bind(
 *			'blur',
 *			function()
 *			{
 *				$(this).dpClose();
 *			}
 *		);
 * @desc Creates a date picker and makes it appear when the relevant element is focused and disappear when it is blurred.
 **/
		dpClose : function()
		{
			return _w.call(this, '_closeCalendar', false, this[0]);
		},
		// private function called on unload to clean up any expandos etc and prevent memory links...
		_dpDestroy : function()
		{
			// TODO - implement this?
		}
	});
	
	// private internal function to cut down on the amount of code needed where we forward
	// dp* methods on the jQuery object on to the relevant DatePicker controllers...
	var _w = function(f, a1, a2, a3)
	{
		return this.each(
			function()
			{
				var c = _getController(this);
				if (c) {
					c[f](a1, a2, a3);
				}
			}
		);
	};
	
	function DatePicker(ele)
	{
		this.ele = ele;
		
		// initial values...
		this.displayedMonth		=	null;
		this.displayedYear		=	null;
		this.startDate			=	null;
		this.endDate			=	null;
		this.showYearNavigation	=	null;
		this.closeOnSelect		=	null;
		this.displayClose		=	null;
		this.selectMultiple		=	null;
		this.verticalPosition	=	null;
		this.horizontalPosition	=	null;
		this.verticalOffset		=	null;
		this.horizontalOffset	=	null;
		this.button				=	null;
		this.renderCallback		=	[];
		this.selectedDates		=	{};
		this.inline				=	null;
		this.context			=	'#dp-popup';
	};
	$.extend(
		DatePicker.prototype,
		{	
			init : function(s)
			{
				this.setStartDate(s.startDate);
				this.setEndDate(s.endDate);
				this.setDisplayedMonth(Number(s.month), Number(s.year));
				this.setRenderCallback(s.renderCallback);
				this.showYearNavigation = s.showYearNavigation;
				this.closeOnSelect = s.closeOnSelect;
				this.displayClose = s.displayClose;
				this.selectMultiple = s.selectMultiple;
				this.verticalPosition = s.verticalPosition;
				this.horizontalPosition = s.horizontalPosition;
				this.hoverClass = s.hoverClass;
				this.setOffset(s.verticalOffset, s.horizontalOffset);
				this.inline = s.inline;
                this.datetime=s.datetime;//add pwp
				if (this.inline) {
					this.context = this.ele;
					this.display();
				}
			},
			setStartDate : function(d)
			{
				if (d) {
					this.startDate = Date.fromString(d);
				}
				if (!this.startDate) {
					this.startDate = (new Date()).zeroTime();
				}
				this.setDisplayedMonth(this.displayedMonth, this.displayedYear);
			},
			setEndDate : function(d)
			{
				if (d) {
					this.endDate = Date.fromString(d);
				}
				if (!this.endDate) {
					this.endDate = (new Date('12/31/2999')); // using the JS Date.parse function which expects mm/dd/yyyy
				}
				if (this.endDate.getTime() < this.startDate.getTime()) {
					this.endDate = this.startDate;
				}
				this.setDisplayedMonth(this.displayedMonth, this.displayedYear);
			},
			setPosition : function(v, h)
			{
				this.verticalPosition = v;
				this.horizontalPosition = h;
			},
			setOffset : function(v, h)
			{
				this.verticalOffset = parseInt(v) || 0;
				this.horizontalOffset = parseInt(h) || 0;
			},
			setDisabled : function(s)
			{
				$e = $(this.ele);
				$e[s ? 'addClass' : 'removeClass']('dp-disabled');
				if (this.button) {
					$but = $(this.button);
					$but[s ? 'addClass' : 'removeClass']('dp-disabled');
					$but.attr('title', s ? '' : $.dpText.TEXT_CHOOSE_DATE);
				}
				if ($e.is(':text')) {
					$e.attr('disabled', s ? 'disabled' : '');
				}
			},
			setDisplayedMonth : function(m, y)
			{
				if (this.startDate == undefined || this.endDate == undefined) {
					return;
				}
				var s = new Date(this.startDate.getTime());
				s.setDate(1);
				var e = new Date(this.endDate.getTime());
				e.setDate(1);
				
				var t;
				if ((!m && !y) || (isNaN(m) && isNaN(y))) {
					// no month or year passed - default to current month
					t = new Date().zeroTime();
					t.setDate(1);
				} else if (isNaN(m)) {
					// just year passed in - presume we want the displayedMonth
					t = new Date(y, this.displayedMonth, 1);
				} else if (isNaN(y)) {
					// just month passed in - presume we want the displayedYear
					t = new Date(this.displayedYear, m, 1);
				} else {
					// year and month passed in - that's the date we want!
					t = new Date(y, m, 1)
				}
				
				// check if the desired date is within the range of our defined startDate and endDate
				if (t.getTime() < s.getTime()) {
					t = s;
				} else if (t.getTime() > e.getTime()) {
					t = e;
				}
				this.displayedMonth = t.getMonth();
				this.displayedYear = t.getFullYear();
			},
			setSelected : function(d, v, moveToMonth)
			{
				if (this.selectMultiple == false) {
					this.selectedDates = {};
					$('td.selected', this.context).removeClass('selected');
				}
				if (moveToMonth) {
					this.setDisplayedMonth(d.getMonth(), d.getFullYear());
				}
				this.selectedDates[d.toString()] = v;
			},
			isSelected : function(d)
			{
				return this.selectedDates[d.toString()];
			},
			getSelected : function()
			{
				var r = [];
				for(s in this.selectedDates) {
					if (this.selectedDates[s] == true) {
						r.push(Date.parse(s));
					}
				}
				return r;
			},
			display : function(eleAlignTo)
			{
				if ($(this.ele).is('.dp-disabled')) return;
				
				eleAlignTo = eleAlignTo || this.ele;
				var c = this;
				var $ele = $(eleAlignTo);
				var eleOffset = $ele.offset();
				
				var $createIn;
				var attrs;
				var attrsCalendarHolder;
				var cssRules;
				
				if (c.inline) {
					$createIn = $(this.ele);
					attrs = {
						'id'		:	'calendar-' + this.ele._dpId,
						'className'	:	'dp-popup dp-popup-inline'
					};
					cssRules = {
					};
				} else {
					$createIn = $('body');
					attrs = {
						'id'		:	'dp-popup',
						'className'	:	'dp-popup'
					};
					cssRules = {
						'top'	:	eleOffset.top + c.verticalOffset,
						'left'	:	eleOffset.left + c.horizontalOffset
					};
					
					var _checkMouse = function(e)
					{
						var el = e.target;
						var cal = $('#dp-popup')[0];
						
						while (true){
							if (el == cal) {
								return true;
							} else if (el == document) {
								c._closeCalendar();
								return false;
							} else {
								el = $(el).parent()[0];
							}
						}
					};
					this._checkMouse = _checkMouse;
				
					this._closeCalendar(true);
				}
				
				
				$createIn
					.append(
						$('<div></div>')
							.attr(attrs)
							.css(cssRules)
							.append(
								$('<h2></h2>'),
								$('<div class="dp-nav-prev"></div>')
									.append(
										$('<a class="dp-nav-prev-year" href="javascript:void(0)" title="' + $.dpText.TEXT_PREV_YEAR + '">&nbsp;</a>')
											.bind(
												'click',
												function()
												{
													return c._displayNewMonth.call(c, this, 0, -1);
												}
											),
										$('<a class="dp-nav-prev-month" href="javascript:void(0)" title="' + $.dpText.TEXT_PREV_MONTH + '">&nbsp;</a>')
											.bind(
												'click',
												function()
												{
													return c._displayNewMonth.call(c, this, -1, 0);
												}
											)
									),
								$('<div class="dp-nav-next"></div>')
									.append(
										$('<a class="dp-nav-next-year" href="javascript:void(0)" title="' + $.dpText.TEXT_NEXT_YEAR + '">&nbsp;</a>')
											.bind(
												'click',
												function()
												{
													return c._displayNewMonth.call(c, this, 0, 1);
												}
											),
										$('<a class="dp-nav-next-month" href="javascript:void(0)" title="' + $.dpText.TEXT_NEXT_MONTH + '">&nbsp;</a>')
											.bind(
												'click',
												function()
												{
													return c._displayNewMonth.call(c, this, 1, 0);
												}
											)
									),
								$('<div></div>')
									.attr('className', 'dp-calendar')
							)
							.bgIframe()
						);
					
				var $pop = this.inline ? $('.dp-popup', this.context) : $('#dp-popup');
				
				if (this.showYearNavigation == false) {
					$('.dp-nav-prev-year, .dp-nav-next-year', c.context).css('display', 'none');
				}
				if (this.displayClose) {
					$pop.append(
						$('<a href="javascript:void(0)" id="dp-close">' + $.dpText.TEXT_CLOSE + '</a>')
							.bind(
								'click',
								function()
								{
									c._closeCalendar();
									return false;
								}
							)
					);
				}
				c._renderCalendar();
				
				$(this.ele).trigger('dpDisplayed', $pop);
				
				if (!c.inline) {
					if (this.verticalPosition == $.dpConst.POS_BOTTOM) {
						$pop.css('top', eleOffset.top + $ele.height() - $pop.height() + c.verticalOffset);
					}
					if (this.horizontalPosition == $.dpConst.POS_RIGHT) {
						$pop.css('left', eleOffset.left + $ele.width() - $pop.width() + c.horizontalOffset);
					}
					$(document).bind('mousedown', this._checkMouse);
				}
			},
			setRenderCallback : function(a)
			{
				if (a && typeof(a) == 'function') {
					a = [a];
				}
				this.renderCallback = this.renderCallback.concat(a);
			},
			cellRender : function ($td, thisDate, month, year) {
				var c = this.dpController;
				var d = new Date(thisDate.getTime());
				
				// add our click handlers to deal with it when the days are clicked...
				
				$td.bind(
					'click',
					function()
					{
						var $this = $(this);
                        var input_value="";
                        /*add pwp*/
                        if(c.datetime){
                            input_value=$(c.ele).val();
                        }
                        /*end add pwp*/
                        
						if (!$this.is('.disabled')) {
							c.setSelected(d, !$this.is('.selected') || !c.selectMultiple);
							var s = c.isSelected(d);
							$(c.ele).trigger('dateSelected', [d, $td, s]);
							$(c.ele).trigger('change');
                            
                            /*add pwp*/
                            if(c.datetime){
                                var tmp_value=$(c.ele).val();
                                $(c.ele).val(input_value);
                                setDate($(c.ele),tmp_value);
                            }
                            /*end add pwp*/
                            
							if (c.closeOnSelect) {
								c._closeCalendar();
							} else {
								$this[s ? 'addClass' : 'removeClass']('selected');
							}
						}
					}
				);
				
				if (c.isSelected(d)) {
					$td.addClass('selected');
				}
				
				// call any extra renderCallbacks that were passed in
				for (var i=0; i<c.renderCallback.length; i++) {
					c.renderCallback[i].apply(this, arguments);
				}
				
				
			},
			// ele is the clicked button - only proceed if it doesn't have the class disabled...
			// m and y are -1, 0 or 1 depending which direction we want to go in...
			_displayNewMonth : function(ele, m, y) 
			{
				if (!$(ele).is('.disabled')) {
					this.setDisplayedMonth(this.displayedMonth + m, this.displayedYear + y);
					this._clearCalendar();
					this._renderCalendar();
					$(this.ele).trigger('dpMonthChanged', [this.displayedMonth, this.displayedYear]);
				}
				ele.blur();
				return false;
			},
			_renderCalendar : function()
			{
				// set the title...
				$('h2', this.context).html(Date.monthNames[this.displayedMonth] + ' ' + this.displayedYear);
				
				// render the calendar...
				$('.dp-calendar', this.context).renderCalendar(
					{
						month			: this.displayedMonth,
						year			: this.displayedYear,
						renderCallback	: this.cellRender,
						dpController	: this,
						hoverClass		: this.hoverClass
					}
				);
				
				// update the status of the control buttons and disable dates before startDate or after endDate...
				// TODO: When should the year buttons be disabled? When you can't go forward a whole year from where you are or is that annoying?
				if (this.displayedYear == this.startDate.getFullYear() && this.displayedMonth == this.startDate.getMonth()) {
					$('.dp-nav-prev-year', this.context).addClass('disabled');
					$('.dp-nav-prev-month', this.context).addClass('disabled');
					$('.dp-calendar td.other-month', this.context).each(
						function()
						{
							var $this = $(this);
							if (Number($this.text()) > 20) {
								$this.addClass('disabled');
							}
						}
					);
					var d = this.startDate.getDate();
					$('.dp-calendar td.current-month', this.context).each(
						function()
						{
							var $this = $(this);
							if (Number($this.text()) < d) {
								$this.addClass('disabled');
							}
						}
					);
				} else {
					$('.dp-nav-prev-year', this.context).removeClass('disabled');
					$('.dp-nav-prev-month', this.context).removeClass('disabled');
					var d = this.startDate.getDate();
					if (d > 20) {
						// check if the startDate is last month as we might need to add some disabled classes...
						var sd = new Date(this.startDate.getTime());
						sd.addMonths(1);
						if (this.displayedYear == sd.getFullYear() && this.displayedMonth == sd.getMonth()) {
							$('dp-calendar td.other-month', this.context).each(
								function()
								{
									var $this = $(this);
									if (Number($this.text()) < d) {
										$this.addClass('disabled');
									}
								}
							);
						}
					}
				}
				if (this.displayedYear == this.endDate.getFullYear() && this.displayedMonth == this.endDate.getMonth()) {
					$('.dp-nav-next-year', this.context).addClass('disabled');
					$('.dp-nav-next-month', this.context).addClass('disabled');
					$('.dp-calendar td.other-month', this.context).each(
						function()
						{
							var $this = $(this);
							if (Number($this.text()) < 14) {
								$this.addClass('disabled');
							}
						}
					);
					var d = this.endDate.getDate();
					$('.dp-calendar td.current-month', this.context).each(
						function()
						{
							var $this = $(this);
							if (Number($this.text()) > d) {
								$this.addClass('disabled');
							}
						}
					);
				} else {
					$('.dp-nav-next-year', this.context).removeClass('disabled');
					$('.dp-nav-next-month', this.context).removeClass('disabled');
					var d = this.endDate.getDate();
					if (d < 13) {
						// check if the endDate is next month as we might need to add some disabled classes...
						var ed = new Date(this.endDate.getTime());
						ed.addMonths(-1);
						if (this.displayedYear == ed.getFullYear() && this.displayedMonth == ed.getMonth()) {
							$('.dp-calendar td.other-month', this.context).each(
								function()
								{
									var $this = $(this);
									if (Number($this.text()) > d) {
										$this.addClass('disabled');
									}
								}
							);
						}
					}
				}
			},
			_closeCalendar : function(programatic, ele)
			{
				if (!ele || ele == this.ele)
				{
					$(document).unbind('mousedown', this._checkMouse);
					this._clearCalendar();
					$('#dp-popup a').unbind();
					$('#dp-popup').empty().remove();
					if (!programatic) {
						$(this.ele).trigger('dpClosed', [this.getSelected()]);
					}
				}
			},
			// empties the current dp-calendar div and makes sure that all events are unbound
			// and expandos removed to avoid memory leaks...
			_clearCalendar : function()
			{
				// TODO.
				$('.dp-calendar td', this.context).unbind();
				$('.dp-calendar', this.context).empty();
			}
		}
	);
	
	// static constants
	$.dpConst = {
		SHOW_HEADER_NONE	:	0,
		SHOW_HEADER_SHORT	:	1,
		SHOW_HEADER_LONG	:	2,
		POS_TOP				:	0,
		POS_BOTTOM			:	1,
		POS_LEFT			:	0,
		POS_RIGHT			:	1
	};
	// localisable text
	$.dpText = {
		TEXT_PREV_YEAR		:	'Previous year',
		TEXT_PREV_MONTH		:	'Previous month',
		TEXT_NEXT_YEAR		:	'Next year',
		TEXT_NEXT_MONTH		:	'Next month',
		TEXT_CLOSE			:	'Close',
		TEXT_CHOOSE_DATE	:	''//Choose date
	};
	// version
	$.dpVersion = '$Id: jquery.datePicker.js 3739 2007-10-25 13:55:30Z kelvin.luck $';

	function _getController(ele)
	{
		if (ele._dpId) return $.event._dpCache[ele._dpId];
		return false;
	};
	
	// make it so that no error is thrown if bgIframe plugin isn't included (allows you to use conditional
	// comments to only include bgIframe where it is needed in IE without breaking this plugin).
	if ($.fn.bgIframe == undefined) {
		$.fn.bgIframe = function() {return this; };
	};


	// clean-up
	$(window)
		.bind('unload', function() {
			var els = $.event._dpCache || [];
			for (var i in els) {
				$(els[i].ele)._dpDestroy();
			}
		});
		
	
})(jQuery);

//jquery.bgiframe.js

/* Copyright (c) 2006 Brandon Aaron (http://brandonaaron.net)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 *
 * $LastChangedDate: 2007-07-21 18:44:59 -0500 (Sat, 21 Jul 2007) $
 * $Rev: 2446 $
 *
 * Version 2.1.1
 */

(function($){

/**
 * The bgiframe is chainable and applies the iframe hack to get 
 * around zIndex issues in IE6. It will only apply itself in IE6 
 * and adds a class to the iframe called 'bgiframe'. The iframe
 * is appeneded as the first child of the matched element(s) 
 * with a tabIndex and zIndex of -1.
 * 
 * By default the plugin will take borders, sized with pixel units,
 * into account. If a different unit is used for the border's width,
 * then you will need to use the top and left settings as explained below.
 *
 * NOTICE: This plugin has been reported to cause perfromance problems
 * when used on elements that change properties (like width, height and
 * opacity) a lot in IE6. Most of these problems have been caused by 
 * the expressions used to calculate the elements width, height and 
 * borders. Some have reported it is due to the opacity filter. All 
 * these settings can be changed if needed as explained below.
 *
 * @example $('div').bgiframe();
 * @before <div><p>Paragraph</p></div>
 * @result <div><iframe class="bgiframe".../><p>Paragraph</p></div>
 *
 * @param Map settings Optional settings to configure the iframe.
 * @option String|Number top The iframe must be offset to the top
 * 		by the width of the top border. This should be a negative 
 *      number representing the border-top-width. If a number is 
 * 		is used here, pixels will be assumed. Otherwise, be sure
 *		to specify a unit. An expression could also be used. 
 * 		By default the value is "auto" which will use an expression 
 * 		to get the border-top-width if it is in pixels.
 * @option String|Number left The iframe must be offset to the left
 * 		by the width of the left border. This should be a negative 
 *      number representing the border-left-width. If a number is 
 * 		is used here, pixels will be assumed. Otherwise, be sure
 *		to specify a unit. An expression could also be used. 
 * 		By default the value is "auto" which will use an expression 
 * 		to get the border-left-width if it is in pixels.
 * @option String|Number width This is the width of the iframe. If
 *		a number is used here, pixels will be assume. Otherwise, be sure
 * 		to specify a unit. An experssion could also be used.
 *		By default the value is "auto" which will use an experssion
 * 		to get the offsetWidth.
 * @option String|Number height This is the height of the iframe. If
 *		a number is used here, pixels will be assume. Otherwise, be sure
 * 		to specify a unit. An experssion could also be used.
 *		By default the value is "auto" which will use an experssion
 * 		to get the offsetHeight.
 * @option Boolean opacity This is a boolean representing whether or not
 * 		to use opacity. If set to true, the opacity of 0 is applied. If
 *		set to false, the opacity filter is not applied. Default: true.
 * @option String src This setting is provided so that one could change 
 *		the src of the iframe to whatever they need.
 *		Default: "javascript:false;"
 *
 * @name bgiframe
 * @type jQuery
 * @cat Plugins/bgiframe
 * @author Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net)
 */
$.fn.bgIframe = $.fn.bgiframe = function(s) {
	// This is only for IE6
	if ( $.browser.msie && /6.0/.test(navigator.userAgent) ) {
		s = $.extend({
			top     : 'auto', // auto == .currentStyle.borderTopWidth
			left    : 'auto', // auto == .currentStyle.borderLeftWidth
			width   : 'auto', // auto == offsetWidth
			height  : 'auto', // auto == offsetHeight
			opacity : true,
			src     : 'javascript:false;'
		}, s || {});
		var prop = function(n){return n&&n.constructor==Number?n+'px':n;},
		    html = '<iframe class="bgiframe"frameborder="0"tabindex="-1"src="'+s.src+'"'+
		               'style="display:block;position:absolute;z-index:-1;'+
			               (s.opacity !== false?'filter:Alpha(Opacity=\'0\');':'')+
					       'top:'+(s.top=='auto'?'expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+\'px\')':prop(s.top))+';'+
					       'left:'+(s.left=='auto'?'expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+\'px\')':prop(s.left))+';'+
					       'width:'+(s.width=='auto'?'expression(this.parentNode.offsetWidth+\'px\')':prop(s.width))+';'+
					       'height:'+(s.height=='auto'?'expression(this.parentNode.offsetHeight+\'px\')':prop(s.height))+';'+
					'"/>';
		return this.each(function() {
			if ( $('> iframe.bgiframe', this).length == 0 )
				this.insertBefore( document.createElement(html), this.firstChild );
		});
	}
	return this;
};

})(jQuery);


//jquery.clockpick.js
eval(function(p,a,c,k,e,r){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('u.27.2Q=7(k,o){x p={1I:8,1J:18,1p:28,S:4,G:y,29:\'1q\',2a:\'2b\',17:1K,19:y,2c:1,2d:1};3(k){u.2R(p,k)};x o=o||7(){},v=(p.2a==\'2b\');2e();u(1r)[p.29](7(e){x g=1r,$T=u(1r),$H=u("H");3(!p.17){$T.1a("M").1L("M",1b)}9{x j=u("[2f="+p.17+"]");j.1a("M").1L("M",1b)[0].2g();j.1L("1q",7(){j.1a("M")})}u("#1M,#1s").2S();$q=u("<A z=\'1M\' E=\'1t\' />").1u($H);!p.19?$q.B("2h",p.2c):1K;1c($q);$N=u("<A E=\'2i\' z=\'N\' />").1u($H);$O=u("<A E=\'2i\' z=\'O\' />").1u($H);3(p.1p){$C=u("<A z=\'1s\' E=\'1t\' />").1u($H);!p.19?$C.B("2h",p.2d):1K;1c($C)}3(!v){$q.B("U","2j");$C.B("U","2j")}9{$N.1v(\'2k\');$O.1v(\'2k\')}2l();2m();7 2l(){x c=1;2n(h=p.1I;h<=p.1J;h++){3(h==12){c=1}F=((!p.G&&h>12)?h-12:h);3(!p.G&&h==0){F=\'12\'}3(p.G&&h<10){F=\'0\'+F}$V=u("<A E=\'W\' z=\'2o"+h+"I"+c+"\'>"+F+1w(h)+"</A>");3(p.G){$V.U(20)}1c($V);3(!v){$V.B("2p","D")}(h<12)?$N.P($V):$O.P($V);c++}$q.P($N);!v?$q.P("<A 2q=\'2r:D\' />"):\'\';$q.P($O)}7 2s(h){1N=h;F=(!p.G&&h>12)?h-12:h;3(!p.G&&h==0){F=\'12\'}3(p.G&&h<10){F=\'0\'+F}$C.2T();x n=1x/p.S,1y=1w(1N),1O=1;2n(m=0;m<1x;m=m+n){$1z=u("<A E=\'1P\' z=\'"+1N+"I"+m+"\'>"+F+":"+((m<10)?"0":"")+m+1y+"</A>");3(!v){$1z.B("2p","D");3(p.S>6&&1O==p.S/2+1){$C.P("<A 2q=\'2r:D\' />")}}$C.P($1z);1c($1z);1O++}}7 1w(a){3(!p.G){w(a>=12)?\' 2U\':\' 2V\'}9{w\'\'}}7 2m(){3(e.1Q!=\'2g\'){$q.B("D",e.2t-5+\'X\').B("L",e.2u-(2W.2X($q.Y()/2))+\'X\');1R($q)}9{$T.2Y($q)}$q.2Z(\'2v\');3(p.19)1S($q)}7 1R(a){x b=J.Z.1T?J.Z.1T:J.H.1T;x c=J.Z.1U?J.Z.1U:J.H.1U;x t=2w(a.B("L"));x l=2w(a.B("D"));x d=J.Z.1V?J.Z.1V:J.H.1V;3(t<=d&&!a.1A("#1s")){a.B("L",d+10+\'X\')}9 3(t+a.Y()-d>b){a.B("L",d+b-a.Y()-10+\'X\')}3(l<=0){a.B("D",\'30\')}}7 1S(a){3(31 u.27.1W==\'7\')a.1W();9 1X(\'1W 32 33 34.\')}7 1c(a){3(a.Q("z")==\'1M\'){a.1B(7(e){2x(e)})}9 3(a.Q("z")==\'1s\'){a.1B(7(e){2y(e)})}9 3(a.Q("E")==\'W\'){a.1C(7(e){1D(a,e)});a.1B(7(){1E(a)});a.1q(7(){2z(a)})}9 3(a.Q("E")==\'1P\'){a.1C(7(){1Y(a)});a.1B(7(){1Z(a)});a.1q(7(){2A(a)})}};7 2x(e){2B{t=(e.1F)?e.1F:e.2C;3(!(u(t).1A("A[E^=1t], 2D"))){R()}}2E(e){R()}}7 2y(e){2B{t=(e.1F)?e.1F:e.2C;3(!(u(t).1A("A[E^=1t], 2D"))){R()}}2E(e){R()}}7 1D(a,e){x h=a.Q("z").11(\'I\')[1],i=a.Q("z").11(\'I\')[2],l,t;a.1v("14");3(p.1p){$C.2F();2s(h);3(v){t=e.1Q==\'1C\'?e.2u-15:$q.16().L+2+(a.Y()*i);3(h<12)l=$q.16().D-$C.U()-2;9 l=$q.16().D+$q.U()+2}9{l=(e.1Q==\'1C\')?e.2t-10:$q.16().D+(a.U()-5)*i;3(h<12){t=$q.16().L-$C.Y()-2}9{t=$q.16().L+$q.Y()}}$C.B("D",l+\'X\').B("L",t+\'X\');1R($C);$C.35();3(p.19)1S($C)}w y}7 1E(a){a.2G("14");w y}7 2z(a){h=a.Q("z").11(\'I\')[1];1y=1w(h);1d=a.1e();3(1d.2H(\' \')!=-1){21=1d.36(0,1d.2H(\' \'))}9{21=1d}a.1e(21+\':3a\'+1y);22(a);R()}7 1Y(a){a.1v("14");w y}7 1Z(a){a.2G("14");w y}7 2A(a){22(a);R()}7 22(a){3(!p.17){g.3b=a.1e()}9{u("3c[2f="+p.17+"]").3d(a.1e())}o.3e($T,[a.1e()]);$T.1a("M",1b)}7 R(){3(p.1p){$C.2F()}$q.3f(\'2v\');$T.1a("M",1b)}7 1b(e){x d=$("A.14").1G()?$("A.14"):$("A.W:2I"),K=d.1A(".W")?\'1H\':\'23\',2J=(K==\'1H\')?d[0].z.11(\'I\')[2]:0,h=(K==\'23\')?d[0].z.11(\'I\')[0]:d[0].z.11(\'I\')[1];3(K==\'23\'){x f=h<12?\'1f\':\'1g\'}9{x f=h<12?\'1h\':\'1i\'}7 24(a){3(a.2K().1G()){1j(K+\'2L($1k)\');1j(K+\'2M($1k.2K(), e)\')}9{w y}}7 25(a){3(a.2N().1G()){1j(K+\'2L($1k)\');1j(K+\'2M($1k.2N(), e)\')}9{w y}}7 1l(a){x b=h>=12?\'#N\':\'#O\';$26=u(".W[z$=I"+2J+"]",b);3($26.1G()){1E(a);1D($26,e)}9{w y}}7 1m(a){1E(a);1Y($(".1P:2I"))}7 1n(a){1Z(a);x b=h>=12?\'#O\':\'#N\';x c=u(".W[z^=2o"+h+"]",b);1D(c,e)}1o(e.3g){r 37:3(v){1o(f){r\'1f\':w y;s;r\'1g\':1n(d);s;r\'1h\':1m(d);s;r\'1i\':1l(d);s}}9{24(d)}s;r 38:3(v){24(d)}9{1o(f){r\'1f\':w y;s;r\'1g\':1n(d);s;r\'1h\':1m(d);s;r\'1i\':1l(d);s}}s;r 39:3(v){1o(f){r\'1f\':1n(d);s;r\'1g\':w y;s;r\'1h\':1l(d);s;r\'1i\':1m(d);s}}9{25(d)}s;r 3h:3(v){25(d)}9{1o(f){r\'1f\':1n(d);s;r\'1g\':w y;s;r\'1h\':1l(d);s;r\'1i\':1m(d);s}}s;r 13:1j(K+\'3i($1k)\');s;3j:w 28}w y}w y});7 2e(){3(p.1I>=p.1J){1X(\'2O - 3k 1H 2P 3l 3m 3n 3o 1H.\');w y}9 3(1x%p.S!=0){1X(\'2O - 3p S 2P 3q 3r 3s 1x.\');w y}}w 1r}',62,215,'|||if||||function||else|||||||||||||||||hourcont|case|break||jQuery||return|var|false|id|div|css|mc|left|class|displayhours|military|body|_|document|divtype|top|keydown|hourcol1|hourcol2|append|attr|cleardivs|minutedivisions|self|width|hd|CP_hour|px|height|documentElement||split|||CP_over||offset|valuefield||useBgiframe|unbind|keyhandler|binder|str|text|m1|m2|h1|h2|eval|obj|hourtohour|hourtominute|minutetohour|switch|showminutes|click|this|CP_minutecont|CP|appendTo|addClass|set_tt|60|tt|md|is|mouseout|mouseover|hourdiv_over|hourdiv_out|toElement|size|hour|starthour|endhour|null|bind|CP_hourcont|realhours|counter|CP_minute|type|rectify|bgi|clientHeight|clientWidth|scrollTop|bgIframe|alert|minutediv_over|minutediv_out||cleanstr|setval|minute|divprev|divnext|newobj|fn|true|event|layout|vertical|hoursopacity|minutesopacity|errorcheck|name|focus|opacity|CP_hourcol|auto|floatleft|renderhours|putcontainer|for|hr_|float|style|clear|renderminutes|pageX|pageY|fast|parseInt|hourcont_out|minutecont_out|hourdiv_click|minutediv_click|try|relatedTarget|iframe|catch|hide|removeClass|indexOf|first|hi|prev|div_out|div_over|next|Error|must|clockpick|extend|remove|empty|PM|AM|Math|floor|after|slideDown|10px|typeof|plugin|not|loaded|show|substring||||00|value|input|val|apply|slideUp|keyCode|40|div_click|default|start|be|less|than|end|param|divide|evenly|into'.split('|'),0,{}))

//jquery.treeview.js
/*
 * Treeview 1.4 - jQuery plugin to hide and show branches of a tree
 * 
 * http://bassistance.de/jquery-plugins/jquery-plugin-treeview/
 * http://docs.jquery.com/Plugins/Treeview
 *
 * Copyright (c) 2007 Jörn Zaefferer
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Revision: $Id: jquery.treeview.js 4684 2008-02-07 19:08:06Z joern.zaefferer $
 *
 */

;(function($) {

	$.extend($.fn, {
		swapClass: function(c1, c2) {
			var c1Elements = this.filter('.' + c1);
			this.filter('.' + c2).removeClass(c2).addClass(c1);
			c1Elements.removeClass(c1).addClass(c2);
			return this;
		},
		replaceClass: function(c1, c2) {
			return this.filter('.' + c1).removeClass(c1).addClass(c2).end();
		},
		hoverClass: function(className) {
			className = className || "hover";
			return this.hover(function() {
				$(this).addClass(className);
			}, function() {
				$(this).removeClass(className);
			});
		},
		heightToggle: function(animated, callback) {
			animated ?
				this.animate({ height: "toggle" }, animated, callback) :
				this.each(function(){
					jQuery(this)[ jQuery(this).is(":hidden") ? "show" : "hide" ]();
					if(callback)
						callback.apply(this, arguments);
				});
		},
		heightHide: function(animated, callback) {
			if (animated) {
				this.animate({ height: "hide" }, animated, callback);
			} else {
				this.hide();
				if (callback)
					this.each(callback);				
			}
		},
		prepareBranches: function(settings) {
			if (!settings.prerendered) {
				// mark last tree items
				this.filter(":last-child:not(ul)").addClass(CLASSES.last);
				// collapse whole tree, or only those marked as closed, anyway except those marked as open
				this.filter((settings.collapsed ? "" : "." + CLASSES.closed) + ":not(." + CLASSES.open + ")").find(">ul").hide();
			}
			// return all items with sublists
			return this.filter(":has(>ul)");
		},
		applyClasses: function(settings, toggler) {
			this.filter(":has(>ul):not(:has(>a))").find(">span").click(function(event) {
				toggler.apply($(this).next());
			}).add( $("a", this) ).hoverClass();
			
			if (!settings.prerendered) {
				// handle closed ones first
				this.filter(":has(>ul:hidden)")
						.addClass(CLASSES.expandable)
						.replaceClass(CLASSES.last, CLASSES.lastExpandable);
						
				// handle open ones
				this.not(":has(>ul:hidden)")
						.addClass(CLASSES.collapsable)
						.replaceClass(CLASSES.last, CLASSES.lastCollapsable);
						
	            // create hitarea
				this.prepend("<div class=\"" + CLASSES.hitarea + "\"/>").find("div." + CLASSES.hitarea).each(function() {
					var classes = "";
					$.each($(this).parent().attr("class").split(" "), function() {
						classes += this + "-hitarea ";
					});
					$(this).addClass( classes );
				});
			}
			
			// apply event to hitarea
			this.find("div." + CLASSES.hitarea).click( toggler );
		},
		treeview: function(settings) {
			
			settings = $.extend({
				cookieId: "treeview"
			}, settings);
			
			if (settings.add) {
				return this.trigger("add", [settings.add]);
			}
			
			if ( settings.toggle ) {
				var callback = settings.toggle;
				settings.toggle = function() {
					return callback.apply($(this).parent()[0], arguments);
				};
			}
		
			// factory for treecontroller
			function treeController(tree, control) {
				// factory for click handlers
				function handler(filter) {
					return function() {
						// reuse toggle event handler, applying the elements to toggle
						// start searching for all hitareas
						toggler.apply( $("div." + CLASSES.hitarea, tree).filter(function() {
							// for plain toggle, no filter is provided, otherwise we need to check the parent element
							return filter ? $(this).parent("." + filter).length : true;
						}) );
						return false;
					};
				}
				// click on first element to collapse tree
				$("a:eq(0)", control).click( handler(CLASSES.collapsable) );
				// click on second to expand tree
				$("a:eq(1)", control).click( handler(CLASSES.expandable) );
				// click on third to toggle tree
				$("a:eq(2)", control).click( handler() ); 
			}
		
			// handle toggle event
			function toggler() {
				$(this)
					.parent()
					// swap classes for hitarea
					.find(">.hitarea")
						.swapClass( CLASSES.collapsableHitarea, CLASSES.expandableHitarea )
						.swapClass( CLASSES.lastCollapsableHitarea, CLASSES.lastExpandableHitarea )
					.end()
					// swap classes for parent li
					.swapClass( CLASSES.collapsable, CLASSES.expandable )
					.swapClass( CLASSES.lastCollapsable, CLASSES.lastExpandable )
					// find child lists
					.find( ">ul" )
					// toggle them
					.heightToggle( settings.animated, settings.toggle );
				if ( settings.unique ) {
					$(this).parent()
						.siblings()
						// swap classes for hitarea
						.find(">.hitarea")
							.replaceClass( CLASSES.collapsableHitarea, CLASSES.expandableHitarea )
							.replaceClass( CLASSES.lastCollapsableHitarea, CLASSES.lastExpandableHitarea )
						.end()
						.replaceClass( CLASSES.collapsable, CLASSES.expandable )
						.replaceClass( CLASSES.lastCollapsable, CLASSES.lastExpandable )
						.find( ">ul" )
						.heightHide( settings.animated, settings.toggle );
				}
			}
			
			function serialize() {
				function binary(arg) {
					return arg ? 1 : 0;
				}
				var data = [];
				branches.each(function(i, e) {
					data[i] = $(e).is(":has(>ul:visible)") ? 1 : 0;
				});
				$.cookie(settings.cookieId, data.join("") );
			}
			
			function deserialize() {
				var stored = $.cookie(settings.cookieId);
				if ( stored ) {
					var data = stored.split("");
					branches.each(function(i, e) {
						$(e).find(">ul")[ parseInt(data[i]) ? "show" : "hide" ]();
					});
				}
			}
			
			// add treeview class to activate styles
			this.addClass("treeview");
			
			// prepare branches and find all tree items with child lists
			var branches = this.find("li").prepareBranches(settings);
			
			switch(settings.persist) {
			case "cookie":
				var toggleCallback = settings.toggle;
				settings.toggle = function() {
					serialize();
					if (toggleCallback) {
						toggleCallback.apply(this, arguments);
					}
				};
				deserialize();
				break;
			case "location":
				var current = this.find("a").filter(function() { return this.href.toLowerCase() == location.href.toLowerCase(); });
				if ( current.length ) {
					current.addClass("selected").parents("ul, li").add( current.next() ).show();
				}
				break;
			}
			
			branches.applyClasses(settings, toggler);
				
			// if control option is set, create the treecontroller and show it
			if ( settings.control ) {
				treeController(this, settings.control);
				$(settings.control).show();
			}
			
			return this.bind("add", function(event, branches) {
				$(branches).prev()
					.removeClass(CLASSES.last)
					.removeClass(CLASSES.lastCollapsable)
					.removeClass(CLASSES.lastExpandable)
				.find(">.hitarea")
					.removeClass(CLASSES.lastCollapsableHitarea)
					.removeClass(CLASSES.lastExpandableHitarea);
				$(branches).find("li").andSelf().prepareBranches(settings).applyClasses(settings, toggler);
			});
		}
	});
	
	// classes used by the plugin
	// need to be styled via external stylesheet, see first example
	var CLASSES = $.fn.treeview.classes = {
		open: "open",
		closed: "closed",
		expandable: "expandable",
		expandableHitarea: "expandable-hitarea",
		lastExpandableHitarea: "lastExpandable-hitarea",
		collapsable: "collapsable",
		collapsableHitarea: "collapsable-hitarea",
		lastCollapsableHitarea: "lastCollapsable-hitarea",
		lastCollapsable: "lastCollapsable",
		lastExpandable: "lastExpandable",
		last: "last",
		hitarea: "hitarea"
	};
	
	// provide backwards compability
	$.fn.Treeview = $.fn.treeview;
	
})(jQuery);

;(function($) {

function load(settings, root, child, container) {
    $.getJSON(settings.url, {root: root}, function(response) {
        function createNode(parent) {
            var current = $("<li/>").attr("id", this.id || "").html("<span>" + this.text + "</span>").appendTo(parent);
            if (this.classes) {
                current.children("span").addClass(this.classes);
            }
            if (this.expanded) {
                current.addClass("open");
            }
            if (this.hasChildren || this.children && this.children.length) {
                var branch = $("<ul/>").appendTo(current);
                if (this.hasChildren) {
                    current.addClass("hasChildren");
                    createNode.call({
                        text:"placeholder",
                        id:"placeholder",
                        children:[]
                    }, branch);
                }
                if (this.children && this.children.length) {
                    $.each(this.children, createNode, [branch])
                }
            }
        }
        $.each(response, createNode, [child]);
        $(container).treeview({add: child});
    });
}

var proxied = $.fn.treeview;
$.fn.treeview = function(settings) {
    settings = settings || {};
    if (!settings.url) {
        return proxied.apply(this, arguments);
    }
    var container = this;
    load(settings, "source", this, container);
    var userToggle = settings.toggle;
    return proxied.call(this, $.extend({}, settings, {
        collapsed: true,
        toggle: function() {
            var $this = $(this);
            if ($this.hasClass("hasChildren")) {
                var childList = $this.removeClass("hasChildren").find("ul");
                childList.empty();
                load(settings, this.id, childList, container);
            }
            if (userToggle) {
                userToggle.apply(this, arguments);
            }
        }
    }));
};

})(jQuery);



//jquery.swift.js

// jQuery - Swift - Copyright TJ Holowaychuk <tj@vision-media.ca> (MIT Licensed)

;(function($){
  
  // --- Swift instances
  
  var instances = []
  
  /**
   * Generate input buttons from the given _hash_.
   *
   * @param  {object} hash
   * @return {string}
   * @api private
   */
  
  function buttons(hash) {
    var buf = ''
    if (!hash) throw 'swift must be passed a hash of buttons'
    for (var key in hash)
      buf += '<input type="button" name="' + key + '" value="' + gettext(key) + '" />'
    return buf
  }
  
  /**
   * Generate a swift instance with the given _options_.
   *
   * Options:
   *
   *  - body:    arbitrary text or markup placed before buttons
   *  - buttons: hash of buttons passed to buttons()
   *
   * @param  {options} hash
   * @return {jQuery}
   * @api private
   */
  
  function template(options) {
    options = options || {}
    var instance = $('<div class="swift east">'
      +'<div class="wrapper">'
        +'<div class="body">' + (options.body || '') + 
		'</div><div class="buttons">'+
        buttons(options.buttons) + '</div>'
	  +'</div>'
    +'</div>')
    instances.push(instance)
    return instance
  }
  
  /**
   * Close all swift instances with the given _options_.
   *
   * Options:
   *
   *  - duration:  animation duration in milliseconds
   *
   * @param  {object} options
   * @api private
   */
  
  function close(options) {
    var instance
    options = options || {}
    while (instance = instances.pop())
      instance.animate({
        left: instance.offset().left - 50,
        opacity: 0
      }, options.duration || 500, function(){
        $(this).remove()
      })
  }
  
  /**
   * Create a swift instance applied to the first element
   * in the collection. Self-positions based on it's offset.
   *
   * Returns the collection of swift elements.
   *
   * Options:
   *
   *  - duration:  animation duration in milliseconds 
   *  - body:      arbitrary text or markup placed before buttons
   *  - buttons:   hash of buttons passed to buttons()
   *
   * @param  {object} options
   * @return {jQuery}
   * @api public
   */
  
  $.fn.swift = function(options) {
    close(options = options || {})
    var self, target = this, left = this.offset().left + this.width()
    return (self = template(options)).appendTo('body').css({
      position: 'absolute',
      top: this.offset().top,
      left: left - 30,
      opacity: 0
    })
    .animate({
      left: left,
      opacity: 1
    }, options.duration || 500)
    .find(':button')
    .click(function(e){
      e.target = target
      var name = $(this).attr('name')
      if (name in options.buttons)
        if (options.buttons[name](self, e) !== false)
          close()
    })
    .end()
  }
  
})(jQuery)

//picture.js
function show_during_times(t1,t2)
{	
	
	if(t1==t2)
		return "";
	else
		return getDuring_time_Str(t1)+"-"+getDuring_time_Str(t2);
}
function getDuring_time_Str(t)
{
	var sec=1/24/60/60;
	t_hour=parseInt((t+sec)*24*60/60)
	t_minute=Math.round((t+sec)*24*60%60)
	return getTimeStr(t_hour)+":"+getTimeStr(t_minute);
	
}
function getTimeStr(t)
{	if(t<10)
		return "0"+t;
	else
		return t;
}
function normalP(v)
{	
	return v*810/10000;  
}
function getTZDateAlt(index,sdate)
{
	if(sdate==undefined)
        return "";
    var tmp=new Date(sdate.valueOf()+index*1000*3600*24);
	var m="00"+(tmp.getMonth()+1);
	var d="00"+tmp.getDate();
	return	tmp.getFullYear()+"-"+m.substring(m.length-2)+"-"+d.substring(d.length-2);
}
function createTZTable(tzData, dayLabelFun, dayCount,sDate)
{
	tzData=tzData.data
  var tz, i, dayi=0, curDay=-1, timei=0, temp=[];
  html='<div id="id_timezone_header"></div><div id="id_timezone_body"><table class="timezone-table">';//<tr><td width="60px">&nbsp;</td><td class="timezone-header">&nbsp;</td></tr>
  for(i=0;i<tzData.length || temp.length>0;)
  {
    if(temp.length==0)
		tz=tzData[i]
	else
	{
		tz=temp[0];
		temp=[];
	}
	dayi=Math.floor(tz.StartTime)
    while(curDay<dayi) //new a day row
	{
		curDay+=1;
		if(curDay<dayi) html+='</td></tr>';
		html+='<tr>'
		if(sDate==undefined) 
			html+='<td class="timezones-week">'+dayLabelFun(curDay)+'</td><td class="timezones-container">'
		else
			html+='<td class="timezones-week">'+dayLabelFun(curDay,sDate)+'</td><td class="timezones-container" >'
		timei=0;
	}
	var dayi2=Math.floor(tz.EndTime)
	var time1=Math.round((tz.StartTime-Math.floor(tz.StartTime))*10000);
	var time2=Math.round((tz.EndTime-Math.floor(tz.EndTime))*10000);
	if(dayi2>dayi) 
	{
		var obj={}
		for (f in tz) { obj[f]=tz[f] }
		obj.StartTime=dayi+1;
		temp=[obj];
		time2=10000;
	}
	if(time1>timei) html+='<div style="width: '+normalP(time1-timei)+'px;" class="tzbar space"></div>'
	html+='<div alt0="'+tz['StartTime']+'" alt1="'+tz['EndTime']+'" alt2="'+getTZDateAlt(curDay,sDate)+'" alt4="'+tz['SchClassID']+'" style="text-align: center; width: '+normalP(time2-time1)+'px;'+
		(tz['Color']==undefined?' ':' background-color: #'+(tz['Color']).toString(16)+' ')+
		'" class="tzbar"><span alt3="'+tz['SchName']+'" style="color:red;font-size:10px;vertical-align:top;">'+show_during_times(tz.StartTime-Math.floor(tz.StartTime),tz.EndTime-Math.floor(tz.EndTime))+'</span></div>'
	timei=time2;
	if(temp.length==0)
		i+=1;
  }
  html+='</td></tr>'
  curDay+=1;
  if(dayCount!=undefined)
  while(curDay<dayCount)
  {
	if(sDate==undefined)
		html+='<tr><td>'+dayLabelFun(curDay)+'</td><td class="timezones-container"></td></tr>'
    else
		html+='<tr><td>'+dayLabelFun(curDay,sDate)+'</td><td class="timezones-container"></td></tr>'
    curDay+=1;
  }
  html+='<tr style="background: #ccc;display:none;"><td colspan="2" style="height:2px;"></td></tr></table></div>'
  return html
}

//jquery.progressbar.min.js

(function($){$.extend({progressBar:new function(){this.defaults={increment:2,speed:15,showText:true,width:120,boxImage:'/media/images/progressbar.gif',barImage:{0:'/media/images/progressbg_red.gif',30:'/media/images/progressbg_orange.gif',70:'/media/images/progressbg_green.gif'},height:12};this.construct=function(arg1,arg2){var argpercentage=null;var argconfig=null;if(arg1!=null){if(!isNaN(arg1)){argpercentage=arg1;if(arg2!=null){argconfig=arg2;}}else{argconfig=arg1;}}
return this.each(function(child){var pb=this;if(argpercentage!=null&&this.bar!=null&&this.config!=null){this.config.tpercentage=argpercentage;if(argconfig!=null)
pb.config=$.extend(this.config,argconfig);}else{var $this=$(this);var config=$.extend({},$.progressBar.defaults,argconfig);var percentage=argpercentage;if(argpercentage==null)
var percentage=$this.html().replace("%","");$this.html("");var bar=document.createElement('img');var text=document.createElement('span');bar.id=this.id+"_percentImage";text.id=this.id+"_percentText";bar.title=percentage+"%";bar.alt=percentage+"%";bar.src=config.boxImage;bar.width=config.width;var $bar=$(bar);var $text=$(text);this.bar=$bar;this.ntext=$text;this.config=config;this.config.cpercentage=0;this.config.tpercentage=percentage;$bar.css("width",config.width+"px");$bar.css("height",config.height+"px");$bar.css("background-image","url("+getBarImage(this.config.cpercentage,config)+")");$bar.css("padding","0");$bar.css("margin","0");$this.append($bar);$this.append($text);}
function getBarImage(percentage,config){var image=config.barImage;if(typeof(config.barImage)=='object'){for(var i in config.barImage){if(percentage>=parseInt(i)){image=config.barImage[i];}else{break;}}}
return image;}
var t=setInterval(function(){var config=pb.config;var cpercentage=parseInt(config.cpercentage);var tpercentage=parseInt(config.tpercentage);var increment=parseInt(config.increment);var bar=pb.bar;var text=pb.ntext;var pixels=config.width/100;bar.css("background-image","url("+getBarImage(cpercentage,config)+")");bar.css("background-position",(((config.width*-1))+(cpercentage*pixels))+'px 50%');if(config.showText)
text.html(" "+Math.round(cpercentage)+"%");if(cpercentage>tpercentage){if(cpercentage-increment<tpercentage){pb.config.cpercentage=0+tpercentage}else{pb.config.cpercentage-=increment;}}
else if(pb.config.cpercentage<pb.config.tpercentage){if(cpercentage+increment>tpercentage){pb.config.cpercentage=tpercentage}else{pb.config.cpercentage+=increment;}}
else{clearInterval(t);}},pb.config.speed);});};}});$.fn.extend({progressBar:$.progressBar.construct});})(jQuery);
