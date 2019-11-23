# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import datetime
import re

from PIL import Image
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from sqlalchemy.orm import sessionmaker, query

from FoodPandaScraper2.models import *


class PostgresPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.session()
        item['images'] = []
        
        # City
        city_id = item.get('city_id', None)
        city = session.query(City).filter_by(id=city_id).first()
        if not city:
            city = City(id=city_id, name=item.get('city_name', None))
            session.add(city)
            session.commit()

        # Vendor
        vendor = session.query(Vendor).filter_by(id=item['id']).first()
        if vendor:
            # Many to many deletes are weird
            for menu in vendor.menus:
                for menu_category in menu.menu_categories:
                    session.delete(menu_category)
            session.delete(vendor)
        vendor = Vendor(
            id=item['id'],
            updated_at=datetime.datetime.now(),
            name=item['name'],
            url=item['url'],
            image=None,
            rating=item.get('rating', None),
            address=None,
            coordinates=str(item['latitude']) + ',' + str(item['longitude']),
            city_id=city_id
        )
        session.add(vendor)

        # Toppings
        toppings = item.get('toppings', [])
        toppings = toppings.values() if isinstance(toppings, dict) else []
        for topping in toppings:
            t = Topping(
                id=topping['id'],
                description=topping['name'],
                min_quantity=topping['quantity_minimum'],
                max_quantity=topping['quantity_maximum'],
            )
            options = topping.get('options', [])
            for option in options:
                p = session.query(Product).filter_by(id=option['product_id']).first()
                if not p:
                    description = option.get('description', None)
                    p = Product(
                        id=option['product_id'],
                        name=option['name'],
                        description=description if description else None
                    )
                    session.add(p)
                o = Option(id=option['id'], price=option['price'])
                p.options.append(o)
                t.options.append(o)
            vendor.toppings.append(t)

        # Menus
        menus = item.get('menus', [])
        for menu in menus:
            m = Menu(
                id=menu['id'],
                name=menu['name'],
                opening_time=menu['opening_time'],
                closing_time=menu['closing_time']
            )
            vendor.menus.append(m)
            # Menu Categories
            menu_categories = menu.get('menu_categories', [])
            for category in menu_categories:
                mc = session.query(MenuCategory).filter_by(id=category['id']).first()
                if not mc:
                    mc = MenuCategory(
                        id=category['id'],
                        name=category['name'],
                        description=category.get('description', None)
                    )
                m.menu_categories.append(mc)
                # Products
                products = category.get('products', [])
                for product in products:
                    p = session.query(Product).filter_by(id=product['id']).first()
                    variations = product.get('product_variations', [])
                    if not p:
                        p = Product(
                            id=product['id'],
                            name=product['name'],
                            description=product.get('description', None),
                            price=variations[0].get('price', None)
                        )
                    elif not p.menu_category_id: 
                        p.price = variations[0].get('price', None)
                    else:
                        mc.products.append(p)
                        continue # Skip this product if it already is set as a menu item
                    
                    # Append product_id for the image download pipeline
                    if product.get('file_path', None):
                        p.has_image = True
                        item['images'].append(product['id'])
                    mc.products.append(p)

                    # Variations
                    multiple_variations = True if len(variations) > 1 else False
                    has_toppings = True if len(variations[0]['topping_ids']) else False
                    # Check if Product has Variations and Toppings
                    if not multiple_variations and not has_toppings:
                        continue # No variations to add
                    for variation in variations:
                        v = Variation(
                            id=variation['id'],
                            name=variation.get('name', None),
                            price=variation.get('price', None)
                        )
                        p.variations.append(v)
                        for topping_id in variation.get('topping_ids', []):
                            topping = session.query(Topping).filter_by(id=topping_id).first()
                            v.toppings.append(topping)

        # Identify combo menu items
        for topping in vendor.toppings:
            # Check if topping selector has menu item options
            topping_has_menu_items = False
            for option in topping.options:
                product = session.query(Product).filter_by(id=option.product_id).first()
                if product.menu_category_id:
                    topping_has_menu_items = True
                    break
            # Flag all products with this topping selector as combo items
            if topping_has_menu_items :
                for variation in topping.variations:
                    product = variation.product
                    product.is_combo_menu_item = True
                    # product.code = item['code']


        # Finish
        session.commit()
        return item
        

class CustomImagesPipeline(ImagesPipeline):
    CONVERTED_ORIGINAL = re.compile('^full/[0-9,a-f]+.jpg$')

    def get_media_requests(self, item, info):
        url = "https://images.deliveryhero.io/image/fd-ro/Products/"
        end = '.jpg?width=3000'
        return [Request(url + str(x) + end, meta={'id': x})
                for x in item.get('images', [])]
        
    def get_images(self, response, request, info):
        for key, image, buf, in super(CustomImagesPipeline, self).\
                get_images(response, request, info):
            if self.CONVERTED_ORIGINAL.match(key):
                key = self.change_filename(key, response)
            yield key, image, buf

    def change_filename(self, key, response):
        return "full/%s.jpg" % response.meta['id']


class JsonPipeline(object):
    def open_spider(self, spider):
        self.file = open('output/scraped.json', 'w')
        self.file.write("[\n")
    
    def close_spider(self, spider):
        self.file.write("]")
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(
            dict(item),
            indent = 2,
            separators = (',', ': ')
        ) + ",\n"
        self.file.write(line)
        return item
