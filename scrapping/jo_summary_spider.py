import scrapy
import json
from copy import copy
import re


class JOSummarySpider(scrapy.Spider):
    name = 'jo_summary_spider'
    start_urls = [
        # 'https://www.legifrance.gouv.fr/eli/jo/2017/11/25',
        # 'https://www.legifrance.gouv.fr/eli/jo/2017/11/23',
        'https://www.legifrance.gouv.fr/eli/jo/2017/11/26',
    ]

    def __init__(self):
        self.array = []
        self.verbose = True

    def handleLeaf(self, leaf, path=[]):
        """
        Receives a potential leaf. In case it is an actual leaf,
        compute information relative to this leaf and add it to the output
        dictionary.
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
        There are two kinds of <li> : nodes and leaves.
        In case it is a node, compute the title, add it to the path
        and call recursiveUL on the first <ul> of this <li>.
        Otherwise, call handleLeaf on this leaf.
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
        Receives an <ul> and iterates through it's direct <li> tags.
        """
        if self.verbose:
            print(''.join(['\t' for _ in range(len(path))]) + 'UL: ' + str(path))
        LIs = ul.xpath('./li')

        for i, li in enumerate(LIs):
            self.recursiveLI(path, li, i, len(LIs))

    def parseText(self, text):
        rx = re.compile('\W+')
        parsedText = rx.sub(' ', text).strip()

        return parsedText

    def parse(self, response):
        """
        Summaries from the Journal Officiel don't follow a clean structure,
        which prevents us from implementing a straitforward recursion.
        """
        self.array = []
        mainTitle = self.parseText(response.css('.titleJO::text').extract_first())
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
        print(len(allProbableArticles))
        print(len(self.array))
        assert(len(self.array) == len(allProbableArticles))

        with open('parsed_summary.json', 'w') as outfile:
            json.dump(data, outfile)

        yield data
