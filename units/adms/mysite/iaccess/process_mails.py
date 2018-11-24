# -*- coding: utf-8 -*-
#! /usr/bin/env python
import threading
from redis_self.filequeue import FileQueue
from django.core.mail import send_mail
from mysite.settings import EMAIL_ADDR,EMAIL_HOST_PASSWORD
from base.crypt import decryption
from traceback import print_exc
from redis_self.server import queqe_server, start_dict_server
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.http import HttpResponse
import time
from django.contrib.auth.decorators import login_required
import dict4ini
import os

def init_Email(cfg=None):
    global email_addr,email_host_password
    if cfg:
        email_addr = cfg.iaccess.email_addr
        email_host_password =cfg.iaccess.email_host_password
    else:
        email_addr = EMAIL_ADDR
        email_host_password = EMAIL_HOST_PASSWORD


#手动发送邮件-----darcy20120220
@login_required
def send_mail_by_hand(request):
    title = request.POST.get("title");
    content = request.POST.get("content");
    receiver = request.POST.get("receiver");
    if not email_addr:
        return HttpResponse('<script>alert("邮件发送失败,门禁参数配置中邮箱配置错误!")</script>')
        #return HttpResponse(smart_str(simplejson.dumps({"ret": "failed"})))
    try:
        send_mail(title,content,email_addr,[receiver],fail_silently=False,auth_password=email_host_password)
        #return HttpResponse(smart_str(simplejson.dumps({"ret": "ok"})))
        return HttpResponse('<script>alert("邮件发送成功.")</script>')
    except:
        return HttpResponse('<script>alert("邮件发送失败.")</script>')

#处理发送邮件的任务---darcy20120220
def process_send_email(email_info,q_server,d_server):
    contin = True
#    print "----sending email-----"
    email_count = d_server.get_from_dict("EMAIL_COUNT")
    exist_mails = q_server.get_from_file("EMAILS")
    if email_count:
        exist_mails = q_server.get_from_file("EMAILS")
        exist_mails_list =exist_mails and exist_mails.split("\n") or []
        
        for exist in exist_mails_list:
            email = exist.split("\t")
            try:
#                print "sending exsit mails"
#                print "__email--1--",email[0],email[1],email_addr,[email[2]],decryption(email_host_password)
                send_mail(email[0],email[1],email_addr,[email[2]],fail_silently=False,auth_password=decryption(email_host_password))
                exist_mails_list.remove(exist)
            except:
                contin = False
                print_exc()
                break
            finally:
                q_server.set_to_file("EMAILS","".join(exist_mails_list))
                if exist_mails_list:
                    d_server.set_to_dict("EMAIL_COUNT", 1)#记录文件中是否存在记录
    
    if contin and email_info:
        #循环发送邮件-darcy20120220
        for mail in email_info:
            email_message = mail and mail[1] or ""
            if email_message:   
                try:
#                    print "sending new mails"
#                    print "mail[2]:---",mail[2]
#                    print "__email---2-",mail[0],email_message,email_addr,[mail[2].split("\n")[0]],False,decryption(email_host_password)
                    send_mail(mail[0],email_message,email_addr,[mail[2].split("\n")[0]],fail_silently=False,auth_password=decryption(email_host_password))
                    email_info.remove(mail)
                except:
                    mail_content = ""
                    for mail in email_info:
                        mail_content += "".join(mail)
                    q_server.set_to_file("EMAILS",mail_content)
                    if mail_content:
                        d_server.set_to_dict("EMAIL_COUNT", 1)#记录文件中是否存在记录
                    print_exc()
                    break
#                    print '=====go to sleep===='
#                print "----done-----"


class SendEmail(threading.Thread):
    def __init__(self):
        super(SendEmail, self).__init__()
    def run(self):
        init_Email()
        d_server = start_dict_server()
        q_server = FileQueue()
        email_count = q_server.get_from_file("EMAILS")
        if email_count:
            d_server.set_to_dict("EMAIL_COUNT", 1)
#        try:
        while True:
            #修改邮件参数不需要重启服务。-darcy20120220
            change_args = d_server.get_from_dict("CHANGE_IACCESS_EMAIL_ARGS")
#            print '-------change_iaccess_argument-----',change_args
            if change_args:
                cfg = dict4ini.DictIni(os.getcwd()+"/appconfig.ini",values={"iaccess":{"down_newlog":0, "realtime_forever":0}})
                realtime_forever = int(cfg.iaccess.realtime_forever)
                down_log_time = cfg.iaccess.down_newlog
                init_Email(cfg)
                d_server.set_to_dict("CHANGE_IACCESS_EMAIL_ARGS", 0)

            email_info = d_server.get_from_dict("EMAIL_INFO")
#            print "EMAIL_INFO:---",email_info
            d_server.set_to_dict("EMAIL_INFO", "")
            process_send_email(email_info, q_server, d_server)
#            print "one round"
            time.sleep(10)
#        except:
#            pass
#        finally:
        q_server.connection.disconnect()
        d_server.close()
