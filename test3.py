import json
import re
from gender_detector.gender_detector import GenderDetector
from fuzzywuzzy import fuzz
from imdb import IMDb
import nltk
import pymongo
nltk.download('words')
from nltk.corpus import words
from nltk.corpus import stopwords
from PyDictionary import PyDictionary
import copy
from preliminary_helpers import categorize_tweets
from nltk import ne_chunk, pos_tag, word_tokenize, sentiment
from nltk.tree import Tree
from collections import defaultdict
from heapq import nlargest

categorized_tweet_dict = categorize_tweets(2013)
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

# Connects to mongodb database with uploaded imdb actors dataset
client = pymongo.MongoClient("mongodb+srv://mry2745:nlplab1pw@cluster0.tmoqg.mongodb.net/test")
db = client["imdb"] # database name: imdb
collection = db["actors"] # collection name: actors


def is_actor(input):
    # Queries mongodb database to see if the input string is an actor in the imdb dataset
    result = list(collection.find({"primaryName": {"$in": [input.lower()]}})) # change to primary name
    # result2 = list(collection.find({"primaryName": {"$in": ["not an actor"]}})) # change to primary name
    return len(result) > 0


def get_nominees(year):
    ia = IMDb()

    stop_list_people = ['best','-','award','for','or','made', 'in', 'a', 'by', 'performance', 'an','golden','globes','role','motion','picture','best','supporting']
    nominees = {}
    nominee_names = {}
    cfd = {}
    detector = GenderDetector('us')
    award_list_person=[]
    freq={}
    award_list_not_person =[]

    def add_people_nominees(award, gender_wanted):
        print("finding nominees for " + award)
        cfd[award] = nltk.FreqDist(nominee_names[award])
        most_common = cfd[award].most_common(50)
        for name in most_common:
            gender = detector.guess(name[0].split()[0])
            if gender_wanted == "any":
                if gender != 'unknown':
                    person = name[0].lower()
                    if is_actor(person):
                        if person not in nominees[award]:
                            nominees[award].append(person)
            if gender == gender_wanted:
                person = name[0].lower()
                if is_actor(person):
                    if person not in nominees[award]:
                        nominees[award].append(person)


    for award in OFFICIAL_AWARDS_1315:
        nominees[award] = []
        nominee_names[award]=[]

    name_pattern = re.compile(r'[A-Z][a-z]+\s[A-Z][a-z]+')

    for award in OFFICIAL_AWARDS_1315:
        for person in ["actor","actress","demille","director"]:
            if person in award:
                award_list_person.append(award)

    for award in award_list_person:
        for tweet in categorized_tweet_dict[award]:
            nltk_results = ne_chunk(pos_tag(word_tokenize(tweet)))
            for nltk_result in nltk_results:
                if type(nltk_result) == Tree:
                    name = ''
                    for nltk_result_leaf in nltk_result.leaves():
                        name += nltk_result_leaf[0] + ' '
                    if nltk_result.label() == "PERSON" and len(name.rstrip().split()) > 1: # might want to use name_pattern
                        nominee_names[award].append(name.rstrip())

    for award in award_list_person:

        if 'actor' in award:
            add_people_nominees(award, 'male')

        elif 'actress' in award:
            add_people_nominees(award, 'female')

        elif 'demille' in award:
            add_people_nominees(award, 'any')

        elif 'director' in award:
            add_people_nominees(award, 'any')


    for award in OFFICIAL_AWARDS_1315:
        if award not in award_list_person:
            award_list_not_person.append(award)

    for award in award_list_not_person:
        ignore_list=["@","#"]
        winner_stoplist = ['Motion','Picture','Best','Supporting','-', 'animated', 'best', 'comedy', 'drama', 'feature', 'film', 'foreign', 'globe', 'goes', 'golden', 'motion', 'movie', 'musical', 'or', 'original', 'picture', 'rt', 'series', 'song', 'television', 'to', 'tv']
        bigrams_list = []


        for tweet in categorized_tweet_dict[award]:

            tweet = re.sub(r'[^\w\s]','',tweet)
            if tweet[0] == "R" and tweet[1]=="T":
                continue

            bigram = nltk.bigrams(tweet.split())

            temp=[]
            for item in bigram:
                if item[0].lower() not in winner_stoplist and item[1].lower() not in winner_stoplist:
                    temp.append(item)


            for item in temp:
                if item[0][0] not in ignore_list and item[1][0] not in ignore_list:
                    bigrams_list.append(item)


        freq[award] = nltk.FreqDist([' '.join(item) for item in bigrams_list])

    for award in award_list_not_person:
        most_common = freq[award].most_common(20)
        for name in most_common:
            p2 = name[0].lower()
            p2 = p2.replace("golden globes", "")
            p2 = p2.replace("goldenglobes", "")
            p2 = p2.strip()
            if p2 not in nominees[award]:
                nominees[award].append(p2)

    for k,v in nominees.items():
        if v:
            v.pop(0)



    global nominee_global
    nominee_global = nominees
    return nominees

nominees = get_nominees(2013)
nom_key = list(nominees.keys())
nom_val = list(nominees.values())
for i in range(len(nominees)):
    print(nom_key[i], ' : ', nom_val[i])