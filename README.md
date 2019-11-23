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
    - ! determine if menu item based on existence of menu_category_id instead
  - options will only contain prod_id and price
- [x] images table + pipeline:
  - save locally with product id as name
- [x] skip vendor if crawled recently
- [x] combo menu items are products with options that are other menu items
  - add vendor
  - add toppings + options (products + product options)
  - add the rest normally
  - go thru all products that have a menu_cat.id and check for combos
    - use .join() in sqlalchemy to get all menu_item_products of a vendor
- [ ] images retry with different widths
  - try requests from predefined array of width
- [ ] add remaining vendor data


## Issues:
- city name issue with restaurant in Arad that's actually in Cluj;
  - seems to be fixed for now on foodpanda's end but need a more reliable solution
  - ? ignore vendor-data.city_id and generate our own id's for each city url