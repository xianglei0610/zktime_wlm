#!/usr/bin/env python
#coding=utf-8
#导入的时候，excel表中不能有空的sheet表，如果有的话，请先删除，每个表的表头为model中的字段
#然后还得在下面配置导入表的路径，导出表的路径，以及到处到哪个应用中的表
#必须下载xlsreader，下载地址：http://www.lexicon.net/sjmachin/xlrd.htm
import xlrd
import string

xlsName="basecodedata.xls"
jsonFileName="basecodedata.json"
dbTableName="base.BaseCode"

def xlsToJson(strXls,strJsonFile,strDbTable):
        wb=xlrd.open_workbook(strXls)
        f=open(strJsonFile,"w")
        listWorksheet=[]
        count=0
        for name in wb.sheet_names():
#                sh=wb.sheet_by_index(0)
                sh=wb.sheet_by_name(name)
                listJson=[]

                columnes=[]
                for r in range(sh.nrows):
                        if r==0:
                                columnes=sh.row_values(r)
                        else:
                                count+=1
                                dictObject={}
                                tempList=sh.row_values(r)
                                dictObject["model"]=strDbTable
                                dictObject["pk"]=str(count)
                                tempDict=dict([("%s"%c,"%s"%d) for c,d in zip(columnes,tempList)])
                                dictObject["fields"]=tempDict
                                listJson.append(dictObject)
                 
                strJson=""
                listJsonOther=[]
                for i in range(len(listJson)):
                        listObj=[]
                        dictTemp=listJson[i]
                        
                        for k in dictTemp:
                                if 'fields'!=k:
                                        try:
                                                dictTemp[k]=int(float(dictTemp[k]))
                                                listObj.append('"%s":%s'%(k,dictTemp[k]))
                                        except:
                                                listObj.append('"%s":"%s"'%(k,dictTemp[k]))
                                else:
                                        strObj=""
                                        listField=[]
                                        dictFields=dictTemp["fields"]
                                        for kf in dictFields:
                                                try:
                                                        dictFields[kf]=int(float(dictFields[kf]))
                                                        listField.append('"%s":%s'%(kf,dictFields[kf]))
                                                except:
                                                        listField.append('"%s":"%s"'%(kf,dictFields[kf]))
                                        strObj='"fields":{'+",".join(listField)+"}"
                                        listObj.append(strObj)
                        listJsonOther.append("{"+",\n".join(listObj)+"}")

                strJson=",\n".join(listJsonOther)
                listWorksheet.append(strJson)


        from StringIO import StringIO
        import sys
        buff=StringIO()
        temp=sys.stdout
        sys.stdout=buff
        print "["+",\n".join(listWorksheet)+"]"
        sys.stdout=temp
        
        
        f.write(buff.getvalue().encode("utf8"))
        f.close()
        
if __name__=="__main__":
        xlsToJson(xlsName,jsonFileName,dbTableName)