import json
import os
import xml.etree.ElementTree as ET


# %% Article Parser
class ArticleParser:
    '''Creates an XML parser for JORF TEXT files.'''

    def __init__(self, logFile=None):
        '''Inits parser with basic information.'''

        self.getTextTags = [
            'ID', 'ID_ELI', 'ORIGINE', 'NATURE', 'NOR',
            'DATE_PUBLI', 'DATE_TEXTE', 'ORIGINE_PUBLI',
            'TITRE', 'TITREFULL', 'AUTORITE', 'MINISTERE'
        ]
        self.getContenuTags = ['NOTICE', 'VISAS', 'ABRO', 'RECT', 'SM', 'TP']
        self.getTextArticleTags = ['ID', 'ID_ELI']
        self.getContenuArticleTags = ['SM', 'BLOC_TEXTUEL']
        self.logFile = logFile

        self.initiate()

    def initiate(self):
        self.information = {}
        self.articles = []
        self.signataires = None

    def parse(self, xmlStringContent):
        '''Takes a string representing xml
        and parses it to json format.'''

        self.initiate()
        self.root = ET.fromstring(xmlStringContent)

        for element in self.root:
            tag = element.tag

            if tag in self.getTextTags:
                self.information[tag] = element.text
                if tag == 'ORIGINE_PUBLI':
                    self.information['ORIGINE_PUBLI_ID'] = element.get('id')
            elif tag in self.getContenuTags:
                self.information[tag] = self.getContenu(element)
            elif tag == 'STRUCT':
                self.parseStructure(element)

        self.information['STRUCT'] = {
            'articles': self.articles,
            'signataires': self.signataires
        }

        return json.dumps(self.information), self.information['ID']

    def getContenu(self, element):
        '''Util function for getting the inner text of a xml tag
        which supposedly contains a CONTENU tag which we are interested in.'''

        return ET.tostring(element.find('CONTENU'), encoding='utf-8').decode('utf-8')

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
                        information[tag] = self.getContenu(element)
                self.articles.append(information)
            elif tag == 'SIGNATAIRES':
                self.signataires = self.getContenu(structElement)
