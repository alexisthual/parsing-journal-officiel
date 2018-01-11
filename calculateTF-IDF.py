import os
import io
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
        self.excluded_vocabulary = []
        f = io.open('tfidf/stopwords.txt', 'r', encoding='utf8')
        self.stopwords = f.read().splitlines()

    def describe_yourself(self):
        s = sorted(self.tfidf_summaries.corpus_dict.items(), key=lambda x: x[1], reverse=True)
        a = sorted(self.tfidf_articles.corpus_dict.items(), key=lambda x: x[1], reverse=True)

        print("Current corpus: {} summaries [{} words] and {} articles [{} words]".format(
            len(self.summaries.content), len(self.tfidf_summaries.corpus_dict.items()),
            len(self.articles.content), len(self.tfidf_articles.corpus_dict.items())))
        print("\n\n----------------------------------------------------------------------------")
        print("List of words in summaries' corpus:")
        print(s)
        print("\nList of words in articles' corpus:")
        print(a)
        print("\nList of current stopwords:")
        print(self.stopwords)
        print("----------------------------------------------------------------------------")

    def generate_excluded_vocabulary(self):
        # total_words = sum(self.tfidf_articles.corpus_dict.values())
        s = sorted(self.tfidf_articles.corpus_dict.items(), key=lambda x: x[1], reverse=True)
        c = 0
        are_you_sure = False
        with io.open('tfidf/stopwords.txt', 'a', encoding='utf8') as f:
            if are_you_sure:
                for w in s:
                    # number is chosen by looking at the sorted values
                    if w[1] > 605:
                        f.write(w[0]+"\n")
                        c += 1
        print("Added {} words to stopwords!".format(c))

    def preprocess_text(self, array):
        """
        Input: array of words
        Output: array of words filtered so that we remove the non relevant ones (and tokenize?)
        """
        initial_number = len(array)
        array = [word.lower() for word in array if word not in self.stopwords and word.lower() not in self.stopwords and not word.isdigit()]
        final_number = len(array)
        # print("Preprocessing: reduced number of words from {} to {}".format(initial_number, final_number))
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
        values = []
        print("\n\nTop {} articles returned for {} ({}):".format(k, string, dictionary.urls[string]))
        # closest one is itself so start at 1 and not 0
        for i in range(1, k+1):
            temp = res[i][0]
            results.append(temp)
            values += [res[i][1]]
            print("->{} ({})".format(temp, dictionary.urls[temp]))
            print(" ".join(dictionary.content[temp]))
        if string[0:7]=='article':
            CIDresults = [self.articles.CIDs[article_string] for article_string in results]
            return results, CIDresults, values
        elif string[0:7] == 'summary':
            return results

    def go_through_data(self):
        rootPath = os.path.join(os.getcwd(), 'output/')  # folder that we will go through
        m = 0
        n = 0
        o = 0
        for fileName in tqdm(os.listdir(rootPath)):
            full_review = True
            folderPath = os.path.join(rootPath, fileName)
            print("\n\nCurrently going over {} \n".format(folderPath))

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
                        self.articles.CIDs[string] = articleData['cid']
                        o += 1

        print("Visited {} folders, {} summaries, {} article words".format(m, n, o))


if __name__ == '__main__':
    tfidf_manager = TFIDFmanager()
    tfidf_manager.go_through_data()

    # this is to add words to the stopwords list
    # tfidf_manager.generate_excluded_vocabulary()

    # examples of retrieving k closest for article and summary
    ex = True
    if ex:
        ex_string_1 = 'article_2017-12-05_66'
        ex_string_2 = 'summary_2017-12-05'
        # close_article_names is under the format 'article_YYYY_MM_DD_numberofarticle'
        close_article_names, close_article_CIDs, close_article_scores = tfidf_manager.find_k_closest(ex_string_1, 5)
        tfidf_manager.find_k_closest(ex_string_2, 5)
        print(close_article_CIDs)
        print(close_article_scores)
    tfidf_manager.describe_yourself()