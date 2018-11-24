#!/usr/bin/env python
#coding=utf-8
import urllib
import datetime
import os
from sgmllib import SGMLParser
from django.conf import settings
from mysite.iclock.models import iclock, devcmds
from dbapp.utils import errorLog
from mysite.iclock.dataprocaction import append_dev_cmd

citys = {
    u"北京": u"54511",
    u"上海": u"58367",
    u"天津": u"54517",
    u"重庆": u"57516",
    u"香港": u"45005",
    u"澳门": u"45011",
    u"哈尔滨": u"50953",
    u"齐齐哈尔": u"50745",
    u"牡丹江": u"54094",
    u"大庆": u"50842",
    u"伊春": u"50774",
    u"双鸭山": u"50884",
    u"鹤岗": u"50775",
    u"鸡西": u"50978",
    u"佳木斯": u"50873",
    u"七台河": u"50971",
    u"黑河": u"50468",
    u"绥化": u"50853",
    u"大兴安岭": u"50442",
    u"长春": u"54161",
    u"延边": u"99999",
    u"吉林": u"54172",
    u"白山": u"54371",
    u"白城": u"50936",
    u"四平": u"54157",
    u"松原": u"50946",
    u"辽源": u"54260",
    u"大安": u"50945",
    u"通化": u"54363",
    u"沈阳": u"54342",
    u"大连": u"54662",
    u"葫芦岛": u"54453",
    u"旅顺": u"54660",
    u"本溪": u"54346",
    u"抚顺": u"54353",
    u"铁岭": u"54249",
    u"辽阳": u"54347",
    u"营口": u"54471",
    u"阜新": u"54237",
    u"朝阳": u"54324",
    u"锦州": u"54337",
    u"丹东": u"54497",
    u"鞍山": u"54339",
    u"呼和浩特": u"53463",
    u"呼伦贝尔": u"99999",
    u"包头": u"53446",
    u"赤峰": u"54218",
    u"海拉尔": u"50527",
    u"乌海": u"53512",
    u"鄂尔多斯": u"53543",
    u"锡林浩特": u"54102",
    u"通辽": u"54135",
    u"石家庄": u"53698",
    u"唐山": u"54534",
    u"张家口": u"54401",
    u"廊坊": u"54515",
    u"邢台": u"53798",
    u"邯郸": u"53892",
    u"沧州": u"54616",
    u"衡水": u"54702",
    u"承德": u"54423",
    u"保定": u"54602",
    u"秦皇岛": u"54449",
    u"郑州": u"57083",
    u"开封": u"57091",
    u"洛阳": u"57073",
    u"平顶山": u"57171",
    u"焦作": u"53982",
    u"鹤壁": u"53990",
    u"新乡": u"53986",
    u"安阳": u"53898",
    u"濮阳": u"54900",
    u"许昌": u"57089",
    u"漯河": u"57186",
    u"三门峡": u"57051",
    u"南阳": u"57178",
    u"商丘": u"58005",
    u"信阳": u"57297",
    u"周口": u"57195",
    u"驻马店": u"57290",
    u"济南": u"54823",
    u"青岛": u"54857",
    u"淄博": u"54830",
    u"威海": u"54774",
    u"曲阜": u"54918",
    u"临沂": u"54938",
    u"烟台": u"54765",
    u"枣庄": u"58024",
    u"聊城": u"54806",
    u"济宁": u"54915",
    u"菏泽": u"54906",
    u"泰安": u"54827",
    u"日照": u"54945",
    u"东营": u"54736",
    u"德州": u"54714",
    u"滨州": u"54734",
    u"莱芜": u"54828",
    u"潍坊": u"54843",
    u"太原": u"53772",
    u"阳泉": u"53782",
    u"晋城": u"53976",
    u"晋中": u"53778",
    u"临汾": u"53868",
    u"运城": u"53959",
    u"长治": u"53882",
    u"朔州": u"53578",
    u"忻州": u"53674",
    u"大同": u"53487",
    u"南京": u"58238",
    u"苏州": u"58357",
    u"昆山": u"58356",
    u"南通": u"58259",
    u"太仓": u"58377",
    u"吴县": u"58349",
    u"徐州": u"58027",
    u"宜兴": u"58346",
    u"镇江": u"58248",
    u"淮安": u"58145",
    u"常熟": u"58352",
    u"盐城": u"58151",
    u"泰州": u"58246",
    u"无锡": u"58354",
    u"连云港": u"58044",
    u"扬州": u"58245",
    u"常州": u"58343",
    u"宿迁": u"58131",
    u"合肥": u"58321",
    u"巢湖": u"58326",
    u"蚌埠": u"58221",
    u"安庆": u"58424",
    u"六安": u"58311",
    u"滁州": u"58236",
    u"马鞍山": u"58336",
    u"阜阳": u"58203",
    u"宣城": u"58433",
    u"铜陵": u"58429",
    u"淮北": u"58116",
    u"芜湖": u"58334",
    u"毫州": u"99999",
    u"宿州": u"58122",
    u"淮南": u"58224",
    u"池州": u"58427",
    u"西安": u"57036",
    u"韩城": u"53955",
    u"安康": u"57245",
    u"汉中": u"57127",
    u"宝鸡": u"57016",
    u"咸阳": u"57048",
    u"榆林": u"53646",
    u"渭南": u"57045",
    u"商洛": u"57143",
    u"铜川": u"53947",
    u"延安": u"53845",
    u"银川": u"53614",
    u"固原": u"53817",
    u"中卫": u"53704",
    u"石嘴山": u"53518",
    u"吴忠": u"53612",
    u"兰州": u"52889",
    u"白银": u"52896",
    u"庆阳": u"53829",
    u"酒泉": u"52533",
    u"天水": u"57006",
    u"武威": u"52679",
    u"张掖": u"52652",
    u"甘南": u"50741",
    u"临夏": u"52984",
    u"平凉": u"53915",
    u"定西": u"52995",
    u"金昌": u"52675",
    u"西宁": u"52866",
    u"海北": u"52754",
    u"海西": u"52737",
    u"黄南": u"56065",
    u"果洛": u"56043",
    u"玉树": u"56029",
    u"海东": u"52875",
    u"海南": u"52856",
    u"武汉": u"57494",
    u"宜昌": u"57461",
    u"黄冈": u"57498",
    u"恩施": u"57447",
    u"荆州": u"57476",
    u"神农架": u"57362",
    u"十堰": u"57256",
    u"咸宁": u"57590",
    u"襄樊": u"57278",
    u"孝感": u"57482",
    u"随州": u"57381",
    u"黄石": u"58407",
    u"荆门": u"57377",
    u"鄂州": u"57496",
    u"长沙": u"57687",
    u"邵阳": u"57766",
    u"常德": u"57662",
    u"郴州": u"57972",
    u"吉首": u"57649",
    u"株洲": u"57780",
    u"娄底": u"57763",
    u"湘潭": u"57773",
    u"益阳": u"99999",
    u"永州": u"57866",
    u"岳阳": u"57584",
    u"衡阳": u"57872",
    u"怀化": u"57749",
    u"韶山": u"57771",
    u"张家界": u"57558",
    u"杭州": u"58457",
    u"湖州": u"58450",
    u"金华": u"58549",
    u"宁波": u"58563",
    u"丽水": u"58646",
    u"绍兴": u"58453",
    u"雁荡山": u"99999",
    u"衢州": u"58633",
    u"嘉兴": u"58452",
    u"台州": u"58660",
    u"舟山": u"58477",
    u"温州": u"58659",
    u"南昌": u"58606",
    u"萍乡": u"57786",
    u"九江": u"58502",
    u"上饶": u"58637",
    u"抚州": u"58617",
    u"吉安": u"57799",
    u"鹰潭": u"58627",
    u"宜春": u"57793",
    u"新余": u"57796",
    u"景德镇": u"58527",
    u"赣州": u"57993",
    u"福州": u"58847",
    u"厦门": u"59134",
    u"龙岩": u"58927",
    u"南平": u"58834",
    u"宁德": u"58846",
    u"莆田": u"58946",
    u"泉州": u"59137",
    u"三明": u"58828",
    u"漳州": u"59126",
    u"贵阳": u"57816",
    u"安顺": u"57806",
    u"赤水": u"57609",
    u"遵义": u"57713",
    u"铜仁": u"57741",
    u"六盘水": u"56693",
    u"毕节": u"57707",
    u"凯里": u"57825",
    u"都匀": u"57827",
    u"成都": u"56294",
    u"泸州": u"57602",
    u"内江": u"57504",
    u"凉山": u"56571",
    u"阿坝": u"56171",
    u"巴中": u"57313",
    u"广元": u"57206",
    u"乐山": u"56386",
    u"绵阳": u"56196",
    u"德阳": u"56198",
    u"攀枝花": u"56666",
    u"雅安 ": u"56287",
    u"宜宾": u"56492",
    u"自贡": u"56396",
    u"甘孜州": u"56146",
    u"达州": u"57328",
    u"资阳": u"56298",
    u"广安": u"57415",
    u"遂宁": u"57405",
    u"眉山": u"56391",
    u"南充": u"57411",
    u"广州": u"59287",
    u"深圳": u"59493",
    u"潮州": u"59312",
    u"韶关": u"59082",
    u"湛江": u"59658",
    u"惠州": u"59298",
    u"清远": u"59280",
    u"东莞": u"59289",
    u"江门": u"59473",
    u"茂名": u"59659",
    u"肇庆": u"59278",
    u"汕尾 ": u"59501",
    u"河源": u"59293",
    u"揭阳": u"59315",
    u"梅州": u"59117",
    u"中山": u"59485",
    u"德庆": u"59269",
    u"阳江": u"59663",
    u"云浮": u"59471",
    u"珠海": u"59488",
    u"汕头": u"59316",
    u"佛山": u"59279",
    u"南宁": u"59432",
    u"桂林": u"57957",
    u"阳朔": u"59051",
    u"柳州": u"59046",
    u"梧州": u"59265",
    u"玉林": u"59453",
    u"桂平": u"59254",
    u"贺州": u"59065",
    u"钦州": u"59632",
    u"贵港": u"59249",
    u"防城港": u"59635",
    u"百色": u"59211",
    u"北海": u"59644",
    u"河池": u"59023",
    u"来宾": u"59242",
    u"崇左": u"59425",
    u"昆明": u"56778",
    u"保山": u"56748",
    u"楚雄": u"56768",
    u"德宏": u"56844",
    u"红河": u"56975",
    u"临沧": u"56951",
    u"怒江": u"56533",
    u"曲靖": u"56783",
    u"思茅": u"56964",
    u"文山": u"56994",
    u"玉溪": u"56875",
    u"昭通": u"56586",
    u"丽江": u"56651",
    u"大理": u"56751",
    u"海口": u"59758",
    u"三亚": u"59948",
    u"儋州": u"59845",
    u"琼山": u"59757",
    u"通什": u"59941",
    u"文昌": u"59856",
    u"乌鲁木齐": u"51463",
    u"阿勒泰": u"51076",
    u"阿克苏": u"51628",
    u"昌吉": u"51368",
    u"哈密": u"52203",
    u"和田": u"51828",
    u"喀什": u"51709",
    u"克拉玛依": u"51243",
    u"石河子": u"51356",
    u"塔城": u"51133",
    u"库尔勒": u"51656",
    u"吐鲁番": u"51573",
    u"伊宁": u"51431",
    u"拉萨": u"55591",
    u"阿里": u"55437",
    u"昌都": u"56137",
    u"那曲": u"55299",
    u"日喀则": u"55578",
    u"山南": u"55598",
    u"林芝": u"56312",
    u"台北": u"58968",
    u"高雄": u"59554",
}

class WeatherStation(SGMLParser):
        def __init__(self, url): 
                SGMLParser.__init__(self)
                self._is_weather, self._is_td  = False, False
                self._page_datas, self._weather = None, []        # 网页数据，天气数据
                self._get_page_datas(url)
                self.feed(self._page_datas)
                
        def _get_page_datas(self, url): # 抓取网页数据
                sock = urllib.urlopen(url) 
                lines = sock.read().split("\n")
                sock.close()                
                lines1=[]
                for line in lines: #一行一行转换，避免一行出错影响全部
                        try:
                                l=line.decode("GB18030")
                                lines1.append(l)
                        except: 
                                pass
                self._page_datas=u"\n".join(lines1)
                
        def start_td(self, attrs):
                self._is_td = True
                
        def end_td(self):
                self._is_td = False
        
        def handle_data(self, text):
                text = self._process_data(text)                
                if  text and self._is_weather:
                        self._weather.append(text)            
                if "时间".decode("utf-8") in text:
                        self._is_weather = True                
                if "指数查询".decode("utf-8") in text:
                        self._is_weather = False
        
        def show(self):
                if len(self._weather) > 16:
                        return self._weather[:12] + self._formatWinds(self._weather[12:])
                return self._weather
        
        def _formatWinds(self, li): # 风力/风向格式不规整
                s = "\n".join(li)
                s = s.replace("\n<\n", "<")
                return s.split("\n")
        
        def _process_data(self, text):        # 清理冗余数据
                text = self._cut_words(text, ['\n', '\r', '\t', ' '])                
                return text
        
        def _cut_words(self, text, words):  # 清理指定字符
                if type(words) == type([]):
                        for row in words:
                                while row in text:                                        
                                        pos = text.index(row)
                                        text = text[:pos] + text[(pos+1):]
                elif words is not None:                        
                        while words in text:
                                pos = text.index(words)
                                text = text[:pos] + text[(pos+1):]                        
                return text
                        
WeatherDB = settings.ADDITION_FILE_ROOT + "weather/"

def getWeather(area):
#        print "getWeather", area, 
        if area is None: return None
        try:
                areaID=citys[area]
        except Exception, e:
                try:
                        areaID=citys[area.decode("GBK")]
                except Exception, e:
                        areaID=area
        WeatherDir = WeatherDB + areaID
        today = (str(datetime.datetime.now())[:10]).replace("-", "")
        WeatherFile = WeatherDir + "/" + today + ".txt"
        if not os.path.isfile(WeatherFile): # 下载天气预报
                url = "http://www.nmc.gov.cn/weatherdetail/%s.html" % (areaID,)        
                try:
                        lister = WeatherStation(url)
                        datas = lister.show()[:16]
                except Exception, e:
                        errorLog()
                        datas = None                
                try:
                        if datas and (len(datas) == 16):
                                s="%s\t%s\t%s\t%s\n%s\t%s\t%s\t%s\n%s\t%s\t%s\t%s\n" % (datas[0], datas[4], datas[8], datas[12], 
                                                datas[1], datas[5], datas[9], datas[13],
                                                datas[2], datas[6], datas[10], datas[14])
                                if not os.path.isdir(WeatherDir):
                                        os.makedirs(WeatherDir)    
                                open(WeatherFile, "w+").write(s.encode("utf-8"))
                                return s.split("\n")
                except Exception, e:
                        errorLog()
        try:
                datas = open(WeatherFile, "r").read().decode("utf-8").split("\n")
        except:
                datas= [u"NULL\n"]
        return datas

def getWeatherCmd(device, wData):
        tft=device.is_tft()
        delta=datetime.datetime.now()-datetime.timedelta(0,3*60*60)  #3小时前
        if devcmds.objects.filter(CmdContent__startswith=tft and "WEATHER MSG=" or "SMS TYPE=IDLELCD", SN=device, 
                CmdCommitTime__gt=delta).count()>0: return None
        if tft:
                return getWeatherCmdTFT(wData)
        return getWeatherCmdMono(wData)

WEATHER_PIC_INDEX={
        u"晴":"w1.gif",
        u"晴间多云":"w2.gif",
        u"晴转多云":"w3.gif",
        u"多云转阴":"w4.gif",
        u"小雨":"w5.gif",
        u"中雨":"w6.gif",
        u"大雨":"w7.gif",
#        u"":"w8.gif",
#        u"":"w9.gif",
#        u"":"w10.gif",
        u"阵雨":"w11.gif",
#        u"":"w12.gif",
#        u"":"w13.gif",
#        u"":"w14.gif",
#        u"":"w15.gif",
#        u"":"w16.gif",
#        u"":"w17.gif",
#        u"":"w18.gif",
#        u"":"w19.gif",
#        u"":"w20.gif",
#        u"":"w21.gif",
#        u"":"w22.gif",
#        u"":"w23.gif",
#        u"":"w24.gif",
#        u"":"w25.gif",
}


def getWeatherCmdTFT(wData):
        wd=[]
        for d in wData:
                ds=d.split("\t")
                if len(ds)>2:
                        try:
                                dpic=WEATHER_PIC_INDEX[ds[1]]
                        except:
                                dpic="w1.gif"
                        ds.append(dpic)
                        wd.append("\t".join(ds))
        return u"WEATHER MSG="+(u"\\n".join(wd))

def getWeatherCmdMono(wData):
        today_weather = formatWeather4iClock(wData[0]) 
        tomorrow_weather = formatWeather4iClock(wData[1])
        if today_weather is None or tomorrow_weather is None: return None                
        ss = today_weather + " " * 16 + tomorrow_weather
        return u"SMS TYPE=IDLELCD\tMSG=%s" % (ss)


def checkWeatherForDev(device):
        areaID=device.City
        if not areaID: return None
        datas=getWeather(areaID)
        if datas and (u"NULL\n" not in datas):
                cmd=getWeatherCmd(device, datas)
                if cmd:        
                        return append_dev_cmd(device, cmd)
        return datas

def formatWeather4iClock(u8):
        u = u8 #.decode("utf-8")
        if u[-1] == '\n': u = u[:-1]
        arr = u.split("\t")        
        ret = ""
        for row in arr:
                ret += gb_16(row)
        return ret

def gb_16(s):
        size = len(s.encode("gb2312"))
        count = (size+15) / 16 * 16 - size        
        return s + " " * count


def index(request):
        from django.http import HttpResponse
        device = Device.objects.all().filter(SN="888888")[0]
        if get_Weather(device.Address.split("=")[1], device) is None:
                return HttpResponse("False")
        return HttpResponse("True")
