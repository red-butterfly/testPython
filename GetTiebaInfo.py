#!/usr/bin/python 
# -*- coding: UTF-8 -*-
__author__ = 'hanfei'
"""根据输入的贴吧代码，获取贴吧的信息并写入贴吧同名的文件中
@version:1.0
@author:hanfei<hanfei1009@126.com>
"""

import urllib
import urllib2
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

class GetBDTB:
    def __init__(self,baseurl,seelz):
        self.baseurl = baseurl
        self.seelz = '?see_lz=' + str(seelz)
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36'}
        self.tool = Tool()
        self.file = None
        self.fileTitle = u'百度贴吧'

    def getTBinfo(self,pageNum):
        """
        通过输入的页码，获取该页码的html网页
        :param pageNum: 贴吧的页码
        :return:输入页码的html网页
        """
        try:
            url = self.baseurl + self.seelz + '&pn=' + str(pageNum)
            resquet = urllib2.Request(url)
            response = urllib2.urlopen(resquet)

            pageCode = response.read()
            return pageCode
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print "Get the TieBa %s error reason: %s" % (url,e.reason)
                return None

    def getTitle(self,page):
        """
        获取该贴吧的贴吧名称
        :param page: 页面内容
        :return:贴吧的名称
        """
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
        title = re.search(pattern,page)
        if title:
            return title.group(1).strip().decode('utf-8','ignore')
        else:
            print None

    def getPageNumber(self,page):
        """
        获取输入贴吧总共页数
        :param page: 页面内容
        :return:贴吧的总页数
        """
        #pattern = re.compile('<li class="l_reply_num.*?>.*?</span>.*?<span class="red">(.*?)</span>.*?</li>',re.S)

        pattern = re.compile('<li class="l_reply_num.*?><span .*?>.*?</span>.*?<span.*?>(.*?)</span>',re.S)
        result = re.search(pattern,page)
        if result:
            return result.group(1).strip()
        else:
            print None

    def setfileTitle(self,title):
        """
        设置保存文件的文件名
        :param title: 贴吧名称
        :return:文件句柄
        """
        if title is not None:
            self.file = open(title+".txt","w+")
        else:
            self.file = open(self.fileTitle+".txt","w+")

    def getContent(self,page):
        """
        获取需要写入文件的贴吧的各种信息，包括楼层号、作者、发帖时间、发帖的内容
        :param page: 页面内容
        :return:需要写入的数据
        """
        pattern = re.compile('<div class="d_author">.*?<ul class="p_author">.*?<a data-field=.*?>(.*?)</a>.*?</ul>.*?</div>.*?<div id="post_content_.*?>(.*?)</div>.*?<div class="post-tail-wrap">.*?<span class="tail-info">(.*?)楼</span><span class="tail-info">(.*?)</span></div>',re.S)
        items = re.findall(pattern,page)
        contentinfo = []
        for item in items:
            if item:
                #print '%s楼 --- %s ----- %s -----------------------------------------------------------------\n' % (self.tool.replace(item[2]).decode('utf-8','ignore'),item[0].decode('utf-8','ignore'),item[3].decode('utf-8','ignore'))
                content = "\n" + self.tool.replace(item[1]).decode('utf-8','ignore') + "\n"
                contentinfo.append([self.tool.replace(item[2]).decode('utf-8','ignore'),item[0].decode('utf-8','ignore'),item[3].decode('utf-8','ignore'),content])

        return contentinfo

    def writeData(self,content):
        """
        将数据写入文件中
        :param content:需要写入的数据
        :return:无
        """
        for item in content:
            self.file.write("\n" + item[0] + u"楼---" + item[1] + u"---" + item[2] + u"-----------------------------------\n")
            self.file.write(item[3])

    def start(self):
        indexPage = self.getTBinfo(1)
        pageNum = self.getPageNumber(indexPage)
        title = self.getTitle(indexPage)
        self.setfileTitle(title)
        if pageNum == None:
            print u"URL已经失效，请重新输入"
            return
        else:
            try:
                print u"该帖子共有" + str(pageNum) + u"页"
                for i in range(1,int(pageNum)+1):
                    print u"正在写入第" + str(i) + u"页数据"
                    page = self.getTBinfo(i)
                    content = self.getContent(page)
                    self.writeData(content)
            except IOError,e:
                print u"写入异常" + e.message
            finally:
                print u"写入完成"


print u"请输入帖子代号"
baseUrl = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
print u"请输入是否只看楼主：是请输入1，否请输入0"
seelz = raw_input()
teiba = GetBDTB(baseUrl,seelz)
teiba.start()
