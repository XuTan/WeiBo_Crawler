# WeiBo_Crawler
### WeiBoPlatform includes spider proxy pool, keyword user spider and weibo spider three sub-system.WeiBoSite includes a simple web site.
#### WeiBoPlatform
+ [keywords.txt](https://github.com/XuTan/WeiBo_Crawler/blob/master/WeiBoPlatform/keywords.txt) includes some keywords topic.
+ [proxypool](https://github.com/XuTan/WeiBo_Crawler/tree/master/WeiBoPlatform/proxypool) is a proxy system,run [run.py](https://github.com/XuTan/WeiBo_Crawler/blob/master/WeiBoPlatform/run.py) to load proxypool.
+ [user_crawler](https://github.com/XuTan/WeiBo_Crawler/tree/master/WeiBoPlatform/user_crawler) includes scripts to crawl topic keyword user info,and the userinfo saved in [tmp_topicuser](https://github.com/XuTan/WeiBo_Crawler/tree/master/WeiBoPlatform/tmp_topicuser) in JSON files.
+ [weibo_crawler](https://github.com/XuTan/WeiBo_Crawler/tree/master/WeiBoPlatform/weibo_crawler) includes scripts to crawl users' weibo data,these information also saved in [tmp_weibo](https://github.com/XuTan/WeiBo_Crawler/tree/master/WeiBoPlatform/tmp_weibo).
+ run [kw.py](https://github.com/XuTan/WeiBo_Crawler/blob/master/WeiBoPlatform/kw.py) to start the sina weibo crawler.
### WeiBoSite
#### using Django2.0,postgresql 10,django-haystack and jieba to create simple crawler data display web site.
