# coding=utf-8

import datetime
from django.conf import settings
from cmdconvert import std_cmd_convert
from mysite.iclock.cache_cmds import cache,update_cached_cmd,get_cached_cmd,post_check_update,update_and_load_cmds,update_start_end_index,check_pre_request,get_pre_request_cmds,get_request_cmds,get_prev_save_time ,save_last_activity,get_device_raise,check_and_init_cmds_cache
from mysite.iclock.cache_utils import  run_cmds,get_cmds
from base.backup import get_attsite_file

from constant import DEVELOP_MODEL as develop_model

def update_cmd(device, id, ret, q_server=None):
    '''
    id: 命令ID ret: 命令返回值
    把返回值更新到命令
    '''
    cmdobj = get_cached_cmd(id)
    if not cmdobj:
        return None
    if cmdobj.SN_id!=device.id: 
        print u"ERROR: 命令对应的设备与指定设备不一致(%s != %s)"%(cmdobj.SN_id, device.id)
        return None
    cmdobj.CmdOverTime=datetime.datetime.now()  #命令返回时间
    cmdobj.CmdReturn=ret    #命令返回值
    update_cached_cmd(cmdobj)   #更新命令到缓存
    cmdobj.SN=device
    return cmdobj

def update_cmds(device, rets):
    post_check_update(device,rets)#更新下发命令，起始结束标示
    for id in rets:
        update_cmd(device, id, rets[id],None)
        
def proceed_cmds(device):
    if develop_model:
        run_cmds(device.pk)
    else:
        update_and_load_cmds(device)
        
def fetch_cmds(device):
    proceed_cmds(device)
    devcmds = []
    flag_new = True
    if develop_model:
        devcmds = get_cmds(device.pk)
    else:
        flag_new = False #是否是下发新的命令
        check_ret = check_pre_request(device)#确认上次下发命令，机器是否成功接收到
        if not check_ret:
            devcmds = get_pre_request_cmds(device) #返回上一次下发的命令
        else:
            flag_new = True
            devcmds = get_request_cmds(device)

    resp = ''
    c=0      
    maxRet = device.max_comm_count  #---每次传送给设备的命令数
    maxRetSize = device.max_comm_size * 1024    #---最大数据包长度(KB)
    while devcmds:
        cmd_key = devcmds.pop(0)
        obj_cmd=cache.get(cmd_key)  #-------------------用到cache
        cmd_return = obj_cmd.CmdReturn
        
        if settings.GETREQ_THREE_TIMES:#兼容固件不确认的bug
            if not cmd_return:
                cmd_return = -99996
            else:
                cmd_return = int(cmd_return) -1
        
        CmdContent=obj_cmd.CmdContent
        if CmdContent.find("DATA UPDATE user")==0 or CmdContent.find("DATA UPDATE SMS")==0: #传送用户命令,需要解码成GB2312
            cc=CmdContent
            try:
                cc=cc.encode("gb18030")
            except:
                try:
                    cc=cc.decode("utf-8").encode("gb18030")
                except:
                    import traceback;traceback.print_exc()
                    pass
        else:                    
            cc=str(CmdContent)
        nowcmd=str(cc)
        cc=std_cmd_convert(cc, device)  #----ZK-ECO 标准命令到 PUSH-SDK 命令的转换
        if cc: resp+="C:%d:%s\n"%(obj_cmd.id,cc)  #---格式: Ｃ:设备序列号:内容 \n

        c=c+1
            
        if settings.GETREQ_THREE_TIMES:#兼容固件bug
            obj_cmd.CmdReturn = cmd_return
            
        obj_cmd.CmdTransTime=datetime.datetime.now()
        update_cached_cmd(obj_cmd)
        
        if (c>=maxRet) or (len(resp)>=maxRetSize): break;     #达到了最大命令数或最大命令长度限制
        if CmdContent in ["CHECK","CLEAR DATA","REBOOT", "RESTART"]: break; #重新启动命令只能是最后一条指令  #增加查找到CHECK指令后，直接发送
        
    if c == 0:#没有发送任何命令时，简单向设备返回 "OK" 即可
        print 'Ok------------------------------------------------'
        resp += "OK"
    else:
        if flag_new:
            update_start_end_index(device,c) #更新下发命令的起始和结束为止
    return  resp
    