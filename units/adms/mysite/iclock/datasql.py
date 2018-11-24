#coding=utf-8
from django.utils.translation import ugettext as _
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response

def sql_page(request): # 生产【执行 SQL 语句】页面
        sql = str(request.POST.get("sql", "")).strip()
        get_content = u"""
                <br /><br /><br />
                <form id="form1" action="" method="POST">
                <div style="margin-left:100px;">
                        <input type="text" name="sql" value="%s" size="120" />
                        <input type="submit" name="submit" value="执行 SQL 语句" />
                </div>
                </form>        <hr /><br />
                """ % (sql)
        if sql:
                from django.db import connection as conn
                cursor = conn.cursor()
                try:
                        count = 50
                        if sql.startswith("select") or sql.startswith("SELECT") or sql.startswith("count="): # select 语句
                                if sql.startswith("count="):
                                        pos=sql.index(" ")
                                        count = int(sql[6:pos])
                                        sql = sql[pos+1:]
                                cursor.execute(sql)
                                conn._commit()
                                i, rs = 0, ""
                                while i < count:
                                        rs_one = cursor.fetchone()
                                        if rs_one is None:
                                                break
                                        rs += u"""<tr><td style='color:red;'>%d</td>""" % (i + 1)
                                        for row in rs_one:
                                                try:
                                                        rs += u"<td>%s</td>" % (row and row or "&nbsp")
                                                except:
                                                        rs += u"<td>[E]</td>"
                                        rs += u"""</tr>"""
                                        i += 1
                                rs = u"""<table border="1">%s</table>""" % (rs)
                                return HttpResponse(u"%s<h2>执行 %s 成功</h2><br />%s" % (get_content, str(sql), rs))
                        else:
                                cursor.execute(sql)
                                conn._commit()
                                return HttpResponse(u"%s执行 %s 成功" % (get_content, str(sql)))
                except Exception, args:
                        return HttpResponse(u"%s<h2>执行 %s 失败</h2><br /><br />%s" % (get_content, str(sql), str(Exception)+str(args)))
        return HttpResponse(get_content)
