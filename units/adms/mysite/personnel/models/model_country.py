# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation
from base.operation import ModelOperation
from base.cached_model import STATUS_INVALID
from django.conf import settings
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

COUNTRY_NAME = _(u"国家")
COUNTRY_NAME_2 = _(u"国家名称")
COUNTRY_NAME_ID = _(u"国家编号")

class Country(CachingModel):
        id = models.AutoField(_(u'国家ID'), primary_key=True, editable=False)
        country_name = models.CharField(COUNTRY_NAME_2, max_length=50)
        country_code = models.CharField(COUNTRY_NAME_ID, max_length=20, null=True, blank=True)

        @staticmethod
        def clear():
            #为保证服务器和设备中数据的一致性，删除国家前先删除这些国家所包含的人员。-comment by darcy
            countries_to_clear = Country.objects.exclude(id=1)
            from mysite.personnel.models import Employee
            emps_to_clear = Employee.objects.filter(country__in=countries_to_clear)

            for emp in emps_to_clear:
                emp.delete()
            for country in countries_to_clear:
                country.delete()

        def __unicode__(self):
                if self.country_code:
                        return u"%s" % (self.country_name)
                else:
                        return u"%s" % self.country_name
        def export_unicode(self):
                return u"%s" % self.country_name
        
        def data_valid(self, sendtype):
            #print "sendtype:%s" % sendtype
            tmp = Country.objects.filter(country_code__exact=self.country_code)
            if self.country_code and len(tmp) > 0 and tmp[0].id != self.id:
                raise Exception(_(u'国家编号已经存在!'))

        def save(self):
                if not self.country_code:
                    raise Exception(_(u'国家编号不能为空!'))
                

                tmp = Country.objects.filter(country_code__exact=self.country_code)
                if self.country_code and len(tmp) > 0 and tmp[0].id != self.id:
                    raise Exception(_(u'国家编号已经存在!'))
                

                super(Country,self).save()   
                
        def delete(self):
                
            if self.pk != 1:
#                self.counadmin_set.all().delete()
                super(Country, self).delete()

        class dataimport(Operation):
                help_text = _(u"导入数据") #导入
                verbose_name = _(u"导入")
                visible = False
                def action(self):
                        pass

        class _delete(Operation):
                help_text = _(u"删除国家") #删除选定的记录
                verbose_name = _(u"删除")
                def action(self):
                        from datetime import datetime
                        from model_emp import Employee
                        from model_city import City
                        from model_state import State
                        emp = Country.employee_set.related.model
                        city = Country.city_set.related.model
                        state = Country.state_set.related.model
                        if len(emp.objects.filter(country=self.object)) > 0:
                                raise Exception, _(u'该国家还有人员，不能删除')
                        if len(city.objects.filter(country=self.object))>0:
                                raise Exception, _(u'该国家还有城市，不能删除')
                        if len(state.objects.filter(country=self.object))>0:
                                raise Exception, _(u'该国家还有省份，不能删除')
                        if self.object.id == 1:
                            raise Exception, _(u'默认国家不能删除')
                        self.object.invalidate = datetime.now().strftime("%Y-%m-%d")
                        self.object.status = STATUS_INVALID
#                        counadmin = Country.counadmin_set.related.model
#                        counadmin.objects.filter(coun=self.object).delete()
                        self.object.delete()

        
        class Admin(CachingModel.Admin):
                sort_fields = ["id"]
                app_menu = "personnel"
                help_text = _(u"如果新增的国家在国家列表中未能显示，请联系管理员到用户编辑中重新授权国家！")
                list_display = ('country_code', 'country_name', )
                adv_fields = ['country_code', 'country_name']            
                import_fields = ['country_code', 'country_name']
                visible = False
                query_fields = ['country_code', 'country_name']
                menu_index = 1
                default_give_perms = ["contenttypes.can_BaseDataPage",]
                cache = 3600
#                menu_focus = "BaseData"
                report_fields=['country_code', 'country_name']
#                @staticmethod
#                def initial_data(): #初始化时增加一个国家
#                        if Country.objects.count() == 0:
#                                Country(country_name=u"%s"%_(u"中国"), country_code="1").save()
#                        pass
        class Meta:
                app_label = 'personnel'
                db_table = 'personnel_countries'
                verbose_name = _(u'国家')
                verbose_name_plural = verbose_name

class CountryForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(CountryForeignKey, self).__init__(Country, to_field=to_field, **kwargs)
                








