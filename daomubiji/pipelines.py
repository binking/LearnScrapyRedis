# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
from scrapy.conf import settings
import pymongo


class DaomubijiPipeline(object):
    def __init__(self):
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbName = settings['MONGODB_DBNAME']
        self.fw = open("files/results/daomubiji.csv", "w")
        # client = pymongo.MongoClient(host=host, port=port)
        # tdb = client[dbName]
        # self.post = tdb[settings['MONGODB_DOCNAME']]

    def process_item(self, item, spider):
        bookInfo = dict(item)
        # self.post.insert(bookInfo)
        for k, v in bookInfo.items():
            print k, v
        return item

class CsvPipeline(object):
    def __init__(self):
        self.fw = codecs.open("files/results/daomubiji.json", "w", encoding="utf-8")  # save into csv files
        self.fw.write("{\n")

    def __del__(self):
        self.fw.write("\n}")
        print "Closd result file pointer."
        self.fw.close()

    def process_item(self, item, spider):
        book_info = dict(item)
        line = "{"
        for k ,v in book_info.items():
            line += '"%s":"%s",' % (k, v)
        line += "},\n"
        self.fw.write(line)


class CloseSpiderPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.redis_db = None
        self.redis_len = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.redis_len = len(spider.server.keys('daomubijiSpider:requests'))  # daomubijiSpider:requests
        print "Hey: %d" % self.redis_len
        print "="* 100
    def process_item(self, item, spider):
        self.redis_len -= 1
        if self.redis_len <= 0:
            self.crawler.engine.close_spider(spider, 'No more items in redis queue')

        return item