import json
import pandas as pd

# import file
actors_df = pd.read_csv('actors.tsv', sep='\t')

# drop unused columns
actors_df.drop(columns=['nconst', 'birthYear', 'primaryProfession', 'knownForTitles'])
actors_df['primaryName'].str.lower()

# serializing json
result = actors_df.to_json(orient="records")
parsed = json.loads(result)
json_object = json.dumps(parsed, indent=4)

# writing to json file
with open("actors.json", "w") as outfile:
    outfile.write(json_object)

print("Done converting actors.tsv to actors.json. Upload this to MongoDB")
