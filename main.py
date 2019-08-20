# -*- coding: utf-8 -*-
import random
import requests
import time
from pymongo import MongoClient
from auto_operate import WX
from wechat_crawler4.html2text import html2text
import urllib3
import toexcel
import excel2json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 获取公众号的一些参数
def get_public_cache(filename, biz):
    """
    获取公众号参数：url, headers, data, biz
    :param filename: fiddler-token-public.log文件路径
    :param biz: 公众号id
    :return: public_cache字典
    """
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    with open(filename, 'r', encoding='utf8') as f:
        lines = f.readlines()
        public_cookie = lines[1].strip('\n')
        public_token = lines[0].split('&')[0].split('=')[1]
        print(public_token)
    headers = {
        "Cookie": public_cookie,
        "User-Agent": "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
    }
    data = {
        "token": public_token,
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "action": "list_ex",
        "begin": "0",
        "count": "5",
        "query": "",
        "fakeid": biz,
        "type": '9',
    }
    public_cache = {}
    public_cache['url'] = url
    public_cache['headers'] = headers
    public_cache['data'] = data
    public_cache['biz'] = biz
    return public_cache


# 获取文章的一些参数
def get_article_cache(link, article_cache):
    """
    获取文章参数
    :param link: 通过微信公众号文章引用获得的文章链接
    :param article_cache: 从fiddler-token.log中过去的文章参数，appmsg_token, phonecookie, pass_ticket, biz
    :return: article_cache：包含获取阅读数点赞数所需的参数字典：url, headers, data, params,
    """
    mid = link.split("&")[1].split("=")[1]
    idx = link.split("&")[2].split("=")[1]
    sn = link.split("&")[3].split("=")[1]
    _biz = link.split("&")[0].split("_biz=")[1]
    url = "http://mp.weixin.qq.com/mp/getappmsgext"
    headers = {
        "Cookie": article_cache['phonecookie'],
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/6.7.2.1340("
                      "0x26070233) NetType/WIFI Language/zh_CN "
    }
    data = {
        "is_only_read": "1",
        "is_temp_url": "0",
        "appmsg_type": "9",
        'reward_uin_count': '0'
    }
    params = {
        "__biz": _biz,
        "mid": mid,
        "sn": sn,
        "idx": idx,
        "key": "777",
        "pass_ticket": article_cache['pass_ticket'],
        "appmsg_token": article_cache['appmsg_token'],
        "uin": "777",
        "wxtoken": "777",
    }
    article_cache['url'] = url
    article_cache['headers'] = headers
    article_cache['data'] = data
    article_cache['params'] = params
    return article_cache


# python 读取fiddler-token.log中的参数
def get_parameter(filename):
    """
    读取fiddler-token.log中的参数
    :param filename: fiddler-token.log文件路径
    :return: appmsg_token, cookie, biz, pass_ticket
    """
    f = open(filename, 'r', encoding='utf8')
    lines = f.readlines()
    pass_ticket = lines[0].split('&')[4].split('=')[1]
    appmsg_token = lines[0].split('&')[8].split('=')[1]
    cookie = lines[1].strip('\n').replace(' ', '').replace('\n', '')
    biz = lines[2].split('=')[1]
    biz = biz + '=='
    f.close()
    return appmsg_token, cookie, biz, pass_ticket


# 毫秒数转日期
def getDate(times):
    """
    转换日期
    :param times:
    :return: data
    """
    timearr = time.localtime(times)
    date = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
    return date


# 获取阅读数和点赞数
def getMoreInfo(article_cache):
    """
    获取阅读数和点赞数
    :param article_cache: 包含获取阅读数点赞数所需的参数字典：url, headers, data, params
    :return: readNum, likeNum, comment_count
    """
    url = article_cache['url']
    headers = article_cache['headers']
    data = article_cache['data']
    params = article_cache['params']
    # 使用post方法进行提交
    content = requests.post(url, headers=headers, data=data, params=params).json()
    # 提取其中的阅读数和点赞数
    try:
        readNum = content["appmsgstat"]["read_num"]
        print(readNum)
    except:
        readNum = 0
    try:
        likeNum = content["appmsgstat"]["like_num"]
        print(likeNum)
    except:
        likeNum = 0
    try:
        comment_count = content['comment_count']
        print("true:" + str(comment_count))
    except:
        comment_count = 0
        print("error:" + str(comment_count))
    # 歇随机时间，防止被封
    rest = 2 + 3 * random.random()
    time.sleep(rest)
    return readNum, likeNum, comment_count


# 从公众号处可以获取文章总数
def get_appmsg_cnt(public_cache):
    """
    获取公众号文章总数，判断什么时候读取完毕
    :param public_cache: url, headers, data, biz
    :return: 公众号文章总数
    """
    url = public_cache['url']
    header = public_cache['headers']
    data = public_cache['data']
    content_json = requests.get(url, headers=header, params=data, verify=False).json()
    return content_json['app_msg_cnt']


# 获得文章所有信息
def getAllInfo(begin, public_cache, article_cache):
    """
    获取文章所有信息
    :param begin: 微信公众号用于翻页，每+5表示翻一页
    :param public_cache: 公众号字典信息
    :param article_cache: 文章字典信息
    :return: 公众号一页所有文章信息
    """
    # 保存一页列表中的所有文章信息
    messageAllInfo = []
    # begin 从0开始，appmsg_cnt结束
    data1 = public_cache['data']
    data1["begin"] = begin
    url = public_cache['url']
    headers = public_cache['headers']
    # 使用get方法获得每一页的文章数据
    content_json = requests.get(url, headers=headers, params=data1, verify=False).json()
    ran_time = 8 + 5 * random.random()
    time.sleep(ran_time)
    # 返回了一个json，里面是每一页的数据
    if "app_msg_list" in content_json:
        for item in content_json["app_msg_list"]:
            # 提取每页文章的标题及对应的url
            url = item['link']
            article_cache = get_article_cache(url, article_cache)
            readNum, likeNum, comment_count = getMoreInfo(article_cache)
            info = {
                "title": item['title'],
                "readNum": readNum,
                "likeNum": likeNum,
                'comment_count': comment_count,
                "digest": item['digest'],
                "date": getDate(item['create_time']),
                "url": item['link']
            }
            text = html2text(info["url"])
            info["article"] = text
            messageAllInfo.append(info)
        # validity_message用于判断爬取该页所有文章阅读数点赞数是否有效，如果无效则需要重新获取参数爬取
        validity_message = list(filter(lambda x: x["readNum"] != 0, messageAllInfo))
        if validity_message:
            return messageAllInfo
        else:
            return None


# 写入数据库
def putIntoMogo(urlList, gzh):
    """
    写入mongoDB数据库
    :param urlList: 公众号一页所有文章信息
    :param gzh: 公众号名字
    :return: None
    """
    host = "127.0.0.1"
    port = 27017
    # 连接数据库
    client = MongoClient(host, port)
    # 建库，如果已有库，则会在已有库的基础上添加
    wechat_crawler = client['wechat_crawler']
    # 建表
    wx_message_sheet = wechat_crawler[gzh]
    # 存
    for message in urlList:
        wx_message_sheet.insert_one(message)
    print("成功！")


# 点击公众号文章并获取文章参数
def task(gzh, item_num=0):
    """
    点击公众号文章并获取文章参数
    :param gzh: 公众号名字
    :param item_num: 点击历史信息的第几条文章
    :return: cache：从fiddler-token.log获取的信息
    """
    wx = WX()
    wx.enter(gzh, item_num)
    appmsg_token, phonecookie, biz, pass_ticket = get_parameter('fiddler-token.log')
    cache = {}
    cache['appmsg_token'] = appmsg_token
    cache['phonecookie'] = phonecookie
    cache['biz'] = biz
    cache['pass_ticket'] = pass_ticket
    return cache


def main(lists):
    """
    主函数
    :param lists:爬取公众号列表
    :return: None
    """
    check_message = True
    for gzh in lists:
        article_cache = task(gzh)
        biz = article_cache['biz']
        public_cache = get_public_cache('fiddler-token-public.log', biz)
        # 获得公众号总共文章
        total_num = get_appmsg_cnt(public_cache)
        i = 0  # 公众号中的页码数
        item_num = 0  # 参数获取出错时，点第二条文章获取参数试试
        while True:
            begin = i * 5
            if begin >= total_num:
                break
            messageAllInfo = getAllInfo(str(begin), public_cache, article_cache)
            # 下面是错误处理，如果参数出错，重复三次获取参数，如果依然出错，
            # 则说明该文章目前在公众号历史文章中已经查不到，只能获得文章不
            # 能获取点赞阅读数
            if check_message:  # 是否需要检查获取参数
                if messageAllInfo == None:  # 有时会出现得不到参数的情况，需要重新获取参数
                    print("第{}次参数获取失败，正在重新获取。。。".format(item_num+1))
                    item_num += 1
                    if item_num < 3:
                        article_cache = task(gzh, item_num)
                        continue
                    else:  # 实在没办法获取参数了，说明这之后的页面是微信上翻不到的历史文章，采集不到点赞和阅读数
                        item_num = 0
                        check_message = False
                else:
                    item_num = 0
            print("第%s页" % i)
            putIntoMogo(messageAllInfo, gzh)
            i += 1
        check_message = True
    print("所有文章已爬取完毕！")


if __name__ == '__main__':
    lists = ["荷赛"]
    main(lists)
    # toexcel.export2excel(lists, '微信公众号爬取.xlsx')  # mongoDB导出到excel
    # excel2json.excel2json('微信公众号爬取.xlsx')

