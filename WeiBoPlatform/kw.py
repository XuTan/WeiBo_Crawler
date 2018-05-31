"""
获取用户关键词
搜索用户
搜索微博
录入数据库
"""
import os
import psycopg2

from user_crawler.user_topic_kw import save2file
from user_crawler.db_topicuser import topic_user_2db
from weibo_crawler.weibo_user_id import topic_user_spider
from weibo_crawler.db_weibo import save_2db


class KW():
    def __init__(self):
        self.keywords = self.get_keywords()

    def get_keywords(self):
        """
        从keywords.txt中获取关键词列表
        :return: kw list
        """
        with open(os.path.join(os.getcwd(), "keywords.txt"), "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines()]
        return lines

    def get_kw_db(self):
        """
        获取数据库中当前的关键词
        :return:
        """
        database = "weiboplatform"
        username = "postgres"
        pwd = "admin"
        localhost = "127.0.0.1"
        port = "5432"
        conn = psycopg2.connect(database=database, user=username, password=pwd, host=localhost, port=port)
        cur = conn.cursor()
        keywords = []
        try:
            cur.execute("select keyword from keywords;")
            keywords = cur.fetchall()
            keywords = [kw[0] for kw in keywords]
        except (BaseException, Exception) as e:
            print(e.args)
        finally:
            conn.close()
        return keywords

    def kw_2db(self, keyword):
        """
        将关键词录入数据库
        :param keywords:
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
            insert_sql = "insert into keywords(keyword) values(%s);"
            cur.execute(insert_sql, (keyword,))
            conn.commit()
            return True
        except (BaseException, Exception) as e:
            print(e.args)
            conn.rollback()
        finally:
            conn.close()
        return False

    def spider(self):
        """
        成功将关键词录入数据库后，即是需要爬虫的
        :param keyword:
        :return:
        """
        kw_indb = self.get_kw_db()
        for kw in self.keywords:
            if kw not in kw_indb:
                self.kw_2db(kw)
            save2file(kw)
            topic_user_2db(kw)
            topic_user_spider(kw)
            save_2db(kw)


if __name__ == "__main__":
    K = KW()
    K.spider()
