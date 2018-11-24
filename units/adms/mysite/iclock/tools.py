#coding=utf-8

def getSQL_insert(table, **kwargs):
        """ 生成 insert SQL 语句
                """
        ks = ""
        vs = ""
        for k, v in kwargs.items():
                ks += k + ","
                if isNumber(v) or v == "null":
                        vs += str(v) + ","
                else:
                        vs += "'" + v + "',"
        return """INSERT INTO %s (%s) VALUES (%s)""" % (table, ks[:-1], vs[:-1])

def getSQL_update(table, **kwargs):
        """ 生成 update SQL 语句
                """
        kvs = ""
        kvs_where = ""
        for k, v in kwargs.items():
                if k.startswith("where"): # where 子句
                        kvs_where += k[5:] + "="
                        if isNumber(v) or v == "null":
                                kvs_where += str(v) + " and "
                        else:
                                kvs_where += "'" + v + "' and "
                else: # set 子句
                        if not v: continue # 空值没必要更新
                        if isNumber(v) or v == "null":
                                kvs += k + "=" + str(v) + ","
                        else:
                                kvs += k + "='" + v + "',"
        if kvs_where == "":
                return """UPDATE %s SET %s""" % (table, kvs[:-1])
        else:
                return """UPDATE %s SET %s WHERE %s""" % (table, kvs[:-1], kvs_where[:-4])

def getSQL_update_ex(table, dict):
        """ 生成 update SQL 语句
                """
        kvs = ""
        kvs_where = ""
        for k, v in dict.items():
                if k.startswith("where"): # where 子句
                        kvs_where += k[5:] + "="
                        if isNumber(v) or v == "null":
                                kvs_where += str(v) + " and "
                        else:
                                kvs_where += "'" + v + "' and "
                else: # set 子句
                        if not v: continue # 空值没必要更新
                        if isNumber(v) or v == "null":
                                kvs += k + "=" + str(v) + ","
                        else:
                                kvs += k + "='" + v + "',"
        if kvs_where == "":
                return """UPDATE %s SET %s""" % (table, kvs[:-1])
        else:
                return """UPDATE %s SET %s WHERE %s""" % (table, kvs[:-1], kvs_where[:-4])
        
        
        
def isNumber(num):
        """ 判断是否数字 (int float long)
                """
        try:
                abs(num)
                return True
        except:
                return False
        
def getStr_c(s):
        """ 获取 C语言系统 传输过来的数据的字符串
                """
        try:
                return s[:s.index("\0")]
        except:
                return s

def getFptemp_c(s):
        """ 获取 C语言系统 传输过来的指纹模版（后面填充的"\0"）
                """
        i = len(s) - 1
        while i > 0 and s[i] == "\0":
                i -= 1
        return s[:i]
        
def getStr_c_decode(s):
        """ 获取 C语言系统 传输过来的数据的字符串，并按 gb18030 解码
                """
        try:
                
                return unicode(s[:s.index("\0")].decode("gb18030"))
        except:
                return unicode(s.decode("gb18030"))
def getSQL_insert_ex(table, dict):
        """ 生成 insert SQL 语句
                """
        ks = ""
        vs = ""
        for k, v in dict.items():
                ks += k + ","
                if v==None:
                        v='null'
                if isNumber(v) or v == "null":
                        vs += str(v) + ","
                elif str(type(v))=="<type 'datetime.datetime'>":
                        vs+="'"+v.strftime('%Y-%m-%d %H:%M:%S')+"',"
                elif str(type(v))=="<type 'datetime.time'>":
                        #if DATABASE_ENGINE=='ado_mssql':
                                #vs+="'1899-12-30 "+v.strftime('%H:%M:%S')+"',"
                        #else:
                        vs+="'"+v.strftime('%H:%M:%S')+"',"
                else:
                        vs += "'" + v + "',"
        return """INSERT INTO %s (%s) VALUES (%s)""" % (table, ks[:-1], vs[:-1])
