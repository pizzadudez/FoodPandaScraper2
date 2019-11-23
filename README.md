# New concept:
- yield json
- db insert in pipeline


??? multiple menus (cu orar diferit)
https://www.foodpanda.ro/restaurant/v5ai/steak



## TODO:
- [x] add menu model
- [x] append scrapy to table names 
- [x] move all products from options to the products table
  - add flag 'is_menu_item'
  - options will only contain prod_id and price
- [x] images table + pipeline:
  - try requests from predefined array of width
  - save locally with product id as name
- skip vendor if crawled recently
- [x] combo menu items are products with options that are other menu items
  - add vendor
  - add toppings + options (products + product options)
  - add the rest normally
  - go thru all products that have a menu_cat.id and check for combos
    - use .join() in sqlalchemy to get all menu_item_products of a vendor
- [ ] images retry with different widths