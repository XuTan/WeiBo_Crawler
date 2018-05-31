# -*-encoding:utf-8-*-
"""
用户关键词搜索爬虫
根据给定的关键词，爬取微博移动端前5页的分页用户
分析筛选
暂时保存到JSON文件中
然后再保存到数据库中
"""
import requests
import json
from urllib.parse import urlencode
from requests.exceptions import RequestException, ConnectTimeout, ContentDecodingError, ConnectionError
import os


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


def get_topic_user_page(keyword, page=1):
    """
    根据主题关键词获取用户信息JSON文件页面
    :param keyword: 主题关键词
    :param page: 分页，默认为第一页
    :return:网页文本/None
    """
    try:
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/66.0.3359.117 Safari/537.36"
        }
        param = {
            'type': 'user',
            'queryVal': keyword,
            'containerid': '100103type=3&q=' + keyword,
            'page': str(page)
        }
        base_url = "https://m.weibo.cn/api/container/getIndex?"
        url = base_url + urlencode(param)
        response = requests.get(url, headers=headers, proxies=get_proxy())
        if response.status_code == 200:
            return response.text
        return None
    except (RequestException, ContentDecodingError, ConnectionError, ConnectTimeout) as e:
        print(e.args)
        return None


def get_topic_user_list(keyword):
    """
    根据主题关键词，获取用户列表，并将其信息保存到list中
    :param keyword: 主题关键词
    :return:JSON格式，[{...},{...},{...}]
    """
    return_json_list = []  # 返回json列表
    for page in range(1, 6):  # 爬取1~5页的用户数据
        html = get_topic_user_page(keyword, page)
        if html is not None:  # 有返回json数据
            data = json.loads(html, encoding="utf-8")
            if data["ok"] == 1:  # 如果页面返回正确
                cards = data.get("data").get("cards")
                cd = 0
                if len(cards) > 0:  # 如果有用户列表
                    cd = 0
                if len(cards) == 2:  # 第一页特殊处理
                    cd = 1
                card_group = cards[cd].get("card_group")
                for j in range(len(card_group)):
                    if card_group[j].get("card_type") == 10:  # 判断card类型，10为用户
                        user_desc1 = str(card_group[j].get("desc1"))
                        user_desc2_fans = str(card_group[j].get("desc2"))  # 获取描述介绍
                        user = card_group[j].get("user")
                        user_uid = user.get("id")
                        user_screen_name = str(user.get("screen_name"))
                        user_followers_count = str(user.get("followers_count"))
                        user_profile_image_url = str(user.get("profile_image_url"))
                        if "有限公司" in user_desc1 or "有限公司" in user_screen_name or "品牌" in user_desc1 or \
                                "品牌" in user_screen_name or "自媒体" in user_desc1 or "自媒体" in user_screen_name:
                            continue
                        if int(user_followers_count.split("万")[0]) >= 10:
                            if "万" in user_followers_count:
                                json_info = {"user_uid": user_uid,
                                             "user_keyword": keyword,
                                             "user_screen_name": user_screen_name,
                                             "user_desc1": user_desc1,
                                             "user_desc2_fans": user_desc2_fans,
                                             "user_profile_image_url": user_profile_image_url
                                             }
                                return_json_list.append(json_info)
                        else:  # 万
                            continue
                else:  # len(cards)>0
                    continue
            else:  # data["ok"]
                continue
        else:  # html is not None
            continue
    return return_json_list


def save2file(keyword):
    """
    将关键词用户以JSON格式保存到本地文件中
    :param keyword:用户关键词
    :return:
    """
    f_path = os.path.dirname(os.path.dirname(__file__))
    try:
        data = get_topic_user_list(keyword)
        with open(os.path.join(f_path, "tmp_topicuser", keyword + ".json"), "w", encoding="utf-8") as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
            print(keyword, len(data), data)
    except (FileNotFoundError, FileExistsError) as e:
        print(e.args)

# if __name__ == "__main__":
#     save2file("python")
