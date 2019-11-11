from .tweetListener import listener
from .utils import CQBOTERRmessage,CQBOTmessage,config_operator
from selenium import webdriver,common
from nonebot import on_command,CommandSession,on_request,RequestSession
from aiocqhttp.exceptions import ActionFailed

import nonebot,time,requests,tweepy

li=listener()
driver=webdriver.Chrome()
bot=nonebot.get_bot()
__c_k__ = 'your twitter app custom key'
__c_s__ = 'your twitter app custom secret'
__A_T__ = 'your twitter app access token'
__A_S__ = 'your twitter app access secret'
auth = tweepy.OAuthHandler(__c_k__, __c_s__)
auth.set_access_token(__A_T__, __A_S__)
api = tweepy.API(auth)
hold = list()


@on_command('adjust',only_to_me=False)
async def adj(session:CommandSession):
    if session.state['op']=='retweet':
        config_operator(1, user_name=session.state['user_name'], want_retweet=session.state['value'],
                        group_id=str(session.ctx['group_id']))
    elif session.state['op']=='comment':
        config_operator(2, user_name=session.state['user_name'], want_comment=session.state['value'],
                        group_id=str(session.ctx['group_id']))
    await session.send('成功')


@adj.args_parser
async def _(session:CommandSession):
    raw=session.current_arg_text
    buf=raw.split(';')
    session.state['op']=buf[0]
    session.state['user_name']=buf[1]
    session.state['value']=buf[2]


@on_request('friend')
async def _(session:RequestSession):
    await session.approve()


@on_request('group')
async def _(session:RequestSession):
    await session.approve()
    await session.send('#help获取更多信息')
    await bot.send_private_msg(user_id=2267980149,message='加入群聊'+str(session.ctx['group_id']))


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
    group_config=list()
    group_config.append({
        'id': str(session.ctx['group_id']),
        'retweet': session.state['want_retweet'],
        'comment': session.state['want_comment']
    })
    config_operator(0, user_id=session.state['user_id'], user_name=session.state['user_name'],
                    group_config=group_config)
    await session.send("加入成功")


@add.args_parser
async def _(session:CommandSession):
    try:
        args=session.current_arg_text.split(';')
        session.state['user_id']=args[0]
        session.state['user_name']=args[1]
        session.state['want_retweet']=args[2]
        session.state['want_comment']=args[3]
    except:
        await session.send("参数错误")


@on_command('stream',only_to_me=False)
async def stream(session:CommandSession):
    followList=config_operator(4)
    print(followList)
    if session.state['pos']=="start":
        s=tweepy.Stream(api.auth,li)
        s.filter(follow=followList,is_async=True)
        hold.append(s)
        await session.send("成功")
    elif session.state['pos']=='restart':
        for each in hold:
            each.disconnect()
        hold.clear()
        s=tweepy.Stream(api.auth,li)
        s.filter(follow=followList,is_async=True)
        hold.append(s)
        await session.send("成功")


@stream.args_parser
async def _(session:CommandSession):
    session.state['pos']=session.current_arg_text


@nonebot.scheduler.scheduled_job('interval', seconds=60)
async def _():
    count = len(li.messageStack)
    if count > 6:
        count = 6
    while count > 0:
        thisMessage = li.messageStack.pop()
        if isinstance(thisMessage, CQBOTERRmessage):
            await bot.send_private_msg(user_id=2267980149, message=thisMessage.errmsg)
            for each in hold:
                each.disconnect()
            hold.clear()
            s = tweepy.Stream(api.auth, li)
            followList = config_operator(4)
            s.filter(follow=followList, is_async=True)
            hold.append(s)
            await bot.send_private_msg(user_id=2267980149, message='自动重启成功')
        elif isinstance(thisMessage, CQBOTmessage):
            try:
                driver.get(thisMessage.tweetUrl)
                driver.maximize_window()
                time.sleep(2)
                need_retweet_group=list()
                need_comment_group=list()
                sendtext=thisMessage.generateText()
                if thisMessage.msgtype==1:
                    for each in thisMessage.toGroup:
                        config=config_operator(5,user_name=thisMessage.user_name,
                                               group_id=each)
                        if config['retweet']=='0':
                            need_retweet_group.append(config['id'])
                    if len(need_retweet_group)>0:
                        if thisMessage.contentHasPic:
                            try:
                                req = requests.get(thisMessage.contentPicUrl)
                                req.raise_for_status()
                            except:
                                await send_to_all_group(need_retweet_group, "获取图片资源错误")
                            with open(thisMessage.contentPicPath, 'wb') as f:
                                f.write(req.content)
                            await send_to_all_group(need_retweet_group, thisMessage.coolqContentPicSend)
                        try:
                            ele = driver.find_element_by_tag_name("article")
                        except common.exceptions.NoSuchElementException:
                            await send_to_all_group(need_retweet_group, '定位失败')
                            driver.refresh()
                            time.sleep(2)
                            ele = driver.find_element_by_tag_name("article")
                        ele.screenshot(thisMessage.screenshotPath)
                        try:
                            await send_to_all_group(need_retweet_group, thisMessage.coolqScreenshotSend)
                            await send_to_all_group(need_retweet_group, sendtext)
                        except ActionFailed as e:
                            await send_to_all_group(need_retweet_group, '酷Q bug，代码'+str(e.retcode))
                            await send_to_all_group(need_retweet_group, thisMessage.tweetUrl)
                            await send_to_all_group(need_retweet_group, sendtext)
                elif thisMessage.msgtype == 0:
                    if thisMessage.contentHasPic:
                        try:
                            req = requests.get(thisMessage.contentPicUrl)
                            req.raise_for_status()
                        except:
                            await send_to_all_group(thisMessage.toGroup, "获取图片资源错误")
                        with open(thisMessage.contentPicPath, 'wb') as f:
                            f.write(req.content)
                        await send_to_all_group(thisMessage.toGroup, thisMessage.coolqContentPicSend)
                    try:
                        ele = driver.find_element_by_tag_name("article")
                    except common.exceptions.NoSuchElementException:
                        await send_to_all_group(thisMessage.toGroup, '定位失败')
                        driver.refresh()
                        time.sleep(2)
                        ele = driver.find_element_by_tag_name("article")
                    ele.screenshot(thisMessage.screenshotPath)
                    try:
                        await send_to_all_group(thisMessage.toGroup, thisMessage.coolqScreenshotSend)
                        await send_to_all_group(thisMessage.toGroup, sendtext)
                    except ActionFailed as e:
                        await send_to_all_group(thisMessage.toGroup, '酷Q bug，代码' + str(e.retcode))
                        await send_to_all_group(thisMessage.toGroup, thisMessage.tweetUrl)
                        await send_to_all_group(thisMessage.toGroup, sendtext)
                elif thisMessage.msgtype == 2:
                    for each in thisMessage.toGroup:
                        config = config_operator(5, user_name=thisMessage.user_name,
                                                 group_id=each)
                        if config['comment'] == '0':
                            need_comment_group.append(config['id'])
                    if len(need_comment_group)>0:
                        try:
                            ele = driver.find_element_by_tag_name("section")
                            cur = driver.find_element_by_css_selector("section>div>div>div>:nth-last-child(2)")
                        except common.exceptions.NoSuchElementException:
                            await send_to_all_group(need_comment_group, "定位失败")
                            driver.refresh()
                            time.sleep(2)
                            ele = driver.find_element_by_css_selector("section")
                            cur = driver.find_element_by_css_selector("section>div>div>div>:nth-last-child(2)")
                        driver.execute_script("window.scrollBy(0,-" + str(cur.size['height']) + ")")
                        ele.screenshot(thisMessage.screenshotPath)
                        try:
                            await send_to_all_group(need_comment_group, thisMessage.coolqScreenshotSend)
                            await send_to_all_group(need_comment_group, sendtext)
                        except ActionFailed as e:
                            await send_to_all_group(need_comment_group, "酷Qbug，代码" + str(e.retcode))
                            await send_to_all_group(need_comment_group, thisMessage.tweetUrl)
                            await send_to_all_group(need_comment_group, sendtext)
            except Exception as otherexception:
                await send_to_all_group(thisMessage.toGroup, "出现其他异常：" + str(otherexception))
                await send_to_all_group(thisMessage.toGroup, "出错推特链接" + thisMessage.tweetUrl)
        count=count-1


async def send_to_all_group(groups:list,message:str):
    for each in groups:
        await bot.send_group_msg(group_id=each,message=message)
