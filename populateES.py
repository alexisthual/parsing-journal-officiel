import json
import os
from tqdm import tqdm
from elasticsearch import Elasticsearch


class dbManager:
    def __init__(self, overwriteIndices=False, maxSummaries=10):
        self.es = Elasticsearch()
        self.maxSummaries = maxSummaries

        if overwriteIndices:
            self.deleteIndices()

    def deleteIndices(self):
        self.es.indices.delete(index='summary', ignore=[400, 404])
        self.es.indices.delete(index='article', ignore=[400, 404])

    def initESIndexes(self):
        self.es.indices.create(index='summary', ignore=400)
        self.es.indices.create(index='article', ignore=400)

    def populateDB(self):
        rootPath = os.path.join(os.getcwd(), 'output/')

        # Iterate through every JO publication
        n = 0
        totalFolders = len(os.listdir(rootPath))
        with tqdm(total = self.maxSummaries if self.maxSummaries else totalFolders) as pbar:
            for fileName in os.listdir(rootPath):
                folderPath = os.path.join(rootPath, fileName)

                if os.path.isdir(folderPath):
                    date = fileName.split('-')

                    # Populate DB with summary file
                    with open(os.path.join(folderPath, 'summary.json')) as summaryJsonData:
                        summaryData = json.load(summaryJsonData)
                        self.es.index(index='summary', doc_type='nodes', body=summaryData)

                    articlesPath = os.path.join(folderPath, 'articles/')

                    # Iterate through every article of the current publication
                    for articleFileName in tqdm(os.listdir(articlesPath)):
                        # Populate DB with article file
                        with open(os.path.join(articlesPath, articleFileName)) as articleJsonData:
                            articleData = json.load(articleJsonData)
                            self.es.index(index='article', doc_type='nodes', body=articleData)

                n += 1
                pbar.update(1)

                if self.maxSummaries and n == self.maxSummaries:
                    pbar.close()
                    break

if __name__ == '__main__':
    dbm = dbManager(overwriteIndices=True, maxSummaries=5)
    dbm.initESIndexes()
    dbm.populateDB()
