import json
from Award import Award
import json
import nltk
nltk.download('words')

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

def populate_awards_nominees(gg):
    f = open('gg2013answers.json')
    answersDictionary = json.load(f)
    for award_name in answersDictionary["award_data"]:
        newAward = Award()
        newAward.award_name = award_name
        award = answersDictionary["award_data"][award_name]
        for n in award["nominees"]:
            newAward.nominees.append(n)
        newAward.nominees.append(award["winner"])
        gg.awards.append(newAward)
    return gg

# Initialize winner dictionary for get_winners
# Returns a dictionary of actual awards as keys and empty string as values
def populate_awards():
    d = {}
    f = open('gg2013answers.json')
    answersDictionary = json.load(f)
    for award_name in answersDictionary["award_data"]:
        d[award_name] = 0
    return 
    
# Returns a dictionary to categorize tweets by award name.
# Key: award names | Value: list of tweets
def categorize_tweets(year):

    print("Categorizing tweets by award name. Takes about 1 min")
    f = open('gg'+ str(year) + '.json')
    data = json.load(f)
    tweets = [tweet['text'] for tweet in data]

    awards = OFFICIAL_AWARDS_1315
    categorized_tweet_dict = {}
    for award in awards:
        categorized_tweet_dict[award] = []

    to_delete = ['-', 'a', 'an', 'award', 'best', 'by', 'for', 'in', 'made', 'or', 'performance', 'role', 'feature', 'language']

    short_awards_dict = dict()
    for award in awards:
        short_awards_dict[award] = [[item for item in award.split() if not item in to_delete]]

    for award in awards:
        if "television" in award:
            extra = award.replace("television", 'tv')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("television", 't.v.')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "motion picture" in award:
            extra = award.replace("motion picture", "movie")
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("motion picture", "film")
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "film" in award:
            extra = award.replace("film", "motion picture")
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("film", "movie")
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "comedy or musical" in award:
            extra = award.replace("comedy or musical", 'comedy')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("comedy or musical", 'musical')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "series, mini-series or motion picture made for television" in award:
            extra = award.replace("series, mini-series or motion picture made for television", 'series')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'mini-series')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'miniseries')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'tv')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'television')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'tv movie')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'tv series')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("series, mini-series or motion picture made for television", 'television series')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "mini-series or motion picture made for television" in award:
            extra = award.replace("mini-series or motion picture made for television", 'miniseries')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("mini-series or motion picture made for television", 'mini-series')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("mini-series or motion picture made for television", 'tv movie')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("mini-series or motion picture made for television", 'television movie')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "television series" in award:
            extra = award.replace("television series", 'series')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("television series", 'tv')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("television series", 't.v.')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

            extra = award.replace("television series", 'television')
            short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "television series - comedy or musical" in award:

            for word in ["tv comedy", "tv musical", "comedy series", "t.v. comedy", "t.v. musical", "television comedy", "television musical"]:
                extra = award.replace("television series - comedy or musical", word)
                short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

        if "television series - drama" in award:
            for word in ["tv drama", "drama series", "television drama", "t.v. drama"]:
                extra = award.replace("television series - drama", word)
                short_awards_dict[award].append([item for item in extra.split() if not item in to_delete])

    awards.sort(key=lambda s: len(s), reverse=True)

    for award in awards:
        print("finding tweets for " + award)
        tweet_length = len(tweets)
        for i in range(tweet_length - 1, -1, -1):
            tweet = tweets[i]
            for extra in short_awards_dict[award]:
                flag = True
                for word in extra:
                    if flag == True:
                        flag = flag and word.lower() in tweet.lower()

                if flag == True:
                    categorized_tweet_dict[award].append(tweet)
                    del tweets[i]
                    break

    print("done categorizing tweets by award name")
    print("--------------------------------------")
    return categorized_tweet_dict
