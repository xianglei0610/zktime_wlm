# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_country import CountryForeignKey, COUNTRY_NAME, Country
from base.models import CachingModel, Operation
from base.operation import ModelOperation
from base.cached_model import STATUS_INVALID
from django.conf import settings
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

STATE_NAME = _(u"省份")
STATE_NAME_2 = _(u"省份名称")
STATE_NAME_ID = _(u"省份编号")



class State(CachingModel):
        id = models.AutoField(_(u'省份ID'), primary_key=True, editable=False)
        state_name = models.CharField(STATE_NAME_2, max_length=50)
        state_code = models.CharField(STATE_NAME_ID, max_length=20, null=True, blank=True)
        country = CountryForeignKey( verbose_name=COUNTRY_NAME, editable=True, null=True, blank=False)

        

 
        @staticmethod
        def clear():
            #为保证服务器和设备中数据的一致性，删除省份前先删除这些省份所包含的人员。-comment by darcy
            states_to_clear = State.objects.exclude(id=1)
            from mysite.personnel.models import Employee
            emps_to_clear = Employee.objects.filter(state__in=states_to_clear)

            for emp in emps_to_clear:
                emp.delete()
            for state in states_to_clear:
                state.delete()

        def __unicode__(self):
                if self.state_code:
                        return u"%s" % (self.state_name)
                else:
                        return u"%s" % self.state_name
        def export_unicode(self):
                return u"%s" % self.state_name
        
        def data_valid(self, sendtype):
            #print "sendtype:%s" % sendtype
            tmp = State.objects.filter(state_code__exact=self.state_code)
            if self.state_code and len(tmp) > 0 and tmp[0].id != self.id:
                raise Exception(_(u'省份编号已经存在!'))

        def save(self):
                if not self.state_code:
                    raise Exception(_(u'省份编号不能为空!'))
                

                tmp = State.objects.filter(state_code__exact=self.state_code)
                if self.state_code and len(tmp) > 0 and tmp[0].id != self.id:
                    raise Exception(_(u'省份编号已经存在!'))
                

                super(State,self).save()

                
        def delete(self):
            if self.pk != 1:
#                self.stateadmin_set.all().delete()
                super(State, self).delete()

        class dataimport(Operation):
                help_text = _(u"导入数据") #导入
                verbose_name = _(u"导入")
                visible = False
                def action(self):
                        pass

        class _delete(Operation):
                help_text = _(u"删除省份") #删除选定的记录
                verbose_name = _(u"删除")
                def action(self):
                        from datetime import datetime
                        from model_emp import Employee
                        from model_city import City
                        emp = State.employee_set.related.model
                        city = State.city_set.related.model

                        if len(emp.objects.filter(state=self.object)) > 0:
                                raise Exception, _(u'该省份还有人员，不能删除')
                        if len(city.objects.filter(state=self.object))>0:
                                raise Exception, _(u'该省份还有城市，不能删除')
                        if self.object.id > 0 and self.object.id < 35:
                            raise Exception, _(u'默认省份不能删除')
                        self.object.invalidate = datetime.now().strftime("%Y-%m-%d")
                        self.object.status = STATUS_INVALID
#                        stateadmin = State.stateadmin_set.related.model
#                        stateadmin.objects.filter(state=self.object).delete()
                        self.object.delete()


        
        class Admin(CachingModel.Admin):
                sort_fields = ["country.country_code", "id"]
                app_menu = "personnel"
                help_text = _(u"如果新增的省份在省份列表中未能显示，请联系管理员到用户编辑中重新授权省份！")
                list_display = ( 'country.country_name', 'state_code', 'state_name', )
                adv_fields = ['country.country_name', 'state_code', 'state_name']
                visible = False
                import_fields = ['state_code', 'state_name']
                query_fields = ['country.country_name', 'state_code', 'state_name']
                menu_index = 2
                cache = 3600
                default_give_perms = ["contenttypes.can_BaseDataPage",]
                report_fields=['state_code', 'state_name']
#                menu_focus = "BaseData"
        class Meta:
                app_label = 'personnel'
                verbose_name = _(u'省份')
                verbose_name_plural = verbose_name

class StateForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(StateForeignKey, self).__init__(State, to_field=to_field, **kwargs)






