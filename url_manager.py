#!/usr/bin/env python
#coding:utf-8

class UrlManager(object):
    """
    url管理器
    """
    def __init__(self):
        self.new_urls = set()    #待爬取的网页集合
    
        # 从文件中读取已经爬取过的地址,防止再次爬取数据.
        with open("urls.txt", "r") as f:
            self.content = f.read()
        content_list = self.content.split("\n")
        self.old_urls = set(content_list)
        # self.old_urls = set()    #爬取过的网页集合

    def add_new_url(self, url):
        """
        添加url到新的url集合中
        """
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)     

    def add_new_urls(self, urls):
        """
        批量添加url
        """
        if urls is None or len(urls) == 0:
            return 
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        """
        判断是否有新的url
        """
        return len(self.new_urls) != 0

    def get_new_url(self):
        """
        从等待爬取的url集合中提取url
        """
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url