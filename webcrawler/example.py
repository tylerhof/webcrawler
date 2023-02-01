import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from webcrawler.crawler import CrawlSpiderSupplier, Scrapy, WebCrawler


def process_links(links):
    for link in links:
        link.url = url_query_cleaner(link.url)
        yield link

class ImdbCrawler(CrawlSpider):
    name = 'test'
    allowed_domains = ['www.citadel.com']
    start_urls = ['https://www.citadel.com/careers/open-opportunities/investing/',
                  'https://www.citadel.com/careers/open-opportunities/engineering/',
                  'https://www.citadel.com/careers/open-opportunities/quantitative-research/',
                  'https://www.citadel.com/careers/open-opportunities/business-operations/']
    rules = (
        Rule(
            LinkExtractor(
                allow=[re.escape('www.citadel.com/careers/details/')],
            ),
            process_links=process_links,
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        return {
            'url': response.url,
            'body': response.body
        }

web_crawler = Scrapy()
supplier = CrawlSpiderSupplier()

test_spider = supplier({'name' : 'test',
                        "allowed_domains" : ["webscraper.io"],
                        "start_urls" : ["https://webscraper.io/test-sites/e-commerce/allinone"]})
citadel_spider = supplier({'name' : 'citadel',
                           "allowed_domains" : ['www.citadel.com'],
                           "start_urls" : ['https://www.citadel.com/careers/open-opportunities/investing/',
                                           'https://www.citadel.com/careers/open-opportunities/engineering/',
                                           'https://www.citadel.com/careers/open-opportunities/quantitative-research/',
                                           'https://www.citadel.com/careers/open-opportunities/business-operations/']})

citadel_spider2 = supplier({'name' : 'citadel',
                           "allowed_domains" : ['www.citadel.com'],
                           "start_urls" : ['https://www.citadel.com/careers/open-opportunities/']})

#results = web_crawler([citadel_spider])

test = WebCrawler()
results = test('https://webscraper.io/test-sites/e-commerce/allinone')
k = 2