import json
import operator
import os
import re
import tarfile
import xml.etree.ElementTree as ET

from collections import defaultdict
from functools import reduce
from tqdm import tqdm

def recursiveDefaultDict():
    return defaultdict(recursiveDefaultDict)

def getNestedDictKey(nestedDicts, keyList):
    return reduce(operator.getitem, nestedDicts, keyList)

def setValueNestedDict(nestedDicts, keyList, value):
    getNestedDictKey(nestedDicts, keyList[:-1])[keyList[:-1]] = value

def updateStructure(structure, xmlElement):
    structure[xmlElement.tag]['attributes'] = []
    for attribute in xmlElement.attrib:
        structure[xmlElement.tag]['attributes'].append(attribute)

    for childElement in xmlElement:
        updateStructure(structure[xmlElement.tag], childElement)

if __name__ == '__main__':
    # CONSTANTS
    fileNameRegex = re.compile('.*jorf/simple/JORF/CONT/([0-9]{2}/){5}[a-zA-Z0-9]+/[a-zA-Z0-9]+\.xml')
    tarballAbsPath = 'data/JORFSIMPLE/Freemium_jorf_simple_20170302-103615.tar.gz'
    tarballAbsPath = 'data/JORFSIMPLE/incremental/jorfsimple_20170228-011719.tar.gz'
    structure = defaultdict(recursiveDefaultDict)
    outputFilePath = 'XMLStructures/structure'

    # Open tarball stream
    with tarfile.open(tarballAbsPath, 'r|gz') as tar:
        with tqdm() as pbar:
            member = tar.next()

            while member:
                if re.match(fileNameRegex, member.name):
                    tarFile = tar.extractfile(member)
                    if tarFile:
                        content = tarFile.read().decode('utf-8')

                        # Check document type
                        if re.match('.*TEXT[a-zA-Z0-9]+\.xml$', member.name) != None:
                            rootElement = ET.fromstring(content)
                            updateStructure(structure, rootElement)

                        pbar.update(1)

                member = tar.next()

    with open(outputFilePath, 'w') as outputFile:
        outputFile.write(json.dumps(structure))
    #print(json.dumps(structure))
