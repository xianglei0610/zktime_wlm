# coding=utf-8

from decimal import Decimal

def decquan(d,leng=1,flag=1):
    '''
    浮点计算
    
    d 为Decimal 类型
    返回 0.000 的 Decimal 类型
    '''
    from decimal import Decimal,ROUND_HALF_UP,ROUND_DOWN
    if leng==1:     
       if flag==0:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_HALF_UP)
       else:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_DOWN) 
    else:
       if flag==0:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_HALF_UP)
       else:
          return Decimal(str(d)).quantize(Decimal('0.000'),ROUND_DOWN)

def intdata(source,min,flag=0):
    '''
    舍入计算
    
    source 原数据 字符型
    min  最小单位 整型
    flag 舍入类型 整型
    '''
    import decimal
    if min==0:
       min =1
    if flag==0:
       try:
          if min!=1:
             if min>1:
                 ret = int(source)/int(min)*min
             else:
                 ret=decimal.Decimal(str(source))//decimal.Decimal(str(min))*decimal.Decimal(str(min))#float
#                ret = float(source)//min*min #向下 舍入 bug
          else:
             ret = int(source) 
       except:
          import traceback;traceback.print_exc()
          ret = source
    if flag==1:   #四舍五入
        if min!=1:
           if min>1:
              if int(source)%int(min)>=(min/2 - 0.0000001):
                 ret = int(source)/int(min)*min+min
              else:
                 ret = int(source)/int(min)*min
           else:
              if int(source*100)%int(min*100)>=((min*100)/2 - 0.0000001):
                 ret = (int(source*100)/int(min*100)*min)+min
              else:
                 ret = (int(source*100)/int(min*100)*min) 
        else:
           if (source*100)%100>=50:
              ret = int(source) +1
           else:
              ret = int(source)
    if flag==2:    #向上取整，如果是最小单位大于20并且不是10的倍数则认为是大于20分钟向上取整成30分钟的情况。
        if min!=1:
           if min>1:
              if int(min)>20 and int(min)%10!=0:
                  if int(source)%(int(30 - min)+int(min))>=int(min):
                     ret = int(source)%30+30
                  else:
                     ret = int(source)%30
              else:  
                  if int(source)%int(min)>0:
                     ret = int(source)/int(min)*min+min
                  else:
                     ret = int(source)/int(min)*min
           else:
              if int(source*100)%int(min*100)>0:
                 ret = (int(source*100)/int(min*100)*min)+min
              else:
                 ret = (int(source*100)/int(min*100)*min) 
        else:
           if (source*100)%100>0:
              ret = int(source) +1
           else:
              ret = int(source)            
    return ret   


def deal_param(value,arg,WorkTimes,WorkDays):
    '''
    统计项目参数的作用
    '''
    ret = value
    if arg['Unit'] ==1:#小时
       ret = decquan(Decimal(str(value))/(60*60))
    if arg['Unit'] ==2:#分钟
       ret = decquan(Decimal(str(value))/60)
    if arg['Unit'] ==3:#工作日
       if WorkTimes!=0:
          ret = decquan(Decimal(str(value))/(WorkTimes))*decquan(WorkDays)
       else:
          ret = decquan(Decimal(str(value))/(480*60))*decquan(WorkDays) 
    ret = intdata(ret,arg['MinUnit'],arg['RemaindProc'])
    return ret