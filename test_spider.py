import scrapy
from scrapy.crawler import CrawlerProcess


class FirstSpider(scrapy.Spider):
    name = 'first_spider'
    custom_settings = {'DOWNLOD_DELAY': 1}
    start_urls = ['https://www.hardmob.com.br/forums/407-Promocoes']


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(FirstSpider)
    process.start()
