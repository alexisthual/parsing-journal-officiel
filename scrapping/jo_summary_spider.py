import scrapy
import json
from copy import copy


class JOSpider(scrapy.Spider):
    name = 'jo_summary_spider'
    start_urls = ['https://www.legifrance.gouv.fr/eli/jo/2017/11/25']

    def __init__(self):
        self.array = []
        self.verbose = False

    def handleLeaf(self, leaf, path=[]):
        """
        Receives a potential leaf. In case it is an actual leaf,
        compute information relative to this leaf and add it to the output
        dictionary.
        """
        nb = leaf.css('.numeroTexte::text').extract_first()
        text = leaf.css('a::text').extract_first()
        href = leaf.css('a::attr(href)').extract_first()
        if self.verbose:
            print(''.join(['\t' for _ in range(len(path))]) + 'LI A: ' + str(text[0:25]))
        if nb and text:
            self.array.append({
                'i': int(nb),
                'path': copy(path),
                'text': text,
                'href': href,
            })

    def recursiveUL(self, path, ul):
        """
        Receives an <ul> and iterates through it's direct <li> tags.
        """
        if self.verbose:
            print(''.join(['\t' for _ in range(len(path)-1)]) + 'UL: ' + str(path))
        LIs = ul.xpath('./li')

        for i, li in enumerate(LIs):
            self.recursiveLI(path, li, i, len(LIs))

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

    def parse(self, response):
        """
        Summaries from the Journal Officiel don't follow a clean structure,
        which prevents us from implementing a straitforward recursion.
        """
        mainTitle = response.css('.titleJO::text').extract_first()
        mainDiv = response.css('.sommaire > ul')

        allLinks = mainDiv.css('a::text').extract()
        mainTitles = mainDiv.css('h3::text').extract()

        allTags = mainDiv.xpath('./ul|li')
        realULs = filter(lambda tag: not tag.extract().startswith('<li'), allTags)
        potentialLeaves = filter(lambda tag: tag.extract().startswith('<li'), allTags)

        for leaf in potentialLeaves:
            self.handleLeaf(leaf)

        for i, mainTag in enumerate(realULs):
            self.recursiveMain([mainTitles[i]], mainTag)

        data = {
            'title': mainTitle,
            'nbLinks': len(allLinks),
            'array': self.array,
        }

        with open('parsed_summary.json', 'w') as outfile:
            json.dump(data, outfile)

        yield data
