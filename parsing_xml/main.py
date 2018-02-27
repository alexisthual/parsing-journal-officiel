import glob
import os
import re
from tqdm import tqdm

from parsers.JORFContextParser import SummaryParser
from parsers.JORFTextParser import ArticleParser
from databaseManager import DatabaseManager

# %% Test cell

# %% Main cell
if __name__ == '__main__':
    # Generate regex for catching all XML files
    currentDir = os.getcwd()
    dataDir = 'data/JORFSIMPLE'
    filePathRegex = '*/jorf/simple/JORF/CONT/**/*.xml'
    fileAbsPath = os.path.join(currentDir, dataDir, filePathRegex)

    # Regex to use in order to extract the file's name
    # from a given path
    fileNameRegex = re.compile('.*\/([a-zA-Z0-9]+\.xml)')

    # Initiabe db
    dbm = DatabaseManager(overwriteIndices=True, verbose=True)
    dbm.initESIndexes()

    # Initiate parsers
    summaryParser = SummaryParser()
    articleParser = ArticleParser()

    for filePath in tqdm(glob.glob(fileAbsPath, recursive=True)):
        fileName = fileNameRegex.search(filePath).group(1)

        if re.match('.*CONT.*', fileName) != None:
            parsedSummary = summaryParser.parse(filePath)
            dbm.addSummary(parsedSummary)
        elif re.match('.*TEXT.*', fileName) != None:
            parsedArticle = articleParser.parse(filePath)
            dbm.addArticle(parsedArticle)
