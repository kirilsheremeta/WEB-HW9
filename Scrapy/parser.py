import re

import scrapy
import json
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.item import Field, Item


class QuoteItem(Item):
    tags = Field()
    author = Field()
    quote = Field()


class AuthorItem(Item):
    fullname = Field()
    date_born = Field()
    born_location = Field()
    bio = Field()


class MainPipeline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'fullname' in adapter.keys():
            self.authors.append(adapter.asdict())
        if 'quote' in adapter.keys():
            self.quotes.append(adapter.asdict())
        return item

    def close_spider(self, spider):
        with open('quotes.json', 'w', encoding='utf-8') as fd:
            json.dump(self.quotes, fd, ensure_ascii=False, indent=4)
        with open('authors.json', 'w', encoding='utf-8') as fd:
            json.dump(self.authors, fd, ensure_ascii=False, indent=4)


class MainSpider(scrapy.Spider):
    START_INDEX = 0
    name = "main_spider"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]
    custom_settings = {'ITEM_PIPELINES': {MainPipeline: 100}}

    def parse(self, response, *args):
        for el in response.xpath("/html//div[@class='quote']"):
            author = el.xpath("span/small[@class='author']/text()").get().strip()
            quote = el.xpath("span[@class='text']/text()").get().strip()
            tags = [e.strip()
                    for e in el.xpath("div[@class='tags']/a[@class='tag']/text()").extract()
                    ]
            yield QuoteItem(author=author, quote=quote, tags=tags)
            yield response.follow(
                url=self.start_urls[self.START_INDEX] + el.xpath("span/a/@href").get().strip(),
                callback=self.parse_author
            )
        next_page_link = response.xpath("//li[@class='next']/a/href").get()
        if next_page_link:
            yield scrapy.Request(url=self.start_urls[self.START_INDEX] + next_page_link.strip())

    def parse_author(self, response, *args):
        content = response.xpath("/html//div[@class='author-details']")
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        date_born = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        bio = content.xpath("div[@class='author-description']/text()").get().strip()
        yield AuthorItem(fullname=fullname,
                         date_born=date_born,
                         born_location=born_location,
                         bio=bio)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(MainSpider)
    process.start()
    print('End')
