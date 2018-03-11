import glob
import os
import re
import tarfile
from tqdm import tqdm

from ftpClient import FTPClient
from fileExtracter import FileExtracter
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

    # CONSTANTS
    verbose = True
    downloadTarballs = False
    downloadFreemium = False
    parseFreemium = False

    cwd = os.getcwd()
    dataDirPath = os.path.join(cwd, 'data/JORFSIMPLE/**/*.tar.gz')
    fileNameRegex = re.compile('.*jorf/simple/JORF/CONT/([0-9]{2}/){5}[a-zA-Z0-9]+/[a-zA-Z0-9]+\.xml')

    # 1. Collect tarballs
    if downloadTarballs:
        ftpClient = FTPClient('echanges.dila.gouv.fr', verbose=verbose)
        ftpClient.retrieveFiles(
            'JORFSIMPLE',
            os.path.join(cwd, 'data/JORFSIMPLE/'),
            downloadFreemium=downloadFreemium
        )
        ftpClient.terminate()

    # 2. Init and create parsers
    dbm = DatabaseManager(overwriteIndices=True, verbose=verbose)
    dbm.initESIndexes()

    summaryParser = SummaryParser()
    articleParser = ArticleParser()

    # 3. Iterate through tarballs and populate database
    # IMPORTANT: the following piece of code is only valid if tarballs are
    # ordered correctly. Indeed, incremental files potentially modify files
    # which where previously put in the database. Eventually, this requires
    # that incremental files are treated in the right order (which should here
    # be the case the they are implicitely ordered by file name, which here
    # implies chronological sorting as well).
    tarballFileNames = glob.glob(dataDirPath, recursive=True)

    with tqdm(total=len(tarballFileNames)) as tarballBar:
        for tarballFileName in tarballFileNames:
            if re.match('.*\.tar\.gz', tarballFileName) and (parseFreemium or re.match('^((?!Freemium).)*$', tarballFileName)):
                # Open tarball
                tarballAbsPath = os.path.join(dataDirPath, tarballFileName)
                tarballBar.set_description(desc='Opening tarball')

                with tarfile.open(tarballAbsPath, 'r:gz') as tar:
                    # List valid XML files in the tarball
                    tarballBar.set_description(desc='Listing members')
                    memberNames = [name for name in tar.getnames() if re.match(fileNameRegex, name)]

                    # Iterate through valid XML files and populate database
                    tarballBar.set_description(desc='Adding members')
                    with tqdm(total=len(memberNames)) as memberBar:
                        for memberName in memberNames:
                            memberBar.set_description(desc='Extracting file')
                            tarFile = tar.extractfile(memberName)
                            # Checks that the tar member is correctly loaded
                            if tarFile:
                                memberBar.set_description(desc='Reading file')
                                content = tarFile.read().decode('utf-8')

                                # Populate database after checking document type (ex: summary, article, etc)
                                memberBar.set_description(desc='Adding file')
                                if re.match('.*CONT[a-zA-Z0-9]+\.xml$', memberName) != None:
                                    parsedSummary, documentId = summaryParser.parse(content)
                                    dbm.addSummary(parsedSummary, documentId=documentId)
                                elif re.match('.*TEXT[a-zA-Z0-9]+\.xml$', memberName) != None:
                                    parsedArticle, documentId = articleParser.parse(content)
                                    dbm.addArticle(parsedArticle, documentId=documentId)

                            memberBar.update(1)

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
