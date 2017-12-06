import scrapy
from scrapy.crawler import CrawlerProcess

from spiders.JOPublicationSpider import JOPublicationSpider


meta = {
    'date': ['2017', '12', '5'],
    'start_url': 'https://www.legifrance.gouv.fr/eli/jo/2017/12/5/',
}

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
})

# TODO: run spiders in batches
# process.crawl(JOPublicationSpider, data=meta2)
process.crawl(JOPublicationSpider, data=meta)
process.start()
