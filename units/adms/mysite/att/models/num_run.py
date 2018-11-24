# -*- coding: utf-8 -*-
from django.db import models
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django import forms
 
from base.cached_model import CachingModel
from base.operation import Operation
from schclass import SchClass
import datetime
from dbapp import data_edit
CYCLE_UNITS=(
    (0, _(u'天')),
    (1, _(u'周')),
    (2, _(u'月')),
)

def cycles_for_day(cycle):
        return [(i, _(u"第%s天")%(1+i)) for i in range(cycle)]

SUNDAY=datetime.datetime(2010,2,28)
ONE_DAY=datetime.timedelta(days=1)
DAY_NAMES=[_((SUNDAY+d*ONE_DAY).strftime('%A')) for d in range(7)]
SHORT_DAY_NAMES=[_((SUNDAY+d*ONE_DAY).strftime('%a')) for d in range(7)]

def cycles_for_week(cycle):
        return [(i, DAY_NAMES[i%7]) for i in  range(cycle*7)]

def cycles_for_month(cycle):
        return [(i, _(u"第%s天")%(i+1)) for i in range(cycle*31)]

CYCLE_DAYS_FUN=(cycles_for_day, cycles_for_week, cycles_for_month)

    ##班次表##
class NUM_RUN(CachingModel):
    Num_runID=models.AutoField(primary_key=True,null=False, editable=False)
    OLDID=models.IntegerField(null=True,default=-1,blank=True, editable=False)
    Name=models.CharField(_(u'班次名称'),max_length=30,null=False)
    StartDate = models.DateField(_(u'开始时间'),null=True,default=datetime.datetime.now().strftime("%Y-%m-%d"), blank=True,editable=False) #日期型
    EndDate = models.DateField(_(u'结束时间'),null=True,default=datetime.datetime.now().strftime("%Y-%m-%d"), blank=True,editable=False)    #日期型
    Units=models.SmallIntegerField(_(u'周期单位'), default=1,editable=True, choices=CYCLE_UNITS)
    Cycle=models.SmallIntegerField(_(u'周期数') ,db_column='Cyle', default=1,editable=True)
    
    def save(self,**args):
        if self.Units==1 and self.Cycle>52:
            raise Exception(_(u'周的周期数不能超过52周！'))
        if self.Units==2 and self.Cycle>12:
            raise Exception(_(u'月的周期数不能超过12个月！'))
        if self.pk==1:
            raise Exception(_(u'%s 不能被修改！')%self.Name)
        exist=NUM_RUN.objects.filter(Name__exact=self.Name)
        if exist and exist[0].pk!=self.Num_runID:
            raise Exception(_(u'%s 名称已经存在,班次不能同名！')%self.Name)
        super(NUM_RUN,self).save(**args)
        from mysite.att.calculate.global_cache import C_NUM_RUN
        C_NUM_RUN.refresh()
            
    def __unicode__(self):
        return unicode(u"%s"%(self.Name))
    
    @staticmethod
    def clear():
        for e in NUM_RUN.objects.all():
            if e.Num_runID>1: 
                e.delete()
    
    def delete(self):
        if self.user_of_run_set.all().count()>0:
            raise Exception(_(u'%s 正在使用，不能被删除')%self)
        
        if self.Num_runID>1:            
            super(NUM_RUN,self).delete()
            from mysite.att.calculate.global_cache import C_NUM_RUN
            C_NUM_RUN.refresh()
        else:
            raise Exception(_(u'%s 不能被删除！')%self.Name)
       
    class OpAddTimeTable(Operation):
        
        help_text=_(u'''增加时间段''')
        verbose_name=_(u"增加时间段")
        params=(
            ('time_table',models.ManyToManyField(SchClass, verbose_name=_(u"时间段"))),
            ('if_overtime', models.BooleanField(_(u'是否需要加班'))),
            ('overtime', models.IntegerField(_(u'加班时间(分钟)'),default=0)),
            ('days', forms.MultipleChoiceField(_(u'选择日期'),widget=forms.CheckboxSelectMultiple)),
            )
        only_one_object=True
        def __init__(self, obj):
            super(NUM_RUN.OpAddTimeTable, self).__init__(obj)
            params=dict(self.params)
            days=params['days']
            days.label=_(u'选择日期')
            days.choices=tuple(CYCLE_DAYS_FUN[obj.Units](obj.Cycle))
            params['days']=days
            self.params=tuple(params.items())
        def action(self, time_table, if_overtime, overtime, days):
            from num_run_deil import NUM_RUN_DEIL
            if self.object.user_of_run_set.all().count()>0:
                raise Exception(_(u'%s 正在使用，不能编辑')%self.object)
            if self.object.pk==1:
                    raise Exception(_(u'%s 不能被修改！')%self.object.Name)
            
#            for t in time_table:
#                ts=datetime.datetime.strptime(t.StartTime.strftime("%H:%M:%S"),"%H:%M:%S")
#                te=datetime.datetime.strptime(t.EndTime.strftime("%H:%M:%S"),"%H:%M:%S")
#                if ts> te:
#                    te=te+datetime.timedelta(days=1)
#                for s in n:
#                    ss=datetime.datetime.strptime(s.SchclassID.StartTime.strftime("%H:%M:%S"),"%H:%M:%S")
#                    se=datetime.datetime.strptime(s.SchclassID.EndTime.strftime("%H:%M:%S"),"%H:%M:%S")
#                    if se<ss:
#                        se=se+datetime.timedelta(days=1)
#                    if (ts<ss and te <ss) or (ts>se and te >se):
#                        pass
#                    else:
#                        raise Exception(_(u'%s 与 %s 已有时间段有重复!'%(t,s)))                        
            
            
            #print "x:%s"%x
            
            for t  in time_table:
                ts=datetime.datetime.strptime(t.StartTime.strftime("%H:%M:%S"),"%H:%M:%S")
                te=datetime.datetime.strptime(t.EndTime.strftime("%H:%M:%S"),"%H:%M:%S")
                if ts> te:
                    te=te+datetime.timedelta(days=1)
                
                for i in days:
                    NUM_RUN_DEIL.objects.filter(Num_runID=self.object,SchclassID=t.pk,Sdays=i).delete()
                    n=NUM_RUN_DEIL.objects.filter(Num_runID=self.object,Sdays=i)
                    if n:
                        for s in n:   
                            ss=datetime.datetime.strptime(s.SchclassID.StartTime.strftime("%H:%M:%S"),"%H:%M:%S")
                            se=datetime.datetime.strptime(s.SchclassID.EndTime.strftime("%H:%M:%S"),"%H:%M:%S")
                            if se<ss:
                                se=se+datetime.timedelta(days=1)
                            if (ts<ss and te <ss) or (ts>se and te >se):
                                pass
                            else:
                            	try:
                            		s = s.split(',')[1]
                            	except:
                            		pass
                            	raise Exception(_(u'%(t)s 与 %(ss)s 时间段有重复! 在第%(d)s 天')%{"t":t,"ss":s,"d":str(int(i)+1)})
                    tmputs=NUM_RUN_DEIL()
                    tmputs.Num_runID=self.object
                    tmputs.StartTime=t.StartTime.strftime("%H:%M:%S")
                    tmputs.EndTime=t.EndTime.strftime("%H:%M:%S")
                    tmputs.Sdays=i
                    tmputs.Edays=i
                    #print tmputs.StartTime
                   # print tmputs.EndTime
                    if if_overtime==True:
                        tmputs.OverTime=overtime
                    tmputs.SchclassID=t
                    tmputs.save()   
                    #print "save OK" 
    class _change(Operation):
        visible=False
        help_text=_(u'''修改''')
        verbose_name=_(u"修改")
        
        def action(self):
            pass
    class OpDeleteTimeTable(Operation):
        help_text=_(u'''清空时间段''')
        verbose_name=_(u"清空时间段")
        def action(self):
            if self.object.user_of_run_set.all().count()>0:
                raise Exception(_(u'%s 正在使用，不能清空')%self.object)
            if self.object.pk==1:
                    raise Exception(_(u'%s 不能被修改！')%self.object.Name)
            from num_run_deil import NUM_RUN_DEIL
            tmp=NUM_RUN_DEIL.objects.filter(Num_runID=self.object)
            for tn in tmp:
                tn.delete()

    class Admin(CachingModel.Admin):
        from dbapp.widgets import ZBaseSmallIntegerWidget
        list_filter=('Name','StartDate','EndDate','Cycle','Units')
        query_fields = ['Name','Cycle','Units']
        list_display=('Name','Cycle','Units','Units|capfirst')
        hide_fields=('Num_runID','data_verbose_column','Units|capfirst')
        api_fields=('Name','StartDate','EndDate','Cycle','Units')
        default_widgets={'Cycle':ZBaseSmallIntegerWidget}
        disabled_perms=['dataimport_num_run','change_num_run']
        menu_index=2
        help_text=_(u'多个时间段一起选择时，时段的起始时间不能相同,如果存在多个相同的起始时间，保存只以时段列表中从上到下排列最前且已选中的第一个的时段为准！\n 选择多个时段时，选择的日期将作用于所有已选择的时段！')
        @staticmethod
        def initial_data(): #
                if NUM_RUN.objects.count()==0:
                        NUM_RUN(Name=u"%s"%_(u"弹性班次"), Units=1,Cycle=1).save()
                pass
        
    class Meta:
        app_label='att'
        db_table = 'num_run'
        verbose_name=_(u'班次')
        verbose_name_plural=verbose_name

#保存时间段
def DataPostCheck(sender, **kwargs):
    from mysite.att.models.schclass import SchClass
    oldObj=kwargs['oldObj']
    newObj=kwargs['newObj']
    request=sender
    if isinstance(newObj, NUM_RUN):        
        try:
            
            days=[]
            schs=[]
            days=request.REQUEST.getlist("days")                
            schs=request.REQUEST.getlist("schs")      
            if_ot=request.REQUEST.get("if_ot","")  
            if schs:
                schs=SchClass.objects.filter(pk__in=schs)
            if if_ot:                   
                if_ot=True
            ot=request.REQUEST.get("overtime","") 
            
            newObj.OpAddTimeTable(newObj).action(schs,if_ot,ot,days)
        except:
            import traceback;traceback.print_exc()

data_edit.post_check.connect(DataPostCheck)
