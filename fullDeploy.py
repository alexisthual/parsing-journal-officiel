import argparse
import glob
import os
import re
import tarfile
import yaml

from datetime import datetime
from tqdm import tqdm

from ftpClient import FTPClient
from parsers.JORFContextParser import SummaryParser
from parsers.JORFTextParser import ArticleParser
from databaseManager import DatabaseManager


# %% Util functions cell
def recursiveSearch(tarFile, tarballAbsPath):
    '''Util function iterating through the directories of a given directory.
    It returns False in case there are several possible directories.'''

    print(tarballAbsPath)
    # directories = [os.path.join(dirAbsPath, d) for d in os.listdir(dirAbsPath) if os.path.isdir(os.path.join(dirAbsPath, d))]
    directDirRegex = re.compile(tarballAbsPath + '\/[a-zA-Z0-9]+$')
    # directChildDirs = [d for d in tarFile.getmembers() if directDirRegex.match(d.name)]
    directChildDirs = [d for d in tarFile.getmembers()]
    print(*list(map(lambda x: x.name, directChildDirs)), sep='\n')

    if len(directChildDirs) == 0:
        return True
    elif len(directChildDirs) == 1:
        return recursiveSearch(directChildDirs[0].open(), directChildDirs[0].name)
    else:
        return False

def shouldExploreDir(tarFile):
    '''Determines whether the given directory respects the format one expects
    from a JORFSIMPLE archive.'''

    path = ''
    r = '[a-zA-Z0-9\-]+$'
    while True:
        children = [d.name for d in tarFile.getmembers() if re.match(os.path.join(path) + r, d.name)]
        if len(children) == 1:
            path = children[0] + '/'
        elif len(children) == 0:
            return path
        else:
            return None

# %% Main Cell
if __name__ == '__main__':
    '''Generic workflow for populating a local ES instance with relevant data.
    It goes through the following steps:
    * collect tarballs from a distant FTP server
        * distinguish between full dumps and incremental ones
    * connect to the local database
    * populate the local database with files from the downloaded tarballs
    '''

    # Read CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('configPath', metavar='configPath', 
            help='Path to YML config file')
    parser.add_argument('-v', '--verbose', action='store_true', 
            help='Should print information and debug messages')
    args = parser.parse_args()

    verbose = args.verbose
    
    with open(args.configPath, 'r') as ymlFile:
        params = yaml.load(ymlFile)

    # CONSTANTS
    verbose = args.verbose
    overwriteIndices = params['overwriteIndices']
    downloadTarballs = params['downloadTarballs']
    downloadFreemium = params['downloadFreemium']
    parseFreemium = params['parseFreemium']

    downloadsDirPath = params['downloadsDirPath']
    dataDirPath = params['dataDirPath']
    incrementalDataDirPath = os.path.join(
        dataDirPath,
        'incremental'
    )
    dataDirPathRegex = os.path.join(
        dataDirPath,
        params['dataRegex']
    )
    logsDirPath = params['logsDirPath']

    downloadsLogFile = os.path.join(logsDirPath, 'downloaded.txt')
    parsedLogFile = os.path.join(logsDirPath, 'parsed.txt')
    logFile = os.path.join(logsDirPath, 'logs.txt')

    fileNameRegex = re.compile('.*jorf/simple/JORF/CONT/([0-9]{2}/){5}[a-zA-Z0-9]+/[a-zA-Z0-9]+\.xml')

    # Check that output folders exist
    # and create them if need be.
    dirList = [downloadsDirPath, dataDirPath,
               incrementalDataDirPath, logsDirPath]
    for directory in dirList:
        if not os.path.isdir(directory):
            os.makedirs(directory)

    # 1. Collect tarballs
    if downloadTarballs:
        ftpClient = FTPClient('echanges.dila.gouv.fr', verbose=verbose)
        ftpClient.retrieveFiles(
            'JORFSIMPLE',
            downloadsDirPath,
            downloadsLogFile=downloadsLogFile,
            downloadFreemium=downloadFreemium
        )
        ftpClient.terminate()

    # 2. Init and create parsers
    dbm = DatabaseManager(overwriteIndices=overwriteIndices, verbose=verbose)
    dbm.initESIndexes()

    summaryParser = SummaryParser(logFile=logFile)
    articleParser = ArticleParser(logFile=logFile)

    # 3. Iterate through tarballs and populate database
    # IMPORTANT: the following piece of code is only valid if tarballs are
    # ordered correctly. Indeed, incremental files potentially modify files
    # which where previously put in the database. Eventually, this requires
    # that incremental files are treated in the right order (which should here
    # be the case the they are implicitely ordered by file name, which here
    # implies chronological sorting as well).
    tarballAbsPaths = glob.glob(dataDirPathRegex, recursive=True)
    previouslyParsedFileList = []

    if os.path.isfile(parsedLogFile):
        with open(parsedLogFile, 'r') as f:
            for line in f:
                previouslyParsedFileList.append(line.split(';')[1].rstrip())

    for tarballAbsPath in tqdm(tarballAbsPaths):
        tarballFileName = re.search('\/([^\/]+)$', tarballAbsPath).group(1)

        if re.match('.*\.tar\.gz', tarballAbsPath) and\
           (parseFreemium or re.match('^((?!Freemium).)*$', tarballAbsPath)) and\
           (tarballFileName not in previouslyParsedFileList):
            # tarballAbsPath = os.path.join(dataDirPath, tarballAbsPath)

            with tarfile.open(tarballAbsPath, 'r|gz') as tar:
                with tqdm() as memberBar:
                    # Load tarball's next header
                    member = tar.next()
                    while member:
                        # Check that the current file name is suitable.
                        if re.match(fileNameRegex, member.name):
                            tarFile = tar.extractfile(member)
                            if tarFile:
                                content = tarFile.read().decode('utf-8')

                                # Populate database after checking document type (ex: summary, article, etc)
                                if re.match('.*CONT[a-zA-Z0-9]+\.xml$', member.name) != None:
                                    parsedSummary, documentId = summaryParser.parse(content)
                                    dbm.addSummary(parsedSummary, documentId=documentId)
                                elif re.match('.*TEXT[a-zA-Z0-9]+\.xml$', member.name) != None:
                                    parsedArticle, documentId = articleParser.parse(content)
                                    dbm.addArticle(parsedArticle, documentId=documentId)

                                memberBar.update(1)

                        member = tar.next()

                with open(parsedLogFile, 'a+') as f:
                    f.write('{};{}\n'.format(str(datetime.now()), tarballFileName))

# %% Test cell
# This cell currently tests whether files present in the Freemium tarball
# refer to uniquely defined articles and summaries.

# p = '/home/alexis/parsing-journal-officiel/parsing_xml/data/JORFSIMPLE/Freemium_jorf_simple_20170302-103615.tar.gz'
# tar = tarfile.open(p, 'r:gz')
#
# fileNameRegex = re.compile('.*jorf/simple/JORF/CONT/([0-9]{2}/){5}[a-zA-Z0-9]+/[a-zA-Z0-9]+\.xml')
# fd = {}
# print(len(tar.getmembers()))
# files = [d.name for d in tar.getmembers() if fileNameRegex.match(d.name)]
# print(len(files))
# # print(*files, sep='\n')
#
# for f in files:
#     if f in fd:
#         fd[f] += 1
#     else:
#         fd[f] = 1
#
# print(len(fd.keys()))
# print({k: v for k, v in fd.items() if v > 1})
