#! /usr/bin/env python
#coding=utf-8
from django.utils.translation import ugettext as _
def get_base_fields():
    '''
    提供显示 统计最早与最晚 显示字段
    '''
    r={}
    strFieldNames=['deptid','badgenumber','username','ssn']
    FieldNames=['userid','badgenumber','username','deptid','deptname','date',
    'firstchecktime','latechecktime']
    for t in FieldNames:
            if t in strFieldNames:
                    r[t]=''
            else:
                    r[t]=''
    r['userid']=-1;
    FieldCaption=[_(u'用户ID'),_(u'人员编号'),_(u'姓名'),_(u'部门编号'),_(u'部门名称'),_(u'日期'),
                  _(u'最早打卡时间'),_(u'最晚打卡时间')]
    return [r,FieldNames,FieldCaption]

def get_yc_fields():
    '''
    提供显示 考勤异常明细表 显示字段
    '''
    r={}
    strFieldNames=['deptid','badgenumber','username','ssn']
    FieldNames=['userid','super_dept','deptname','badgenumber','username','date',
    'late','early','absent','late_times','early_times','absent_times','worktime','card_times']
    for t in FieldNames:
            if t in strFieldNames:
                    r[t]=''
            else:
                    r[t]=''
    r['userid']=-1;
    FieldCaption=[_(u'用户ID'),_(u'上级部门'),_(u'部门名称'),_(u'人员编号'),_(u'姓名'),_(u'日期'),
                  _(u'迟到分钟'),_(u'早退分钟'),_(u'旷工时间'),_(u'迟到次数'),_(u'早退次数'),_(u'旷工次数'),_(u'上班时间'),_(u'打卡时间')]
    return [r,FieldNames,FieldCaption]
def get_card_times_fields():
    '''
    提供显示 打卡详情表 显示字段
    '''
    r={}
    strFieldNames=['deptid','badgenumber','username','ssn']
    FieldNames=['userid','super_dept','deptname','badgenumber','username','date',
    'times','card_times']
    for t in FieldNames:
            if t in strFieldNames:
                    r[t]=''
            else:
                    r[t]=''
    r['userid']=-1;
    FieldCaption=[_(u'用户ID'),_(u'上级部门'),_(u'部门名称'),_(u'人员编号'),_(u'姓名'),_(u'日期'),
                  _(u'打卡次数'),_(u'打卡时间')]
    return [r,FieldNames,FieldCaption]


   