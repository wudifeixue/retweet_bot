from .tweetListener import listener
from .utils import readall,read,write,CQBOTERRmessage,CQBOTmessage
from selenium import webdriver,common
from nonebot import on_command,CommandSession
from aiocqhttp.exceptions import ActionFailed

import nonebot,time,requests,tweepy

li=listener()
driver=webdriver.Chrome()
bot=nonebot.get_bot()
__c_k__ = 'your costum key'
__c_s__ = 'your custom secret'
__A_T__ = 'your access token'
__A_S__ = 'your access secret'
auth = tweepy.OAuthHandler(__c_k__, __c_s__)
auth.set_access_token(__A_T__, __A_S__)
api = tweepy.API(auth)
hold=list()

@on_command('help',only_to_me=False)
async def helpMsg(session:CommandSession):
    await session.send('stream start 启动bot监听，请勿随意调用，否则会重复发送消息\n'
                       'stream restart 重启监听流，不知道现在能不能成功\n'
                       'tell bot出现问题时调用，可以直接发送消息给管理员\n'
                       'add screen_name;user_id;want_retweet(0或1，0需要，1不需要);want_comment(同上)\n'
                       '管理员为2267980149')

@on_command('tell',only_to_me=False)
async def tellAdmin(session:CommandSession):
    await bot.send_private_msg(user_id=2267980149,message=session.state['msg'])

@tellAdmin.args_parser
async def _(session:CommandSession):
    session.state['msg']=session.current_arg_text


@on_command('add',only_to_me=False)
async def add(session:CommandSession):
    user_name=session.state['user_name']
    user_id=session.state['user_id']
    group=str(session.ctx['group_id'])
    want_retweet=session.state['want_retweet']
    want_comment=session.state['want_comment']
    write(user_name,user_id,group,want_retweet,want_comment)
    await session.send("加入成功")

@add.args_parser
async def _(session:CommandSession):
    try:
        args=session.current_arg_text.split(';')
        session.state['user_name']=args[0]
        session.state['user_id']=args[1]
        session.state['want_retweet']=args[2]
        session.state['want_comment']=args[3]
    except:
        await session.send("参数错误")

@on_command('stream',only_to_me=False)
async def stream(session:CommandSession):
    raw=readall()
    if session.state['pos']=="start":
        s=tweepy.Stream(api.auth,li)
        followList=list()
        for each in raw:
            followList.append(str(each[0]))
        print(followList)
        s.filter(follow=followList,is_async=True)
        hold.append(s)
        await session.send("成功")
    elif session.state['pos']=='restart':
        print(hold)
        for each in hold:
            each.disconnect()
            del each
        s=tweepy.Stream(api.auth,li)
        followList = list()
        for each in raw:
            followList.append(str(each[0]))
        print(followList)
        s.filter(follow=followList,is_async=True)
        hold.append(s)
        await session.send("成功")

@stream.args_parser
async def _(session:CommandSession):
    session.state['pos']=session.current_arg_text

@nonebot.scheduler.scheduled_job('interval',seconds=60)
async def _():
    count=len(li.messageStack)
    if count>6:
        count=6
    while count>0:
        thisMessage=li.messageStack.pop()
        if isinstance(thisMessage,CQBOTERRmessage):
            await bot.send_group_msg(group_id=thisMessage.toGroup,message=thisMessage.errmsg)
        elif isinstance(thisMessage,CQBOTmessage):
            want_retweet=read(thisMessage.user_name)[3]
            want_comment=read(thisMessage.user_name)[4]
            sendText=thisMessage.generateText()
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
        count=count-1
                        
                    
