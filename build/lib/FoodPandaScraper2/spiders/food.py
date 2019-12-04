import json
import scrapy
import datetime

from bs4 import BeautifulSoup as bs
from scrapy.http import Request
from sqlalchemy.orm import sessionmaker, query

from FoodPandaScraper2.models import db_connect, Vendor
from FoodPandaScraper2.settings import VENDOR_UPDATE_DELTA, VENDOR_COUNT_LIMIT


class FoodSpider(scrapy.Spider):
    name = 'food'
    allowed_domains = ['foodpanda.ro']
    start_urls = ['https://www.foodpanda.ro']
    dev = False
    dev_urls = [
        # 'https://www.foodpanda.ro/chain/ca1vt/french-bakery',

        # 'https://www.foodpanda.ro/chain/cw9yi/pizza-hut-delivery',
        # 'https://www.foodpanda.ro/restaurant/v5gi/azima',
        # 'https://www.foodpanda.ro/restaurant/v1js/hopaa',
        # 'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        # 'https://www.foodpanda.ro/restaurant/v5wn/pizza-adaggio',
        # 'https://www.foodpanda.ro/restaurant/v4yi/big-belly-vendor',
        # 'https://www.foodpanda.ro/restaurant/v1ok/taboo-doner',
        # 'https://www.foodpanda.ro/chain/cj2cc/pizza-romana',

        # 'https://www.foodpanda.ro/restaurant/v5ek/cedelicii-delivery',
        # 'https://www.foodpanda.ro/restaurant/v0kk/log-out',
        # 'https://www.foodpanda.ro/restaurant/v4pl/bonita',
        # 'https://www.foodpanda.ro/restaurant/v7qc/pizza-napoli-cuptor-cu-lemne',
    ]
    engine = db_connect()
    session = sessionmaker(bind=engine)

    def start_requests(self):
        if self.dev:
            session = self.session()
            for url in self.dev_urls:
                current_time = datetime.datetime.now()
                vendor = session.query(Vendor).filter_by(url=url).filter(
                        Vendor.updated_at > current_time - VENDOR_UPDATE_DELTA).first()
                if vendor:
                    continue
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
        session = self.session()

        soup = bs(response.text, 'html.parser')
        city_name = soup.select_one(
                '.hero-section-content .hero-section-text strong').text.strip()
        vendor_nodes = soup.select(
                'div.restaurants-container ul.vendor-list > li > a')
        urls = [response.meta['start_url'] + x['href'] for x in vendor_nodes]

        count = 0
        for url in urls:
            # skip vendor if already scraped and it's not yet time to update
            current_time = datetime.datetime.now()
            vendor = session.query(Vendor).filter_by(url=url).filter(
                    Vendor.updated_at > current_time - VENDOR_UPDATE_DELTA).first()
            if vendor:
                continue

            # stop crawling if vendor limit exists
            count = count + 1
            if VENDOR_COUNT_LIMIT > 0 and count > VENDOR_COUNT_LIMIT:
                break

            meta = {'city_name': city_name}
            yield Request(url=url, callback=self.parse_vendor, meta=meta)

    def parse_vendor(self, response):
        soup = bs(response.text, 'html.parser')
        menu = soup.select_one('div.menu__list-wrapper')
        vendor_data = json.loads(menu.get('data-vendor', {}))
        vendor_data['url'] = response.url
        vendor_data['city_name'] = response.meta.get('city_name', None)
        vendor_data['address'] = soup.select_one('p.vendor-location').text.strip()
        
        yield vendor_data
