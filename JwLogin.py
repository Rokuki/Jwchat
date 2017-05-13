# coding=utf-8
import random
import re
import urllib

import requests
from bs4 import BeautifulSoup
from lxml import etree

from captcha.Predict import predict

url = 'http://jw.xhsysu.cn/'
host = 'jw.xhsysu.cn'
userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 " \
            "Safari/537.36 "
sname = ''
Cookie = ''
user = ''


def login(xh, password, action, itchat, username):
    global sname
    global url
    global Cookie
    global host
    global user
    global userAgent
    user = username
    s = requests.session()
    try:
        response = s.get(url)
    except:
        return 'TIMEOUT'
    selector = etree.HTML(response.content)
    try:
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
    except:
        return 'UNKNOWN_ERROR'
    CheckCodeUrl = url+'CheckCode.aspx'
    CheckCodeResponse = s.get(CheckCodeUrl, stream=True)
    cookies = s.cookies
    # print cookies
    # 验证码目录
    Dstdir = "captcha/download_code/"
    # print ('save the checkcode to the' + Dstdir + 'code.jpg' + "\n")
    with open(Dstdir + 'code.jpg', 'wb') as f:
        for chunk in CheckCodeResponse.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
        f.close()
    code = predict(Dstdir + 'code.jpg')
    radio_button_list1 = u"学生".encode('gb2312')
    if code != "":
        data = {
            "RadioButtonList1": radio_button_list1,
            "__VIEWSTATE": __VIEWSTATE,
            "txtUserName": xh,
            "TextBox2": password,
            "txtSecretCode": code,
            "Button1": "",
        }
    # print code
    headers = {
        "User-Agent": userAgent
    }
    response = s.post(url, data=data, headers=headers)
    if response.url == url+'default2.aspx':
        return 'UNKNOWN_ERROR'
    soup = BeautifulSoup(response.content.decode('gb2312'))
    try:
        sname = soup.find(id="xhxm").string
    except:
        return 'UNKNOWN_ERROR'

    for i in cookies:
        Cookie = i.name + "=" + i.value
    # 查询成绩
    if action == 'GET_SCORE':
        url2 = url+'xscjcx.aspx?'
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': host,
            'Cookie': Cookie,
            'Origin': url,
            'Pragma': 'no-cache',
            'Referer': url+'xs_main.aspx?xh=' + xh,
            "User-Agent": userAgent
        }
        data2 = urllib.urlencode({
            'xh': xh,
            'gnmkdm': 'N121605',
            'xm': sname[:-2].encode('UTF-8'),
        })

        response = s.post(url2 + data2, None, headers=head)
        __VIEWSTATE = getViewState(response.content.decode('gb2312'))
        data = urllib.urlencode({
            "__VIEWSTATE": __VIEWSTATE,
            "btn_zcj": "历年成绩",
            "ddl_kcxz": ""
        })
        response = s.post(url2 + data2, data=data, headers=head)
        return getScore(response.content.decode('gb2312'))
    # 一键评教
    elif action == 'DO_EVALUATE':
        pj_url = []
        li = soup.find('ul', {'class': 'nav'}).find_all('li')
        li2 = li[5].find_all('li')
        # pj_url = li2[0].a.get('href')
        for i in range(len(li2)):
            pj_url.append(li2[i].a.get('href'))
        head = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep - alive',
            'Cookie': Cookie,
            'Host': host,
            'Referer': url+'xs_main.aspx?xh=' + xh,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': userAgent
        }
        try:
            response = s.post(url + pj_url[0], data=None, headers=head)
        except IndexError:
            return u'该学生已完成评教！'
        doEvaluate(response.content.decode('gb2312'), pj_url, 0, s, itchat)
        # print '评教完成'
        return u'评教成功，为保证安全，请登录教务系统查看并提交。http://jw.xhsysu.cn'


def doEvaluate(response, pj_url, index, s, itchat):
    global user
    global Cookie
    global userAgent
    evaluateResults = []
    itchat.send(u'正在评价第'+str(index+1)+u'位教师，一共有'+str(len(pj_url))+u'位教师',toUserName=user)
    pjkc = pj_url[index][pj_url[index].find('=') + 1: pj_url[index].find('&')]  # 如(2016-2017-2)-02013024-1001945-3
    __VIEWSTATE = getViewState(response)
    soup = BeautifulSoup(response)
    dataGird = soup.find(id='DataGrid1')
    pjkc_name = soup.find(id='pjkc').find_all('option')  # 评教课程名称
    Js1 = {}    # DataGrid1:_ctl2:JS1
    txtjs1 = {}     # DataGrid1:_ctl2:txtjs1
    tr = dataGird.find_all('tr')
    # 设置评价
    for i in range(1, len(tr)):
        select = tr[i].find('select')
        if select is not None:
            if random.random() < 0.15:
                Js1[select.get('name')] = u'良'.encode('gb2312')
                evaluateResults.append('B')
            else:
                Js1[select.get('name')] = u'优'.encode('gb2312')
                evaluateResults.append('A')
            txtjs1[select.get('name')] = ''
    itchat.send(pjkc_name[index].string + str(evaluateResults), toUserName=user)
    head = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep - alive',
        'Cookie': Cookie,
        'Host': host,
        'Referer': url + pj_url[0],
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': userAgent
    }
    # data22 = collections.OrderedDict()
    # data22['__EVENTTARGET'] = pjkc,
    # data22['__EVENTARGUMENT'] = '',
    # data22['__VIEWSTATE'] = __VIEWSTATE,
    # data22['pjkc'] = pjkc,
    # data22['txt1'] = '',
    # data22['TextBox1'] = '0',
    # data22['pjxx'] = '',
    # data22.update(txtjs1)
    # data22.update(Js1)
    # data22['Button1'] = u'保  存'.encode('gb2312')
    data22 = {
        '__EVENTTARGET': pjkc,
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': __VIEWSTATE,
        'pjkc': pjkc,
        'txt1': '',
        'TextBox1': '0',
        'pjxx': '',
        'Button1': u'保  存'.encode('gb2312')
    }
    # 从第一页进入，post和refer的url皆为第一页的url
    response = s.post(url + pj_url[0], data=data22, headers=head)
    response = response.content.decode('gb2312')
    index += 1
    if index < len(pj_url):
        doEvaluate(response, pj_url, index, s, itchat)


def getViewState(response):
    view = r'name="__VIEWSTATE" value="(.+)" '
    view = re.compile(view)
    __VIEWSTATE = view.findall(response)[0]
    return __VIEWSTATE


def getScore(Score_html):  # print the result
    soup = BeautifulSoup(Score_html)
    tab = soup.find(id="divNotPs").table
    col = [3, 7, 6, 8]
    tr = tab.findAll('tr')
    count = len(tr)
    result = ''
    for j in range(count):
        colname = tr[j].findAll('td')
        m = ''
        for i in col:
            m = colname[i].getText() + "|" + m  # 列表名字
        result = result + m + '\n'
    return result


