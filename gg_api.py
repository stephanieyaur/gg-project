'''Version 0.35'''
import time
import json
import re
import nltk
import numpy
import spacy
import pandas as pd
import pymongo
import json
import re

from tkinter.tix import TCL_WINDOW_EVENTS
from unicodedata import name
from Award import Award
from GoldenGlobe import GoldenGlobe
from preliminary_helpers import populate_awards
from preliminary_helpers import categorize_tweets
from string import punctuation
from gender_detector.gender_detector import GenderDetector
from imdb import IMDb
from preliminary_helpers import categorize_tweets
from gender_detector.gender_detector import GenderDetector
from nltk import ne_chunk, pos_tag, word_tokenize, sentiment
from nltk.tree import Tree
from collections import defaultdict
from heapq import nlargest

nltk.download('words')

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

# variables
data = None
lower_tweets = None
split_tweets = None
final_presenters = {"best screenplay - motion picture": ["robert pattinson", "amanda seyfried"]}
gg = GoldenGlobe()
categorized_tweet_dict = categorize_tweets(2013)


# Connects to mongodb database with uploaded imdb actors dataset
client = pymongo.MongoClient("mongodb+srv://mry2745:nlplab1pw@cluster0.tmoqg.mongodb.net/test")
db = client["imdb"] # database name: imdb
collection = db["actors"] # collection name: actors


def is_actor(input):
    # Queries mongodb database to see if the input string is an actor in the imdb dataset
    result = list(collection.find({"primaryName": {"$in": [input.lower()]}})) # change to primary name
    # result2 = list(collection.find({"primaryName": {"$in": ["not an actor"]}})) # change to primary name
    return len(result) > 0


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    hosts = []
    potential_hosts = defaultdict(int)
    # Only look for tweets that mention "host"
    for i in range(len(data)):
        try:
            host_index = split_tweets[i].index("host")
            # METHOD 1 (faster - 7.113235712051392s): NLTK
            nltk_results = ne_chunk(pos_tag(word_tokenize(data[i])))
            for nltk_result in nltk_results:
                if type(nltk_result) == Tree:
                    name = ''
                    for nltk_result_leaf in nltk_result.leaves():
                        name += nltk_result_leaf[0] + ' '
                    if nltk_result.label() == "PERSON":
                        potential_hosts[name] += 1

            # Method 2(slower - 9.111426830291748s): SPACY
            # spacy_parser = english_nlp(data[i])
            # for entity in spacy_parser.ents:
            #     if entity.label_=="PERSON":
            #         potential_hosts[entity.text] += 1

        except:
            continue
    # get 2 actors with highest votes
    host1 = None
    host2 = None
    for h in potential_hosts:
        if not host1:
            host1 = h
        elif not host2:
            host2 = h
        else:
            if potential_hosts[h] > potential_hosts[host1] or potential_hosts[h] > potential_hosts[host2]:
                # TODO: check h against imdb before doing any updating
                # this potential host needs to be added. check if need to remove host1 or host2
                if potential_hosts[host1] < potential_hosts[host2]:
                    host1 = host2
                host2 = h
    hosts.append(host1)
    hosts.append(host2)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here

    # look for everything after "won" XX and before "goes to" - find the intersection
    won_awards = set()
    goes_to_awards = set()
    for i in range(len(data)):
        split_tweet = split_tweets[i]
        try:
            # look for won
            won_index = split_tweet.index("won")
            if split_tweet[won_index+1] == "best":
                for i in range(won_index+2, len(split_tweet)):
                    delimiter = " "
                    won_awards.add(delimiter.join(split_tweet[won_index+1: i+1]).strip(punctuation))
            # look for goes to
            goes_index = split_tweet.index("goes")
            to_index = split_tweet[goes_index:].index("to")
            if to_index == 1:
                for i in range(0, goes_index):
                    delimiter = " "
                    goes_to_awards.add(delimiter.join(split_tweet[i: goes_index]).strip(punctuation))
        except:
            try:
                # look for goes to
                goes_index = split_tweet.index("goes")
                to_index = split_tweet[goes_index:].index("to")
                if to_index == 1:
                    for i in range(0, goes_index):
                        delimiter = " "
                        goes_to_awards.add(delimiter.join(split_tweet[i: goes_index]).strip(punctuation))
            except:
                continue
    awards = goes_to_awards.copy()
    for a in goes_to_awards:
        if a not in won_awards:
            awards.remove(a)
    return awards

def get_nominees(year):
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
        potential_nominees = {}


        for tweet in categorized_tweet_dict[award]:

            # strategy 1: +2 for anything inside quotes
                    try:
                        match1 = re.search(r'"(.*?)"', tweet).group().strip(punctuation)
                        potential_nominees[match1] += 2
                    except:
                    # strategy 2: get all capitalized groups
                            stop_words = ["rt" , "@" "golden", "globes", "goldenglobe", "goldenglobes", "best", "demille", "comedy", "musical", "tv", "television", "drama", "motion picture", "award", "congrat",]
                            foundCapital = False
                            start_index = 0
                            end_index = None
                            split_tweet = tweet.split()
                            for i in range(0, len(split_tweet)):
                                if foundCapital == False:
                                    if split_tweet[i][0].isupper(): # found beginning of capitalized group
                                        start_index = i
                                        end_index = i
                                        foundCapital = True
                                else:
                                    if split_tweet[i][0].isupper(): # appending to capitalized group
                                        end_index = i
                                    else: # end of capitalized group
                                        foundCapital = False
                                        
                                        delimiter = " "
                                        name = delimiter.join(split_tweet[start_index: end_index+1]).strip(punctuation)
                                        name = name.lower().rstrip()
                                        if not any([x in name for x in stop_words]) and name != "i" and name != "golden globe" and name != "we" and name != "and" and name != "the" and name != "so":
                                            if name not in potential_nominees:
                                                potential_nominees[name] = 1
                                            else:
                                                potential_nominees[name] += 1


        # get top 4 nominees
        top_nominees = nlargest(4, potential_nominees, key = potential_nominees.get)
        nominees[award] = top_nominees



    global nominee_global
    nominee_global = nominees
    return nominees


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here

    # TODO: change award_short

    winners = populate_awards()

    for award in winners:
        isPerson = re.search(r"\bactor\b|\bactress\b", award) != None
        potential_winners = defaultdict(int)
        award_short = ' '.join(award.split(' ')[0:2])
        potential_tweets = {}
        for i in range(len(data)):
            tweet = data[i]
            lower_tweet = lower_tweets[i]
            winSearch = re.search(r"\bwon\b|\bwins\b",lower_tweet)
            goesToSearch = re.search("goes to",lower_tweet)
            if (winSearch or goesToSearch) and re.search(award_short,lower_tweet):
                # look for actors using NLTK
                if isPerson:
                    nltk_results = ne_chunk(pos_tag(word_tokenize(tweet)))
                    for nltk_result in nltk_results:
                        if type(nltk_result) == Tree:
                            name = ''
                            for nltk_result_leaf in nltk_result.leaves():
                                name += nltk_result_leaf[0] + ' '
                            if nltk_result.label() == "PERSON" and not re.search("[Bb]est",name):# and is_actor(name):
                                #print(name, " is a potential winner")
                                potential_winners[name] += 1
                                potential_tweets[tweet] = name
                # look for movies using similar strategy to get_awards
                else:
                    # strategy 1: +2 for anything inside quotes
                    try:
                        match1 = re.search(r'"(.*?)"', tweet).group().strip(punctuation)
                        potential_winners[match1] += 2
                        potential_tweets[tweet] = match1
                    except:
                    # strategy 2: get all capitalized things from sentence AFTER the word "for"
                        split_tweet_upper = data[i].split()
                        split_tweet = split_tweets[i]
                        try:
                            for_index = split_tweet.index("for")
                            foundCapital = False
                            endIndex = None
                            for i in range(for_index+1, len(split_tweet)):
                                if foundCapital and not split_tweet_upper[i][0].isupper():
                                    break
                                if split_tweet_upper[i][0].isupper():
                                    if foundCapital == False and type(foundCapital) != int:
                                        foundCapital = i
                                        endIndex = i
                                    else:
                                        endIndex = i
                            if endIndex:
                                delimiter = " "
                                potential_winners[(delimiter.join(split_tweet_upper[foundCapital: endIndex+1]).strip(punctuation))] += 1
                                potential_tweets[tweet] = (delimiter.join(split_tweet_upper[foundCapital: endIndex+1]).strip(punctuation))
                        except:
                            continue

                    # strategy 3: get first group of words capitalized before "wins" or "won", or after "goes to" - LOW SUCCESS (i.e. Quentin Tarantino overwhelmingly had greater count than Django Unchained)
                    # if winSearch: #look at first half
                    #     try:
                    #         won_index = split_tweet.index("won")
                    #         foundCapital = False
                    #         endIndex = None
                    #         for i in range(0, won_index):
                    #             if foundCapital and not split_tweet_upper[i][0].isupper():
                    #                 break
                    #             if split_tweet_upper[i][0].isupper():
                    #                 if foundCapital == False and type(foundCapital) != int:
                    #                     foundCapital = i
                    #                     endIndex = i
                    #                 else:
                    #                     endIndex = i
                    #         if endIndex:
                    #             delimiter = " "
                    #             potential_winners[(delimiter.join(split_tweet_upper[foundCapital: endIndex+1]).strip(punctuation))] += 1
                    #     except:
                    #         try:
                    #             wins_index = split_tweet.index("wins")
                    #             foundCapital = False
                    #             endIndex = None
                    #             for i in range(0, wins_index):
                    #                 if foundCapital and not split_tweet_upper[i][0].isupper():
                    #                     break
                    #                 if split_tweet_upper[i][0].isupper():
                    #                     if foundCapital == False and type(foundCapital) != int:
                    #                         foundCapital = i
                    #                         endIndex = i
                    #                     else:
                    #                         endIndex = i
                    #             if endIndex:
                    #                 delimiter = " "
                    #                 potential_winners[(
                    #                     delimiter.join(split_tweet_upper[foundCapital: endIndex + 1]).strip(
                    #                         punctuation))] += 1
                    #         except:
                    #             continue
                    # else:
                    #     try:
                    #         goes_index = split_tweet.index("goes")
                    #         to_index = split_tweet[goes_index:].index("to")
                    #         if to_index == 1:
                    #             foundCapital = False
                    #             endIndex = None
                    #             for i in range(goes_index + 2, len(split_tweet_upper)):
                    #                 if foundCapital and not split_tweet_upper[i][0].isupper():
                    #                     break
                    #                 if split_tweet_upper[i][0].isupper():
                    #                     if foundCapital == False and type(foundCapital) != int:
                    #                         foundCapital = i
                    #                         endIndex = i
                    #                     else:
                    #                         endIndex = i
                    #             if endIndex:
                    #                 delimiter = " "
                    #                 potential_winners[(delimiter.join(split_tweet_upper[foundCapital: endIndex+1]).strip(punctuation))] += 1
                    #     except:
                    #         continue
        maxPW = None
        for pw in potential_winners:
            if not maxPW:
                maxPW = pw
            if potential_winners[maxPW] < potential_winners[pw]:
                maxPW = pw
        winners[award] = maxPW
    #print(winners[award], " won ",award)

    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    presenters = populate_awards()
    for award in presenters:
        potential_presenters = {}
        award_short = ' '.join(award.split(' ')[0:2])
        for tweet in data:
            text = tweet.lower()
            if re.search(award_short.lower(),text) and re.search("(present|announce)",text):
                nltk_results = ne_chunk(pos_tag(word_tokenize(tweet)))
                for nltk_result in nltk_results:
                    if type(nltk_result) == Tree:
                        name = ''
                        for nltk_result_leaf in nltk_result.leaves():
                            name += nltk_result_leaf[0] + ' '
                        name = name.strip()
                        if nltk_result.label() == "PERSON":
                            matched = 0
                            og_name = []
                            for person in potential_presenters:
                                # clustering names if short name contained in other
                                if re.search(name,person):
                                    potential_presenters[person] += 1
                                    matched = True
                                    full_name = person
                                    og_name.append(person)
                                elif re.search(person,name):
                                    potential_presenters[person] += 1
                                    matched = True
                                    full_name = name
                                    og_name.append(person)

                            if matched:
                                for og in og_name:
                                    try:
                                        potential_presenters[full_name] += potential_presenters.pop(og)
                                    except:
                                        potential_presenters[full_name] = potential_presenters.pop(og)
                            else:
                                potential_presenters[name] = 1


                            # if is_actor(name):
                            #     potential_presenters[name] += 0.5
        # try:
        #     presenter1 = max(potential_presenters)
        #     while not is_actor(presenter1):
        #         potential_presenters.pop(presenter1)
        #         presenter1 = max(potential_presenters)
            
        #     try:
        #         presenter2 = max(potential_presenters)
        #         while not is_actor(presenter2):
        #             potential_presenters.pop(presenter2)
        #             presenter2 = max(potential_presenters)
        #         presenters[award] = [presenter1,presenter2]
        #     except:
        #         print("only one match for",award)
        #         presenters[award] = [presenter1]
        # except:
        #    print("no one matched for",award)
        try:
            presenter1 = max(potential_presenters) 
            potential_presenters.pop(presenter1)
            presenter2 = max(potential_presenters)
            presenters[award] = [presenter1,presenter2]
        except:
            print("no one matched for",award)
        
        



    print(presenters)
    final_presenters = presenters
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    f = open('gg2013.json')
    global data
    global split_tweets
    global lower_tweets
    loaded_data = json.load(f)
    data = [None for i in range(len(loaded_data))]
    lower_tweets = [None for i in range(len(loaded_data))] # all tweets saved in lowercase form
    split_tweets = [None for i in range(len(loaded_data))] # each tweet split by space
    # Clean each tweet so only keep the "data" field and make it all lowercase
    for i in range(len(loaded_data)):
        data[i] = loaded_data[i]["text"]
        lower_tweets[i] = data[i].lower()
        split_tweets[i] = lower_tweets[i].split()
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    pre_ceremony()
    # # get award and nominees within GoldenGlobes object
    global gg
    # gg = populate_awards_nominees(gg)
    # get awards
    # get_awards(2013)
    # get_winner(2013)
    # get_nominees(2013)
    # time1 = time.time()
    # get_hosts(2013)
    # time2 = time.time()
    # print("get_hosts using nltk elapsed time: " + str(time2-time1))
    # is_actor("jennifer lawrence")
    # get_presenters(2013)
    nominees = get_nominees(2013)
    return

if __name__ == '__main__':
    main()
