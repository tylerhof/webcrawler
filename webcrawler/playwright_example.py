import scrapy
from scrapy.linkextractors import LinkExtractor

from webcrawler.crawler import CrawlSpiderSupplier, Scrapy
from webcrawler.utils import GetDomain

optiver_url = 'https://optiver.com/working-at-optiver/career-opportunities/'

link_extractor = LinkExtractor(allow=['https://optiver.com/working-at-optiver/career-opportunities/'],
                               deny=['https://optiver.com/working-at-optiver/career-opportunities/#roles'])

async def parse(response):
    page = response.meta["playwright_page"]
    page.set_default_timeout(1000)
    try:
        while button := page.locator('xpath=//a[@title="Load more"]'):
            await button.click(timeout=5000)
            # page.wait_for_timeout(1000)
    except Exception as exc:
        pass
    content = await page.content()
    final_response = response.replace(body=content)
    links = link_extractor.extract_links(final_response)
    yield {'url': final_response.url,
           'body': final_response.body,
           'links': [link.url for link in links if link.url != 'https://optiver.com/working-at-optiver/career-opportunities/']}


def start_requests(self):
    for url in self.start_urls:
        yield scrapy.Request(
            url=url,
            meta=dict(
                playwright=True,
                playwright_include_page=True),
            callback=parse,
        )


web_crawler = Scrapy(settings={'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
                               'DOWNLOAD_HANDLERS': {
                                   "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                                   "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"},
                               'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
                               'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 90000,
                               'DEPTH_LIMIT': 1})
supplier = CrawlSpiderSupplier()
spider = supplier(None, name='optiver',
                  allowed_domains=[GetDomain()('https://optiver.com/working-at-optiver/career-opportunities/').value],
                  start_urls=['https://optiver.com/working-at-optiver/career-opportunities/', ],
                  start_requests=start_requests)

results = web_crawler(spider, start_requests=start_requests)
k = 2

# with sync_playwright() as playwright:
#     browser = playwright.chromium.launch(headless=True)
#     page = browser.new_page()
#     page.goto('https://optiver.com/working-at-optiver/career-opportunities/')
#
#     # Wait for the alert to appear
#     page.wait_for_selector('xpath=//a[@title="Load more"]').click()
#     alert = page.get_alert_box()
#
#     # Accept the alert
#     alert.accept()
