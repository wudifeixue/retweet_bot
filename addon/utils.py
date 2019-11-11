import random,re,urllib,hashlib,http,json,os

appid = 'baidu trans appid'
secretKey = 'baidu trans secret'
path = "你的酷Qimage文件夹路径"


def config_operator(operate:int, **kwargs):
    #add user 0;update retweet 1;update comment 2;read group 3;read all id 4;read config 5
    if operate == 0:
        setting_file = 'settings\\' + kwargs['user_name'] + '.json'
        config = {
            'name': kwargs['user_name'],
            'id': kwargs['user_id'],
            'groups': kwargs['group_config']
        }
        if not os.path.exists(setting_file):
            with open(setting_file, 'w') as f:
                json.dump(config, f, indent=1)
            with open('settings\\index.txt', 'r+') as f:
                buf = f.read()
                buf = buf.split(';')
                buf.pop()
                if str(kwargs['user_id']) not in buf:
                    f.write(str(kwargs['user_id']) + ';')
        else:
            with open(setting_file, 'r') as f:
                present = json.load(f)
            print(present['groups'])
            present['groups'].append(config['groups'][0])
            with open(setting_file, 'w') as f:
                json.dump(present, f, indent=1)

    elif operate == 1:
        setting_file = 'settings\\' + kwargs['user_name'] + '.json'
        with open(setting_file,'r') as f:
            buf=json.load(f)
        for each in buf['groups']:
            if each['id']==kwargs['group_id']:
                each['retweet']=kwargs['want_retweet']
        with open(setting_file,'w') as f:
            json.dump(buf, f, indent=1)
    elif operate == 2:
        setting_file = 'settings\\' + kwargs['user_name'] + '.json'
        with open(setting_file, 'r') as f:
            buf = json.load(f)
        for each in buf['groups']:
            if each['id'] == kwargs['group_id']:
                each['comment']=kwargs['want_comment']
        with open(setting_file, 'w') as f:
            json.dump(buf, f, indent=1)
    elif operate == 3:
        setting_file = 'settings\\' + kwargs['user_name'] + '.json'
        with open(setting_file, 'r') as f:
            buf = json.load(f)
            res=list()
            for each in buf['groups']:
                res.append(each['id'])
        return res
    elif operate == 4:
        with open('settings\\index.txt','r') as f:
            buf = f.read()
        buf = buf.split(';')
        buf.pop()
        return buf
    elif operate == 5:
        setting_file = 'settings\\' + kwargs['user_name'] + '.json'
        with open(setting_file, 'r') as f:
            buf = json.load(f)
            for each in buf['groups']:
                if each['id'] == kwargs['group_id']:
                    return each


class CQBOTmessage():
    def __init__(self,msgtype:int,toGroup:list,user_name:str):
        self.user_name=user_name
        self.msgtype=msgtype
        self.toGroup=toGroup

        self.rawText=""
        self.transText=""

        self.screenshotPath = path + self.user_name + ".png"
        self.coolqScreenshotSend = '[CQ:image,file=' + self.user_name + '.png]'

        self.contentHasPic=False
        self.contentPicUrl=""

        self.tweetUrl=""
    def putPic(self,contentPicUrl:str):
        self.contentHasPic = True
        self.contentPicPath = path + self.user_name + "_contentpic.png"
        self.contentPicUrl = contentPicUrl
        self.coolqContentPicSend = '[CQ:image,file=' + self.user_name + '_contentpic.png]'
    def generateText(self)->str:
        return "原文："+self.rawText+"\n翻译："+self.transText


class CQBOTERRmessage():
    def __init__(self,errmsg:str):
        self.errmsg=errmsg


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
        return eb
    finally:
        if httpClient:
            httpClient.close()
