import sqlite3,random,re,urllib,hashlib,http

appid = '百度翻译'
secretKey = '百度翻译'
path="C:\\Users\\Administrator\\Desktop\\酷Q Pro\\data\\image\\"

def read(user_name:str)->list:
    db=sqlite3.connect('addon//tw.db')
    cursor=db.cursor()
    cursor.execute("SELECT * FROM 'data' WHERE user_name='"+user_name+"'")
    res=cursor.fetchone()
    db.close()
    return res

def readall(user_name:str)->list:
    db = sqlite3.connect('addon//tw.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM 'data' WHERE user_name='" + user_name + "'")
    res = cursor.fetchall()
    db.close()
    return res

def write(user_name:str,user_id:str,group_id:str,want_retweet:str):
    db=sqlite3.connect('addon//tw.db')
    cursor=db.cursor()
    cursor.execute("INSERT INTO 'data' (user_id,group_id,user_name,want_retweet) VALUES("+user_id+","+group_id+",'"+user_name+"',"+want_retweet+")")
    db.commit()
    db.close()

def remove(user_name:str):
    db = sqlite3.connect('addon//tw.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM 'data' WHERE user_name='" + user_name + "'")
    db.commit()
    db.close()

class CQBOTmessage():
    def __init__(self,msgtype:int,toGroup:int,user_name:str,):
        self.username=user_name
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
        self.contentPic = True
        self.contentPicPath = path + self.user_name + "_contentpic.png"
        self.contentPicUrl = contentPicUrl
        self.coolqContentPicSend = '[CQ:image,file=' + self.user_name + '_contentpic.png]'
    def generateText(self)->str:
        return "原文："+self.rawText+"\n翻译："+self.transText


class CQBOTERRmessage():
    def __init__(self,errmsg:str):
        self.errmsg=errmsg
        self.toGroup=681345620

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
