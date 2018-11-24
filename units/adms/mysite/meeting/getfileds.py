#! /usr/bin/env python
#coding=utf-8

from django.utils.translation import ugettext as _
import datetime
def get_base_fields():
    r={}
    strFieldNames=['deptid','badgenumber','username','ssn']
    FieldNames=['badgenumber','username','gender','deptcode','deptname','meetingcode',
    'meetingname','is_attend','is_leave','total_score','cut_score','net_score']
   
    for t in FieldNames:
            if t in strFieldNames:
                    r[t]=''
            else:
                    r[t]=''
    r['userid']=-1;
    FieldCaption=[_(u'人员编号'),_(u'姓名'),_(u'性别'),_(u'部门编号'),_(u'部门名称'),
    _(u'会议编号'),_(u'会议名称'),_(u'是否出席'),_(u'是否请假'),_(u'会议绩效'),_(u'扣除绩效'),_(u'应得绩效')]
    return [r,FieldNames,FieldCaption]

