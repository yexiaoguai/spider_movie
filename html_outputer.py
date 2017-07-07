#!/usr/bin/env python
#coding:utf-8

import html_downloader, html_parser

class HtmlOutputer(object):
    def __init__(self):
        self.datas = []
        self.downloader_image = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()

    def collect_data(self, data):
        """
        收集数据
        """
        if data is None:
            return
        self.datas.append(data)

    def output_html(self):
        # (245,'海豚湾','https://movie.douban.com/subject/3442220/','9.3',159504,
        # 'http://www.thecovemovie.com','NULL','NULL','NULL','NULL','NULL','美国','2009-07-31(美国)',
        # 'John·Chisholm Mandy-Rae·Cruikshank Charles·Hambleton Simon·Hutchins Kirk·Krack 伊莎贝尔·卢卡斯 Richard·O\'Barry 海顿·潘妮蒂尔 路易·西霍尤斯','路易·西霍尤斯','纪录片',
        # 'http://www.bilibili.com/video/av5383247/',
        # 'magnet:?xt=urn:btih:5c0ad2fa227e1b2a6a433498be4d80016732bf5e','NULL','4',1,'/static/movie/img/p455222172.jpg','NULL','NULL','NULL','NULL','NULL','NULL')
        # (246,'云水谣','https://movie.douban.com/subject/1949811/','6.9',85441,
        # 'http://www.imdb.com/title/tt0924003','NULL','NULL','NULL','NULL','NULL','中国大陆 / 台湾','2006-12-01(中国大陆)',
        # '陈坤 徐若瑄 李冰冰 归亚蕾 秦汉 梁洛施 朱茵 张致恒','尹力','剧情  爱情  战争',
        # 'NULL',
        # 'NULL','NULL','4',1,'/static/movie/img/p787214519.jpg','NULL','NULL','NULL','NULL','NULL','NULL')
        id = 4413
        for data in self.datas:
            id = id + 1
            
            # 得到文件名.
            new_image = data["image"].split("/")[-1]
            # 图片存放地址.
            filename = "/home/yeliang/movie/img/{0}".format(new_image)
            # 下载图片.
            self.downloader_image.download_image(data["image_name"], filename)

            # 获取电影下载地址.
            try:
                movie_download_address = "http://www.btbtdy.com/search/{0}.html".format(data["movie_name"].encode("utf-8"))
                content = self.downloader_image.download(movie_download_address)
                if content == None:
                    print "'{0}'--电影下载资源网络无法访问！".format(data["movie_name"].encode("utf-8"))
                    data["download_link"] = 'NULL'
                else:
                    address_data = self.parser.parse2(content, data["movie_name"].encode("utf-8"))
                    if address_data["name"] == "NULL":
                        print "'{0}'--没有该电影资源！".format(data["movie_name"].encode("utf-8"))
                        data["download_link"] = 'NULL'
                    else:
                        new_url = "http://www.btbtdy.com/down/{0}-0-0.html".format(address_data["name"])
                        content2 = self.downloader_image.download(new_url)
                        address_data2 = self.parser.parse3(content2)
                        print "'{0}'--电影下载地址 : ".format(data["movie_name"].encode("utf-8")), address_data2["address"]
                        data["download_link"] = address_data2["address"]
            except Exception as e:
                data["download_link"] = 'NULL'
                print "获取电影下载地址失败 : ", e

            # 获取电影播放地址.
            movie_address_url = "http://so.iqiyi.com/so/q_{0}".format(data["movie_name"].encode("utf-8"))
            movie_address_content = self.downloader_image.requests_download(movie_address_url)
            movie_address_data = self.parser.parse4(movie_address_content, data["movie_name"].encode("utf-8"), data["director"].encode("utf-8"))
            data["movie_address"] = movie_address_data["movie_address"]
            
            # 得到的数据进行保存.
            str_movie = "({0},'{1}','{2}','{3}',{4},\n'{5}','NULL','NULL','NULL','NULL','NULL','{6}','{7}',\n'{8}','{9}','{10}',\n'{13}',\n'{12}','NULL','4',1,'{11}','NULL','NULL','NULL','NULL','NULL','NULL'),\n"\
                .format(id, data["movie_name"].encode("utf-8"), data["douban_link"], data["douban_score"], 
                        data["douban_counter"], data["imdb_link"], data["country"], data["dateyear"].encode("utf-8"),
                        data["actor"].encode("utf-8"), data["director"].encode("utf-8"), data["style_str"].encode("utf-8"), data["image"],
                        data["download_link"], data["movie_address"])
            with open("sql_movie.txt", "a") as f:
                f.write(str_movie)