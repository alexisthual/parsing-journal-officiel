import glob
import os
import re
from tqdm import tqdm

from ftpClient import FTPClient
from fileExtracter import FileExtracter
from parsers.JORFContextParser import SummaryParser
from parsers.JORFTextParser import ArticleParser
from databaseManager import DatabaseManager


# %% Util functions cell
def recursiveSearch(dirAbsPath):
    '''Util function iterating through the directories of a given directory.
    It returns False in case there are several possible directories.'''

    directories = [os.path.join(dirAbsPath, d) for d in os.listdir(dirAbsPath) if os.path.isdir(os.path.join(dirAbsPath, d))]
    if len(directories) == 0:
        return True
    elif len(directories) == 1:
        return recursiveSearch(os.path.join(dirAbsPath, directories[0]))
    else:
        return False

def shouldExploreDir(dirAbsPath):
    '''Determines whether the given directory respects the format one expects
    from a JORFSIMPLE archive.'''

    return recursiveSearch(dirAbsPath)

# %% Main Cell
if __name__ == '__main__':
    verbose = True
    cwd = os.getcwd()

    # Connext to distant FTP server and download tarballs
    ftpClient = FTPClient('echanges.dila.gouv.fr', verbose=verbose)
    ftpClient.retrieveFiles(
        'JORFSIMPLE',
        os.path.join(cwd, 'parsing_xml/data/JORFSIMPLE/tarballs/'),
        regex='.*2018.*\-.*\.tar\.gz'
    )
    ftpClient.terminate()

    # Untar downloaded tarballs
    fileExtracter = FileExtracter(verbose=verbose)
    fileExtracter.extractAll(
        os.path.join(cwd, 'parsing_xml/data/JORFSIMPLE/tarballs'),
        os.path.join(cwd, 'parsing_xml/data/JORFSIMPLE/extracted')
    )

    # Generate regex for catching all XML files
    dataDir = 'parsing_xml/data/JORFSIMPLE/extracted/'
    filePathRegex = '*/jorf/simple/JORF/CONT/**/*.xml'
    fileAbsPath = os.path.join(cwd, dataDir, filePathRegex)

    # Regex to use in order to extract the file's name
    # from a given path
    fileNameRegex = re.compile('.*\/([a-zA-Z0-9]+\.xml)')

    # Initiabe db
    dbm = DatabaseManager(overwriteIndices=True, verbose=verbose)
    dbm.initESIndexes()

    # Initiate parsers
    summaryParser = SummaryParser()
    articleParser = ArticleParser()

    dataDirPath = os.path.join(cwd, dataDir)

    for dirName in tqdm(os.listdir(dataDirPath)):
        dirAbsPath = os.path.join(dataDirPath, dirName, 'jorf/simple/JORF')

        if os.path.isdir(dirAbsPath) and shouldExploreDir(dirAbsPath):
            dirAbsPathRegex = os.path.join(dirAbsPath, 'CONT/**/*.xml')
            for filePath in tqdm(glob.glob(dirAbsPathRegex, recursive=True)):
                fileName = fileNameRegex.search(filePath).group(1)

                if re.match('.*CONT.*', fileName) != None:
                    parsedSummary = summaryParser.parse(filePath)
                    dbm.addSummary(parsedSummary)
                elif re.match('.*TEXT.*', fileName) != None:
                    parsedArticle = articleParser.parse(filePath)
                    dbm.addArticle(parsedArticle)
