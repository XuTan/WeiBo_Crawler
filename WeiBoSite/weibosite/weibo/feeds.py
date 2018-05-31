from django.contrib.syndication.views import Feed

from .models import Weibodata


class AllPostsRssFeed(Feed):
    # 显示在聚合阅读器上的标题
    title = "Weibo Platform 微博爬虫学习资料分享平台"

    # 通过聚合阅读器跳转到网站的地址
    link = "/"

    # 显示在聚合阅读器上的描述信息
    description = "Weibo Platform"

    # 需要显示的内容条目
    def items(self):
        return Weibodata.objects.all()

    # 聚合器中显示的内容条目的标题
    def item_title(self, item):
        return '[%s] %s' % (item.keyword, item.weibo_screen_name)

    # 聚合器中显示的内容条目的描述
    def item_description(self, item):
        return item.weibo_text
