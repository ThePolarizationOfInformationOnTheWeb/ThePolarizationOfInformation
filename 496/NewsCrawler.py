import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor

class NewsSpider(CrawlSpider):
    name = 'google_news'

    def __init__(self, topic: str):
        super().__init__()
        assert topic is not None, "topic is None"
        self.topic = topic

    def start_requests(self):
        request_url = "https://news.google.com/search?q="
        topic_words = self.topic.split()

        for i, word in enumerate(topic_words):
            if i is not len(topic_words) - 1:
                request_url = request_url + word + "%20"
            else:
                request_url = request_url + word + "&hl=en-US&gl=US&ceid=US%3Aen"

        yield scrapy.Request(request_url, self.parse_google_news_home)

    def parse_google_news_home(self, response):
        articles = response.xpath('//article')

        prefix = 'https://news.google.com/'

        for article_link in articles:
            scrapy.Request(prefix + article_link.xpath('.//a/@href')[0].get(), self.parse_news_article)

    def parse_news_article(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['name'] = response.xpath('//td[@id="item_name"]/text()').get()
        item['description'] = response.xpath('//td[@id="item_description"]/text()').get()
        return item