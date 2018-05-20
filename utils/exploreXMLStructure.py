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
    def __init__(self, tarballAbsPath, outputFilePath, fileNameRegex, verbose=False):
        self.tarballAbsPath = tarballAbsPath
        self.outputFilePath = outputFilePath
        self.structure = defaultdict(recursiveDefaultDict)
        self.verbose = verbose

        self.fileNameRegex = fileNameRegex

    def updateStructure(self, structure, xmlElement):
        structure[xmlElement.tag]['attributes'] = []
        for attribute in xmlElement.attrib:
            structure[xmlElement.tag]['attributes'].append(attribute)

        for childElement in xmlElement:
            self.updateStructure(structure[xmlElement.tag], childElement)

    def explore(self):
        # Do first pass on data in order to count
        # total number of files
        if self.verbose:
            print('Counting selectable files in tarball...')

        totalNumberMembers = 0
        with tarfile.open(self.tarballAbsPath, 'r|gz') as tar:
            with tqdm(disable=(not self.verbose)) as pbar:
                member = tar.next()
                while member:
                    if re.match(self.fileNameRegex, member.name):
                        totalNumberMembers += 1
                    member = tar.next()
                    pbar.update(1)

        # Iterate through files in the tarball and update structure
        # for each file
        if self.verbose:
            print('Iterating through tarball\'s files...')

        with tarfile.open(self.tarballAbsPath, 'r|gz') as tar:
            with tqdm(total=totalNumberMembers, disable=(not self.verbose)) as pbar:
                member = tar.next()

                while member:
                    if re.match(self.fileNameRegex, member.name):
                        tarFile = tar.extractfile(member)

                        if tarFile:
                            content = tarFile.read().decode('utf-8')
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
    # CONSTANTS
    regexes = {
        'jo_article': '.*jorf/simple/JORF/CONT/([0-9]{2}/){5}[a-zA-Z0-9]+/[a-zA-Z0-9]+\.xml',
        'legi_text': '.*LEGITEXT.*\.xml',
        'legi_arti': '.*LEGIARTI.*\.xml'
    }

    # Read CLI arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('configPath', metavar='configPath',
        help='Path to YML config file')
    parser.add_argument('-r', dest='regexKey',
        help='Key to select the regex which will be used to select files\n{}'.format(
            '\n'.join(['\t{}: {}'.format(key, regexes[key]) for key in regexes])
        )
    )
    parser.add_argument('-i', dest='inputFilePath',
        help='Path to input tarball')
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

    # VARIABLES
    regexFileName = re.compile(regexes[args.regexKey])
    tarballAbsPath = args.inputFilePath
    outputFilePath = os.path.join(
        params['xmlStructuresDirPath'],
        args.outputFileName
    )

    # Create tarballExplorer and launch main methods
    explorer = tarballExplorer(tarballAbsPath, outputFilePath,
                               regexFileName, verbose=verbose)
    explorer.explore()
    explorer.write()
