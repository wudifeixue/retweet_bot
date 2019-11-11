from .tweetListener import listener
from .utils import CQBOTERRmessage,CQBOTmessage,config_operator
from selenium import webdriver,common
from nonebot import on_command,CommandSession,on_request,RequestSession
from aiocqhttp.exceptions import ActionFailed

import nonebot,time,requests,tweepy

li=listener()
driver=webdriver.Chrome()
bot=nonebot.get_bot()
__c_k__ = 'RgIKD6VSZG9H403HzZry13pD5'
__c_s__ = 'kmpttSb4wSoibWxP1QQc0oCekJqyblR9UuvqzyrTzH4XcyA5xP'
__A_T__ = '1166612812510171136-H5lHwqZYR65KzgpAymbueMsDYvFYwr'
__A_S__ = 'DSBKEpYgTSwPUmkHnI4E6nAdm2BxC12YyxkeXPiMMGRvW'
auth = tweepy.OAuthHandler(__c_k__, __c_s__)
auth.set_access_token(__A_T__, __A_S__)
api = tweepy.API(auth)
hold = list()


@on_command('adjust',only_to_me=False)
async def adj(session:CommandSession):
    if session.state['op']=='retweet':
        config_operator(1, user_name=session.state['user_name'], want_retweet=session.state['value'])
    elif session.state['op']=='comment':
        config_operator(2, user_name=session.state['user_name'], want_retweet=session.state['value'])
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
    session.approve()


@on_request('group')
async def _(session:RequestSession):
    session.approve()
    await session.send('#help获取更多信息')
    await bot.send_private_msg(user_id=2267980149,message='加入群聊'+session.ctx['group_id'])


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
    config_operator(0, user_id=session.state['user_id'], user_name=session.state['user_name'],
                    group_id=session.ctx['group_id'], want_retweet=str(session.state['want_retweet']),
                    want_comment=str(session.state['want_comment']))
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
    count=len(li.messageStack)
    if count>6:
        count=6
    while count>0:
        thisMessage=li.messageStack.pop()
        if isinstance(thisMessage,CQBOTERRmessage):
            await bot.send_group_msg(group_id=thisMessage.toGroup, message=thisMessage.errmsg)
            await bot.send_private_msg(user_id=2267980149, message=thisMessage.errmsg)
            for each in hold:
                each.disconnect()
            hold.clear()
            s=tweepy.Stream(api.auth,li)
            followList = config_operator(4)
            s.filter(follow=followList, is_async=True)
            hold.append(s)
            await bot.send_private_msg(user_id=2267980149,message='自动重启成功')
        elif isinstance(thisMessage,CQBOTmessage):
            config=config_operator(5,user_name=thisMessage.user_name).split(';')
            want_retweet = int(config[0])
            want_comment = int(config[1])
            sendText = thisMessage.generateText()
            try:
                driver.get(thisMessage.tweetUrl)
                driver.maximize_window()
                time.sleep(2)
                if thisMessage.msgtype==0 or (thisMessage.msgtype==1 and want_retweet==0):
                    if thisMessage.contentHasPic:
                        try:
                            req=requests.get(thisMessage.contentPicUrl)
                            req.raise_for_status()
                        except:
                            await bot.send_group_msg(group_id=thisMessage.toGroup, message="获取图片资源错误")
                        with open(thisMessage.contentPicPath, 'wb') as f:
                            f.write(req.content)
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=thisMessage.coolqContentPicSend)
                    try:
                        ele=driver.find_element_by_tag_name("article")
                    except common.exceptions.NoSuchElementException:
                        await bot.send_group_msg(group_id=thisMessage.toGroup,message="定位失败")
                        driver.refresh()
                        time.sleep(3)
                        ele=driver.find_element_by_tag_name("article")
                    ele.screenshot(thisMessage.screenshotPath)
                    try:
                        await bot.send_group_msg(group_id=thisMessage.toGroup,message=thisMessage.coolqScreenshotSend)
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=sendText)
                    except ActionFailed as e:
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message="酷Qbug，代码"+str(e.retcode))
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=thisMessage.tweetUrl)
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=sendText)
                
                elif thisMessage.msgtype==2 and want_comment==0:
                    try:
                        ele=driver.find_element_by_tag_name("section")
                        cur = driver.find_element_by_css_selector("section>div>div>div>:nth-last-child(2)")
                    except common.exceptions.NoSuchElementException:
                        await bot.send_group_msg(group_id=thisMessage.toGroup,message="定位失败")
                        driver.refresh()
                        time.sleep(3)
                        ele=driver.find_element_by_css_selector("section")
                        cur = driver.find_element_by_css_selector("section>div>div>div>:nth-last-child(2)")
                    driver.execute_script("window.scrollBy(0,-" + str(cur.size['height']) + ")")
                    ele.screenshot(thisMessage.screenshotPath)
                    try:
                        await bot.send_group_msg(group_id=thisMessage.toGroup,message=thisMessage.coolqScreenshotSend)
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=sendText)
                    except ActionFailed as e:
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message="酷Qbug，代码"+str(e.retcode))
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=thisMessage.tweetUrl)
                        await bot.send_group_msg(group_id=thisMessage.toGroup, message=sendText)
            except Exception as otherexception:
                await bot.send_group_msg(group_id=thisMessage.toGroup,message="出现其他异常："+str(otherexception))
                await bot.send_group_msg(group_id=thisMessage.toGroup, message="出错推特链接"+thisMessage.tweetUrl)
        count = count-1
