import json
import os
import time
from tqdm import tqdm
from elasticsearch import Elasticsearch


class DatabaseManager:
    '''Populates local ElasticSearch database with JORF
    summaries and articles.'''

    def __init__(self, overwriteIndices=False, verbose=False):
        '''Initiates database manager with a connexion to the
        local running ElasticSearch instance.'''

        self.es = Elasticsearch()
        self.verbose = verbose
        if overwriteIndices:
            self.deleteIndices()

    def deleteIndices(self):
        '''Deletes used indices in ES.'''

        if self.verbose:
            print('Deleting indices...')

        self.es.indices.delete(index='summary', ignore=[400, 404])
        self.es.indices.delete(index='article', ignore=[400, 404])

    def initESIndexes(self):
        '''Creates indices in ES, as well as their respective mappings.'''

        if self.verbose:
            print('Creating indices...')

        # Initate summary ES index
        self.es.indices.create(index='summary', ignore=400)
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
                    },
                    "STRUCTURE_TXT": {
                        "type": "object",
                        "enabled": False
                    }
                }
            }
        )

        # Initiate article ES index
        self.es.indices.create(index='article', ignore=400)
        self.es.indices.close(index='article')
        self.es.indices.put_settings(index='article',
            body={
                "analysis": {
                    "analyzer": {
                        "htmlStripAnalyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["standard", "lowercase"],
                            "char_filter": [
                                "html_strip"
                            ]
                        }
                    }
                }
            }
        )
        self.es.indices.put_mapping(index='article', doc_type='nodes',
            body={
                "properties": {
                    "DATE_PUBLI": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "ID": {
                        "type": "keyword"
                    },
                    "STRUCT": {
                        "type": "object",
                        "properties": {
                            "articles": {
                                "type": "nested",
                                "properties": {
                                    "BLOC_TEXTUEL": {
                                        "type": "text",
                                        "analyzer": "htmlStripAnalyzer"
                                    }
                                }
                            },
                            "signataires": {
                                "type": "text"
                            }
                        }
                    }
                }
            }
        )
        self.es.indices.open(index='article')

    def addSummary(self, nodeData, documentId=None):
        self.es.index(index='summary', doc_type='nodes', body=nodeData, id=documentId)

    def addArticle(self, nodeData, documentId=None):
        self.es.index(index='article', doc_type='nodes', body=nodeData, id=documentId)
