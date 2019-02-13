# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from scrapy.spiders import CrawlSpider
import re
from newspaper import Article


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

        prefix = 'https://news.google.com'

        # for article_link in articles:
        #     article = article_link.xpath('.//a/@href')[0].get()
        #     article = article[1:]
        #     yield scrapy.Request(prefix + article, self.parse_news_article)

        article = articles[3].xpath('.//a/@href')[0].get()
        article = article[1:]
        print(prefix + article)

        return scrapy.Request(prefix + article, callback=self.parse_news_article)

    def parse_news_article(self, response):
        #use newspaper to download and parse article
        article_name = Article(response.url, language='en')
        article_name.download()
        article_name.parse()

        # here is where the article item is created. Add more feature extraction here.
        item = {}
        item['url'] = response.url
        item['title'] = article_name.title
        item['content'] = article_name.text

        return item
