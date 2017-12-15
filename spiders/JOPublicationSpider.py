import json
import os
import re
import scrapy
from copy import copy
from functools import partial
from bs4 import BeautifulSoup

from utils.textParser import textParser
from utils.tableParser import tableParser


class JOPublicationSpider(scrapy.Spider):
    name = 'JOPublicationSpider'

    def __init__(self, *args, **kwargs):
        super(JOPublicationSpider, self).__init__(*args, **kwargs)
        self.meta = kwargs.get('meta')
        self.start_urls = kwargs.get('meta').keys()
        self.array = []
        self.verbose = False
        self.tableParser = tableParser()

    # PARSING THE PUBLICATION'S SUMMARY

    def handleLeaf(self, leaf, path=[]):
        """
        Input: Scrapy <li> tag (potential leaf of the concept tree).
        Output: dict containing information about the leaf.
        """

        nb = leaf.css('.numeroTexte::text').extract_first()
        text = leaf.xpath('./a/text()').extract_first()
        href = leaf.css('a::attr(href)').extract_first()

        if self.verbose:
            print(''.join(['\t' for _ in range(len(path))]) + 'LI A: ' + (text[0:20] if text else 'None'))

        if nb and text:
            self.array.append({
                'i': int(nb),
                'path': copy(path),
                'text': text,
                'href': href,
            })

    def recursiveLI(self, path, li, i, n):
        """
        Input: a scrapy <li> tag.
        Output:
        * In case it is a node, compute the title, add it to the path
        and call recursiveUL on the first <ul> of this <li>.
        * Otherwise, call handleLeaf on this leaf.

        To tell apart leaves and nodes, simply check if the <li> has a title.
        If it does, then it's a node.
        Important: if i == n-1 then this <li> is the last of it's <ul> and
        one therefore needs to pop path.
        """

        titre = li.css('h3::text').extract_first()

        if not titre:
            titre = li.css('h4::text').extract_first()
            if not titre:
                titre = li.css('h5::text').extract_first()
                if not titre:
                    titre = li.css('h6::text').extract_first()

        if titre:
            if self.verbose:
                print(''.join(['\t' for _ in range(len(path))]) + 'LI T: ' + str(titre))
            path.append(titre)
            self.recursiveUL(path, li.xpath('./ul[1]'))
        else:
            self.handleLeaf(li, path)

        if i == n-1:
            path.pop()

    def recursiveUL(self, path, ul):
        """
        Input: a Scrapy <ul> tag.
        Output: call to recursiveLI for each of the direct <li> tags of the input.
        """

        if self.verbose:
            print(''.join(['\t' for _ in range(len(path))]) + 'UL: ' + str(path))
        LIs = ul.xpath('./li')

        for i, li in enumerate(LIs):
            self.recursiveLI(path, li, i, len(LIs))

    def parse(self, response):
        """
        Input: Scrapy response.
        Output: calls to parseArticle on each of the article links
        found in the input. One also saves all links in a separated JSON file.
        """

        # Check if the url actually leads to a JO edition and
        # if not, then stop exploring.
        if len(response.css('.sommaire').extract()) == 0:
            return

        self.array = []
        mainTitle = textParser.parseTitle(response.css('.titleJO::text').extract_first())
        mainUl = response.css('.sommaire > ul')
        mainTag = response.css('.sommaire > ul > li')

        allProbableArticles = mainUl.css('a::text').extract()
        h3Titles = mainTag.css('h3::text').extract()

        for i, ul in enumerate(mainTag.xpath('./ul')):
            self.recursiveUL([h3Titles[i]], ul)

        # RIDICULOUS SPECIAL CASES

            # https://www.legifrance.gouv.fr/eli/jo/2017/11/25
        potentialLeaves = mainUl.xpath('./li')

        for leaf in potentialLeaves:
            self.handleLeaf(leaf)

        missedMainLi = len(mainUl.xpath('./li').extract()) > 1
        if missedMainLi:
            mainTag = response.css('.sommaire > ul')
            h3Titles = mainTag.css('h3::text').extract()

            for i, ul in enumerate(mainTag.xpath('./ul')):
                self.recursiveUL([h3Titles[i]], ul)

        # Final data
        data = {
            'title': mainTitle,
            'url': response.url,
            'array': self.array,
        }

        # Testing that the retreived data is somewhat consistent with
        # what we would expect (ie checking that the assumptions that
        # we are making on the page's structure seems correct).
        assert(
            len(self.array) == len(allProbableArticles),
            'Missing articles in summary {0}'.format(str(self.meta[response.url]))
        )

        path = 'output/{0}'.format(str(self.meta[response.url]))
        filename = 'summary.json'

        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, filename), 'w+') as outfile:
            json.dump(data, outfile)

        for followLink in data['array']:
            yield scrapy.Request(
                'https://www.legifrance.gouv.fr' + followLink['href'],
                callback=partial(self.parseArticle, response.url, followLink['i'])
            )


    # PARSING THE PUBLICATION'S ARTICLES

    # Inside an article, find the relevant pieces of text
    # and parse them correctly.


    def enrichLinks(self, div):
        """
        Input: Scrapy <div> tag.
        Output: dict with information concerning the input tag.
        """

        links = div.xpath('.//a')

        for a in links:
            text = a.xpath('./text()').extract_first()
            href = a.xpath('./@href').extract_first()
            self.links.append({
                'text': text,
                'href': href,
            })

    def parseTables(self, soup):
        """
        Input: BeatifulSoup soup.
        Output:
            * soup with <table> tags replaced by their hash value
            * a dict mapping each <table> tag's hash value to the parsed version
            of that table.
        """

        parsedTables = {}

        for table in soup.findAll('table'):
            parsedTable = self.tableParser.toJson(table)
            h = hash(str(parsedTable))
            parsedTables[h] = parsedTable
            table.replaceWith('parsedTable#' + str(h))

        return soup, parsedTables

    def scrapMainDiv(self, div):
        """
        Input: Scrapy <div> tag.
        Output: parses the input div by finding the entete first and then the
        rest of the article.
        """

        # Collect Entete
        enteteDiv = div.xpath('./div[contains(@class, \'enteteTexte\')]')
        enteteSoup = BeautifulSoup(enteteDiv.extract_first(), 'html.parser')
        self.entete = enteteSoup.get_text()
        # Collect links inside entete
        self.enrichLinks(enteteDiv)

        if self.verbose:
            print(self.entete)

        # Collect remaining text
        articleDiv = div.xpath('./div[2]')
        articleSoup = BeautifulSoup(articleDiv.extract_first(), 'html.parser')
        # Parse all tables inside the main div
        articleSoup, parsedTables = self.parseTables(articleSoup)
        self.article = articleSoup.get_text()
        self.parsedTables = parsedTables
        # Collect links inside entete
        self.enrichLinks(articleDiv)

        if self.verbose:
            print(self.article)

    def parseArticle(self, parentUrl, textNumber, response):
        """
        Input: article index in publication summary, Scrapy response.
        Output: writes parsed version of the article to a specific JSON file.
        """

        # A priori, the div we are interested in is the second div
        # which is a direct children of div.data
        # For "safety" reasons, we chose to check them all.
        self.links = []
        dataDiv = response.css('.data')
        mainDiv = None

        for div in dataDiv.xpath('./div'):
            hasEntete = len(div.xpath('./div[contains(@class, \'enteteTexte\')]')) == 1
            if hasEntete:
                if self.verbose:
                    print('LOG: div.data correctly found')
                mainDiv = div

        assert(
            mainDiv,
            'Missing mainDiv in {0}: {1}'.format(str(self.meta[parentUrl]), textNumber)
        )

        self.scrapMainDiv(mainDiv)

        textToParse = [self.entete, self.article]
        textToParse = list(map(textParser.parseText, textToParse))
        [self.entete, self.article] = textToParse

        assert(
            'NOR' in self.entete,
            'Missing NOR in article {0}: {1}'.format(str(self.meta[parentUrl]), textNumber)
        )
        assert(
            'ELI' in self.entete,
            'Missing ELI in article {0}: {1}'.format(str(self.meta[parentUrl]), textNumber)
        )
        assert(len(self.article) > 15)

        data = {
            'url': response.url,
            'entete': self.entete,
            'article': self.article,
            'links': self.links,
            'tables': self.parsedTables,
        }

        path = 'output/{0}/articles/'.format(str(self.meta[parentUrl]))
        filename = str(textNumber) + '.json'

        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, filename), 'w+') as outfile:
            json.dump(data, outfile)
