# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from base.models import CachingModel, Operation
from base.operation import ModelOperation
from base.cached_model import STATUS_INVALID
from django.conf import settings
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

NATIONAL_NAME = _(u"民族")
NATIONAL_NAME_2 = _(u"民族名称")
NATIONAL_NAME_ID = _(u"民族编号")

class National(CachingModel):
        id = models.AutoField(_(u'民族ID'),  primary_key=True, editable=False)
        name = models.CharField(NATIONAL_NAME_2, max_length=50)
        code = models.CharField(NATIONAL_NAME_ID, max_length=20, null=True, blank=True)

        @staticmethod
        def clear():
            #为保证服务器和设备中数据的一致性，删除国家前先删除这些国家所包含的人员。-comment by darcy
            nationals_to_clear = National.objects.exclude(id=1)
            from mysite.personnel.models import Employee
            emps_to_clear = Employee.objects.filter(national__in=nationals_to_clear)

            for emp in emps_to_clear:
                emp.delete()
            for national in nationals_to_clear:
                national.delete()

        def __unicode__(self):
                if self.code:
                        return u"%s" % (self.name)
                else:
                        return u"%s" % self.name
        def export_unicode(self):
                return u"%s" % self.name
        
        def data_valid(self, sendtype):
            #print "sendtype:%s" % sendtype
            tmp = National.objects.filter(code__exact=self.code)
            if self.code and len(tmp) > 0 and tmp[0].id != self.id:
                raise Exception(_(u'民族编号已经存在!'))

        def save(self):
                if not self.code:
                    raise Exception(_(u'民族编号不能为空!'))
                

                tmp = National.objects.filter(code__exact=self.code)
                if self.code and len(tmp) > 0 and tmp[0].id != self.id:
                    raise Exception(_(u'民族编号已经存在!'))
                

                super(National,self).save()   
                
        def delete(self):
                
            if self.pk != 1:
                super(National, self).delete()

        class dataimport(Operation):
                help_text = _(u"导入数据") #导入
                verbose_name = _(u"导入")
                visible = False
                def action(self):
                        pass

        class _delete(Operation):
                help_text = _(u"删除民族") #删除选定的记录
                verbose_name = _(u"删除")
                def action(self):
                        from datetime import datetime
                        from model_emp import Employee
                        emp = National.employee_set.related.model
                        if len(emp.objects.filter(national=self.object)) > 0:
                                raise Exception, _(u'该民族还有人员，不能删除')
                        if self.object.id > 0 and self.object.id < 57:
                            raise Exception, _(u'默认民族不能删除')
                        self.object.invalidate = datetime.now().strftime("%Y-%m-%d")
                        self.object.status = STATUS_INVALID
                        self.object.delete()

        
        class Admin(CachingModel.Admin):
                sort_fields = ["id"]
                app_menu = "personnel"
                help_text = _(u"如果新增的民族在民族列表中未能显示，请联系管理员到用户编辑中重新授权民族！")
                list_display = ('code', 'name', )
                adv_fields = ['code', 'name']            
                import_fields = ['code', 'name']
                visible = False
                query_fields = ['code', 'name']
                menu_index = 1
                cache = 3600
                default_give_perms = ["contenttypes.can_BaseDataPage",]
                report_fields=['code', 'name']

        class Meta:
                app_label = 'personnel'
                db_table = 'personnel_national'
                verbose_name = _(u'民族')
                verbose_name_plural = verbose_name

class NationalForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(NationalForeignKey, self).__init__(National, to_field=to_field, **kwargs)
                








