# -*-encoding:utf-8-*-
"""
将本地的关键词用户信息
JSON文件中的信息
保存到PostgreSQL数据库中
"""
import psycopg2
import os
import json
from requests.exceptions import RequestException, ConnectTimeout, ConnectionError, ContentDecodingError

# 当前脚本文件父目录
f_path = os.path.dirname(os.path.dirname(__file__))


def get_users(uid):
    """
    获取当前数据库中的用户id，避免重复录入
    :param: uid 用户id
    :return:
    """
    database = "weiboplatform"
    username = "postgres"
    pwd = "admin"
    localhost = "127.0.0.1"
    port = "5432"
    conn = psycopg2.connect(database=database, user=username, password=pwd, host=localhost, port=port)
    cur = conn.cursor()
    users = 0
    try:
        cur.execute("select count(uid) from userdata where uid=%s;", (str(uid),))
        users = cur.fetchone()[0]
    except (BaseException, Exception) as e:
        print(e.args)
    finally:
        conn.close()
    return users


def save_user_2db(keyword, data):
    """
    保存某个关键词下的json文件用户信息到数据库中
    :param keyword：用户关键词类别
    :param data：用户类别关键词数据
    :return:True/False
    """
    database = "weiboplatform"
    username = "postgres"
    pwd = "admin"
    localhost = "127.0.0.1"
    port = "5432"
    conn = psycopg2.connect(database=database, user=username, password=pwd, host=localhost, port=port)
    cur = conn.cursor()
    try:
        uid = str(data["user_uid"])
        screen_name = data["user_screen_name"]
        desc1 = data["user_desc1"]
        desc2_fans = data["user_desc2_fans"]
        profile_image_url = data["user_profile_image_url"]
        main_page = "https://m.weibo.cn/u/" + uid
        # user is a reserved keyword in postgresql
        insert_sql = "insert into userdata(uid,keyword,user_screen_name,user_main_page," \
                     "user_desc1,user_desc2_fans,user_image_url) " \
                     "values(%s,%s,%s,%s,%s,%s,%s);"
        cur.execute(insert_sql, (
            uid, keyword, screen_name, main_page, desc1, desc2_fans, profile_image_url,
        ))
        conn.commit()
        return True
    except (BaseException, FileExistsError, FileNotFoundError, RequestException) as e:
        conn.rollback()
        print(e)
        return False
    finally:
        conn.close()


def topic_user_2db(keyword):
    """
    处理topic下的用户
    :return:
    """
    try:
        with open(os.path.join(f_path, "tmp_topicuser", keyword + ".json"), "r", encoding="utf-8") \
                as file:
            data = json.loads(file.read(), encoding="utf-8")
            for j in range(len(data)):
                if get_users(data[j]["user_uid"]) >= 1:  # 避免重复录入数据库
                    continue
                else:
                    if save_user_2db(keyword, data[j]):  # data[j]为每个用户
                        print(keyword, data[j]["user_uid"])
    except (BaseException, FileNotFoundError, FileExistsError) as e:
        print(e.args)


# if __name__ == "__main__":
#     topic_user_2db("IT")
#     topic_user_2db("Python")
#     topic_user_2db("刊")
#     topic_user_2db("报")
#     topic_user_2db("爱可可-爱生活")
#     topic_user_2db("经济")
#     topic_user_2db("计算机")
