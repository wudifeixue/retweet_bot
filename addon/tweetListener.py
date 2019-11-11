from .utils import CQBOTmessage,trans,CQBOTERRmessage,config_operator
import tweepy


class listener(tweepy.StreamListener):
    this_status=''
    messageStack=list()
    followers=config_operator(4)
    def on_status(self, status):
        self.this_status=str(status)
        url='https://mobile.twitter.com/'+str(status.user.screen_name)+'/status/'+str(status.id_str)
        if status.user.id_str in self.followers:
            rawText = status.text
            transText = trans(rawText)
            toGroup = config_operator(3,user_name=status.user.screen_name)
            print(url)
            if hasattr(status,'retweeted_status'):
                thisMessage = CQBOTmessage(msgtype=1,toGroup=toGroup,user_name=status.user.screen_name)
                if status.retweeted_status.entities.__contains__('media'):
                    thisMessage.putPic(str(status.entities['media'][0]['media_url_https']))
                thisMessage.rawText=rawText
                thisMessage.transText=transText
                thisMessage.tweetUrl=url
                self.messageStack.append(thisMessage)
            elif status.in_reply_to_screen_name!=None:
                thisMessage = CQBOTmessage(msgtype=2, toGroup=toGroup, user_name=status.user.screen_name)
                thisMessage.rawText = rawText
                thisMessage.transText = transText
                thisMessage.tweetUrl = url
                self.messageStack.append(thisMessage)
            else:
                thisMessage = CQBOTmessage(msgtype=0, toGroup=toGroup, user_name=status.user.screen_name)
                if status.entities.__contains__('media'):
                    thisMessage.putPic(str(status.entities['media'][0]['media_url_https']))
                thisMessage.rawText = rawText
                thisMessage.transText = transText
                thisMessage.tweetUrl = url
                self.messageStack.append(thisMessage)

    def on_exception(self, exception):
        thisMessage = CQBOTERRmessage(errmsg="发生致命异常："+str(exception))
        self.messageStack.append(thisMessage)
        with open('err.txt','a') as f:
            f.write(self.this_status+'\n')
        return True

    def on_disconnect(self, notice):
        thisMessage = CQBOTERRmessage(errmsg="丢失连接："+str(notice))
        self.messageStack.append(thisMessage)
        return True

    def on_error(self, status_code):
        thisMessage = CQBOTERRmessage(errmsg="工口发生："+str(status_code))
        self.messageStack.append(thisMessage)
        return True

    def on_warning(self, notice):
        thisMessage = CQBOTERRmessage(errmsg="服务器警告："+str(notice))
        self.messageStack.append(thisMessage)
        return True

    def on_timeout(self):
        thisMessage = CQBOTERRmessage(errmsg="不知为何超时了")
        self.messageStack.append(thisMessage)
        return True
