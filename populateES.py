import json
import os
from tqdm import tqdm
from elasticsearch import Elasticsearch


class dbManager:
    def __init__(self, overwriteIndices=False, maxSummaries=None):
        self.es = Elasticsearch()
        self.maxSummaries = maxSummaries

        if overwriteIndices:
            try:
                self.deleteIndices()
            except Exception as e:
                print("Error raised while trying to delete indices...")
                print(e)

    def deleteIndices(self):
        self.es.indices.delete(index='summary', ignore=400)
        self.es.indices.delete(index='article', ignore=400)

    def initESIndexes(self):
        self.es.indices.create(index='summary', ignore=400)
        self.es.indices.create(index='article', ignore=400)

    def populateDB(self):
        rootPath = os.path.join(os.getcwd(), 'output/')

        # Iterate through every JO publication
        n = 0
        for fileName in tqdm(os.listdir(rootPath)):
            folderPath = os.path.join(rootPath, fileName)

            if os.path.isdir(folderPath):
                date = fileName.split('-')

                # Populate DB with summary file
                with open(os.path.join(folderPath, 'summary.json')) as summaryJsonData:
                    summaryData = json.load(summaryJsonData)
                    self.es.index(index='summary', doc_type='doc', body=summaryData)

                articlesPath = os.path.join(folderPath, 'articles/')
                print("\nCurrently going over {} \n".format(articlesPath))

                # Iterate through every article of the current publication
                for articleFileName in tqdm(os.listdir(articlesPath)):
                    # Populate DB with article file
                    with open(os.path.join(articlesPath, articleFileName)) as articleJsonData:
                        articleData = json.load(articleJsonData)
                        self.es.index(index='article', doc_type='doc', body=articleData)
                        print(articleData)

            n += 1
            if self.maxSummaries and n > self.maxSummaries:
                break


if __name__ == '__main__':
    dbm = dbManager(overwriteIndices=True, maxSummaries=5)
    dbm.initESIndexes()
    dbm.populateDB()
