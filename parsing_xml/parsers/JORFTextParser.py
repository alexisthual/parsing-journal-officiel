import json
import os
import xml.etree.ElementTree as ET


# %% Article Parser
class ArticleParser:
    '''Creates an XML parser for JORF TEXT files.'''

    def __init__(self):
        '''Inits parser with basic information.'''

        self.getTextTags = [
            'ID', 'ID_ELI', 'ORIGINE', 'NATURE', 'NOR',
            'DATE_PUBLI', 'DATE_TEXTE', 'ORIGINE_PUBLI',
            'TITRE', 'TITREFULL', 'AUTORITE', 'MINISTERE']
        self.getTextArticleTags = ['ID', 'ID_ELI']
        self.getContenuArticleTags = ['SM', 'BLOC_TEXTUEL']
        self.initiate()

    def initiate(self):
        self.information = {}
        self.articles = []
        self.signataires = None

    def parse(self, absPath):
        '''Takes the absolute path to the file to be parsed
        and parses it.'''

        self.initiate()
        self.tree = ET.parse(absPath)
        self.root = self.tree.getroot()

        for element in self.root:
            tag = element.tag

            if tag in self.getTextTags:
                self.information[tag] = element.text
                if tag == 'ORIGINE_PUBLI':
                    self.information['ORIGINE_PUBLI_ID'] = element.get('id')
            elif tag == 'STRUCT':
                self.parseStructure(element)

        self.information['STRUCT'] = {
            'articles': self.articles,
            'signataires': self.signataires
        }

        return json.dumps(self.information)

    def parseStructure(self, parentElement):
        '''Util function to parse a given STRUCT tag.'''

        for structElement in parentElement:
            tag = structElement.tag

            if tag == 'ARTICLE':
                information = {}
                for element in structElement:
                    tag = element.tag
                    if tag in self.getTextArticleTags:
                        information[tag] = element.text
                    elif tag in self.getContenuArticleTags:
                        # information[tag] = ''.join(element.find('CONTENU').itertext()) if element.find('CONTENU') else None
                        information[tag] =\
                            ET.tostring(element.find('CONTENU'), encoding='utf-8').decode('utf-8')
                self.articles.append(information)
            elif tag == 'SIGNATAIRES':
                # self.signataires = structElement.find('CONTENU').text if structElement.find('CONTENU') else None
                self.signataires =\
                    ET.tostring(structElement.find('CONTENU'), encoding='utf-8').decode('utf-8')
