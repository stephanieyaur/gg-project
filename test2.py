import json
import re
from gender_detector.gender_detector import GenderDetector
from imdb import IMDb
import nltk
import pymongo
nltk.download('words')
from preliminary_helpers import categorize_tweets
from nltk import ne_chunk, pos_tag, word_tokenize, sentiment
from nltk.tree import Tree
from heapq import nlargest
from string import punctuation

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

nominees = get_nominees(2013)
nom_key = list(nominees.keys())
nom_val = list(nominees.values())
for i in range(len(nominees)):
    print(nom_key[i], ' : ', nom_val[i])