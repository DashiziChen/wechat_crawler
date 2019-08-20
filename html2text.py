from requests_html import HTMLSession


def html2text(url):
    """
    提取url中的文章
    :param url:微信文章的url
    :return:文章
    """
    # 设置代理
    proxy = "47.102.216.176:3128"
    proxies = {
        'http': 'http//' + proxy,
        'https': 'https//' + proxy
    }
    session = HTMLSession()
    r = session.get(url, verify=False)
    a = r.html.text.split('\n')  # r.html.text可去掉html中的所有标签
    flag = False  # 使用flag来确定是否为需写入的内容
    text = ""
    for num in range(len(a)):
        if '功能介绍' in a[num]:  # 写入‘功能介绍’以后的内容
            flag = True
            continue
        elif 'var first_sceen__time' in a[num]:  # 写入‘var first_sceen__time’以前的内容
            flag = False
        elif flag:
            text += a[num]
    return text
