import json
import os
import xml.etree.ElementTree as ET

from anytree import Node, RenderTree


# %% Summary parsing
class SummaryParser:
    '''Creates an XML parser for JORF CONT files.'''

    def __init__(self):
        '''Inits parser with basic information.'''

        self.getTextTags = ['ID', 'ID_ELI', 'ORIGINE', 'TITRE', 'DATE_PUBLI']
        self.initiate()

    def initiate(self):
        self.information = {}

    def parse(self, xmlStringContent):
        '''Takes the absolute path to the file to be parsed
        and parses it.'''

        self.initiate()
        self.root = ET.fromstring(xmlStringContent)

        for element in self.root:
            tag = element.tag

            if tag in self.getTextTags:
                self.information[tag] = element.text
            elif tag == 'STRUCTURE_TXT':
                self.parseStructureText(element)
                self.information['STRUCTURE_TXT'] = self.parsedTree

        return json.dumps(self.information), self.information['ID']

    def parseStructureText(self, parentElement):
        currentDepth = 0
        rootNode = Node('root', parent=None)
        currentNode = rootNode

        for element in parentElement.iter():
            tag = element.tag

            if tag == 'TM':
                depth = int(element.attrib['niv'])

                if depth == currentDepth + 1:
                    currentNode = Node('', parent=currentNode)
                else:
                    for _ in range(abs(depth - currentDepth) + 1):
                        currentNode = currentNode.parent
                    newNode = Node('', parent=currentNode)
                    currentNode = newNode

                currentDepth = depth

            elif tag == 'TITRE_TM':
                currentNode.name = element.text
            elif tag == 'LIEN_TXT':
                Node('', parent=currentNode, idtxt=element.get('idtxt'), titre=element.get('titretxt'))

        self.structTree = rootNode
        self.parsedTree = self.recursiveParseNode(self.structTree)

    def recursiveParseNode(self, node):
        '''Recursively parses Nodes generated by parseStructureText
        into JSON.'''

        information = {
            'name': node.name,
            'links': [],
            'children': []
        }

        for child in node.children:
            if child.is_leaf:
                # This means the current child should be a LIEN_TXT
                try:
                    information['links'].append({
                        'idtxt': child.idtxt,
                        'titre': child.titre
                    })
                except Exception as e:
                    with open('./logs.txt', 'a+') as logFile:
                        logFile.write('{} - {}'.format(str(datetime.datetime.now()), e))
            else:
                information['children'].append(
                    self.recursiveParseNode(child)
                )

        return information


class SummaryTester:
    '''Util class for testing the previous parser.'''

    def __init__(self):
        self.absPath = '/home/alexis/parsing-journal-officiel/parsing_xml/data/JORFSIMPLE/20180227-010332/jorf/simple/JORF/CONT/00/00/36/64/47/JORFCONT000036644766/JORFCONT000036644766.xml'

    def test(self):
        summaryParser = SummaryParser()
        parsedSummary = summaryParser.parse(self.absPath)
        # print(RenderTree(summaryParser.structTree))
        print(json.dumps(summaryParser.parsedTree, indent=4))

# %% Test Cell
# summaryTester = SummaryTester()
# summaryTester.test()
