# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import datetime

from sqlalchemy.orm import sessionmaker, query
from FoodPandaScraper2.models import *


class PostgresPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.session()
        
        city_id = item.get('city_id', None)
        city = session.query(City).filter_by(id=city_id).first()
        if not city:
            city = City(id=city_id, name=item.get('city_name', None))
            session.add(city)
            session.commit()

        # Toppings
        toppings = item.get('toppings', [])
        toppings = toppings.values() if isinstance(toppings, dict) else []
        for topping in toppings:
            t = session.query(Topping).filter_by(id=topping['id']).first()
            if t:
                session.delete(t)
                session.commit()
            t = Topping(
                id=topping['id'],
                description=topping['name'],
                min_quantity=topping['quantity_minimum'],
                max_quantity=topping['quantity_maximum']
            )
            options = topping.get('options', [])
            for option in options:
                o = Option(
                    name=option['name'],
                    price=option['price'],
                    product_id=option['product_id']
                )
                t.options.append(o)
            session.add(t)
        session.commit()

        # Vendor
        vendor = session.query(Vendor).filter_by(id=item['id']).first()
        if vendor:
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
        # Menus
        menus = item.get('menus', [])
        for menu in menus:
            m = Menu(
                id=menu['id'],
                name=menu['name'],
                opening_time=menu['opening_time'],
                closing_time=menu['closing_time']
            )
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
                # Products
                products = category.get('products', [])
                for product in products:
                    variations = product.get('product_variations', [])
                    p = session.query(Product).filter_by(id=product['id']).first()
                    if not p:
                        p = Product(
                            id=product['id'],
                            name=product['name'],
                            description=product.get('description', None),
                            price=variations[0].get('price', None)
                        )
                        # Check if Product has Variations and Toppings
                        multiple_variations = True if len(variations) > 1 else False
                        has_toppings = True if len(variations[0]['topping_ids']) else False
                        if not multiple_variations and not has_toppings:
                            continue # No variations to add
                        # Variations
                        for variation in variations:
                            v = Variation(
                                id=variation['id'],
                                name=variation.get('name', None),
                                price=variation.get('price', None)
                            )
                            for topping_id in variation.get('topping_ids', []):
                                topping = session.query(Topping).filter_by(id=topping_id).first()
                                v.toppings.append(topping)
                            p.variations.append(v)
                    mc.products.append(p)
                m.menu_categories.append(mc)
            vendor.menus.append(m)

        # Finish
        session.commit()
        # return item
        


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
