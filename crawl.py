from datetime import date, timedelta, datetime
import getopt
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import sys

from spiders.JOPublicationSpider import JOPublicationSpider


def parseUrl(date):
    url = 'https://www.legifrance.gouv.fr/eli/jo/'
    return url + '/'.join(list(map(str, [date.year, date.month, date.day])))


def main(argv):
    # Create output folders in case they don't exist
    dirList = ['./logs', './output']

    for dirName in dirList:
        if not os.path.isdir(dirName):
            os.makedirs(dirName)

    # Add cleaning option for CLI
    try:
        opts, args = getopt.getopt(argv[1:], 'c', ['clean='])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    for k, v in opts:
        if k == '-c' or '--clean':
            folderName = './output'
            for path, folders, files in os.walk(folderName, topdown=False):
                for fileName in files:
                    os.remove(os.path.join(path, fileName))
                if path != './output':
                    os.rmdir(path)

    settings = Settings()
    settings.set('USER_AGENT', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
    settings.set('CONCURRENT_REQUESTS', 100)
    settings.set('COOKIES_ENABLED', False)
    settings.set('REDIRECT_ENABLED', False)
    settings.set('LOG_LEVEL', 'INFO')
    # Prevent loading errors from the server:
    settings.set('DOWNLOAD_DELAY', 0.1)
    settings.set('FEED_EXPORT_ENCODING', 'utf-8')
    process = CrawlerProcess(settings)

    # Parallelize main spider
    batches = 3
    daysPerBatch = 3
    logFileName = './logs/{0}.txt'.format(str(datetime.now()))

    for batch in range(batches):
        dates = [singleDate for singleDate in ((date.today() - batch * timedelta(daysPerBatch)) - timedelta(day) for day in range(daysPerBatch))]
        meta = {
            'urls': {},
            'logFileName': logFileName,
        }

        for d in dates:
            meta['urls'][parseUrl(d)] = d

        process.crawl(JOPublicationSpider, meta=meta)

    process.start()


if __name__ == '__main__':
    main(sys.argv)
