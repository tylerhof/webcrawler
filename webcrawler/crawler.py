import re

from exceptionhandling.exception_handler import ExceptionHandler, Unwrap, Safe
from exceptionhandling.functor import Functor
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.signalmanager import dispatcher
from scrapy import signals, Request
from scrapy_playwright.page import PageMethod
from w3lib.url import url_query_cleaner
from scrapy.linkextractors import LinkExtractor

from webcrawler.utils import GetDomain


class Scrapy(Functor):

    def __init__(self, settings={'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
                                 'DOWNLOAD_HANDLERS': {
                                     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                                     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler", }},
                 policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.process = CrawlerProcess(settings)

    def apply(self, input, **kwargs):
        results = set()

        def crawler_results(signal, sender, item, response, spider):
            [results.add(link) for link in item['links']]

        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        if hasattr(input, '__iter__'):
            [self.process.crawl(spider) for spider in input]
        else:
            self.process.crawl(input)

        self.process.start()
        return list(results)


def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link


class CrawlSpiderSupplier(Functor):

    def __init__(self, parse_links_getter=None, policy: ExceptionHandler = Unwrap()):
        super().__init__(policy)
        if parse_links_getter:
            self.parse_links_getter = parse_links_getter
        else:
            self.parse_links_getter = self.default_parse_links_getter

    def default_parse_links_getter(self, input, **kwargs):
        link_extractor = self.get_link_extractor(input, **kwargs)
        return lambda self, response: {'url': response.url,
                                       'body': response.body,
                                       'links': [link.url for link in link_extractor.extract_links(response)]}

    def get_link_extractor(self, input, **kwargs):
        if 'allow' in kwargs:
            return LinkExtractor(allow=kwargs['allow'])
        else:
            return LinkExtractor(allow=[re.escape(kwargs['allowed_domains'][0])])

    def apply(self, input, **kwargs):
        link_extractor = self.get_link_extractor(input, **kwargs)
        parse_links = self.parse_links_getter(input, **kwargs)
        return type("AnonymousSpiderClass",
                    (CrawlSpider,),
                    {'name': kwargs['name'],
                     'allowed_domains': kwargs['allowed_domains'],
                     'start_urls': kwargs['start_urls'],
                     'rules': (Rule(link_extractor,
                                    process_links=process_links,
                                    callback='parse_item',
                                    follow=True),),
                     'parse_item': parse_links,
                     'custom_settings': {'DOWNLOAD_DELAY': 2,
                                         'RANDOMIZE_DOWNLOAD_DELAY': False,
                                         }
                     })

class WebCrawler(Functor):

    def __init__(self, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.get_domain = GetDomain()
        self.spider_supplier = CrawlSpiderSupplier()
        self.scrapy = Scrapy()

    def apply(self, input, **kwargs):
        domain = self.get_domain(input)
        if domain.is_ok():
            return self.apply_from_domain(domain.value, input)
        else:
            return domain

    def apply_from_domain(self, domain, input):
        spider = self.spider_supplier({'name': domain,
                                       'start_urls': [input],
                                       'allowed_domains': [domain]})
        return self.scrapy(spider)
