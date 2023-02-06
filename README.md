# gg-project-master
Golden Globe Project Master

## Installation

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
   

## Strategy
1. ```sh
    pre_ceremony
   ```
   

## Helpful resources