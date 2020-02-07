import json


def operator(opt:int, **kwargs):
    adjust_group=kwargs['group']
    params=dict()
    prev_content=dict()
    with open('config\\config.json','r',encoding='utf-8') as f:
        prev_content=json.load(f)
    if opt==0:
        params['twitter_id']=kwargs['twitter_id']
        params['screen_name']=kwargs['screen_name']
        params['want_retweet']=kwargs['want_retweet']
        params['want_comment']=kwargs['want_comment']
        if adjust_group in prev_content:
            #查重
            for follower in prev_content[adjust_group]:
                if follower['twitter_id']==params['twitter_id']:
                    return False
            prev_content[adjust_group].append(params)
        else:
            prev_content[adjust_group]=list()
            prev_content[adjust_group].append(params)
        with open('config\\config.json', 'w', encoding='utf-8') as f:
            json.dump(prev_content, f, indent=1)
        return True
    elif opt==1:#编辑需求
        if adjust_group in prev_content:
            for follower in prev_content[adjust_group]:
                if follower['twitter_id']==kwargs['twitter_id']:
                    if 'adjust_comment' in kwargs:
                        follower['want_comment']=kwargs['adjust_comment']
                    if 'adjust_retweet' in kwargs:
                        follower['want_retweet']=kwargs['adjust_retweet']
                    with open('config\\config.json', 'w', encoding='utf-8') as f:
                        json.dump(prev_content, f, indent=1)
                    return True
        return False
    elif opt==2:#获取所有监听id
        followers=list()
        for group in prev_content:
            for follower in prev_content[group]:
                if not followers.__contains__(follower['twitter_id']):
                    followers.append(follower['twitter_id'])
        return followers
    elif opt==3:#获取所有组
        return list(prev_content.keys())
    elif opt==4:#获取某个用户所有监听组
        watch_groups=list()
        for group in prev_content:
            for follower in prev_content[group]:
                if follower['twitter_id']==kwargs['twitter_id']:
                    watch_groups.append(group)
                    break
        return watch_groups
    elif opt==5:#获取需求
        option=list()
        if adjust_group in prev_content:
            for follower in prev_content[adjust_group]:
                if follower['twitter_id']==kwargs['twitter_id']:
                    option.append(follower['want_retweet'])
                    option.append(follower['want_comment'])
                    break
        return option


def add_tweet_to_log(url:str):
    prev_content=''
    with open('.\\config\\list_of_tweets.json','r') as f:
        prev_content=json.load(f)
    index=prev_content['index']+1
    prev_content[str(index)]=url
    prev_content['index']=index
    with open('.\\config\\list_of_tweets.json','w') as f:
        json.dump(prev_content,f,indent=1)
    return str(index)

def read_tweet_from_log(index:str):
    prev_content = ''
    with open('.\\config\\list_of_tweets.json', 'r') as f:
        prev_content = json.load(f)
    if int(index)>int(prev_content['index']) or int(index)<0:
        return None
    return prev_content[index]


if __name__=='__main__':
    group=input('请输入群号')
    '''twitter_id=input('请输入id')
    screen_name=input('请输入名字')
    want_retweet=int(input('请输入是否需要转推'))
    want_comment=int(input('请输入是否需要评论'))
    #operator(0,group=group,twitter_id=twitter_id,screen_name=screen_name,want_comment=want_comment,want_retweet=want_retweet)
    #operator(1,twitter_id=twitter_id,group=group,adjust_comment=want_comment,adjust_retweet=want_retweet)'''
    print(operator(3,group=group))