import requests
import random,re,urllib,hashlib,http

appid = 'baidu translation app id'
secretKey = 'baidu translation secret key'

class MSG:
    #1,发推
    #2,转推
    #3,评论
    msg_type=0
    msg_url=''
    msg_txt=''
    msg_txt_translated=''
    msg_sender=''
    msg_id=''
    msg_has_pic=False
    def __init__(self,msg_txt:str,msg_sender:str,msg_id:str,msg_url:str):
        self.msg_txt=msg_txt
        self.msg_txt_translated=trans(msg_txt)
        self.msg_sender=msg_sender
        self.msg_id=msg_id
        self.msg_url=msg_url
    def add_pic_info_to_msg(self,pic_url:list,pic_cqcode:list):
        self.msg_has_pic=True
        self.pic_url=pic_url
        self.pic_cqcode=pic_cqcode


class ERRMSG:
    txt=''

    def __init__(self,txt:str):
        self.txt=txt


def get_pic(urls:list,prefix:str):
    count=0
    cqcodes=list()
    for url in urls:
        pic=requests.get(url)
        suffix=str(url).split('.').pop()
        if count==0:
            p=open('cache\\'+prefix+'_'+str(count)+suffix,'w')
        with open('cache\\'+prefix+'_'+str(count)+suffix,'wb') as f:
            f.write(pic.content)
            cqcodes.append('[CQ:image,file=file:///C:\\Users\\Administrator\\Desktop\\RTBOT\\'+'cache\\'+prefix+'_'+str(count)+suffix+']')
        count+=1
    return cqcodes


def trans(transstr:str):
    httpClient = None
    myurl = '/api/trans/vip/translate'
    qaa = str(transstr)
    qaa = qaa.replace('\n', '')
    fromLang = 'auto'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = str(appid) + qaa + str(salt) + str(secretKey)
    m1 = hashlib.md5()
    m2 = sign.encode(encoding='utf-8')
    m1.update(m2)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        qaa) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        response = httpClient.getresponse()
        resp = str(response.read())
        resu = str(re.findall('"dst":"(.+?)"', resp)[0])
        resul = resu.encode('utf-8').decode('unicode_escape')
        resultr = resul.encode('utf-8').decode('unicode_escape')
        result = resultr.replace(r'\/', r'/')
        return result
    except Exception as eb:
        return '翻译api超速，获取失败'
    finally:
        if httpClient:
            httpClient.close()