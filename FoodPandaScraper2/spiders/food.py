import json
from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.http import Request


class FoodSpider(scrapy.Spider):
    name = 'food'
    allowed_domains = ['foodpanda.ro']
    start_urls = ['https://www.foodpanda.ro']
    limit = 1 # number of vendors per city allowed
    dev = False
    dev_urls = [
        'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        # 'https://www.foodpanda.ro/restaurant/v4no/pizza-hut-delivery-brasov-nord',
    ]

    def start_requests(self):
        if self.dev:
            for url in self.dev_urls:
                yield Request(url=url, callback=self.parse_vendor)
            return

        for url in self.start_urls:
            yield Request(url=url, callback=self.city_crawl)

    def city_crawl(self, response):
        soup = bs(response.text, 'html.parser')
        city_nodes = soup.select('section.home-cities a.city-tile')
        urls = [response.url + x['href'].strip().lower() for x in city_nodes]
        
        for url in urls:
            meta = {'start_url': response.url}
            yield Request(url=url, callback=self.vendor_crawl, meta=meta)

    def vendor_crawl(self, response):
        soup = bs(response.text, 'html.parser')
        city_name = soup.select_one(
                '.hero-section-content .hero-section-text strong').text.strip()
        vendor_nodes = soup.select(
                'div.restaurants-container ul.vendor-list > li > a')
        urls = [response.meta['start_url'] + x['href'] for x in vendor_nodes]

        for count, url in enumerate(urls):
            if self.limit and count >= self.limit:
                break
            meta = {'city_name': city_name}
            yield Request(url=url, callback=self.parse_vendor, meta=meta)

    def parse_vendor(self, response):
        soup = bs(response.text, 'html.parser')
        menu = soup.select_one('div.menu__list-wrapper')
        vendor_data = json.loads(menu.get('data-vendor', {}))
        vendor_data['url'] = response.url
        vendor_data['city_name'] = response.meta.get('city_name', None)
        yield vendor_data
