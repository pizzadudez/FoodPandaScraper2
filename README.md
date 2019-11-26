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
- [x] images retry with different widths
  - try requests from predefined array of width
  - Solved: added download delay => all images @ 5000px
- [ ] add remaining vendor data
  - vendor banner
- [ ] images table (one products many images) -> figure out after s3 integration


```
https://images.deliveryhero.io/image/fd-ro/Products/60253.png?width=5000
https://images.deliveryhero.io/image/fd-ro/Products/60253.jpg?width=5000
```

## Issues:
- city name issue with restaurant in Arad that's actually in Cluj;
  - seems to be fixed for now on foodpanda's end but need a more reliable solution
  - ? ignore vendor-data.city_id and generate our own id's for each city url
- Handling chains (crawling vendors doesn't redirect)

