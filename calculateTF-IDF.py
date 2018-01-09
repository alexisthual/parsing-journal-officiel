import os
import json
from tqdm import tqdm
from tfidf.tfidf import TfIdf
from tfidf.articleDictionary import ArticleDictionary


class TFIDFmanager():
    def __init__(self):
        self.tfidf_summaries = TfIdf()
        self.tfidf_articles = TfIdf()
        self.summaries = ArticleDictionary()
        self.articles = ArticleDictionary()

    def preprocess_text(self, array):
        """
        Input: array of words
        Output: array of words filtered so that we remove the non relevant ones (and tokenize?)
        """
        return array

    def find_k_closest(self, string, k):
        if string[0:7]=='article':
            tfidf = self.tfidf_articles
            dictionary = self.articles
        elif string[0:7]=='summary':
            tfidf = self.tfidf_summaries
            dictionary = self.summaries
        else:
            print("WRONG QUERY")
            return
        res = tfidf.similarities(dictionary.content[string])
        res.sort(key=lambda x: x[1], reverse=True)
        results = []
        print("\n\nTop {} articles returned for {} ({}):".format(k, string, dictionary.urls[string]))
        # closest one is itself
        for i in range(1, k+1):
            temp = res[i][0]
            results += temp
            print("->{} ({})".format(temp, dictionary.urls[temp]))
            print(" ".join(dictionary.content[temp]))
        return results

    def go_through_data(self):
        rootPath = os.path.join(os.getcwd(), 'short/output/')  # folder that we will go through
        m = 0
        n = 0
        o = 0
        for fileName in tqdm(os.listdir(rootPath)):
            full_review = True
            folderPath = os.path.join(rootPath, fileName)
            print("\nCurrently going over {} \n".format(folderPath))

            if os.path.isdir(folderPath):
                m += 1
                date = fileName.split('-')

                # summaries
                with open(os.path.join(folderPath, 'summary.json')) as summaryJsonData:
                    string = 'summary_'+folderPath[-10:]
                    # 'summary_2017-12-02' for ex
                    words = []
                    summaryData = json.load(summaryJsonData)
                    array = summaryData['array']
                    for l in array:
                        words += self.preprocess_text(l['text'].split())
                    self.tfidf_summaries.add_document(string, words)
                    self.summaries.content[string] = words
                    self.summaries.urls[string] = summaryData['url']
                    n += 1

                articlesPath = os.path.join(folderPath, 'articles/')

                # articles
                for articleFileName in os.listdir(articlesPath):
                    with open(os.path.join(articlesPath, articleFileName)) as articleJsonData:
                        articleData = json.load(articleJsonData)
                        # 'article_2017-12-05_66' for ex
                        string = 'article_{}_{}'.format(folderPath[-10:], articleFileName[:-5])
                        words = self.preprocess_text(articleData['article'].split())
                        self.tfidf_articles.add_document(string, words)
                        self.articles.content[string] = words
                        self.articles.urls[string] = articleData['url']
                        self.articles.NORs[string] = articleData['NOR']
                        o += 1

        print("Visited {} folders, {} summaries, {} article words".format(m, n, o))


if __name__ == '__main__':
    tfidf_manager = TFIDFmanager()
    tfidf_manager.go_through_data()
    ex_string_1 = 'article_2017-12-05_66'
    ex_string_2 = 'summary_2017-12-05'
    tfidf_manager.find_k_closest(ex_string_1, 5)
    tfidf_manager.find_k_closest(ex_string_2, 5)
