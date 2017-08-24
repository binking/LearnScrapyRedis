#-*_coding:utf8-*-
import time
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy.http import Request
from daomubiji.items import DaomubijiItem
from utils import get_now

class daomubijiSpider(RedisSpider):
    name = "daomubijiSpider"
    redis_key = 'daomubijiSpider:start_urls'
    start_urls = ['http://www.daomubiji.com/']

    def parse_content(self,response): # 爬取每一章节的内容
        url_cahracter = response.request.url.split("/")[-1].replace(".html", "")
        content_file = "files/archives/content/daomubiji_content_{ct}_{dt}.html".format(ct=url_cahracter, dt=get_now(tab=False))
        print >>open(content_file, "w"), content_file
        selector = Selector(response)
        chapter_content = selector.xpath('//article[@class="article-content"]/p/text()').extract()
        item = response.meta['item']
        item['content'] = '\n'.join(chapter_content)
        yield item
        # time.sleep(2)

    def parse_title(self,response): # 提取子网页信息
        # Save raw data to Archive
        url_cahracter = response.request.url.split("/")[-1]
        chapter_file = "files/archives/chapter_index/daomuji_chapter_index_{ct}_{dt}.html".format(ct=url_cahracter, dt=get_now(tab=False))
        print >>open(chapter_file, "w"), response.body

        selector = Selector(response)

        book_order_name = selector.xpath('//h1/text()').extract()[0]
        pos = book_order_name.find(u'：')
        book_order = book_order_name[:pos] # 获取书编号
        book_name = book_order_name[pos + 1:] # 获取书名

        chapter_list = selector.xpath('//article[@class="excerpt excerpt-c3"]//text()').extract()
        chapter_link = selector.xpath('//article[@class="excerpt excerpt-c3"]/a/@href').extract()
        chapter_link_flag = 0 # 链接序号
        for each in chapter_list:
            pos_first = each.find(' ')
            pos_last = each.rfind(' ')
            # chapter_first = ''
            chapter_mid = ''
            # chapter_last = ''
            if pos_first != pos_last:
                chapter_first = each[:pos_first]
                chapter_mid = each[(pos_first + 1): pos_last]
                chapter_last = each[pos_last + 1:]
            else:
                chapter_first = each[:pos_first]
                chapter_last = each[pos_last + 1:]

            # 存储信息
            item = DaomubijiItem()
            item['bookOrder'] = book_order
            item['bookName'] = book_name
            item['chapterFirst'] = chapter_first
            item['chapterMid'] = chapter_mid
            item['chapterLast'] = chapter_last
            yield Request(chapter_link[chapter_link_flag], callback='parse_content', meta={'item':item})
            chapter_link_flag += 1
            # time.sleep(2)

    def parse(self, response): # 程序从这个函数开始执行
        book_file = "files/archives/daomubiji_book_index_{dt}.html".format(dt=get_now(tab=False))
        print >>open(book_file, "w"), response.body
        selector = Selector(response)
        book_filed = selector.xpath('//article/div')
        # 抓取书标题: <div class="homebook">
        book_link = selector.xpath('//article/p/a/@href').extract()
        # 抓取盗墓笔记每本书的链接: <p><a href="http://www.daomubiji.com/dao-mu-bi-ji-1"></p>
        # '//article/p/a/@href'也可以写成('//article//@href')

        link_flag = 0
        for each in book_filed:
            book_name_title = each.xpath('h2/text()').extract()[0]
            pos = book_name_title.find(u'：')  # like 盗墓笔记1：七星鲁王宫
            if pos == -1: # 只抓取符合我们格式规定的书
                continue
            yield Request(book_link[link_flag], callback='parse_title') # 调用parse_title函数
            link_flag += 1  # next page
            # time.sleep(2)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        from_crawler = super(daomubijiSpider, cls).from_crawler
        spider = from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.idle, signal=scrapy.signals.spider_idle)
        return spider

    def idle(self):
        # import ipdb; ipdb.set_trace()
        # if self.q.llen(self.redis_key) <= 0:
        if self.server.zcard("daomubijiSpider:requests") <= 0:
            self.crawler.engine.close_spider(self, reason='No more items in redis queue')