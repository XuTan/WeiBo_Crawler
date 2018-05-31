from django import template
from ..models import Weibodata, Keywords,Userdata
from django.db.models.aggregates import Count

register = template.Library()


# 显示最新博文用户前9
@register.simple_tag
def get_recent_posts(num=9):
    return Weibodata.objects.all().order_by('-weibo_created_at').distinct()[:num]


# 按照年份、月份分类归档
@register.simple_tag
def archives():
    return Weibodata.objects.dates('weibo_created_at', 'year', order='DESC')


# 按照关键词分类
@register.simple_tag
def get_categories():
    return Keywords.objects.all()


# 用户标签
@register.simple_tag
def get_tags():
    return Userdata.objects.all()
