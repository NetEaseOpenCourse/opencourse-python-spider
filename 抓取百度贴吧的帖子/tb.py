# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import thread
import time

#处理页面标签类
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

 
#百度贴吧爬虫类
class BDTB:
 
    #初始化，传入基地址，是否只看楼主的参数
    def __init__(self,baseUrl,seeLZ,floorTag):
        self.baseURL = baseUrl
        self.seeLZ = '?see_lz='+str(seeLZ)
        self.tool = Tool()
        self.file = None
        self.defaultTitle = u"百度贴吧"
        self.floorTag = floorTag
        self.floor = 1
 
    #传入页码，获取该页帖子的代码
    def getPage(self,pageNum):
        try:
            url = self.baseURL+ self.seeLZ + '&pn=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')
            return pageCode
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接百度贴吧失败,错误原因",e.reason
                return None

    #获取帖子标题
    def getTitle(self,page):
        page = self.getPage(1)
        if not page:
            print "page load error"
            return None

        pattern = re.compile(r'<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
        result = re.search(pattern,page)
        if result:
            print result.group(1)  #测试输出
            return result.group(1).strip()
        else:
            return None

    # 获取帖子一共有多少页
    def getPageNum(self,page):
        page = self.getPage(1)
        pattern = re.compile(r'<li class="l_reply_num.*?</span>(.*?)<span.*?>(.*?)</span>(.*?)</li>',re.S)
        result = re.search(pattern,page)
        if result:
            print result.group(1),result.group(2),result.group(3) #测试输出
            return result.group(2).strip()
        else:
            return None

    #获取每一层楼的内容,传入页面内容
    def getContent(self,page):
        pattern = re.compile(r'<div id="post_content_.*?>(.*?)</div>',re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            #将文本进行去除标签处理，同时在前后加入换行符
            content = "\n"+self.tool.replace(item)+"\n"
            contents.append(content.encode('utf-8'))

        return contents

    def setFileTitle(self,title):
            #如果标题不是为None，即成功获取到标题
            if title is not None:
                self.file = open(title + ".txt","w+")
            else:
                self.file = open(self.defaultTitle + ".txt","w+")

    def writeData(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            if self.floorTag == '1':
                print "正在写入第%s楼" %(str(self.floor))
                #楼之间的分隔符
                floorLine = "\n" + str(self.floor) + u"-----------------------------------------------------------------------------------------\n"
                self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        title = self.getTitle(indexPage)
        pageNum = self.getPageNum(indexPage)
        self.setFileTitle(title)

        if pageNum == None:
            print "URL已失效，请重试"
            return
        try:
            for i in range(1,int(pageNum)+1):
                print "正在写入第" + str(i) + "页数据"
                page = self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        # 出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message
        finally:
            print "写入任务完成"


baseURL = 'http://tieba.baidu.com/p/5176659692'
# print u"请输入帖子代号"
# baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
# seeLZ = raw_input("是否只获取楼主发言，是输入1，否输入0\n")
# floorTag = raw_input("是否写入楼层信息，是输入1，否输入0\n")
bdtb = BDTB(baseURL,'1','1')
bdtb.start()
# print u"请输入帖子代号"
# baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
# seeLZ = raw_input("是否只获取楼主发言，是输入1，否输入0\n")
# floorTag = raw_input("是否写入楼层信息，是输入1，否输入0\n")
# bdtb = BDTB(baseURL,seeLZ,floorTag)
# bdtb.start()

