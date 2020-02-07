import tweepy
from .utils import MSG,ERRMSG,get_pic

class Listener(tweepy.StreamListener):
    MSGHolder = list()
    followers = ['']

    def on_status(self, status):
        url='https://mobile.twitter.com/'+status.user.screen_name+'/status/'+status.id_str
        msg = MSG(msg_txt=status.text, msg_sender=status.user.id_str, msg_id=status.id_str,msg_url=url)
        if status.user.id_str in self.followers:
            if hasattr(status, 'retweeted_status'):
                print("转推")
                msg.msg_type=2
            elif status.in_reply_to_status_id != None:
                print("评论")
                msg.msg_type=3
            else:
                print("发推")
                msg.msg_type=1
            if hasattr(status, 'extended_entities'):
                pic_urls=list()
                pic_cqcodes=list()
                print(len(status.extended_entities['media']))
                for pic in status.extended_entities['media']:
                    pic_urls.append(pic['media_url_https'])
                pic_cqcodes=get_pic(pic_urls, status.id_str)
                msg.add_pic_info_to_msg(pic_urls,pic_cqcodes)
        self.MSGHolder.append(msg)

    def on_exception(self, exception):
        msg=ERRMSG("致命异常"+str(exception))
        self.MSGHolder.append(msg)
        return True

    def on_disconnect(self, notice):
        msg=ERRMSG("丢失链接:"+str(notice))
        self.MSGHolder.append(msg)
        return True

    def on_error(self, status_code):
        msg=ERRMSG("工口发生:"+str(status_code))
        self.MSGHolder.append(msg)
        return True

    def on_warning(self, notice):
        msg=ERRMSG("服务器警告："+str(notice))
        self.MSGHolder.append(msg)
        return True

    def on_timeout(self):
        msg=ERRMSG("超时")
        self.MSGHolder.append(msg)
        return True