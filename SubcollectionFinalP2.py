"""
Created on Mon Nov  4 23:11:29 2019

@author: saralivbroe
"""

#Importing the libraries that we'll be using
import json
import requests
from os import makedirs
from os.path import join, exists
from datetime import date, timedelta
from bs4 import BeautifulSoup
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import os

# Variables to hold processing statistics
stat_wordsBefore = 0
stat_wordsAfter = 0
stat_lenghtOfDocument = 0

model_articelTexts = []

# This creates two subdirectories called "theguardian" and "collection"
ARTICLES_DIR = join('theguardian', 'collectionSUBSET')
makedirs(ARTICLES_DIR, exist_ok=True)

MY_API_KEY = 'zzzyyyyy-9a9z-999z-z999-9e8a83922516'

API_ENDPOINT = 'http://content.guardianapis.com/search'
my_params = {
    'from-date': "", 
    'to-date': "",
    'order-by': "newest",
    'show-tags': "usnews, worldsnews",
    'show-fields': "all",
    'page-size': "200",
    'q': "Donald Trump",
    'api-key': "f906dd3e-6c7c-4562-84f7-4d95329bad6a"
}

start_date = date(2018, 10, 30)
end_date = date(2019, 10, 30)

dayrange = range((end_date - start_date).days + 1)
for daycount in dayrange:
    dt = start_date + timedelta(days=daycount)
    datestr = dt.strftime('%Y-%m-%d')
    fname = join(ARTICLES_DIR, datestr + '.json')
    if not exists(fname):
        print("Downloading", datestr)
        all_results = []
        my_params['from-date'] = datestr
        my_params['to-date'] = datestr
        current_page = 1
        total_pages = 1
        while current_page <= total_pages:
            print("...page", current_page)
            my_params['page'] = current_page
            resp = requests.get(API_ENDPOINT, my_params)
            data = resp.json()
            all_results.extend(data['response']['results'])
            current_page += 1
            total_pages = data['response']['pages']

        with open(fname, 'w') as f:
            print("Writing to", fname)

            f.write(json.dumps(all_results, indent=2))

def get_collection():
    """ Returns a list of all filepaths to articles found in the specified folder """
    articles = []
    article_path = '/Users/saralivbroe/Arbejdskatalog Ana/theguardian/collectionSUBSET/'
    all_files = [os.path.join(article_path, f) for f in os.listdir(article_path)]

    for filepath in all_files:
        with open(filepath) as file:
            try:
                for article in json.load(file):
                    articles.append(article)
            except UnicodeDecodeError:
                print(f'{filepath} ignored, unicode error')
    return articles


def calculate_top_ten(article):
    global stat_wordsBefore
    global stat_wordsAfter
    global stat_lenghtOfDocument
    
    raw_text = article["fields"]["body"]
    soup = BeautifulSoup(raw_text, 'html.parser')
    text = soup.get_text(strip=True)
    stat_lenghtOfDocument += len(text)
    
    # splits text into words (seperate by white space, removes 's, so that Trump's is the same as Trump, 
    # makes all words lowercase words - so uppercase and lowercase are the same words
    # removes dots and commas 
    tokens = []
    
    words = text.split()
    stat_wordsBefore += len(words)
    
    # HACK - Saving it for topic modeling later
    model_articelTexts.append(text)
    
    for word in words:
        if word[-2:] == "’s":
            word = word[0:-2]
        tokens.append(word.lower().strip(".,"))
    
    # deletes words that are "stopwords"
    clean_tokens = []
    #You can always add more stopwords to this list
    my_stop_words = [""]
    for word in tokens:
        if word not in stopwords.words('english') and word not in my_stop_words:
            clean_tokens.append(word)
            
    stat_wordsAfter += len(clean_tokens)
    
    # counting the frequency of words
    freq = nltk.FreqDist(clean_tokens)
    
    # makes a sorted list of words (reverse since we want the highest frequency of words first)
    ordered_list = [(x,y) for x,y in freq.items()]
    ordered_list.sort(key=lambda x: x[1], reverse=True)
    
    # returns top 10 word
    return [x[0] for x in ordered_list[:10]]

def calculate_cross_statistics(result_list):
    total = {}
    for result in result_list:
        for word in result:
            if word not in total:
                total[word] = 0
            total[word] += 1
            
    ordered_list = [(x,y) for x,y in total.items()]
    ordered_list.sort(key=lambda x: x[1], reverse=True)
    return ordered_list

print(stopwords.words('english'))

collection = get_collection()

print('Collection loaded. Processing...')

results = []
processing = 0
toBeProcessed = len(collection)
for article in collection:
    result = calculate_top_ten(article)
    processing += 1
    print(str(processing) + '/' + str(toBeProcessed))
    results.append(result)

total = calculate_cross_statistics(results)
for x in total[:10]:
    print(x)
    
print('Statistics')
print('----------')
print('Number of documents: ' + str(len(collection)))
print('Number of words before processing (number of words in total): ' + str(stat_wordsBefore ))
print('Number of words after processing: ' + str(stat_wordsAfter))
print('Average word count per document before processing: ' + str((stat_wordsBefore / len(collection))))
print('Average word count per document after processing: ' + str((stat_wordsAfter / len(collection))))
print('Average length of documents: ' + str((stat_lenghtOfDocument / len(collection))))

print('\n')
print('Topic model')

#word cloud - https://www.geeksforgeeks.org/generating-word-cloud-python/

def makeWordCloud(words):
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt 
    
    stopwords = []
    topic_words = ' '
    
    for word in words: 
        topic_words = topic_words + word + ' '
    
    wordcloud = WordCloud(width = 800, height = 800, 
                    background_color ='white', 
                    stopwords = stopwords, 
                    min_font_size = 10).generate(topic_words) 
      
    # plot the WordCloud image                        
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
      
    plt.show() 

# Taken from https://stackabuse.com/python-for-nlp-topic-modeling/

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

articel_datasets = pd.DataFrame(model_articelTexts)
articel_datasets.dropna()

count_vect = CountVectorizer(max_df=0.8, min_df=2, stop_words='english')
doc_term_matrix = count_vect.fit_transform(articel_datasets[0].values.astype('U'))

from sklearn.decomposition import LatentDirichletAllocation

LDA = LatentDirichletAllocation(n_components=5, random_state=42)
LDA.fit(doc_term_matrix)

import random

for i in range(10):
    random_id = random.randint(0,len(count_vect.get_feature_names()))
    print(count_vect.get_feature_names()[random_id])
    
first_topic = LDA.components_[0]
top_topic_words = first_topic.argsort()[-10:]
    
for i,topic in enumerate(LDA.components_):
    words = [count_vect.get_feature_names()[i] for i in topic.argsort()[-10:]]
    
    print(f'Top 10 words for topic #{i}:')
    print(*words, sep = ", ")
    makeWordCloud(words)
    print('\n')
    