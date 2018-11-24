#! /usr/bin/env python
#coding=utf-8
from django.utils import simplejson
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from redis_self.server import start_dict_server, queqe_server
from django.contrib.auth.decorators import login_required
from mysite.utils import printf, delete_log, write_log
import redis_self, re, os, dict4ini, datetime


#进行访客监控
@login_required
def get_visitor_monitor(request):
    from view import get_visitor_option, get_visitor_in, get_visitor_by_pin, add_recode_to_report
    d_server = start_dict_server()
    current_time = datetime.datetime.now()#当前的时间
    time_length = get_visitor_option()#来访的时长
    
    visitor_alarm_info = d_server.get_from_dict("visitor_alarm_info")#获取缓存中访客来访需要监控的访客信息
    #print '---------visitor_alarm_info=', visitor_alarm_info
    alarm_visitor_info = []#传到前端的访客信息
    if visitor_alarm_info:
        alarm_time_length = d_server.get_from_dict("visitor_alarm_info")[2]#获取来访时长
        #print '-----------alarm_time_length=', alarm_time_length
        #如果来访时长修改了，更新缓存中的信息
        if alarm_time_length != time_length:
            #print '------update lai fang shi chang------'
            visitor_in = get_visitor_in()
            alarm_pin_set = visitor_in["alarm_pin_set"]
            alarm_time_list = visitor_in["alarm_time_list"]
            d_server.set_to_dict("visitor_alarm_info", [alarm_pin_set, alarm_time_list, time_length])
        
        #访客超过来访时长，将信息传到前端, 更新缓存
        alarm_pin_set = d_server.get_from_dict("visitor_alarm_info")[0]
        alarm_time_list = d_server.get_from_dict("visitor_alarm_info")[1]#取缓存中的报警时间
        alarm_info = {}#报警的信息
        begin_length = len(alarm_pin_set)#缓存alarm_pin_set开始时的长度
        end_length = 0#缓存alarm_pin_set循环结束后的长度
        
        for alarm_time in alarm_time_list:
#            print '--------current_time==', current_time
#            print '--------alarm_time====', alarm_time
            if current_time < alarm_time:#当前时间小于报警时间，跳出
                break
            else:
                index = alarm_time_list.index(alarm_time)
                pin = alarm_pin_set[index]#获取来访超时的访客的编号
                #print '-----pin=', pin
                alarm_visitor = get_visitor_by_pin(pin)#获取来访超时的访客信息
                
                #传到前端的访客信息
                alarm_info["name"] = alarm_visitor[0]
                #print '--------name=',alarm_info["name"]
                alarm_info["pin"] = alarm_visitor[1]
                alarm_info["card"] = alarm_visitor[2]
                #print '--------card=', alarm_info["card"]
                alarm_info["visitor_company"] = alarm_visitor[3]
                alarm_info["visit_reason"] = alarm_visitor[4]
                alarm_info["visitor_number"] = alarm_visitor[5]
                alarm_info["exit"] = alarm_visitor[6]
                alarm_info["visit_time"] = str(alarm_visitor[7])
                
                alarm_visitor_info.append(alarm_info)
                
                #往报表插入记录
                #print '----begin add to report-------'
                add_recode_to_report(alarm_info)
                #print '---------end add to report----'
                #更新缓存
     
                alarm_pin_set.remove(pin)
                alarm_time_list.remove(alarm_time)
                end_length = len(alarm_pin_set)
        #有变化，更新缓存
        if begin_length > end_length:
            d_server.set_to_dict("visitor_alarm_info", [alarm_pin_set, alarm_time_list, time_length])
    #重启系统后
    else:
        try:
            visitor_in = get_visitor_in()
            if visitor_in:
                alarm_pin_set = visitor_in["alarm_pin_set"]
                alarm_time_list = visitor_in["alarm_time_list"]
                d_server.set_to_dict("visitor_alarm_info", [alarm_pin_set, alarm_time_list, time_length])
        except Exception, e:
            print '---else--e=',e
    cc={
        'data': alarm_visitor_info,
    }
    rtdata = simplejson.dumps(cc)
    #print '------rtdata==', rtdata
    return HttpResponse(smart_str(rtdata))








