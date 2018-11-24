# -*- coding: utf-8 -*-
from dbapp.import_data import ImportData
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.db.models.fields import AutoField
import xlrd
import types

class ImportDeptData(ImportData):
    u"部门导入类"
    def __init__(self,req,input_name = "import_data"):
        super(ImportDeptData, self).__init__(req,input_name)
        self.calculate_fields_verbose = [u"%s"%_(u"上级部门编号")]
        self.must_fields = [
            u"%s"%_(u"部门编号"),
            u"%s"%_(u"部门名称"),
            u"%s"%_(u"上级部门编号"),
        ]#必填字段
    def is_valid_record(self,index_code,index_name,index_pcode,current_dept,all_dept,store):
        u"判断是否设置了一个部门的上级部门为其自身或其子部门"
        stack = []
        stack.append(current_dept)
        while len(stack)>0:
            pop = stack.pop()
            store.insert(0,pop)
            for elem in all_dept:
                if pop[ index_pcode ] == elem[index_code]:
                    if elem[index_code] == current_dept[index_code]:#循环到了自己
                        return False
                    else:
                        stack.append(elem)                    
        return True
        
    def before_insert(self):
        u'''对self.records记录进行验证
            记录进行排序,防止插入子部门,
            按级别排序，同一级的部门一次性批量插入
        '''
        index_code = None
        index_name=None
        index_pcode = None
        for index in range(len(self.head)):
            e = self.head[index]
            if e == u"%s"%_(u"部门编号"):
                index_code =  index
            if e == u"%s"%_(u"部门名称"):
                index_name = index
            if e == u"%s"%_(u"上级部门编号"):
                index_pcode = index
        #验证是否有非法部门关系,并排序
        level_dict_depts = {}
        for elem in self.records:
            store = []
            if not self.is_valid_record(index_code,index_name,index_pcode,elem,self.records,store):
                self.errors.append(u"不能设置%s部门的上级部门为其自身或其子部门"%elem[index_name])
                return False
        
            for index in range(len(store)):#按照排好的顺序分级
                key = u"%s"%index
                v  = store[index]
                if not level_dict_depts.has_key(key):
                    level_dict_depts[ key ] = [ v ]
                else:
                    if v not in level_dict_depts[ key ]:
                        level_dict_depts[ key ].append( v )
                    
        #把字典转换为列表排序
        items = level_dict_depts.items()
        items.sort(lambda x1,x2: int(x1[0])- int(x2[0]))
        self.records = items
        return True
        #检查是否有循环调用的部门
        
        return True
    def sqlserver_insert(self):
        u"sqlserver 数据插入"
        from mysite.personnel.models import Department
        model_table = self.model_cls._meta.db_table
        v_f_db_names  = [ e.get_attname_column()[1] for e in self.valid_model_fields ]
        o_f_db_names  = [ e.get_attname_column()[1] for e in self.other_fields ]
        INSERT_SQL ="INSERT INTO %(table)s ( %(fields)s ) VALUES ( %(row)s )"
        
        cursor = connection.cursor()
        count_head = len(self.head) 
        sql_list = []
        dept_codes = [] 
        for level_key,level_value  in self.records:
            for row in level_value:
                row_fields_select = {}
                calculate_dict = {}
                count_v = 0
                for index in range(count_head):
                    for k,v in self.calculate_fields_index.items():#不在数据库中的计算字段
                        if v == index:
                            calculate_dict[ k ] = row[index]
                    
                    if index in self.valid_head_indexs:#在文档中的数据库字段
                        tmp_value = row[index]
                        tmp_field = self.valid_model_fields[count_v]
                        if tmp_field.choices:
                            tv = [ e[0] for e in tmp_field.choices if e[1] == tmp_value ] #通过verbose_name得到实际数据库的值
                            if tv:
                                tmp_value = tv[0]
                        key = v_f_db_names[count_v]
                        if key == "code":
                            dept_codes.append( tmp_value )
                        value = "'%s'"%(self.get_db_value(tmp_field,tmp_value))
                        row_fields_select[key] =  value
                        count_v = count_v +1
                
                count_o = 0
                for f in self.other_fields:#不在文档中的数据库字段
                    default_value = f.get_default()
                    if default_value == None:
                        default_value = "NULL"
                    else:
                        if default_value in (True,False):
                            default_value = u"'%s'"%int(default_value)
                        else:
                            default_value = u"'%s'"%default_value
                    key = o_f_db_names[count_o]
                    row_fields_select[ key ] =   default_value
                    count_o = count_o + 1
                    
                row_fields_select = self.process_row(row_fields_select,calculate_dict) #处理每一行的接口
                
                sql_list.append(INSERT_SQL%{
                    "table":model_table,
                    "fields":",".join(row_fields_select.keys()),
                    "row":",".join(row_fields_select.values())
                })
                
                
            if sql_list:
                depts = Department.objects.filter(code__in=dept_codes).values_list("code",flat= True) #同一级查一次数据库
                ret_sql_list = [ ]
                for index in range(len(dept_codes)):
                    if dept_codes[index] not  in depts:#已经有的数据就不插入了
                        ret_sql_list.append(sql_list[index])
                
                if ret_sql_list:
                    insert_sql = ";".join(ret_sql_list)
                    cursor.execute(insert_sql)
                sql_list = []
                dept_codes = []
        
        try:
            connection._commit()
        except:
            pass
                
    def mysql_insert(self):
        u"mysql 数据插入"
        from mysite.personnel.models import Department
        model_table = self.model_cls._meta.db_table
        v_f_db_names  = [ e.get_attname_column()[1] for e in self.valid_model_fields ]
        o_f_db_names  = [ e.get_attname_column()[1] for e in self.other_fields ]

        INSERT_SQL ="INSERT INTO %(table)s ( %(fields)s ) VALUES %(batch_rows)s "
        
        cursor = connection.cursor()
        count_head = len(self.head) 
        sql_list = [ ]
        dept_codes = [ ]
        calculate_dict = {}
        
        insert_keys = []
        for level_key,level_value  in self.records:
            for row in level_value:
                row_fields_select = {}
                count_v = 0
                for index in range(count_head):
                    for k,v in self.calculate_fields_index.items():
                        if v == index:
                            calculate_dict[ k ] = row[index]
                    
                    if index in self.valid_head_indexs:
                        tmp_value = row[index]
                        tmp_field = self.valid_model_fields[count_v]
                        if tmp_field.choices:
                            tv = [e[0] for e in tmp_field.choices if e[1] == tmp_value ] #通过verbose_name得到实际数据库的值
                            if tv:
                                tmp_value = tv[0]
                        key = v_f_db_names[count_v]
                        if key == "code":
                            dept_codes.append( tmp_value )
                        value = self.get_db_value(tmp_field,tmp_value)
                        if key =="DeptName":#如果部门名称为中文的话，必须添加""否则拼出的sql语句不对。cc20120806
                            row_fields_select[key] = '"%s"'%value
                        else:
                            row_fields_select[key] = value

                        #row_fields_select[key] = value
                        count_v = count_v +1
                
                count_o = 0
                for f in self.other_fields:
                    default_value = f.get_default()
                    if default_value == None:
                        default_value = "NULL"
                    else:
                        if default_value in (True,False):
                            default_value = u"'%s'"%int(default_value)
                        else:
                            default_value = u"'%s'"%default_value
                    key = o_f_db_names[count_o]
                    row_fields_select[key]=default_value
                    count_o = count_o + 1
                
                row_fields_select = self.process_row(row_fields_select,calculate_dict) #处理每一行的接口
                sql_list.append( "("+",".join(row_fields_select.values())+")" )
                
                if not insert_keys :
                    insert_keys = ",".join(row_fields_select.keys())
            if sql_list:
                depts = Department.objects.filter(code__in=dept_codes).values_list("code",flat= True) #同一级查一次数据库
                ret_sql_list = [ ]
                for index in range(len(dept_codes)):
                    if dept_codes[index] not  in depts:#已经有的数据就不插入了
                        ret_sql_list.append(sql_list[index])
                if ret_sql_list:
                    insert_sql = INSERT_SQL%{
                        "table":model_table,
                        "fields":insert_keys,
                        "batch_rows":",".join(ret_sql_list),
                    }
#                    print "start*************************************\n"
#                    print insert_sql
#                    print "*******************************************end\n"
                    cursor.execute(insert_sql)
                sql_list = []
                dept_codes = []
            
        try:
            connection._commit()
        except:
            pass
    
    def process_row(self,row_data,calculate_dict):
        u'''
            特殊情况给开发人员提供的接口
            row_data 这一行的数据
            calculate_dict 文档附加的列，如上级部门编号，
        '''
        from mysite.personnel.models import Department
        key = u"%s"%_(u"上级部门编号")
        #print "calculate_dict:",calculate_dict,"\n"
        dept_code = (u"%s"%calculate_dict[key]).strip()
        #print "COUNT:",len(dept_code),"\n"
        if dept_code != "":
            try:
                obj_dept = Department.objects.get(code = dept_code)
            except:
                #print 'row_data:',row_data, 'code:',dept_code,'\n'
                #判断是使用默认还是创建新的部门
                obj_dept = Department()
                obj_dept.code = u"%s"%dept_code
                obj_dept.name = u"%s"%dept_code
                obj_dept.parent_id = 1
                obj_dept.save()
                
            row_data["supdeptid"] = u"'%s'"%obj_dept.pk #初始化部门
        return row_data
