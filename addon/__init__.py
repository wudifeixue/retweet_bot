from .listener import Listener
from .json_operator import operator,add_tweet_to_log,read_tweet_from_log
from splinter import Browser
from nonebot import on_command,CommandSession,on_request,RequestSession
from aiocqhttp.exceptions import ActionFailed
from .utils import ERRMSG,MSG

import nonebot,time,tweepy


watch_dog=Listener()
bot=nonebot.get_bot()
browser=Browser('chrome',executable_path='.\\chromedriver.exe',headless=True)

__c_k__ = 'your custom key'
__c_s__ = 'your custom secret'
__A_T__ = 'your access token'
__A_S__ = 'your access secret'
auth = tweepy.OAuthHandler(__c_k__, __c_s__)
auth.set_access_token(__A_T__, __A_S__)
api = tweepy.API(auth)
hold = list()

@on_command('adjust',only_to_me=False)
async def adj(session:CommandSession):
    res=operator(1,group=session.ctx['group_id'],adjust_retweet=session.state['op'][0],adjust_comment=session.state['op'][1])
    if res:
        await session.send('成功')
    else:
        await session.send('出错啦')

@adj.args_parser
async def _(session:CommandSession):
    session.state['op']=session.current_arg_text.split(';')

@on_request('friend')
async def _(session:RequestSession):
    await session.approve()

@on_request('group')
async def _(session:RequestSession):
    await session.approve()
    await session.send('#帮助 获取更多信息')
    await bot.send_private_msg(user_id=2267980149, message='加入群聊' + str(session.ctx['group_id']))

@on_command('help',only_to_me=False)
async def helpMsg(session:CommandSession):
    with open('help.txt','r',encoding='utf-8') as f:
        msg=f.read()
    await session.send(msg)

@on_command('tell',only_to_me=False)
async def tellAdmin(session:CommandSession):
    await bot.send_private_msg(user_id=2267980149,message=session.state['msg'])

@tellAdmin.args_parser
async def _(session:CommandSession):
    session.state['msg']=session.current_arg_text

@on_command('add',only_to_me=False)
async def add(session:CommandSession):
    res=operator(0,group=session.ctx['group_id'],twitter_id=session.state['twitter_id'],
             screen_name=session.state['screen_name'],want_comment=session.state['want_comment'],
             want_retweet=session.state['want_retweet'])
    if res:
        await session.send('成功')
    else:
        await session.send('出错啦')

@add.args_parser
async def _(session:CommandSession):
    try:
        args=session.current_arg_text.split(';')
        session.state['twitter_id']=args[0]
        session.state['screen_name']=args[1]
        session.state['want_retweet']=args[2]
        session.state['want_comment']=args[3]
    except:
        await session.send("参数错误")

@on_command('stream',only_to_me=False)
async def stream(session:CommandSession):
    followers=operator(2,group=session.ctx['group_id'])
    print(followers)
    if session.state['pos'] == "start":
        s = tweepy.Stream(api.auth, watch_dog)
        s.filter(follow=followers, is_async=True)
        hold.append(s)
        await session.send("成功")
    elif session.state['pos'] == 'restart':
        for each in hold:
            each.disconnect()
        hold.clear()
        s = tweepy.Stream(api.auth, watch_dog)
        s.filter(follow=followers, is_async=True)
        hold.append(s)
        await session.send("成功")

@stream.args_parser
async def _(session:CommandSession):
    session.state['pos']=session.current_arg_text

@on_command('announce',only_to_me=False)
async def announce(session:CommandSession):
    group_list=operator(3,group='')
    for each in group_list:
        try:
            await bot.send_group_msg(group_id=each,message=session.current_arg_text)
        except ActionFailed as e:
            print('发送失败')
            pass
        continue

@on_command('add_trans',only_to_me=False)
async def add_trans(session:CommandSession):
    trans = session.state['trans_txt']
    buf = trans.split('\n')
    trans=''
    for each in buf:
        trans=trans+each+'&&'
    index = session.state['index']
    url = read_tweet_from_log(index)
    if url != None:
        browser.visit(url)
        cmd = 'var target=document.getElementsByTagName("article")[0].childNodes[0];'
        cmd += 'var text_holder=document.createElement("div");'
        cmd += 'var text=document.createElement("p");'
        cmd += 'text.innerText="' + buf + r'".replace(/&&/g,"\n");text_holder.append(text);'
        cmd += 'text.style.fontSize="25px";'
        cmd += 'target.insertBefore(text_holder,target.childNodes[3]);'
        print(cmd)
        time.sleep(2)
        browser.execute_script(cmd)
        file_name = browser.find_by_tag("article").first.screenshot(name="C:/Users/Administrator/Desktop/RTBOT/cache/",
                                                                    full=True)
        cq_sreenshot = '[CQ:image,file=file:///' + file_name + ']'
        await session.send(cq_sreenshot)
    else:
        await session.send('不存在该编号')

@add_trans.args_parser
async def _(session:CommandSession):
    if session.is_first_run:
        session.state['index']=session.current_arg_text
        session.get('trans_txt',prompt='请输入翻译文本')
    else:
        session.state['trans_txt']=session.current_arg_text

@nonebot.scheduler.scheduled_job('interval', seconds=60)
async def _():
    count=len(watch_dog.MSGHolder)
    if count > 6:
        count = 6
    while count > 0:
        msg=watch_dog.MSGHolder.pop()
        if isinstance(msg,ERRMSG):
            await bot.send_private_msg(user_id=2267980149, message=msg.txt)
            for each in hold:
                each.disconnect()
            hold.clear()
            s = tweepy.Stream(api.auth, watch_dog)
            followList = operator(2,group="")
            s.filter(follow=followList, is_async=True)
            hold.append(s)
            await bot.send_private_msg(user_id=2267980149, message='自动重启成功')
        elif isinstance(msg,MSG):
            browser.visit(msg.msg_url)
            time.sleep(2)
            watch_groups=operator(4,group='',twitter_id=msg.msg_sender)
            to_send_msg = '原文：' + msg.msg_txt + '\n' + '翻译：' + msg.msg_txt_translated+'\n'
            screenshot=''
            if msg.msg_type==2:#转推
                for each in watch_groups:
                    options=operator(5,group=each,twitter_id=msg.msg_sender)
                    if options[0]=="1":
                        watch_groups.remove(each)
                screenshot = browser.find_by_tag('article').first.screenshot(
                name='C:\\Users\\Administrator\\Desktop\\RTBOT\\cache\\', full=True)
            elif msg.msg_type==3:#评论
                for each in watch_groups:
                    options=operator(5,group=each,twitter_id=msg.msg_sender)
                    if options[1]=="1":
                        watch_groups.remove(each)
                screenshot = browser.find_by_tag('section').first.screenshot(
                name='C:\\Users\\Administrator\\Desktop\\RTBOT\\cache\\', full=True)
            elif msg.msg_type==1:
                screenshot = browser.find_by_tag('article').first.screenshot(
                name='C:\\Users\\Administrator\\Desktop\\RTBOT\\cache\\', full=True)
            if len(watch_groups)!=0:
                if msg.msg_has_pic:
                    to_send_msg+='附件：'
                    for each in msg.pic_cqcode:
                        to_send_msg+=each

                cq_sreenshot='[CQ:image,file=file:///'+screenshot+']'
                to_send_msg+='\n嵌字编号:'+add_tweet_to_log(msg.msg_url)
                for each in watch_groups:
                    try:
                        await bot.send_group_msg(group_id=each,message=cq_sreenshot)
                        await bot.send_group_msg(group_id=each,message=to_send_msg)
                    except ActionFailed as e:
                        for each in watch_groups:
                            await bot.send_group_msg(group_id=each, message="酷Qbug，代码" + str(e.retcode))
                            await bot.send_group_msg(group_id=each, message=msg.msg_url)
        count-=1