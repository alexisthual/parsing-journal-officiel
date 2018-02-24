import json
from tqdm import tqdm
from elasticsearch import Elasticsearch


class dbCompleter:
    def __init__(self, maxArticles=3000):
        self.es = Elasticsearch()
        self.maxArticles = maxArticles

    def complete(self):
        '''Gets all entries for the 'article' index
        and makes sure all their links exist as nodes in the
        database.'''

        articles = self.es.search(
            index='article',
            body=json.dumps({
                'size': self.maxArticles,
                '_source': ['cid', 'links'],
                'query': {
                    'match_all': {}
                }
            })
        )

        articles = [article['_source'] for article in articles['hits']['hits']]
        self.cids = [article['cid'] for article in articles]

        for article in tqdm(articles):
            if 'links' in article:
                for link in article['links']:
                    cid = link['cid']
                    if cid and (not cid in self.cids):
                        articleData = json.dumps({
                            'url': link['href'],
                            'entete': None,
                            'NOR': None,
                            'ELI': None,
                            'cid': cid,
                            'article': link['text'],
                            'links': None,
                            'tables': None,
                        })

                        self.es.index(index='article', doc_type='nodes', body=articleData)
                        self.cids.append(cid)

if __name__ == '__main__':
    dbc = dbCompleter()
    dbc.complete()
