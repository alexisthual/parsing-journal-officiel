import json
import os
from tqdm import tqdm
from elasticsearch import Elasticsearch

from calculateTFIDF import TFIDFmanager


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

        self.es.indices.put_mapping(index='summary',
            doc_type='nodes',
            body={
                "properties": {
                    "date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        )

        self.es.indices.put_mapping(index='article',
            doc_type='nodes',
            body={
                "properties": {
                    "date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "cid": {
                        "type": "keyword"
                    }
                }
            }
        )

    def populateDB(self, rootDir, tfidfManager, k=5):
        rootPath = os.path.join(os.getcwd(), rootDir)

        # Iterate through every JO publication
        n = 0
        totalFolders = len(os.listdir(rootPath))
        with tqdm(total = self.maxSummaries if self.maxSummaries else totalFolders) as pbar:
            for folderName in os.listdir(rootPath):
                folderPath = os.path.join(rootPath, folderName)

                if os.path.isdir(folderPath):
                    date = folderName.split('-')

                    # Populate DB with summary file
                    with open(os.path.join(folderPath, 'summary.json')) as summaryJsonData:
                        summaryData = json.load(summaryJsonData)
                        self.es.index(index='summary', doc_type='nodes', body=summaryData)

                    articlesPath = os.path.join(folderPath, 'articles/')

                    # Iterate through every article of the current publication
                    for articleFileName in tqdm(os.listdir(articlesPath)):
                        # Given an article, computes the k closest articles
                        # and adds this information to the already existing JSON file
                        # 'article_2017-12-05_66'
                        articleString = 'article_{}_{}'.format(folderName, articleFileName.split('.')[0])
                        k_names, k_cids, k_scores = tfidfManager.find_k_closest(articleString, k)

                        # Populate DB with article file
                        with open(os.path.join(articlesPath, articleFileName)) as articleJsonData:
                            articleData = json.load(articleJsonData)
                            articleData['neighbors'] = [{
                                'cid': k_cids[i],
                                'score': k_scores[i]
                            } for i in range(len(k_cids))]
                            self.es.index(index='article', doc_type='nodes', body=articleData)

                n += 1
                pbar.update(1)

                if self.maxSummaries and n == self.maxSummaries:
                    pbar.close()
                    break


if __name__ == '__main__':
    rootDir = 'output/'

    print('Initiate TFIDF:')
    tfidfManager = TFIDFmanager()
    tfidfManager.go_through_data(rootDir)

    print('Populate Elastic instance:')
    dbm = dbManager(overwriteIndices=True, maxSummaries=None)
    dbm.initESIndexes()
    dbm.populateDB(rootDir, tfidfManager, k=5)
