from sqlalchemy import create_engine, Column, Table
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from FoodPandaScraper2.settings import DATABASE


def db_connect():
    return create_engine(URL(**DATABASE))

def create_tables(engine):
    Base.metadata.create_all(engine)

Base = declarative_base()


class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    # Children
    vendors = relationship('Vendor', back_populates='city',
            cascade='save-update, delete')


class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    updated_at = Column('updated_at', DateTime)
    name = Column('name', String)
    url = Column('url', String)
    image = Column('image', String)
    rating = Column('rating', String)
    address = Column('address', String)
    coordinates = Column('coordinates', String)
    city_id = Column(Integer, ForeignKey('cities.id'))
    # Parent
    city = relationship('City', back_populates='vendors')
    # Children
    toppings = relationship('Topping', back_populates='vendor',
            cascade='save-update, delete')
    menus = relationship('Menu', back_populates='vendor',
            cascade='save-update, delete')


menus_menu_categories = Table('menus_menu_categories', Base.metadata,
    Column('menu_id', Integer, ForeignKey('menus.id', ondelete='cascade')),
    Column('menu_category_id', Integer, ForeignKey('menu_categories.id', ondelete='cascade'))
)


class Menu(Base):
    __tablename__ = 'menus'
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    opening_time = Column('opening_time', String)
    closing_time = Column('closing_time', String)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    # Parent
    vendor = relationship('Vendor', back_populates='menus')
    # Children
    menu_categories = relationship('MenuCategory', secondary=menus_menu_categories,
            back_populates='menus')


class MenuCategory(Base):
    __tablename__ = 'menu_categories'
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    description = Column('description', String)
    # Parents
    menus = relationship('Menu', secondary=menus_menu_categories,
            back_populates='menu_categories')
    # Children
    products = relationship('Product', back_populates='menu_category',
            cascade='save-update, delete')


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    description = Column('description', String)
    price = Column('price', String)
    is_combo_menu_item = Column('is_combo_menu_item', Boolean, default=False)
    code = Column('code', String)
    menu_category_id = Column(Integer, ForeignKey('menu_categories.id'))
    # Parent
    menu_category = relationship('MenuCategory', back_populates='products')
    # Children
    variations = relationship('Variation', back_populates='product',
            cascade='save-update, delete')
    options = relationship('Option', back_populates='product',
            cascade='save-update, delete')


variations_toppings = Table('variations_toppings', Base.metadata,
    Column('variation_id', Integer, ForeignKey('variations.id')),
    Column('topping_id', Integer, ForeignKey('toppings.id'))
)   


class Variation(Base):
    __tablename__ = 'variations'
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    price = Column('price', String)
    product_id = Column(Integer, ForeignKey('products.id'))
    # Parent
    product = relationship('Product', back_populates='variations')
    # Children
    toppings = relationship('Topping', secondary=variations_toppings,
            back_populates='variations')


class Topping(Base):
    __tablename__ = 'toppings'
    id = Column(Integer, primary_key=True)
    description = Column('description', String)
    min_quantity = Column('min_quantity', Integer)
    max_quantity = Column('max_quantity', Integer)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    # Parents
    vendor = relationship('Vendor', back_populates='toppings')
    variations = relationship('Variation', secondary=variations_toppings,
            back_populates='toppings')
    # Children
    options = relationship('Option', back_populates='topping',
            passive_deletes=True)


class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    price = Column('price', String)
    product_id = Column(Integer, ForeignKey('products.id'))
    topping_id = Column(Integer, ForeignKey('toppings.id', ondelete='cascade'))
    # Parents
    product = relationship('Product', back_populates='options')
    topping = relationship('Topping', back_populates='options')