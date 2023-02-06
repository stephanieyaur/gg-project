# gg-project-master
Golden Globe Project Master

## Installation
To run:
```sh
    py gg_api.py
   ```
The final answer is written to final.json.

Commands had to run:
python -m spacy download en_core_web_sm

## Instructuons
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
- `preliminary_helpers.py` contains a function called categorize_tweets(year) which returns a dictionary to categorize tweets by award name. The key: award names | value: list of tweets. This is loaded as a global variable in `gg_api.py`called categorized_tweet_dict. 

- is_actor: Given an input name, returns bool if input name is an actor according to the imdb dataset. I created a MongoDb Database as explained in the MongoDb Database section.
- get_nominees: First gets nominees of awards where nominee types are people. The function uses nltk to get all “PERSON” types, narrows it down to the 50 most common names using FreqDist, checks for gender if gender matters (eg. actor should be male), and adds the person to the list of nominees if they are an actor according to the imdb dataset. If it is not a person, then I use two strategies to find movie/tv titles. First is to search for anything inside quotes and second is to search for all chunks that begin with capital letters (chunks of proper nouns). I then used a voting system to return the 4 nominees that occur the most often.
- get_presenters:
For each award, finds two presenters. Loops through tweets pertaining to each award and filters down to those mentioning a presenter - regex: “(announce|g[ia]ve|intro|present)”. Then uses NLTK to look for names, clustering if that name is contained in another name already in the dictionary. Then adds top two vote getters that are also actors (using is_actor to check).

## Additional Work
- We also worked on sentiment analysis as an extra credit feature. We implement this in get_winners where positive sentiments indicate winners.

## Helpful resources
1. Spacy
   - https://unbiased-coder.com/extract-names-python-spacy/

