# -*- coding: utf-8 -*-
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User, Permission, Group
import datetime
import os
import string
from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from dbapp.utils import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceIterator
from schclass import SchClass
from num_run import NUM_RUN

from base.cached_model import CachingModel
from base.operation import Operation


class NUM_RUN_DEIL(CachingModel):
    Num_runID = models.ForeignKey(NUM_RUN, verbose_name=_(u"班次"), db_column='Num_runID', null=False, blank=False)
    StartTime = models.TimeField(_(u'开始时间'), null=False, blank=False)
    EndTime = models.TimeField(_(u'结束时间'), null=True, blank=False)
    Sdays = models.SmallIntegerField(_(u'开始日期'), null=False, blank=False)
    Edays = models.SmallIntegerField(_(u'结束日期'), null=True, blank=True)
    SchclassID = models.ForeignKey("SchClass", verbose_name=_(u'时段类型'), db_column='SchclassID', null=True, default= -1, blank=True)
#    SchclassID=models.IntegerField("SchClass",  db_column='SchclassID', null=True,default=-1,blank=True)

    OverTime = models.IntegerField(_(u'加班'), null=False, default=0, blank=True)
    def __unicode__(self):
        return unicode(u"%s,%s" % (self.Num_runID, self.SchclassID))
    def delete(self):
        if self.pk > 7:
            super(NUM_RUN_DEIL, self).delete()
    class Admin(CachingModel.Admin):
        import datetime
        visible = False
        @staticmethod
        def initial_data(): #
                from mysite.att.models import SchClass
                import datetime
                if NUM_RUN.objects.count() == 0:
                        NUM_RUN(Name=u"%s" % _(u"弹性班次"), Units=1, Cycle=1).save()
                if SchClass.objects.count() == 0:
                        SchClass(SchName=u"%s" % _(u"弹性时段"),
                                StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(),
                                CheckInTime1=datetime.datetime.strptime("00:01", "%H:%M").time(),
                                CheckInTime2=datetime.datetime.strptime("23:59", "%H:%M").time(),
                                CheckOutTime1=datetime.datetime.strptime("00:01", "%H:%M").time(),
                                CheckOutTime2=datetime.datetime.strptime("23:59", "%H:%M").time(),
                                OverTime=0,
                                ).save()

                if NUM_RUN_DEIL.objects.count() == 0:
                        cc = SchClass.objects.all()
                        #print cc[0].SchclassID, '-------count-------'
                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=0 , Edays=0, SchclassID_id=1).save()

                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=1 , Edays=1 , SchclassID_id=1).save()
                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=2 , Edays=2, SchclassID_id=1).save()
                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=3, Edays=3, SchclassID_id=1).save()
                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=4 , Edays=4 , SchclassID_id=1).save()
                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=5 , Edays=5 , SchclassID_id=1).save()
                        NUM_RUN_DEIL(Num_runID_id=1, StartTime=datetime.datetime.strptime("08:00", "%H:%M").time(),
                                EndTime=datetime.datetime.strptime("18:00", "%H:%M").time(), Sdays=6 , Edays=6 , SchclassID_id=1).save()
#
#                        from django.db.models import connection
#                        cur=connection.cursor()
#                        for i in range(7):
#                            sql="insert into num_run_deil(Num_runID,StartTime,EndTime,Sdays,Edays,SchclassID,status,OverTime) values(1,'08:00:00','18:00:00',%s,%s,1,0,0)"%(i,i)
#                            cur.execute(sql)
#                        connection._commit()

                pass



    class Meta:
        app_label = 'att'
        db_table = 'num_run_deil'
        verbose_name = _(u'班次明细')
        verbose_name_plural = verbose_name
        unique_together = (("Num_runID", "Sdays", "StartTime"),)
