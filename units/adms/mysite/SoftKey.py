# -*- coding: utf-8 -*-
# Filename : SoftKey.py

from ctypes import *
from ctypes.wintypes import LPCSTR
from random import *

prototype = WINFUNCTYPE(c_int, c_int, LPCSTR)
paramflags = (1, "start"), (1, "KeyPath")
FindPort = prototype(("FindPort", windll.my3l_ex), paramflags)

prototype = WINFUNCTYPE(c_int, LPCSTR, LPCSTR,POINTER(c_ubyte
),POINTER(c_ubyte
),LPCSTR)
paramflags = (1, "HKEY"), (1, "LKEY"), (1, "InBuf"), (1, "OutBuf"), (1, "KeyPath")
E_Dec_6 = prototype(("E_Dec_6", windll.my3l_ex), paramflags)

prototype = WINFUNCTYPE(c_int, LPCSTR, c_short,c_int,LPCSTR)
paramflags = (1, "OutString"), (1, "Address"), (1, "Outlen"), (1, "KeyPath")
ReadString = prototype(("ReadString", windll.my3l_ex), paramflags)

prototype = WINFUNCTYPE(c_int, LPCSTR, c_short,LPCSTR)
paramflags = (1, "InString"), (1, "Address"),  (1, "KeyPath")
WriteString = prototype(("WriteString", windll.my3l_ex), paramflags)

global E_Hkey,E_Lkey,KeyPath,LastError

def GetLastError():
  return LastError

def F_ReadKey():
  global E_Hkey,E_Lkey,KeyPath
  temp=c_int()
  for n in range(0, 4):

    ret=windll.my3l_ex.YReadEx(n,byref(temp),KeyPath)
    if ret==0:
      E_Hkey=format(temp.value,"02X")+E_Hkey
    else:
      return -1

    ret=windll.my3l_ex.YReadEx(n+4,byref(temp),KeyPath)
    if ret==0:
      E_Lkey=format(temp.value,"02X")+E_Lkey
    else:
      return -1

  else:
    return 0
    u'''加机器的时候验证'''
    pass

#输出函数Ini:(注意：这个函数必须被首先调用）
#目的：初步检查是否存在用户锁，如果有存在，提示用户插入用户锁。在程序初始化时，一定要使用这段代码
def Ini():
  ##以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式一定为：a=123,b=123,c=123,d=123
  #//该表达式只是初步用来检查是否存在加密锁
  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray(52, 107, 12, 152, 79, 49, 23, 94, 144, 108,  97, 19,  201,  167, 55, 70)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  KeyPath=create_string_buffer('\0'*260)
  a=c_ubyte()
  b=c_ubyte()
  c=c_ubyte()
  d=c_ubyte()
  start=0
  E_Hkey =''
  E_Lkey =''
  while LastError == 0 :#这里之所以要做循环，是由于系统中可能会存在多把加密锁
    LastError = FindPort(start, KeyPath)
    print "soft key LastError",LastError
    if LastError != 0 :
       break
    else:
      start = start + 1

    #  //从相应的加密锁储存器中读出相应的授权号
    if F_ReadKey()!=0 :
       break

    #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
    # //然后返回加密后的数据（该加密后的数据与该加密锁相对应）
    # //只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
    LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
    if LastError != 0 :
       break

    LastError = windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(a), byref(b), byref(c), byref(d), KeyPath, 16, 2000)

    if (a.value == 123) and (b.value == 123) and (c.value == 123) and (d.value == 123):
       return 0

  else:

    E_Hkey = "0"
    E_Lkey = "0"
    LastError=-93
    #print ("不存在对应的用户锁。请插入对应的用户锁。")
    return LastError




#输出函数Ini_2:(注意：这个函数必须被首先调用），该函数不能与ini函数一同使用。
#参数1：用户输入的授权号的高八位。
#参数2：用户输入的授权号的低八位。
#目的：使用授权号的方式初步检查是否存在用户锁，如果有存在，提示用户插入用户锁。在程序初始化时，一定要使用这段代码
def Ini_2(HKey , LKey):
  ##以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式一定为：a=123,b=123,c=123,d=123
  #//该表达式只是初步用来检查是否存在加密锁
  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray(52, 107, 12, 152, 79, 49, 23, 94, 144, 108,  97, 19,  201,  167, 55, 70)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  KeyPath=create_string_buffer('\0'*260)
  a=c_ubyte()
  b=c_ubyte()
  c=c_ubyte()
  d=c_ubyte()
  start=0
  E_Hkey = HKey
  E_Lkey = LKey
  while LastError == 0 :#这里之所以要做循环，是由于系统中可能会存在多把加密锁
    LastError = FindPort(start, KeyPath)
    if LastError != 0 :
       break
    else:
      start = start + 1

    #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
    # //然后返回加密后的数据（该加密后的数据与该加密锁相对应）
    # //只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
    LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
    if LastError != 0 :
       break

    LastError = windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(a), byref(b), byref(c), byref(d), KeyPath, 16, 2000)

    if (a.value == 123) and (b.value == 123) and (c.value == 123) and (d.value == 123):
       return 0

  else:

    LastError=-93
    #print ("不存在对应的用户锁。请插入对应的用户锁。")
    return LastError



#输出函数Ystrcat
#目的：用来对两个字符串进行连接
#参数s1：要连接的两个字符串之一
#参数s2：要连接的两个字符串之一
#返回结果：#返回结果：返回目的字符串
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def Ystrcat(s1,s2):

  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：a=a^d,b=b^12,c=c>1,a=a>1,a=a^c,a=a^d,c=c>1,c=c>1

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 243, 47, 39, 106, 193, 114, 189, 33, 101, 37,  141, 61,  33,  63, 141, 248)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return ''
  #///////////////////////////////加密字符串1////////////////////////////////////////////////////////////
  temp_s=c_char_p(s1)
  #获取字符串的长度
  s_len=len(s1)
  #定义局部变量

  #根据字符串的长度对临时变量进行付值，以便以后对其进行加密处理
  if(s_len>0):
    temp_a=c_ubyte(ord(temp_s.value[0]))#取字符串的第一个值到变量temp_a;
  else:
    temp_a=c_ubyte(0)

  if(s_len>1):
    temp_b=c_ubyte(ord(temp_s.value[1]))#取字符串的第二个值到变量temp_b;
  else:
    temp_b=c_ubyte(0)

  if(s_len>2):
    temp_c=c_ubyte(ord(temp_s.value[2]))#取字符串的第三个值到变量temp_c;
  else:
    temp_c=c_ubyte(0)

  if(s_len>3):
    temp_d=c_ubyte(ord(temp_s.value[3]))#取字符串的第四个值到变量temp_d;
  else:
    temp_d=c_ubyte(0)

  #这步将a,b,d变量的到加密锁内部进行相加运算,
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(temp_c), byref(temp_d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return ''

  ############
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_c.value).value
  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))
  temp_b.value= temp_b.value ^ c_ubyte(12).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value


  #在加密锁运算后的结果返回到变量temp_a,temp_b,temp_c,temp_d中
  #再将结果送回到字符串中
  #ret_s1=s1;
  temp_s=create_string_buffer('\0'*len(s1)*2)
  temp_s.value=s1
  if(s_len>0):
    temp_s[0]=chr(temp_a.value)#将变量temp_a的值放到字符串中;
  if(s_len>1):
    temp_s[1]=chr(temp_b.value)#将变量temp_b的值放到字符串中
  if(s_len>2):
    temp_s[2]=chr(temp_c.value)#将变量temp_c的值放到字符串中
  if(s_len>3):
    temp_s[3]=chr(temp_d.value)#将变量temp_d的值放到字符串中

  ret_string=create_unicode_buffer(temp_s.value).value
  #///////////////////////////////////加密字符串2////////////////////////////////////
  temp_s=c_char_p(s2)
  #获取字符串的长度
  s_len=len(s2)
  #定义局部变量

  #根据字符串的长度对临时变量进行付值，以便以后对其进行加密处理
  if(s_len>0):
    temp_a=c_ubyte(ord(temp_s.value[0]))#取字符串的第一个值到变量temp_a;
  else:
    temp_a=c_ubyte(0)

  if(s_len>1):
    temp_b=c_ubyte(ord(temp_s.value[1]))#取字符串的第二个值到变量temp_b;
  else:
    temp_b=c_ubyte(0)

  if(s_len>2):
    temp_c=c_ubyte(ord(temp_s.value[2]))#取字符串的第三个值到变量temp_c;
  else:
    temp_c=c_ubyte(0)

  if(s_len>3):
    temp_d=c_ubyte(ord(temp_s.value[3]))#取字符串的第四个值到变量temp_d;
  else:
    temp_d=c_ubyte(0)

  #这步将a,b,d变量的到加密锁内部进行相加运算,
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(temp_c), byref(temp_d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return ''

  ############
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_c.value).value
  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))
  temp_b.value= temp_b.value ^ c_ubyte(12).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value


  #在加密锁运算后的结果返回到变量temp_a,temp_b,temp_c,temp_d中
  #再将结果送回到字符串中
  #ret_s2=s2;
  temp_s=create_string_buffer('\0'*len(s2)*2)
  temp_s.value=s2
  if(s_len>0):
    temp_s[0]=chr(temp_a.value)#将变量temp_a的值放到字符串中;
  if(s_len>1):
    temp_s[1]=chr(temp_b.value)#将变量temp_b的值放到字符串中
  if(s_len>2):
    temp_s[2]=chr(temp_c.value)#将变量temp_c的值放到字符串中
  if(s_len>3):
    temp_s[3]=chr(temp_d.value)#将变量temp_d的值放到字符串中

  #连接两个字符串
  ret_string=ret_string+create_unicode_buffer(temp_s.value).value

  return  ret_string




#输出函数YCompareString
#目的：用来对两个字符串进行比较
#参数s1：要比较的两个字符串之一
#参数s2：要比较的两个字符串之一
#返回结果：如果为0，两个字符串相等，如果为正数，s1>s2,如果为负数,s1<s2
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def YCompareString(s1,s2):

  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：c=c>1,d=d<1,b=b^c,a=a^c,a=a^b,a=a>1,b=b^c,d=d^96

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 128, 100, 235, 62, 166, 241, 229, 250, 110, 152,  25, 241,  143,  244, 5, 195)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return ''
  #///////////////////////////////加密字符串1////////////////////////////////////////////////////////////
  temp_s=c_char_p(s1)
  #获取字符串的长度
  s_len=len(s1)
  #定义局部变量

  #根据字符串的长度对临时变量进行付值，以便以后对其进行加密处理
  if(s_len>0):
    temp_a=c_ubyte(ord(temp_s.value[0]))#取字符串的第一个值到变量temp_a;
  else:
    temp_a=c_ubyte(0)

  if(s_len>1):
    temp_b=c_ubyte(ord(temp_s.value[1]))#取字符串的第二个值到变量temp_b;
  else:
    temp_b=c_ubyte(0)

  if(s_len>2):
    temp_c=c_ubyte(ord(temp_s.value[2]))#取字符串的第三个值到变量temp_c;
  else:
    temp_c=c_ubyte(0)

  if(s_len>3):
    temp_d=c_ubyte(ord(temp_s.value[3]))#取字符串的第四个值到变量temp_d;
  else:
    temp_d=c_ubyte(0)

  #这步将a,b,d变量的到加密锁内部进行相加运算,
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(temp_c), byref(temp_d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return ''
	###########
  temp_d.value= temp_d.value ^ c_ubyte(96).value
  temp_b.value= temp_b.value ^ c_ubyte(temp_c.value).value
  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_a.value= temp_a.value ^ c_ubyte(temp_b.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_c.value).value
  temp_b.value= temp_b.value ^ c_ubyte(temp_c.value).value
  temp_d.value= ((temp_d.value << c_ubyte(7).value) | (temp_d.value >>c_ubyte(1).value))
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))


  #在加密锁运算后的结果返回到变量temp_a,temp_b,temp_c,temp_d中
  #再将结果送回到字符串中
  #ret_s1=s1;
  temp_s=create_string_buffer('\0'*len(s1)*2)
  temp_s.value=s1
  if(s_len>0):
    temp_s[0]=chr(temp_a.value)#将变量temp_a的值放到字符串中;
  if(s_len>1):
    temp_s[1]=chr(temp_b.value)#将变量temp_b的值放到字符串中
  if(s_len>2):
    temp_s[2]=chr(temp_c.value)#将变量temp_c的值放到字符串中
  if(s_len>3):
    temp_s[3]=chr(temp_d.value)#将变量temp_d的值放到字符串中

  ret_string=create_unicode_buffer(temp_s.value).value
#///////////////////////////////////加密字符串2////////////////////////////////////
  temp_s=c_char_p(s2)
  #获取字符串的长度
  s_len=len(s2)
  #定义局部变量

  #根据字符串的长度对临时变量进行付值，以便以后对其进行加密处理
  if(s_len>0):
    temp_a=c_ubyte(ord(temp_s.value[0]))#取字符串的第一个值到变量temp_a;
  else:
    temp_a=c_ubyte(0)

  if(s_len>1):
    temp_b=c_ubyte(ord(temp_s.value[1]))#取字符串的第二个值到变量temp_b;
  else:
    temp_b=c_ubyte(0)

  if(s_len>2):
    temp_c=c_ubyte(ord(temp_s.value[2]))#取字符串的第三个值到变量temp_c;
  else:
    temp_c=c_ubyte(0)

  if(s_len>3):
    temp_d=c_ubyte(ord(temp_s.value[3]))#取字符串的第四个值到变量temp_d;
  else:
    temp_d=c_ubyte(0)

  #这步将a,b,d变量的到加密锁内部进行相加运算,
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(temp_c), byref(temp_d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return ''
	###########
  temp_d.value= temp_d.value ^ c_ubyte(96).value
  temp_b.value= temp_b.value ^ c_ubyte(temp_c.value).value
  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_a.value= temp_a.value ^ c_ubyte(temp_b.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_c.value).value
  temp_b.value= temp_b.value ^ c_ubyte(temp_c.value).value
  temp_d.value= ((temp_d.value << c_ubyte(7).value) | (temp_d.value >>c_ubyte(1).value))
  temp_c.value= ((temp_c.value << c_ubyte(1).value) | (temp_c.value >>c_ubyte(7).value))


  #在加密锁运算后的结果返回到变量temp_a,temp_b,temp_c,temp_d中
  #再将结果送回到字符串中
  #ret_s2=s2;
  temp_s=create_string_buffer('\0'*len(s2)*2)
  temp_s.value=s2
  if(s_len>0):
    temp_s[0]=chr(temp_a.value)#将变量temp_a的值放到字符串中;
  if(s_len>1):
    temp_s[1]=chr(temp_b.value)#将变量temp_b的值放到字符串中
  if(s_len>2):
    temp_s[2]=chr(temp_c.value)#将变量temp_c的值放到字符串中
  if(s_len>3):
    temp_s[3]=chr(temp_d.value)#将变量temp_d的值放到字符串中

  #比较两个字符串是否相等
  return  (ret_string==create_unicode_buffer(temp_s.value).value)




#输出函数Ystrcpy
#目的：对字符串进行复制
#参数sd：目的字符串
#参数s:源字符串
#返回结果：要进行设置的值
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def Ystrcpy(s):

  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：a=a^117,a=a^222,d=d<1,a=a^d,d=d^b,b=b^204,a=a>1,a=a^d

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 83, 155, 36, 81, 43, 24, 99, 72, 26, 58,  236, 30,  16,  173, 97, 4)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return ''
  #/////////////////////////////////////////////////////////////////////////////////////////////////////

  temp_s=c_char_p(s)
  #获取字符串的长度
  s_len=len(s)
  #定义局部变量

  #根据字符串的长度对临时变量进行付值，以便以后对其进行加密处理
  if(s_len>0):
    temp_a=c_ubyte(ord(temp_s.value[0]))#取字符串的第一个值到变量temp_a;
  else:
    temp_a=c_ubyte(0)

  if(s_len>1):
    temp_b=c_ubyte(ord(temp_s.value[1]))#取字符串的第二个值到变量temp_b;
  else:
    temp_b=c_ubyte(0)

  if(s_len>2):
    temp_c=c_ubyte(ord(temp_s.value[2]))#取字符串的第三个值到变量temp_c;
  else:
    temp_c=c_ubyte(0)

  if(s_len>3):
    temp_d=c_ubyte(ord(temp_s.value[3]))#取字符串的第四个值到变量temp_d;
  else:
    temp_d=c_ubyte(0)

  #这步将a,b,d变量的到加密锁内部进行相加运算,
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(temp_c), byref(temp_d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return ''

  ############
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value
  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_b.value= temp_b.value ^ c_ubyte(204).value
  temp_d.value= temp_d.value ^ c_ubyte(temp_b.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value
  temp_d.value= ((temp_d.value << c_ubyte(7).value) | (temp_d.value >>c_ubyte(1).value))
  temp_a.value= temp_a.value ^ c_ubyte(222).value
  temp_a.value= temp_a.value ^ c_ubyte(117).value



  #在加密锁运算后的结果返回到变量temp_a,temp_b,temp_c,temp_d中
  #再将结果送回到字符串中
  #ret_s=s;
  temp_s=create_string_buffer('\0'*len(s)*2)
  temp_s.value=s
  if(s_len>0):
    temp_s[0]=chr(temp_a.value)#将变量temp_a的值放到字符串中;
  if(s_len>1):
    temp_s[1]=chr(temp_b.value)#将变量temp_b的值放到字符串中
  if(s_len>2):
    temp_s[2]=chr(temp_c.value)#将变量temp_c的值放到字符串中
  if(s_len>3):
    temp_s[3]=chr(temp_d.value)#将变量temp_d的值放到字符串中

  return create_unicode_buffer(temp_s.value).value




#输出函数YSetValue
#目的：用来对长整形变量进行值的设置
#参数a：要进行设置的长整形变量
#返回结果：返回设置的长整形变量
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def YSetValue(a):

  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：c=c>1,a=a^b,a=a^d,c=c<1,c=c^a,a=a^b,b=b^a,a=a^135

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 240, 227, 86, 141, 7, 176, 55, 133, 247, 221,  178, 47,  176,  42, 26, 15)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return 0
  #/////////////////////////////////////////////////////////////////////////////////////////////////////

  b_negative=0 #定义局部变量，用于储存是否负数
  if(a<0):
    a=-a
    b_negative=1#如果为负数，将a变为正数，然后设置负数属性

  #定义局部变量

  #将a变量除以256后取余
  #因为CalculateEx_2表达式只接受字节变量，不能超过256，
  temp_a=c_ubyte(a%256)
  #将a变量减去余数，
  #为什么要将a变量减去余数呢？
  #因为余数准备在加密锁内部参加，所以a变量要减去自己的余数。
  a=a-temp_a.value
  b=c_ubyte(randint(0, 255))
  c=c_ubyte(randint(0, 255))
  d=c_ubyte(randint(0, 255))
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(b), byref(c), byref(d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return 0

  ############
  temp_a.value= temp_a.value ^ c_ubyte(135).value
  b.value= b.value ^ c_ubyte(temp_a.value).value
  temp_a.value= temp_a.value ^ c_ubyte(b.value).value
  c.value= c.value ^ c_ubyte(temp_a.value).value
  c.value= ((c.value << c_ubyte(7).value) | (c.value >>c_ubyte(1).value))
  temp_a.value= temp_a.value ^ c_ubyte(d.value).value
  temp_a.value= temp_a.value ^ c_ubyte(b.value).value
  c.value= ((c.value << c_ubyte(1).value) | (c.value >>c_ubyte(7).value))



  #在加密锁运算后的结果返回到变量temp_a中
  #我们再将其与先前减去余数的a变量相加就可以了。
  if(b_negative):
    return -(temp_a.value+a);#如果a为负数，直接相加temp_a，然后取负数;
  else:
    return temp_a.value+a #如果均为正数,直接相加temp_a




#输出函数:compare
#目的：用来比较两个数的大小，相当于?a>b,a<b,a=b
#参数p1：要比较的第一个数
#参数p2：要比较的第二个数
#参数c：是大于，小于或等于，即">","<","="
#返回结果：
#如果返回0，表示表达式为假，返回1表示表达式为真
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def compare( p1 , p2, exp):
  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：c=c^28,c=c^d,c=c^11,b=b>1,d=d<1,b=b^a,a=a^b,d=d^a

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 140, 29, 210, 149, 117, 18, 93, 84, 210, 201,  12, 233,  250,  245, 190, 216)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return 0
  #/////////////////////////////////////////////////////////////////////////////////////////////////////

  #定义局部变量
  #将p1分拆成四个字节。
  a=c_ubyte(p1)
  b=c_ubyte(p1>>8)
  c=c_ubyte(p1>>16)
  d=c_ubyte(p1>>24)

  #这步将a,b,d变量的到加密锁内部进行相加运算,
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(a), byref(b), byref(c), byref(d), KeyPath, 16, 2000)
  if ( LastError!= 0):
    return 0

  d.value= d.value ^ c_ubyte(a.value).value
  a.value= a.value ^ c_ubyte(b.value).value
  b.value= b.value ^ c_ubyte(a.value).value
  d.value= ((d.value << c_ubyte(7).value) | (d.value >>c_ubyte(1).value))
  b.value= ((b.value << c_ubyte(1).value) | (b.value >>c_ubyte(7).value))
  c.value= c.value ^ c_ubyte(11).value
  c.value= c.value ^ c_ubyte(d.value).value
  c.value= c.value ^ c_ubyte(28).value


  #定义局部变量
  temp_a=c_int(a.value)
  temp_b=c_int(b.value)
  temp_c=c_int(c.value)
  temp_d=c_int(d.value)
  #将四个字节再合并成一个长整型
  p1=(temp_a.value)|(temp_b.value<<8)|(temp_c.value<<16)|(temp_d.value<<24);
  if(exp=='>'):
    return p1>p2;

  if(exp=='<'):
    return p1<p2;

  if(exp=='='):
    return p1==p2;

  LastError=-3;#表示c参数错误
  return 0;




#输出函数:CheckKey
#目的：用来检查是否存在对应的加密锁
#返回结果：
#如果返回假，表示未找到对应的加密锁或未注册或注册错误，返回真,表示存在对应的加密锁
def  CheckKey():
  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：b=b^c,a=a^b,a=a^d,b=b>1,d=d>1,b=b>1,c=c^192,c=c^a

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 3, 206, 140, 55, 77, 104, 70, 167, 25, 91,  255, 143,  100,  73, 162, 106)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return 0
  
  #/////////////////////////////////////////////////////////////////////////////////////////////////////
  #产生随机数
  a=c_ubyte(randint(0, 255))
  b=c_ubyte(randint(0, 255))
  c=c_ubyte(randint(0, 255))
  d=c_ubyte(randint(0, 255))

  temp_a = a
  temp_b = b
  temp_c = c
  temp_d = d
  #送到加密锁内进行运算，
  if (windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(a), byref(b), byref(c), byref(d), KeyPath, 16, 2000) != 0):
    return 0

  ############
  temp_b.value= temp_b.value ^ c_ubyte(temp_c.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_b.value).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_d.value).value
  temp_b.value= ((temp_b.value << c_ubyte(7).value) | (temp_b.value >>c_ubyte(1).value))
  temp_d.value= ((temp_d.value << c_ubyte(7).value) | (temp_d.value >>c_ubyte(1).value))
  temp_b.value= ((temp_b.value << c_ubyte(7).value) | (temp_b.value >>c_ubyte(1).value))
  temp_c.value= temp_c.value ^ c_ubyte(192).value
  temp_c.value= temp_c.value ^ c_ubyte(temp_a.value).value



  #如果相同，则存在对应加密锁，否则，不存在对应的加密锁
  if (a == temp_a) and (b == temp_b) and (c == temp_c) and (d == temp_d) :
    return 1
  else:
      return 0



#输出函数YAnd:
#目的：YAnd函数作用：用来对两个布尔变量进行逻辑“与(&&)”运算，并返回运算结果
#参数a：要进行逻辑运算的变量1
#参数b：要进行逻辑运算的变量2
#返回结果：两个变量进行逻辑与运算后的结果
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def YAnd( a, b):

  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：a=a<1,a=a^205,a=a^d,a=a^101,a=a<1,a=a^d,a=a^28,a=a&b

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 147, 5, 26, 29, 163, 14, 69, 249, 222, 101,  191, 179,  145,  234, 227, 94)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return 0
  #/////////////////////////////////////////////////////////////////////////////////////////////////////

  #定义局部变量
  if( a ):
    temp_a = c_ubyte(1);
  else:
    temp_a = c_ubyte(0);

  if (b ):
    temp_b = c_ubyte(1);
  else:
    temp_b = c_ubyte(0);

  c=c_ubyte(randint(0, 255))
  d=c_ubyte(randint(0, 255))
  #这步将temp_a,temp_b变量送到加密锁内部进行与运算,c,d变量忽略。

  temp_a.value= temp_a.value ^ c_ubyte(28).value
  temp_a.value= temp_a.value ^ c_ubyte(d.value).value
  temp_a.value= ((temp_a.value << c_ubyte(7).value) | (temp_a.value >>c_ubyte(1).value))
  temp_a.value= temp_a.value ^ c_ubyte(101).value
  temp_a.value= temp_a.value ^ c_ubyte(d.value).value
  temp_a.value= temp_a.value ^ c_ubyte(205).value
  temp_a.value= ((temp_a.value << c_ubyte(7).value) | (temp_a.value >>c_ubyte(1).value))
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(c), byref(d), KeyPath, 16, 2000)



  if ( LastError!= 0):
    return 0


  #在加密锁运算后的结果返回到变量temp_a中
  return c_bool(temp_a).value;




#输出函数Yor:
#目的：Yor函数作用：用来对两个布尔变量进行逻辑“与(||)”运算，并返回运算结果
#参数a：要进行逻辑运算的变量1
#参数b：要进行逻辑运算的变量2
#返回结果：两个变量进行逻辑与运算后的结果
#如果错误码LastError=0，操作正确，如果LastError为负数，请参见操作手册
def Yor( a, b):

  #//以下是由域天工具随机生成的加密后的加密表达式，
  #//其中被加密的表达式为：a=a^b,a=a^218,a=a|b,a=a^c,a=a>1,a=a^d,a=a^c,a=a>1

  global E_Hkey,E_Lkey,KeyPath,LastError
  ret=0
  InArray =c_ubyte*16
  InBuf=InArray( 188, 198, 206, 7, 7, 42, 235, 69, 42, 121,  98, 132,  172,  5, 92, 131)
  OutArray=c_ubyte(16)
  LastError = 0 # 初始化错误码为无错误

  #//将加密后的表达式送到加密锁中进行解密并重新加密（使用相应的授权号），即注册或转换
  #//然后返回加密后的数据（该加密后的数据与该加密锁相对应）
  #//只有被对应的授权号进行转换的数据才能被对应的加密锁解密并运行
  LastError = E_Dec_6(E_Hkey, E_Lkey, InBuf, pointer(OutArray), KeyPath)
  if LastError != 0 :
    return 0
  #/////////////////////////////////////////////////////////////////////////////////////////////////////

  #定义局部变量
  if( a ):
    temp_a = c_ubyte(1);
  else:
    temp_a = c_ubyte(0);

  if (b ):
      temp_b = c_ubyte(1);
  else:
      temp_b = c_ubyte(0);

  c=c_ubyte(randint(0, 255))
  d=c_ubyte(randint(0, 255))
  #这步将a,b变量送到加密锁内部进行与运算,c,d变量忽略。
  temp_a.value= temp_a.value ^ c_ubyte(218).value
  temp_a.value= temp_a.value ^ c_ubyte(temp_b.value).value
  LastError=windll.my3l_ex.CalculateEx_2(pointer(OutArray), byref(temp_a), byref(temp_b), byref(c), byref(d), KeyPath, 16, 2000)

  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_a.value= temp_a.value ^ c_ubyte(c.value).value
  temp_a.value= temp_a.value ^ c_ubyte(d.value).value
  temp_a.value= ((temp_a.value << c_ubyte(1).value) | (temp_a.value >>c_ubyte(7).value))
  temp_a.value= temp_a.value ^ c_ubyte(c.value).value


  if ( LastError!= 0):
    return 0

  #在加密锁运算后的结果返回到变量temp_a中
  return c_bool(temp_a).value;
