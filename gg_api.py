'''Version 0.35'''
from tkinter.tix import TCL_WINDOW_EVENTS
from unicodedata import name

from Award import Award
from GoldenGlobe import GoldenGlobe
from preliminary_helpers import populate_awards_nominees
from string import punctuation

import json
import re
import nltk
import numpy
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

# variables
data = None
gg = GoldenGlobe()

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here

    # look for everything after "won" XX and before "goes to" - find the intersection
    won_awards = set()
    goes_to_awards = set()
    for d in data:
        tweet = d["text"]
        split_tweet = tweet.lower().split()
        try:
            # look for won
            won_index = split_tweet.index("won")
            if split_tweet[won_index+1] == "best":
                for i in range(won_index+2, len(split_tweet)):
                    delimiter = " "
                    won_awards.add(delimiter.join(split_tweet[won_index+1: i+1]).strip(punctuation))
            # look for goes to
            if "Kate" in tweet:
                x = "hoi"
            goes_index = split_tweet.index("goes")
            to_index = split_tweet[goes_index:].index("to")
            if to_index == 1:
                for i in range(0, goes_index):
                    delimiter = " "
                    goes_to_awards.add(delimiter.join(split_tweet[i: goes_index]).strip(punctuation))
        except:
            try:
                # look for goes to
                if "Kate" in tweet:
                    x = "hoi"
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
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here

    """
    for all tweets:
        split tweet
        if "nominated" or "nominee" in split_tweet:
        find actor name
        find award name

        add actor name to Award.nominees

    return nominees
    """
    for tweet in data:
        nltk_results = ne_chunk(pos_tag(word_tokenize(tweet["text"])))
        for nltk_result in nltk_results:
            if type(nltk_result) == Tree:
                name = ''
                for nltk_result_leaf in nltk_result.leaves():
                    name += nltk_result_leaf[0] + ' '
                if nltk_result.label() == "PERSON":
                    print('Type: ', nltk_result.label(), 'Name: ', name)
                    # check if they are an actor

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    
    global gg
    for award in gg.awards:
        winner_dict = {}
        for nominee in award.nominees:
            winner_dict[nominee] = 0
        
            for tweet in data:
                text = tweet["text"].lower()
                # expand thi
                #form1 = nominee.lower() + " won " + award.award_name.lower()
                if re.search(nominee.lower(),text):
                    if re.search("(won|wins|goes to|)",text) or re.search(award.award_name.lower().split(),text):
                        winner_dict[nominee] += 1 
        
        #print(winner_dict)
        max_votes = 0
        winner = ""
        for nominee in winner_dict:
            if winner_dict[nominee] > max_votes:
                max_votes = winner_dict[nominee]
                winner = nominee
        
        winner = ' '.join(word[0].upper() + word[1:] for word in winner.split())
        award.winners.append(winner)
        #print(winner_dict)
        print(winner + " won " + award.award_name)
        
    winners = {}
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    f = open('gg2013.json')
    global data
    data = json.load(f)
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
    gg = populate_awards_nominees(gg)
    # get awards
    # get_awards(2013)
    get_winner(2013)

    return

if __name__ == '__main__':
    main()
