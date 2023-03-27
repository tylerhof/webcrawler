import re
from scrapy.linkextractors import LinkExtractor

from webcrawler.crawler import CrawlSpiderSupplier, Scrapy
from webcrawler.utils import GetDomain, GetRestJson, PostRestJson

web_crawler = Scrapy(settings={'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
                               'DOWNLOAD_HANDLERS': {
                                   "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                                   "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"},
                               'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
                               'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 90000,
                               'DEPTH_LIMIT' : 1})

parse_links = lambda input_dict: lambda self, response: {'url': response.url,
                                                         'body': response.body,
                                                         'links': [link.url for link in LinkExtractor(allow=[re.escape(
                                                             input_dict['allowed_domains'][0])]).extract_links(
                                                             response)]}

supplier = CrawlSpiderSupplier()

#citadel_spider = supplier(None, name='citadel',
#                          allowed_domains=['www.citadel.com'],
#                          start_urls=['https://www.citadel.com/careers/open-opportunities/investing/',
#                                      'https://www.citadel.com/careers/open-opportunities/engineering/',
#                                      'https://www.citadel.com/careers/open-opportunities/quantitative-research/',
#                                      'https://www.citadel.com/careers/open-opportunities/business-operations/'])

domain_getter = GetDomain()

rest_getter = GetRestJson()

jane_street = rest_getter('https://www.janestreet.com/jobs/main.json')
# mlp = rest_getter('https://corsanywhere-mlp.herokuapp.com/https://wd5-services1.myworkday.com/ccx/service/customreport2/mlp/ISU_Sullivan_JobPostings/INT_External_Job_Postings_RaaS?format=json',
#                  headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0',
#                           'Origin': 'https://www.mlp.com',
#                           'Authorization': 'Basic SVNVX1N1bGxpdmFuX0pvYlBvc3RpbmdzOjVjWWJzVDZVT0dTZFZwY3dnanpW'})

rest_poster = PostRestJson()
#man_ahl = rest_poster('https://mangroupplc.wd3.myworkdayjobs.com/wday/cxs/mangroupplc/Man_Group_Careers/jobs',
#            data='{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}',
#                      headers={'Content-Type': 'application/json'})


jane_street_spider = supplier(None,
                              name='jane',
                              allowed_domains=[domain_getter(
                                  'https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates').value,
                                               domain_getter(
                                                   'https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates').value],
                              start_urls=[
                                  'https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates', ])

capula_spider = supplier(None,
                       name='capula',
                       allowed_domains=['fsr.cvmailuk.com'],
                       start_urls=['https://fsr.cvmailuk.com/capula/main.cfm'],
                       allow=[r'jobSpecific&jobId'])

citadel_spider = supplier(None, name='citadel',
                          allowed_domains=['www.citadel.com'],
                          start_urls=['https://www.citadel.com/careers/open-opportunities/investing/'])

results = web_crawler([citadel_spider])

k = 2

#results = web_crawler([jane_street_spider])


test_spider = supplier(None, name='test',
                       allowed_domains=[domain_getter('http://quotes.toscrape.com/author/Albert-Einstein/').value],
                       start_urls=["http://quotes.toscrape.com/author/Albert-Einstein/"])

#results = web_crawler([capula_spider])
k = 2