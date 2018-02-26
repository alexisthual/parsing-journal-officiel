import json
import os
from tqdm import tqdm
from elasticsearch import Elasticsearch


class DatabaseManager:
    '''Populates local ElasticSearch database with JORF
    summaries and articles.'''

    def __init__(self, overwriteIndices=False):
        '''Initiates database manager with a connexion to the
        local running ElasticSearch instance.'''

        self.es = Elasticsearch()
        if overwriteIndices:
            self.deleteIndices()

    def deleteIndices(self):
        '''Deletes used indices in ES.'''

        self.es.indices.delete(index='summary', ignore=[400, 404])
        self.es.indices.delete(index='article', ignore=[400, 404])

    def initESIndexes(self):
        '''Creates indices in ES, as well as their respective mappings.'''

        self.es.indices.create(index='summary', ignore=400)
        self.es.indices.create(index='article', ignore=400)

        self.es.indices.put_mapping(index='summary',
            doc_type='nodes',
            body={
                "properties": {
                    "DATE_PUBLI": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "ID": {
                        "type": "keyword"
                    }
                }
            }
        )

        self.es.indices.put_mapping(index='article',
            doc_type='nodes',
            body={
                "properties": {
                    "DATE_PUBLI": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "ID": {
                        "type": "keyword"
                    }
                }
            }
        )

    def addSummary(self, nodeData):
        self.es.index(index='summary', doc_type='nodes', body=nodeData)

    def addArticle(self, nodeData):
        self.es.index(index='article', doc_type='nodes', body=nodeData)
