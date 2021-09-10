# coding=utf-8
import os
import random
import time

import re  # 需安装re模块
import requests  # 需安装requests库

# 目标网址：https://qun.icve.com.cn/
# 代码仅支持重庆电子工程职业学院
# 代码够烂，欢迎指正。随缘修改。
# 禁止用于商业用途！！

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

session_ = requests.Session()


def PPT(cell, courseOpenId, watchVideoLength, videoAllLength, title):
    url = "https://qun.icve.com.cn/study/process/saveStudy"
    for i in range(2):
        if watchVideoLength <= videoAllLength:
            data = {
                "courseOpenId": courseOpenId,
                "cellId": cell,
                "watchVideoLength": 10,
                "videoAllLength": 0
            }

            resp = session_.post(url, data, headers=headers)
            watchVideoLength = videoAllLength
        else:
            print(title, "PPT完成或看过！")
            break
    time.sleep(2)


def videos(cell, courseOpenId, Time, title, stuStudyNewlyTime):  # 刷视频
    url = "https://qun.icve.com.cn/study/process/saveStudy"  # 上传数据
    audioVideoLong = int(Time[3:5]) * 60 + int(Time[6:8])
    forNum = int((audioVideoLong - stuStudyNewlyTime) / 10) + 2  # 循环次数 总视频长度-观看过后的长度分10段 每段循环后会加10.多

    for i in range(forNum):
        if stuStudyNewlyTime - 1 < 0:
            stuStudyNewlyTime = 1

        nowTime = stuStudyNewlyTime - 1 + 10.000001 * i

        if nowTime >= audioVideoLong:
            stutyTime = audioVideoLong
        else:
            stutyTime = nowTime
        data = {
            "courseOpenId": courseOpenId,
            "cellId": cell,
            "watchVideoLength": stutyTime,
            "videoAllLength": audioVideoLong
        }
        res = session_.post(url, data=data, headers=headers)
        if res.json()['code'] != 1:
            exit()
        if res.json()['status'] == 1:
            print(title + "视频完成或看过！！")
            break
        time.sleep(3)
    time.sleep(5)


def saveCellTime(cell, courseOpenId, seekTime, title):  # 刷图片和其他东西 易出现异常
    url = 'https://qun.icve.com.cn/study/process/saveStudy'
    data = {
        'courseOpenId': courseOpenId,
        'cellId': cell,
        'watchVideoLength': seekTime,
        'videoAllLength': "0"
    }
    for i in range(2):
        resp = session_.post(url, data, headers=headers)
        seekTime = "10"
        time.sleep(3)

    url1 = 'https://qun.icve.com.cn/study/process/saveCellTime'
    data1 = {
        'courseOpenId': courseOpenId,
        'cellId': cell,
        'auvideoLength': "30",
    }
    time.sleep(2)
    resp1 = session_.post(url1, data1, headers=headers)
    print(title + '完成!')


def states(cell, courseOpenId, URL, title, seekTime):  # 拿到文件页数和视频时间
    url = URL
    resp = session_.post(url, headers=headers)
    tep = resp.json()
    if 'duration' in tep['args']:  # 是视频
        Time = tep['args']['duration']  # 视频总长度
        videos(cell, courseOpenId, Time, title, seekTime)
    elif 'page_count' in tep['args']:  # 是PPT
        videoAllLength = tep['args']['page_count']  # PPT页数
        PPT(cell, courseOpenId, seekTime, videoAllLength, title)
    else:  # 其它  暂时不要刷图片  日后会更新
        saveCellTime(cell, courseOpenId, seekTime, title)


def viewDirectory(cell, courseOpenId):  # 拿到time和token
    url = "https://qun.icve.com.cn/study/process/viewDirectory"
    dat = {
        "courseOpenId": courseOpenId,
        "cellId": cell
    }
    resp = session_.post(url, data=dat, headers=headers)
    seekTime = resp.json()['seekTime']
    title = resp.json()['title']
    tep = resp.json()['resUrl']
    job = re.compile(r'.*?status\":\"(?P<time>.*?)\".*?', re.S)
    t = job.finditer(tep)
    for i in t:
        Time = i.group('time')
        states(cell, courseOpenId, Time, title, seekTime)
        time.sleep(0.2)


def addReply(topicId, courseOpenId, cell):  # 评论

    add = ['很透彻啊', '通俗易懂', '内容主次分明，抓住关键', '很有艺术，清晰有序，科学规范', '很有创意，对教材把握透彻、挖掘深入、处理新颖', '结构紧凑,生动形象', '目标全面、准确、具体',
           '讲的不错，都明白了，点赞！', '此课程讲的非常好。']
    url = "https://qun.icve.com.cn/study/bbs/addReply"
    data = {
        "topicId": topicId,
        "content": f'{random.choice(add)}',
        "courseOpenId": courseOpenId,
    }
    resp = session_.post(url, data, headers=headers)
    print(resp.json()['msg'])
    time.sleep(10)


def viewDirectory1(cell, courseOpenId):  # 讨论专属
    url = "https://qun.icve.com.cn/study/process/viewDirectory"
    data = {
        "courseOpenId": courseOpenId,
        "cellId": cell,
    }
    resp = session_.post(url, data, headers=headers)
    topicId = resp.json()['operationId']
    addReply(topicId, courseOpenId, cell)


def getList(courseOpenId, flag):  # 具体刷课 获取里的所有 cellid
    url = "https://qun.icve.com.cn/study/process/getList"
    dat = {
        "courseOpenId": courseOpenId
    }
    resp = session_.post(url, data=dat, headers=headers)
    result = resp.json()
    for i in range(len(result['list'])):
        time.sleep(1)
        for j in range(len(result['list'][i]["topics"])):
            time.sleep(1)
            for k in range(len(result['list'][i]["topics"][j]['cells'])):
                time.sleep(1)
                cell = result['list'][i]["topics"][j]['cells'][k]['Id']
                cellTypeStr = result['list'][i]["topics"][j]['cells'][k]['cellTypeStr']  # 讨论
                if cellTypeStr == "讨论" and flag == 1:
                    viewDirectory1(cell, courseOpenId)

                viewDirectory(cell, courseOpenId)


def getCourseList(flag):  # 课程列表
    url = "https://qun.icve.com.cn/api/portal/personal/getCourseList?type=1&page=1&pageSize=9"
    resp = session_.post(url, headers=headers)
    result = resp.json()["list"]
    for i in range(len(result)):
        print(result[i]['Title'] + "  {}".format(i))
    print("请输入0～{}".format(len(result) - 1))
    try:
        value = eval(input())  # 合理选课程
        print("您已选择" + result[value]['Title'])
        courseOpenId = resp.json()["list"][value]["Id"]
        getList(courseOpenId, flag)
    except Exception:
        print("异常请重新执行！拜拜！")
        exit()


def login():  # 登录函数
    url = "https://qun.icve.com.cn/common/login/loginSystem"
    global session_
    print('#' * 50)
    print('*          Welcome to ICVE script !              *')
    print('*            author:真皮沙发                      *')
    print('*            createTime:2021-7-23                *')
    print('*       免责声明,仅供学习交流使用,任何行为与作者无关     *')
    print('#' * 50)
    username = str(input("请输入账号:"))
    password = str(input("请输入密码:"))
    flag = eval(input("是否需要评论？ 1(是) or 2(否):"))
    dat = {
        "username": username,
        "password": password,
    }
    session_ = requests.Session()
    resp = session_.post(url, data=dat, headers=headers)
    if resp.json()["code"] == 1:
        print(resp.json()["msg"])
        getCourseList(flag)  # 刷评论
        print("恭喜！该课程所有视频及PPT完成！请自行完成该课程作业！ ^_^' ")
    else:
        print(resp.json()["msg"], "请重新输入！")


login()
