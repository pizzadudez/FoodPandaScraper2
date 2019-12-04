# -*- coding: utf-8 -*-

# Scrapy settings for FoodPandaScraper2 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import datetime
from FoodPandaScraper2.credentials import credentials

###############################################################################
# Custom Crawler SETTINGS 
###############################################################################
# Set how old vendor data must be to be updated
VENDOR_UPDATE_DELTA = datetime.timedelta(days=7)
# (dev) Limit how many vendors per city get crawled, 0 means no limit
VENDOR_COUNT_LIMIT = 1
# Max-width: 5000
PRODUCT_IMAGE_WIDTH = 3000
###############################################################################

BOT_NAME = 'FoodPandaScraper2'

SPIDER_MODULES = ['FoodPandaScraper2.spiders']
NEWSPIDER_MODULE = 'FoodPandaScraper2.spiders'

# Database Connection String
CONNECTION_STRING = 'mysql+pymysql://{username}:{password}@{host}/{database}'.format(
    driver = credentials.get('DB_DRIVER', None),
    host = credentials.get('DB_HOST', None),
    username = credentials.get('DB_USERNAME', None),
    password = credentials.get('DB_PASSWORD', None),
    database = credentials.get('DB_NAME', None),
)

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'FoodPandaScraper2 (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 5
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'FoodPandaScraper2.middlewares.Foodpandascraper2SpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'FoodPandaScraper2.middlewares.Foodpandascraper2DownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'FoodPandaScraper2.pipelines.DatabasePipeline': 100,
   'FoodPandaScraper2.pipelines.CustomImagesPipeline': 300,
#    'FoodPandaScraper2.pipelines.JsonPipeline': 200,
}

# Image store S3
AWS_ACCESS_KEY_ID = credentials.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = credentials.get('AWS_SECRET_ACCESS_KEY', None)
IMAGES_STORE = credentials.get('AWS_BUCKET_URI', None)

# Image store local
# IMAGES_STORE = 'FoodPandaScraper2/images'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
