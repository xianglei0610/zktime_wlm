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
	if (tz['StartTime']==0 && tz['EndTime']==0 ){
		
	}else{
		html+='<div alt0="'+tz['StartTime']+'" alt1="'+tz['EndTime']+'" alt2="'+getTZDateAlt(curDay,sDate)+'" alt4="'+tz['SchClassID']+'" style="text-align: center; width:100%;'+
			(tz['Color']==undefined?' ':' background-color: #'+(tz['Color']).toString(16)+' ')+
			'" class="tzbar"><span title="'+tz['SchName']+'" alt3="'+tz['SchName']+'" style="color:red;font-size:10px;vertical-align:top;">'+show_during_times(tz.StartTime-Math.floor(tz.StartTime),tz.EndTime-Math.floor(tz.EndTime))+'</span></div>'
	}
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
		html+='<tr><td class="timezones-week">'+dayLabelFun(curDay)+'</td><td class="timezones-container"><div style="width:100%;"></div></td></tr>'
    else
		html+='<tr><td class="timezones-week">'+dayLabelFun(curDay,sDate)+'</td><td class="timezones-container"><div style="width:100%;"></div></td></tr>'
    curDay+=1;
  }
  html+='<tr style="background: #ccc;display:none;"><td colspan="2" style="height:2px;"></td></tr></table></div>'
  return html
}