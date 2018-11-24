#!/usr/bin/env python
#coding=utf-8
import string,os

#static unsigned int hashpjw(const void *key, int keySize)
#{
#        unsigned char     *ptr=(unsigned char *)key;
#        unsigned int       val=0;
#        while (keySize--) {
#                int tmp;
#                val = (val << 4) + (*ptr);
#                if ((tmp = (val & 0xf0000000))!=0) {
#                        val = val ^ (tmp >> 24);
#                        val = val ^ tmp;
#                }
#                ptr++;
#        }
#        return val % (PRIME_TBLSIZ-1);
#}

def hashpjw(data):
        i,val=0,0
        for ch in data:
                val= (val << 4) + ord(ch)
                tmp=val & 0xf0000000
                if tmp>0x7fffffff: tmp=tmp-0x100000000
                if tmp!=0:
                        val= val ^ (tmp >> 24)
                        val= val ^ tmp
                val = val & 0xffffffff
                i+=1
        return val % (65536*255-1)

def checkALogData(data):
        if data[:3]!="SN=": return None, data, None
        rawdata, checksum=data.split("CHECKSUM=",1)
        checksum=int(checksum)
        if checksum<0: checksum=0x100000000+checksum
        sum=0
        for line in rawdata.split("\r\n"):
                if line: sum=sum+hashpjw(line+"\r\n")
        sum=sum & 0xFFFFFFFF
#        print "%X - %X"%(sum, checksum)
        if sum==checksum:
                sn,rawdata=rawdata.split("\r\n",1)
                sn=sn[3:]
                return sn, rawdata, sum
        return False, False, False

def checkRecData(data, recSize):
        if data[:3]!="SN=": return None, data, None
        rawdata, checksum=data.split("CHECKSUM=",1)
        checksum=int(checksum)
        if checksum<0: checksum=0x100000000+checksum
        sn, rawdata=rawdata.split("\r\n",1)
        sum=hashpjw(sn+"\r\n")
#        print sn, len(rawdata),len(rawdata)%recSize, checksum
        if len(rawdata)%recSize!=0: return False, False, False        
        for i in range(len(rawdata)/recSize):
                sum=sum+hashpjw(rawdata[i*recSize:(i+1)*recSize])
        sum=sum & 0xFFFFFFFF
#        print "%X - %X"%(sum, checksum)
        if sum==checksum:
                sn=sn[3:]
                return sn, rawdata, sum
        return False, False, False

def testHash():
        s="123\0".ljust(15).replace(" ","\xef")
#        print "Test Hash: ",hashpjw(s)

if __name__=="__main__":
        testHash()
        data=file("g:\\1_attlog.dat", "rb").read()
#        print checkALogData(data)

