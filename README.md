# gg-project-master
Golden Globe Project Master
Stephanie Yaur, Megan Yaur, Max Rogal

## General Approach
Created global var categorized_tweet_dict that saved all award-related tweets to a particular award
Created mongodb dataset of actors to quickly check if an entity is an actor (used for get_nominees, get_hosts, and get_winners)
Used a general voting system for get_hosts, get_nominees, get_presenters, and get_winners
Used sentiment analysis to add bonus points (added the positive score) to each potential winner in get_winners

## Instructions

### How to Run:
After cloning the git repo and cd-ing to the directory, enter the following into your command line:
```sh
    py gg_api.py [YEAR]
   ```
where [YEAR] should be replaced by the year you want to run. For instance,
```sh
    py gg_api.py 2013
```
If no [YEAR] is added as a sys.argv, then it will default to 2013.
The final answer is written to `final.json`. The human readable format is written to `final.txt`.

### MongoDb Database
We created a MongoDb Database to store and access the imdb dataset of actors. 
*Note: You do NOT need to follow the MongoDb Database instructions to run our code. The database is up and running.
1. Download the IMDB actors dataset from https://datasets.imdbws.com/ and select the `name.basics.tsv.gz` file
2. Unzip the file and add it to the `gg-project` directory
3. Run `actors_modifier.py`. This will convert `actors.tgz` into a json file called `actors.json` containing primaryNames and deathYears of actors. Duplicates and unused columns are removed.
   ```sh
    py actors_modifier.py
   ```
4. Run `actors_upload_mongodb.py`. This will upload `actors.json` to mongodb.
   ```sh
    py actors_upload_mongodb.py
   ```

## Descriptions
`preliminary_helpers.py`:
- This file contains a function called categorize_tweets(year) which returns a dictionary to categorize tweets by award name. The key: award names | value: list of tweets. This is loaded as a global variable in `gg_api.py`called categorized_tweet_dict.
is_actor: 
- Given an input name, returns bool if input name is an actor according to the imdb dataset. I created a MongoDb Database as explained in the MongoDb Database section.
get_hosts:
- Finds all tweets that mention the word “host” and use NLTK to retrieve the PERSON entities in that tweet - increment the count of that person. After going through all tweets, iterate through all potential hosts and choose the top 2 that are actors, checking with the imdb mongodb.
get_awards:
- Finds all tweets that mentions “wins” or “goes to”. If the tweet mentions “wins”, add all possible phrases after “wins” to a set. If the tweet mentions “goes to”, add all possible phrases before “goes to” to a set. Then remove any instances that do not intersect with both sets.
get_nominees: 
- First, the function gets nominees of awards where nominee types are people. The function uses NLTK to get all “PERSON” types, narrows it down to the 50 most common names using FreqDist, checks for gender if gender matters (eg. actor should be male), and adds the person to the list of nominees if they are an actor according to the imdb dataset. If it is not a person, then I use two strategies to find movie/tv titles. First is to search for anything inside quotes and second is to search for all chunks that begin with capital letters (chunks of proper nouns). I then used a voting system to return the 4 nominees that occur the most often.
get_winners:
- For each award, look at tweets related to the award (see categorize_tweets in preliminary_helpers.py). Out of those tweets, check if mentions the words “wins”, “won”, or “goes to”. If so, then check if we should be looking for a person (mentions “actor” or “actress) or a film/TV show name. If person, then use NLTK to tokenize the tweets and get all “PERSON” entities (+1) . If not a person, then add anything inside quotes (+2). If there are no quotes, then look for the first group of capitalized words after the word “for” (+1). Also used sentiment analysis (see b.) to add to score. Then set this award’s winner to be the potential_winner with the highest score.
Uses NLTK’s pretrained vader algorithm to analyze tweets for sentiment. Giving preference to positive tweets about someone winning, get_winners takes the “pos” polarity score (value between zero and one) as a bonus voting score is added for how positive the tweet was.
get_presenters
- For each award, finds two presenters. Loops through tweets pertaining to each award and filters down to those mentioning a presenter - regex: “(announce|g[ia]ve|intro|present)”. Then uses NLTK to look for names using a similar method to previous functions. Names are clustered if that name is contained in another name already in the dictionary. Then adds top two vote getters that are also actors (using is_actor to check).

## Additional Work
- We also worked on sentiment analysis as an extra credit feature. We implement this in get_winners where positive sentiments indicate winners. Further explanation is in the get_winners description.
