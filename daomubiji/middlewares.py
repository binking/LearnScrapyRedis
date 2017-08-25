# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

from scrapy import signals
from scrapy.conf import settings
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
from scrapy.utils.response import response_status_message


def CustomRetryMidlleware(RetryMiddleware):
    """
    Buddy, you must understand when to retry:
        1. Wrong Http code: retry and change abuyun channel;
        2. Wrong Html content
        3. 
    :param RetryMiddleware: 
    :return: 
    """
    pass


class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        # if item got wrong
        if response.status == 200 and response.xpath(spider.retry_xpath):  # if can't get the correct xpath
            return self._retry(request, 'response got xpath "{}"'.format(spider.retry_xpath), spider) or response
        return response


class RandomUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        ua = random.choice(settings['USER_AGENTS'])
        request.headers.setdefault('User-Agent', ua)

class AbuyunProxyMiddleware(HttpProxyMiddleware):
    def process_request(self, request, spider):
        request.meta["proxy"] = settings['proxyServer']
        request.headers["Proxy-Authorization"] = settings['proxyAuth']


class DaomubijiSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
