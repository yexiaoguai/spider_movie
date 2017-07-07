#!/usr/bin/env python
#coding:utf-8

import urllib2, requests

from contextlib import closing

class HtmlDownloader(object):
    """
    网页下载器
    """   
    def download(self, url):
        if url is None:
            return None
        request = urllib2.Request(url)
        request.add_header("user-agent", "Mozilla/5.0")
        response2 = urllib2.urlopen(request)   
        #response = urllib2.urlopen(url)       
        if response2.getcode() != 200:
            return None
        return response2.read()

    def download_image(self, url, filename):
        """
        下载图片
        """
        if url is None:
            return None
        with closing(requests.get(url, stream=True)) as response:
            with open(filename, "wb") as fd: 
                #每128写入一次
                for chunk in response.iter_content(128):
                    fd.write(chunk)

    def requests_download(self, url):
        """
        用requests获取网页内容.
        """
        html_bytes = requests.get(url)
        return html_bytes.content