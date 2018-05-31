# -*-encoding:utf-8-*-
"""
通过用户的id
获取每个用户的最新微博
分析筛选出重要的信息
以JSON格式暂时保存到本地文件中
"""
import requests
from requests.exceptions import RequestException, ConnectionError, ConnectTimeout, ContentDecodingError
import json
from datetime import date
import time
import os
from bs4 import BeautifulSoup


def get_proxy():
    def get_IP():
        try:
            response = requests.get('http://127.0.0.9:5555/random')
            if response.status_code == 200:
                return response.text
        except ConnectionError:
            return None

    proxy = get_IP()
    if proxy is None:
        return None
    else:
        return {'http': 'http://' + proxy, 'https': 'https://' + proxy}


def get_page(url):
    """
    通过url，获取用户的页面数据
    :param url: 爬取页面url
    :return: 页面数据
    """
    try:
        headers = {
            "User - Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36"
        }
        response = requests.get(url, headers=headers, proxies=get_proxy())
        if response.status_code == 200:
            return response.text
    except (RequestException, BaseException, ConnectionError, ContentDecodingError, ConnectTimeout) as e:
        print(e.message)
    return None


def get_containerid(uid):
    """
    获取微博主页的containerid,爬取用户的所有微博时需要此id
    :param uid:识别用户的唯一id
    :return:containerid
    """
    containerid = None
    try:
        url = "https://m.weibo.cn/api/container/getIndex?type=uid&value=" + str(uid)
        html = get_page(url)
        content = json.loads(html, encoding="utf-8")
        if content.get("ok") == 1:  # 有正确获取到数据
            if "data" in content:
                data = content.get("data")
                if "tabsInfo" in data:
                    tabs = data.get("tabsInfo").get("tabs")
                    for i in range(5):  # note bug len(tabs)
                        if str(i) in tabs:
                            tabs_d = tabs.get(str(i))
                            tab_type = tabs_d.get("tab_type")
                            if tab_type == "weibo":
                                containerid = tabs_d.get("containerid")
    except (BaseException, Exception) as e:
        print(e)
    return containerid


def transfer_time(created_at):
    """
    转换发布博文的时间格式
    1)2017-12-24 往年的不需要转换
    2) 04-21 当年的，在两天以前的，需要添加年份
    3) 昨天 XX:XX 当年，昨天，需要对月末和月初进行处理
    4) XX前 当年，简单设计为当天的博文
    :param: create_at:从JSON文件中提取出来的，字符串类型
    :return:YYYY-MM-DD
    """
    dt = date.today()
    if created_at.count("-") == 2:
        created_at_split = created_at.split("-")
        return [int(created_at_split[0]), int(created_at_split[1]), int(created_at_split[2])]
    elif created_at.count("-") == 1:
        return [dt.year, int(created_at.split("-")[0]), int(created_at.split("-")[1])]
    elif "昨天" in created_at:
        new_dt = date.fromtimestamp(time.time() - 24 * 3600)
        return [new_dt.year, new_dt.month, new_dt.day]
    elif "前" in created_at:
        return [dt.year, dt.month, dt.day]


def get_weibo_text(text):
    """
    获取完整微博文本信息
    :param text:
    :return:
    """
    weibo_text = ""
    if "/status/" in text:  # 如果有缩略原文
        href = BeautifulSoup(text, "html5lib").findAll("a")[-1]['href']
        headers = {
            "User - Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36"
        }
        response = requests.get("https://m.weibo.cn/statuses/extend?id=" + href.split("/")[-1], headers=headers,
                                proxies=get_proxy())
        if response.status_code == 200:
            html_text = response.text
            content = json.loads(html_text, encoding="utf-8")
            if content.get("ok") == 1:  # 如果页面获取正确
                weibo_text = content.get("data").get("longTextContent")
    else:
        weibo_text = text
    return weibo_text


def get_weibo(uid):
    """
    爬取用户的所有微博，提示输出信息，并保存到JSON文件中
    uid:识别用户的唯一id
    created_at:发送博文时间 YYYY-MM-DD
    scheme:原博文URL地址
    text:原博文文本内容，包含一些图片、表情链接
    pics:列表，原博文的large图片
    comments_count:原博文评论数
    attitudes_count:原博文被圈数
    reports_count:原博文转发数
    :param uid:识别用户的唯一id
    :return:
    """
    i = 0  # 用户微博分页数
    return_weibo_list = []  # 返回json列表
    try:
        containerid = get_containerid(uid)
        if containerid is not None:
            while i < 100:  # 爬取前1000条微博
                i += 1
                weibo_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value=" + str(uid) + "&containerid=" \
                            + containerid + "&page=" + str(i)
                data = get_page(weibo_url)
                content = json.loads(data, encoding="utf-8")
                if content.get("ok") == 1 and "cards" in content.get("data"):  # 如果分页正确，有该页存在
                    cards = content.get("data").get('cards')
                    if len(cards) > 0:  # 如果该页有博文
                        for j in range(len(cards)):
                            if cards[j].get('card_type') == 9 and "mblog" in cards[j]:  # 判断card类型，9为博文,判断不为空
                                mblog = cards[j].get('mblog')
                                attitudes_count = mblog.get('attitudes_count')
                                comments_count = mblog.get('comments_count')
                                created_at = transfer_time(str(mblog.get('created_at')))
                                reposts_count = mblog.get('reposts_count')
                                scheme = cards[j].get('scheme')
                                text = get_weibo_text(mblog.get('text'))
                                if "retweeted_status" in mblog:  # 筛选掉转发而来的博文
                                    continue
                                else:
                                    bs_text = BeautifulSoup(text, "html5lib")
                                    if len(list(bs_text.findAll("a"))) > 0:  # 当有链接标签时
                                        bs_text_attrs = bs_text.a.attrs  # 筛选掉带标签话题的博文
                                        if "class" in bs_text_attrs:
                                            if bs_text_attrs["class"][0] == "k":
                                                continue  # notice the space and logic
                                    pics = []
                                    if "pics" in mblog:
                                        pics_obj = mblog.get("pics")
                                        for pic_index in range(len(pics_obj)):
                                            pics.append(pics_obj[pic_index].get("large").get("url"))
                                    d = {"user_uid": uid,
                                         "created_at": created_at,
                                         "scheme": str(scheme),
                                         "text": str(text),
                                         "pics": pics,
                                         "comments_count": comments_count,
                                         "attitudes_count": attitudes_count,
                                         "reposts_count": reposts_count,
                                         }
                                    return_weibo_list.append(d)
                else:
                    continue
    except (Exception, BaseException) as e:
        print(e)
    return return_weibo_list


def topic_user_spider(keyword):
    """
    根据主题关键词，将用户微博信息爬取下来
    JSON文件格式
    暂时保存到本地
    :return:
    """
    f_path = os.path.dirname(os.path.dirname(__file__))
    if os.path.exists(os.path.join(f_path, "tmp_weibo", keyword)) is not True:
        os.mkdir(os.path.join(f_path, "tmp_weibo", keyword))
    try:
        with open(os.path.join(f_path, "tmp_topicuser", keyword + ".json"), "r", encoding="utf=8") as user_f:
            data = json.loads(user_f.read(), encoding="utf-8")
        for i in range(len(data)):  # 对主题下的每个用户的微博进行爬取
            times = 0
            while times < 4:  # 每个用户尝试爬取4次
                user_weibo = get_weibo(data[i]["user_uid"])
                if len(user_weibo) > 0:  # 爬取到了数据
                    with open(os.path.join(f_path, "tmp_weibo", keyword,
                                           str(data[i]["user_uid"]) + "_" + data[i][
                                               "user_screen_name"] + ".json"),
                              "w", encoding="utf-8") as user_weibo_f:
                        user_weibo_f.write(json.dumps(user_weibo, indent=4, ensure_ascii=False))
                        print(keyword, data[i]["user_uid"], data[i]["user_screen_name"])
                        break
                times += 1
            time.sleep(1)  # 礼貌爬取
    except (FileExistsError, FileNotFoundError, BaseException) as e:
        print(e.args)


# if __name__ == "__main__":
#     topic_user_spider("爱可可-爱生活")
