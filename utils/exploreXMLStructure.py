import argparse
import json
import operator
import os
import re
import tarfile
import xml.etree.ElementTree as ET
import yaml

from collections import defaultdict
from functools import reduce
from tqdm import tqdm

def recursiveDefaultDict():
    return defaultdict(recursiveDefaultDict)


class tarballExplorer():
    def __init__(self, tarballAbsPath, outputFilePath):
        self.tarballAbsPath = tarballAbsPath
        self.outputFilePath = outputFilePath
        self.structure = defaultdict(recursiveDefaultDict)

        self.stopTags = ['table', 'br']
        self.fileNameRegex =\
            re.compile('.*jorf/simple/JORF/CONT/([0-9]{2}/){5}[a-zA-Z0-9]+/[a-zA-Z0-9]+\.xml')

    def updateStructure(self, structure, xmlElement):
        structure[xmlElement.tag]['attributes'] = []
        for attribute in xmlElement.attrib:
            structure[xmlElement.tag]['attributes'].append(attribute)

        if not xmlElement.tag in self.stopTags:
            for childElement in xmlElement:
                self.updateStructure(structure[xmlElement.tag], childElement)

    def explore(self):
        # Do first pass on data in order to count
        # total number of files
        totalNumberMembers = 0
        with tarfile.open(self.tarballAbsPath, 'r|gz') as tar:
            member = tar.next()
            while member:
                if re.match(self.fileNameRegex, member.name):
                    totalNumberMembers += 1
                member = tar.next()

        # Iterate through files in the tarball and update structure
        # for each file
        with tarfile.open(self.tarballAbsPath, 'r|gz') as tar:
            with tqdm(total=totalNumberMembers) as pbar:
                member = tar.next()

                while member:
                    if re.match(self.fileNameRegex, member.name):
                        tarFile = tar.extractfile(member)

                        if tarFile:
                            content = tarFile.read().decode('utf-8')

                            if re.match('.*TEXT[a-zA-Z0-9]+\.xml$', member.name) != None:
                                rootElement = ET.fromstring(content)
                                self.updateStructure(self.structure, rootElement)

                            pbar.update(1)

                    member = tar.next()

    def write(self):
        with open(self.outputFilePath, 'w') as outputFile:
            outputFile.write(json.dumps(self.structure))

def getNestedDictKey(nestedDicts, keyList):
    return reduce(operator.getitem, nestedDicts, keyList)

def setValueNestedDict(nestedDicts, keyList, value):
    getNestedDictKey(nestedDicts, keyList[:-1])[keyList[:-1]] = value

if __name__ == '__main__':
    # Read CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('configPath', metavar='configPath',
            help='Path to YML config file')
    parser.add_argument('-o', dest='outputFileName',
            help='Output file name')
    parser.add_argument('-v', '--verbose', action='store_true',
            help='Should print information and debug messages')
    args = parser.parse_args()

    verbose = args.verbose

    with open(args.configPath, 'r') as ymlFile:
        params = yaml.load(ymlFile)

    if not os.path.exists(params['xmlStructuresDirPath']):
        os.makedirs(params['xmlStructuresDirPath'])

    # CONSTANTS
    #tarballAbsPath = '/home/alexis/bureau_ouvert/jo/data/JORFSIMPLE/Freemium_jorf_simple_20170302-103615.tar.gz'
    tarballAbsPath = '/home/alexis/bureau_ouvert/jo/data/JORFSIMPLE/incremental/jorfsimple_20170228-011719.tar.gz'
    outputFilePath = os.path.join(
        params['xmlStructuresDirPath'],
        args.outputFileName
    )

    explorer = tarballExplorer(tarballAbsPath, outputFilePath)
    explorer.explore()
    explorer.write()
