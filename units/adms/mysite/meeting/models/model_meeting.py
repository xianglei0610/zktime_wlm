#! /usr/bin/env python
#coding=utf-8

from base.models import AppOperation
from django.db import models
from base.models import CachingModel
from base.operation import Operation,ModelOperation
from django.utils.translation import ugettext_lazy as _
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
from type import TypeForeignKey
from mysite.meeting.models.room import Room,RoomManyToManyFieldKey
#from room import Room,RoomForeignKey
import datetime
import re
YESORNO = (
    (1, _(u'是')),
    (0, _(u'否')),
)

def get_endtime(self, starttime, continuetime):
    #获得会议结束时间，如果会议 持续到第二天则无效。。但不会报错或提示
        h = starttime.hour
        m = starttime.minute
        if continuetime >= 60:
            if h < 23:
               h = h + 1
            m = m + (continuetime - 60)
        if continuetime + m >= 60:
            if h < 23:
               h = h + 1            
            m = (m + continuetime) - 60
        else:
            m = m + continuetime
        return time(h, m, starttime.second)


class MeetingEntity(CachingModel):
    id = models.AutoField(db_column="id",primary_key=True,editable=False)#勿删，会议统计会用到该属性
    numberMeeting = models.CharField(verbose_name=_(u'会议编号'),max_length=20)
    nameMeeting = models.CharField(verbose_name=_(u'会议名称'), max_length=40,)
    typeMeeting =TypeForeignKey(verbose_name=_(u'会议室类型'),null=True,blank=True,editable=False)
    roomMeeting = models.ForeignKey(Room,verbose_name=_(u'会议室'), editable=True)
    startTime = models.DateTimeField(verbose_name=_(u'开始时间'))
    endTime = models.DateTimeField(verbose_name=_(u'结束时间'))
    lateAllow = models.IntegerField(verbose_name=_(u'允许迟到（分钟）'),default=0)
    leaveAllow = models.IntegerField(verbose_name=_(u'允许早退（分钟）'),default=0)
    startCheckInTime = models.DateTimeField(verbose_name=_(u'会议开始签到时间'))
    endCheckInTime = models.DateTimeField(verbose_name=_(u'会议结束签到时间'))
    startCheckOutTime = models.DateTimeField(verbose_name=_(u'会议开始签退时间'))
    endCheckOutTime = models.DateTimeField(verbose_name=_(u'会议结束签退时间'))
    
    remark = models.TextField(verbose_name=_(u'内容纪要'),blank=True,null=True)
    
    
    def __unicode__(self):
        return '%s %s' % (self.numberMeeting, self.nameMeeting)
        
    
    def save(self):
        from statisticsMeeting import StatisticsMeeting
        if len(self.numberMeeting)>20:
            raise Exception(_(u'会议编号长度不能超过20位有效字符'))
        if len(self.nameMeeting)>40:
            raise Exception(_(u'会议名称长度不能超过40个有效字符'))
        p = re.compile(r'^[a-zA-Z0-9]*$')
        if not p.match(self.numberMeeting):
            raise Exception(_(u"会议编号只能为数字或字母"))        
        ee = MeetingEntity.objects.filter(numberMeeting=self.numberMeeting)

        if len(ee)>0 and not self.id:
            raise Exception(_(u'会议编号已存在'))
        if not self.roomMeeting.isUse:
            raise Exception(_(u'会议室处于无法使用状态'))
        eNam = MeetingEntity.objects.filter(nameMeeting=self.nameMeeting)
        if not self.id and len(eNam) >0:
            raise Exception(_(u'会议名称已存在'))
        
        if self.endTime <= self.startTime:
            raise Exception(_(u'结束时间不应小于开始时间'))
        if self.startTime.day != self.endTime.day or (self.endTime - self.startTime).seconds/3600 >= 8:
            raise Exception(_(u'本系统暂不支持跨天或超过8小时的大型会议'))
        if datetime.timedelta(minutes=(self.lateAllow+self.lateAllow))>=(self.endTime-self.startTime):
            raise Exception(_(u'允许迟到、早退设置不合理'))
        if self.startCheckInTime > self.startTime:
            raise Exception(_(u'开始签到时间不应大于会议开始时间'))
        if self.endCheckInTime <= (self.startTime + datetime.timedelta(minutes=(self.lateAllow))):          
            raise Exception(_(u'结束签到时间不应小于或等于会议开始时间加允许迟到时间'))
        if self.startCheckOutTime > (self.endTime-datetime.timedelta(minutes=(self.leaveAllow))):
            raise Exception(_(u'开始签退时间不应大于会议结束时间减允许早退时间'))
        if self.startCheckOutTime > self.endCheckOutTime:
            raise Exception(_(u'开始签退时间不应小于结束签退时间'))
        if self.endCheckInTime > (self.endTime-datetime.timedelta(minutes=(self.leaveAllow))):
            raise Exception(_(u'结束签到时间不应大于会议结束时间减允许早退时间'))
        if self.endCheckOutTime <= self.endTime:
            raise Exception(_(u'结束签退时间不应小于或等于会议结束时间'))
        if self.id:
            mE = MeetingEntity.objects.get(id=self.id)
            if mE.numberMeeting != self.numberMeeting:
                raise Exception(_(u"会议编号不可修改"))
        
        meetingAll = MeetingEntity.objects.all()
        if len(meetingAll)>0 :
            for meeting in meetingAll :
                if self.roomMeeting == meeting.roomMeeting and self.numberMeeting != meeting.numberMeeting and self.startTime.date() == meeting.startTime.date() and self.startCheckInTime >= meeting.startCheckInTime and self.startCheckInTime <= meeting.endCheckOutTime:
                    raise Exception(_(u'该时间段内会议室已被占用'))
                if self.roomMeeting == meeting.roomMeeting and self.numberMeeting != meeting.numberMeeting and self.startTime.date() == meeting.startTime.date() and self.endCheckOutTime >= meeting.startCheckInTime and self.endCheckOutTime <= meeting.endCheckOutTime:
                    raise Exception(_(u'该时间段内会议室已被占用'))
                if self.roomMeeting == meeting.roomMeeting and self.numberMeeting != meeting.numberMeeting and self.startTime.date() == meeting.startTime.date() and self.startCheckInTime <= meeting.startCheckInTime and self.endCheckOutTime >= meeting.endCheckOutTime:
                    raise Exception(_(u'该时间段内会议室已被占用'))
                
#        
                            
                        
        if self.id:
            eNam = MeetingEntity.objects.filter(nameMeeting=self.nameMeeting)
            ee = MeetingEntity.objects.filter(numberMeeting=self.numberMeeting)
            if len(eNam)>0 and len(ee)>0 and ee[0].id != eNam[0].id:
                raise Exception(_(u'会议名称已存在'))
        
        super(MeetingEntity,self).save()
        me = MeetingEntity.objects.get(id=self.id)
        sMeeting = StatisticsMeeting.objects.filter(meetingID=me)
        if len(sMeeting)<1:
            sm = StatisticsMeeting()
            sm.meetingID = me
            sm.save()
        

        
    def delete(self):
        from meeting_emp import MeetingEmp
        from statisticsMeeting import StatisticsMeeting
        m = MeetingEntity.objects.get(id=self.id)
        if len(MeetingEmp.objects.filter(meetingID=m))>0:
            raise Exception(_(u'会议中还有人员，不能删除'))
        super(MeetingEntity,self).delete()
        try:
            me = MeetingEntity.objects.get(id=self.id)
            sm = StatisticsMeeting.objects.get(meetingID=me)
            sm.delete()
        except:
            pass
        
        
    class Admin(CachingModel.Admin):    #管理该模型
        
        menu_group = 'meeting'          #在哪个app应用下
        menu_index=3                #菜单的摆放的位置
        query_fields=['numberMeeting','nameMeeting','roomMeeting.nameRoom','startTime','endTime']     #需要查找的字段
#        adv_fields=['code','datetime','type','startTime']
        list_display=['numberMeeting','nameMeeting','roomMeeting.nameRoom','startTime','endTime'] #列表显示那些字段
        sort_fields=['numberMeeting','startTime']      #需要排序的字段，放在列表中
    class Meta:
        verbose_name=_(u'会议')#名字
        verbose_name_plural=verbose_name
        app_label=  'meeting' #属于哪个app
        
        
class MeetingForeignKey(models.ForeignKey):
    def __init__(self, to_field=None, **kwargs):
        super(MeetingForeignKey, self).__init__(MeetingEntity, to_field=to_field, **kwargs)

class MeetingManyToToManyField(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(MeetingManyToToManyField, self).__init__(MeetingEntity,*args, **kwargs)


#        
#def update_dept_widgets():
#    from dbapp import widgets
#    if MeetingManyToToManyField not in widgets.WIDGET_FOR_DBFIELD_DEFAULTS:
#        from meeting_widget import ZDeptMultiChoiceWidget
#        widgets.WIDGET_FOR_DBFIELD_DEFAULTS[MeetingManyToToManyField]= ZDeptMultiChoiceWidget
#                
##update_dept_widgets()
