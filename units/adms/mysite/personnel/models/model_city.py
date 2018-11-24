# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_country import CountryForeignKey, COUNTRY_NAME, Country
from model_state import StateForeignKey, STATE_NAME, State
from base.models import CachingModel, Operation
from base.operation import ModelOperation
from base.cached_model import STATUS_INVALID
from django.conf import settings
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals
#from model_coun import CounForeignKey, COUN_NAME, Country

#from model_state import StateForeignKey, STATE_NAME, State

CITY_NAME = _(u"城市")
CITY_NAME_2 = _(u"城市名称")
CITY_NAME_ID = _(u"城市编号")

class City(CachingModel):
        id = models.AutoField(_(u'城市ID'), primary_key=True, editable=False)
        city_name = models.CharField(CITY_NAME_2, max_length=50)
        city_code = models.CharField(CITY_NAME_ID, max_length=20, null=True, blank=True)
        country = CountryForeignKey(verbose_name=COUNTRY_NAME, editable=True, null=True, blank=False)
        state = StateForeignKey(verbose_name=STATE_NAME, editable=True, null=True, blank=False)
        
        @staticmethod
        def clear():
            #为保证服务器和设备中数据的一致性，删除国家前先删除这些国家所包含的人员。-comment by darcy
            cities_to_clear = City.objects.exclude(id=1)
            from mysite.personnel.models import Employee
            emps_to_clear = Employee.objects.filter(city__in=cities_to_clear)

            for emp in emps_to_clear:
                emp.delete()
            for city in cities_to_clear:
                city.delete()

        def __unicode__(self):
                if self.city_code:
                        return u"%s" % (self.city_name)
                else:
                        return u"%s" % self.city_name
        def export_unicode(self):
                return u"%s" % self.city_name
        
        def data_valid(self, sendtype):
            #print "sendtype:%s" % sendtype
            tmp = City.objects.filter(city_code__exact=self.city_code)
            if self.city_code and len(tmp) > 0 and tmp[0].id != self.id:
                raise Exception(_(u'城市编号已经存在!'))

        def save(self):
                if not self.city_code:
                    raise Exception(_(u'城市编号不能为空!'))
                

                tmp = City.objects.filter(city_code__exact=self.city_code)
                if self.city_code and len(tmp) > 0 and tmp[0].id != self.id:
                    raise Exception(_(u'城市编号已经存在!'))
                

                super(City,self).save()

                
        def delete(self):
            if self.pk != 1:
#                self.cityadmin_set.all().delete()
                super(City, self).delete()

        class dataimport(Operation):
                help_text = _(u"导入数据") #导入
                verbose_name = _(u"导入")
                visible = False
                def action(self):
                        pass

        class _delete(Operation):
                help_text = _(u"删除城市") #删除选定的记录
                verbose_name = _(u"删除")
                def action(self):
                        from datetime import datetime
                        from model_emp import Employee
                        emp = City.employee_set.related.model

                        if len(emp.objects.filter(city=self.object)) > 0:
                                raise Exception, _(u'该城市还有人员，不能删除')
                        if self.object.id > 0 and self.object.id < 372:                        
                            raise Exception, _(u'默认城市不能删除')
                        self.object.invalidate = datetime.now().strftime("%Y-%m-%d")
                        self.object.status = STATUS_INVALID
#                        cityadmin = City.cityadmin_set.related.model
#                        cityadmin.objects.filter(city=self.object).delete()
                        self.object.delete()


        class Admin(CachingModel.Admin):
                sort_fields = ["country.country_code", "state.state_code","id"]
                app_menu = "personnel"
                help_text = _(u"如果新增的城市在城市列表中未能显示，请联系管理员到用户编辑中重新授权城市！")
                list_display = ('country.country_name', 'state.state_name','city_code', 'city_name',)
                adv_fields = [ 'country.country_name', 'state.state_name','city_code', 'city_name', ]
                import_fields = ['city_code', 'city_name']
                query_fields = ['city_code', 'city_name']
                visible = False
#                menu_focus = "BaseData"
                menu_index = 3
                cache = 3600
                default_give_perms = ["contenttypes.can_BaseDataPage",]
                report_fields=['city_code', 'city_name']
        class Meta:
                app_label = 'personnel'
                db_table = 'personnel_cities'
                verbose_name = _(u'城市')
                verbose_name_plural = verbose_name

class CityForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(CityForeignKey, self).__init__(City, to_field=to_field, **kwargs)







