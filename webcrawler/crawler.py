import re

from exceptionhandling.exception_handler import ExceptionHandler, Unwrap, Safe
from exceptionhandling.functor import Functor
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.signalmanager import dispatcher
from scrapy import signals
from w3lib.url import url_query_cleaner
from scrapy.linkextractors import LinkExtractor

from webcrawler.utils import GetDomain


class Scrapy(Functor):

    def __init__(self, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})

    def apply(self, input):
        results = []
        def crawler_results(signal, sender, item, response, spider):
            results.append(item)

        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        if hasattr(input, '__iter__'):
            [self.process.crawl(spider) for spider in input]
        else:
            self.process.crawl(input)
            
        self.process.start()
        return results

def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link

class CrawlSpiderSupplier(Functor):

    def __init__(self, policy: ExceptionHandler = Unwrap()):
        super().__init__(policy)

    def apply(self, input):
        link_extractor = LinkExtractor(
                        allow=[re.escape(input['allowed_domains'][0])])
        return type("AnonymousSpiderClass",
                    (CrawlSpider,),
                    {'name' : input['name'],
                    'allowed_domains' : input['allowed_domains'],
                    'start_urls' : input['start_urls'],
                    'rules' : (Rule(link_extractor,
                        process_links=process_links,
                        callback='parse_item',
                        follow=True),),
                     'parse_item': (lambda self, response: {'url': response.url,
                                                            'body': response.body,
                                                            'links': [link.url for link in link_extractor.extract_links(response)]}),
                     'custom_settings' : {'DOWNLOAD_DELAY': 2,
                                           'RANDOMIZE_DOWNLOAD_DELAY': False,
                                          }
                    })

class WebCrawler(Functor):

    def __init__(self, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.get_domain = GetDomain()
        self.spider_supplier = CrawlSpiderSupplier()
        self.scrapy = Scrapy()

    def apply(self, input):
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