#!/usr/bin/env python
#coding:utf-8

from bs4 import BeautifulSoup
import re
import urlparse

class HtmlParser(object):
    """
    网页解析
    """
    def _get_new_urls(self, page_url, soup):
        # 爬取到的新的豆瓣电影地址集合
        new_urls = set()
        # /item/Guido%20van%20Rossum
        # https://movie.douban.com/subject/1308587/?from=subject-page
        links = soup.find_all("a", href=re.compile(r"https://movie.douban.com/subject/\w+/\?from=subject-page"))
        for link in links:
            new_url = link['href']    #获取到后半段的地址
            new_url = new_url.split("?")[0]
            new_urls.add(new_url)
        return new_urls

    def _get_new_data(self, page_url, soup):
        res_data = {}
        # 电影信息节点.
        info_node = soup.find("div", id="info")
        info_str = info_node.get_text().encode("utf-8").strip()
        info_list = info_str.split("\n")

        # url
        res_data["douban_link"] = page_url

        # 名字.<span property="v:itemreviewed">云水谣</span>
        movie_name = soup.find("span", property="v:itemreviewed").get_text()
        movie_name_list = movie_name.split(" ")
        print "电影名称 : ", movie_name_list[0]
        res_data["movie_name"] = movie_name_list[0]

        # 评分.<strong class="ll rating_num" property="v:average">6.9</strong>
        douban_score = soup.find("strong", class_="ll rating_num", property="v:average").get_text()
        print "评分 : ", douban_score
        res_data["douban_score"] = douban_score

        # 豆瓣评分人数.<span property="v:votes">85435</span>
        douban_counter = soup.find("span", property="v:votes").get_text()
        print "豆瓣评分人数 : ",douban_counter
        res_data["douban_counter"] = douban_counter

        # Imdb链接
        imdb_link_node = soup.find("a", href=re.compile(r"http://www.imdb.com/title/\w+"))
        if imdb_link_node != None:
            imdb_link = imdb_link_node["href"]
            print "Imdb链接 : ", imdb_link
            res_data["imdb_link"] = imdb_link
        else:
            res_data["imdb_link"] = "NULL"

        # 导演.<a href="/celebrity/1276060/" rel="v:directedBy">尹力</a>
        director = soup.find("a", rel="v:directedBy").get_text()
        print "导演 : ", director
        res_data["director"] = director

        # 上映国家.
        tag = 0
        for info in info_list: 
            country = info.split(":")[0].strip()
            if country == "制片国家/地区":
                print "上映国家 : ", info.split(":")[1].strip()
                tag += 1
                res_data["country"] = info.split(":")[1].strip()
        if tag == 0:
             print "上映国家 : 暂时无数据"
             res_data["country"] = "暂时无数据"

        # 上映日期.
        dateyear = soup.find("span", property="v:initialReleaseDate")
        if dateyear == None:
            res_data["dateyear"] = "0000-00-00"
        else:
            print "上映日期 : ", dateyear.get_text()
            res_data["dateyear"] = dateyear.get_text()
            
        # 主演.<a href="/celebrity/1053618/" rel="v:starring">陈坤</a>
        actors = soup.find_all("a", rel="v:starring")
        actor_list = []
        for actor in actors:
            actor_list.append(actor.get_text())
        actor_str = " ".join(actor_list)
        print "主演 : ", actor_str
        res_data["actor"] = actor_str

        # 电影类型.
        style_list_node = info_node.find_all("span", property="v:genre")
        style_list = []
        if len(style_list_node) != 0:
            for style in style_list_node:
                style_list.append(style.get_text())
            style_str = " ".join(style_list)
            print "电影类型 : ", style_str
            res_data["style_str"] = style_str
        else:
            print "电影类型 : 暂时无数据"
            res_data["style_str"] = u"暂时无数据"

        # 图片保存地址.
        # <img src="https://img1.doubanio.com/view/movie_poster_cover/lpst/public/p787214519.webp" 
        # title="点击看更多海报" alt="云水谣" rel="v:image">
        image_name = soup.find("img", rel="v:image")
        image = "/static/movie/img/" + image_name["src"].split("/")[-1]
        print "图片保存地址 : ", image
        print "图片下载地址 : ", image_name["src"]
        res_data["image"] = image
        res_data["image_name"] = image_name["src"]

        return res_data

    def _get_new_data2(self, soup, movie_name):
        """
        获取到电影的编号.
        """
        res_data = {}
        node_list = soup.find_all("dd", class_="lf")
        for node in node_list:
            ch_node = node.find("a", href=re.compile(r"/btdy/\w+.html"))
            style = node.find("span")
            # 判断是不是电影类型
            if "电影" in style.get_text().encode("utf-8"):
                # 判断名字是不是要下载的电影
                if ch_node["title"].encode("utf-8") == movie_name:
                    name = ch_node["href"].split("/")[-1].split(".")[0]
                    res_data["name"] = name[2:]
        # 没有该电影资源或者搜索不到该电影的情况下,字典都为0,就加载为NULL.
        if len(res_data) == 0:
            res_data["name"] = "NULL" 
        return res_data

    def _get_new_data3(self, soup):
        """
        获取到电影的下载地址.
        """
        res_data = {}
        node = soup.find("input", id="text1")
        address = node["value"]
        res_data["address"] = address
        return res_data

    def _get_new_data4(self, soup, movie_name, director):
        """
        获取到电影的播放地址.
        """
        res_data = {}
        node_list = soup.find_all("li", class_="list_item")
        for node in node_list:
            try:
                movie = node["data-widget-searchlist-tvname"]
                name = node.find("a", title=director)
                # 说明导演也对,电影名称也对,这样就排除了同名的电影的情况.
                if name != None:
                    #new_name = name.get_text().encode("utf-8")
                    if node["data-searchpingback-albumname"].encode("utf-8") == movie_name:
                        movie_address = node.find("a", class_="info_play_btn")["href"]
                        print "'{0}'--电影播放地址 : ".format(movie_name), movie_address
                        res_data["movie_address"] = movie_address
            except Exception as e:
                # 出错了继续运行.
                pass 
        if len(res_data) == 0:
            res_data["movie_address"] = "NULL"
            print "'{0}'--没有播放地址！".format(movie_name)
        return res_data
        
    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return
        #html_cont为网页下载器下载的网页内容
        soup = BeautifulSoup(html_cont, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)    #从网页内容上获取到百科链接地址
        new_data = self._get_new_data(page_url, soup)    #从网页内容中获取到标题和简介的数据
        return new_urls, new_data

    def parse2(self, html_content, movie_name):
        """
        第二个网页解析器.返回电影的编号.
        """
        if html_content is None:
            return
        soup2 = BeautifulSoup(html_content, "html.parser", from_encoding="utf-8")
        data = self._get_new_data2(soup2, movie_name)
        return data

    def parse3(self, html_content):
        """
        第三个网页解析器.返回电影的下载地址.
        """
        if html_content is None:
            return
        soup3 = BeautifulSoup(html_content, "html.parser", from_encoding="utf-8")
        data = self._get_new_data3(soup3)
        return data

    def parse4(self, html_content, movie_name, director):
        """
        第四个网页解析器.返回电影的播放地址.
        """
        if html_content is None:
            return
        soup4 = BeautifulSoup(html_content, "html.parser")
        data = self._get_new_data4(soup4, movie_name, director)
        return data