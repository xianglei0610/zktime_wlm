# -*- coding: utf-8 -*-

#检查一条完整的命令是否指定命令，如果是的话，分解出命令的各个字段
def parse_cmd(cmd_content, cmd): 
    if cmd_content.find(cmd+" ")==0:
        return dict([item.split("=",1) for item in cmd_content[len(cmd)+1:].split("\t") if item.find("=")>0])

# 实现 ZK-ECO 标准命令到 PUSH-SDK 命令的转换
#DATA UPDATE user CardNo=0\tPin=110565\tPassword=\tGroup=1\tStartTime=0\tEndTime=0
# -> 
#DATA USER Card=0\tPIN=110565\tPwd=\tGrp=1


def std_cmd_convert_(cmd, device=None):
    cmd_dict=parse_cmd(cmd, "DATA UPDATE user")
    if cmd_dict:
        pushcmd =  "DATA USER PIN=%s%s%s%s%s%s"%(cmd_dict['Pin'], 
            ("Name" in cmd_dict) and "\tName=%s"%cmd_dict['Name'] or "",  #这种方式生成的命令使得没有Name字段时不要生成空的内容覆盖掉原来的记录内容
            ("Password" in cmd_dict) and "\tPasswd=%s"%cmd_dict['Password'] or "",
            ("Group" in cmd_dict) and "\tGrp=%s"%cmd_dict['Group'] or "",
            ("CardNo" in cmd_dict) and "\tCard=%s"%cmd_dict['CardNo'] or "",
            ("Pri" in cmd_dict) and "\tPri=%s"%cmd_dict['Pri'] or "",
            )
        #print "convert to push sdk:",pushcmd
        return pushcmd

    cmd_dict=parse_cmd(cmd, "DATA UPDATE fingerprint")
    if cmd_dict:
        pushcmd= "DATA FP PIN=%s\tValid=1\tSize=%s\tFID=%s\tTMP=%s"%(cmd_dict['Pin'],
            len(cmd_dict['Template']),         #2010-07-10  gxw修改 加入指纹模版长度
            cmd_dict.get('FingerID',"0"),
            cmd_dict['Template'],
            )
        #print "convert to push sdk:",pushcmd
        return pushcmd

    cmd_dict=parse_cmd(cmd, "DATA DELETE user")
    if cmd_dict:
        return "DATA DEL_USER PIN=%s"%(cmd_dict['Pin'],
            )
    cmd_dict=parse_cmd(cmd, "DATA DELETE fingerprint")
    if cmd_dict:
        return "DATA DEL_FP PIN=%s"%(cmd_dict['Pin'],  #DEL_FP PIN=%d\tFID=%d
            )


    return cmd

def std_cmd_convert(cmd, device=None):
    try:
        cmd=std_cmd_convert_(cmd, device)
    except:pass
    return cmd
