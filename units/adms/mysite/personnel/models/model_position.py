# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_dept import DeptForeignKey, DEPT_NAME, Department
from base.models import CachingModel, Operation
from base.operation import ModelOperation
from base.cached_model import STATUS_INVALID
from django.conf import settings
from dbapp.datautils import filterdata_by_user
from base.middleware import threadlocals

POSITION_NAME = _(u"职位")
POSITION_NAME_2 = _(u"职位名称")
POSITION_NAME_ID = _(u"职位编号")



class Position(CachingModel):
        id = models.AutoField(_(u'职位ID'),  primary_key=True, editable=False)
        name = models.CharField(POSITION_NAME_2,  max_length=50)
        code = models.CharField(POSITION_NAME_ID, max_length=20, null=True, blank=True)
        DeptID = DeptForeignKey(verbose_name=DEPT_NAME, editable=True, null=True, blank=False)

        

 
        @staticmethod
        def clear():
            #为保证服务器和设备中数据的一致性，删除省份前先删除这些省份所包含的人员。-comment by darcy
            positions_to_clear = Position.objects.exclude(id=1)
            from mysite.personnel.models import Employee
            emps_to_clear = Employee.objects.filter(position__in=positions_to_clear)

            for emp in emps_to_clear:
                emp.delete()
            for position in positions_to_clear:
                position.delete()

        def __unicode__(self):
                if self.code:
                        return u"%s %s" % (self.code, self.name)
                else:
                        return u"%s" % self.name
        def export_unicode(self):
                return u"%s" % self.name
        
        def data_valid(self, sendtype):
            #print "sendtype:%s" % sendtype
            tmp = Position.objects.filter(code__exact=self.code)
            if self.code and len(tmp) > 0 and tmp[0].id != self.id:
                raise Exception(_(u'职位编号已经存在!'))

        def save(self):
                if not self.code:
                    raise Exception(_(u'职位编号不能为空!'))
                

                tmp = Position.objects.filter(code__exact=self.code)
                if self.code and len(tmp) > 0 and tmp[0].id != self.id:
                    raise Exception(_(u'职位编号已经存在!'))
                

                super(Position,self).save()

                
        def delete(self):
#            if self.pk != 1:
#                self.positionadmin_set.all().delete()
                super(Position, self).delete()

        class dataimport(Operation):
                help_text = _(u"导入数据") #导入
                verbose_name = _(u"导入")
                visible = False
                def action(self):
                        pass

        class _delete(Operation):
                help_text = _(u"删除职位") #删除选定的记录
                verbose_name = _(u"删除")
                def action(self):
                        from datetime import datetime
                        from model_emp import Employee
                        emp = Position.employee_set.related.model

                        if len(emp.objects.filter(position=self.object)) > 0:
                                raise Exception, _(u'该职位还有人员，不能删除')
#                        if self.object.id == 1:
#                            raise Exception, _(u'默认职位不能删除')
                        self.object.invalidate = datetime.now().strftime("%Y-%m-%d")
                        self.object.status = STATUS_INVALID
#                        positionadmin = Position.positionadmin_set.related.model
#                        positionadmin.objects.filter(position=self.object).delete()
                        self.object.delete()


        
        class Admin(CachingModel.Admin):
                disable_inherit_perms = ["dataimport"]
                sort_fields = ["name", "code"]
                app_menu = "personnel"
                help_text = _(u"如果新增的职位在职位列表中未能显示，请联系管理员到用户编辑中重新授权职位！")
                search_fields = ['name', 'code', ]
                list_display = ('DeptID.code', 'DeptID.name', 'code', 'name', )
                
                adv_fields = ['DeptID.code', 'DeptID.name', 'code', 'name']
                
                
                import_fields = ['code', 'name']

                query_fields = ['code', 'name']

                menu_index = 2
                cache = 3600
                report_fields=['code', 'name']
        class Meta:
                app_label = 'personnel'
                db_table = 'personnel_positions'
                ordering = ('code', 'name',)
                verbose_name = _(u'职位')
                verbose_name_plural = verbose_name

class PositionForeignKey(models.ForeignKey):
        def __init__(self, to_field=None, **kwargs):
                super(PositionForeignKey, self).__init__(Position, to_field=to_field, **kwargs)






