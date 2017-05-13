# -*- coding: utf-8 -*-
import itchat
from urllib import urlretrieve
import json
from itchat.content import *
from JwLogin import *
import requests
import os
import thread
import sys

global studentNum
studentNum = {}
global password
password = {}
key = 'c065e3df9d884f8c97854b8b19e63926'
global useRobotList
useRobotList = []
global useCheckScoreList
useCheckScoreList = []
global useEvaluateList
useEvaluateList = []
global useSearchImgMap
useSearchImgMap = {}
global useSearchImgIndexDic
useSearchImgIndexDic = {}
global pathList
pathList = []


# 获取机器人回复
def get_response(msg, username):
    api = 'http://www.tuling123.com/openapi/api'
    data = {
        'key': key,
        'info': msg,
        'userid': 'rokuki',
    }
    try:
        res = requests.post(api, data=data).json()
        itchat.send(res.get('text'), toUserName=username)
    except:
        itchat.send(u'嗯', toUserName=username)


# 获取成绩 & 一键评教
def getResult(studentNum, password, action, username):
    global useCheckScoreList
    global useEvaluateList
    if action == 'DO_EVALUATE':
        result = login(studentNum, password, 'DO_EVALUATE', itchat, username)
    elif action == 'GET_SCORE':
        result = login(studentNum, password, 'GET_SCORE', itchat, username)
        itchat.send(u'正在获取成绩', toUserName=username)
    if result == 'TIMEOUT':
        itchat.send(u'教务又挂了，请稍候再试。', toUserName=username)
    elif result == 'UNKNOWN_ERROR':
        itchat.send(u'未知错误，请确认密码正确后选择\n'u'【retry】重新登录\n'u'【exit】退出', toUserName=username)
    else:
        if user in useCheckScoreList:
            useCheckScoreList.remove(user)  # 成功查询后，退出输入状态
        if user in useEvaluateList:
            useEvaluateList.remove(user)
        itchat.send(result, toUserName=username)


def loginJw(msg, action):
    global studentNum
    global password
    global useCheckScoreList
    msg1 = msg.text.encode('UTF-8')
    username = msg['User']['UserName'].encode('UTF-8')

    if password[username] == '' and studentNum[username] != '':
        password[username] = msg1
        itchat.send(u'登录教务中,请稍候...', toUserName=username)
        print 'username:' + studentNum[username]
        print 'password:' + password[username]

        thread.start_new_thread(getResult, (studentNum[username], password[username], action, username, ))

    if studentNum[username] == '':
        if msg1.isdigit() and str(msg1)[0] == '1' and len(str(msg1)) == 8:  # 是否纯数字
            studentNum[username] = msg1
            itchat.send(u'请输入密码（可撤回）：', toUserName=username)
        else:
            itchat.send(u'学号不正确', toUserName=username)


# 获取图片搜索路径
def getImg(keyword, index, username):
    imgUrlList = []
    imgList = []
    global pathList
    pathList = []
    dirs = ('img/' + keyword + '/').decode('UTF-8')
    api = 'http://m.image.so.com/i?a=jsonpview&q=' + keyword + '&count=' + str(index + 1) + '&start=0&multiple=0'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/49.0.2623.110 "
                      "Safari/537.36",
    }
    res = requests.post(api, headers=headers)
    data = res.json()['data']
    for i in data:
        imgUrlList.append(i.get('img_url'))
    if not os.path.exists(dirs) or index >= 1:  # index >=1 ,表示用户提交了next请求
        print u'目录不存在，正在创建' + dirs
        if index == 0:  # 第一次查询，index为0，此时创建目录
            os.makedirs(dirs)
        for i in range(len(imgUrlList)):
            print u'正在下载第' + str(i) + u'张图片'
            imgurl = imgUrlList[i]
            path = dirs + str(i) + imgurl[imgurl.rindex('.'):]
            pathList.append(path)
            if not os.path.exists(path):  # 目录内图片不存在时才下载
                urlretrieve(imgurl, path)
        itchat.send_image(pathList[index], toUserName=username)
    else:
        print u'目录已存在' + dirs
        imgdir = os.listdir(dirs)
        imgdir.sort()
        for filename in imgdir:
            imgList.append(dirs + filename)
        print imgList
        itchat.send_image(imgList[index], toUserName=username)


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    global studentNum
    global password
    global useRobotList
    global useCheckScoreList
    global useEvaluateList
    global useSearchImgMap
    msg1 = msg.text.encode('UTF-8')
    username = msg['User']['UserName'].encode('UTF-8')
    print 'username:' + username
    print 'message:' + msg1
    print 'robotList:' + str(useRobotList)
    print 'useCheckScoreList' + str(useCheckScoreList)
    print 'useSearchImg' + str(useSearchImgMap)

    # 图灵机器人
    if msg1 == 'start':
        useRobotList.append(username)
        # 防止list重复
        useRobotList = list(set(useRobotList))
        return u'Hello,我是机器人Ro'

    if msg1 == 'exit' or msg1 == 'stop':
        if username in useCheckScoreList:
            useCheckScoreList.remove(username)
            return u'已退出查询成绩'
        elif username in useEvaluateList:
            useEvaluateList.remove(username)
            return u'已退出一键评教'
        elif username in useRobotList:
            useRobotList.remove(username)
            return u'bye~'

    if username in useCheckScoreList:
        if msg1 == 'retry':
            thread.start_new_thread(getResult, (studentNum[username], password[username], 'GET_SCORE', username,))
        else:
            thread.start_new_thread(loginJw, (msg, 'GET_SCORE',))

    if username in useEvaluateList:
        if msg1 == 'retry':
            thread.start_new_thread(getResult, (studentNum[username], password[username], 'DO_EVALUATE', username,))
            itchat.send(u'正在尝试重新登录', toUserName=username)
        else:
            thread.start_new_thread(loginJw, (msg, 'DO_EVALUATE',))

    if username in useSearchImgMap:
        if '下一张' in msg1 or 'next' in msg1:
            useSearchImgIndexDic.update({username: useSearchImgIndexDic[username] + 1})
            print useSearchImgMap[username]
            print useSearchImgIndexDic[username]
            thread.start_new_thread(getImg, (useSearchImgMap[username], useSearchImgIndexDic[username], username, ))

    if msg1 == '查询成绩':
        useCheckScoreList.append(username)
        # 防止list重复
        useCheckScoreList = list(set(useCheckScoreList))
        # 查成绩时，退出机器人模式
        if username in useRobotList:
            useRobotList.remove(username)
        # 进行查询前清空学号密码
        studentNum[username] = ''
        password[username] = ''
        return u'请输入学号：'

    if msg1 == '一键评教':
        useEvaluateList.append(username)
        useEvaluateList = list(set(useEvaluateList))
        if username in useRobotList:
            useRobotList.remove(username)
        # 进行查询前清空学号密码
        studentNum[username] = ''
        password[username] = ''
        return u'请输入学号：'

    if '图片' in msg1:
        useSearchImgMap.update({username: msg1})
        useSearchImgIndexDic.update({username: 0})
        if username in useCheckScoreList:
            useCheckScoreList.remove(username)
        thread.start_new_thread(getImg, (msg1, 0, username, ))

    if username in useRobotList:
        thread.start_new_thread(get_response, (msg1, username, ))



# 处理好友添加请求
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.add_friend(**msg['Text'])
    itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])


if sys.argv[1] == 'getQR':
    itchat.auto_login(True, enableCmdQR=False, picDir='/home/myproject/static/qrcode.png')
elif sys.argv[1] == 'cmdQR':
    itchat.auto_login(True, enableCmdQR=2, statusStorageDir='itchat.pkl')

itchat.run()
itchat.dump_login_status()
