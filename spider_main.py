#!/usr/bin/env python
#coding:utf-8

import url_manager,html_downloader,html_outputer,\
    html_parser

class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()

    # 爬虫的调度程序.
    def craw(self, root_url):
        count = 1
        self.urls.add_new_url(root_url)
        while self.urls.has_new_url():
            try:
                new_url = self.urls.get_new_url()
                print "craw %d : %s" % (count, new_url)
                html_cont = self.downloader.download(new_url)    # 从url获取到该网页内容.
                new_urls, new_data = self.parser.parse(new_url, html_cont)
                self.urls.add_new_urls(new_urls)
                self.outputer.collect_data(new_data)
                #爬取到有1000个词条就break
                if count == 300:
                    break
                count = count + 1
            except Exception as e:
                print "craw failed : ", e
        # 将收集的数据输出,我在这里顺便下载图片到web服务器.
        # 将根据电影名称获取到电影下载地址.
        self.outputer.output_html()
        # print self.urls.old_urls
        # set -> str : ''.join(c)
        str_old_urls = "\n".join(self.urls.old_urls)
        # 保存自己已经爬取的url,方便下次爬取的url不会重复.
        with open("urls.txt", "w") as f:
            f.write(str_old_urls)
        
if __name__ == '__main__':
    # 爬取入口url
    root_url = "https://movie.douban.com/subject/26844922/"
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)  