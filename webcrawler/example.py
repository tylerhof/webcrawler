import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.url import url_query_cleaner

from webcrawler.crawler import CrawlSpiderSupplier, Scrapy, WebCrawler
from webcrawler.utils import GetDomain

web_crawler = Scrapy()

parse_links = lambda input_dict: lambda self, response: {'url': response.url,
                            'body': response.body,
                            'links': [link.url for link in LinkExtractor(allow=[re.escape(input_dict['allowed_domains'][0])]).extract_links(response)]}

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
domain_getter = GetDomain()

jane_street_spider = supplier({'name' : 'jane',
                               "allowed_domains" : [domain_getter('https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates').value],
                               "start_urls" : ['https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates',]})

test_spider = supplier({'name' : 'test',
                        "allowed_domains" : ["webscraper.io"],
                        "start_urls" : ["https://webscraper.io/test-sites/e-commerce/allinone"]})

results = web_crawler([jane_street_spider])

results = web_crawler([citadel_spider])