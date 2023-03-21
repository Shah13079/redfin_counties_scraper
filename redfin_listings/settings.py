# Scrapy settings for redfin_listings project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from shutil import which
from webdriver_manager.chrome import ChromeDriverManager
BOT_NAME = "redfin_listings"

SPIDER_MODULES = ["redfin_listings.spiders"]
NEWSPIDER_MODULE = "redfin_listings.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "redfin_listings (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_LEVEL = "INFO"


# from shutil import which
BOT_NAME = 'redfin_sales'

# DOWNLOAD_DELAY = 0.5


# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS_PER_DOMAIN = 1

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which(ChromeDriverManager().install())
SELENIUM_DRIVER_ARGUMENTS = [
    '------headless', '--log-level=3', '--blink-settings=imagesEnabled=false']

# scrapy selenium middleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}


# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
