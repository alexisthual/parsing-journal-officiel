import scrapy
import json
from copy import copy
import re
from bs4 import BeautifulSoup
from utils.textParser import textParser


class JOArticleSpider(scrapy.Spider):
    name = 'jo_article_spider'
    start_urls = [
        # 'https://www.legifrance.gouv.fr/eli/decret/2017/11/24/INTE1728700D/jo/texte',
        # 'https://www.legifrance.gouv.fr/eli/decret/2017/11/24/SSAH1720799D/jo/texte',
        # TODO: The following link has a <table>
        # TODO: Find articles which might display HTML tags that one wants to keep track of.
        # 'https://www.legifrance.gouv.fr/eli/arrete/2017/11/21/CPAB1732576A/jo/texte',
        # 'https://www.legifrance.gouv.fr/eli/arrete/2017/11/22/MICC1732367A/jo/texte',
        'https://www.legifrance.gouv.fr/affichTexte.do;jsessionid=8B37EB9CD05070E2B2D7AC64463FE0B7.tplgfr30s_3?cidTexte=JORFTEXT000036086705&dateTexte=&oldAction=rechJO&categorieLien=id&idJO=JORFCONT000036086530',
    ]

    def __init__(self):
        self.links = []
        self.verbose = False

    def enrichLinks(self, div):
        links = div.xpath('.//a')

        for a in links:
            text = a.xpath('./text()').extract_first()
            href = a.xpath('./@href').extract_first()
            self.links.append({
                'text': text,
                'href': href,
            })

    def scrapMainDiv(self, div):
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
        self.article = articleSoup.get_text()
        # Collect links inside entete
        self.enrichLinks(articleDiv)
        if self.verbose:
            print(self.article)

    def parse(self, response):
        """
        Doc
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

        assert(mainDiv)

        self.scrapMainDiv(mainDiv)

        textToParse = [self.entete, self.article]
        textToParse = list(map(textParser.parseText, textToParse))
        [self.entete, self.article] = textToParse

        assert('NOR' in self.entete)
        assert('ELI' in self.entete)
        assert(len(self.article) > 15)

        data = {
            'url': response.url,
            'entete': self.entete,
            'article': self.article,
            'links': self.links,
        }

        with open('parsed_article.json', 'w') as outfile:
            json.dump(data, outfile)

        yield data
