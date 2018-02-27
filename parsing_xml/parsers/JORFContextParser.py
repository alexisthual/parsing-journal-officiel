import json
import os
import xml.etree.ElementTree as ET


# %% Summary parsing
class SummaryParser:
    '''Creates an XML parser for JORF CONT files.'''

    def __init__(self):
        '''Inits parser with basic information.'''

        self.getTextTags = ['ID', 'ID_ELI', 'ORIGINE', 'TITRE', 'DATE_PUBLI']
        self.initiate()

    def initiate(self):
        self.information = {}
        self.articleHierarchy = {}

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
            elif tag == 'STRUCTURE_TXT':
                self.parseStructureText(element)

        self.information['STRUCTURE_TXT'] = self.articleHierarchy
        return json.dumps(self.information)

    def parseStructureText(self, parentElement):
        '''Util function to parse a given STRUCTURE_TXT tag.'''

        currentLevel = 0
        levelCount = [0]
        self.currentConceptPath = []

        for element in parentElement.iter():
            tag = element.tag

            if tag == 'TM':
                level = int(element.attrib['niv'])
                if level != currentLevel + 1:
                    for _ in range(abs(level - currentLevel + 1)):
                        self.currentConceptPath.pop()
                currentLevel = level
            elif tag == 'TITRE_TM':
                self.currentConceptPath.append(element.text)
            elif tag == 'LIEN_TXT':
                self.addSummaryLink(element)

    def updateSummaryLinks(self, concept):
        '''Util function which updates the currentConceptPath
        as well as our hierarchy structure with the given concept.'''

        self.currentConceptPath.append(concept)
        d = self.articleHierarchy
        for c in self.currentConceptPath:
            d = d.setdefault(c, {})

    def addSummaryLink(self, element):
        '''Util function which adds an article to our
        hierarchy.'''

        d = self.articleHierarchy
        for c in self.currentConceptPath:
            d = d.setdefault(c, {})

        newArticle = {
            'cid': element.get('idtxt'),
            'titre': element.get('titretxt')
        }

        d = d.setdefault('articles', [])
        d.append(newArticle)
