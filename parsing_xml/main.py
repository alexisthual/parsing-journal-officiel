import os

from xmlParser import SummaryParser, ArticleParser
from databaseManager import DatabaseManager

if __name__ == '__main__':
    currentPath = os.getcwd()
    pathToFile = 'data/JORFSIMPLE/20170319-002045/jorf/simple/JORF/CONT/00/00/34/20/94/JORFCONT000034209405'

    dbm = DatabaseManager(overwriteIndices=True)
    dbm.initESIndexes()

    summaryFileName = 'JORFCONT000034209405.xml'
    summaryAbsPath = os.path.join(currentPath, pathToFile, summaryFileName)
    summaryParser = SummaryParser()
    parsedSummary = summaryParser.parse(summaryAbsPath)
    dbm.addSummary(parsedSummary)
    print('added summary')

    articleFileName = 'JORFTEXT000034209410.xml'
    articleAbsPath = os.path.join(currentPath, pathToFile, articleFileName)
    articleParser = ArticleParser()
    parsedArticle = articleParser.parse(articleAbsPath)
    dbm.addArticle(parsedArticle)
    print('added article')
