#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


# This creates two subdirectories called "theguardian" and "collection"
ARTICLES_DIR = join('theguardian', 'collection')
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
    'q': "Trump",
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
    article_path = '/Users/saralivbroe/Arbejdskatalog Ana/theguardian/collection/'
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
    raw_text = article["fields"]["body"]
    soup = BeautifulSoup(raw_text, 'html.parser')
    text = soup.get_text(strip=True)
    
    # splits text into words (seperate by white space, removes 's, so that Trump's is the same as Trump, 
    # makes all words lowercase words - so uppercase and lowercase are the same words
    # removes dots and commas 
    tokens = []
    for word in text.split():
        if word[-2:] == "’s":
            word = word[0:-2]
        tokens.append(word.lower().strip(".,"))
    
    # deletes words that are "stopwords"
    clean_tokens = []
    for word in tokens:
        if word not in stopwords.words('english'):
            clean_tokens.append(word)
    
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


collection = get_collection()

results = []
for article in collection:
    result = calculate_top_ten(article)
    results.append(result)

total = calculate_cross_statistics(results)
for x in total:
    print(x)