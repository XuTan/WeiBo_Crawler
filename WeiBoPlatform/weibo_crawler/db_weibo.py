"""
将本地保存的用户微博信息
保存到PostgreSQL数据库中
"""
import requests
from requests.exceptions import RequestException, ConnectTimeout, ContentDecodingError, ConnectionError
import os
from bs4 import BeautifulSoup
import psycopg2
import json


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


f_path = os.path.dirname(os.path.dirname(__file__))


def save_weibo_db(weibo, screen_name, keyword):
    """
    将用户微博信息保存到数据库中
    :param weibo:微博字典数据
    :param screen_name:微博用户名
    :param keyword:微博关键词
    :return:
    """
    database = "weiboplatform"
    username = "postgres"
    pwd = "admin"
    localhost = "127.0.0.1"
    port = "5432"
    conn = psycopg2.connect(database=database, user=username, password=pwd, host=localhost, port=port)
    cur = conn.cursor()
    try:
        weibo_uid = weibo["user_uid"]
        weibo_screen_name = screen_name
        weibo_keyword = keyword
        weibo_scheme = weibo["scheme"]
        weibo_created_at = weibo["created_at"]
        text = weibo["text"]
        text = text.replace("\'", "'")
        text = text.replace('\"', '"')
        weibo_text = text
        bs_obj = BeautifulSoup(weibo_text, "html5lib")
        weibo_raw_text = bs_obj.get_text()
        weibo_pics = weibo["pics"]
        weibo_comments_count = weibo["comments_count"]
        weibo_attitudes_count = weibo["attitudes_count"]
        weibo_reposts_count = weibo["reposts_count"]
        # 去掉图片的http
        for url in weibo_pics:
            if "http:" in url:
                url = url[5:]
            elif "https:" in url:
                url = url[6:]
        # 处理图片链接长度问题
        if len(weibo_pics) < 9:
            for i in range(9 - len(weibo_pics)):
                weibo_pics.append(None)
        i0, i1, i2, i3, i4, i5, i6, i7, i8 = weibo_pics[0], weibo_pics[1], weibo_pics[2], weibo_pics[3], \
                                             weibo_pics[4], weibo_pics[5], weibo_pics[6], weibo_pics[7], weibo_pics[8]
        insert_sql = "insert into weibodata(uid,weibo_screen_name,weibo_scheme," \
                     "weibo_created_at,keyword,weibo_text,weibo_raw_text," \
                     "weibo_comments_count,weibo_attitudes_count,weibo_reposts_count," \
                     "weibo_pics1,weibo_pics2,weibo_pics3,weibo_pics4," \
                     "weibo_pics5,weibo_pics6,weibo_pics7,weibo_pics8,weibo_pics9) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        cur.execute(insert_sql, (
            weibo_uid,
            weibo_screen_name,
            weibo_scheme,
            psycopg2.Date(weibo_created_at[0], weibo_created_at[1], weibo_created_at[2]),
            weibo_keyword,
            weibo_text,
            weibo_raw_text,
            weibo_comments_count,
            weibo_attitudes_count,
            weibo_reposts_count,
            i0, i1, i2, i3, i4, i5, i6, i7, i8,
        ))
        conn.commit()
        return True
    except (BaseException, FileExistsError, FileNotFoundError, RequestException, ConnectionError, ConnectTimeout,
            ContentDecodingError) as e:
        conn.rollback()
        print(e.args)
    finally:
        conn.close()


def get_weibo_text(uid):
    """
    获取某个用户的微博文本，防止重复录入数据库
    :param:weibo_t 微博文本(包含链接)
    :return:
    """
    database = "weiboplatform"
    username = "postgres"
    pwd = "admin"
    localhost = "127.0.0.1"
    port = "5432"
    conn = psycopg2.connect(database=database, user=username, password=pwd, host=localhost, port=port)
    cur = conn.cursor()
    weibo_texts = []
    try:
        cur.execute("select weibo_text from weibodata where uid=%s", (str(uid),))
        weibos = cur.fetchall()
        weibo_texts = [wt[0] for wt in weibos]
    except (BaseException, Exception) as e:
        print(e.args)
    finally:
        conn.close()
    return weibo_texts


def save_2db(keyword):
    """
    分主题、关键词，
    保存用户微博到数据库中
    :param keyword 用户关键词
    :return:
    """
    try:
        for filename in os.listdir(os.path.join(f_path, "tmp_weibo", keyword)):
            file_name = filename.split(".")[0]
            screen_name = file_name.split("_")[1]
            with open(os.path.join(f_path, "tmp_weibo", keyword, filename), "r",
                      encoding="utf-8") as weibo_file:
                weibos = json.loads(weibo_file.read(), encoding="utf-8")
                for j in range(len(weibos)):  # 遍历筛选微博
                    weibo_before = get_weibo_text(weibos[j]["user_uid"])
                    if weibos[j]["text"] in weibo_before:  # 数据库中存在当前博文
                        continue
                    else:
                        if save_weibo_db(weibos[j], screen_name, keyword):
                            print(screen_name, j)
                        else:
                            print("2db", screen_name, j, "passed")
    except (BaseException, FileNotFoundError, FileExistsError) as e:
        print(e)


# if __name__ == "__main__":
#     save_2db("IT")
#     save_2db("Python")
#     save_2db("刊")
#     save_2db("报")
#     save_2db("爱可可-爱生活")
#     save_2db("经济")
#     save_2db("计算机")
